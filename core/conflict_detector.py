import datetime
import pytz
from core.calendar_service import list_upcoming_events

TIMEZONE = "Asia/Kolkata"


def has_conflict(date, start_time, end_time):

    try:

        ist = pytz.timezone(TIMEZONE)

        new_start = ist.localize(
            datetime.datetime.fromisoformat(f"{date}T{start_time}:00")
        )

        new_end = ist.localize(datetime.datetime.fromisoformat(f"{date}T{end_time}:00"))

        events = list_upcoming_events()

        for event in events:

            start_data = event.get("start", {})
            end_data = event.get("end", {})

            if "dateTime" not in start_data or "dateTime" not in end_data:
                continue

            existing_start = datetime.datetime.fromisoformat(
                start_data["dateTime"].replace("Z", "+00:00")
            )
            existing_end = datetime.datetime.fromisoformat(
                end_data["dateTime"].replace("Z", "+00:00")
            )

            # Convert to same timezone if needed
            if existing_start.tzinfo is None:
                existing_start = ist.localize(existing_start)

            if existing_end.tzinfo is None:
                existing_end = ist.localize(existing_end)

            if existing_start.date() != new_start.date():
                continue

            # Overlap check
            if new_start < existing_end and new_end > existing_start:

                return True, event.get("summary", "Existing Event")

        return False, None

    except Exception:

        # If anything fails we assume no conflict
        return False, None
