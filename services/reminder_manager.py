# Core logic for handling reminders CRUD

from pushbullet import Pushbullet
from config.settings import EMAIL_SENDER, EMAIL_PASSWORD
from utils.validation_utils import *
from database.db_manager import DBManager
from typing import Optional
from services.scheduler_service import ReminderScheduler


class ReminderManager:
    """Handles CRUD operations for reminders and Pushbullet notifications."""

    def __init__(self, db_manager: DBManager, pushbullet_api_key: Optional[str] = None, scheduler: Optional[ReminderScheduler] = None) -> None:
        """Initialize ReminderManager with database and optional Pushbullet API."""

        self.db_manager = db_manager
        self.scheduler = scheduler

        # Initialize Pushbullet
        try:
            self.pb = Pushbullet(pushbullet_api_key) if pushbullet_api_key else None
        except Exception as e:
            print(f"❌ Error initializing Pushbullet: {e}")
            self.pb = None

        # Email Credentials
        self.email_address = EMAIL_SENDER
        self.email_password = EMAIL_PASSWORD

    def add_reminder(self, title: str, description: str, reminder_time: str, email: Optional[str] = None, recurrence: str ="none") -> None:
        """
        Adds a new reminder.

        Args:
            title (str): Reminder title.
            description (str): Reminder description.
            reminder_time (str): Date and time of the reminder (format: "%Y-%m-%d %H:%M").
            email (Optional[str]): Email for sending the reminder. Defaults to None.
            recurrence (str): Recurrence pattern. Defaults to "none".

        Raises:
            Exception: If date-time format validation or database insertion fails.
        """

        try:
            datetime.strptime(reminder_time, "%Y-%m-%d %H:%M")  # Validate format
            query = """
                INSERT INTO reminders (title, description, reminder_time, email, recurrence)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db_manager.execute(query, (title, description, reminder_time, email, recurrence))
            print(f"✅ Reminder added: {title} at {reminder_time} {'for ' + email if email else ''} (Recurrence: {recurrence})")
        except ValueError:
            print("❌ Invalid date-time format. Use YYYY-MM-DD HH:MM.")

    def get_reminder_by_id(self, reminder_id: int) -> Optional[dict]:
        """
        Fetches a reminder by its ID.

        Args:
            reminder_id (int): ID of the reminder.

        Returns:
            Optional[dict]: Reminder details if found, otherwise None.
        """
        query = "SELECT * FROM reminders WHERE id = ?"
        result = self.db_manager.fetch_all(query, (reminder_id,))
        return result[0] if result else None

    def edit_reminder(self) -> None:
        """
        Edits an existing reminder by selecting it from the database.

        Prompts the user to select a reminder and update its details.
        Allows keeping existing values if no new input is provided.
        """
        # Fetch and display all reminders ordering them by time
        reminders = self.db_manager.fetch_all("SELECT id, title, reminder_time FROM reminders ORDER BY reminder_time ASC;")

        if not reminders:
            print("❌ No reminders found.")
            return

        print("\n📋 Available Reminders:")
        for reminder in reminders:
            print(f"  ID: [{reminder[0]}] | {reminder[1]} | {reminder[2]}")

        # Ask for Reminder ID
        reminder_id = get_valid_input("\nEnter Reminder ID to edit (or type 'menu' to go back): ", validate_reminder_id)
        if reminder_id == "MENU_EXIT":
            return

        reminder_id = int(reminder_id)  # ✅ Convert to int after validation
        reminder_data = self.get_reminder_by_id(reminder_id)

        if not reminder_data:
            print("❌ Reminder ID not found.")
            return

        print("\nPress Enter to keep existing values.")

        # Get new values with validation, keeping old values if input is empty
        new_title = input(f"New title (current: {reminder_data[1]}): ").strip()
        if new_title:
            while not validate_title(new_title):
                new_title = input(f"Enter a new title (current: {reminder_data[1]}): ").strip()
        else:
            new_title = reminder_data[1]

        new_description = input(f"New description (current: {reminder_data[2]}): ").strip()
        if new_description:
            while not validate_description(new_description):
                new_description = input(f"Enter a new description (current: {reminder_data[2]}): ").strip()
        else:
            new_description = reminder_data[2]

        new_reminder_time = input(f"New date-time (YYYY-MM-DD HH:MM, current: {reminder_data[3]}): ").strip()
        if new_reminder_time:
            while not validate_reminder_time(new_reminder_time):
                new_reminder_time = input(f"Enter a new date-time (current: {reminder_data[3]}): ").strip()
        else:
            new_reminder_time = reminder_data[3]

        new_email = input(f"New email (current: {reminder_data[4]}): ").strip()
        if new_email:
            while not validate_email(new_email):
                new_email = input(f"Enter a new email (current: {reminder_data[4]}): ").strip()
        else:
            new_email = reminder_data[4]

        new_recurrence = input(f"New recurrence (none/daily/weekly/monthly, current: {reminder_data[5]}): ").strip()
        if new_recurrence:
            while not validate_recurrence(new_recurrence):
                new_recurrence = input(f"Enter a new recurrence (current: {reminder_data[5]}): ").strip()
        else:
            new_recurrence = reminder_data[5]

        # Check if all values remain unchanged
        if (
                new_title == reminder_data[1] and
                new_description == reminder_data[2] and
                new_reminder_time == reminder_data[3] and
                new_email == reminder_data[4] and
                new_recurrence == reminder_data[5]
        ):
            print("🙃 Looks like you changed your mind! Your reminder is unchanged!")
            return
        else:
            query = """
                    UPDATE reminders
                    SET title = ?, description = ?, reminder_time = ?, email = ?, recurrence = ?
                    WHERE id = ?
                    """
            self.db_manager.execute(query,
                                    (new_title, new_description, new_reminder_time, new_email, new_recurrence,
                                     reminder_id))

            # Reset notified status if user updates the reminder_time
            if datetime.strptime(new_reminder_time, '%Y-%m-%d %H:%M') > datetime.now():
                self.db_manager.update_reminder_status(reminder_id, False)  # Reset notified to False

            print(f"✅ Reminder {reminder_id} updated successfully!")

    def delete_reminder(self) -> None:
        """Delete a reminder after confirming its existence.

        Displays available reminders and prompts the user to select one for deletion.
        """

        # Fetch and display all reminders and ordering them by time
        reminders = self.db_manager.fetch_all("SELECT id, title, reminder_time FROM reminders ORDER BY reminder_time ASC;")

        if not reminders:
            print("❌ No reminders found.")
            return

        print("\n📋 Available Reminders:")
        for reminder in reminders:
            print(f"  [{reminder[0]}] {reminder[1]} - {reminder[2]}")

        reminder_id = get_valid_input("\nEnter Reminder ID to edit (or type 'menu' to go back): ", validate_reminder_id)
        if reminder_id == "MENU_EXIT":
            return
        reminder_id = int(reminder_id)  # ✅ Convert to int after validation

        if not self.get_reminder_by_id(reminder_id):
            print("❌ Reminder ID not found.")
            return

        query = "DELETE FROM reminders WHERE id = ?"
        self.db_manager.execute(query, (reminder_id,))
        print(f"✅ Reminder {reminder_id} deleted successfully!")

    def display_reminders(self, filter_type: str = "all") -> None:
        """Displays reminders based on the selected filter type.

        Args:
            filter_type (str): The type of filter to apply ("all", "date", "month", "year").
                - "all": Display all reminders.
                - "date": Display reminders for a specific date.
                - "month": Display reminders for a specific month.
                - "year": Display reminders for a specific year.
        """

        query = "SELECT id, title, description, reminder_time, email, recurrence, notified FROM reminders ORDER BY reminder_time ASC;"
        params = ()

        if filter_type == "date":
            date_input = get_valid_input("Enter date (YYYY-MM-DD) or type 'menu' to return to menu): ", validate_date)
            if date_input == "MENU_EXIT":
                return
            print(f"Reminders for {date_input}")
            query += " WHERE reminder_time LIKE ?"
            params = (f"{date_input}%",)

        elif filter_type == "month":
            month_input = get_valid_input("Enter month (YYYY-MM) or type 'menu' to return to menu): ", validate_month)
            if month_input == "MENU_EXIT":
                return
            query += " WHERE strftime('%Y-%m', reminder_time) = ?"
            params = (month_input,)

        elif filter_type == "year":
            year_input = get_valid_input("Enter year (YYYY) or type 'menu' to return to menu): ", validate_year)
            if year_input == "MENU_EXIT":
                return
            query += " WHERE strftime('%Y', reminder_time) = ?"
            params = (year_input,)

        reminders = self.db_manager.fetch_all(query, params)

        if not reminders:
            print("❌ No reminders found.")
            return

        print("_" * 40)
        for reminder in reminders:
            print("\n🔔 Reminder ID:", reminder[0])
            print("📌 Title:", reminder[1])
            print("📝 Description:", reminder[2])
            print("📅 Time:", reminder[3])
            print("📧 Email:", reminder[4] if reminder[4] else "Not Set")
            print("🔁 Recurrence:", reminder[5])
            print("✅ Notified:", "Yes" if reminder[6] else "No")
            print("-" * 40)

    def view_reminders(self) -> None:
        """
        Allow users to choose how they want to view reminders.

        Options:
        1. Date-wise
        2. Month-wise
        3. Yearly-wise
        4. All Reminders
        5. Return to Main Menu
        """

        options = {
            "1": "date",
            "2": "month",
            "3": "year",
            "4": "all"
        }

        while True:
            print("\n📅 How would you like to view your reminders?")
            print("1. Date-wise")
            print("2. Month-wise")
            print("3. Yearly-wise")
            print("4. All Reminders")
            print("5. Main Menu")

            choice = input("Enter your choice (1-5): ")

            if choice in options:
                self.display_reminders(options[choice])
            elif choice == "5":
                print("Returning to Menu...")
                break
            else:
                print("⚠️ Invalid choice. Please enter a number between 1 and 5.")

    def get_all_titles(self) -> set[str]:
        """
        Fetch all existing reminder titles from the database.

        Returns:
            set[str]: A set of existing reminder titles.
        """
        query = "SELECT title FROM reminders"
        result = self.db_manager.fetch_all(query)
        return {row[0] for row in result}
