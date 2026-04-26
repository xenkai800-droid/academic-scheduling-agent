import os
import datetime
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"
CALENDAR_ID ="3c9092805c462e45b2a35f5354130403f35dc0063834de436fbdf03642f68e7e@group.calendar.google.com"

# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------
def authenticate_google_calendar():
    try:
        # ==================================================
        # 🔥 STREAMLIT MODE (Service Account)
        # ==================================================
        try:
            import streamlit as st
            

            if "GOOGLE_CREDENTIALS" in st.secrets:
                creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])

                creds = service_account.Credentials.from_service_account_info(
                    creds_dict,
                    scopes=SCOPES
                )

                return build("calendar", "v3", credentials=creds)

        except Exception as e:
            print("Service account fallback triggered:", e)

        # ==================================================
        # 💻 LOCAL MODE (Your ORIGINAL code untouched)
        # ==================================================

        # ❌ If credentials.json doesn't exist → skip Google completely
        if not os.path.exists("credentials.json"):
            print("⚠️ Google Calendar disabled (no credentials.json)")
            return None

        creds = None

        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    except Exception as e:
        print("GOOGLE AUTH ERROR:", e)
        return None


# --------------------------------------------------
# LIST EVENTS (🔥 FIXED: NO CACHE)
# --------------------------------------------------

def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        # 🚫 If Google not available → return empty (no crash)
        if not service:
            return []

        IST = pytz.timezone(TIMEZONE)

        now = datetime.datetime.now(IST).astimezone(pytz.utc).isoformat()

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=now,
            maxResults=100,
            singleEvents=True,
            orderBy="startTime",
        ).execute()

        return events_result.get("items", [])

    except Exception as e:
        print("LIST EVENTS ERROR:", e)
        return []


# --------------------------------------------------
# CREATE EVENT
# --------------------------------------------------

def create_event(title, date, start_time, end_time):

    try:

        service = authenticate_google_calendar()

        # 🚫 If Google not available → skip Google creation
        if not service:
            return None

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
            created_event = service.events().insert(
                calendarId=CALENDAR_ID,
                body=event
            ).execute()

            print("✅ GOOGLE EVENT CREATED:", created_event)

            if not created_event or "id" not in created_event:
                raise Exception("Invalid response from Google")

            return created_event

        except Exception as e:
            print("❌ GOOGLE INSERT FAILED:", e)
            raise e

    except Exception as e:
        print("GOOGLE CREATE EVENT ERROR:", e)
        return None


# --------------------------------------------------
# DELETE EVENT (🔥 IMPROVED)
# --------------------------------------------------

def delete_event(event_id):

    try:

        service = authenticate_google_calendar()

        if not service:
            return False

        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=event_id,
        ).execute()

        return True

    except Exception as e:
        print("❌ DELETE EVENT ERROR:", e)
        return False


# --------------------------------------------------
# DUPLICATE CHECK
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

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True,
        ).execute()

        for event in events_result.get("items", []):
            if event.get("summary", "").strip().lower() == title.strip().lower():
                return True

        return False

    except Exception as e:
        print("DUPLICATE CHECK ERROR:", e)
        return False