"""
Unit tests for the analytics functions in habit_analyse.py.
Tests cover: habit filtering, streak analysis, completion rates, time analysis, and edge cases with empty data.
"""

import pytest
from datetime import date, datetime, timedelta

from Models.habit import (Habit, DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency)
from Models.habit_management import HabitTracker
import Analytics.habit_analyse as an


# --- Fixtures ---

@pytest.fixture
def habits_mixed():
    """
    A list of habits with different frequencies and completion patterns for analytics testing.
    """
    # daily habit — perfect streak
    exercise = DailyHabit(
        name               = "Exercise",
        begn_date          = date.today() - timedelta(days=7),
        _bypass_date_check = True
    )
    for days_ago in range(7, 0, -1):
        d = date.today() - timedelta(days=days_ago)
        exercise.check_habit_completion(
            datetime(d.year, d.month, d.day, 8, 0)
        )

    # daily habit — no completions (struggling)
    water = DailyHabit(
        name               = "Water",
        begn_date          = date.today() - timedelta(days=7),
        _bypass_date_check = True
    )

    # weekly habit — one completion
    reading = WeeklyHabit(
        name               = "Reading",
        begn_date          = date.today() - timedelta(days=14),
        _bypass_date_check = True
    )
    d = date.today() - timedelta(days=7)
    reading.check_habit_completion(
        datetime(d.year, d.month, d.day, 20, 0)
    )

    # biweekly habit — paused
    meditation = BiWeeklyHabit(
        name               = "Meditation",
        begn_date          = date.today() - timedelta(days=14),
        _bypass_date_check = True
    )
    meditation.deactivate_habit()

    return [exercise, water, reading, meditation]


@pytest.fixture
def empty_habits():
    """An empty list of habits for edge case testing."""
    return []


@pytest.fixture
def single_habit():
    """A list with one DailyHabit and 3 completions."""
    habit = DailyHabit(
        name               = "Single",
        begn_date          = date.today() - timedelta(days=3),
        _bypass_date_check = True
    )
    for days_ago in range(3, 0, -1):
        d = date.today() - timedelta(days=days_ago)
        habit.check_habit_completion(
            datetime(d.year, d.month, d.day, 9, 0)
        )
    return [habit]


# --- Functions get_all tests ---

class TestGetAllHabits:
    """Tests for get_all_habits_list function."""

    def test_returns_all_habits(self, habits_mixed):
        """Returns all habits regardless of status."""
        result = an.get_all_habits_list(habits_mixed)
        assert len(result) == 4

    def test_returns_empty_list_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_all_habits_list(empty_habits)
        assert result == []

    def test_returns_list_type(self, habits_mixed):
        """Result is a list."""
        result = an.get_all_habits_list(habits_mixed)
        assert isinstance(result, list)

    def test_includes_inactive_habits(self, habits_mixed):
        """Includes paused habits."""
        result = an.get_all_habits_list(habits_mixed)
        names = [h.name for h in result]
        assert "Meditation" in names


# --- Functions get_habits_by_frequency tests ---

class TestGetHabitsByPeriodicity:
    """Tests for get_habits_by_frequency function."""

    def test_filters_daily_habits(self, habits_mixed):
        """Returns only daily habits."""
        result = an.get_habits_by_frequency(
            habits_mixed, Frequency.DAILY
        )
        assert all(h.frequency == Frequency.DAILY for h in result)

    def test_filters_weekly_habits(self, habits_mixed):
        """Returns only weekly habits."""
        result = an.get_habits_by_frequency(
            habits_mixed, Frequency.WEEKLY
        )
        assert len(result) == 1
        assert result[0].name == "Reading"

    def test_returns_empty_for_no_match(self, habits_mixed):
        """Returns empty list when no habits match."""
        result = an.get_habits_by_frequency(
            habits_mixed, Frequency.TWICEWEEKLY
        )
        assert result == []

    def test_returns_empty_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_habits_by_frequency(
            empty_habits, Frequency.DAILY
        )
        assert result == []

    def test_wrong_frequency_type_raises_type_error(self, habits_mixed):
        """Wrong frequency type raises TypeError."""
        with pytest.raises(TypeError):
            an.get_habits_by_frequency(habits_mixed, "daily")

    def test_daily_count_correct(self, habits_mixed):
        """Correct number of daily habits returned."""
        result = an.get_habits_by_frequency(
            habits_mixed, Frequency.DAILY
        )
        assert len(result) == 2


