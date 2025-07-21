CREATE TABLE alumni (
    id INTEGER PRIMARY KEY ,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    graduation_year INTEGER,
    major TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE events (
    id INTEGER PRIMARY KEY ,
    title TEXT NOT NULL,
    description TEXT,
    event_date DATE NOT NULL,
    location TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE event_registrations (
    id INTEGER PRIMARY KEY ,
    alumni_id INTEGER,
    event_id INTEGER,
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumni_id) REFERENCES alumni (id),
    FOREIGN KEY (event_id) REFERENCES events (id)
);

CREATE TABLE donations (
    id INTEGER PRIMARY KEY ,
    alumni_id INTEGER,
    amount REAL NOT NULL,
    donation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumni_id) REFERENCES alumni (id)
);

CREATE TABLE feedback (
    id INTEGER PRIMARY KEY ,
    alumni_id INTEGER,
    message TEXT NOT NULL,
    feedback_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (alumni_id) REFERENCES alumni (id)
);

CREATE TABLE job_postings (
    id INTEGER PRIMARY KEY ,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    company TEXT NOT NULL,
    posting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);