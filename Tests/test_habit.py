"""
Unit tests for the Habit class and its child classes.
Tests cover: creation, validation, immutability, completions, streaks, notes, late completions, and status behaviour.
"""

import pytest
from datetime import date, datetime, timedelta
from Models.habit import (Habit, DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency)


# --- Creation Tests ---

class TestHabitCreation:
    """Tests for creating valid and invalid habits."""

    def test_daily_habit_created_correctly(self):
        """A valid DailyHabit is created with correct attributes."""
        habit = DailyHabit("Exercise", descp="Test description.")
        assert habit.name == "Exercise"
        assert habit.frequency == Frequency.DAILY
        assert habit.description == "Test description."
        assert habit.start_date == date.today()
        assert habit.created_date == date.today()
        assert len(habit.completions) == 0
        assert habit._manually_paused == False

    def test_weekly_habit_created_correctly(self):
        """A valid WeeklyHabit has correct frequency."""
        habit = WeeklyHabit("Reading")
        assert habit.frequency == Frequency.WEEKLY
        assert habit.PERIOD_DAYS == 7
        assert habit.REQUIRED_PER_PERIOD == 1

    def test_biweekly_habit_created_correctly(self):
        """A valid BiWeeklyHabit has correct frequency."""
        habit = BiWeeklyHabit("Meditation")
        assert habit.frequency == Frequency.BIWEEKLY
        assert habit.PERIOD_DAYS == 14
        assert habit.REQUIRED_PER_PERIOD == 1

    def test_twice_weekly_habit_created_correctly(self):
        """A valid TwiceWeeklyHabit has correct frequency and requirement."""
        habit = TwiceWeeklyHabit("Gym")
        assert habit.frequency == Frequency.TWICEWEEKLY
        assert habit.PERIOD_DAYS == 7
        assert habit.REQUIRED_PER_PERIOD == 2

    def test_start_date_defaults_to_today(self):
        """Start date defaults to today when not provided."""
        habit = DailyHabit("Exercise")
        assert habit.start_date == date.today()

    def test_custom_start_date_accepted(self):
        """A future start date is accepted."""
        tomorrow = date.today() + timedelta(days=1)
        habit = DailyHabit("Exercise", begn_date=tomorrow)
        assert habit.start_date == tomorrow

    def test_past_start_date_rejected(self):
        """A past start date raises ValueError."""
        yesterday = date.today() - timedelta(days=1)
        with pytest.raises(ValueError):
            DailyHabit("Exercise", begn_date=yesterday)

    def test_past_start_date_bypass_works(self):
        """A past start date is accepted with _bypass_date_check=True."""
        yesterday = date.today() - timedelta(days=1)
        habit = DailyHabit(
            "Exercise",
            begn_date          = yesterday,
            _bypass_date_check = True
        )
        assert habit.start_date == yesterday

    def test_optional_description_defaults_to_none(self):
        """Description defaults to None when not provided."""
        habit = DailyHabit("Exercise")
        assert habit.description is None


# --- Validation Tests ---

class TestHabitValidation:
    """Tests for input validation on creation."""

    def test_empty_name_raises_value_error(self):
        """Empty name raises ValueError."""
        with pytest.raises(ValueError):
            DailyHabit("")

    def test_whitespace_name_raises_value_error(self):
        """Whitespace-only name raises ValueError."""
        with pytest.raises(ValueError):
            DailyHabit("   ")

    def test_non_string_name_raises_type_error(self):
        """Non-string name raises TypeError."""
        with pytest.raises(TypeError):
            DailyHabit(123)

    def test_wrong_frequency_type_raises_type_error(self):
        """Passing a string as frequency raises TypeError."""
        with pytest.raises(TypeError):
            Habit("Exercise", "daily")

    def test_none_frequency_raises_type_error(self):
        """None as frequency raises TypeError."""
        with pytest.raises(TypeError):
            Habit("Exercise", None)


# --- Immutability Tests ---

class TestHabitImmutability:
    """Tests that immutable fields cannot be changed after creation."""

    def test_name_cannot_be_changed(self, daily_habit):
        """Name raises AttributeError when reassigned."""
        with pytest.raises(AttributeError):
            daily_habit.name = "New Name"

    def test_frequency_cannot_be_changed(self, daily_habit):
        """Frequency raises AttributeError when reassigned."""
        with pytest.raises(AttributeError):
            daily_habit.frequency = Frequency.WEEKLY

    def test_created_date_cannot_be_changed(self, daily_habit):
        """Created date raises AttributeError when reassigned."""
        with pytest.raises(AttributeError):
            daily_habit.created_date = date.today()

    def test_start_date_can_be_changed_before_completions(self, daily_habit):
        """Start date can be changed when no completions exist."""
        tomorrow = date.today() + timedelta(days=1)
        daily_habit.start_date = tomorrow
        assert daily_habit.start_date == tomorrow

    def test_start_date_cannot_be_changed_after_completions(self, daily_habit):
        """Start date raises ValueError after completions exist."""
        daily_habit.check_habit_completion(datetime.now())
        tomorrow = date.today() + timedelta(days=1)
        with pytest.raises(ValueError):
            daily_habit.start_date = tomorrow


