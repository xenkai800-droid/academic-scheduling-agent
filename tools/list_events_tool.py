from core.calendar_service import list_upcoming_events
import datetime
import pytz

TIMEZONE = "Asia/Kolkata"


def list_events_tool():

    events = list_upcoming_events()

    if not events:
        return "You have no upcoming events."

    ist = pytz.timezone(TIMEZONE)

    message = "📅 Your Upcoming Events:\n\n"

    for event in events[:10]:

        title = event.get("summary", "Untitled Event")

        start_info = event.get("start", {})

        # timed event
        if "dateTime" in start_info:

            start = datetime.datetime.fromisoformat(
                start_info["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

            time_str = start.strftime("%d %b %Y | %I:%M %p")

        # all-day event
        elif "date" in start_info:

            start = datetime.date.fromisoformat(start_info["date"])

            time_str = start.strftime("%d %b %Y | All Day")

        else:
            continue

        message += f"• {title}\n🕒 {time_str}\n\n"

    return message
