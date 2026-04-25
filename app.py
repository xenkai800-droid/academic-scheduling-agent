import streamlit as st
import datetime
import pytz
import pandas as pd

from core.reminder_engine import get_due_assignments
try:
    from core.email_reminder import send_email_reminders
    EMAIL_ENABLED = True
except:
    EMAIL_ENABLED = False
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
from tools.add_assignment_tool import add_assignment_tool

from core.agent_controller import run_agent
from core.semester_manager import apply_semester_template

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


# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="Academic Scheduling Agent",
    page_icon="📅",
    layout="wide",
)

initialize_database()

# ---------------- HEADER ----------------

st.title("📅 Academic Scheduling Agent")
st.markdown("AI-powered academic planner with smart scheduling & conflict management.")
st.divider()

# ---------------- REMINDERS ----------------

reminders = get_due_assignments()

if reminders:
    st.warning("⚠️ Upcoming Assignment Deadlines")

    today = datetime.date.today()

    for r in reminders:

        if isinstance(r, dict):
            aid = r["id"]
            title = r["title"]
            subject = r.get("subject", "General")
            due = r["due_date"]
            status = r.get("status", "")
        else:
            aid, title, subject, due = r
            status = ""

        subject = subject or "General"
        due_date = datetime.date.fromisoformat(due)

        if status == "past_due" or due_date < today:
            label = "⚠️ Past Due"
            show_delete = True
        elif status == "today" or due_date == today:
            label = "⏰ Due Today"
            show_delete = False
        else:
            label = "⏳ Due Tomorrow"
            show_delete = False

        col1, col2 = st.columns([5, 1])

        with col1:
            st.write(f"• {title} ({subject}) — {label}")

        with col2:
            if show_delete:
                if st.button("❌", key=f"rem_{aid}"):
                    mark_assignment_complete(aid)
                    st.rerun()

st.divider()

# ---------------- NAVIGATION ----------------

st.sidebar.header("Navigation")

pages = [
    "AI Assistant",
    "Dashboard",
    "Create Event",
    "Find Free Time",
    "Assignments",
]

page = st.sidebar.radio("Go to", pages)


# ==================================================
# 🤖 AI ASSISTANT (CLEAN MODE)
# ==================================================

if page == "AI Assistant":

    st.subheader("🤖 AI Scheduling Assistant")

    if st.button("📚 Apply Semester Template"):
        result = apply_semester_template(datetime.date.today().isoformat())
        st.success(result)

    st.divider()
    # 🔥 MEMORY STATE
    if "pending_action" not in st.session_state:
        st.session_state.pending_action = None
    query = st.text_input(
        "Enter your request",
        placeholder="e.g. schedule math exam tomorrow at 10am"
    )

    if st.button("Run AI"):

        if not query.strip():
            st.error("❌ Please enter a request")
        else:
            # 🔥 HANDLE FOLLOW-UP MEMORY
            if st.session_state.pending_action == "schedule":
                query = f"schedule {query}"
                st.session_state.pending_action = None

            response = run_agent(query)

            # 🔥 DETECT FOLLOW-UP QUESTIONS FROM AI
            if isinstance(response, str):
                if "what would you like to schedule" in response.lower():
                    st.session_state.pending_action = "schedule"

            st.divider()

            # 🔥 CLEAN OUTPUT BLOCK
            with st.container(border=True):
                st.markdown("### 🤖 Result")
                st.markdown(response)


# ==================================================
# 📊 DASHBOARD
# ==================================================

