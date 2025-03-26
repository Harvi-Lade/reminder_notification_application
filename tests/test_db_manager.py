
def test_create_table(db_manager):
    query = "SELECT name FROM sqlite_master WHERE type='table' AND name='reminders';"
    result = db_manager.fetch_all(query)
    assert len(result) == 1, "Table 'reminders' should be created"

def test_execute_valid_insert(db_manager):
    query = """
        INSERT INTO reminders (title, description, reminder_time, email, recurrence, notified)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = ("Test Reminder", "This is a test reminder", "2025-03-25 10:00:00", "test@example.com", "none", 0)
    db_manager.execute(query, params)

    # Verify the inserted data
    result = db_manager.fetch_all("SELECT * FROM reminders")
    assert len(result) == 1
    assert result[0][1] == "Test Reminder"
    assert result[0][2] == "This is a test reminder"

def test_execute_invalid_query(db_manager):
    query = "INSERT INTO reminders (title, description) VALUES (?, ?)"
    params = ("Incomplete Reminder",)  # Missing one parameter

    db_manager.execute(query, params)  # Should not raise an error, but also not insert data

    result = db_manager.fetch_all("SELECT * FROM reminders")
    assert len(result) == 0  # No data should be inserted


def test_fetch_all_with_data(db_manager):
    # Insert sample reminders
    query = """
        INSERT INTO reminders (title, description, reminder_time, email, recurrence, notified)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = ("Test Reminder", "This is a test reminder", "2025-03-25 10:00:00", "test@example.com", "none", 0)
    db_manager.execute(query, params)

    # Fetch all reminders
    result = db_manager.fetch_all("SELECT * FROM reminders")

    # Verify the result
    assert len(result) == 1
    assert result[0][1] == "Test Reminder"
    assert result[0][2] == "This is a test reminder"
    assert result[0][3] == "2025-03-25 10:00:00"
    assert result[0][4] == "test@example.com"
    assert result[0][5] == "none"
    assert result[0][6] == 0


def test_fetch_all_with_no_data(db_manager):
    # Fetch all reminders without adding data
    result = db_manager.fetch_all("SELECT * FROM reminders")

    # Verify the result is an empty list
    assert result == []


def test_update_reminder_status(db_manager):
    # Insert sample reminder
    query = """
        INSERT INTO reminders (title, description, reminder_time, email, recurrence, notified)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = ("Test Reminder", "This is a test reminder", "2025-03-25 10:00:00", "test@example.com", "none", 0)
    db_manager.execute(query, params)

    # Get reminder ID
    reminder_id = db_manager.fetch_all("SELECT id FROM reminders")[0][0]

    # Update reminder status
    db_manager.update_reminder_status(reminder_id, 1)

    # Fetch the updated reminder
    result = db_manager.fetch_all("SELECT notified FROM reminders WHERE id = ?", (reminder_id,))

    # Verify the status is updated
    assert result[0][0] == 1


def test_update_reminder_status_invalid_id(db_manager):
    # Try to update a non-existent reminder ID
    invalid_id = 9999
    db_manager.update_reminder_status(invalid_id, 1)

    # Ensure no data was updated
    result = db_manager.fetch_all("SELECT * FROM reminders WHERE id = ?", (invalid_id,))

    # Should return an empty result since ID does not exist
    assert result == []
