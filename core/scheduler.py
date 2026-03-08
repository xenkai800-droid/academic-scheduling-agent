from core.calendar_service import create_event
from core.conflict_detector import has_conflict
from db.database import save_event


def schedule_event(title, date, start_time, end_time):

    try:

        # ------------------------------
        # BASIC VALIDATION
        # ------------------------------

        if not title:
            return "Error: Event title is required."

        if not date or not start_time or not end_time:
            return "Error: Missing date or time information."

        if start_time >= end_time:
            return "Error: End time must be after start time."

        # ------------------------------
        # CHECK CONFLICT
        # ------------------------------

        conflict, event_name = has_conflict(date, start_time, end_time)

        if conflict:
            return (
                "⚠️ Scheduling conflict detected.\n\n"
                f"This overlaps with:\n{event_name}"
            )

        # ------------------------------
        # CREATE GOOGLE CALENDAR EVENT
        # ------------------------------

        created_event = create_event(title, date, start_time, end_time)

        if not created_event or "id" not in created_event:
            return "Error: Failed to create event in Google Calendar."

        event_id = created_event["id"]

        # ------------------------------
        # SAVE TO LOCAL DATABASE
        # ------------------------------

        save_event(event_id, title, date, start_time, end_time)

        return "✅ Event created successfully"

    except Exception as e:

        return f"Error scheduling event: {str(e)}"
