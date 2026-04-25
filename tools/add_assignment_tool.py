import datetime
from core.assignment_manager import add_assignment
from core.date_parser import parse_natural_date


def add_assignment_tool(query: str = "", title: str = "", subject: str = "", due_date: str = "", priority: str = "auto", **kwargs):

    try:

        # -------------------------
        # HANDLE LANGCHAIN "args"
        # -------------------------

        if "args" in kwargs:
            args = kwargs["args"]

            # Example: ('physics', {'due': 'tomorrow'})
            if isinstance(args, tuple) and len(args) >= 1:
                title = args[0]

                if len(args) > 1 and isinstance(args[1], dict):
                    due = args[1].get("due")

                    if due == "tomorrow":
                        due_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
                    elif due == "today":
                        due_date = datetime.date.today().isoformat()

        # -------------------------
        # NLP QUERY PARSING
        # -------------------------

        if query:
            q = query.lower()

            if not title:
                cleaned = q.replace("add assignment", "").replace("due", "").strip()

                words = cleaned.split()

                # 🔥 REMOVE DATE WORDS
                invalid_words = ["today", "tomorrow"]

                filtered = [w for w in words if w not in invalid_words]

                # ALSO REMOVE NUMERIC DATES
                filtered = [w for w in filtered if not any(c.isdigit() for c in w)]

                if filtered:
                    title = filtered[0].capitalize()

            if not subject:
                subject = title

            parsed = parse_natural_date(q)

            if parsed:
                due_date = parsed

            elif "tomorrow" in q:
                due_date = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()

            elif "today" in q:
                due_date = datetime.date.today().isoformat()

        # -------------------------
        # VALIDATION
        # -------------------------

        if not title:
            return "❌ Assignment title is required."

        if not due_date:
            return "❌ Due date is required."

        title = title.strip()
        subject = subject.strip() if subject else "General"

        try:
            today = datetime.date.today()
            parsed = datetime.date.fromisoformat(due_date)

            if parsed < today:
                return "❌ Due date cannot be in the past."

            due_date = parsed.isoformat()

        except Exception:
            return "❌ Invalid due date format."

        # -------------------------
        # PRIORITY
        # -------------------------

        if priority not in ["low", "medium", "high", "auto"]:
            priority = "auto"

        # -------------------------
        # SAVE
        # -------------------------

        result = add_assignment(title, subject, due_date, priority)

        return result

    except Exception as e:
        return f"❌ Error adding assignment: {str(e)}"