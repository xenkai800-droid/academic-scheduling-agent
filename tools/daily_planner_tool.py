from core.calendar_service import list_upcoming_events
from core.assignment_manager import get_assignments
from tools.find_free_time_tool import find_free_time
import datetime
import pytz

TIMEZONE = "Asia/Kolkata"


def daily_planner_tool(day: str = "today"):

    try:

        ist = pytz.timezone(TIMEZONE)
        today = datetime.datetime.now(ist).date()

        # -------------------------
        # DAY
        # -------------------------

        if day.lower() == "tomorrow":
            target_date = today + datetime.timedelta(days=1)
            label = "Tomorrow"
        else:
            target_date = today
            label = "Today"

        message = f"📅 {label}'s Plan\n\n"

        # -------------------------
        # EVENTS
        # -------------------------

        events = list_upcoming_events()
        day_events = []

        for e in events:

            start = e.get("start", {})

            if "dateTime" in start:
                dt = datetime.datetime.fromisoformat(
                    start["dateTime"].replace("Z", "+00:00")
                ).astimezone(ist)

                if dt.date() == target_date:
                    day_events.append((dt, e.get("summary", "Event")))

            elif "date" in start:
                if start["date"] == target_date.isoformat():
                    day_events.append((None, e.get("summary", "Event")))

        day_events.sort(key=lambda x: x[0] or datetime.datetime.min)

        if day_events:
            message += "📆 Events\n\n"
            for dt, title in day_events:
                if dt:
                    message += f"• {title} — {dt.strftime('%I:%M %p')}\n"
                else:
                    message += f"• {title} (All Day)\n"
            message += "\n"
        else:
            message += "📭 No events scheduled.\n\n"

        # -------------------------
        # ASSIGNMENTS (CLEANED)
        # -------------------------

        assignments = get_assignments()

        if assignments:
            message += "📚 Assignments\n\n"

            for a in assignments[:5]:

                subject = a['subject'] if a['subject'] and a['subject'].lower() != "idk" else "General"

                message += (
                    f"• {a['title']} ({subject})\n"
                    f"  🔥 {a['priority'].upper()} | ⏰ {a['due_date']}\n\n"
                )
        else:
            message += "📭 No assignments.\n\n"

        # -------------------------
        # EXAM ALERT (FIXED)
        # -------------------------

        for _, title in day_events:
            if "exam" in title.lower():
                message += "⚠️ You have an exam on this day. Plan wisely.\n\n"
                break

        # -------------------------
        # FREE TIME (CLEANED)
        # -------------------------

        free_time = find_free_time(date=target_date.isoformat())
        free_time = free_time.replace("🕒 Available Free Time\n\n", "")

        message += "🕒 Free Time\n\n"
        message += free_time

        return message

    except Exception as e:
        return f"❌ Error creating daily plan: {str(e)}"