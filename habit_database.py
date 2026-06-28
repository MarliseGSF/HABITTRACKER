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


# --- Helper Methods Definition ---

def _check_if_habit_exists(conn: sqlite3.Connection, name: str) -> int | None:
    """
    Helper function that checks if a habit already exists in the database. 

    Arguments: 
        conn: open database connection
        name: name of the habit to be checked 
    
    Returns: 
        The habits's id if the name matches a previous record, None if the name does not match any database. 
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()
    return row["id"] if row else None


def _sync_completions_date(conn: sqlite3.Connection, habit_id: int, habit: Habit) -> None:
    """
    Function that fully resync completions for a habit in the database.

    Deletes all existing completion rows for this habit and reinserts from the current in-memory state to ensure the database always matches habit._completions exactly.

    Called by save_habit after the habit row has been saved — never called directly.

    Arguments:
        conn: open database connection.
        habit_id: the database id of the parent habit row. Used as foreign key in the completions table.
        habit: the Habit object whose completions should be synced.
    """
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM completions WHERE habit_id = ?",
        (habit_id,)
    )

    cursor.executemany("""
        INSERT INTO completions (habit_id, completion_dt)
        VALUES (?, ?)
    """, [
        (habit_id, c.isoformat()) for c in habit.completions
    ])


def _sync_notes_data(conn: sqlite3.Connection, habit_id: int, habit: Habit) -> None:
    """
    Function that fully resync notes for a habit in the database.

    Deletes all existing note rows for this habit and reinserts from the current in-memory state to ensure the database always matches habit.notes exactly.

    Called by save_habit after the habit row has been saved — never called directly.

    Arguments:
        conn: open database connection.
        habit_id: the database id of the parent habit row. Used as foreign key in the notes table.
        habit: the Habit object whose notes should be synced.
    """
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM notes WHERE habit_id = ?",
        (habit_id,)
    )

    cursor.executemany("""
        INSERT INTO notes (habit_id, note_date, note)
        VALUES (?, ?, ?)
    """, [
        (habit_id, note_date.isoformat(), note_text)
        for note_date, note_text in habit.notes.items()
    ])


# --- Methods Definition ---

def save_habit(conn: sqlite3.Connection, habit: Habit) -> bool:
    """
    Function to save a single Habit object to the database.
    
    If the habit is new, inserts a new row.
    If the habit already exists (same name), updates its mutable fields (start_date, description and is_paused). 
    Syncs all notes and completions. 
    
    Note: the business rules are enforced in the Habit class and are not re-evaluated here. 

    Arguments:
        conn: open database connection.
        habit: the Habit object to save.

    Returns:
        True if successfully saved, False if a database error occurred.

    Raises:
        TypeError: if habit is not a Habit instance.
    """
    if not isinstance(habit, Habit):
        raise TypeError("The habit must be a Habit instance")

    try:
        cursor = conn.cursor()
        habit_id = _check_if_habit_exists(conn, habit.name)

        if habit_id is None:
            # new habit — INSERT all fields
            cursor.execute("""
                INSERT INTO habits
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

        else:
            cursor.execute("""
                UPDATE habits
                SET start_date  = ?,
                    description = ?,
                    is_paused   = ?
                WHERE id = ?
            """, (
                habit.start_date.isoformat(),
                habit.description,
                1 if habit._manually_paused else 0,
                habit_id
            ))

        _sync_completions_date(conn, habit_id, habit)
        _sync_notes_data(conn, habit_id, habit)

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error while saving '{habit.name}': {e}")
        return False
    

