from core.nlp_parser import parse_event_request
from core.date_parser import parse_natural_date
from tools.add_event_tool import add_event_tool
import datetime


def normalize_date(date_str: str):
    """
    Convert natural language date to ISO format.
    Supports:
    - tomorrow
    - march 11
    - 11 march
    - 12/10/2026
    - next monday
    """

    if not date_str:
        return None

    # try natural language parser first
    parsed = parse_natural_date(date_str)

    if parsed:
        return parsed

    return date_str


def normalize_time(time_str: str):
    """
    Convert '2pm', '2:30pm', '14:00' to HH:MM format.
    """

    if not time_str:
        return None

    try:

        time_str = time_str.lower().replace(" ", "")

        if "am" in time_str or "pm" in time_str:

            if ":" in time_str:
                t = datetime.datetime.strptime(time_str, "%I:%M%p")
            else:
                t = datetime.datetime.strptime(time_str, "%I%p")

            return t.strftime("%H:%M")

        return time_str

    except Exception:
        return None


def schedule_from_text_tool(query: str):
    """
    Schedule an event using natural language.

    Examples:
    - schedule physics class tomorrow at 2pm
    - add meeting march 11 at 10am
    - schedule exam 11th march at 9am
    """

    try:

        if not query:
            return "Error: No scheduling request provided."

        parsed = parse_event_request(query)

        if not parsed:
            return "Sorry, I couldn't understand the scheduling request."

        # -------------------------
        # REQUIRED FIELDS
        # -------------------------

        title = parsed.get("title")
        date = parsed.get("date")
        start_time = parsed.get("start_time")
        end_time = parsed.get("end_time")

        if not title:
            return "Error: Event title missing."

        if not date:
            return "Error: Event date missing."

        if not start_time:
            return "Error: Event start time missing."

        # -------------------------
        # NORMALIZE VALUES
        # -------------------------

        date = normalize_date(date)

        start_time = normalize_time(start_time)
        end_time = normalize_time(end_time)

        if not start_time:
            return "Error: Invalid start time."

        # -------------------------
        # AUTO-GENERATE END TIME
        # -------------------------

        if not end_time:

            start_dt = datetime.datetime.strptime(start_time, "%H:%M")

            end_dt = start_dt + datetime.timedelta(hours=1)

            end_time = end_dt.strftime("%H:%M")

        # -------------------------
        # CREATE EVENT
        # -------------------------

        return add_event_tool(
            title,
            date,
            start_time,
            end_time,
        )

    except Exception as e:

        return f"Error scheduling event: {str(e)}"
