import sqlite3
import os
from datetime import datetime, date
from habit import Frequency, Habit, DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit
from habit_management import HabitTracker

FREQUENCY_CLASS_MAP = {
    Frequency.DAILY.value:        DailyHabit,
    Frequency.WEEKLY.value:       WeeklyHabit,
    Frequency.BIWEEKLY.value:     BiWeeklyHabit,
    Frequency.TWICE_WEEKLY.value: TwiceWeeklyHabit
}

def init_db(db_path: str = "habits.db") -> sqlite3.Connection:
    """
    Initialise the SQLite database and create tables if they don't already exist.

    Argumentss:
        db_path: path to the .db file. 

    Returns:
        An open sqlite3.Connection object.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    cursor = conn.cursor()
    conn.execute("PRAGMA foreign_keys = ON")

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS habits (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT    NOT NULL UNIQUE,
            frequency    TEXT    NOT NULL,
            start_date   DATE    NOT NULL,
            created_date DATE    NOT NULL,
            description  TEXT,
            is_paused    INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS completions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id      INTEGER NOT NULL,
            completion_dt DATETIME    NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        );

        CREATE TABLE IF NOT EXISTS notes (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id   INTEGER NOT NULL,
            note_date  DATE    NOT NULL,
            note       TEXT    NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id)
        );
    """)

    conn.commit()
    return conn

def save_habit(conn: sqlite3.Connection, habit: Habit) -> None: ##Working on this one, need to add protections and change to boolean when the function works.
    """
    Function to save a single Habit object and all its completions and notes to the database. 
    If a habit with the same name already exists, it will be replaced.

    Arguments:
        conn: open database connection.
        habit: the Habit object to save.
    """
    cursor = conn.cursor()

    # save or replace the habit row
    cursor.execute("""
        INSERT OR REPLACE INTO habits
            (name, frequency, start_date, created_date, description, is_paused)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        habit.name,
        habit.frequency.value,
        habit.start_date.isoformat(),
        habit.created_date.isoformat(),
        habit.description,
        1 if habit._manually_paused else 0
    ))

    habit_id = cursor.lastrowid

    # delete existing completions and notes for this habit
    # then re-insert — simpler than trying to sync differences
    cursor.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM notes WHERE habit_id = ?", (habit_id,))

    # save completions
    cursor.executemany("""
        INSERT INTO completions (habit_id, completion_dt)
        VALUES (?, ?)
    """, [
        (habit_id, c.isoformat()) for c in habit.completions
    ])

    # save notes
    cursor.executemany("""
        INSERT INTO notes (habit_id, note_date, note)
        VALUES (?, ?, ?)
    """, [
        (habit_id, note_date.isoformat(), note_text)
        for note_date, note_text in habit.notes.items()
    ])

    conn.commit()

    #####################################################################################################################

    def save_all_habits(conn: sqlite3.Connection, tracker: HabitTracker) -> None:
    """
    Save all habits in a HabitTracker to the database.

    Args:
        conn: open database connection.
        tracker: the HabitTracker whose habits should be saved.
    """
    for habit in tracker.habits:
        save_habit(conn, habit)

        def load_habits(conn: sqlite3.Connection) -> HabitTracker:
    """
    Load all habits from the database and return a populated
    HabitTracker.

    Args:
        conn: open database connection.

    Returns:
        A HabitTracker populated with all stored habits,
        their completions, and their notes.
    """
    cursor = conn.cursor()
    tracker = HabitTracker()

    cursor.execute("SELECT * FROM habits")
    habit_rows = cursor.fetchall()

    for row in habit_rows:
        # reconstruct the correct child class from stored frequency
        HabitClass = FREQUENCY_CLASS_MAP.get(row["frequency"])
        if HabitClass is None:
            continue   # unknown frequency — skip rather than crash

        # reconstruct the habit object
        habit = HabitClass(
            name     = row["name"],
            begn_date = date.fromisoformat(row["start_date"]),
            descp    = row["description"]
        )

        # restore created_date (bypasses __init__ which sets it to today)
        habit._created_date = date.fromisoformat(row["created_date"])

        # restore paused state
        habit._manually_paused = bool(row["is_paused"])

        # load completions
        cursor.execute(
            "SELECT completion_dt FROM completions WHERE habit_id = ? ORDER BY completion_dt",
            (row["id"],)
        )
        for completion_row in cursor.fetchall():
            habit._completions.append(
                datetime.fromisoformat(completion_row["completion_dt"])
            )

        # load notes
        cursor.execute(
            "SELECT note_date, note FROM notes WHERE habit_id = ?",
            (row["id"],)
        )
        for note_row in cursor.fetchall():
            habit.notes[date.fromisoformat(note_row["note_date"])] = note_row["note"]

        tracker.add_habit(habit)

    return tracker

def delete_habit(conn: sqlite3.Connection, name: str) -> bool:
    """
    Delete a habit and all its completions and notes from
    the database.

    Args:
        conn: open database connection.
        name: the name of the habit to delete.

    Returns:
        True if deleted, False if no habit with that name exists.
    """
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()

    if row is None:
        return False

    habit_id = row["id"]

    # delete completions and notes first (foreign key constraint)
    cursor.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM notes WHERE habit_id = ?", (habit_id,))
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))

    conn.commit()
    return True

def update_habit(conn: sqlite3.Connection, habit: Habit) -> None:
    """
    Update a habit's mutable fields in the database
    (description and is_paused).

    Completions and notes are fully resynced.

    Args:
        conn: open database connection.
        habit: the Habit object with updated values.
    """
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE habits
        SET description = ?,
            is_paused   = ?
        WHERE name = ?
    """, (
        habit.description,
        1 if habit._manually_paused else 0,
        habit.name
    ))

    conn.commit()

    # resync completions and notes
    save_habit(conn, habit)