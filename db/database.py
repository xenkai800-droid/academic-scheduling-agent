import sqlite3

DB_NAME = "scheduler.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_event_id TEXT,
            title TEXT,
            event_date TEXT,
            start_time TEXT,
            end_time TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def save_event(google_event_id, title, date, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO events (google_event_id, title, event_date, start_time, end_time)
        VALUES (?, ?, ?, ?, ?)
    """, (google_event_id, title, date, start_time, end_time))

    conn.commit()
    conn.close()