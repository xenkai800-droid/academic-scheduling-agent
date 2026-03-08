from core.reminder_engine import get_due_assignments
import datetime


def check_due_assignments_tool():
    """
    Check assignments that are due today, tomorrow, or already past due.
    """

    try:

        reminders = get_due_assignments()

        if not reminders:
            return "✅ You have no assignments due today or tomorrow."

        today = datetime.date.today()

        message = "📚 Upcoming Assignment Deadlines:\n\n"

        for assignment in reminders:

            # safe unpack
            _, title, subject, due = assignment[:4]

            subject = subject if subject else "General"

            due_date = datetime.date.fromisoformat(due)

            if due_date < today:
                label = "❗ Past Due"

            elif due_date == today:
                label = "⏰ Due Today"

            else:
                label = "📅 Due Tomorrow"

            message += f"• {title} ({subject}) — {label}\n\n"

        return message

    except Exception as e:
        return f"Error checking assignments: {str(e)}"
