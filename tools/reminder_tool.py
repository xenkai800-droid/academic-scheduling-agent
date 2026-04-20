from core.reminder_engine import get_due_assignments
import datetime


def check_due_assignments_tool():
    """
    Check assignments that are due today, tomorrow, or already past due.
    """

    try:

        reminders = get_due_assignments()

        # 🔴 HANDLE EMPTY OR INVALID DATA
        if not reminders or not isinstance(reminders, list):
            return "✅ You have no assignments due today or tomorrow."

        today = datetime.date.today()

        message = "📚 Upcoming Assignment Deadlines:\n\n"

        for assignment in reminders:

            # 🔥 HANDLE DIFFERENT DATA FORMATS SAFELY
            try:
                # Case 1: tuple/list
                if isinstance(assignment, (list, tuple)) and len(assignment) >= 4:
                    _, title, subject, due = assignment[:4]

                # Case 2: dict
                elif isinstance(assignment, dict):
                    title = assignment.get("title", "Untitled")
                    subject = assignment.get("subject", "General")
                    due = assignment.get("due_date")

                else:
                    continue

                if not due:
                    continue

                subject = subject if subject else "General"

                due_date = datetime.date.fromisoformat(due)

                if due_date < today:
                    label = "❗ Past Due"

                elif due_date == today:
                    label = "⏰ Due Today"

                else:
                    label = "📅 Due Tomorrow"

                message += f"• {title} ({subject}) — {label}\n\n"

            except Exception:
                # skip broken entries instead of crashing
                continue

        return message if message.strip() != "📚 Upcoming Assignment Deadlines:" else "✅ No valid assignments found."

    except Exception as e:
        return f"Error checking assignments: {str(e)}"