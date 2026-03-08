import sqlite3
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

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assignments (title, subject, due_date)
            VALUES (?, ?, ?)
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
    Retrieve all assignments sorted by due date.
    """

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, subject, due_date, status
            FROM assignments
            ORDER BY due_date
            """
        )

        rows = cursor.fetchall()
        conn.close()

        return rows

    except Exception:
        return []


def mark_assignment_complete(assignment_id):
    """
    Mark an assignment as completed.
    """

    try:

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE assignments
            SET status = 'completed'
            WHERE id = ?
            """,
            (assignment_id,),
        )

        conn.commit()
        conn.close()

        return "Assignment marked as completed"

    except Exception as e:
        return f"Error updating assignment: {str(e)}"
