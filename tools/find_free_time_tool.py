import datetime
import pytz

from core.calendar_service import list_upcoming_events
from core.date_parser import parse_natural_date

TIMEZONE = "Asia/Kolkata"
WORK_START = "09:00"
WORK_END = "17:00"

PERIODS = {
    "morning": ("06:00", "12:00"),
    "afternoon": ("12:00", "17:00"),
    "evening": ("17:00", "21:00"),
}

WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


# -----------------------------------
# DATE NORMALIZATION
# -----------------------------------

def normalize_date_input(date, today):

    if not date:
        return None

    date = date.lower()

    if date == "today":
        return today

    if date == "tomorrow":
        return today + datetime.timedelta(days=1)

    parsed = parse_natural_date(date)

    if parsed:
        return datetime.date.fromisoformat(parsed)

    try:
        parsed = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        if parsed.year < today.year:
            parsed = parsed.replace(year=today.year)

        return parsed

    except Exception:
        return None


# -----------------------------------
# CORE LOGIC (STRUCTURED)
# -----------------------------------

def get_free_time_structured(days=1, period=None, date=None, weekday=None):

    ist = pytz.timezone(TIMEZONE)
    today = datetime.datetime.now(ist).date()

    # ✅ FIXED DATE HANDLING
    if date == "tomorrow":
        parsed_date = today + datetime.timedelta(days=1)

    elif date == "today":
        parsed_date = today

    else:
        parsed_date = normalize_date_input(date, today)

    if parsed_date:
        start_day = parsed_date
        end_day = parsed_date

    elif weekday:
        weekday = weekday.lower()

        if weekday not in WEEKDAYS:
            return {}

        target = WEEKDAYS[weekday]
        days_ahead = (target - today.weekday()) % 7

        start_day = today + datetime.timedelta(days=days_ahead)
        end_day = start_day

    else:
        start_day = today
        end_day = today + datetime.timedelta(days=days - 1)

    events = []

    # 🔥 TRY GOOGLE EVENTS
    try:
        google_events = list_upcoming_events()
        if google_events:
            events.extend(google_events)
    except:
        pass

    # 🔥 ADD LOCAL EVENTS (CONVERT TO SAME FORMAT)
    from db.database import get_all_events

    local_events = get_all_events()

    for title, date, start, end in local_events:
        events.append({
            "summary": title,
            "start": {
                "dateTime": f"{date}T{start}:00"
            },
            "end": {
                "dateTime": f"{date}T{end}:00"
            }
        })
        
    results = {}

    current_day = start_day

    while current_day <= end_day:

        day_events = []

        for event in events:

            start_info = event.get("start", {})
            end_info = event.get("end", {})

            if "dateTime" not in start_info:
                continue

            try:
                start = datetime.datetime.fromisoformat(
                    start_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

                end = datetime.datetime.fromisoformat(
                    end_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

            except Exception:
                continue

            if start.date() == current_day:
                day_events.append((start.time(), end.time()))

        day_events.sort()

        free = []

        day_start = datetime.datetime.strptime(WORK_START, "%H:%M").time()
        day_end = datetime.datetime.strptime(WORK_END, "%H:%M").time()

        cursor = day_start

        for s, e in day_events:

            if s > cursor:
                free.append((cursor, s))

            if e > cursor:
                cursor = e

        if cursor < day_end:
            free.append((cursor, day_end))

        # PERIOD FILTER
        if period:
            period = period.lower()

            if period in PERIODS:

                p_start = datetime.datetime.strptime(PERIODS[period][0], "%H:%M").time()
                p_end = datetime.datetime.strptime(PERIODS[period][1], "%H:%M").time()

                filtered = []

                for s, e in free:
                    start = max(s, p_start)
                    end = min(e, p_end)

                    if start < end:
                        filtered.append((start, end))

                free = filtered

        results[current_day.isoformat()] = [
            {
                "start": s.strftime("%H:%M"),
                "end": e.strftime("%H:%M"),
                "display": f"{s.strftime('%H:%M')} - {e.strftime('%H:%M')}",
            }
            for s, e in free
        ]

        current_day += datetime.timedelta(days=1)

    return results


# -----------------------------------
# USER TOOL (TEXT OUTPUT)
# -----------------------------------

def find_free_time(query: str = "", days: int = 1, period: str = None, date: str = None, weekday: str = None, **kwargs):

    # ✅ FIX: PARSE QUERY PROPERLY
    if query:
        q = query.lower()

        if "tomorrow" in q:
            date = "tomorrow"

        elif "today" in q:
            date = "today"

        for p in PERIODS:
            if p in q:
                period = p

        for w in WEEKDAYS:
            if w in q:
                weekday = w

    results = get_free_time_structured(days, period, date, weekday)

    if not results:
        return "⚠️ No free time found."

    message = "🕒 Available Free Time\n\n"

    for date_key, slots in results.items():

        formatted_date = datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime(
            "%d %b %Y"
        )

        message += f"📅 {formatted_date}\n"

        if not slots:
            message += "• ❌ No free slots\n\n"
            continue

        for slot in slots:
            message += f"• {slot['display']}\n"

        message += "\n"

    return message