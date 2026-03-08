import sqlite3
import datetime
from db.database import DB_NAME


def get_due_assignments():

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        cursor.execute(
            """
            SELECT id, title, subject, due_date
            FROM assignments
            WHERE status = 'pending'
            AND reminder_sent = 0
            """
        )

        rows = cursor.fetchall()

        reminders = []

        for aid, title, subject, due in rows:

            due_date = datetime.date.fromisoformat(due)

            if due_date <= tomorrow:
                reminders.append((aid, title, subject, due))

        conn.close()

        return reminders

    except Exception:
        return []


def mark_reminder_sent(assignment_id):

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE assignments
            SET reminder_sent = 1
            WHERE id = ?
            """,
            (assignment_id,),
        )

        conn.commit()
        conn.close()

    except Exception:
        pass
