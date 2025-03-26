import pytest
from unittest.mock import patch, MagicMock
from services.notification_service import NotificationService
from database.db_manager import DBManager
import logging


logging.basicConfig(level=logging.INFO)


# ✅ Test Initialization
class TestNotificationServiceInitialization:
    def test_initialization(self, db_manager):
        service = NotificationService(db_manager)
        assert service.email_sender is not None
        assert service.email_password is not None
        assert service.pushbullet_api_key is not None
        assert service.db_manager is db_manager


# ✅ Test Desktop Notifications
class TestDesktopNotification:
    def setup_method(self, db_manager):
        self.service = NotificationService(db_manager)  # Use the fixture directly

    @patch("services.notification_service.notification.notify")
    def test_send_desktop_notification_success(self, mock_notify, db_manager):
        # service = NotificationService(db_manager)

        title = "Test Reminder"
        message = "This is a test desktop notification"

        self.service.send_desktop_notification(title, message)

        mock_notify.assert_called_once_with(
            title=title,
            message=message,
            timeout=10
        )

    @patch("services.notification_service.notification.notify", side_effect=Exception("Desktop error"))
    def test_send_desktop_notification_failure(self, mock_notify, db_manager, caplog):
        # service = NotificationService(db_manager)

        self.service.send_desktop_notification("Test", "Message")

        assert "Failed to send desktop notification: Desktop error" in caplog.text


# ✅ Test Email Notifications
class TestEmailNotification:
    def setup_method(self, db_manager):
        self.service = NotificationService(db_manager)  # Use the fixture directly

    @pytest.mark.parametrize(
        "recipient, subject, message, expected_output",
        [
            (None, "Test Subject", "Test Message", "⚠️ No email provided. Skipping email notification."),
            ("test@example.com", "Test Subject", "Test Message", None),
        ]
    )
    @patch("smtplib.SMTP_SSL")
    def test_send_email_notification(self, mock_smtp, db_manager, recipient, subject, message, expected_output, capfd):
        # service = NotificationService(db_manager)

        if recipient is None:
            self.service.send_email_notification(recipient, subject, message)
            captured = capfd.readouterr()
            assert expected_output in captured.out
        else:
            mock_server = mock_smtp.return_value.__enter__.return_value
            self.service.send_email_notification(recipient, subject, message)
            mock_server.login.assert_called_once_with(self.service.email_sender, self.service.email_password)
            mock_server.send_message.assert_called_once()

    @patch("smtplib.SMTP_SSL", side_effect=Exception("Email error"))
    def test_send_email_notification_failure(self, mock_smtp, db_manager, caplog):
        # service = NotificationService(db_manager)

        self.service.send_email_notification("test@example.com", "Test Subject", "Test Message")

        assert "Error sending email to test@example.com: Email error" in caplog.text


# ✅ Test Pushbullet Notifications
class TestPushbulletNotification:
    def setup_method(self, db_manager):
        self.service = NotificationService(db_manager)  # Use the fixture directly

    @pytest.mark.parametrize(
        "status_code, response_text, expected_log",
        [
            (200, None, None),
            (400, "Bad Request", "Failed to send Pushbullet notification: Bad Request"),
            (401, "Unauthorized", "Failed to send Pushbullet notification: Unauthorized"),
        ]
    )
    @patch("requests.post")
    def test_send_pushbullet_notification(self, mock_post, db_manager, caplog, status_code, response_text, expected_log):
        # service = NotificationService(db_manager)

        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.text = response_text
        mock_post.return_value = mock_response

        self.service.send_pushbullet_notification("Test", "Message")

        mock_post.assert_called_once()
        if expected_log:
            assert expected_log in caplog.text

    @patch("requests.post", side_effect=Exception("Network error"))
    def test_send_pushbullet_notification_exception(self, mock_post, db_manager, caplog):
        # service = NotificationService(db_manager)

        self.service.send_pushbullet_notification("Test", "Message")

        assert "Error sending Pushbullet notification: Network error" in caplog.text


# ✅ Test Reminder Handling
class TestReminderHandling:
    def setup_method(self, db_manager):
        self.service = NotificationService(db_manager)  # Use the fixture directly

    @patch.object(NotificationService, 'send_desktop_notification')
    @patch.object(NotificationService, 'send_email_notification')
    @patch.object(NotificationService, 'send_pushbullet_notification')
    def test_check_reminder_success(self, mock_push, mock_email, mock_desktop):
        mock_update_status = MagicMock()

        # ✅ Create a mock db_manager
        mock_db_manager = MagicMock()
        mock_db_manager.update_reminder_status = mock_update_status

        # ✅ Pass the mock instance into NotificationService
        self.service = NotificationService(db_manager=mock_db_manager)

        reminder = {
            "id": 1,
            "title": "Test Reminder",
            "time": "10:00 AM",
            "email": "test@example.com"
        }

        self.service.check_reminder(reminder)

        mock_desktop.assert_called_once_with("Reminder Notification", "⏰ Reminder: Test Reminder at 10:00 AM")
        mock_email.assert_called_once_with("test@example.com", "Reminder Notification",
                                           "⏰ Reminder: Test Reminder at 10:00 AM")
        mock_push.assert_called_once_with("Reminder Notification", "⏰ Reminder: Test Reminder at 10:00 AM")

        # ✅ Assert database update is called
        mock_update_status.assert_called_once_with(1, notified=True)

    def test_notify_reminders_empty(self, db_manager, capfd):
        # service = NotificationService(db_manager)

        self.service.notify_reminders([])

        captured = capfd.readouterr()
        assert "✅ No due reminders found." in captured.out

    @patch.object(NotificationService, 'check_reminder', side_effect=[None, Exception("Pushbullet failure")])
    def test_notify_reminders_mixed(self, mock_check, db_manager, caplog):
        # service = NotificationService(db_manager)

        reminders = [
            {"id": 1, "title": "Test 1", "time": "10:00 AM", "email": "test1@example.com"},
            {"id": 2, "title": "Test 2", "time": "11:00 AM", "email": "test2@example.com"},
        ]

        self.service.notify_reminders(reminders)

        assert mock_check.call_count == 2
        assert "Pushbullet failure" in caplog.text
