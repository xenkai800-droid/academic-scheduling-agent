from core.calendar_service import list_upcoming_events
from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time
import datetime


def daily_planner_tool(day: str = "today"):

    try:

        message = "📅 Daily Plan\n\n"

        # -------------------------
        # Normalize day
        # -------------------------

        today = datetime.date.today()

        if day.lower() == "tomorrow":
            target_date = today + datetime.timedelta(days=1)
            date_str = target_date.isoformat()
        else:
            target_date = today
            date_str = today.isoformat()

        # -------------------------
        # Events
        # -------------------------

        events = list_upcoming_events()

        if events:

            message += "📆 Upcoming Events\n"

            for event in events[:5]:

                title = event.get("summary", "Event")

                message += f"• {title}\n"

            message += "\n"

        else:

            message += "You have no upcoming events.\n\n"

        # -------------------------
        # Assignments
        # -------------------------

        assignments = get_assignments()
        print("DEBUG assignments:", assignments)
        if assignments:

            message += "\n📚 Assignments\n\n"

            for a in assignments[:5]:

                assignment_id = a[0]
                title = a[1]
                subject = a[2]
                due_date = a[3]

                message += f"• {title} ({subject}) — due {due_date}\n\n"

            message += "\n"

        else:

            message += "No assignments found.\n\n"

        # -------------------------
        # Free Time
        # -------------------------

        free_time = find_free_time(date=date_str)

        message += free_time

        return message

    except Exception as e:

        return f"Error creating daily plan: {str(e)}"
