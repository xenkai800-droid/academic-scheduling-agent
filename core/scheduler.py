from core.calendar_service import create_event
from core.conflict_detector import has_conflict
from db.database import save_event
import datetime
from tools.find_free_time_tool import find_free_time

# ------------------------------
# ACADEMIC CALENDAR (HOLIDAYS)
# ------------------------------

HOLIDAYS = [
    "2026-01-26",  # Republic Day
    "2026-08-15",  # Independence Day
    "2026-10-02",  # Gandhi Jayanti
    "2026-03-02",  # Holi
    "2026-03-20",  # Ugadi
    "2026-04-18",  # Good Friday
    "2026-08-29",  # Raksha Bandhan
    "2026-09-07",  # Janmashtami
    "2026-09-17",  # Ganesh Chaturthi
    "2026-10-12",  # Dussehra
    "2026-11-01",  # Diwali
    "2026-11-15",  # Guru Nanak Jayanti
    "2026-12-25",  # Christmas
]

# ------------------------------
# HOLIDAY / WEEKEND CHECK
# ------------------------------

def get_block_reason(date: str):

    try:
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        return None

    if date in HOLIDAYS:
        return "Academic Holiday"

    if dt.weekday() >= 5:
        return "Weekend (Non-working day)"

    return None


# ------------------------------
# MAIN SCHEDULER
# ------------------------------

def schedule_event(title, date, start_time, end_time):

    try:

        # ------------------------------
        # BASIC VALIDATION
        # ------------------------------

        if not title:
            return "❌ Event title is required."

        if not date or not start_time or not end_time:
            return "❌ Missing date or time information."

        try:
            start_dt = datetime.datetime.strptime(start_time, "%H:%M")
            end_dt = datetime.datetime.strptime(end_time, "%H:%M")
        except Exception:
            return "❌ Invalid time format."

        if start_dt >= end_dt:
            return "❌ End time must be after start time."

        # ------------------------------
        # HOLIDAY / WEEKEND CHECK
        # ------------------------------

        reason = get_block_reason(date)

        if reason:
            return (
                "⚠️ Scheduling Conflict Detected\n\n"
                f"📌 Reason: {reason}\n\n"
                "🚫 Scheduling is not allowed on this day.\n"
            )

        # ------------------------------
        # CONFLICT CHECK
        # ------------------------------

        conflict, event_name = has_conflict(date, start_time, end_time)

        if conflict:
            suggestion = find_free_time(date=date)

            return (
                "⚠️ Scheduling Conflict Detected\n\n"
                f"📌 Overlaps with: {event_name.title()}\n\n"
                "💡 Suggested Free Slots:\n\n"
                f"{suggestion}"
            )

        # ------------------------------
        # CREATE GOOGLE EVENT
        # ------------------------------

        created_event = create_event(title, date, start_time, end_time)

        if not created_event or "id" not in created_event:
            return "❌ Failed to create event in Google Calendar."

        event_id = created_event["id"]

        # ------------------------------
        # SAVE LOCALLY
        # ------------------------------

        save_event(event_id, title, date, start_time, end_time)

        return (
            "✅ Event Created Successfully\n\n"
            f"📌 {title.title()}\n"
            f"📅 {date}\n"
            f"🕒 {start_time} - {end_time}"
        )

    except Exception as e:
        return f"❌ Error scheduling event: {str(e)}"