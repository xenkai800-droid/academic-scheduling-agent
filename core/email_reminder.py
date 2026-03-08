import smtplib
from email.mime.text import MIMEText

from core.reminder_engine import get_due_assignments, mark_reminder_sent


def send_email_reminders(sender_email, sender_password, user_email):

    reminders = get_due_assignments()

    if not reminders:
        print("No reminders to send.")
        return

    message_body = "📚 Academic Scheduling Agent - Assignment Reminder\n\n"

    # Build email body
    for aid, title, subject, due in reminders:
        message_body += f"• {title} ({subject}) due on {due}\n"

    msg = MIMEText(message_body)

    msg["Subject"] = "Assignment Reminder"
    msg["From"] = sender_email
    msg["To"] = user_email

    try:

        with smtplib.SMTP("smtp.gmail.com", 587) as server:

            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("Reminder email sent successfully.")

        # After email is sent → mark reminders as sent
        for aid, title, subject, due in reminders:
            mark_reminder_sent(aid)

    except Exception as e:

        print("Email sending failed:", e)
