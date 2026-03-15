import datetime

from core.calendar_service import list_upcoming_events
from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time


def daily_planner_tool(day: str = "today"):

    try:

        today = datetime.date.today()

        if day.lower() == "tomorrow":
            target = today + datetime.timedelta(days=1)
        else:
            target = today

        message = "📅 Daily Plan\n\n"

        # Upcoming events
        events = list_upcoming_events()

        if events:

            message += "📆 Upcoming Events\n\n"

            for event in events[:5]:

                title = event.get("summary", "Event")

                message += f"• {title}\n"

            message += "\n"

        else:
            message += "No upcoming events.\n\n"

        # Assignments
        assignments = get_assignments()

        if assignments:

            message += "📚 Assignments\n\n"

            for a in assignments[:5]:

                _, title, subject, due_date, _ = a

                message += f"• {title} ({subject}) — due {due_date}\n"

            message += "\n"

        else:

            message += "No assignments found.\n\n"

        # Free time
        free_time = find_free_time(date=target.isoformat())

        message += free_time

        return message

    except Exception as e:

        return f"Error generating daily plan: {str(e)}"
