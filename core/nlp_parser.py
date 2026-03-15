import re
import datetime
from core.date_parser import parse_natural_date


TIME_REGEX = r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b"


def parse_time_component(hour, minute, period):

    hour = int(hour)
    minute = int(minute or 0)

    if period:
        period = period.lower()

        if period == "pm" and hour != 12:
            hour += 12

        if period == "am" and hour == 12:
            hour = 0

    if hour > 23 or minute > 59:
        return None

    return f"{hour:02d}:{minute:02d}"


def extract_times(text):

    matches = list(re.finditer(TIME_REGEX, text))

    if not matches:
        return None, None

    start = matches[0]

    start_time = parse_time_component(
        start.group(1),
        start.group(2),
        start.group(3),
    )

    if not start_time:
        return None, None

    end_time = None

    if len(matches) > 1:

        end = matches[1]

        end_time = parse_time_component(
            end.group(1),
            end.group(2),
            end.group(3),
        )

    return start_time, end_time


def extract_date(text):

    parsed = parse_natural_date(text)

    if parsed:
        return parsed

    today = datetime.date.today()

    if "tomorrow" in text:
        return (today + datetime.timedelta(days=1)).isoformat()

    if "today" in text:
        return today.isoformat()

    return today.isoformat()


def clean_title(text):

    text = text.lower()

    # remove time expressions
    text = re.sub(TIME_REGEX, "", text)

    # remove date words FIRST
    text = re.sub(r"\b(today|tomorrow)\b", "", text)

    text = re.sub(
        r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
        "",
        text,
    )

    text = re.sub(
        r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\b",
        "",
        text,
    )

    # remove numeric dates
    text = re.sub(r"\b\d{1,2}(st|nd|rd|th)?\b", "", text)

    # remove scheduling keywords (whole words only)
    keywords = [
        "schedule",
        "add",
        "create",
        "event",
        "meeting",
        "class",
        "at",
        "to",
        "from",
        "on",
    ]

    for k in keywords:
        text = re.sub(rf"\b{k}\b", "", text)

    # normalize spaces
    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    if not text:
        return "Event"

    return text.title()


def parse_event_request(text):

    text = text.lower()

    date = extract_date(text)

    start_time, end_time = extract_times(text)

    if not start_time:
        return None

    title = clean_title(text)

    return {
        "title": title,
        "date": date,
        "start_time": start_time,
        "end_time": end_time,
    }
