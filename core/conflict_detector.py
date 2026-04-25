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

        new_end = ist.localize(
            datetime.datetime.fromisoformat(f"{date}T{end_time}:00")
        )

        events = list_upcoming_events()

        if not events:
            from db.database import get_all_events
            events = get_all_events()
        for event in events:

            start_data = event.get("start", {})
            end_data = event.get("end", {})

            # skip all-day events
            if "dateTime" not in start_data or "dateTime" not in end_data:
                continue

            existing_start = datetime.datetime.fromisoformat(
                start_data["dateTime"].replace("Z", "+00:00")
            )
            existing_end = datetime.datetime.fromisoformat(
                end_data["dateTime"].replace("Z", "+00:00")
            )

            # normalize timezone
            if existing_start.tzinfo is None:
                existing_start = ist.localize(existing_start)
            else:
                existing_start = existing_start.astimezone(ist)

            if existing_end.tzinfo is None:
                existing_end = ist.localize(existing_end)
            else:
                existing_end = existing_end.astimezone(ist)

            # only same day
            if existing_start.date() != new_start.date():
                continue

            # overlap condition
            if new_start < existing_end and new_end > existing_start:

                return {
                    "conflict": True,
                    "event_name": event.get("summary", "Existing Event"),
                    "event_start": existing_start.strftime("%H:%M"),
                    "event_end": existing_end.strftime("%H:%M"),
                }

        return {
            "conflict": False
        }

    except Exception as e:

        return {
            "conflict": False,
            "error": str(e)
        }