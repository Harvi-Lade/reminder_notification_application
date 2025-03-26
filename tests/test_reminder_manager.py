import pytest
from services.reminder_manager import ReminderManager
from database.db_manager import DBManager
from unittest.mock import patch
from datetime import datetime


# Sample reminder data for reuse
SAMPLE_REMINDER = {
    "title": "Doctor's Appointment",
    "description": "Routine checkup",
    "reminder_time": "2025-05-20 10:00",
    "email": None,
    "recurrence": "none"
}

SAMPLE_REMINDERS = [
    {"title": "Doctor Appointment", "description": "Visit Dr. Smith", "reminder_time": "2025-06-15 10:00", "email": "test@example.com", "recurrence": "none", "notified": 0},
    {"title": "Meeting", "description": "Project status update", "reminder_time": "2025-06-20 15:00", "email": "", "recurrence": "none", "notified": 0},
    {"title": "Gym", "description": "Leg day", "reminder_time": "2025-07-10 18:00", "email": "gym@example.com", "recurrence": "weekly", "notified": 1}
]


@pytest.fixture
def reminder_manager(db_manager):
    return ReminderManager(db_manager)

# ✅ 1. Test adding a reminder (positive case)
def test_add_reminder(reminder_manager, db_manager):
    reminder_manager.add_reminder(**SAMPLE_REMINDER)
    reminders = db_manager.fetch_all("SELECT * FROM reminders")

    assert len(reminders) == 1
    assert reminders[0][1] == SAMPLE_REMINDER["title"]
    assert reminders[0][2] == SAMPLE_REMINDER["description"]
    assert reminders[0][3] == SAMPLE_REMINDER["reminder_time"]
    assert reminders[0][4] == SAMPLE_REMINDER["email"]
    assert reminders[0][5] == SAMPLE_REMINDER["recurrence"]

# ✅ 2. Test fetching a valid reminder by ID (positive case)
def test_get_reminder_by_id(reminder_manager, db_manager):
    # Add a reminder first
    reminder_manager.add_reminder(**SAMPLE_REMINDER)
    reminder_id = db_manager.fetch_all("SELECT id FROM reminders")[0][0]

    # Now test get_reminder_by_id
    reminder = reminder_manager.get_reminder_by_id(reminder_id)

    assert reminder is not None
    assert reminder[1] == SAMPLE_REMINDER["title"]
    assert reminder[2] == SAMPLE_REMINDER["description"]
    assert reminder[3] == SAMPLE_REMINDER["reminder_time"]
    assert reminder[4] == SAMPLE_REMINDER["email"]
    assert reminder[5] == SAMPLE_REMINDER["recurrence"]


# ✅ 3. Test editing an existing reminder (positive case)
def test_edit_reminder(reminder_manager, db_manager):
    # Step 1: Add a reminder first
    reminder_manager.add_reminder(**SAMPLE_REMINDER)
    reminder_id = db_manager.fetch_all("SELECT id FROM reminders")[0][0]

    # Step 2: Updated data
    UPDATED_REMINDER = {
        "title": "Dentist Appointment",
        "description": "Teeth cleaning session",
        "reminder_time": "2025-06-15 14:30",
        "email": "test@example.com",
        "recurrence": "weekly"
    }

    # Step 3: Edit the reminder
    reminder_manager.edit_reminder(reminder_id, **UPDATED_REMINDER)

    # Step 4: Fetch and verify updated values
    updated_reminder = reminder_manager.get_reminder_by_id(reminder_id)

    assert updated_reminder is not None
    assert updated_reminder[1] == UPDATED_REMINDER["title"]
    assert updated_reminder[2] == UPDATED_REMINDER["description"]
    assert updated_reminder[3] == UPDATED_REMINDER["reminder_time"]
    assert updated_reminder[4] == UPDATED_REMINDER["email"]
    assert updated_reminder[5] == UPDATED_REMINDER["recurrence"]

# ✅ 4. Test deleting an existing reminder (positive case)
def test_delete_reminder(mocker, reminder_manager, db_manager):
    # Step 1: Add a reminder
    reminder_manager.add_reminder(**SAMPLE_REMINDER)
    reminder_id = db_manager.fetch_all("SELECT id FROM reminders")[0][0]

    # Step 2: Confirm that the reminder exists
    reminder = reminder_manager.get_reminder_by_id(reminder_id)
    assert reminder is not None

    # Step 3: Mock user input to pass reminder ID
    mocker.patch('services.reminder_manager.get_valid_input', return_value=str(reminder_id))

    # Step 4: Delete using CLI-based function
    reminder_manager.delete_reminder()

    # Step 5: Verify deletion
    deleted_reminder = reminder_manager.get_reminder_by_id(reminder_id)
    assert deleted_reminder is None

@pytest.fixture
def setup_sample_reminders(reminder_manager):
    for reminder in SAMPLE_REMINDERS:
        # Remove 'notified' from sample data before adding
        reminder_data = {k: v for k, v in reminder.items() if k != 'notified'}
        reminder_manager.add_reminder(**reminder_data)


def test_display_all_reminders(reminder_manager, setup_sample_reminders, capfd):
    reminder_manager.display_reminders("all")
    captured = capfd.readouterr().out
    assert "Doctor Appointment" in captured
    assert "Meeting" in captured
    assert "Gym" in captured


@patch('services.reminder_manager.get_valid_input', return_value="2025")
@patch.object(DBManager, 'fetch_all', return_value=[
    (1, "Doctor Appointment", "Visit Dr. Smith", "2025-06-15 10:00", "test@example.com", "none", False),
    (2, "Meeting", "Project status update", "2025-06-20 15:00", "", "none", False),
    (3, "Gym", "Leg day", "2025-07-10 18:00", "gym@example.com", "weekly", True)
])
def test_display_reminders_by_year(mock_input, mock_fetch, reminder_manager, setup_sample_reminders, capfd):
    reminder_manager.display_reminders("year")
    captured = capfd.readouterr().out

    assert "Doctor Appointment" in captured
    assert "Meeting" in captured
    assert "Gym" in captured
    assert "Visit Dr. Smith" in captured
    assert "Project status update" in captured
    assert "Leg day" in captured


# ✅ 7. Test fetching all reminder titles (positive case)
@patch.object(DBManager, 'fetch_all', return_value=[
    ("Doctor Appointment",),
    ("Meeting",),
    ("Gym",)
])
def test_get_all_titles(mock_fetch, reminder_manager):
    expected_titles = {"Doctor Appointment", "Meeting", "Gym"}  # Use a set here
    titles = reminder_manager.get_all_titles()
    assert titles == expected_titles
