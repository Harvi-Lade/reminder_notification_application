import pytest
from views.cli_menu import (
    validate_title,
    validate_description,
    validate_reminder_time,
    validate_email,
    validate_recurrence,
    validate_date,
    validate_month,
    validate_year,
    validate_reminder_id,
    get_valid_input
)
from datetime import datetime, timedelta


# ------------------------------ Test validate_title ------------------------------

def test_validate_title_valid():
    assert validate_title("Morning Workout", {"meeting", "doctor"}) is True

def test_validate_title_empty():
    assert validate_title("") is False

def test_validate_title_too_short():
    assert validate_title("Go") is False

def test_validate_title_too_long():
    long_title = "A" * 101
    assert validate_title(long_title) is False

def test_validate_title_duplicate():
    assert validate_title("Meeting", {"meeting", "doctor"}) is False

def test_validate_title_non_alpha_start_user_rejects(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert validate_title("1Reminder") is False

def test_validate_title_non_alpha_start_user_accepts(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert validate_title("1Reminder") is True


# ------------------------------ Test validate_description ------------------------------

def test_validate_description_valid():
    assert validate_description("This is a valid description.") is True

def test_validate_description_empty():
    assert validate_description("") is False

def test_validate_description_too_short():
    assert validate_description("1234") is False

def test_validate_description_too_long():
    long_description = "A" * 201
    assert validate_description(long_description) is False

def test_validate_description_non_alpha_start_user_rejects(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'n')
    assert validate_description("1Description") is False

def test_validate_description_non_alpha_start_user_accepts(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'y')
    assert validate_description("1Description") is True


# ------------------------------ Test validate_reminder_time ------------------------------

def test_validate_reminder_time_valid():
    future_time = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    assert validate_reminder_time(future_time) is True

def test_validate_reminder_time_past():
    past_time = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M")
    assert validate_reminder_time(past_time) is False

def test_validate_reminder_time_invalid_format():
    assert validate_reminder_time("2025-03-25 99:99") is False


# ------------------------------ Test validate_email ------------------------------

def test_validate_email_valid():
    assert validate_email("test@example.com") is True

def test_validate_email_invalid_format():
    assert validate_email("invalid-email") is False


# ------------------------------ Test validate_recurrence ------------------------------

def test_validate_recurrence_valid():
    assert validate_recurrence("daily") is True

def test_validate_recurrence_invalid():
    assert validate_recurrence("hourly") is False


# ------------------------------ Test validate_date ------------------------------

def test_validate_date_valid():
    assert validate_date("2025-03-25") is True

def test_validate_date_invalid_format():
    assert validate_date("25-03-2025") is False


# ------------------------------ Test validate_month ------------------------------

def test_validate_month_valid():
    assert validate_month("2025-03") is True

def test_validate_month_invalid_format():
    assert validate_month("03-2025") is False


# ------------------------------ Test validate_year ------------------------------

def test_validate_year_valid():
    assert validate_year("2025") is True

def test_validate_year_invalid_format():
    assert validate_year("25") is False


# ------------------------------ Test validate_reminder_id ------------------------------

def test_validate_reminder_id_valid():
    assert validate_reminder_id("5") is True

def test_validate_reminder_id_invalid_out_of_range():
    assert validate_reminder_id("0") is False


# ------------------------------ Test get_valid_input ------------------------------

def test_get_valid_input_valid(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'Workout')
    assert get_valid_input("Enter title:") == "Workout"

def test_get_valid_input_menu_exit(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'menu')
    assert get_valid_input("Enter title:") == "MENU_EXIT"

def test_get_valid_input_with_validation(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: 'test@example.com')
    assert get_valid_input("Enter email:", validate_email) == "test@example.com"

def test_get_valid_input_with_invalid_then_valid(monkeypatch):
    inputs = iter(["invalid-email", "test@example.com"])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))
    assert get_valid_input("Enter email:", validate_email) == "test@example.com"
