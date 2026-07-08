"""
File with 5 pre-defined habits with simulated tracking data spanning 4 weeks. 
It is used to seed the database on the first run. 

Habit patterns:
    Exercise        → DailyHabit,       imperfect streak
    Drink Water     → DailyHabit,       perfect streak
    Gym             → TwiceWeeklyHabit, inconsistent
    Review Finances → WeeklyHabit,      mostly consistent
    Meditation      → BiweeklyHabit,    struggling, currently paused
"""

from datetime import date, datetime, timedelta
from Models.habit import (DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit)


# --- Helper Methods Definition ---

def _make_datetime(d: date, hour: int, minute: int = 0) -> datetime:
    """
    Helper function that creates a datetime from a date and time components.
    Keeps sample data creation clean and readable.

    Arguments:
        d: the date.
        hour: the hour (0-23).
        minute: the minute (0-59). Defaults to 0.

    Returns:
        A datetime object combining the date and time.
    """
    return datetime(d.year, d.month, d.day, hour, minute)


# --- Methods Definition ---

def create_sample_habits() -> list:
    """
    Function that create 5 pre-defined habits with 4 weeks of realistic tracking data. 
    Each habit has a different completion pattern to demonstrate analytics functions effectively.

    Habit patterns:
        Exercise        → strong but imperfect daily streak
        Drink Water     → perfect daily streak, never missed
        Gym             → inconsistent twice-weekly habit
        Review Finances → mostly consistent weekly habit
        Meditation      → struggling biweekly habit, currently paused

    Returns:
        A list of 5 Habit objects ready to be added to a HabitTracker and saved to the database.
    """
    today = date.today()
    four_weeks_ago = today - timedelta(weeks=4)

    # ── 1. Exercise — DailyHabit ─────────────────────────────────────────
    # Strong streak with a few missed days scattered throughout.
    # Completed mostly in the morning.

    exercise = DailyHabit(
        name      = "[Sample] Exercise",
        begn_date = four_weeks_ago,
        descp     = "30 minutes of exercise every day."
    )

    # days to SKIP (missed) — day offsets from four_weeks_ago
    exercise_missed = {3, 10, 17, 24}   # one missed day per week

    for day_offset in range(28):
        if day_offset not in exercise_missed:
            completion_date = four_weeks_ago + timedelta(days=day_offset)
            exercise.check_habit_completion(
                _make_datetime(completion_date, hour=7, minute=30)
            )

    # add a note explaining one missed day - will fail due to being outside of the grace period
    exercise.add_note(
        four_weeks_ago + timedelta(days=3),
        "Missed due to illness."
    )

    # Write directly (same as load_habits does):
    exercise.notes[four_weeks_ago + timedelta(days=3)] = "Missed due to illness."

    # ── 2. Drink Water — DailyHabit ──────────────────────────────────────
    # Perfect streak — completed every single day.
    # Completed at varied times throughout the day.

    drink_water = DailyHabit(
        name      = "[Sample] Drink Water",
        begn_date = four_weeks_ago,
        descp     = "Drink at least 2 litres of water every day."
    )

    completion_times = [9, 10, 8, 11, 9, 10, 8,    # week 1
                        9, 10, 9, 11, 8, 10, 9,     # week 2
                        10, 9, 8, 9, 11, 10, 9,     # week 3
                        8, 9, 10, 9, 8, 11, 10]     # week 4

    for day_offset in range(28):
        completion_date = four_weeks_ago + timedelta(days=day_offset)
        drink_water.check_habit_completion(
            _make_datetime(completion_date, hour=completion_times[day_offset])
        )

    # ── 3. Gym — TwiceWeeklyHabit ────────────────────────────────────────
    # Inconsistent — some weeks completed twice, some only once or not at all.
    # Completed in the evening.

    gym = TwiceWeeklyHabit(
        name      = "[Sample] Gym",
        begn_date = four_weeks_ago,
        descp     = "Go to the gym twice a week."
    )

    # (day_offset, hour) for each completion
    gym_completions = [
        (1, 18),    # week 1 — two completions ✅
        (4, 19),
        (8, 18),    # week 2 — only one completion ❌
        (15, 19),   # week 3 — two completions ✅
        (18, 18),
                    # week 4 — no completions ❌
    ]

    for day_offset, hour in gym_completions:
        completion_date = four_weeks_ago + timedelta(days=day_offset)
        gym.check_habit_completion(
            _make_datetime(completion_date, hour=hour)
        )

    gym.add_note(
        four_weeks_ago + timedelta(days=22),
        "Missed gym this week due to travel."
    )

    # ── 4. Review Finances — WeeklyHabit ─────────────────────────────────
    # Mostly consistent — completed 3 out of 4 weeks.
    # Completed on Sunday afternoons.

    review_finances = WeeklyHabit(
        name      = "[Sample] Review Finances",
        begn_date = four_weeks_ago,
        descp     = "Review budget and expenses every week."
    )

    # completed on day 6 (Sunday), 13, skipped week 3, completed day 27
    finances_completions = [6, 13, 27]

    for day_offset in finances_completions:
        completion_date = four_weeks_ago + timedelta(days=day_offset)
        review_finances.check_habit_completion(
            _make_datetime(completion_date, hour=15, minute=30)
        )

    review_finances.add_note(
        four_weeks_ago + timedelta(days=20),
        "Skipped this week — will catch up next Sunday."
    )

    # ── 5. Meditation — BiWeeklyHabit ────────────────────────────────────
    # Struggling — only completed once in 4 weeks.
    # Currently paused.

    meditation = BiWeeklyHabit(
        name      = "[Sample] Meditation",
        begn_date = four_weeks_ago,
        descp     = "Meditate at least once every two weeks."
    )

    # only one completion in 4 weeks
    meditation.check_habit_completion(
        _make_datetime(four_weeks_ago + timedelta(days=5), hour=21)
    )

    meditation.add_note(
        four_weeks_ago + timedelta(days=19),
        "Struggling to keep up with this habit — pausing for now."
    )

    # manually pause — reflects _manually_paused flag
    meditation.deactivate_habit()

    return [exercise, drink_water, gym, review_finances, meditation]