def load_habits(conn: sqlite3.Connection) -> HabitTracker:
    """
    Function that loads all the habits from the database to return a populated Habittracker.
    The function reconstructs the correct child class based on the frequency value, its completion, and notes.

    Argumentss:
        conn: open database connection.

    Returns:
        A HabitTracker populated with all stored habits, their completions, and their notes.
        Returns an empty HabitTracker if no habits exist or if a database error occurs.
    """
    tracker = HabitTracker()

    try:
        cursor = conn.cursor()

        # load all habit rows
        cursor.execute("SELECT * FROM habits")
        habit_rows = cursor.fetchall()

        for row in habit_rows:

            # ── Step 1: reconstruct the correct child class ──────────────
            HabitClass = FREQUENCY_CLASS_MAP.get(row["frequency"])

            if HabitClass is None:
                print(f"Unknown frequency '{row['frequency']}' for habit "
                      f"'{row['name']}' — skipping.")
                continue

            # ── Step 2: reconstruct the habit object ─────────────────────
            habit = HabitClass(
                name      = row["name"],
                begn_date = date.fromisoformat(row["start_date"]),
                descp     = row["description"]
            )

            # ── Step 3: restore immutable fields ───────
            # __init__ sets _created_date to date.today() — override with the stored value to preserve the original date
            habit._created_date = date.fromisoformat(row["created_date"])

            # ── Step 4: restore paused state ─────────────────────────────
            habit._manually_paused = bool(row["is_paused"])

            # ── Step 5: restore completions ───────────────────────────────
            cursor.execute("""
                SELECT completion_dt
                FROM completions
                WHERE habit_id = ?
                ORDER BY completion_dt ASC
            """, (row["id"],))

            for completion_row in cursor.fetchall():
                habit._completions.append(
                    datetime.fromisoformat(completion_row["completion_dt"])
                )

            # ── Step 6: restore notes ─────────────────────────────────────
            cursor.execute("""
                SELECT note_date, note
                FROM notes
                WHERE habit_id = ?
            """, (row["id"],))

            for note_row in cursor.fetchall():
                habit.notes[
                    date.fromisoformat(note_row["note_date"])
                ] = note_row["note"]

            # ── Step 7: add to tracker ────────────────────────────────────
            try:
                tracker.create_new_habit(habit)
            except ValueError as e:
                print(f"Skipping duplicate habit '{habit.name}': {e}")
                continue

    except sqlite3.Error as e:
        print(f"Database error while loading habits: {e}")

    return tracker


def save_all_habits(conn: sqlite3.Connection, tracker: HabitTracker) -> bool:
    """
    Functions that saves all habits in the HabitTracker to the database.
    The function calls the save_habit function for each habit individually.

    Argumentss:
        conn: open database connection.
        tracker: the HabitTracker whose habits should be saved.

    Returns:
        True if all habits saved successfully.
        False if any habit failed to save.

    Raises:
        TypeError: if tracker is not a HabitTracker instance.
    """
    if not isinstance(tracker, HabitTracker):
        raise TypeError("The tracker must be a HabitTracker instance")

    if not tracker.habits:
        return True   # nothing to save — not an error

    results = list(map(
        lambda habit: save_habit(conn, habit),
        tracker.habits
    ))

    return all(results)


def delete_habit(conn: sqlite3.Connection, name: str) -> bool:
    """
    Function that deletes a habit and all its completions and notes from the database permanently.

    Completions and notes are deleted first to satisfy the foreign key constraint before removing the habit row.

    Argumentss:
        conn: open database connection.
        name: the name of the habit to be deleted.

    Returns:
        True if successfully deleted.
        False if no habit with that name exists or a database error occurs.

    Raises:
        TypeError: if name is not a string.
    """
    if not isinstance(name, str):
        raise TypeError("The name of the habit must be a string")

    try:
        cursor = conn.cursor()

        habit_id = _check_if_habit_exists(conn, name)

        if habit_id is None:
            return False   # habit doesn't exist — nothing to delete

        cursor.execute(
            "DELETE FROM completions WHERE habit_id = ?",
            (habit_id,)
        )
        cursor.execute(
            "DELETE FROM notes WHERE habit_id = ?",
            (habit_id,)
        )

        cursor.execute(
            "DELETE FROM habits WHERE id = ?",
            (habit_id,)
        )

        conn.commit()
        return True

    except sqlite3.Error as e:
        print(f"Database error while deleting '{name}': {e}")
        return False