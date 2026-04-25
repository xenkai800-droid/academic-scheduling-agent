import dateparser
import pytz
import re

TIMEZONE = "Asia/Kolkata"


def extract_date_phrase(text: str):
    """
    Extract likely date-related portion from full sentence.
    """

    text = text.lower()

    # -------------------------
    # 🔥 NEW: NUMERIC DATE SUPPORT
    # -------------------------

    numeric_match = re.search(
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        text
    )

    if numeric_match:
        return numeric_match.group(0)

    # -------------------------
    # EXISTING MONTH FORMATS
    # -------------------------

    match = re.search(
        r"\b(\d{1,2}(st|nd|rd|th)?\s+(january|february|march|april|may|june|july|august|september|october|november|december))\b",
        text,
    )

    if not match:
        match = re.search(
            r"\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}\b",
            text,
        )

    if match:
        return match.group(0)

    # fallback (for tomorrow, next monday, etc.)
    return text


def parse_natural_date(text: str):
    """
    Convert natural language dates into YYYY-MM-DD format.
    """

    if not text:
        return None

    date_text = extract_date_phrase(text)

    parsed = dateparser.parse(
        date_text,
        settings={
            "PREFER_DATES_FROM": "future",
            "TIMEZONE": TIMEZONE,
            "RETURN_AS_TIMEZONE_AWARE": False,
        },
    )

    if not parsed:
        return None

    return parsed.date().isoformat()