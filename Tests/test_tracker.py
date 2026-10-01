"""
Unit tests for the HabitTracker class.
Tests cover: adding, removing, finding, and filtering habits.
"""

import pytest
from datetime import date, datetime, timedelta
from Models.habit import (Habit, DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit)
from Models.habit_management import HabitTracker


# --- Add Habits Tests ---

class TestAddHabit:
    """Tests for create_new_habit behaviour."""

    def test_add_valid_habit(self, empty_tracker, daily_habit):
        """A valid habit is added successfully."""
        result = empty_tracker.create_new_habit(daily_habit)
        assert result == True
        assert len(empty_tracker.habits) == 1

    def test_add_multiple_habits(self, empty_tracker):
        """Multiple habits can be added."""
        empty_tracker.create_new_habit(DailyHabit("Exercise"))
        empty_tracker.create_new_habit(WeeklyHabit("Reading"))
        empty_tracker.create_new_habit(BiWeeklyHabit("Meditation"))
        assert len(empty_tracker.habits) == 3

    def test_add_duplicate_name_raises_value_error(
        self, empty_tracker, daily_habit
    ):
        """Adding a habit with a duplicate name raises ValueError."""
        empty_tracker.create_new_habit(daily_habit)
        with pytest.raises(ValueError):
            empty_tracker.create_new_habit(DailyHabit("Test Exercise"))

    def test_duplicate_check_case_insensitive(self, empty_tracker):
        """Duplicate check is case insensitive."""
        empty_tracker.create_new_habit(DailyHabit("Exercise"))
        with pytest.raises(ValueError):
            empty_tracker.create_new_habit(DailyHabit("exercise"))

    def test_add_wrong_type_raises_type_error(self, empty_tracker):
        """Adding a non-Habit object raises TypeError."""
        with pytest.raises(TypeError):
            empty_tracker.create_new_habit("not a habit")

    def test_add_none_raises_type_error(self, empty_tracker):
        """Adding None raises TypeError."""
        with pytest.raises(TypeError):
            empty_tracker.create_new_habit(None)

    def test_all_frequency_types_accepted(self, empty_tracker):
        """All four frequency types can be added."""
        empty_tracker.create_new_habit(DailyHabit("Daily"))
        empty_tracker.create_new_habit(WeeklyHabit("Weekly"))
        empty_tracker.create_new_habit(BiWeeklyHabit("Biweekly"))
        empty_tracker.create_new_habit(TwiceWeeklyHabit("Twice"))
        assert len(empty_tracker.habits) == 4


# --- Remove Habit Tests ---

class TestRemoveHabit:
    """Tests for remove_habit behaviour."""

    def test_remove_existing_habit(self, populated_tracker):
        """Removing an existing habit returns True."""
        result = populated_tracker.remove_habit("Tracker Exercise")
        assert result == True

    def test_remove_reduces_count(self, populated_tracker):
        """Removing a habit reduces the habit count by 1."""
        initial_count = len(populated_tracker.habits)
        populated_tracker.remove_habit("Tracker Exercise")
        assert len(populated_tracker.habits) == initial_count - 1

    def test_remove_nonexistent_habit_returns_false(
        self, empty_tracker
    ):
        """Removing a habit that doesn't exist returns False."""
        result = empty_tracker.remove_habit("Nonexistent")
        assert result == False

    def test_remove_nonexistent_does_not_change_count(
        self, empty_tracker
    ):
        """Failed removal does not change the habit count."""
        initial_count = len(empty_tracker.habits)
        empty_tracker.remove_habit("Nonexistent")
        assert len(empty_tracker.habits) == initial_count

    def test_removed_habit_not_findable(self, empty_tracker):
        """Removed habit cannot be found by name."""
        empty_tracker.remove_habit("Tracker Exercise")
        result = empty_tracker.find_habit_by_name("Tracker Exercise")
        assert result is None

    def test_remove_wrong_type_raises_type_error(
        self, empty_tracker
    ):
        """Passing non-string to remove_habit raises TypeError."""
        with pytest.raises(TypeError):
            empty_tracker.remove_habit(123)


# --- Find Habit Tests ---

class TestFindHabit:
    """Tests for find_habit_by_name behaviour."""

    def test_find_existing_habit(self, populated_tracker):
        """Finding an existing habit returns the correct object."""
        habit = populated_tracker.find_habit_by_name("Tracker Exercise")
        assert habit is not None
        assert habit.name == "Tracker Exercise"

    def test_find_is_case_insensitive(self, populated_tracker):
        """Search is case insensitive."""
        habit = populated_tracker.find_habit_by_name("tracker exercise")
        assert habit is not None
        assert habit.name == "Tracker Exercise"

    def test_find_nonexistent_returns_none(self, empty_tracker):
        """Finding a nonexistent habit returns None."""
        result = empty_tracker.find_habit_by_name("Nonexistent")
        assert result is None

    def test_find_wrong_type_raises_type_error(self, empty_tracker):
        """Passing non-string raises TypeError."""
        with pytest.raises(TypeError):
            empty_tracker.find_habit_by_name(123)

    def test_find_returns_correct_type(self, populated_tracker):
        """Found habit is the correct child class."""
        habit = populated_tracker.find_habit_by_name("Tracker Exercise")
        assert isinstance(habit, DailyHabit)


# --- Filter Tests ---

class TestFilterHabits:
    """Tests for get_habits_from_status behaviour."""

    def test_get_active_habits(self, empty_tracker):
        """Returns only active habits."""
        active = empty_tracker.get_habits_from_status(True)
        assert all(h.is_active for h in active)

    def test_get_inactive_habits(self, populated_tracker):
        """Returns only inactive habits."""
        # pause one habit first
        habit = populated_tracker.find_habit_by_name("Tracker Exercise")
        habit.deactivate_habit()

        inactive = populated_tracker.get_habits_from_status(False)
        assert len(inactive) >= 1
        assert all(not h.is_active for h in inactive)

    def test_active_filter_excludes_paused(self, populated_tracker):
        """Paused habit does not appear in active list."""
        habit = populated_tracker.find_habit_by_name("Tracker Exercise")
        habit.deactivate_habit()

        active = populated_tracker.get_habits_from_status(True)
        names = [h.name for h in active]
        assert "Tracker Exercise" not in names

    def test_wrong_type_raises_type_error(self, empty_tracker):
        """Passing non-bool raises TypeError."""
        with pytest.raises(TypeError):
            empty_tracker.get_habits_from_status("active")

    def test_empty_tracker_returns_empty_list(self, empty_tracker):
        """Empty tracker returns empty list for any status."""
        assert empty_tracker.get_habits_from_status(True) == []
        assert empty_tracker.get_habits_from_status(False) == []


# --- Habits Properties Tests ---

class TestHabitsProperty:
    """Tests for the habits property."""

    def test_habits_returns_list(self, empty_tracker):
        """Habits property returns a list."""
        assert isinstance(empty_tracker.habits, list)

    def test_habits_returns_copy(self, populated_tracker):
        """
        Modifying the returned list does not affect the tracker's internal list.
        """
        habits_copy = populated_tracker.habits
        habits_copy.clear()
        assert len(populated_tracker.habits) == 4

    def test_empty_tracker_returns_empty_list(self, empty_tracker):
        """Empty tracker returns empty list."""
        assert empty_tracker.habits == []

    def test_habits_count_matches_added(self, empty_tracker):
        """Habits count matches number of added habits."""
        empty_tracker.create_new_habit(DailyHabit("One"))
        empty_tracker.create_new_habit(DailyHabit("Two"))
        assert len(empty_tracker.habits) == 2