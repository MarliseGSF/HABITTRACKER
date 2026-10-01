"""
Unit tests for the database persistence layer.
Tests cover: initialisation, saving, loading, deleting, and full round-trip data integrity.
"""

import pytest
import os
from datetime import date, datetime, timedelta

from Models.habit import (DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency)
from Models.habit_management import HabitTracker
from Storage.habit_database import (init_db, save_habit, load_habits, save_all_habits, delete_habit)


# --- Initialisation Tests Definition ---

class TestInitDb:
    """Tests for database initialisation."""

    def test_creates_database_file(self, db_conn, tmp_path):
        """Database file is created on init."""
        assert os.path.exists("database/test_habits.db")

    def test_creates_habits_table(self, db_conn):
        """Habits table is created."""
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='habits'"
        )
        assert cursor.fetchone() is not None

    def test_creates_completions_table(self, db_conn):
        """Completions table is created."""
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='completions'"
        )
        assert cursor.fetchone() is not None

    def test_creates_notes_table(self, db_conn):
        """Notes table is created."""
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='notes'"
        )
        assert cursor.fetchone() is not None

    def test_returns_connection(self, db_conn):
        """init_db returns a connection object."""
        import sqlite3
        assert isinstance(db_conn, sqlite3.Connection)


# --- Sabe Habit Tests ---

class TestSaveHabit:
    """Tests for save_habit function."""

    def test_save_new_habit_returns_true(self, db_conn, daily_habit):
        """Saving a new habit returns True."""
        result = save_habit(db_conn, daily_habit)
        assert result == True

    def test_save_new_habit_inserts_row(self, db_conn, daily_habit):
        """Saving a new habit inserts a row in habits table."""
        save_habit(db_conn, daily_habit)
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name FROM habits WHERE name = ?",
            (daily_habit.name,)
        )
        assert cursor.fetchone() is not None

    def test_save_habit_stores_correct_frequency(
        self, db_conn, weekly_habit
    ):
        """Frequency is stored correctly."""
        save_habit(db_conn, weekly_habit)
        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT frequency FROM habits WHERE name = ?",
            (weekly_habit.name,)
        )
        row = cursor.fetchone()
        assert row["frequency"] == Frequency.WEEKLY.value

    def test_save_habit_stores_completions(self, db_conn):
        """Completions are stored in completions table."""
        habit = DailyHabit(
            name               = "Test Completions",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in range(3, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        save_habit(db_conn, habit)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM completions "
            "JOIN habits ON completions.habit_id = habits.id "
            "WHERE habits.name = ?",
            (habit.name,)
        )
        row = cursor.fetchone()
        assert row["count"] == 3

    def test_save_habit_stores_notes(self, db_conn):
        """Notes are stored in notes table."""
        habit = DailyHabit(name="Test Notes")
        habit.notes[date.today()] = "Test note."
        save_habit(db_conn, habit)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM notes "
            "JOIN habits ON notes.habit_id = habits.id "
            "WHERE habits.name = ?",
            (habit.name,)
        )
        row = cursor.fetchone()
        assert row["count"] == 1

    def test_save_existing_habit_updates_row(self, db_conn, daily_habit):
        """Saving an existing habit updates rather than duplicates."""
        save_habit(db_conn, daily_habit)
        daily_habit.description = "Updated description."
        save_habit(db_conn, daily_habit)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM habits WHERE name = ?",
            (daily_habit.name,)
        )
        row = cursor.fetchone()
        assert row["count"] == 1

    def test_save_wrong_type_raises_type_error(self, db_conn):
        """Passing non-Habit raises TypeError."""
        with pytest.raises(TypeError):
            save_habit(db_conn, "not a habit")

    def test_save_paused_habit_stores_paused_state(self, db_conn):
        """Paused state is stored correctly."""
        habit = DailyHabit(name="Test Paused")
        habit.deactivate_habit()
        save_habit(db_conn, habit)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT is_paused FROM habits WHERE name = ?",
            (habit.name,)
        )
        row = cursor.fetchone()
        assert row["is_paused"] == 1


# --- Load Habits Tests ---


