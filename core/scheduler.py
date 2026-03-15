import datetime

from core.calendar_service import create_event
from core.conflict_detector import has_conflict
from db.database import save_event, event_exists_locally
from tools.find_free_time_tool import find_free_time


def schedule_event(title, date, start_time, end_time):

    try:

        if not title:
            return "Error: Event title is required."

        if not date or not start_time or not end_time:
            return "Error: Missing date or time."

        title = title.strip()

        start = datetime.datetime.strptime(start_time, "%H:%M").time()
        end = datetime.datetime.strptime(end_time, "%H:%M").time()

        if start >= end:
            return "Error: End time must be after start time."

        # Prevent exact duplicate events
        if event_exists_locally(title, date, start_time):
            return (
                "⚠ This exact event already exists.\n"
                "Same title and start time found."
            )

        # Conflict detection
        conflict, event_name = has_conflict(date, start_time, end_time)

        if conflict:

            suggestion = find_free_time(date=date)

            return (
                "⚠ Scheduling conflict detected.\n\n"
                f"This overlaps with: {event_name}\n\n"
                "Suggested free slots:\n\n"
                f"{suggestion}"
            )

        created_event = create_event(title, date, start_time, end_time)

        if not created_event or "id" not in created_event:
            return "Error: Failed to create event."

        event_id = created_event["id"]

        save_event(event_id, title, date, start_time, end_time)

        return "✅ Event created successfully"

    except ValueError:
        return "Error: Invalid time format. Use HH:MM."

    except Exception as e:

        return f"Error scheduling event: {str(e)}"
