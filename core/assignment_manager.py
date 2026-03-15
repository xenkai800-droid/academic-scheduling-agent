import sqlite3
import datetime
from db.database import DB_NAME


def add_assignment(title, subject, due_date):
    """
    Add a new assignment to the database.
    """

    try:

        if not title:
            return "Error: Assignment title is required."

        if not due_date:
            return "Error: Due date is required."

        # Prevent past assignments
        today = datetime.date.today().isoformat()

        if due_date < today:
            return "Error: Due date cannot be in the past."

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assignments (title, subject, due_date, status)
            VALUES (?, ?, ?, 'pending')
            """,
            (title.strip(), subject.strip(), due_date),
        )

        conn.commit()
        conn.close()

        return "✅ Assignment added successfully"

    except Exception as e:
        return f"Error adding assignment: {str(e)}"


def get_assignments():
    """
    Return only pending assignments with future due dates.
    """

    try:

        today = datetime.date.today().isoformat()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, subject, due_date, status
            FROM assignments
            WHERE status = 'pending'
            AND due_date >= ?
            ORDER BY due_date ASC
            """,
            (today,),
        )

        rows = cursor.fetchall()
        conn.close()

        return rows

    except Exception:
        return []


def mark_assignment_complete(assignment_id):
    """
    Delete assignment when completed.
    """

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM assignments
            WHERE id = ?
            """,
            (assignment_id,),
        )

        conn.commit()
        conn.close()

        return "✅ Assignment completed and removed"

    except Exception as e:
        return f"Error removing assignment: {str(e)}"
