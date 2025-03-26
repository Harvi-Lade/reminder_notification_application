from datetime import datetime
import re
from database.db_manager import DBManager
from typing import Callable, Optional


# Instantiate DBManager for database interactions
db_manager = DBManager()

# Validation Functions
def validate_title(title: str, existing_titles: Optional[set[str]] = None) -> bool:
    """
    Validate the title for length and uniqueness.

    Args:
        title (str): The title to validate.
        existing_titles (Optional[set[str]]): Set of existing titles to ensure uniqueness.

    Returns:
        bool: True if the title is valid, False otherwise.
    """

    title = title.strip()

    if not title:
        print("❌ Title cannot be empty.")
        return False

    if not (3 <= len(title) <= 100):
        print("❌ Keep title between 3 - 100 characters.")
        return False

    if existing_titles is None:
        existing_titles = set()

    # ✅ Case-insensitive uniqueness check
    if title.lower() in {t.lower() for t in existing_titles}:
        print("❌ Title must be unique. This title is already in use.")
        return False

    # Soft validation for starting character
    if not title[0].isalpha():
        confirm = input("⚠️ Title doesn't start with a letter. Do you want to continue? (y/n): ").strip().lower()
        if confirm != 'y':
            return False

    return True

def validate_description(description: str) -> bool:
    """
    Validate the description for length and non-emptiness.

    Args:
        description (str): The description to validate.

    Returns:
        bool: True if the description is valid, False otherwise.
    """

    description = description.strip()

    if not description:
        print("❌ Description cannot be empty.")
        return False

    if not (5 <= len(description) <= 200):
        print("❌ Keep Description between 5 - 200 characters.")
        return False

    # Soft validation for starting character
    if not description[0].isalpha():
        confirm = input(
            "⚠️ Description doesn't start with a letter. Do you want to continue? (y/n): ").strip().lower()
        if confirm != 'y':
            return False

    return True

def validate_reminder_time(reminder_time: str) -> bool:
    """
    Validate the reminder time format and ensure it's in the future.

    Args:
        reminder_time (str): The reminder time string to validate.

    Returns:
        bool: True if the reminder time is valid and in the future, False otherwise.
    """
    date_formats = ["%Y-%m-%d %H:%M"]

    for date_format in date_formats:
        try:
            reminder_dt = datetime.strptime(reminder_time, date_format)
            if reminder_dt <= datetime.now():
                print("❌ Reminder time must be in the future.")
                return False
            return True  # Valid format and in the future
        except ValueError:
            continue  # Try next format

    print("❌ Invalid date format. Use YYYY-MM-DD HH:MM:SS.")
    return False

def validate_email(email: str) -> bool:
    """
    Validate the email format

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """
    email = email.strip()
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        print("❌ Invalid email format. Use example@domain.com.")
        return False
    return True

def validate_recurrence(recurrence: str) -> bool:
    """
    Validate that the recurrence type is one of the allowed values.

    Args:
        recurrence (str): The recurrence type to validate.

    Returns:
        bool: True if the recurrence type is valid, False otherwise.
    """
    valid_recurrences = {"none", "daily", "weekly", "monthly", "yearly"}
    if recurrence.lower() not in valid_recurrences:
        print("❌ Invalid recurrence type. Choose from: none, daily, weekly, monthly, yearly")
        return False
    return True

def validate_date(date_input: str) -> bool:
    """
    Validate a date in the format YYYY-MM-DD.

    Args:
        date_input (str): The date string to validate.

    Returns:
        bool: True if the date format is valid, False otherwise.
    """
    try:
        datetime.strptime(date_input, "%Y-%m-%d")
        return True
    except ValueError:
        print("Please enter date in this format (YYYY-MM-DD): ")
        return False

def validate_month(month_input: str) -> bool:
    """
    Validates a month in the format YYYY-MM.

    Args:
        month_input (str): The month string to validate.

    Returns:
        bool: True if the month format is valid, False otherwise.
    """
    try:
        datetime.strptime(month_input, "%Y-%m")
        return True
    except ValueError:
        print("Please enter date in this format (YYYY-MM): ")
        return False

def validate_year(year_input: str) -> bool:
    """
    Validate a year as a 4-digit number.

    Args:
        year_input (str): The year string to validate.

    Returns:
        bool: True if the input is a valid 4-digit year, False otherwise.
    """
    if year_input.isdigit() and len(year_input) == 4:
        return True
    else:
        print("❌ Please enter year in this format (YYYY): ")
        return False

def validate_reminder_id(user_input: str) -> bool:
    """
    Validate that the input is a positive integer.

    Args:
        user_input (str): The user input to validate.

    Returns:
        bool: True if the input is a positive integer, False otherwise.
    """
    if user_input.isdigit() and int(user_input) > 0:
        return True
    else:
        print("❌ Invalid choice! Please select a valid ID from the list above.")
        return False

def get_valid_input(prompt: str, validation_func: Optional[Callable[[str], bool]] = None) -> str:
    """
    Get valid user input, validate it (if a validation function is provided),
    and allow returning to the menu.

    Args:
        prompt (str): The input prompt to display.
        validation_func (Optional[Callable[[str], bool]]): A function to validate the input.

    Returns:
        str: The valid user input or "MENU_EXIT" if the user chooses to return to the menu.
    """
    while True:
        user_input = input(prompt).strip()

        if user_input.lower() == "menu":
            print("🔄 Returning to the main menu...")
            return "MENU_EXIT"  # Clearer than None

        if validation_func is None or validation_func(user_input):
            return user_input