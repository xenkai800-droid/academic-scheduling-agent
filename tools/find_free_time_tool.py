import datetime
import pytz

from core.calendar_service import list_upcoming_events
from core.date_parser import normalize_date_input
from db.database import get_events_by_date

TIMEZONE = "Asia/Kolkata"

WORK_START = "09:00"
WORK_END = "17:00"

MIN_SLOT_MINUTES = 15


def merge_intervals(intervals):

    if not intervals:
        return []

    intervals.sort()

    merged = [intervals[0]]

    for current in intervals[1:]:

        last_start, last_end = merged[-1]
        curr_start, curr_end = current

        if curr_start <= last_end:
            merged[-1] = (last_start, max(last_end, curr_end))
        else:
            merged.append(current)

    return merged


def find_free_time(days: int = 1, date: str = None):

    ist = pytz.timezone(TIMEZONE)

    today = datetime.datetime.now(ist).date()

    if date:
        parsed = normalize_date_input(date)
        if not parsed:
            return "Invalid date."
        start_day = datetime.date.fromisoformat(parsed)
        end_day = start_day
    else:
        start_day = today
        end_day = today + datetime.timedelta(days=days - 1)

    events = list_upcoming_events()

    results = {}

    current_day = start_day

    while current_day <= end_day:

        intervals = []

        # ------------------------------
        # GOOGLE CALENDAR EVENTS
        # ------------------------------
        for event in events:

            start_info = event.get("start", {})
            end_info = event.get("end", {})

            if "dateTime" not in start_info:
                continue

            try:

                start_dt = datetime.datetime.fromisoformat(
                    start_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

                end_dt = datetime.datetime.fromisoformat(
                    end_info["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

            except Exception:
                continue

            if start_dt.date() != current_day:
                continue

            intervals.append((start_dt.time(), end_dt.time()))

        # ------------------------------
        # LOCAL DATABASE EVENTS
        # (fix for Google API delay)
        # ------------------------------
        local_events = get_events_by_date(current_day.isoformat())

        for title, start_time, end_time in local_events:

            try:

                start_t = datetime.datetime.strptime(start_time, "%H:%M").time()
                end_t = datetime.datetime.strptime(end_time, "%H:%M").time()

                intervals.append((start_t, end_t))

            except Exception:
                continue

        # ------------------------------
        # MERGE OVERLAPPING EVENTS
        # ------------------------------
        merged = merge_intervals(intervals)

        day_start = datetime.datetime.strptime(WORK_START, "%H:%M").time()
        day_end = datetime.datetime.strptime(WORK_END, "%H:%M").time()

        free_slots = []

        cursor = day_start

        for start, end in merged:

            if start > cursor:

                delta = datetime.datetime.combine(
                    current_day, start
                ) - datetime.datetime.combine(current_day, cursor)

                if delta.total_seconds() >= MIN_SLOT_MINUTES * 60:
                    free_slots.append((cursor, start))

            if end > cursor:
                cursor = end

        if cursor < day_end:

            delta = datetime.datetime.combine(
                current_day, day_end
            ) - datetime.datetime.combine(current_day, cursor)

            if delta.total_seconds() >= MIN_SLOT_MINUTES * 60:
                free_slots.append((cursor, day_end))

        formatted = []

        for s, e in free_slots:
            formatted.append(f"{s.strftime('%H:%M')} - {e.strftime('%H:%M')}")

        results[str(current_day)] = formatted

        current_day += datetime.timedelta(days=1)

    message = "🕒 Available Free Time\n\n"

    for date_key, slots in results.items():

        formatted_date = datetime.datetime.strptime(date_key, "%Y-%m-%d").strftime(
            "%d %b %Y"
        )

        message += f"📅 {formatted_date}\n"

        if not slots:
            message += "• No free slots\n\n"
            continue

        for slot in slots:
            message += f"• {slot}\n"

        message += "\n"

    return message
