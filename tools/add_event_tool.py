from core.scheduler import schedule_event


def add_event_tool(title: str, date: str, start_time: str, end_time: str):
    """
    Create a calendar event.

    Parameters
    ----------
    title : str
        Title of the event
    date : str
        Date in YYYY-MM-DD format
    start_time : str
        Start time in HH:MM format
    end_time : str
        End time in HH:MM format
    """

    try:

        # Validate inputs
        if not title:
            return "⚠️ Event title is required."

        if not date:
            return "⚠️ Event date is required."

        if not start_time or not end_time:
            return "⚠️ Start and end time are required."

        # Clean title
        title = title.strip()

        # Call scheduler (handles conflict detection + event creation)
        result = schedule_event(title, date, start_time, end_time)

        return result

    except Exception as e:

        return f"❌ Error creating event: {str(e)}"