class TestLoadHabits:
    """Tests for load_habits function."""

    def test_load_returns_tracker(self, db_conn):
        """load_habits returns a HabitTracker."""
        tracker = load_habits(db_conn)
        assert isinstance(tracker, HabitTracker)

    def test_load_empty_database_returns_empty_tracker(self, db_conn):
        """Empty database returns empty tracker."""
        tracker = load_habits(db_conn)
        assert len(tracker.habits) == 0

    def test_load_reconstructs_correct_child_class(self, db_conn):
        """Saved DailyHabit is loaded as DailyHabit."""
        habit = DailyHabit(name="Test Daily")
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Daily")
        assert isinstance(loaded, DailyHabit)

    def test_load_reconstructs_all_frequency_types(self, db_conn):
        """All four frequency types are reconstructed correctly."""
        save_habit(db_conn, DailyHabit("Daily"))
        save_habit(db_conn, WeeklyHabit("Weekly"))
        save_habit(db_conn, BiWeeklyHabit("Biweekly"))
        save_habit(db_conn, TwiceWeeklyHabit("Twice"))

        tracker = load_habits(db_conn)
        assert len(tracker.habits) == 4
        assert isinstance(
            tracker.find_habit_by_name("Daily"), DailyHabit
        )
        assert isinstance(
            tracker.find_habit_by_name("Weekly"), WeeklyHabit
        )
        assert isinstance(
            tracker.find_habit_by_name("Biweekly"), BiWeeklyHabit
        )
        assert isinstance(
            tracker.find_habit_by_name("Twice"), TwiceWeeklyHabit
        )

    def test_load_restores_completions(self, db_conn):
        """Completions are restored correctly after load."""
        habit = DailyHabit(
            name               = "Test Completions",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in range(3, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Completions")
        assert len(loaded.completions) == 3

    def test_load_restores_notes(self, db_conn):
        """Notes are restored correctly after load."""
        habit = DailyHabit(name="Test Notes")
        habit.notes[date.today()] = "Test note content."
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Notes")
        assert date.today() in loaded.notes
        assert loaded.notes[date.today()] == "Test note content."

    def test_load_restores_paused_state(self, db_conn):
        """Manually paused state is restored correctly."""
        habit = DailyHabit(name="Test Paused")
        habit.deactivate_habit()
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Paused")
        assert loaded._manually_paused == True

    def test_load_restores_description(self, db_conn):
        """Description is restored correctly."""
        habit = DailyHabit(
            name  = "Test Desc",
            descp = "My description."
        )
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Desc")
        assert loaded.description == "My description."

    def test_load_restores_start_date(self, db_conn):
        """Start date is restored correctly."""
        tomorrow = date.today() + timedelta(days=1)
        habit = DailyHabit(
            name      = "Test Start",
            begn_date = tomorrow
        )
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Test Start")
        assert loaded.start_date == tomorrow


# --- Delete Habit Tests ---

class TestDeleteHabit:
    """Tests for delete_habit function."""

    def test_delete_existing_habit_returns_true(
        self, db_conn, daily_habit
    ):
        """Deleting an existing habit returns True."""
        save_habit(db_conn, daily_habit)
        result = delete_habit(db_conn, daily_habit.name)
        assert result == True

    def test_delete_removes_habit_row(self, db_conn, daily_habit):
        """Deleted habit no longer exists in habits table."""
        save_habit(db_conn, daily_habit)
        delete_habit(db_conn, daily_habit.name)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT name FROM habits WHERE name = ?",
            (daily_habit.name,)
        )
        assert cursor.fetchone() is None

    def test_delete_removes_completions(self, db_conn):
        """Deleting a habit also removes its completions."""
        habit = DailyHabit(
            name               = "Test Delete",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in range(3, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        save_habit(db_conn, habit)
        delete_habit(db_conn, habit.name)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM completions "
            "JOIN habits ON completions.habit_id = habits.id "
            "WHERE habits.name = ?",
            (habit.name,)
        )
        # habit is gone so join returns 0
        assert cursor.fetchone()["count"] == 0

    def test_delete_removes_notes(self, db_conn):
        """Deleting a habit also removes its notes."""
        habit = DailyHabit(name="Test Delete Notes")
        habit.notes[date.today()] = "Test note."
        save_habit(db_conn, habit)
        delete_habit(db_conn, habit.name)

        cursor = db_conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) as count FROM notes "
            "JOIN habits ON notes.habit_id = habits.id "
            "WHERE habits.name = ?",
            (habit.name,)
        )
        assert cursor.fetchone()["count"] == 0

    def test_delete_nonexistent_returns_false(self, db_conn):
        """Deleting a nonexistent habit returns False."""
        result = delete_habit(db_conn, "Nonexistent")
        assert result == False

    def test_delete_wrong_type_raises_type_error(self, db_conn):
        """Passing non-string raises TypeError."""
        with pytest.raises(TypeError):
            delete_habit(db_conn, 123)


