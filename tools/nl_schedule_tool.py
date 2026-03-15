from core.nlp_parser import parse_event_request
from tools.add_event_tool import add_event_tool


def schedule_from_text_tool(query: str):

    try:

        if not query:
            return "Error: No scheduling request provided."

        parsed = parse_event_request(query)

        if not parsed:
            return (
                "I couldn't understand the scheduling request.\n\n"
                "Example:\n"
                "schedule physics tomorrow 2pm to 4pm"
            )

        title = parsed.get("title")
        date = parsed.get("date")
        start_time = parsed.get("start_time")
        end_time = parsed.get("end_time")

        if not start_time:

            return (
                "Please specify a start time.\n\n"
                "Example:\n"
                "schedule physics tomorrow at 2pm"
            )

        if not end_time:

            return (
                "Please specify how long the event lasts.\n\n"
                "Example:\n"
                "schedule physics tomorrow 2pm to 4pm"
            )

        return add_event_tool(
            title,
            date,
            start_time,
            end_time,
        )

    except Exception as e:

        return f"Error scheduling event: {str(e)}"
