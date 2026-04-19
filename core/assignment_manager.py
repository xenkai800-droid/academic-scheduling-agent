import sqlite3
import datetime
from db.database import DB_NAME


# -----------------------------------
# ADD ASSIGNMENT
# -----------------------------------

def add_assignment(title, subject, due_date, priority="auto"):

    try:

        if not title:
            return "❌ Assignment title is required."

        if not due_date:
            return "❌ Due date is required."

        today = datetime.date.today()

        try:
            due = datetime.date.fromisoformat(due_date)
        except Exception:
            return "❌ Invalid date format."

        if due < today:
            return "❌ Due date cannot be in the past."

        # -------------------------
        # PRIORITY LOGIC
        # -------------------------

        if not priority or priority == "auto":

            days_left = (due - today).days

            if days_left <= 1:
                priority = "high"
            elif days_left <= 3:
                priority = "medium"
            else:
                priority = "low"

        priority = priority.lower()

        if priority not in ["low", "medium", "high"]:
            priority = "medium"

        # -------------------------
        # SAVE TO DB
        # -------------------------

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
        return f"❌ Error adding assignment: {str(e)}"


# -----------------------------------
# GET ASSIGNMENTS (STRUCTURED)
# -----------------------------------

def get_assignments():

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

        structured = []

        for r in rows:
            structured.append({
                "id": r[0],
                "title": r[1],
                "subject": r[2] or "General",
                "due_date": r[3],
                "status": r[4],
                "priority": r[5],
            })

        return structured

    except Exception:
        return []


# -----------------------------------
# MARK COMPLETE
# -----------------------------------

def mark_assignment_complete(assignment_id):

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

        return "✅ Assignment completed"

    except Exception as e:
        return f"❌ Error removing assignment: {str(e)}"