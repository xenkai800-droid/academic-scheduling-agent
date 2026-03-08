import datetime
import pytz
from core.calendar_service import list_upcoming_events

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


def find_free_time(
    days: int = 1, period: str = None, date: str = None, weekday: str = None
):

    ist = pytz.timezone(TIMEZONE)

    today = datetime.datetime.now(ist).date()

    # -----------------------------------
    # NORMALIZE NATURAL LANGUAGE DATES
    # -----------------------------------

    if date == "today":
        date = today.isoformat()

    elif date == "tomorrow":
        date = (today + datetime.timedelta(days=1)).isoformat()

    # Fix LLM wrong-year guesses
    elif date:
        try:
            parsed = datetime.datetime.strptime(date, "%Y-%m-%d").date()

            if parsed.year < today.year:
                parsed = parsed.replace(year=today.year)

            date = parsed.isoformat()

        except:
            return "Invalid date format. Please use YYYY-MM-DD."

    # -----------------------------------
    # DETERMINE TARGET DATE RANGE
    # -----------------------------------

    if date:
        start_day = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        end_day = start_day

    elif weekday:
        weekday = weekday.lower()

        if weekday not in WEEKDAYS:
            return "Invalid weekday."

        target = WEEKDAYS[weekday]
        days_ahead = (target - today.weekday()) % 7

        start_day = today + datetime.timedelta(days=days_ahead)
        end_day = start_day

    else:
        start_day = today + datetime.timedelta(days=days)
        end_day = start_day

    events = list_upcoming_events()

    results = {}

    current_day = start_day

    while current_day <= end_day:

        day_events = []

        for event in events:

            if "dateTime" not in event["start"]:
                continue

            start = datetime.datetime.fromisoformat(
                event["start"]["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

            end = datetime.datetime.fromisoformat(
                event["end"]["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

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

        # -----------------------------------
        # FILTER BY PERIOD
        # -----------------------------------

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

        formatted_slots = []

        for s, e in free:
            formatted_slots.append(f"{s.strftime('%H:%M')} - {e.strftime('%H:%M')}")

        results[str(current_day)] = formatted_slots

        current_day += datetime.timedelta(days=1)

    if not results:
        return "No free time found."

    message = "🕒 Your Free Time\n\n"

    for date_key, slots in results.items():

        formatted_date = datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime(
            "%d %b %Y"
        )

        message += f"📅 {formatted_date}\n"

        if not slots:
            message += "• No free slots\n\n"
            continue

        for slot in slots:
            message += f"\n• {slot}\n"

        message += "\n"

    return message