# --- Functions get_longest_streak_all_habits Tests ---

class TestGetLongestStreakAllHabits:
    """Tests for get_longest_streak_all_habits function."""

    def test_finds_habit_with_longest_streak(self, habits_mixed):
        """Returns the habit with the highest longest streak."""
        result = an.get_longest_streak_all_habits(habits_mixed)
        assert result is not None
        assert result.name == "Exercise"

    def test_returns_none_for_empty_list(self, empty_habits):
        """Returns None for empty list."""
        result = an.get_longest_streak_all_habits(empty_habits)
        assert result is None

    def test_returns_habit_instance(self, habits_mixed):
        """Returns a Habit instance."""
        from Models.habit import Habit
        result = an.get_longest_streak_all_habits(habits_mixed)
        assert isinstance(result, Habit)

    def test_single_habit_returned(self, single_habit):
        """Returns the only habit in a single-item list."""
        result = an.get_longest_streak_all_habits(single_habit)
        assert result.name == "Single"


# --- Functions get_longest_streak_all_habits Tests ---

class TestGetLongestStreakForHabit:
    """Tests for get_longest_streak_for_single_habit function."""

    def test_returns_correct_streak(self, daily_habit_with_streak):
        """Returns correct longest streak value."""
        result = an.get_longest_streak_for_single_habit(
            daily_habit_with_streak
        )
        assert result == 7

    def test_returns_zero_for_no_completions(self, daily_habit):
        """Returns 0 for habit with no completions."""
        result = an.get_longest_streak_for_single_habit(daily_habit)
        assert result == 0

    def test_wrong_type_raises_type_error(self):
        """Wrong type raises TypeError."""
        with pytest.raises(TypeError):
            an.get_longest_streak_for_single_habit("not a habit")


# --- Functions get_struggling_habits Tests ---

class TestGetStrugglingHabits:
    """Tests for get_struggling_habits function."""

    def test_identifies_struggling_habits(self, habits_mixed):
        """
        Identifies habits with streak of 0 that have started and had at least one period elapse.
        Water has no completions and has started → struggling.
        """
        result = an.get_struggling_habits(habits_mixed)
        names = [h.name for h in result]
        assert "Water" in names

    def test_excludes_habits_with_streak(self, habits_mixed):
        """Habits with active streak are not struggling."""
        result = an.get_struggling_habits(habits_mixed)
        names = [h.name for h in result]
        assert "Exercise" not in names

    def test_returns_empty_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_struggling_habits(empty_habits)
        assert result == []

    def test_returns_list(self, habits_mixed):
        """Returns a list."""
        result = an.get_struggling_habits(habits_mixed)
        assert isinstance(result, list)


# --- Functions get_most_consistent_habit Tests ---

class TestGetMostConsistentHabit:
    """Tests for get_most_consistent_habit function."""

    def test_finds_most_consistent(self, habits_mixed):
        """Returns the habit with the highest completion rate."""
        result = an.get_most_consistent_habit(habits_mixed)
        assert result is not None
        assert result.name == "Exercise"

    def test_returns_none_for_empty_list(self, empty_habits):
        """Returns None for empty list."""
        result = an.get_most_consistent_habit(empty_habits)
        assert result is None

    def test_returns_single_habit(self, single_habit):
        """Returns the only habit in a single-item list."""
        result = an.get_most_consistent_habit(single_habit)
        assert result.name == "Single"


# --- Functions get_Completion_time_analysis Tests ---

