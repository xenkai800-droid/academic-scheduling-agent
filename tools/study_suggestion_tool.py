import datetime

from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time


def suggest_study_session_tool():
    """
    Suggest a study session for urgent assignments (due today or tomorrow).
    """

    try:

        assignments = get_assignments()

        if not assignments:
            return "📚 You have no pending assignments."

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        urgent_assignments = []

        # 🔥 FIX: HANDLE DICT FORMAT
        for assignment in assignments:

            try:
                due_date_str = assignment.get("due_date")
                status = assignment.get("status")

                if status != "pending":
                    continue

                due_date = datetime.date.fromisoformat(due_date_str)

            except Exception:
                continue

            if due_date <= tomorrow:
                urgent_assignments.append((assignment, due_date))

        if not urgent_assignments:
            return "📚 No urgent assignments requiring study time."

        # 🔥 SORT BY URGENCY
        urgent_assignments.sort(key=lambda x: x[1])

        assignment, due_date = urgent_assignments[0]

        title = assignment.get("title", "Untitled")
        subject = assignment.get("subject", "General")
        priority = assignment.get("priority", "medium")

        # 🔥 GET FREE TIME
        free_time_message = find_free_time(date=today.isoformat())

        if not free_time_message or "No free slots" in free_time_message:
            return (
                f"📚 Study Recommendation\n\n"
                f"📌 {title} ({subject})\n"
                f"🔥 Priority: {priority.upper()}\n"
                f"⏰ Due: {due_date}\n\n"
                f"⚠️ No free slots available today."
            )

        return (
            f"📚 Study Recommendation\n\n"
            f"📌 {title} ({subject})\n"
            f"🔥 Priority: {priority.upper()}\n"
            f"⏰ Due: {due_date}\n\n"
            f"💡 Suggested study time:\n\n"
            f"{free_time_message}"
        )

    except Exception as e:
        return f"Error generating study suggestion: {str(e)}"