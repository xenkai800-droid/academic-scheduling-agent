import os
import datetime
import pytz
import json

from googleapiclient.discovery import build
from google.oauth2 import service_account

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"


# --------------------------------------------------
# AUTH (STREAMLIT ONLY — NO LOCAL FALLBACK)
# --------------------------------------------------

def authenticate_google_calendar():
    try:
        import streamlit as st

        if "GOOGLE_CREDENTIALS" not in st.secrets:
            print("❌ GOOGLE_CREDENTIALS missing in secrets")
            return None

        creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

        creds = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=SCOPES
        )

        # 🔥 REQUIRED: act as real user
        creds = creds.with_subject("chocolatewrapper25@gmail.com")

        service = build("calendar", "v3", credentials=creds)

        print("✅ Google service initialized")

        return service

    except Exception as e:
        print("❌ AUTH ERROR:", repr(e))
        return None


# --------------------------------------------------
# CREATE EVENT (FINAL)
# --------------------------------------------------

def create_event(title, date, start_time, end_time):

    try:

        print("\n🚀 CREATE EVENT STARTED")

        service = authenticate_google_calendar()

        if not service:
            return "ERROR: Google service not initialized"

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

        try:
            print("📤 INSERTING EVENT INTO GOOGLE")

            created_event = service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            print("✅ SUCCESS:", created_event)

            return created_event

        except Exception as e:
            print("❌ INSERT ERROR:", repr(e))
            return f"ERROR: {repr(e)}"

    except Exception as e:
        print("❌ CREATE EVENT ERROR:", repr(e))
        return f"ERROR: {repr(e)}"


# --------------------------------------------------
# LIST EVENTS (SAFE)
# --------------------------------------------------

def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        if not service:
            return []

        IST = pytz.timezone(TIMEZONE)

        now = datetime.datetime.now(IST).astimezone(pytz.utc).isoformat()

        events_result = service.events().list(
            calendarId="primary",
            timeMin=now,
            maxResults=50,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events_result.get("items", [])

    except Exception as e:
        print("❌ LIST ERROR:", repr(e))
        return []


# --------------------------------------------------
# DELETE EVENT
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