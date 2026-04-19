import os
import datetime
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

def authenticate_google_calendar():

    try:

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
        raise Exception("Google Calendar authentication failed.")


# --------------------------------------------------
# LIST EVENTS (🔥 FIXED: NO CACHE)
# --------------------------------------------------

def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        now = datetime.datetime.utcnow().isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
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

        return (
            service.events()
            .insert(calendarId="primary", body=event)
            .execute()
        )

    except Exception as e:
        print("GOOGLE CREATE EVENT ERROR:", e)
        raise Exception("Failed to create event.")


# --------------------------------------------------
# DELETE EVENT (🔥 IMPROVED)
# --------------------------------------------------

def delete_event(event_id):

    try:

        service = authenticate_google_calendar()

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        print(f"✅ Deleted event: {event_id}")

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

        ist = pytz.timezone(TIMEZONE)

        start_dt = ist.localize(
            datetime.datetime.strptime(date + " 00:00", "%Y-%m-%d %H:%M")
        )

        end_dt = ist.localize(
            datetime.datetime.strptime(date + " 23:59", "%Y-%m-%d %H:%M")
        )

        events_result = service.events().list(
            calendarId="primary",
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