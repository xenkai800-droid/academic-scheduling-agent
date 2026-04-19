import smtplib
from email.mime.text import MIMEText

from core.reminder_engine import get_due_assignments, mark_reminder_sent


def send_email_reminders(sender_email, sender_password, user_email):

    try:

        reminders = get_due_assignments()

        if not reminders:
            print("No reminders to send.")
            return

        message_body = "📚 Academic Scheduling Agent - Assignment Reminder\n\n"

        valid_reminders = []

        for r in reminders:

            # -------------------------
            # HANDLE DICT FORMAT (NEW)
            # -------------------------

            if isinstance(r, dict):
                aid = r["id"]
                title = r["title"]
                subject = r.get("subject", "General")
                due = r["due_date"]
                status = r.get("status", "")
                sent = r.get("reminder_sent", 0)

            # -------------------------
            # FALLBACK (OLD FORMAT)
            # -------------------------

            else:
                aid, title, subject, due = r
                status = ""
                sent = 0

            # -------------------------
            # SKIP IF ALREADY SENT
            # -------------------------

            if sent == 1:
                continue

            # -------------------------
            # FORMAT LABEL
            # -------------------------

            if status == "past_due":
                label = "⚠️ Past Due"
            elif status == "today":
                label = "⏰ Due Today"
            elif status == "tomorrow":
                label = "⏳ Due Tomorrow"
            else:
                label = ""

            message_body += f"• {title} ({subject}) — {label} ({due})\n"

            valid_reminders.append(aid)

        if not valid_reminders:
            print("No new reminders to send.")
            return

        # -------------------------
        # SEND EMAIL
        # -------------------------

        msg = MIMEText(message_body)

        msg["Subject"] = "Assignment Reminder"
        msg["From"] = sender_email
        msg["To"] = user_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Reminder email sent successfully.")

        # -------------------------
        # MARK AS SENT
        # -------------------------

        for aid in valid_reminders:
            mark_reminder_sent(aid)

    except Exception as e:

        print("Email sending failed:", e)