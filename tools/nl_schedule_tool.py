from core.nlp_parser import parse_event_request
from tools.add_event_tool import add_event_tool
import datetime


def normalize_date(date_str: str):
    """Convert natural language date to ISO format."""

    if date_str.lower() == "today":
        return datetime.date.today().isoformat()

    if date_str.lower() == "tomorrow":
        return (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

    return date_str


def normalize_time(time_str: str):
    """Convert '2pm' → '14:00' format."""

    try:

        time_str = time_str.lower().replace(" ", "")

        if "am" in time_str or "pm" in time_str:

            t = datetime.datetime.strptime(time_str, "%I%p")

            return t.strftime("%H:%M")

        return time_str

    except:
        return time_str


def schedule_from_text_tool(query: str):
    """
    Schedule an event using natural language.
    Example: 'schedule physics class tomorrow at 2pm'
    """

    try:

        if not query:
            return "Error: No scheduling request provided."

        parsed = parse_event_request(query)

        if not parsed:
            return "Sorry, I couldn't understand the scheduling request."

        required_fields = ["title", "date", "start_time", "end_time"]

        for field in required_fields:
            if field not in parsed:
                return f"Error: Missing '{field}' in parsed request."

        # normalize values
        date = normalize_date(parsed["date"])
        start_time = normalize_time(parsed["start_time"])
        end_time = normalize_time(parsed["end_time"])

        return add_event_tool(
            parsed["title"],
            date,
            start_time,
            end_time,
        )

    except Exception as e:
        return f"Error scheduling event: {str(e)}"
