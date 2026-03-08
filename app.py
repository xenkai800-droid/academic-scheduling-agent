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
# SMART STUDY SUGGESTION
# --------------------------------------------------

# suggestion = suggest_study_session_tool()

# if suggestion != "No urgent assignments requiring study time.":

#    st.info("🧠 Smart Study Suggestion")
#    st.write(suggestion)

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
                st.error("❌ An event with this name already exists on this date.")

            else:

                with st.spinner("Creating event..."):

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

    with st.spinner("Fetching events..."):
        events = list_upcoming_events()

    if not events:
        st.info("No upcoming events found.")

    else:

        st.success(f"Found {len(events)} upcoming events")

        IST = pytz.timezone("Asia/Kolkata")

        for event in events:

            start_data = event["start"]

            try:

                # ---------------------------
                # Timed events
                # ---------------------------
                if "dateTime" in start_data:

                    start_raw = start_data["dateTime"].replace("Z", "+00:00")

                    start_dt = datetime.datetime.fromisoformat(start_raw)

                    # convert to IST
                    start_dt = start_dt.astimezone(IST)

                    formatted_time = start_dt.strftime("%d %b %Y | %I:%M %p")

                # ---------------------------
                # All day events
                # ---------------------------
                elif "date" in start_data:

                    start_dt = datetime.date.fromisoformat(start_data["date"])

                    formatted_time = start_dt.strftime("%d %b %Y | All Day")

                else:
                    formatted_time = "Unknown time"

            except:
                formatted_time = "Invalid time format"

            with st.container(border=True):

                col1, col2 = st.columns([4, 1])

                with col1:

                    st.markdown(
                        f"""
                        **{event['summary']}**  
                        🕒 {formatted_time}
                        """
                    )

                with col2:

                    if st.button("🗑", key=f"delete_{event['id']}"):

                        with st.spinner("Deleting..."):

                            delete_event(event["id"])
                            delete_local_event(event["id"])

                        st.success("✅ Event deleted successfully.")
                        st.rerun()
# --------------------------------------------------
# FIND FREE TIME
# --------------------------------------------------

elif page == "Find Free Time":

    st.subheader("🕒 Find Free Time")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input("Start Date")

    with col2:
        end_date = st.date_input("End Date")

    if st.button("Find Free Slots"):

        results = find_free_time(start_date.isoformat(), end_date.isoformat())

        for day, slots in results.items():

            st.markdown(f"### 📅 {day}")

            if not slots:
                st.write("No free slots available")
            else:
                for slot in slots:
                    st.write(f"• {slot}")


# --------------------------------------------------
# ASSIGNMENTS
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

        if st.button("Add Assignment"):

            if not title.strip():
                st.error("Assignment title cannot be empty")

            else:

                result = add_assignment_tool(
                    title.strip(),
                    subject.strip(),
                    due_date.isoformat(),
                )

                st.success(result)

    st.divider()

    st.subheader("Assignments")

    assignments = get_assignments()

    if not assignments:
        st.info("No assignments added yet.")

    else:

        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=1)

        past_due = []
        due_today = []
        due_tomorrow = []
        upcoming = []
        completed = []

        for aid, title, subject, due, status in assignments:

            due_date = datetime.date.fromisoformat(due)

            if status == "completed":
                completed.append((aid, title, subject, due, status))

            elif due_date < today:
                past_due.append((aid, title, subject, due, status))

            elif due_date == today:
                due_today.append((aid, title, subject, due, status))

            elif due_date == tomorrow:
                due_tomorrow.append((aid, title, subject, due, status))

            else:
                upcoming.append((aid, title, subject, due, status))

        def render_section(title, items):

            if not items:
                return

            st.markdown(f"### {title}")

            for aid, title, subject, due, status in items:

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:

                        st.markdown(
                            f"""
                            **{title}**  
                            📘 {subject}  
                            ⏰ Due: {due}
                            """
                        )

                    with col2:

                        if status == "pending":

                            if st.button("✔", key=f"complete_{aid}"):

                                mark_assignment_complete(aid)
                                st.success("Assignment marked as completed")
                                st.rerun()

                            if st.button("📅", key=f"study_{aid}"):

                                st.session_state["study_assignment"] = f"Study: {title}"
                                st.session_state["page_redirect"] = "Create Event"

                                st.success(
                                    "Redirecting to Create Event to schedule study time..."
                                )

                                st.rerun()

        render_section("⚠ Past Due", past_due)
        render_section("⏰ Due Today", due_today)
        render_section("⏳ Due Tomorrow", due_tomorrow)
        render_section("📚 Upcoming", upcoming)
        render_section("✅ Completed", completed)


# --------------------------------------------------
# AI ASSISTANT
# --------------------------------------------------

elif page == "AI Assistant":

    st.subheader("🤖 AI Scheduling Assistant")

    st.write("Ask me anything about your schedule.")

    user_query = st.text_input("Enter your request")

    if st.button("Run Assistant"):

        if not user_query.strip():
            st.error("Please enter a request.")
        else:

            with st.spinner("Thinking..."):

                try:
                    response = run_agent(user_query)

                    st.success("Assistant Response:")
                    st.write(response)

                except Exception as e:
                    st.error(f"Agent error: {e}")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption("Built using Streamlit • Google Calendar API • SQLite")
