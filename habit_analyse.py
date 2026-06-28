from datetime import date
from functools import reduce
from habit import Frequency, Habit

# --- Helper Methods Definition ---
def _should_be_analysed(habits_list: Habit) -> bool:
    """
    A habit is worth analysing only if it is active, has started,
    and at least one full period has passed since start_date.
    """
    if not habits_list.is_active:
        return False
    if not habits_list.has_started:
        return False
    periods_elapsed = (date.today() - habits_list.start_date).days // habits_list.PERIOD_DAYS
    return periods_elapsed >= 1


# --- Functions Definition ---

def get_all_habits_list(habits_list: list[Habit]) -> list[Habit]: 
    """
    Function that returns a list with all the habits. 
    Includes inactive habits that have not started yet.

    Arguments: 
        habits_list: list with all the Habit objects.

    Returns: 
        Full habits list. 
    """
    return list(map(lambda h: h, habits_list))


def get_habits_by_frequency(habits_list: list[Habit], frequency: Frequency) -> list[Habit]:
    """
    Function that returns all habits that have the chosen frequency. 
    Includes inactive habits but excludes habits that have not started. 

    Arguments: 
        habits_list: list of all the Habits. 
        frequency: the frequency (from the Fequency class) that we want to analyse.

    Returns: 
        List of habits that match the chosen frequency. 
        Returns an empty list if there are no habits of that frequency. 

    Raises:
        TypeError: if frequency is not a Frequency enum value.
    """
    if not isinstance(frequency, Frequency):
        raise TypeError("The frequency must belong to the Frequency(Enum) Class.")

    return list(filter(lambda h: h.habit_has_started and h.frequency == frequency, habits_list))


def get_longest_streak_all_habits(habits_list: list[Habit]) -> Habit | None:
    """
    Function that takes into consideration all active habits with at least one completion and returns the one that has the longest streak.
    
    Arguments:
        habits_list: list of Habit objects to analyse.

    Returns:
        The Habit with the highest longest streak. Returns None if the list is empty.
    """
    analysable = list(filter(_should_be_analysed, habits_list))

    if not analysable: 
        return None
    
    return reduce(
        lambda best, current:
            current if current.get_longest_habit_streak() > best.get_longest_habit_streak()
            else best,
        analysable
    )


def get_longest_streak_for_single_habit(habit: Habit) -> int:
    """
    Function that returns the the longest run streak for a specific habit.

    Argumentss:
        habit: the Habit object to analyse.

    Returns:
        The longest streak as an integer.

    Raises:
        TypeError: if habit is not a Habit instance.
    """
    if not isinstance(habit, Habit):
        raise TypeError("The habit must be a Habit instance")

    return habit.get_longest_habit_streak()


def get_completion_rate(habit: Habit) -> float:
    """
    Function that calculates the completion rate since the habit's start date.
    Rate = completed periods / total periods since start date.

    Arguments:
        habit: the Habit object to analyse.

    Returns:
        Completion rate as a float between 0.0 and 1.0.
        Returns 0.0 if habit has no completions.
    """
    if not habit.completions:
        return 0.0

    total_periods = max(
        (date.today() - habit.start_date).days // habit.PERIOD_DAYS,
        1
    )

    completed_periods = len(set(
        (habit._to_date(c) - habit.start_date).days // habit.PERIOD_DAYS
        for c in habit.completions
    ))

    return round(completed_periods / total_periods, 2)


def get_completion_rate_over_last_n_periods(habit: Habit, n: int) -> float:
    """
    Function that calculate completion rate over the last N periods.
    Rate = completed periods out of last N periods.

    Arguments:
        habit: the Habit object to analyse.
        n: number of periods to look back on.

    Returns:
        Completion rate as a float between 0.0 and 1.0.
        Returns 0.0 if habit has no completions.

    Raises:
        ValueError: if n is less than 1.
        TypeError: if n is not an int.
    """
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 1:
        raise ValueError("n must be at least 1")
    if not habit.completions:
        return 0.0

    today = date.today()

    completed_in_window = len(set(filter(
        lambda p: 0 <= p < n,
        map(
            lambda c: (today - habit._to_date(c)).days // habit.PERIOD_DAYS,
            habit.completions
        )
    )))

    return round(completed_in_window / n, 2)


