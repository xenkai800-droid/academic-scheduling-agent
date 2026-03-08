import sqlite3

DB_NAME = "scheduler.db"


def initialize_database():

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                google_event_id TEXT UNIQUE,
                title TEXT NOT NULL,
                event_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT NOT NULL
            )
        """
        )

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT,
                due_date TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                reminder_sent INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print("Database initialization error:", e)


def save_event(google_event_id, title, event_date, start_time, end_time):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO events
            (google_event_id, title, event_date, start_time, end_time)
            VALUES (?, ?, ?, ?, ?)
        """,
            (google_event_id, title, event_date, start_time, end_time),
        )

        conn.commit()
        conn.close()

    except Exception as e:
        print("Error saving event:", e)


def delete_local_event(event_id):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM events WHERE google_event_id = ?", (event_id,))

        conn.commit()
        conn.close()

    except Exception as e:
        print("Error deleting event:", e)


def event_exists_locally(title, event_date):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1 FROM events
            WHERE LOWER(title) = LOWER(?)
            AND event_date = ?
            LIMIT 1
        """,
            (title, event_date),
        )

        result = cursor.fetchone()
        conn.close()

        return result is not None

    except Exception:
        return False


def is_time_slot_available(event_date, start_time):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT 1 FROM events
            WHERE event_date = ?
            AND start_time = ?
            LIMIT 1
        """,
            (event_date, start_time),
        )

        result = cursor.fetchone()
        conn.close()

        return result is None

    except Exception:
        return False


def get_events_by_date(event_date):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT title, start_time, end_time
            FROM events
            WHERE event_date = ?
            ORDER BY start_time
            """,
            (event_date,),
        )

        events = cursor.fetchall()

        conn.close()

        return events

    except Exception:
        return []
