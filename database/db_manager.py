# Database connection and query management

import sqlite3
from config.settings import DB_NAME
from typing import Tuple, List, Any


class DBManager:
    def __init__(self, db_name: str = DB_NAME, create_table: bool = True) -> None:
        self.db_name = db_name
        if create_table:
            self.create_table()

    @staticmethod
    def create_table() -> None:
        """
        Creates the 'reminders' table in the database if it doesn't exist.
        """
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reminders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    reminder_time DATETIME NOT NULL,
                    email TEXT,
                    recurrence TEXT DEFAULT 'none',
                    notified INTEGER DEFAULT 0
                )
            """)
            conn.commit()

    @staticmethod
    def fetch_all(query: str, params: Tuple[Any, ...] = ()) -> List[Tuple[Any, ...]]:
        """
        Executes a SELECT query and fetches all matching results.

        Args:
            query (str): The SQL query to execute.
            params (Tuple[Any, ...], optional): Parameters to use in query.

        Returns:
            List[Tuple[Any, ...]]: A list of tuples containing the fetched rows.
        """
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"❌ Database Error (fetch_all): {e}")
            return []

    @staticmethod
    def execute(query: str, params: Tuple[Any, ...] = ()) -> None:
        """
        Executes an INSERT, UPDATE, or DELETE query and commits the changes.

        Args:
            query (str): The SQL query to execute.
            params (Tuple[Any, ...], optional): Parameters to use in the query.
        """
        try:
            with sqlite3.connect(DB_NAME) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
        except sqlite3.Error as e:
            print(f"❌ Database Error (execute): {e}")

    def update_reminder_status(self, reminder_id: int, notified: bool = True) -> None:
        """
        Updates the 'notified' status of a reminder in the database.

        Args:
            reminder_id (int): The ID of the reminder to update.
            notified (bool, optional): Whether the reminder has been notified. Defaults to True
        """
        query = "UPDATE reminders SET notified = ? WHERE id = ?"
        self.execute(query, (int(notified), reminder_id))