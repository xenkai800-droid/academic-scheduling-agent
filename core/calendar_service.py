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

        # Load existing token
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # If no valid credentials
        if not creds or not creds.valid:

            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())

            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", SCOPES
                )

                creds = flow.run_local_server(port=0)

            # Save token
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        service = build("calendar", "v3", credentials=creds)

        return service

    except Exception as e:
        raise Exception(f"Google Calendar authentication failed: {str(e)}")


# --------------------------------------------------
# LIST UPCOMING EVENTS
# --------------------------------------------------


def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        ist = pytz.timezone(TIMEZONE)
        now = datetime.datetime.now(ist).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=20,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return events_result.get("items", [])

    except Exception:
        return []


# --------------------------------------------------
# CREATE EVENT
# --------------------------------------------------


def create_event(title, date, start_time, end_time):

    try:

        service = authenticate_google_calendar()

        event = {
            "summary": title.strip(),
            "start": {
                "dateTime": f"{date}T{start_time}:00",
                "timeZone": TIMEZONE,
            },
            "end": {
                "dateTime": f"{date}T{end_time}:00",
                "timeZone": TIMEZONE,
            },
        }

        created_event = (
            service.events().insert(calendarId="primary", body=event).execute()
        )

        return created_event

    except Exception as e:

        print("GOOGLE CALENDAR ERROR:", e)

        raise Exception("Failed to create event in Google Calendar.")


# --------------------------------------------------
# DELETE EVENT
# --------------------------------------------------


def delete_event(event_id):

    try:

        service = authenticate_google_calendar()

        service.events().delete(calendarId="primary", eventId=event_id).execute()

        return True

    except Exception:
        return False


# --------------------------------------------------
# CHECK DUPLICATE EVENT
# --------------------------------------------------


def event_exists_on_date(title, date):

    try:

        service = authenticate_google_calendar()

        ist = pytz.timezone(TIMEZONE)

        start_dt = ist.localize(datetime.datetime.fromisoformat(date + "T00:00:00"))

        end_dt = ist.localize(datetime.datetime.fromisoformat(date + "T23:59:59"))

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_dt.isoformat(),
                timeMax=end_dt.isoformat(),
                singleEvents=True,
            )
            .execute()
        )

        events = events_result.get("items", [])

        for event in events:

            if event.get("summary", "").strip().lower() == title.strip().lower():
                return True

        return False

    except Exception:
        return False