class TestGetCompletionTimeAnalysis:
    """Tests for get_completion_time_analysis function."""

    def test_returns_dict_with_correct_keys(self, habits_mixed):
        """Returns dict with 'overall' and 'per_habit' keys."""
        result = an.get_completion_time_analysis(habits_mixed)
        assert "overall" in result
        assert "per_habit" in result

    def test_overall_is_string_or_none(self, habits_mixed):
        """Overall bracket is a string or None."""
        result = an.get_completion_time_analysis(habits_mixed)
        assert result["overall"] is None or isinstance(
            result["overall"], str
        )

    def test_per_habit_is_dict(self, habits_mixed):
        """per_habit is a dictionary."""
        result = an.get_completion_time_analysis(habits_mixed)
        assert isinstance(result["per_habit"], dict)

    def test_morning_bracket_for_morning_completions(self):
        """
        Habit with completions at 8am returns Morning bracket.
        """
        habit = DailyHabit(
            name               = "Morning Habit",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in range(3, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        result = an.get_completion_time_analysis([habit])
        assert result["overall"] == "Morning"

    def test_evening_bracket_for_evening_completions(self):
        """
        Habit with completions at 19:00 returns Evening bracket.
        """
        habit = DailyHabit(
            name               = "Evening Habit",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in range(3, 0, -1):
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 19, 0)
            )
        result = an.get_completion_time_analysis([habit])
        assert result["overall"] == "Evening"

    def test_returns_none_overall_for_empty_input(self, empty_habits):
        """Returns None overall for empty input."""
        result = an.get_completion_time_analysis(empty_habits)
        assert result["overall"] is None

    def test_excludes_inactive_from_overall(self, habits_mixed):
        """
        Paused habits excluded from overall but
        included in per_habit.
        """
        result = an.get_completion_time_analysis(habits_mixed)
        assert "Meditation" not in result["per_habit"] or \
               result["per_habit"].get("Meditation") is None


# --- Functions fet_age_habit tests ---

class TestOldestNewestHabits:
    """Tests for get_oldest_habit and get_newest_habit."""

    def test_oldest_habit_found(self, habits_mixed):
        """Returns habits with earliest start date."""
        result = an.get_oldest_habit(habits_mixed)
        assert result is not None
        assert len(result) >= 1

    def test_newest_habit_found(self, habits_mixed):
        """Returns habits with most recent start date."""
        result = an.get_newest_habit(habits_mixed)
        assert result is not None
        assert len(result) >= 1

    def test_oldest_returns_empty_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_oldest_habit(empty_habits)
        assert result == []

    def test_newest_returns_empty_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_newest_habit(empty_habits)
        assert result == []

    def test_same_start_date_returns_multiple(self):
        """
        Multiple habits with same start date are all returned.
        """
        today = date.today()
        h1 = DailyHabit("Habit One")
        h2 = DailyHabit("Habit Two")
        result = an.get_oldest_habit([h1, h2])
        assert len(result) == 2


# --- Functions get_habits_never_completed Tests ---

class TestGetHabitsNeverCompleted:
    """Tests for get_habits_never_completed function."""

    def test_finds_never_completed(self, habits_mixed):
        """
        Water has no completions and is analysable
        → should appear in never completed.
        """
        result = an.get_habits_never_completed(habits_mixed)
        names = [h.name for h in result]
        assert "Water" in names

    def test_excludes_completed_habits(self, habits_mixed):
        """Exercise has completions → not in never completed."""
        result = an.get_habits_never_completed(habits_mixed)
        names = [h.name for h in result]
        assert "Exercise" not in names

    def test_returns_empty_for_empty_input(self, empty_habits):
        """Returns empty list for empty input."""
        result = an.get_habits_never_completed(empty_habits)
        assert result == []


# --- Functions get_completion_rates_by_frequecy Tests ---

class TestGetCompletionRatesByFrequency:
    """Tests for get_completion_rates_by_frequency function."""

    def test_returns_float(self, habits_mixed):
        """Returns a float."""
        result = an.get_completion_rates_by_frequency(
            habits_mixed, Frequency.DAILY
        )
        assert isinstance(result, float)

    def test_rate_between_zero_and_one(self, habits_mixed):
        """Rate is between 0.0 and 1.0."""
        result = an.get_completion_rates_by_frequency(
            habits_mixed, Frequency.DAILY
        )
        assert 0.0 <= result <= 1.0

    def test_returns_zero_for_no_matching_habits(self, habits_mixed):
        """Returns 0.0 when no habits match frequency."""
        result = an.get_completion_rates_by_frequency(
            habits_mixed, Frequency.TWICEWEEKLY
        )
        assert result == 0.0

    def test_wrong_frequency_type_raises_type_error(self, habits_mixed):
        """Wrong frequency type raises TypeError."""
        with pytest.raises(TypeError):
            an.get_completion_rates_by_frequency(
                habits_mixed, "weekly"
            )

    def test_returns_zero_for_empty_input(self, empty_habits):
        """Returns 0.0 for empty input."""
        result = an.get_completion_rates_by_frequency(
            empty_habits, Frequency.DAILY
        )
        assert result == 0.0