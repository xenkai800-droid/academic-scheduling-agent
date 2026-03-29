import datetime

from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time


def suggest_study_session_tool():
    """
    Suggest a study session for assignments that are due soon.
    """

    try:

        assignments = get_assignments()

        if not assignments:
            return "You have no pending assignments."

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        # Find the most urgent assignment
        urgent_assignment = None
        urgent_due = None

        for assignment in assignments:

            try:
                aid, title, subject, due_date, status = assignment
            except Exception:
                continue

            if status != "pending":
                continue

            due_date = datetime.date.fromisoformat(due_date)

            if urgent_due is None or due_date < urgent_due:
                urgent_assignment = assignment
                urgent_due = due_date

        if not urgent_assignment:
            return "No urgent assignments requiring study time."

        aid, title, subject, due_date, status = urgent_assignment

        due_date = datetime.date.fromisoformat(due_date)

        # Only suggest study if due today or tomorrow
        if due_date > tomorrow:
            return "No urgent assignments requiring study time."

        subject = subject if subject else "General"

        free_time_message = find_free_time(date=today.isoformat())

        if "No free slots" in free_time_message:
            return (
                f"📚 Study Suggestion\n\n"
                f"'{title}' ({subject}) is due soon, "
                f"but you currently have no free time available today."
            )

        return (
            f"📚 Study Suggestion\n\n"
            f"'{title}' for {subject} is due soon.\n\n"
            f"You have available free time today.\n"
            f"Consider scheduling a study session.\n\n"
            f"{free_time_message}"
        )

    except Exception as e:
        return f"Error generating study suggestion: {str(e)}"