def get_struggling_habits(habits_list: list[Habit]) -> list[Habit]:
    """
    Function that returns habits which the user is struggling to complete with the required consistency. 
    Excludes inactive habits, habits that have not started yet and habits where a full period has not passed yet and so we cannot judge the performance yet.

    A habit is defined as struggling (or in need of attention) if its current streak is zero (0) and at least one full period has passed since its last completion or start date. 

    Arguments:
        habits_list: list of Habit objects to analyse.

    Returns:
        List of active and started habits with current streak of 0. Returns an empty list if none.
    """
    return list(filter(lambda h: _should_be_analysed(h) and h.get_current_habit_streak() == 0, habits_list))


def get_habits_never_completed(habits_list: list[Habit]) -> list[Habit]:
    """
    Function that returns active habits, that are past their start date and have never been completed.

    Arguments:
        habits_list: list of Habit objects to analyse.

    Returns:
        List of habits with no completions. Empty list if none.
    """
    return list(filter(lambda h: _should_be_analysed(h) and len(h.completions) == 0, habits_list))


def get_most_consistent_habit(habits_list: list[Habit]) -> Habit | None:
    """
    Function that returns the started active habit with the highest completion rate since its start date.

    Arguments:
        habits_list: list of Habit objects to analyse.

    Returns:
        The most consistent Habit, or None if list is empty.
    """
    analysable = list(filter(_should_be_analysed, habits_list))

    if not analysable:
        return None

    return reduce(
        lambda best, current:
            current if get_completion_rate(current) > get_completion_rate(best)
            else best,
        analysable
    )


def get_oldest_habit(habits_list: list[Habit]) -> Habit | None:
    """
    Function that return the active habit with the earliest start date.
    Excludes habits that have not started yet.

    Arguments:
        habits_list: list of Habit objects to analyse.

    Returns:
        The oldest Habit, or None if list is empty.
    """
    started = list(filter(lambda h: h.has_started, habits_list))

    if not started:
        return None

    return reduce(
        lambda oldest, current:
            current if current.start_date < oldest.start_date else oldest,
        started
    )


def get_newest_habit(habits_list: list[Habit]) -> Habit | None:
    """
    Function that returns the active habit with the most recent start date.
    Excludes habits that have not started yet.

    Argumentss:
        habits_list: list of Habit objects to analyse.

    Returns:
        The newest Habit, or None if list is empty.
    """
    started = list(filter(lambda h: h.has_started, habits_list))

    if not started:
        return None

    return reduce(
        lambda newest, current:
            current if current.start_date < newest.start_date else newest,
        started
    )


def get_completion_rates_by_frequency(habits_list: list[Habit], frequency: Frequency) -> float:
    """
    Function that return the average completion rate for started and active habits of a given frequency.

    Argumentss:
        habits_list: list of Habit objects to analyse.
        frequency: the Frequency enum value to filter by.

    Returns:
        Average completion rate as float between 0.0 and 1.0.
        Returns 0.0 if no analysable habits match the frequency.

    Raises:
        TypeError: if frequency is not a Frequency enum value.
    """
    if not isinstance(frequency, Frequency):
        raise TypeError("The frequency must belong to the Frequency(Enum) Class.")

    matching = list(filter(
        lambda h: _should_be_analysed(h) and h.frequency == frequency,
        habits_list
    ))

    if not matching:
        return 0.0

    rates = list(map(get_completion_rate, matching))

    return round(reduce(lambda acc, r: acc + r, rates) / len(rates), 2)