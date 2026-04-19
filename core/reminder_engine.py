import sqlite3
import datetime
from db.database import DB_NAME


def get_due_assignments():
    """
    Return assignments that are:
    - Past due
    - Due today
    - Due tomorrow

    Output format: list of dicts
    """

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        cursor.execute(
            """
            SELECT id, title, subject, due_date, reminder_sent
            FROM assignments
            WHERE status = 'pending'
            """
        )

        rows = cursor.fetchall()
        conn.close()

        reminders = []

        for aid, title, subject, due, sent in rows:

            try:
                due_date = datetime.date.fromisoformat(due)
            except Exception:
                continue

            # -------------------------
            # FILTER ONLY RELEVANT
            # -------------------------

            if due_date > tomorrow:
                continue

            # -------------------------
            # LABEL CLASSIFICATION
            # -------------------------

            if due_date < today:
                label = "past_due"
            elif due_date == today:
                label = "today"
            else:
                label = "tomorrow"

            reminders.append({
                "id": aid,
                "title": title,
                "subject": subject or "General",
                "due_date": due,
                "status": label,
                "reminder_sent": sent,
            })

        return reminders

    except Exception:
        return []


def mark_reminder_sent(assignment_id):
    """
    Mark reminder as sent (used by email system)
    """

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