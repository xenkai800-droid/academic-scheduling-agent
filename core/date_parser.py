import dateparser
import datetime
import pytz

TIMEZONE = "Asia/Kolkata"


def parse_natural_date(text: str):
    """
    Convert natural language dates into YYYY-MM-DD format.
    """

    if not text:
        return None

    parsed = dateparser.parse(
        text,
        settings={
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": TIMEZONE,
            "RETURN_AS_TIMEZONE_AWARE": False,
        },
    )

    if not parsed:
        return None

    return parsed.date().isoformat()


def normalize_date_input(text: str):

    if not text:
        return None

    text = text.strip().lower()

    today = datetime.date.today()

    if text == "today":
        return today.isoformat()

    if text == "tomorrow":
        return (today + datetime.timedelta(days=1)).isoformat()

    parsed = parse_natural_date(text)

    if parsed:
        return parsed

    try:
        dt = datetime.datetime.strptime(text, "%Y-%m-%d").date()
        return dt.isoformat()
    except Exception:
        return None
