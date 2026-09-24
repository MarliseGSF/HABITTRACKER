import pytest
import os
from datetime import date, datetime, timedelta
from Models.habit import (DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit)
from Models.habit_management import HabitTracker
from Storage.habit_database import init_db


# ── Database Fixtures ─────────────────────────────────────────────────────────

TEST_DB_PATH = "database/test_habits.db"

@pytest.fixture
def db_conn():
    """
    Function that creates a fresh test database connection before each test
    and deletes it after the test is complete. Keeps tests completely isolated from
    the real database.

    Yields:
        An open sqlite3 connection to a temporary test database.
    """
    conn = init_db(TEST_DB_PATH)
    yield conn
    conn.close()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


# ── Simple Habit Fixtures (no completions) ────────────────────────────────────

@pytest.fixture
def daily_habit():
    """
    A test DailyHabit with no completions, starting today.
    Use for testing creation, validation, and basic behaviour.
    """
    return DailyHabit(
        name  = "Test Exercise",
        descp = "Test daily habit."
    )


@pytest.fixture
def weekly_habit():
    """
    A test WeeklyHabit with no completions, starting today.
    Use for testing creation, validation, and basic behaviour.
    """
    return WeeklyHabit(
        name  = "Test Reading",
        descp = "Test weekly habit."
    )


@pytest.fixture
def biweekly_habit():
    """
    A test BiWeeklyHabit with no completions, starting today.
    Use for testing creation, validation, and basic behaviour.
    """
    return BiWeeklyHabit(
        name  = "Test Meditation",
        descp = "Test biweekly habit."
    )


@pytest.fixture
def twice_weekly_habit():
    """
    A test TwiceWeeklyHabit with no completions, starting today.
    Use for testing creation, validation, and basic behaviour.
    """
    return TwiceWeeklyHabit(
        name  = "Test Gym",
        descp = "Test twice weekly habit."
    )


@pytest.fixture
def future_habit():
    """
    A DailyHabit that has not started yet (start date tomorrow).
    Use for testing has_started and is_active behaviour.
    """
    return DailyHabit(
        name      = "Test Future",
        begn_date = date.today() + timedelta(days=1)
    )


@pytest.fixture
def paused_habit():
    """
    A DailyHabit that has been manually paused.
    Use for testing pause/resume behaviour.
    """
    habit = DailyHabit(
        name  = "Test Paused",
        descp = "A manually paused habit."
    )
    habit.deactivate_habit()
    return habit


# ── Habit Fixtures With Completions ──────────────────────────────────────────

@pytest.fixture
def daily_habit_with_streak():
    """
    A DailyHabit with 7 consecutive daily completions
    ending yesterday. Current streak should be 7.
    Use for testing streak calculations.
    """
    habit = DailyHabit(
        name               = "Test Streak",
        begn_date          = date.today() - timedelta(days=7),
        _bypass_date_check = True
    )
    for days_ago in range(7, 0, -1):
        completion_date = date.today() - timedelta(days=days_ago)
        habit.check_habit_completion(datetime(
            completion_date.year,
            completion_date.month,
            completion_date.day,
            8, 0
        ))
    return habit


@pytest.fixture
def daily_habit_with_gap():
    """
    A DailyHabit with a gap in completions.
    Completed days 10-8 ago, gap days 7-5, completed days 4-2 ago.
    Current streak = 3, longest streak = 3.
    Use for testing streak gap detection.
    """
    habit = DailyHabit(
        name               = "Test Gap",
        begn_date          = date.today() - timedelta(days=10),
        _bypass_date_check = True
    )
    for days_ago in [10, 9, 8, 4, 3, 2, 1]:
        completion_date = date.today() - timedelta(days=days_ago)
        habit.check_habit_completion(datetime(
            completion_date.year,
            completion_date.month,
            completion_date.day,
            8, 0
        ))
    return habit


@pytest.fixture
def abandoned_habit():
    """
    A DailyHabit whose last completion was 10 days ago.
    Abandonment threshold for daily = 5 days.
    is_active should return False.
    Use for testing auto-pause behaviour.
    """
    habit = DailyHabit(
        name               = "Test Abandoned",
        begn_date          = date.today() - timedelta(days=10),
        _bypass_date_check = True
    )
    completion_date = date.today() - timedelta(days=10)
    habit.check_habit_completion(datetime(
        completion_date.year,
        completion_date.month,
        completion_date.day,
        8, 0
    ))
    return habit


@pytest.fixture
def habit_with_notes():
    """
    A DailyHabit with a note added directly to the notes dict
    (bypassing grace period for test setup purposes).
    """
    habit = DailyHabit(
        name  = "Test Notes",
        descp = "A habit with notes."
    )
    habit.notes[date.today()] = "Test note content."
    return habit


# ── Tracker Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def empty_tracker():
    """
    An empty HabitTracker with no habits.
    Use for testing add/remove behaviour.
    """
    return HabitTracker()


@pytest.fixture
def populated_tracker():
    """
    A HabitTracker with one habit of each frequency type.
    No completions — use for structural and filter tests.
    """
    tracker = HabitTracker()
    tracker.create_new_habit(DailyHabit("Tracker Exercise"))
    tracker.create_new_habit(WeeklyHabit("Tracker Reading"))
    tracker.create_new_habit(BiWeeklyHabit("Tracker Meditation"))
    tracker.create_new_habit(TwiceWeeklyHabit("Tracker Gym"))
    return tracker


@pytest.fixture
def tracker_with_completions():
    """
    A HabitTracker with one DailyHabit that has 7 consecutive
    completions. Use for analytics tests.
    """
    tracker = HabitTracker()
    habit = DailyHabit(
        name               = "Tracker Water",
        begn_date          = date.today() - timedelta(days=7),
        _bypass_date_check = True
    )
    for days_ago in range(7, 0, -1):
        completion_date = date.today() - timedelta(days=days_ago)
        habit.check_habit_completion(datetime(
            completion_date.year,
            completion_date.month,
            completion_date.day,
            8, 0
        ))
    tracker.create_new_habit(habit)
    return tracker