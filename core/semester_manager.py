import datetime
from tools.add_event_tool import add_event_tool
from core.calendar_service import event_exists_on_date


# -----------------------------------
# SEMESTER TEMPLATE (EDITABLE)
# -----------------------------------

SEMESTER_TEMPLATE = {
    "Monday": [
        ("Math Lecture", "09:00", "10:00"),
        ("Physics Lecture", "10:00", "11:00"),
    ],
    "Tuesday": [
        ("DBMS Lab", "14:00", "16:00"),
    ],
    "Wednesday": [
        ("AI Lecture", "11:00", "12:00"),
    ],
}


# -----------------------------------
# APPLY TEMPLATE
# -----------------------------------

def apply_semester_template(start_date: str, weeks: int = 4):

    try:

        start = datetime.date.fromisoformat(start_date)

        created = 0
        skipped = 0
        failed = 0

        for i in range(weeks * 7):

            current = start + datetime.timedelta(days=i)
            day_name = current.strftime("%A")
            date_str = current.isoformat()

            if day_name not in SEMESTER_TEMPLATE:
                continue

            for title, start_time, end_time in SEMESTER_TEMPLATE[day_name]:

                # -----------------------------------
                # DUPLICATE CHECK (VERY IMPORTANT)
                # -----------------------------------

                if event_exists_on_date(title, date_str):
                    skipped += 1
                    continue

                result = add_event_tool(
                    title,
                    date_str,
                    start_time,
                    end_time,
                )

                if result and "❌" not in result and "⚠️" not in result:
                    created += 1
                else:
                    failed += 1

        # -----------------------------------
        # FINAL SUMMARY (FOR DEMO)
        # -----------------------------------

        return (
            "✅ Semester Template Applied\n\n"
            f"📌 Events Created: {created}\n"
            f"⏭️ Skipped (Already Exists): {skipped}\n"
            f"⚠️ Failed: {failed}"
        )

    except Exception as e:
        return f"❌ Error applying semester template: {str(e)}"