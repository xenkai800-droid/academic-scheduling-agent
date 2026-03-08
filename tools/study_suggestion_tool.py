import datetime

from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time


def suggest_study_session_tool():
    """
    Suggest a study session for assignments that are due soon.
    """

    try:

        assignments = get_assignments()

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        for assignment in assignments:

            # safe unpack
            aid, title, subject, due, status = assignment[:5]

            if status != "pending":
                continue

            due_date = datetime.date.fromisoformat(due)

            # Check assignments due soon
            if due_date <= tomorrow:

                free_time_message = find_free_time(date=today.isoformat())

                if "No free slots" not in free_time_message:

                    subject = subject if subject else "General"

                    return (
                        f"📚 Study Suggestion\n\n"
                        f"'{title}' for {subject} is due soon.\n\n"
                        f"You have available free time today.\n"
                        f"Consider scheduling a study session.\n\n"
                        f"{free_time_message}"
                    )

        return "No urgent assignments requiring study time."

    except Exception as e:
        return f"Error generating study suggestion: {str(e)}"
