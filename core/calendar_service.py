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

        # Load saved token
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)

        # Refresh or create new token
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

        print("GOOGLE AUTH ERROR:", e)

        raise Exception("Google Calendar authentication failed.")


# --------------------------------------------------
# LIST UPCOMING EVENTS
# --------------------------------------------------


def list_upcoming_events():

    try:

        service = authenticate_google_calendar()

        ist = pytz.timezone(TIMEZONE)

        # look back one day so today's events aren't missed
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

        print("DEBUG: EVENTS FROM GOOGLE:", len(events))

        for e in events:
            print("EVENT:", e.get("summary"), e.get("start"))

        return events

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

        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event,
            )
            .execute()
        )

        print("DEBUG: EVENT CREATED:", created_event.get("summary"))
        print("DEBUG: EVENT ID:", created_event.get("id"))

        return created_event

    except Exception as e:

        print("GOOGLE CREATE EVENT ERROR:", e)

        raise Exception("Failed to create event in Google Calendar.")


# --------------------------------------------------
# DELETE EVENT
# --------------------------------------------------


def delete_event(event_id):

    try:

        service = authenticate_google_calendar()

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        print("DEBUG: EVENT DELETED:", event_id)

        return True

    except Exception as e:

        print("DELETE EVENT ERROR:", e)

        return False


# --------------------------------------------------
# CHECK DUPLICATE EVENT
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

    except Exception as e:

        print("DUPLICATE CHECK ERROR:", e)

        return False
