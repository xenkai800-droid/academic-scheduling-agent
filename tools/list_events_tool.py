from core.calendar_service import list_upcoming_events
import datetime
import pytz

TIMEZONE = "Asia/Kolkata"


# -----------------------------------
# CORE FUNCTION (STRUCTURED DATA)
# -----------------------------------

def get_events_structured(limit=50):

    try:

        events = list_upcoming_events()

        if not events:
            return []

        ist = pytz.timezone(TIMEZONE)

        structured = []

        for event in events[:limit]:

            title = event.get("summary") or "Untitled Event"
            start_info = event.get("start", {})
            end_info = event.get("end", {})

            if "dateTime" in start_info:

                start = datetime.datetime.fromisoformat(
                    start_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

                end = datetime.datetime.fromisoformat(
                    end_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

                structured.append({
                    "title": title,
                    "date": start.date(),
                    "start_time": start.strftime("%H:%M"),
                    "end_time": end.strftime("%H:%M"),
                    "display_time": start.strftime("%I:%M %p"),
                    "all_day": False,
                    "event_id": event.get("id"),
                })

            elif "date" in start_info:

                start = datetime.date.fromisoformat(start_info["date"])

                structured.append({
                    "title": title,
                    "date": start,
                    "start_time": None,
                    "end_time": None,
                    "display_time": "All Day",
                    "all_day": True,
                    "event_id": event.get("id"),
                })

        return structured

    except Exception:
        return []


# -----------------------------------
# FILTER FUNCTION
# -----------------------------------

def filter_events(events, mode=None):

    today = datetime.date.today()

    if mode == "today":
        return [e for e in events if e["date"] == today]

    elif mode == "tomorrow":
        tomorrow = today + datetime.timedelta(days=1)
        return [e for e in events if e["date"] == tomorrow]

    return events


# -----------------------------------
# USER TOOL
# -----------------------------------

def list_events_tool(query: str = ""):

    try:

        events = get_events_structured(limit=50)

        if not events:
            return "📭 You have no upcoming events."

        query = (query or "").lower()

        # 🔥 detect intent
        if "tomorrow" in query:
            events = filter_events(events, "tomorrow")
            title = "📅 Tomorrow's Schedule\n\n"

        elif "today" in query:
            events = filter_events(events, "today")
            title = "📅 Today's Schedule\n\n"

        else:
            title = "📅 Upcoming Events\n\n"

        if not events:
            return "📭 No events found."

        # sort by date + time
        events.sort(key=lambda x: (x["date"], x["start_time"] or "00:00"))

        message = title

        for e in events[:10]:

            formatted_date = e["date"].strftime("%d %b %Y")

            message += f"• {e['title']}\n"
            message += f"  🕒 {formatted_date} | {e['display_time']}\n\n"

        return message

    except Exception:
        return "❌ Failed to fetch events."