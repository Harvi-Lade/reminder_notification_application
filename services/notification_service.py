import smtplib
import json
import requests
import logging
from email.message import EmailMessage
from plyer import notification
from config.settings import EMAIL_SENDER, EMAIL_PASSWORD, PUSHBULLET_API_KEY
from typing import Dict, Any, Optional, List


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("reminder_log.log", encoding="utf-8"),  # Logs to file
        logging.StreamHandler()  # Logs to terminal
    ]
)


class NotificationService:
    """
    Manages notifications through Desktop, Email, and Pushbullet.
    """

    def __init__(self, db_manager: Any) -> None:
        """"
        Initializes the NotificationService with a database manager and notification credentials.

        Args:
            db_manager (Any): The database manager instance for accessing reminders.
        """
        self.email_sender = EMAIL_SENDER
        self.email_password = EMAIL_PASSWORD
        self.pushbullet_api_key = PUSHBULLET_API_KEY
        self.db_manager = db_manager  # Avoids circular import issue

    def check_reminder(self, reminder: Dict[str, Any]) -> None:
        """
        Checks if a reminder is due and sends notifications via desktop, email, and Pushbullet.

        Args:
            reminder (Dict[str, Any]): The reminder details including id, title, time and email.
        """
        reminder_id = reminder["id"]
        title = "Reminder Notification"
        message = f"⏰ Reminder: {reminder['title']} at {reminder['time']}"

        print(f"   🔍 Due Reminder: \"{reminder['title']}\"")

        try:
            self.send_desktop_notification(title, message)

            if reminder.get("email"):
                self.send_email_notification(reminder["email"], title, message)

            if self.pushbullet_api_key:
                self.send_pushbullet_notification(title, message)

            self.db_manager.update_reminder_status(reminder_id, notified=True)

        except Exception as e:
            logging.error(f"Error processing reminder '{reminder['title']}': {e}")

    @staticmethod
    def send_desktop_notification(title: str, message: str) -> None:
        """
        Sends a desktop notification with the given title and message.

        Args:
            title (str): Notification title.
            message (str): Notification message.
        """
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=10
            )
            print("     📢 Desktop notification: Sent ✔️")
        except Exception as e:
            logging.error(f"Failed to send desktop notification: {e}")

    def send_email_notification(self, recipient_email: Optional[str], subject: str, message: str) -> None:
        """
        Sends an email notification to the specified recipient with the given subject and message.

        Args:
            recipient_email (Optional[str]): Recipient's email address.
            subject (str): Email subject.
            message (str): Email content
        """
        if not recipient_email or recipient_email.lower() == "none":
            print("⚠️ No email provided. Skipping email notification.")
            return

        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.email_sender
            msg["To"] = recipient_email
            msg.set_content(message)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)

            print(f"     📧 Email to {recipient_email}: Sent ✔️")
        except Exception as e:
            logging.error(f"Error sending email to {recipient_email}: {e}")

    def send_pushbullet_notification(self, title: str, message: str) -> None:
        """
         Sends a Pushbullet notification.

         Args:
             title (str): Notification title
             message (str): Notification message.
         """

        if not self.pushbullet_api_key:
            print("⚠️ Pushbullet API key missing. Skipping Pushbullet notification.")
            return
        try:
            data = {"type": "note", "title": title, "body": message}
            response = requests.post(
                "https://api.pushbullet.com/v2/pushes",
                data=json.dumps(data),
                headers={
                    "Access-Token": self.pushbullet_api_key,
                    "Content-Type": "application/json",
                },
            )
            if response.status_code == 200:
                print(f"     🚀 Pushbullet notification: Sent ✔️")
            else:
                logging.error(f"Failed to send Pushbullet notification: {response.text}")

        except Exception as e:
            logging.error(f"Error sending Pushbullet notification: {e}")

    def notify_reminders(self, due_reminders: List[Dict]) -> None:
        """Sends notifications for due reminders.

        Args:
            due_reminders (List[Dict]): List of reminders to notify.
        """

        if not due_reminders:
            print("✅ No due reminders found.\n")
            return

        for reminder in due_reminders:
            self.check_reminder(reminder)

        print("✅ All due reminders processed!")