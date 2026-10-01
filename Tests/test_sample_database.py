"""
Unit tests for the sample data module.
Verifies that create_sample_habits produces consistent, valid data that correctly demonstrates all habit types and completion patterns.
"""

import pytest
from datetime import date, timedelta

from Models.habit import (DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency)
from Storage.sample_data import create_sample_habits


# --- Fixture ---

@pytest.fixture
def sample_habits():
    """
    Create sample habits once for all tests in this module.
    Returns the list from create_sample_habits().
    """
    return create_sample_habits()


# --- Structure Tests ---

class TestSampleDataStructure:
    """Tests for basic structure of sample data."""

    def test_returns_six_habits(self, sample_habits):
        """create_sample_habits returns exactly 6 habits."""
        assert len(sample_habits) == 6

    def test_returns_list(self, sample_habits):
        """create_sample_habits returns a list."""
        assert isinstance(sample_habits, list)

    def test_all_items_are_habits(self, sample_habits):
        """All items in the list are Habit instances."""
        from Models.habit import Habit
        assert all(isinstance(h, Habit) for h in sample_habits)

    def test_all_names_unique(self, sample_habits):
        """All habit names are unique."""
        names = [h.name for h in sample_habits]
        assert len(names) == len(set(names))

    def test_all_names_start_with_sample_prefix(self, sample_habits):
        """All habit names start with '[Sample]' prefix."""
        assert all(h.name.startswith("[Sample]") for h in sample_habits)


# --- Frequency Tests ---

class TestSampleDataFrequencies:
    """Tests that correct frequency types are represented."""

    def test_has_three_daily_habits(self, sample_habits):
        """Three daily habits exist in sample data."""
        daily = [
            h for h in sample_habits
            if h.frequency == Frequency.DAILY
        ]
        assert len(daily) == 3

    def test_has_one_weekly_habit(self, sample_habits):
        """One weekly habit exists in sample data."""
        weekly = [
            h for h in sample_habits
            if h.frequency == Frequency.WEEKLY
        ]
        assert len(weekly) == 1

    def test_has_one_biweekly_habit(self, sample_habits):
        """One biweekly habit exists in sample data."""
        biweekly = [
            h for h in sample_habits
            if h.frequency == Frequency.BIWEEKLY
        ]
        assert len(biweekly) == 1

    def test_has_one_twice_weekly_habit(self, sample_habits):
        """One twice-weekly habit exists in sample data."""
        twice = [
            h for h in sample_habits
            if h.frequency == Frequency.TWICEWEEKLY
        ]
        assert len(twice) == 1

    def test_correct_child_classes_used(self, sample_habits):
        """Each frequency uses the correct child class."""
        for habit in sample_habits:
            if habit.frequency == Frequency.DAILY:
                assert isinstance(habit, DailyHabit)
            elif habit.frequency == Frequency.WEEKLY:
                assert isinstance(habit, WeeklyHabit)
            elif habit.frequency == Frequency.BIWEEKLY:
                assert isinstance(habit, BiWeeklyHabit)
            elif habit.frequency == Frequency.TWICEWEEKLY:
                assert isinstance(habit, TwiceWeeklyHabit)


# --- Start Date Tests ---

class TestSampleDataStartDates:
    """Tests that habits start approximately 4 weeks ago."""

    def test_all_habits_have_started(self, sample_habits):
        """All sample habits have already started."""
        assert all(h.habit_has_started for h in sample_habits)

    def test_start_dates_approximately_four_weeks_ago(
        self, sample_habits
    ):
        """
        All habits start within a day of 4 weeks ago.
        Allows one day tolerance for test timing.
        """
        four_weeks_ago = date.today() - timedelta(weeks=4)
        for habit in sample_habits:
            diff = abs((habit.start_date - four_weeks_ago).days)
            assert diff <= 1, (
                f"{habit.name} start_date {habit.start_date} "
                f"is not close to 4 weeks ago ({four_weeks_ago})"
            )


