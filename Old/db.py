"""
import sqlite3
import os

def initialize_database(db_path="habits.db"):
    Create the SQLite database and tables if they do not already exist.
    Includes basic input validation and error handling.
    # Validate database path
    if not isinstance(db_path, str) or not db_path.strip():
        raise ValueError("Database path must be a non-empty string.")

    try:
        # Create folder if necessary
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)

        # Connect to SQLite (creates file if it doesn't exist)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Create habits table
        cursor.execute
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                periodicity TEXT NOT NULL,   -- e.g. daily, weekly
                created_at TEXT NOT NULL
            );
        )

        # Create log table to store check‑ins
        cursor.execute(
            CREATE TABLE IF NOT EXISTS habit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                FOREIGN KEY (habit_id) REFERENCES habits(id)
                    ON DELETE CASCADE
            );
        )

        conn.commit()
        print("Database and tables created successfully.")

    except sqlite3.Error as e:
        print("SQLite error:", e)

    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    initialize_database("habits.db")
"""
