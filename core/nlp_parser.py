import re
import datetime
from core.date_parser import parse_natural_date


def parse_event_request(text):

    original_text = text
    text = text.lower().strip()

    today = datetime.date.today()

    # --------------------------------
    # DATE DETECTION
    # --------------------------------

    natural_date = parse_natural_date(text)

    if natural_date:
        date = datetime.date.fromisoformat(natural_date)

    else:

        if "tomorrow" in text:
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
                today_weekday = today.weekday()
                days_ahead = (found_day - today_weekday) % 7
                date = today + datetime.timedelta(days=days_ahead)

            else:
                date = today

    # --------------------------------
    # TIME DETECTION
    # --------------------------------

    time_match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", text)

    if not time_match:
        return None

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
    # AUTO END TIME (1 hour)
    # --------------------------------

    if hour == 23:
        end_time = "23:59"
    else:
        end_hour = hour + 1
        end_time = f"{end_hour:02d}:{minute:02d}"

    # --------------------------------
    # TITLE EXTRACTION (ROBUST)
    # --------------------------------

    cleaned = text

    # remove command words
    command_words = ["schedule", "add", "create", "set", "plan"]

    for word in command_words:
        cleaned = re.sub(rf"\b{word}\b", "", cleaned)

    # remove date keywords
    cleaned = re.sub(r"\b(today|tomorrow)\b", "", cleaned)

    # remove weekdays
    cleaned = re.sub(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        "",
        cleaned,
    )

    # remove time expressions ONLY (safe)
    cleaned = re.sub(
        r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b",
        "",
        cleaned,
    )

    # remove connectors
    cleaned = re.sub(r"\b(at|on|for|to)\b", "", cleaned)

    # remove months
    cleaned = re.sub(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        "",
        cleaned,
    )

    # clean spaces
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # fallback
    if not cleaned:
        cleaned = "event"

    title = cleaned.title()

    # --------------------------------
    # COURSE TYPE DETECTION (SAFE)
    # --------------------------------

    if "exam" in text and "exam" not in title.lower():
        title += " Exam"

    elif "lab" in text and "lab" not in title.lower():
        title += " Lab"

    elif "lecture" in text and "lecture" not in title.lower():
        title += " Lecture"

    elif "tutorial" in text and "tutorial" not in title.lower():
        title += " Tutorial"

    return {
        "title": title,
        "date": date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
    }
