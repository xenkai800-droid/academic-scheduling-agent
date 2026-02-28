import streamlit as st
from core.calendar_service import list_upcoming_events, create_event
from db.database import initialize_database, save_event
import datetime

# Initialize DB
initialize_database()

st.set_page_config(
    page_title="Academic Scheduling Agent",
    layout="centered"
)

# -------------------------
# SIDEBAR
# -------------------------

st.sidebar.title("Academic Scheduling Agent")
st.sidebar.markdown("Track A – Calendar Integration Module")

page = st.sidebar.radio(
    "Navigation",
    ["Create Event", "View Upcoming Events"]
)

st.title("Academic Scheduling Agent")

st.markdown("---")

# -------------------------
# CREATE EVENT PAGE
# -------------------------

if page == "Create Event":

    st.subheader("Create New Calendar Event")

    col1, col2 = st.columns(2)

    with col1:
        title = st.text_input("Event Title")
        date = st.date_input("Event Date")

    with col2:
        start_time = st.time_input("Start Time")
        end_time = st.time_input("End Time")

    if st.button("Create Event"):

        # Basic validation
        if not title:
            st.error("Event title cannot be empty.")
        elif end_time <= start_time:
            st.error("End time must be later than start time.")
        else:
            with st.spinner("Creating event..."):
                created_event = create_event(
                    title,
                    date.isoformat(),
                    start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M")
                )

                save_event(
                    created_event["id"],
                    title,
                    date.isoformat(),
                    start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M")
                )

            st.success("Event created and stored successfully.")

# -------------------------
# VIEW EVENTS PAGE
# -------------------------

elif page == "View Upcoming Events":

    st.subheader("Upcoming Calendar Events")

    if st.button("Refresh Events"):
        with st.spinner("Fetching events..."):
            events = list_upcoming_events()

        if not events:
            st.info("No upcoming events found.")
        else:
            st.write(f"Total upcoming events: {len(events)}")
            st.markdown("---")

            for event in events:
                start_raw = event["start"].get("dateTime", event["start"].get("date"))

                # Format nicely
                try:
                    start_dt = datetime.datetime.fromisoformat(start_raw.replace("Z", "+00:00"))
                    formatted_time = start_dt.strftime("%d %b %Y | %I:%M %p")
                except:
                    formatted_time = start_raw

                st.write(f"{formatted_time}  —  {event['summary']}")

# -------------------------
# FOOTER
# -------------------------

st.markdown("---")
st.caption("Built using Streamlit, Google Calendar API, and SQLite")