elif page == "Dashboard":

    st.subheader("📊 Schedule Dashboard")

    st.subheader("📧 Reminders")

    if st.button("Send Reminder Email Now"):
        try:
            if EMAIL_ENABLED:
                send_email_reminders(
                    st.secrets["EMAIL_USER"],
                    st.secrets["EMAIL_PASS"],
                    st.secrets["USER_EMAIL"]
                )
            else:
                st.warning("📧 Email reminders not configured in this environment.")
        except Exception as e:
            st.error(f"❌ Email failed: {str(e)}")

    st.divider()

    events = list_upcoming_events()

    if not events:
        st.info("No upcoming events.")
    else:

        IST = pytz.timezone("Asia/Kolkata")
        grouped = {}

        for event in events:

            start = event.get("start", {})

            if "dateTime" in start:
                dt = datetime.datetime.fromisoformat(
                    start["dateTime"].replace("Z", "+00:00")
                ).astimezone(IST)
                date_key = dt.date()
                time_str = dt.strftime("%I:%M %p")

            elif "date" in start:
                date_key = datetime.date.fromisoformat(start["date"])
                time_str = "All Day"
            else:
                continue

            grouped.setdefault(date_key, []).append((event, time_str))

        for date_key in sorted(grouped.keys()):

            st.markdown(f"### 📅 {date_key.strftime('%d %b %Y')}")

            for event, time_str in grouped[date_key]:

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"**{event['summary']}**  \n🕒 {time_str}")

                    with col2:
                        if st.button("🗑", key=event["id"]):
                            delete_event(event["id"])
                            delete_local_event(event["id"])
                            st.rerun()

    st.divider()

    st.subheader("📤 Export Schedule")

    if events:
        from openpyxl import Workbook
        from openpyxl.utils import get_column_letter
        from io import BytesIO
        from datetime import datetime

        wb = Workbook()
        ws = wb.active
        ws.title = "Schedule"

        # Headers
        headers = ["Title", "Start", "End", "Type"]
        ws.append(headers)

        # Format function
        def format_dt(dt_str):
            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
                return dt.strftime("%d-%m-%Y %H:%M")
            except:
                return dt_str

        # Data
        for e in events:
            start = e.get("start", {})
            end = e.get("end", {})

            start_val = format_dt(start.get("dateTime") or start.get("date", ""))
            end_val = format_dt(end.get("dateTime") or end.get("date", ""))

            ws.append([
                e.get("summary"),
                start_val,
                end_val,
                "All Day" if "date" in start else "Timed"
            ])

        # 🔥 AUTO COLUMN WIDTH
        for col in ws.columns:
            max_length = 0
            col_letter = get_column_letter(col[0].column)

            for cell in col:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))

            ws.column_dimensions[col_letter].width = max_length + 2

        # Save to memory
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Download
        st.download_button(
            "Download Excel",
            buffer,
            file_name="schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# ==================================================
# CREATE EVENT
# ==================================================

elif page == "Create Event":

    st.subheader("➕ Create Event")

    title = st.text_input("Title")
    date = st.date_input("Date")
    start_time = st.time_input("Start Time")
    end_time = st.time_input("End Time")

    if st.button("Create"):

        if not title.strip():
            st.error("Title required")

        elif end_time <= start_time:
            st.error("Invalid time range")

        elif event_exists_on_date(title, date.isoformat()):
            st.error("Event already exists")

        else:
            result = add_event_tool(
                title,
                date.isoformat(),
                start_time.strftime("%H:%M"),
                end_time.strftime("%H:%M"),
            )

            if "⚠️" in result:
                st.warning(result)
                st.info("Try another time → Check Free Time below 👇")

                free = find_free_time(date=date.isoformat())
                st.markdown(free)

            elif "❌" in result:
                st.error(result)

            else:
                st.success(result)


# ==================================================
# FIND FREE TIME
# ==================================================

elif page == "Find Free Time":

    st.subheader("🕒 Free Time Finder")

    date = st.date_input("Select Date")

    if st.button("Check"):
        result = find_free_time(date=date.isoformat())
        st.markdown(result)


# ==================================================
# ASSIGNMENTS
# ==================================================

elif page == "Assignments":

    st.subheader("📚 Assignments")

    title = st.text_input("Title")
    subject = st.text_input("Subject")
    due_date = st.date_input("Due Date")
    priority = st.selectbox("Priority", ["auto", "low", "medium", "high"])

    if st.button("Add Assignment"):

        if not title.strip():
            st.error("Title required")

        else:
            result = add_assignment_tool(
                title=title,
                subject=subject,
                due_date=due_date.isoformat(),
                priority=priority,
            )
            st.success(result)

    st.divider()

    assignments = get_assignments()

    for a in assignments:

        with st.container(border=True):

            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(
                    f"**{a['title']}** ({a['subject']})  \n🔥 {a['priority'].upper()}  \n⏰ {a['due_date']}"
                )

            with col2:
                if st.button("✔", key=f"a_{a['id']}"):
                    mark_assignment_complete(a['id'])
                    st.rerun()


# ---------------- FOOTER ----------------

st.divider()
st.caption("Production-ready Academic Scheduling Agent 🚀")