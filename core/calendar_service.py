import datetime
import pytz
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"


# --------------------------------------------------
# AUTH
# --------------------------------------------------

def authenticate_google_calendar():
    try:
        import streamlit as st

        if "GOOGLE_CREDENTIALS" not in st.secrets:
            print("❌ GOOGLE_CREDENTIALS missing")
            return None

        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )

        creds = creds.with_subject("chocolatewrapper25@gmail.com")

        return build("calendar", "v3", credentials=creds)

    except Exception as e:
        print("❌ AUTH ERROR:", repr(e))
        return None


# --------------------------------------------------
# CREATE EVENT (SAFE)
# --------------------------------------------------

def create_event(title, date, start_time, end_time):

    try:
        service = authenticate_google_calendar()

        if not service:
            return None  # 🔥 fallback handled in scheduler

        ist = pytz.timezone(TIMEZONE)

        start_dt = ist.localize(
            datetime.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        )

        end_dt = ist.localize(
            datetime.datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        )

        event = {
            "summary": title.strip(),
            "start": {
                "dateTime": start_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": end_dt.isoformat(),
                "timeZone": TIMEZONE,
            },
        }

        created = service.events().insert(
            calendarId="primary",
            body=event
        ).execute()

        return created

    except Exception as e:
        print("❌ GOOGLE CREATE ERROR:", repr(e))
        return None  # 🔥 NEVER BLOCK


# --------------------------------------------------
# LIST EVENTS
# --------------------------------------------------

def list_upcoming_events():
    try:
        service = authenticate_google_calendar()
        if not service:
            return []

        IST = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(IST).astimezone(pytz.utc).isoformat()

        events = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events.get("items", [])

    except Exception as e:
        print("❌ LIST ERROR:", repr(e))
        return []


# --------------------------------------------------
# DELETE
# --------------------------------------------------

def delete_event(event_id):
    try:
        service = authenticate_google_calendar()
        if not service:
            return False

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        return True

    except Exception as e:
        print("❌ DELETE ERROR:", repr(e))
        return False


# --------------------------------------------------
# DUPLICATE CHECK (RESTORED)
# --------------------------------------------------

def event_exists_on_date(title, date):

    try:
        service = authenticate_google_calendar()
        if not service:
            return False

        ist = pytz.timezone(TIMEZONE)

        start_dt = ist.localize(
            datetime.datetime.strptime(date + " 00:00", "%Y-%m-%d %H:%M")
        )

        end_dt = ist.localize(
            datetime.datetime.strptime(date + " 23:59", "%Y-%m-%d %H:%M")
        )

        events = service.events().list(
            calendarId="primary",
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
        ).execute()

        for e in events.get("items", []):
            if e.get("summary", "").strip().lower() == title.lower():
                return True

        return False

    except Exception:
        return False