# --- Save All Habits Tests ---

class TestSaveAllHabits:
    """Tests for save_all_habits function."""

    def test_save_all_returns_true(self, db_conn, populated_tracker):
        """save_all_habits returns True on success."""
        result = save_all_habits(db_conn, populated_tracker)
        assert result == True

    def test_save_all_stores_all_habits(
        self, db_conn, populated_tracker
    ):
        """All habits in tracker are saved."""
        save_all_habits(db_conn, populated_tracker)

        cursor = db_conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM habits")
        row = cursor.fetchone()
        assert row["count"] == len(populated_tracker.habits)

    def test_save_all_wrong_type_raises_type_error(self, db_conn):
        """Passing non-HabitTracker raises TypeError."""
        with pytest.raises(TypeError):
            save_all_habits(db_conn, "not a tracker")


# --- Data Integrity Tests ---

class TestRoundTrip:
    """
    Tests that verify data integrity through a full save → load cycle.
    """

    def test_round_trip_preserves_habit_name(self, db_conn):
        """Name survives save → load cycle."""
        save_habit(db_conn, DailyHabit("Round Trip Test"))
        tracker = load_habits(db_conn)
        assert tracker.find_habit_by_name("Round Trip Test") is not None

    def test_round_trip_preserves_completions(self, db_conn):
        """Completions survive save → load cycle."""
        habit = DailyHabit(
            name               = "Round Trip",
            begn_date          = date.today() - timedelta(days=5),
            _bypass_date_check = True
        )
        for days_ago in range(5, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Round Trip")
        assert len(loaded.completions) == 5

    def test_round_trip_preserves_streak(self, db_conn):
        """Streak calculation is correct after save → load cycle."""
        habit = DailyHabit(
            name               = "Streak Round Trip",
            begn_date          = date.today() - timedelta(days=5),
            _bypass_date_check = True
        )
        for days_ago in range(5, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        original_streak = habit.get_current_habit_streak()
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Streak Round Trip")
        assert loaded.get_current_habit_streak() == original_streak

    def test_round_trip_preserves_notes(self, db_conn):
        """Notes survive save → load cycle."""
        habit = DailyHabit(name="Notes Round Trip")
        habit.notes[date.today()] = "Round trip note."
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Notes Round Trip")
        assert loaded.notes[date.today()] == "Round trip note."

    def test_round_trip_preserves_paused_state(self, db_conn):
        """Paused state survives save → load cycle."""
        habit = DailyHabit(name="Paused Round Trip")
        habit.deactivate_habit()
        save_habit(db_conn, habit)

        tracker = load_habits(db_conn)
        loaded = tracker.find_habit_by_name("Paused Round Trip")
        assert loaded._manually_paused == True

    def test_round_trip_multiple_habits(self, db_conn):
        """Multiple habits all survive save → load cycle."""
        tracker = HabitTracker()
        tracker.create_new_habit(DailyHabit("One"))
        tracker.create_new_habit(WeeklyHabit("Two"))
        tracker.create_new_habit(BiWeeklyHabit("Three"))
        save_all_habits(db_conn, tracker)

        loaded_tracker = load_habits(db_conn)
        assert len(loaded_tracker.habits) == 3