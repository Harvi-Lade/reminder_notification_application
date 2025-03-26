import pytest
from utils.validation_utils import (
    validate_title, validate_description, validate_reminder_time,
    validate_email, validate_recurrence, validate_date, validate_month,
    validate_year, validate_reminder_id, get_valid_input
)
from unittest.mock import patch
from datetime import datetime, timedelta


@pytest.fixture
def mock_input(mocker):
    return mocker.patch("builtins.input")

# Test validate_title
def test_validate_title_valid():
    assert validate_title("My Reminder", existing_titles={"Test", "Sample"}) is True

def test_validate_title_empty():
    assert validate_title("") is False

def test_validate_title_too_short():
    assert validate_title("Hi") is False

def test_validate_title_too_long():
    assert validate_title("A" * 101) is False

def test_validate_title_non_unique():
    assert validate_title("test", existing_titles={"Test", "Sample"}) is False

def test_validate_title_non_alpha_start(mock_input):
    mock_input.return_value = "y"
    assert validate_title("1Reminder") is True

def test_validate_title_non_alpha_start_reject(mock_input):
    mock_input.return_value = "n"
    assert validate_title("1Reminder") is False

# Test validate_description
def test_validate_description_valid():
    assert validate_description("This is a valid description.") is True

def test_validate_description_empty():
    assert validate_description("") is False

def test_validate_description_too_short():
    assert validate_description("Hi") is False

def test_validate_description_too_long():
    assert validate_description("A" * 201) is False

def test_validate_description_non_alpha_start(mock_input):
    mock_input.return_value = "y"
    assert validate_description("1Description") is True

def test_validate_description_non_alpha_start_reject(mock_input):
    mock_input.return_value = "n"
    assert validate_description("1Description") is False

# Test validate_reminder_time
def test_validate_reminder_time_valid():
    future_time = (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    assert validate_reminder_time(future_time) is True

def test_validate_reminder_time_past():
    past_time = (datetime.now() - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")
    assert validate_reminder_time(past_time) is False

def test_validate_reminder_time_invalid_format():
    assert validate_reminder_time("2025/03/24 12:00") is False

# Test validate_email
def test_validate_email_valid():
    assert validate_email("test@example.com") is True

def test_validate_email_invalid():
    assert validate_email("test@com") is False

# Test validate_recurrence
def test_validate_recurrence_valid():
    assert validate_recurrence("daily") is True

def test_validate_recurrence_invalid():
    assert validate_recurrence("hourly") is False

# Test validate_date
def test_validate_date_valid():
    assert validate_date("2025-03-24") is True

def test_validate_date_invalid():
    assert validate_date("24-03-2025") is False

# Test validate_month
def test_validate_month_valid():
    assert validate_month("2025-03") is True

def test_validate_month_invalid():
    assert validate_month("03-2025") is False

# Test validate_year
def test_validate_year_valid():
    assert validate_year("2025") is True

def test_validate_year_invalid():
    assert validate_year("25") is False

# Test validate_reminder_id
def test_validate_reminder_id_valid():
    assert validate_reminder_id("5") is True

def test_validate_reminder_id_invalid():
    assert validate_reminder_id("-1") is False
    assert validate_reminder_id("abc") is False

# Test get_valid_input
@patch("builtins.input", side_effect=["test input"])
def test_get_valid_input_valid(mock_input):
    assert get_valid_input("Enter:") == "test input"

@patch("builtins.input", side_effect=["menu"])
def test_get_valid_input_menu(mock_input):
    assert get_valid_input("Enter:") == "MENU_EXIT"

@patch("builtins.input", side_effect=["invalid", "valid"])
def test_get_valid_input_with_validation(mock_input):
    assert get_valid_input("Enter:", lambda x: x == "valid") == "valid"
