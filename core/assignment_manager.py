import sqlite3
import datetime
from db.database import DB_NAME


def add_assignment(title, subject, due_date, priority="auto"):
    """
    Add a new assignment with hybrid priority:
    - User-defined priority OR
    - Auto-calculated based on urgency
    """

    try:

        if not title:
            return "Error: Assignment title is required."

        if not due_date:
            return "Error: Due date is required."

        today = datetime.date.today()

        # Convert due_date safely
        try:
            due = datetime.date.fromisoformat(due_date)
        except Exception:
            return "Error: Invalid date format."

        if due < today:
            return "Error: Due date cannot be in the past."

        # ------------------------------
        # HYBRID PRIORITY LOGIC
        # ------------------------------

        if not priority or priority == "auto":

            days_left = (due - today).days

            if days_left <= 1:
                priority = "high"
            elif days_left <= 3:
                priority = "medium"
            else:
                priority = "low"

        # Normalize priority
        priority = priority.lower()
        if priority not in ["low", "medium", "high"]:
            priority = "medium"

        # ------------------------------
        # DATABASE INSERT
        # ------------------------------

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO assignments (title, subject, due_date, status, priority)
            VALUES (?, ?, ?, 'pending', ?)
            """,
            (title.strip(), subject.strip(), due_date, priority),
        )

        conn.commit()
        conn.close()

        return f"✅ Assignment added (Priority: {priority.upper()})"

    except Exception as e:
        return f"Error adding assignment: {str(e)}"


def get_assignments():
    """
    Return only pending assignments with priority sorting.
    """

    try:

        today = datetime.date.today().isoformat()

        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, title, subject, due_date, status, priority
            FROM assignments
            WHERE status = 'pending'
            AND due_date >= ?
            ORDER BY 
                CASE priority
                    WHEN 'high' THEN 1
                    WHEN 'medium' THEN 2
                    WHEN 'low' THEN 3
                END,
                due_date ASC
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