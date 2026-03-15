import os
import datetime
import pytz

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ["https://www.googleapis.com/auth/calendar"]
TIMEZONE = "Asia/Kolkata"


def authenticate_google_calendar():

    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:

            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json",
                SCOPES,
            )

            creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build("calendar", "v3", credentials=creds)

    return service


def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        ist = pytz.timezone(TIMEZONE)

        now = (datetime.datetime.now(ist) - datetime.timedelta(days=1)).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=100,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        return events

    except Exception:

        return []


def create_event(title, date, start_time, end_time):

    service = authenticate_google_calendar()

    ist = pytz.timezone(TIMEZONE)

    start_local = ist.localize(
        datetime.datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
    )

    end_local = ist.localize(
        datetime.datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
    )

    # convert to UTC
    start_utc = start_local.astimezone(pytz.utc)
    end_utc = end_local.astimezone(pytz.utc)

    event = {
        "summary": title.strip(),
        "start": {
            "dateTime": start_utc.isoformat(),
        },
        "end": {
            "dateTime": end_utc.isoformat(),
        },
    }

    created_event = service.events().insert(calendarId="primary", body=event).execute()

    return created_event


def delete_event(event_id):

    try:

        service = authenticate_google_calendar()

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        return True

    except Exception:
        return False


def event_exists_on_date(title, date):

    try:

        service = authenticate_google_calendar()

        ist = pytz.timezone(TIMEZONE)

        start_dt = ist.localize(
            datetime.datetime.strptime(f"{date} 00:00", "%Y-%m-%d %H:%M")
        )

        end_dt = ist.localize(
            datetime.datetime.strptime(f"{date} 23:59", "%Y-%m-%d %H:%M")
        )

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
