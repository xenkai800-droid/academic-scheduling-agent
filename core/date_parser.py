import dateparser
import pytz

TIMEZONE = "Asia/Kolkata"


def parse_natural_date(text: str):
    """
    Convert natural language dates into YYYY-MM-DD format.

    Supported examples:
    - march 11
    - 11 march
    - 11th march
    - 12/10/2026
    - tomorrow
    - next monday
    - this sunday
    - in 3 days
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
