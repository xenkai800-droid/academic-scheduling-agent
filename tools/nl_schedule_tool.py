from core.nlp_parser import parse_event_request
from tools.add_event_tool import add_event_tool
from tools.find_free_time_tool import find_free_time
import traceback

# --------------------------------------------------
# MAIN TOOL
# --------------------------------------------------

def schedule_from_text_tool(query: str):

    try:

        # -------------------------
        # INPUT VALIDATION
        # -------------------------

        if not query or not query.strip():
            return "❌ Please provide a scheduling request."

        # -------------------------
        # PARSE USER INPUT
        # -------------------------

        parsed = parse_event_request(query)

        if not parsed:
            return (
                "❌ I couldn't understand the request.\n\n"
                "Try: 'schedule math tomorrow at 2pm'"
            )

        title = parsed.get("title")
        date = parsed.get("date")
        start_time = parsed.get("start_time")
        end_time = parsed.get("end_time")

        # -------------------------
        # VALIDATION
        # -------------------------

        if not title:
            return "❌ Missing event title."

        if not date:
            return "❌ Missing event date."

        if not start_time:
            return "❌ Missing start time."

        if not end_time:
            return "❌ Missing end time."

        # -------------------------
        # CREATE EVENT
        # -------------------------

        result = add_event_tool(
            title.strip(),
            date,
            start_time,
            end_time,
        )

        # -------------------------
        # HANDLE TOOL RESPONSE
        # -------------------------

        if not result:
            return "❌ Failed to schedule event."

        if "❌" in result or "⚠️" in result:
            return result

        # -------------------------
        # CLEAN OUTPUT
        # -------------------------

        response = (
            "✅ Event Scheduled Successfully\n\n"
            f"📌 {title}\n"
            f"📅 {date}\n"
            f"🕒 {start_time} - {end_time}"
        )

        # --------------------------------------------------
        # EXAM → SMART STUDY SUGGESTION (UPGRADED)
        # --------------------------------------------------

        if "exam" in title.lower():

            try:

                study_plan = find_free_time(date=date)

                if study_plan and "No free slots" not in study_plan:

                    response += (
                        "\n\n📚 Study Plan Recommendation:\n\n"
                        f"{study_plan}"
                    )

                else:

                    response += (
                        "\n\n⚠️ No free study slots available.\n"
                        "Consider rescheduling or adjusting workload."
                    )

            except Exception:
                pass

        return response


    except Exception as e:
        print("\n===== FULL ERROR TRACE =====")
        traceback.print_exc()
        print("===== END TRACE =====\n")

        return f"❌ Error scheduling event: {str(e)}"