import re
import datetime


def parse_event_request(text):

    text = text.lower()

    today = datetime.date.today()

    # --------------------------------
    # DATE DETECTION
    # --------------------------------

    # tomorrow
    if "tomorrow" in text:
        date = today + datetime.timedelta(days=1)

    # today
    elif "today" in text:
        date = today

    # weekday detection
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

            days_ahead = found_day - today_weekday

            if days_ahead <= 0:
                days_ahead += 7

            date = today + datetime.timedelta(days=days_ahead)

        else:

            # fallback
            date = today

    # detect time
    time_match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", text)

    if not time_match:
        return None

    hour = int(time_match.group(1))
    minute = int(time_match.group(2) or 0)
    period = time_match.group(3)

    # convert to 24h
    if period == "pm" and hour != 12:
        hour += 12

    if period == "am" and hour == 12:
        hour = 0

    # validation
    if hour > 23 or minute > 59:
        return None

    start_time = f"{hour:02d}:{minute:02d}"

    end_hour = hour + 1
    end_time = f"{end_hour:02d}:{minute:02d}"

    title = text.replace("schedule", "").replace("at", "").strip()

    return {
        "title": title.title(),
        "date": date.isoformat(),
        "start_time": start_time,
        "end_time": end_time,
    }