# --- Completion Tests ---

class TestHabitCompletion:
    """Tests for check_habit_completion behaviour."""

    def test_completion_returns_true_for_new_entry(self, daily_habit):
        """First completion of the day returns True."""
        result = daily_habit.check_habit_completion(datetime.now())
        assert result == True

    def test_completion_is_stored(self, daily_habit):
        """Completion is added to completions list."""
        daily_habit.check_habit_completion(datetime.now())
        assert len(daily_habit.completions) == 1

    def test_completion_stores_datetime(self, daily_habit):
        """Stored completion is a datetime object."""
        daily_habit.check_habit_completion(datetime.now())
        assert isinstance(daily_habit.completions[0], datetime)

    def test_duplicate_completion_returns_false(self, daily_habit):
        """Second completion on same day returns False."""
        daily_habit.check_habit_completion(datetime.now())
        result = daily_habit.check_habit_completion(datetime.now())
        assert result == False

    def test_duplicate_not_stored(self, daily_habit):
        """Duplicate completion is not added to list."""
        daily_habit.check_habit_completion(datetime.now())
        daily_habit.check_habit_completion(datetime.now())
        assert len(daily_habit.completions) == 1

    def test_future_completion_rejected(self, daily_habit):
        """Future date raises ValueError."""
        future = datetime.now() + timedelta(days=1)
        with pytest.raises(ValueError):
            daily_habit.check_habit_completion(future)

    def test_completion_before_start_date_rejected(self):
        """Date before start_date raises ValueError."""
        habit = DailyHabit(
            name               = "Test",
            begn_date          = date.today(),
            _bypass_date_check = False
        )
        yesterday = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError):
            habit.check_habit_completion(yesterday)

    def test_wrong_type_raises_type_error(self, daily_habit):
        """Non-datetime argument raises TypeError."""
        with pytest.raises(TypeError):
            daily_habit.check_habit_completion("2026-07-08")

    def test_completions_stored_in_order(self, daily_habit):
        """Multiple completions are stored in chronological order."""
        habit = DailyHabit(
            name               = "Test Order",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        for days_ago in [3, 1, 2]:
            d = date.today() - timedelta(days=days_ago)
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )
        dates = [c.date() for c in habit.completions]
        assert dates == sorted(dates)


# --- Streak Tests ---

class TestHabitStreak:
    """Tests for streak calculations."""

    def test_streak_zero_with_no_completions(self, daily_habit):
        """Streak is 0 with no completions."""
        assert daily_habit.get_current_habit_streak() == 0

    def test_streak_one_after_completion_today(self, daily_habit):
        """Streak is 1 after completing today."""
        daily_habit.check_habit_completion(datetime.now())
        assert daily_habit.get_current_habit_streak() == 1

    def test_streak_counts_consecutive_days(self, daily_habit_with_streak):
        """Streak correctly counts 7 consecutive days."""
        assert daily_habit_with_streak.get_current_habit_streak() == 7

    def test_streak_breaks_on_gap(self, daily_habit_with_gap):
        """
        Streak resets after a gap.
        Gap habit: completed days 10-8, gap days 7-5, completed days 4-2.
        Current streak should be 4.
        """
        assert daily_habit_with_gap.get_current_habit_streak() == 4

    def test_longest_streak_found_correctly(self, daily_habit_with_gap):
        """Longest streak is correctly identified across all history."""
        assert daily_habit_with_gap.get_longest_habit_streak() == 4

    def test_longest_streak_zero_with_no_completions(self, daily_habit):
        """Longest streak is 0 with no completions."""
        assert daily_habit.get_longest_habit_streak() == 0

    def test_twice_weekly_streak_requires_two_completions(self):
        """
        TwiceWeeklyHabit streak only counts weeks with at least 2 completions. 
        A week with only 1 completion does not satisfy the requirement.
        """
        habit = TwiceWeeklyHabit(
            name               = "Test Gym",
            begn_date          = date.today() - timedelta(days=21),
            _bypass_date_check = True
        )
        # two weeks ago — two completions (period 2)
        # 14//7=2 and 15//7=2 — both in period 2
        d1 = date.today() - timedelta(days=14)
        d2 = date.today() - timedelta(days=15)

        # last week — only one completion (period 1)
        # 8//7=1 — in period 1
        d3 = date.today() - timedelta(days=8)

        # current week — no completions (period 0)
        for d in [d1, d2, d3]:
            habit.check_habit_completion(
                datetime(d.year, d.month, d.day, 8, 0)
            )

        # period 0: 0 completions → start from period 1
        # period 1: 1 completion < REQUIRED(2) → streak = 0
        assert habit.get_current_habit_streak() == 0

# --- Status Tests ---

