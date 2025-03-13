# Handles recurrence, due reminders, upcoming reminders

import time
from datetime import datetime, timedelta
import calendar


class ReminderScheduler:

    def __init__(self, db_manager) -> None:
        """
            Initialize ReminderScheduler with a database manager.
        """
        self.db_manager = db_manager

    @staticmethod
    def calculate_next_occurrence(reminder_time: datetime, recurrence: str) -> datetime | None:
        """
        Calculate the next occurrence of a reminder based on the recurrence type.

        Args:
            reminder_time (datetime): The original reminder time.
            recurrence (str): The recurrence type ('none', 'daily', 'weekly', 'monthly', 'yearly').

        Returns:
            datetime | None: The next occurrence datetime or None if no recurrence.
        """
        if not reminder_time or recurrence == "none":
            return None

        next_time = None

        if recurrence == "daily":
            next_time = reminder_time + timedelta(days=1)

        elif recurrence == "weekly":
            next_time = reminder_time + timedelta(weeks=1)

        elif recurrence == "monthly":
            # Handle month transition safely
            month = reminder_time.month + 1 if reminder_time.month < 12 else 1
            year = reminder_time.year + 1 if month == 1 else reminder_time.year
            day = min(reminder_time.day, calendar.monthrange(year, month)[1])  # Ensure valid day
            next_time = reminder_time.replace(year=year, month=month, day=day)

        elif recurrence == "yearly":
            next_time = reminder_time.replace(year=reminder_time.year + 1)

        print(f"🔄 Recurrence: {recurrence} | Old: {reminder_time} | Next: {next_time}")

        return next_time

    def get_due_reminders(self) -> list[tuple[int, str, str, str, str]]:
        """
        Fetch reminders that are due but not yet notified.

        Returns:
            list[tuple[int, str, str, str, str]]: List of due reminders (id, title, reminder_time, recurrence, email).
        """
        query = """
        SELECT id, title, reminder_time, recurrence, email
        FROM reminders 
        WHERE reminder_time <= ? AND notified = 0
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.db_manager.fetch_all(query, (current_time,))

    def fetch_upcoming_reminders(self) -> list[tuple[str, str]]:
        """
        Fetch reminders scheduled within the next 24 hours.

        Returns:
            list[tuple[str, str]]: List of upcoming reminders (title, reminder_time).
        """
        query = """
        SELECT title, reminder_time 
        FROM reminders 
        WHERE reminder_time > ? AND reminder_time <= ?
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        next_24_hours = (datetime.now() + timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")
        return self.db_manager.fetch_all(query, (current_time, next_24_hours))

    def update_reminder_status(self, reminder_id: int, notified: bool = True) -> None:
        """
        Mark a reminder as notified.

        Args:
            reminder_id (int): ID of the reminder.
            notified (bool): Whether the reminder has been notified. Defaults to True.
        """

        query = "UPDATE reminders SET notified = ? WHERE id = ?"
        self.db_manager.execute(query, (int(notified), reminder_id))

    def clean_old_reminders(self) -> None:
        """
        Delete reminders that were notified, have no recurrence,
        and are older than 7 days.
        """
        query = """
        DELETE FROM reminders 
        WHERE notified = 1 AND recurrence = 'none' 
        AND reminder_time <= ?
        """
        past_7_days = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        self.db_manager.execute(query, (past_7_days,))

    def run_reminder_checker(self, check_interval: int = 10, max_checks: int = 2, duration_minutes: int = 1) -> None:
        """
        Run the reminder checker for a limited number of checks or duration.

        Stops when either:
        - `max_checks` are completed
        - `duration_minutes` time has passed

        Args:
            check_interval (int): Time (in seconds) to wait between checks.
            max_checks (int): Maximum number of checks to perform.
            duration_minutes (int): Duration (in minutes) before stopping the checker.
        """

        print("=" * 50)
        print("🔄 REMINDER CHECKER STARTED".center(50))
        print("=" * 50)

        # Lazy import to avoid circular dependencies
        from services.notification_service import NotificationService
        notification_service = NotificationService(self.db_manager)

        # Choose ONE method by commenting/uncommenting

        ### 🔹 Method 1: Using datetime.now()
        # end_time = datetime.now() + timedelta(minutes=duration_minutes)

        ### 🔹 Method 2: Using time.time()
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        check_count = 0

        while check_count < max_checks:  # Stop after max_checks
            print(f"\n🔎 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking reminders...")

            # Fetch and display upcoming reminders in the next 24 hours
            upcoming_reminders = self.fetch_upcoming_reminders()
            if upcoming_reminders:
                print("\n📌 Upcoming Reminders in the Next 24 Hours:")
                for title, reminder_time in upcoming_reminders:
                    print(f"  - {title} at {reminder_time} \n")

            # Fetch due reminders
            due_reminders = self.get_due_reminders()

            if not due_reminders:
                print("✅ No due reminders.")
            else:
                for reminder in due_reminders:
                    reminder_dict = {
                        "id": reminder[0],
                        "title": reminder[1],
                        "time": reminder[2],
                        "recurrence": reminder[3],
                        "email": reminder[4]
                    }

                    print(f"\n✅ Sending Notifications:")

                    # Send notification
                    notification_service.check_reminder(reminder_dict)

                    # Mark reminder as notified
                    self.update_reminder_status(reminder_dict["id"])

                    # Handle recurrence
                    if reminder_dict["recurrence"] != "none":
                        reminder_time_dt = datetime.strptime(reminder_dict["time"], "%Y-%m-%d %H:%M")
                        next_time = self.calculate_next_occurrence(reminder_time_dt, reminder_dict["recurrence"])
                        if next_time is not None:
                            query = "UPDATE reminders SET reminder_time = ?, notified = 0 WHERE id = ?"
                            self.db_manager.execute(query, (next_time.strftime("%Y-%m-%d %H:%M"), reminder_dict["id"]))
                        else:
                            print(
                                f"⚠️ No next occurrence calculated for reminder ID {reminder_dict['id']}. Recurrence type: {reminder_dict['recurrence']}")

            check_count += 1
            print(f"🔄 Check {check_count}/{max_checks} completed.")

            # Stop based on chosen method:

            ## Method 1: Using datetime.now()
            # if datetime.now() >= end_time:
            #     print("⏳ Time limit reached. Stopping reminder checker.")
            #     break

            ## Method 2: Using time.time()
            if time.time() >= end_time:
                print("⏳ Time limit reached. Stopping reminder checker.")
                break

            print("-" * 40)
            print(f"⏳ Sleeping for {check_interval} seconds...\n")
            time.sleep(check_interval)

        print("=" * 50)
        print("✅ REMINDER CHECKER STOPPED".center(50))
        print("=" * 50)