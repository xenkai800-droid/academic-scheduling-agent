import schedule
import time

from core.email_reminder import send_email_reminders


def start_scheduler(sender_email, sender_password, user_email):

    # run every day at 08:00 AM
    # schedule.every().day.at("08:00").do(
    #    send_email_reminders, sender_email, sender_password, user_email
    # )
    schedule.every(10).seconds.do(
        send_email_reminders, sender_email, sender_password, user_email
    )

    print("Reminder scheduler started...")

    while True:
        schedule.run_pending()
        time.sleep(60)