# --- Data Completion Tests ---

class TestSampleDataCompletions:
    """Tests that each habit has the expected completion pattern."""

    def _get_habit(self, sample_habits, name_fragment):
        """Helper to find a habit by name fragment."""
        matches = [
            h for h in sample_habits
            if name_fragment in h.name
        ]
        assert len(matches) == 1, (
            f"Expected 1 habit matching '{name_fragment}', "
            f"got {len(matches)}"
        )
        return matches[0]

    def test_drink_water_has_perfect_completions(self, sample_habits):
        """
        Drink Water has 28 completions —
        one for every day of the 4-week period.
        """
        water = self._get_habit(sample_habits, "Drink Water")
        assert len(water.completions) == 28

    def test_exercise_has_missed_days(self, sample_habits):
        """
        Exercise has fewer than 28 completions —
        some days were missed.
        """
        exercise = self._get_habit(sample_habits, "Exercise")
        assert len(exercise.completions) < 28
        assert len(exercise.completions) > 0

    def test_gym_has_some_completions(self, sample_habits):
        """Gym has some completions but not all weeks satisfied."""
        gym = self._get_habit(sample_habits, "Gym")
        assert len(gym.completions) > 0

    def test_finances_has_completions(self, sample_habits):
        """Review Finances has some weekly completions."""
        finances = self._get_habit(sample_habits, "Finances")
        assert len(finances.completions) > 0
        assert len(finances.completions) < 5

    def test_meditation_has_one_completion(self, sample_habits):
        """Meditation has exactly one completion."""
        meditation = self._get_habit(sample_habits, "Meditation")
        assert len(meditation.completions) == 1

    def test_journaling_has_few_completions(self, sample_habits):
        """Journaling has very few completions — struggling habit."""
        journaling = self._get_habit(sample_habits, "Journaling")
        assert len(journaling.completions) <= 3


# --- Status Tests ---

class TestSampleDataStatus:
    """Tests for expected active/paused states."""

    def _get_habit(self, sample_habits, name_fragment):
        """Helper to find a habit by name fragment."""
        matches = [
            h for h in sample_habits
            if name_fragment in h.name
        ]
        assert len(matches) == 1
        return matches[0]

    def test_meditation_is_paused(self, sample_habits):
        """Meditation is manually paused."""
        meditation = self._get_habit(sample_habits, "Meditation")
        assert meditation._manually_paused == True

    def test_drink_water_is_active(self, sample_habits):
        """Drink Water with perfect completions is active."""
        water = self._get_habit(sample_habits, "Drink Water")
        assert water.is_active == True

    def test_journaling_is_auto_paused(self, sample_habits):
        """
        Journaling has no recent completions —
        should be auto-paused by abandonment threshold.
        """
        journaling = self._get_habit(sample_habits, "Journaling")
        assert journaling.is_active == False


# --- Streak Tests ---

class TestSampleDataStreaks:
    """Tests for expected streak values in sample data."""

    def _get_habit(self, sample_habits, name_fragment):
        """Helper to find a habit by name fragment."""
        matches = [
            h for h in sample_habits
            if name_fragment in h.name
        ]
        assert len(matches) == 1
        return matches[0]

    def test_drink_water_has_high_streak(self, sample_habits):
        """Drink Water has a streak greater than 20."""
        water = self._get_habit(sample_habits, "Drink Water")
        assert water.get_current_habit_streak() > 20

    def test_journaling_has_zero_streak(self, sample_habits):
        """Journaling has a current streak of 0."""
        journaling = self._get_habit(sample_habits, "Journaling")
        assert journaling.get_current_habit_streak() == 0

    def test_exercise_has_positive_streak(self, sample_habits):
        """Exercise has a current streak greater than 0."""
        exercise = self._get_habit(sample_habits, "Exercise")
        assert exercise.get_current_habit_streak() > 0