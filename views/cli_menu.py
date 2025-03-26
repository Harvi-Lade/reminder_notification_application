# CLI menu and user input handling

from services.reminder_manager import ReminderManager
from config.settings import PUSHBULLET_API_KEY
from services.scheduler_service import ReminderScheduler
from services.notification_service import NotificationService
from utils.validation_utils import *


class ShowMenu:
    """Main Application Class for the Reminder Notification Application."""

    def __init__(self) -> None:
        """
        Initialize the ShowMenu class.

        - Initializes the database connection.
        - Sets up the reminder manager, notification service, and scheduler service.
        """
        self.db_manager = DBManager()  # Initializes database connection
        self.scheduler_service = ReminderScheduler(self.db_manager)
        self.reminder_manager = ReminderManager(self.db_manager, PUSHBULLET_API_KEY, self.scheduler_service)
        self.notification_service = NotificationService(self.db_manager)

    def menu(self) -> None:
        """
        Display the main menu and handle user input.

        Options:
            1. Add Reminder
            2. View Reminders
            3. Edit Reminder
            4. Delete Reminder
            5. Notify Due Reminders
            6. Exit
        """
        while True:
            print("\n📌 Menu:")
            print("1. Add Reminder")
            print("2. View Reminders")
            print("3. Edit Reminder")
            print("4. Delete Reminder")
            print("5. Notify Due Reminders")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == "1":
                existing_titles = self.reminder_manager.get_all_titles()
                title = get_valid_input(
                    "Enter title (or type 'menu' to return to menu): ",
                    lambda t: validate_title(t, existing_titles)
                )
                if title == "MENU_EXIT":
                    continue

                description = get_valid_input("Enter description (or type 'menu' to return to menu): ", validate_description)
                if description == "MENU_EXIT": continue

                reminder_time = get_valid_input("Enter reminder time (YYYY-MM-DD HH:MM) (or type 'menu' to return to menu): ", validate_reminder_time)
                if reminder_time == "MENU_EXIT": continue

                email = input("Enter your email (or press Enter to skip): ").strip()
                if email:
                    while not validate_email(email):
                        email = input("❌ Invalid email. Enter again (or press Enter to skip): ").strip()
                        if email == "":  # Allow skipping after an invalid attempt
                            email = None
                            break
                else:
                    email = None  # Store None if empty

                recurrence = input("Enter recurrence (none/daily/weekly/monthly/yearly) (or press Enter to skip): ").strip()
                if recurrence:  # Validate only if the user entered something
                    while not validate_recurrence(recurrence):
                        recurrence = input("❌ Invalid recurrence. Enter again (or press Enter to skip): ").strip()
                        if recurrence == "":  # Allow skipping after an invalid attempt
                            recurrence = None
                            break
                else:
                    recurrence = None  # Store None if empty

                self.reminder_manager.add_reminder(title, description, reminder_time, email, recurrence)

            elif choice == "2":
                self.reminder_manager.view_reminders()

            elif choice == "3":
                self.reminder_manager.edit_reminder_cli()

            elif choice == "4":
                self.reminder_manager.delete_reminder()

            elif choice == "5":
                self.scheduler_service.run_reminder_checker()

            elif choice == "6":
                print("Goodbye! Hope to remind you again soon! 😊🔔")
                break

            else:
                print("Invalid choice. Please try again.")