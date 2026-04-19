import re
import datetime
from core.date_parser import parse_natural_date


def parse_event_request(text):

    if not text or not text.strip():
        return None

    original_text = text
    text = text.lower().strip()

    today = datetime.date.today()

    # --------------------------------
    # DATE DETECTION
    # --------------------------------

    natural_date = parse_natural_date(text)

    if natural_date:
        date = datetime.date.fromisoformat(natural_date)

    elif "tomorrow" in text:
        date = today + datetime.timedelta(days=1)

    elif "today" in text:
        date = today

    else:

        weekdays = {
            "monday": 0,
            "tuesday": 1,
            "wednesday": 2,
            "thursday": 3,
            "friday": 4,
            "saturday": 5,
            "sunday": 6,
        }

        found_day = None

        for day in weekdays:
            if day in text:
                found_day = weekdays[day]
                break

        if found_day is not None:
            days_ahead = (found_day - today.weekday()) % 7
            date = today + datetime.timedelta(days=days_ahead)
        else:
            date = today

    # --------------------------------
    # TIME RANGE DETECTION (NEW)
    # --------------------------------

    range_match = re.search(
        r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)\s*(to|-)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)",
        text,
    )

    if range_match:

        def convert(h, m, p):
            h = int(h)
            m = int(m or 0)

            if p == "pm" and h != 12:
                h += 12
            if p == "am" and h == 12:
                h = 0

            return h, m

        sh, sm = convert(range_match.group(1), range_match.group(2), range_match.group(3))
        eh, em = convert(range_match.group(5), range_match.group(6), range_match.group(7))

        if sh > 23 or eh > 23 or sm > 59 or em > 59:
            return None

        start_time = f"{sh:02d}:{sm:02d}"
        end_time = f"{eh:02d}:{em:02d}"

    else:

        # --------------------------------
        # SINGLE TIME DETECTION
        # --------------------------------

        time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text)

        if not time_match:
            hour = 10
            minute = 0
        else:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2) or 0)
            period = time_match.group(3)

            if period == "pm" and hour != 12:
                hour += 12
            if period == "am" and hour == 12:
                hour = 0

        if hour > 23 or minute > 59:
            return None

        start_time = f"{hour:02d}:{minute:02d}"

        # --------------------------------
        # COURSE TYPE DETECTION
        # --------------------------------

        course_type = None

        if "exam" in text:
            course_type = "Exam"
        elif "lab" in text or "practical" in text:
            course_type = "Lab"
        elif "lecture" in text or "class" in text:
            course_type = "Lecture"
        elif "tutorial" in text:
            course_type = "Tutorial"

        # --------------------------------
        # SMART DURATION
        # --------------------------------

        if course_type == "Lab":
            duration_hours = 2
        elif course_type == "Exam":
            duration_hours = 2
        else:
            duration_hours = 1

        start_dt = datetime.datetime.strptime(start_time, "%H:%M")
        end_dt = start_dt + datetime.timedelta(hours=duration_hours)

        if end_dt.day != start_dt.day:
            end_time = "23:59"
        else:
            end_time = end_dt.strftime("%H:%M")

    # --------------------------------
    # TITLE EXTRACTION
    # --------------------------------

    cleaned = text

    cleaned = re.sub(r"\b(schedule|add|create|set|plan)\b", "", cleaned)
    cleaned = re.sub(r"\b(today|tomorrow)\b", "", cleaned)

    cleaned = re.sub(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        "",
        cleaned,
    )

    cleaned = re.sub(r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b", "", cleaned)
    cleaned = re.sub(r"\b(at|on|for|to|-)\b", "", cleaned)

    cleaned = re.sub(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        "",
        cleaned,
    )

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    if not cleaned:
        cleaned = "Event"

    title = cleaned.title()

    # --------------------------------
    # COURSE TYPE (FINAL)
    # --------------------------------

    course_type = None

    if "exam" in text:
        course_type = "Exam"
    elif "lab" in text or "practical" in text:
        course_type = "Lab"
    elif "lecture" in text or "class" in text:
        course_type = "Lecture"
    elif "tutorial" in text:
        course_type = "Tutorial"

    if course_type and course_type.lower() not in title.lower():
        title += f" {course_type}"

    return {
        "title": title,
        "date": date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
        "course_type": course_type or "General",
    }