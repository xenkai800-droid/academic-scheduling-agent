import re
import datetime
from core.date_parser import parse_natural_date


def parse_event_request(text):

    text = text.lower()

    today = datetime.date.today()

    # --------------------------------
    # DATE DETECTION (NATURAL LANGUAGE)
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
    # AUTO END TIME (1 hour event)
    # --------------------------------

    if hour == 23:
        end_hour = 23
        end_minute = 59
    else:
        end_hour = hour + 1
        end_minute = minute

    end_time = f"{end_hour:02d}:{end_minute:02d}"

    # --------------------------------
    # CLEAN TITLE
    # --------------------------------

    cleaned = text

    keywords = [
        "schedule",
        "add",
        "create",
        "meeting",
        "event",
        "class",
    ]

    for word in keywords:
        cleaned = cleaned.replace(word, "")

    for word in ["today", "tomorrow"]:
        cleaned = cleaned.replace(word, "")

    for day in [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]:
        cleaned = cleaned.replace(day, "")

    # remove time expressions
    cleaned = re.sub(r"\d{1,2}(?::\d{2})?\s*(am|pm)?", "", cleaned)

    cleaned = cleaned.replace("at", "")

    title = cleaned.strip().title()

    if not title:
        title = "Event"

    return {
        "title": title,
        "date": date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
    }
