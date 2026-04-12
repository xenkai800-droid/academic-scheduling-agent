from core.nlp_parser import parse_event_request
from core.date_parser import parse_natural_date
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
import datetime


def normalize_date(date_str: str):

    if not date_str:
        return None

    parsed = parse_natural_date(date_str)

    if parsed:
        return parsed

    return date_str


def normalize_time(time_str: str):

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

    try:

        if not query:
            return "❌ No scheduling request provided."

        parsed = parse_event_request(query)

        if not parsed:
            return "❌ I couldn't understand the scheduling request. Try rephrasing."

        title = parsed.get("title")
        date = parsed.get("date")
        start_time = parsed.get("start_time")
        end_time = parsed.get("end_time")

        if not title:
            return "❌ Missing event title."

        if not date:
            return "❌ Missing event date."

        if not start_time:
            return "❌ Missing start time."

        # -------------------------
        # NORMALIZE
        # -------------------------

        date = normalize_date(date)

        if not date:
            return "❌ Invalid date."

        start_time = normalize_time(start_time)
        end_time = normalize_time(end_time)

        if not start_time:
            return "❌ Invalid start time."

        # -------------------------
        # AUTO END TIME
        # -------------------------

        if not end_time:

            start_dt = datetime.datetime.strptime(start_time, "%H:%M")
            end_dt = start_dt + datetime.timedelta(hours=1)
            end_time = end_dt.strftime("%H:%M")

        # -------------------------
        # CREATE EVENT
        # -------------------------

        result = add_event_tool(
            title.strip(),
            date,
            start_time,
            end_time,
        )

        # -------------------------
        # CLEAN OUTPUT
        # -------------------------

        if "Error" in result or "⚠️" in result:
            return result

        clean_output = (
            f"✅ Event Scheduled Successfully\n\n"
            f"📌 {title.title()}\n"
            f"📅 {date}\n"
            f"🕒 {start_time} - {end_time}"
        )

        # -------------------------
        # EXAM → STUDY SUGGESTION
        # -------------------------

        if "exam" in title.lower():

            try:

                suggestion = find_free_time(date=date)

                clean_output += "\n\n📚 Study Recommendation:\n\n"
                clean_output += suggestion

            except Exception:
                pass

        return clean_output

    except Exception as e:

        return f"❌ Error scheduling event: {str(e)}"