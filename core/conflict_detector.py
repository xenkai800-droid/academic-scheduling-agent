import datetime
import pytz
from core.calendar_service import list_upcoming_events

TIMEZONE = "Asia/Kolkata"


def has_conflict(date, start_time, end_time):

    try:
        import datetime
        import pytz
        from db.database import get_events_by_date
        from core.calendar_service import list_upcoming_events

        TIMEZONE = "Asia/Kolkata"
        ist = pytz.timezone(TIMEZONE)

        new_start = ist.localize(
            datetime.datetime.fromisoformat(f"{date}T{start_time}:00")
        )
        new_end = ist.localize(
            datetime.datetime.fromisoformat(f"{date}T{end_time}:00")
        )

        # ==================================================
        # 🔥 1. LOCAL EVENTS (PRIMARY SOURCE)
        # ==================================================
        local_events = get_events_by_date(date)

        for title, start, end in local_events:

            existing_start = ist.localize(
                datetime.datetime.fromisoformat(f"{date}T{start}:00")
            )
            existing_end = ist.localize(
                datetime.datetime.fromisoformat(f"{date}T{end}:00")
            )

            if new_start < existing_end and new_end > existing_start:
                return {
                    "conflict": True,
                    "event_name": title,
                }

        # ==================================================
        # 🔥 2. GOOGLE EVENTS (OPTIONAL)
        # ==================================================
        try:
            events = list_upcoming_events()
        except:
            events = []

        for event in events:

            start_data = event.get("start", {})
            end_data = event.get("end", {})

            if "dateTime" not in start_data:
                continue

            existing_start = datetime.datetime.fromisoformat(
                start_data["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

            existing_end = datetime.datetime.fromisoformat(
                end_data["dateTime"].replace("Z", "+00:00")
            ).astimezone(ist)

            if existing_start.date().isoformat() != date:
                continue

            if new_start < existing_end and new_end > existing_start:
                return {
                    "conflict": True,
                    "event_name": event.get("summary", "Existing Event"),
                }

        return {"conflict": False}

    except Exception as e:
        return {"conflict": False, "error": str(e)}