from core.calendar_service import create_event, list_upcoming_events
from core.conflict_detector import has_conflict
from db.database import save_event
import datetime
from tools.find_free_time_tool import find_free_time

def is_weekend(date_str):
    try:
        date = datetime.date.fromisoformat(date_str)
        return date.weekday() >= 5  # 5 = Saturday, 6 = Sunday
    except Exception:
        return False

# -----------------------------------
# SEMESTER BREAKS
# -----------------------------------

SEMESTER_BREAKS = [
    ("2026-05-01", "2026-05-10"),
]


def is_semester_break(date_str):

    try:
        date = datetime.date.fromisoformat(date_str)

        for start, end in SEMESTER_BREAKS:
            start_d = datetime.date.fromisoformat(start)
            end_d = datetime.date.fromisoformat(end)

            if start_d <= date <= end_d:
                return True

        return False

    except Exception:
        return False


# -----------------------------------
# GOOGLE HOLIDAY DETECTION
# -----------------------------------

def is_google_holiday(date_str):

    try:

        events = list_upcoming_events()

        for event in events:

            start = event.get("start", {})
            title = event.get("summary", "").lower()

            if "date" not in start:
                continue

            if start["date"] != date_str:
                continue

            keywords = [
                "holiday", "festival", "independence",
                "republic", "diwali", "holi", "eid",
                "christmas", "gandhi"
            ]

            if any(k in title for k in keywords):
                return event.get("summary", "Holiday")

        return None

    except Exception:
        return None


# -----------------------------------
# MAIN SCHEDULER
# -----------------------------------

def schedule_event(title, date, start_time, end_time):

    try:

        # -------------------------
        # BASIC VALIDATION
        # -------------------------

        if not title:
            return "❌ Event title is required."

        if not date or not start_time or not end_time:
            return "❌ Missing date or time."

        try:
            start_dt = datetime.datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.datetime.strptime(end_time, "%H:%M")
        except Exception:
            return "❌ Invalid time format."

        if start_dt >= end_dt:
            return "❌ End time must be after start time."

        # -------------------------
        # SEMESTER BREAK
        # -------------------------

        if is_semester_break(date):
            return "⚠️ Semester Break - Scheduling blocked"
        
        # -------------------------
        # WEEKEND CHECK
        # -------------------------

        if is_weekend(date):
            return "⚠️ Weekend detected. Academic scheduling is restricted."
        
        # -------------------------
        # HOLIDAY
        # -------------------------

        holiday = is_google_holiday(date)

        if holiday:
            return f"⚠️ Holiday: {holiday} - Scheduling blocked"

        # -------------------------
        # 🔥 FIXED CONFLICT CHECK
        # -------------------------

        conflict_data = has_conflict(date, start_time, end_time)

        if conflict_data.get("conflict"):

            event_name = conflict_data.get("event_name", "Existing Event")

            suggestion = find_free_time(date=date)

            return (
                "⚠️ Scheduling Conflict Detected\n\n"
                f"📌 Overlaps with: {event_name}\n\n"
                f"💡 Suggested Free Slots:\n\n{suggestion}"
            )

        # -------------------------
        # CREATE EVENT
        # -------------------------

        created = create_event(title, date, start_time, end_time)

        if not created or "id" not in created:
            return "❌ Failed to create event"

        save_event(created["id"], title, date, start_time, end_time)

        return (
            "✅ Event Created Successfully\n\n"
            f"📌 {title}\n"
            f"📅 {date}\n"
            f"🕒 {start_time} - {end_time}"
        )

    except Exception as e:
        return f"❌ Error scheduling event: {str(e)}"