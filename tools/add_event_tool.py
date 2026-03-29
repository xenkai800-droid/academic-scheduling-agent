from core.scheduler import schedule_event
import datetime


def normalize_time(t: str):

    if not t:
        return t

    t = t.strip().lower()

    try:
        parsed = datetime.datetime.strptime(t, "%I%p")
        return parsed.strftime("%H:%M")
    except:
        pass

    try:
        parsed = datetime.datetime.strptime(t, "%I:%M%p")
        return parsed.strftime("%H:%M")
    except:
        pass

    try:
        parsed = datetime.datetime.strptime(t, "%H:%M")
        return parsed.strftime("%H:%M")
    except:
        pass

    return t


def normalize_date(d: str):
    d = d.strip().lower()

    today = datetime.date.today()

    if d == "today":
        return today.isoformat()

    if d == "tomorrow":
        return (today + datetime.timedelta(days=1)).isoformat()

    # already in correct format
    return d


def add_event_tool(title: str, date: str, start_time: str, end_time: str):

    try:

        if not title:
            return "⚠️ Event title is required."

        if not date:
            return "⚠️ Event date is required."

        if not start_time or not end_time:
            return "⚠️ Start and end time are required."

        # 🔥 FIX 1: normalize date
        date = normalize_date(date)

        # 🔥 FIX 2: normalize time
        start_time = normalize_time(start_time)
        end_time = normalize_time(end_time)

        title = title.strip()

        result = schedule_event(title, date, start_time, end_time)

        return result

    except Exception as e:

        return f"❌ Error creating event: {str(e)}"