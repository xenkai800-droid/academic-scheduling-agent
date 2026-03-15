import datetime
import pytz
from core.calendar_service import list_upcoming_events

TIMEZONE = "Asia/Kolkata"


def has_conflict(date, start_time, end_time):

    ist = pytz.timezone(TIMEZONE)

    try:

        new_start = ist.localize(
            datetime.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        )

        new_end = ist.localize(
            datetime.datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        )

    except Exception:
        return False, None

    events = list_upcoming_events()

    for event in events:

        start_info = event.get("start", {})
        end_info = event.get("end", {})

        if "dateTime" not in start_info or "dateTime" not in end_info:
            continue

        try:

            existing_start = datetime.datetime.fromisoformat(
                start_info["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

            existing_end = datetime.datetime.fromisoformat(
                end_info["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

        except Exception:
            continue

        if existing_start.date() != new_start.date():
            continue

        if new_start < existing_end and new_end > existing_start:

            return True, event.get("summary", "Existing Event")

    return False, None
