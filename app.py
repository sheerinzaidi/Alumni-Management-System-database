from flask import Flask, jsonify, request, render_template, session, redirect
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'mypass'       # change it later !!

DATABASE = os.path.join(os.path.dirname(__file__), 'db', 'alumni_dms.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/events')
def events_page():
    return render_template('events.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/api/alumni', methods=['GET'])
def get_alumni():
    conn = get_db_connection()
    alumni = conn.execute('SELECT * FROM alumni').fetchall()
    conn.close()
    return jsonify([dict(row) for row in alumni])

@app.route('/api/events', methods=['GET'])
def get_events():
    conn = get_db_connection()
    events = conn.execute('SELECT * FROM events').fetchall()
    conn.close()
    return jsonify([dict(row) for row in events])

@app.route('/api/registrations', methods=['POST'])
def register_event():
    new_registration = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO event_registrations (alumni_id, event_id) VALUES (?, ?)',
                 (new_registration['alumni_id'], new_registration['event_id']))
    conn.commit()
    conn.close()
    return jsonify(new_registration), 201

@app.route('/api/donations', methods=['POST'])
def make_donation():
    new_donation = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO donations (alumni_id, amount, purpose, transaction_date) VALUES (?, ?, ?, date("now"))',
                     (new_donation['alumni_id'], new_donation['amount'], new_donation.get('purpose', '')))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Donation added successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    feedback = request.get_json()
    conn = get_db_connection()
    conn.execute('INSERT INTO feedback (alumni_id, feedback_message) VALUES (?, ?)',
                 (feedback['alumni_id'], feedback['message']))
    conn.commit()
    conn.close()
    return jsonify(feedback), 201

@app.route('/api/job_postings', methods=['GET'])
def get_job_postings():
    conn = get_db_connection()
    job_postings = conn.execute('SELECT * FROM job_postings').fetchall()
    conn.close()
    return jsonify([dict(row) for row in job_postings])

# Add new API endpoints
@app.route('/api/alumni', methods=['POST'])
def add_alumni():
    data = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO alumni (full_name, email, graduation_year, contact_info, current_location, current_employment) 
                       VALUES (?, ?, ?, ?, ?, ?)''',
                    (data['full_name'], data['email'], data['graduation_year'], 
                     data.get('contact_info', ''), data.get('current_location', ''), data.get('current_employment', '')))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Alumni added successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO events (event_name, event_date, venue) VALUES (?, ?, ?)',
                    (data['event_name'], data['event_date'], data['venue']))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Event added successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/job_postings', methods=['POST'])
def add_job_posting():
    data = request.get_json()
    conn = get_db_connection()
    try:
        conn.execute('''INSERT INTO job_postings (job_title, description, posting_date, application_deadline, posted_by_admin_id) 
                       VALUES (?, ?, ?, ?, ?)''',
                    (data['job_title'], data['description'], data.get('posting_date'), 
                     data.get('application_deadline'), data.get('posted_by_admin_id', 1)))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Job posting added successfully'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/donations', methods=['GET'])
def get_donations():
    conn = get_db_connection()
    donations = conn.execute('''SELECT d.*, a.full_name FROM donations d 
                               LEFT JOIN alumni a ON d.alumni_id = a.alumni_id''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in donations])

@app.route('/api/feedback', methods=['GET'])
def get_feedback():
    conn = get_db_connection()
    feedback = conn.execute('''SELECT f.*, a.full_name FROM feedback f 
                              LEFT JOIN alumni a ON f.alumni_id = a.alumni_id''').fetchall()
    conn.close()
    return jsonify([dict(row) for row in feedback])

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    
    # Get total alumni count
    alumni_count = conn.execute('SELECT COUNT(*) as count FROM alumni').fetchone()['count']
    
    # Get total events count
    events_count = conn.execute('SELECT COUNT(*) as count FROM events').fetchone()['count']
    
    # Get total donations amount
    donations_total = conn.execute('SELECT SUM(amount) as total FROM donations').fetchone()['total'] or 0
    
    # Get total job postings count
    jobs_count = conn.execute('SELECT COUNT(*) as count FROM job_postings').fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'alumni_count': alumni_count,
        'events_count': events_count,
        'donations_total': donations_total,
        'jobs_count': jobs_count
    })

@app.route('/api/signup', methods=['POST'])
def signup():
    # Use form data instead of JSON
    email = request.form.get('email')
    password = request.form.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    if user:
        conn.close()
        return jsonify({'error': 'User already exists'}), 409

    hashed_password = generate_password_hash(password)
    conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, hashed_password))
    conn.commit()
    conn.close()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/signin')
def signin_page():
    return render_template('signin.html')

@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        session['user_id'] = user['id']
        session['user_email'] = user['email']
        return jsonify({'message': 'Sign in successful', 'user_id': user['id']}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/signin')
    return render_template('dashboard.html')  # You'll need to create this

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    
    # Create alumni table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alumni (
            alumni_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE,
            graduation_year INTEGER,
            contact_info TEXT,
            current_location TEXT,
            current_employment TEXT
        )
    ''')
    
    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_name TEXT NOT NULL,
            event_date DATE,
            venue TEXT
        )
    ''')
    
    # Create event_registrations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS event_registrations (
            registration_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER,
            event_id INTEGER,
            registration_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (alumni_id) REFERENCES alumni(alumni_id),
            FOREIGN KEY (event_id) REFERENCES events(event_id)
        )
    ''')
    
    # Create donations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS donations (
            donation_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER,
            amount DECIMAL(10,2),
            purpose TEXT,
            transaction_date DATE,
            FOREIGN KEY (alumni_id) REFERENCES alumni(alumni_id)
        )
    ''')
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
            alumni_id INTEGER,
            feedback_message TEXT,
            related_event_or_service TEXT,
            date_submitted DATE,
            FOREIGN KEY (alumni_id) REFERENCES alumni(alumni_id)
        )
    ''')
    
    # Create job_postings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS job_postings (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            description TEXT,
            posting_date DATE,
            application_deadline DATE,
            posted_by_admin_id INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize DB on app startup
init_db()

if __name__ == '__main__':
    app.run(debug=True)