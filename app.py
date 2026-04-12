import streamlit as st
import datetime
import pytz

from tools.study_suggestion_tool import suggest_study_session_tool
from core.reminder_engine import get_due_assignments
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
from tools.add_assignment_tool import add_assignment_tool
from core.agent_controller import run_agent

from core.calendar_service import (
    list_upcoming_events,
    delete_event,
    event_exists_on_date,
)

from core.assignment_manager import (
    get_assignments,
    mark_assignment_complete,
)

from db.database import initialize_database, delete_local_event

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Academic Scheduling Agent",
    page_icon="📅",
    layout="wide",
)

initialize_database()

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("📅 Academic Scheduling Agent")
st.markdown("Manage your academic schedule with seamless Google Calendar integration.")
st.divider()

# --------------------------------------------------
# REMINDER PANEL
# --------------------------------------------------

reminders = get_due_assignments()

if reminders:

    st.warning("⚠ Upcoming Assignment Reminders")

    today = datetime.date.today()

    for aid, title, subject, due in reminders:

        due_date = datetime.date.fromisoformat(due)

        if due_date < today:
            label = "⚠ Past Due"
        elif due_date == today:
            label = "⏰ Due Today"
        else:
            label = "⏳ Due Tomorrow"

        st.write(f"• {title} ({subject}) — {label}")

st.divider()

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.header("Navigation")

pages = [
    "Create Event",
    "View Upcoming Events",
    "Find Free Time",
    "Assignments",
    "AI Assistant",
]

default_page = st.session_state.get("page_redirect", pages[0])

page = st.sidebar.radio(
    "Go to",
    pages,
    index=pages.index(default_page),
)

st.session_state["page_redirect"] = page

# --------------------------------------------------
# CREATE EVENT
# --------------------------------------------------

if page == "Create Event":

    st.subheader("➕ Create New Event")

    default_title = st.session_state.get("study_assignment", "")

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input("Event Title", value=default_title)
            date = st.date_input("Event Date")

        with col2:
            start_time = st.time_input("Start Time")
            end_time = st.time_input("End Time")

        if st.button("🚀 Create Event"):

            event_datetime = datetime.datetime.combine(date, start_time)
            now = datetime.datetime.now()

            if not title.strip():
                st.error("❌ Event title cannot be empty.")

            elif event_datetime < now:
                st.error("❌ Cannot create event in the past.")

            elif end_time <= start_time:
                st.error("❌ End time must be later than start time.")

            elif event_exists_on_date(title, date.isoformat()):
                st.error("❌ Event already exists on this date.")

            else:

                result = add_event_tool(
                    title.strip(),
                    date.isoformat(),
                    start_time.strftime("%H:%M"),
                    end_time.strftime("%H:%M"),
                )

                if "❌" in result:
                    st.error(result)
                else:
                    st.success(result)

# --------------------------------------------------
# VIEW EVENTS
# --------------------------------------------------

elif page == "View Upcoming Events":

    st.subheader("📌 Upcoming Events")

    events = list_upcoming_events()

    if not events:
        st.info("No upcoming events found.")

    else:

        IST = pytz.timezone("Asia/Kolkata")

        for event in events:

            start_data = event["start"]

            if "dateTime" in start_data:
                dt = datetime.datetime.fromisoformat(start_data["dateTime"].replace("Z", "+00:00"))
                dt = dt.astimezone(IST)
                time_str = dt.strftime("%d %b %Y | %I:%M %p")
            else:
                dt = datetime.date.fromisoformat(start_data["date"])
                time_str = dt.strftime("%d %b %Y | All Day")

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"**{event['summary']}**  \n🕒 {time_str}")

                with col2:
                    if st.button("🗑", key=event["id"]):
                        delete_event(event["id"])
                        delete_local_event(event["id"])
                        st.rerun()

# --------------------------------------------------
# FIND FREE TIME
# --------------------------------------------------

elif page == "Find Free Time":

    st.subheader("🕒 Find Free Time")

    start_date = st.date_input("Start Date")
    end_date = st.date_input("End Date")

    if st.button("Find Free Slots"):

        results = find_free_time(start_date.isoformat(), end_date.isoformat())

        for day, slots in results.items():
            st.markdown(f"### {day}")
            if not slots:
                st.write("No free slots")
            else:
                for slot in slots:
                    st.write(f"• {slot}")

# --------------------------------------------------
# ASSIGNMENTS (UPDATED)
# --------------------------------------------------

elif page == "Assignments":

    st.subheader("📚 Assignment Tracker")

    with st.container(border=True):

        col1, col2, col3 = st.columns(3)

        with col1:
            title = st.text_input("Assignment Title")

        with col2:
            subject = st.text_input("Subject")

        with col3:
            due_date = st.date_input("Due Date")

        # ✅ AUTO + MANUAL PRIORITY
        priority = st.selectbox(
            "Priority (Optional)",
            ["auto", "low", "medium", "high"]
        )

        if st.button("Add Assignment"):

            if not title.strip():
                st.error("Assignment title cannot be empty")

            elif due_date < datetime.date.today():
                st.error("Due date cannot be in the past")

            else:

                result = add_assignment_tool(
                    title.strip(),
                    subject.strip(),
                    due_date.isoformat(),
                    priority,
                )

                st.success(result)

    st.divider()

    assignments = get_assignments()

    if not assignments:
        st.info("No assignments added yet.")

    else:

        for aid, title, subject, due, status, priority in assignments:

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(
                        f"**{title}**  \n📘 {subject}  \n🔥 {priority.upper()}  \n⏰ {due}"
                    )

                with col2:

                    if st.button("✔", key=f"done_{aid}"):
                        mark_assignment_complete(aid)
                        st.rerun()

# --------------------------------------------------
# AI ASSISTANT
# --------------------------------------------------

elif page == "AI Assistant":

    st.subheader("🤖 AI Scheduling Assistant")

    query = st.text_input("Enter your request")

    if st.button("Run"):

        if not query.strip():
            st.error("Enter a request")
        else:
            response = run_agent(query)

            if not response:
                st.error("No response generated.")

            elif "Error" in response or "❌" in response:
                st.error(response)

            elif "⚠️" in response:
                st.warning(response)

            elif "📚" in response:
                st.info(response)

            else:
                st.success(response)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()
st.caption("Built with Streamlit • Google Calendar • AI Scheduling")