from core.assignment_manager import add_assignment
import datetime


def add_assignment_tool(title: str, subject: str, due_date: str):
    """
    Add a new assignment.

    Parameters
    ----------
    title : str
        Assignment title
    subject : str
        Subject name
    due_date : str
        Due date in YYYY-MM-DD format
    """

    try:

        # -------------------------------
        # BASIC VALIDATION
        # -------------------------------

        if not title:
            return "Error: Assignment title is required."

        if not due_date:
            return "Error: Due date is required."

        title = title.strip()
        subject = subject.strip() if subject else "General"

        # -------------------------------
        # NORMALIZE DATE
        # -------------------------------

        try:

            today = datetime.date.today()
            parsed = datetime.datetime.strptime(due_date, "%Y-%m-%d").date()

            # Fix LLM wrong-year hallucination
            if parsed.year < today.year:
                parsed = parsed.replace(year=today.year)

            # Prevent past assignments
            if parsed < today:
                return "Error: Due date cannot be in the past."

            due_date = parsed.isoformat()

        except Exception:
            return "Invalid due date format. Please use YYYY-MM-DD."

        # -------------------------------
        # SAVE ASSIGNMENT
        # -------------------------------

        result = add_assignment(title, subject, due_date)

        return result

    except Exception as e:
        return f"Error adding assignment: {str(e)}"