class TestHabitStatus:
    """Tests for is_active and has_started behaviour."""

    def test_new_habit_is_active(self, daily_habit):
        """A new habit starting today is active."""
        assert daily_habit.is_active == True

    def test_future_habit_not_started(self, future_habit):
        """A habit with future start date has not started."""
        assert future_habit.habit_has_started == False

    def test_future_habit_not_active(self, future_habit):
        """A habit with future start date is not active."""
        assert future_habit.is_active == False

    def test_manually_paused_habit_not_active(self, paused_habit):
        """A manually paused habit is not active."""
        assert paused_habit.is_active == False

    def test_reactivated_habit_is_active(self, paused_habit):
        """A reactivated habit is active again."""
        paused_habit.reactivate_habit()
        assert paused_habit.is_active == True

    def test_abandoned_habit_not_active(self, abandoned_habit):
        """
        A habit with no completion for longer than
        the abandonment threshold is not active.
        """
        assert abandoned_habit.is_active == False

    def test_completion_reactivates_abandoned_habit(self, abandoned_habit):
        """Recording a completion today reactivates an abandoned habit."""
        abandoned_habit.check_habit_completion(datetime.now())
        assert abandoned_habit.is_active == True

    def test_has_started_true_for_today(self, daily_habit):
        """A habit starting today has started."""
        assert daily_habit.habit_has_started == True


# --- Notes Tests ---

class TestHabitNotes:
    """Tests for add_note behaviour."""

    def test_note_added_within_grace_period(self, daily_habit):
        """Note is added successfully for today."""
        result = daily_habit.add_note(date.today(), "Test note.")
        assert result == True
        assert date.today() in daily_habit.notes

    def test_note_content_stored_correctly(self, daily_habit):
        """Note content is stored as written."""
        daily_habit.add_note(date.today(), "My note content.")
        assert daily_habit.notes[date.today()] == "My note content."

    def test_note_outside_grace_period_returns_false(self):
        """Note for a date outside grace period returns False."""
        habit = DailyHabit(
            name               = "Test",
            begn_date          = date.today() - timedelta(days=30),
            _bypass_date_check = True
        )
        old_date = date.today() - timedelta(days=25)
        result = habit.add_note(old_date, "Old note.")
        assert result == False

    def test_empty_note_raises_value_error(self, daily_habit):
        """Empty note string raises ValueError."""
        with pytest.raises(ValueError):
            daily_habit.add_note(date.today(), "")

    def test_whitespace_note_raises_value_error(self, daily_habit):
        """Whitespace-only note raises ValueError."""
        with pytest.raises(ValueError):
            daily_habit.add_note(date.today(), "   ")

    def test_wrong_date_type_raises_type_error(self, daily_habit):
        """Non-date argument raises TypeError."""
        with pytest.raises(TypeError):
            daily_habit.add_note("2026-07-08", "Note.")

    def test_note_before_start_date_raises_value_error(self, daily_habit):
        """Note for date before start_date raises ValueError."""
        yesterday = date.today() - timedelta(days=1)
        with pytest.raises(ValueError):
            daily_habit.add_note(yesterday, "Note.")

    def test_existing_note_overwritten(self, daily_habit):
        """Adding a note for the same date overwrites the previous one."""
        daily_habit.add_note(date.today(), "First note.")
        daily_habit.add_note(date.today(), "Second note.")
        assert daily_habit.notes[date.today()] == "Second note."


# --- Late Completion Tests ---

class TestLateCompletion:
    """Tests for late_complete behaviour."""

    def test_late_completion_within_grace_period(self):
        """
        Late completion within grace period returns True and is stored.
        """
        habit = DailyHabit(
            name               = "Test Late",
            begn_date          = date.today() - timedelta(days=5),
            _bypass_date_check = True
        )
        yesterday = datetime.now() - timedelta(days=1)
        result = habit.late_complete(yesterday)
        assert result == True
        assert len(habit.completions) == 1

    def test_late_completion_outside_grace_period_returns_false(self):
        """
        Late completion outside grace period returns False and is not stored.
        """
        habit = DailyHabit(
            name               = "Test Late",
            begn_date          = date.today() - timedelta(days=30),
            _bypass_date_check = True
        )
        old_date = datetime.now() - timedelta(days=25)
        result = habit.late_complete(old_date)
        assert result == False
        assert len(habit.completions) == 0

    def test_late_completion_wrong_type_raises_type_error(self, daily_habit):
        """Non-datetime argument raises TypeError."""
        with pytest.raises(TypeError):
            daily_habit.late_complete("2026-07-07")

    def test_late_completion_duplicate_returns_false(self):
        """
        Late completion for an already-completed day returns False.
        """
        habit = DailyHabit(
            name               = "Test Late Dup",
            begn_date          = date.today() - timedelta(days=3),
            _bypass_date_check = True
        )
        yesterday = datetime.now() - timedelta(days=1)
        habit.late_complete(yesterday)
        result = habit.late_complete(yesterday)
        assert result == False
        assert len(habit.completions) == 1