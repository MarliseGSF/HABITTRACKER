import os
import Storage.habit_database as st
import Analytics.habit_analyse as an
from datetime import datetime, date, timedelta
from Storage.sample_data import create_sample_habits
from Models.habit import Habit, DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency
from Models.habit_management import HabitTracker

def startup() -> tuple:
    """
    Function to initialise the database and load the habits.
    If the database is empty it loads the sample data into memory only. 
    Note: sample data is never persisted.
    
    Returns:
        A tuple of (conn, tracker, is_sample_session): 
            conn: the open database connection
            tracker: the populated HabitTracker
            is_sample_session: flag that is true if only sample data is loaded.
    """
    conn = st.init_db()
    tracker = st.load_habits(conn)

    if not tracker.habits:
        print("No saved habits found — loading sample data for demonstration purposes.")
        print("─────────────────────────────────────────────")
        print("PLEASE NOTE:")
        print("Sample habits are loaded for demonstration only and will not be stored once you exited the session.")
        print("Any additional habits added WILL be saved.")
        print("─────────────────────────────────────────────\n")
        
        for habit in create_sample_habits():
            tracker.create_new_habit(habit)

        """
        for h in tracker.habits:
            today = date.today()
            completion_dates = [c.date() for c in h.completions]
            
            print(f"DEBUG: {h.name}")
            print(f"       start_date  = {h.start_date}")
            print(f"       completions = {len(h.completions)}")
            print(f"       streak      = {h.get_current_habit_streak()}")
            print(f"    PERIOD_DAYS     : {h.PERIOD_DAYS}")
            print(f"    last completion : {max(completion_dates) if completion_dates else 'none'}")
            print(f"    first completion: {min(completion_dates) if completion_dates else 'none'}")
            if completion_dates:
                days_since_last = (today - max(completion_dates)).days
                period = (today - max(completion_dates)).days // h.PERIOD_DAYS
                print(f"    days since last : {days_since_last}")
                print(f"    periods ago     : {period}")
            """


        input("Press Enter to continue...")
        return conn, tracker, True

    return conn, tracker, False


def shutdown(conn, tracker: HabitTracker, is_sample: bool) -> None:
    """
    Function that saves all - except sample - habits and closes the database connection.

    Argumentss:
        conn: open database connection.
        tracker: the HabitTracker to save.
        is_sample: true if the session was started by loading the sample data. 
    """
    if is_sample:
        # separates real habits from sample habits
        real_habits = [
            h for h in tracker.habits
            if not h.name.startswith("[Sample]")
        ]
        sample_habits = [
            h for h in tracker.habits
            if h.name.startswith("[Sample]")
        ]

        print("\n─────────────────────────────────────────────")
        print("SESSION SUMMARY")
        print("─────────────────────────────────────────────")

        if sample_habits:
            print(f"\n {len(sample_habits)} sample habit(s) were NOT saved:")
            for h in sample_habits:
                print(f"      → {h.name}")

        if real_habits:
            print(f"\n {len(real_habits)} real habit(s) were saved:")
            for h in real_habits:
                print(f"      → {h.name}")
            # save only real habits
            for habit in real_habits:
                st.save_habit(conn, habit)
        else:
            print("\nNo real habits were added this session.")
            print("Sample data will reload on your next visit.")

        print("─────────────────────────────────────────────")

    else:
        # normal session — save everything
        saved = st.save_all_habits(conn, tracker)
        if saved:
            print(f"\n{len(tracker.habits)} habit(s) saved successfully.")
        else:
            print("\nSome habits may not have saved correctly.")

    conn.close()
    print("\nEnd of Session\n")


# --- Display Function Definition ---

def clear_screen() -> None:
    """
    Function that clears the terminal screen.

    Arguments:
        conn: open database connection.
        tracker: the HabitTracker to save.
    """
    os.system("cls" if os.name == "nt" else "clear")


def print_header(title: str) -> None:
    """
    Function to print a formatted section header.
    """
    print(f"\n{'═' * 40}")
    print(f"  {title}")
    print(f"{'═' * 40}\n")


def print_habit_summary(habit) -> None:
    """
    Function that prints a single habit's key information.

    Argumnts: 
        habit: the habit to be printed.
    """
    if not habit.habit_has_started: status = "Not started yet"
    elif habit._manually_paused: status = "Manually Paused"
    elif not habit.is_active: status = "Auto-Paused (completion needed)"
    else: status = "Active"
    started = "Started" if habit.habit_has_started else "Not started yet"
    print(f"  {habit.name}")
    print(f"    Frequency      : {habit.frequency.value}")
    print(f"    Status         : {status}") #{status} ({started})")
    print(f"    Start date     : ({habit.start_date})")
    print(f"    Streak         : {habit.get_current_habit_streak()} periods")
    print(f"    Completions    : {len(habit.completions)}")
    if habit.description:
        print(f"    Description    : {habit.description}")
    print()


def get_valid_input(prompt: str, valid_options: list) -> str:
    """
    Function that prompts the user  until the user enters a valid option.

    Arguments:
        prompt: the input prompt to display.
        valid_options: list of accepted input strings.

    Returns:
        The validated user input.
    """
    while True:
        choice = input(prompt).strip()
        if choice in valid_options:
            return choice
        print(f"Invalid option. Please choose from {valid_options}")

    
def get_valid_date(prompt: str, allow_empty: bool = True, reject_past: bool = False, reject_future: bool = False, min_date: date = None, min_date_message: str = None) -> date | None:
    """
    Function that prompts the user to enter a valid date.

    Args:
        prompt: the input prompt to display.
        allow_empty: if True, empty input returns today's date.
        reject_past: if True, rejects dates before today.
        reject_future: if True, rejects dates after today.
        min_date: if provided, rejects dates before this date.
        min_message: if provided, message to be shown to the user in case the input date is rejected.

    Returns:
        A valid date object, or None if allow_empty and input empty.
    """
    while True:
        date_input = input(prompt).strip()

        if not date_input:
            if allow_empty:
                return date.today()
            else:
                print("Date cannot be empty. Please choose a valid date.")
                continue

        try:
            parsed = date.fromisoformat(date_input)

            if reject_past and parsed < date.today():
                print("\nDate cannot be in the past. Please choose a valid date.")
                continue

            if reject_future and parsed > date.today():
                print("\nDate cannot be in the future. Please choose a valid date.")
                continue

            if min_date and parsed < min_date:
                print(
                    min_date_message or
                    f"\nDate cannot be before {min_date}. Please choose a valid date.")
                continue

            return parsed

        except ValueError:
            print("\nInvalid date format. Please use YYYY-MM-DD.")


def get_valid_name(prompt: str, reserved_prefix: str = None) -> str:
    """
    Function that prompts the user to enter a valid name.

    Args:
        prompt: the input prompt to display.
        reserved_prefix: if provided, names starting with this prefix are rejected.

    Returns:
        A valid name string.
    """
    while True:
        name = input(prompt).strip()

        if not name:
            print("Name cannot be empty. Please write a valid name.")
            continue

        if reserved_prefix and name.startswith(reserved_prefix):
            print(
                f"Names cannot start with '{reserved_prefix}' — this prefix is reserved for demonstration habits."
            )
            continue

        return name


# --- Analytics Helper Functions ---

def _show_by_frequency(tracker: HabitTracker) -> None:
    """
    Function that displays habits grouped by frequency.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Habits by Frequency")
    for freq in Frequency:
        habits = an.get_habits_by_frequency(tracker.habits, freq)
        if habits:
            print(f"  {freq.value.upper()}:")
            for h in habits:
                print(f"    → {h.name}")
            print()


def _show_longest_streak(tracker: HabitTracker) -> None:
    """
    Function that displays the habit with the longest streak.
    
    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Longest Streak")
    best = an.get_longest_streak_all_habits(tracker.habits)
    if best:
        print(f"{best.name} → {best.get_longest_habit_streak()} periods")
    else:
        print("No data yet.")


def _show_struggling(tracker: HabitTracker) -> None:
    """
    Function that displays the habits with no current completion (the current streak is null).

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Struggling Habits")
    struggling = an.get_struggling_habits(tracker.habits)
    if struggling:
        for h in struggling:
            print(f"→ {h.name} (best streak: {h.get_longest_habit_streak()} periods)")
    else:
        print("No struggling habits — good job!")


def _show_most_consistent(tracker: HabitTracker) -> None:
    """
    Function to display the most consistently completed habit.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Most Consistent Habit")
    best = an.get_most_consistent_habit(tracker.habits)
    if best:
        print(f"The habit {best.name} is the habit being achieved most consistently.")
    else:
        print("No data yet.")


def _show_time_analysis(tracker: HabitTracker) -> None:
    """
    Function that displays completion time-of-day analysis.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Completion Time Analysis")
    analysis = an.get_completion_time_analysis(tracker.habits)
    overall = analysis['overall'] or 'No data'
    if overall and "/" in overall:
        print(f"Overall most common time: {overall} (tied)")
    else:
        print(f"Overall most common time (takes into account the number of completions): {overall}")
    print("Per habit:")
    for habit_name, bracket in analysis["per_habit"].items():
        print(f"    {habit_name} → {bracket or 'No data'}")


def _show_oldest_habit(tracker: HabitTracker) -> None:
    """
    Function that displays the habit with the earliest start date.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Oldest Habit")
    oldest = an.get_oldest_habit(tracker.habits)
    if oldest:
        print(f"Started on {oldest[0].start_date}:")
        for h in oldest:
            print(f"→ {h.name}")
    else:
        print("No data yet.")


def _show_newest_habit(tracker: HabitTracker) -> None:
    """
    Function that displays the habit with the most recent start date.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Newest Habit")
    newest = an.get_newest_habit(tracker.habits)
    if newest:
        print(f"Started on {newest[0].start_date}:")
        for h in newest:
            print(f"→ {h.name}")
    else:
        print("No data yet.")


def _show_never_completed(tracker: HabitTracker) -> None:
    """
    Function that displays habits that do not have any completion and habits that have not yet started.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Never Completed Habits")
    never_completed = an.get_habits_never_completed(tracker.habits)
    not_started = list(filter( lambda h: not h.habit_has_started, tracker.habits))

    if never_completed:
        print("Habits pass their start date that have never been completed:")
        for h in never_completed:
            print(f"→ {h.name} (started {h.start_date})")
    else:
        print("All habits that have passed their defined start date have been completed at least once!")

    if not_started:
        print("\nHabits scheduled to start: ")
        for h in not_started:
            print(f"→ {h.name} (starts {h.start_date})")

def _show_rate_by_frequency(tracker: HabitTracker) -> None:
    """
    Function that displays the average habit completion rate per frequency type.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Completion Rate by Frequency")
    for freq in Frequency:
        rate = an.get_completion_rates_by_frequency(tracker.habits, freq)
        habits_of_type = an.get_habits_by_frequency(tracker.habits, freq)
        if habits_of_type:
            print(f"  {freq.value.upper()}: {rate * 100:.1f}%")


def _show_recent_completions(habit: Habit, n: int = 5) -> None:
    """
    Function that allows the user to display the last N completions for a habit.

    Arguments: 
        habit: habit to be accessed.
        n: number of completions to be displayed.
    """
    if not habit.completions:
        print("\nNo completions yet.")
        return

    recent = sorted(habit.completions, reverse=True)[:n]
    print(f"\nLast {len(recent)} completion(s):")
    for c in recent:
        print(f"→ {c.strftime('%Y-%m-%d %H:%M')}")


def _show_recent_notes(habit: Habit, n: int = 5) -> None:
    """
    Function that allows the user to display the last N notes for a habit.

    Arguments: 
        habit: habit to be accessed.
        n: number of notes to be displayed.
    """
    if not habit.notes:
        print("\nNo notes yet.")
        return

    recent = sorted(habit.notes.items(), reverse=True)[:n]
    print(f"\nLast {len(recent)} note(s):")
    for note_date, note_text in recent:
        print(f"→ {note_date}: {note_text}")


def _show_completions_for_date(tracker: HabitTracker) -> None:
    """
    Function that allows a user to check which habits were completed on a certain date.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Completions for a Date")

    check_date = get_valid_date(
        "\nEnter date to check (YYYY-MM-DD, press Enter for today)): ",
        allow_empty = True, reject_future = True)

    completed = list(filter(
        lambda h: any(
            c.date() == check_date for c in h.completions
        ),
        tracker.habits
    ))

    print(f"\nResults for {check_date}:")

    if completed:
        print(f"\nCompleted ({len(completed)}):")
        for h in completed:
            completion = next(
                c for c in h.completions if c.date() == check_date
            )
            print(f"→ {h.name} at {completion.strftime('%H:%M')}")
    else:
        print("\nNo habits completed on this date.")


def _get_history_count(default: int = 5, item_name: str = "items", total: int = None) -> int:
    """
    Funtion that asks the user how many recent items to display.
    Defaults to 5 if Enter is pressed.

    Arguments:
        default: the default number to show.
        item_name: name of the item.
        total: total of items available.

    Returns:
        The number of items to display.
    """
    total_str = f" ({total} available)" if total is not None else ""
    while True:
        choice = input(
            f"\nHow many {item_name} to show{total_str} (in descending order)? (press Enter for {default}): "
        ).strip()

        if not choice:
            return min(default, total) if total else default

        try:
            n = int(choice)
            if n < 1:
                print("Please enter a number greater than 0.")
                continue
            if total and n > total:
                print(f"Only {total} {item_name} available — showing all.")
                return total
            return n
        except ValueError:
            print("Please enter a valid number.")


def select_habit_from_list(tracker: HabitTracker) -> "Habit | None":
    """
    Function that displays a numbered list of habits and lets the user select one by number.

    Arguments:
        tracker: the HabitTracker containing habits.

    Returns:
        The selected Habit, or None if no habits exist or user cancels.
    """
    habits = tracker.habits

    if not habits:
        print("No habits found.")
        return None

    print("\nAvailable habits:")
    for i, habit in enumerate(habits, start=1):
        if not habit.habit_has_started: status = "Not started yet"
        elif habit._manually_paused: status = "Manually Paused"
        elif not habit.is_active: status = "Auto-Paused (completion needed)"
        else: status = "Active"

        print(f"{i}. {habit.name} ({habit.frequency.value}, {status})")

    print(f"0. Cancel")

    valid = [str(i) for i in range(len(habits) + 1)]
    choice = get_valid_input(
        "\nSelect habit (0 to cancel): ",
        valid
    )

    if choice == "0":
        return None

    return habits[int(choice) - 1]


# --- Handler Function Definition ---

def handle_view_habits(tracker: HabitTracker) -> None:
    """
    Function that displays all the habits and their current status.

    Arguments:
        tracker: the HabitTracker.
    """
    print_header("All Habits")

    habits = an.get_all_habits_list(tracker.habits)
    if not habits:
        print("No habits found.")
        return

    for habit in habits:
        print_habit_summary(habit)


def handle_add_habit(conn, tracker: HabitTracker, is_sample: bool) -> None:
    """
    Function that guides the user through creating a new habit.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracke to be added.
        is_sample: boolean indication if the habit is a sample or not. 
    """
    print_header("Add New Habit")

    name = get_valid_name("Habit name: ", reserved_prefix="[Sample]")
    
    print("\nFrequency options:")
    print("  1. Daily")
    print("  2. Twice weekly (twice every week)")
    print("  3. Weekly")
    print("  4. Bi-weekly (once every two weeks)")

    freq_choice = get_valid_input(
        "\nChoose frequency (1-4): ",
        ["1", "2", "3", "4"]
    )

    description = input("Description (optional, press Enter to skip): ").strip()
    description = description if description else None

    start_date = get_valid_date(
        "Start date (YYYY-MM-DD, press Enter for today): ",
        allow_empty  = True, reject_past  = True)

    # map choice to child class
    habit_classes = {
        "1": DailyHabit,
        "2": TwiceWeeklyHabit,
        "3": WeeklyHabit,
        "4": BiWeeklyHabit
    }

    HabitClass = habit_classes[freq_choice]

    try:
        habit = HabitClass(
            name      = name,
            begn_date = start_date,
            descp     = description
        )
        tracker.create_new_habit(habit)
        st.save_habit(conn, habit)
        print(f"The habit '{name}' was successfully added")

        if is_sample:
            print("This habit has been saved permanently.")
            print("The sample data will be removed on exit.")

    except ValueError as e:
        print(f"Could not add habit: {e}")

def handle_view_habit_details(tracker: HabitTracker) -> None:
    """
    Function that displays detailed information on a chosen habit.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Habit Details")

    habit = select_habit_from_list(tracker)
    if habit is None:
        return

    if not habit.habit_has_started:
        status = "Not started yet"
    elif habit._manually_paused:
        status = "Manually Paused"
    elif not habit.is_active:
        status = "Auto-Paused (completion needed to reactivate)"
    else:
        status = "Active"


    print(f"\n ══ {habit.name} ══")
    print(f"\nGeneral")
    print(f"Frequency    : {habit.frequency.value}")
    print(f"Status       : {status}")
    print(f"Created      : {habit.created_date}")
    print(f"Start date   : {habit.start_date}")
    if habit.description:
        print(f"Description  : {habit.description}")

    print(f"\nStreaks")
    print(f"Current streak  : {habit.get_current_habit_streak()} periods")
    print(f"Longest streak  : {habit.get_longest_habit_streak()} periods")

    print(f"\nCompletions")
    print(f"Total           : {len(habit.completions)}")

    if habit.completions:
        rate = an.get_completion_rate(habit)
        print(f"Rate since start: {rate * 100:.1f}%")
        usual_time = an.get_most_common_completion_time(habit)
        print(f"Usual time      : {usual_time or 'No data'}")
        print(f"Last completion : {max(c.date() for c in habit.completions)}")
        print(f"First completion: {min(c.date() for c in habit.completions)}")

    n = _get_history_count(default = 5, item_name = "completions", total = len(habit.completions))
    _show_recent_completions(habit, n)

    if habit.notes:
       #print(f"Total : {len(habit.notes)}")
       n = _get_history_count(default = 5, item_name = "notes", total = len(habit.notes))
       _show_recent_notes(habit, n)
    else:
        print("None")


def handle_complete_habit(conn, tracker: HabitTracker) -> None:
    """
    Function that marks the habit has having been completed.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
        is_sample: boolean indication if the habit is a sample or not. 
    """
    print_header("Complete a Habit")

    habit = select_habit_from_list(tracker)

    if habit is None:
        return

    if not habit.habit_has_started:
        print(f"The habit '{habit.name}' has not started yet (starts {habit.start_date}). Please update the start date to start tracking the habit.")
        return
    
    try:
        was_active = habit.is_active
        result = habit.check_habit_completion(datetime.now())

        if result:
            print(f"'Habit {habit.name}' marked complete for today!")
            if was_active: None
            elif not was_active and habit.is_active:
                print(f"The habit '{habit.name}' is now active.")
            elif not was_active and not habit.is_active:
                print(
                    f"The habit '{habit.name}' remains paused — not enough recent completions to reactivate."
                )
            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
            else: 
                print("Sample Habit, the completion will not be permanently stored.")
        else:
            print(f"Habit '{habit.name}' was already completed today.")

    except ValueError as e:
        print(f"\n{e}")

    
def handle_complete_late(conn, tracker: HabitTracker) -> None:
    """
    Function that allows the user to mark a late habit has completed if it is inside its grace period.
    
    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Record Late Completion")

    habit = select_habit_from_list(tracker)
    if habit is None:
        return

    if not habit.habit_has_started:
        print(f"\nThe habit'{habit.name}' has not started yet. Please choose a valid date.")
        print(f"Start date: {habit.start_date}")
        return
    
    grace_days = int((habit.PERIOD_DAYS / 2) + 2)
    max_days_back = habit.PERIOD_DAYS + grace_days
    earliest_allowed = max(
        date.today() - timedelta(days=max_days_back),
        habit.start_date    # ← can't go before habit started
    )

    print(f"\n'{habit.name}' grace period:")
    print(f"     Earliest allowed date: {earliest_allowed}")
    print(f"     Latest allowed date:   {date.today()}")

    if habit.start_date > date.today() - timedelta(days=max_days_back):
        message = (
            f"\nDate cannot be before the habit's start date ({habit.start_date}). Please choose a valid date."
        )
    else:
        message = (
            f"Date is outside the grace period (earliest date: {earliest_allowed}). Please choose a valid date."
        )

    while True:
        completion_date = get_valid_date(
            "\nCompletion date (YYYY-MM-DD): ", 
            allow_empty = False, reject_future = True, min_date = earliest_allowed, min_date_message = message)

        completion_datetime = datetime(completion_date.year, completion_date.month, completion_date.day, 0, 0)

        was_active = habit.is_active

        try:
            result = habit.late_complete(completion_datetime)

            if result:
                print(f"\nLate completion recorded for {completion_date}.")

                if was_active: None
                elif not was_active and habit.is_active:
                    print(f"The habit '{habit.name}' is now active.")
                elif not was_active and not habit.is_active:
                    print(f"The habit '{habit.name}' remains paused — not enough recent completions to reactivate.")
                    threshold = int(2 * ((habit.PERIOD_DAYS / 2) + 2))
                    print(
                        f"A completion within the last {threshold} days is needed to reactivate the habit."
                    )

                if not habit.name.startswith("[Sample]"):
                    st.save_habit(conn, habit)
                else:
                    print("\nSample habit — completion not saved permanently.")
                break

            else:
                print(
                    f"\n{habit.name} already has a completion recorded for that date {completion_date}."
                )
                retry = get_valid_input(
                    "\nWould you like to write a different date? (y/n): ",
                    ["y", "n"]
                )
                if retry == "n":
                    print("\nLate completion cancelled.")
                    break 

        except ValueError as e:
            print(f"\n{e}")
            break


def handle_add_note(conn, tracker: HabitTracker) -> None:
    """
    Function to allow the user to add a note to a specific date. 

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Add Note")

    habit = select_habit_from_list(tracker)
    if habit is None:
        return

    if not habit.habit_has_started:
        print(f"\nThe habit'{habit.name}' has not started yet. Please choose a valid date.")
        print(f"Start date: {habit.start_date}")
        return
    
    grace_days = int((habit.PERIOD_DAYS / 2) + 2)
    max_days_back = habit.PERIOD_DAYS + grace_days
    earliest_allowed = max(
        date.today() - timedelta(days=max_days_back),
        habit.start_date
    )

    print(f"\n'{habit.name}' grace period:")
    print(f"     Earliest allowed date: {earliest_allowed}")
    print(f"     Latest allowed date:   {date.today()}")

    if habit.start_date > date.today() - timedelta(days=max_days_back):
        message = (
            f"\nDate cannot be before the habit's start date ({habit.start_date}). Please choose a valid date."
        )
    else:
        message = (
            f"Date is outside the grace period (earliest date: {earliest_allowed}). Please choose a valid date."
        )

    while True: 
        note_date = get_valid_date(
        "\nDate for note (YYYY-MM-DD, press Enter for today): ",
        allow_empty = True, reject_future = True, min_date = earliest_allowed, min_date_message = message)

        if note_date in habit.notes:
            print(f"\nA note already exists for {note_date}:")
            print(f"     '{habit.notes[note_date]}'")
            confirm = get_valid_input(
                "\n  Overwrite this note? (y/n): ",
                ["y", "n"]
            )
            if confirm == "n":
                print("\n  Note not changed.")
                retry = get_valid_input(
                    "  Try a different date? (y/n): ",
                    ["y", "n"]
                )
                if retry == "n":
                    print("\nNote cancelled.")
                    break
                else:
                    continue
        
        while True:
            note = input("Note: ").strip()
            if note:
                break
            print("Note cannot be empty.")

        try:
            result = habit.add_note(note_date, note)
            if result:
                print(f"Note added for the {note_date} completion.")
                if not habit.name.startswith("[Sample]"):
                    st.save_habit(conn, habit)
                else: 
                    print("Sample Habit, the note will not be permanently stored.")
                break

            else:
                print(f"Could not add note — date may be outside grace period."
                      f"\n     Start of the grace period: {earliest_allowed}")

            retry = get_valid_input(
                    "\nWould you like to try a different date? (y/n): ",
                    ["y", "n"]
                )
            if retry == "n":
                print("\nNote cancelled.")
                break
            
        except ValueError as e: 
            print(f"{e}")


def handle_delete_habit(conn, tracker: HabitTracker) -> None:
    """
    Function that deletes a habit and all its data from the database.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker. 
    """
    print_header("Delete Habit")

    habit = select_habit_from_list(tracker)

    if habit is None:
        return

    confirm = get_valid_input(
        f"Are you sure you want to delete '{habit.name}'? Please note that once deleted it is not possible to restore it. (y/n) ",
        ["y", "n"]
    )

    if confirm == "y":
        tracker.remove_habit(habit.name)
        result = st.delete_habit(conn, habit.name)
        if result: 
            print(f"The habit: '{habit.name}' was permanently deleted.")
        else: 
            print(f"The habit '{habit.name}' was deleted from the session but could not be deleted from the database and it may reappear on restart.")
    else:
        print("Deletion cancelled.")


def handle_pause_resume(conn, tracker: HabitTracker) -> None:
    """
    Function that allows the user to pause, and resume his/hers habits. 

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
        is_sample: boolean indication if the habit is a sample or not. 
    """
    print_header("Pause / Resume Habit")

    habit = select_habit_from_list(tracker)
    if habit is None:
        return
    
    if not habit.habit_has_started:
        print(f"\n'{habit.name}' has not started yet.")
        print(f"Start date: {habit.start_date}")
        print(f"\nTo start tracking this habit please update its start date with option 8 (Modify a habit).")
        return

    if habit._manually_paused or not habit.is_active:
        confirm = get_valid_input(
            f"\nResume '{habit.name}'? (y/n): ",
            ["y", "n"]
        )
        if confirm == "n":
            print("No changes made.")
            return

        habit.reactivate_habit()
        print(f"\n'{habit.name}' resumed.")

        if not habit.is_active:
            # auto-paused due to abandonment threshold
            grace_days = int((habit.PERIOD_DAYS / 2) + 2)
            max_days_back = habit.PERIOD_DAYS + grace_days

            print(f"\nDespite being manually resumed, the habit '{habit.name}' is currently inactive.")
            print(f"This habit was automatically paused because no completion was recorded for more than {max_days_back} days.")
            print(f"\nTo reactivate it, please record a completion using option 4 (Complete a habit) from the main menu.")
        else: None

        if not habit.name.startswith("[Sample]"):
            st.save_habit(conn, habit)
        else:
            print("Sample Habit, the change will not be permanently stored.")


    else:
        confirm = get_valid_input(
            f"\nPause '{habit.name}'? (y/n): ",
            ["y", "n"]
        )
        if confirm == "n":
            print("No changes made.")
            return

        habit.deactivate_habit()
        print(f"\n'{habit.name}' paused.")

        if not habit.name.startswith("[Sample]"):
            st.save_habit(conn, habit)
        else:
            print("Sample Habit, the change will not be permanently stored.")


def handle_analytics(tracker: HabitTracker) -> None:
    """
    Function that creates a submenu with the different analysis position.

    Arguments: 
        tracker: the HabitTracker.
    """
    while True: 
        print_header("Analytics")

        # options dict — label and action defined together
        options = {
            "1": ("  Habits by Frequency",          lambda: _show_by_frequency(tracker)),
            "2": ("  Longest Streak",               lambda: _show_longest_streak(tracker)),
            "3": ("  Struggling Habits",            lambda: _show_struggling(tracker)),
            "4": ("  Most Consistent Habit",        lambda: _show_most_consistent(tracker)),
            "5": ("  Completion Time Analysis",     lambda: _show_time_analysis(tracker)),
            "6": ("  Oldest Habit",                 lambda: _show_oldest_habit(tracker)),
            "7": ("  Newest Habit",                 lambda: _show_newest_habit(tracker)),
            "8": ("  Never Completed Habits",       lambda: _show_never_completed(tracker)),
            "9": ("  Completion Rate by Frequency", lambda: _show_rate_by_frequency(tracker)),
            "10": (" Completions for a Date",       lambda: _show_completions_for_date(tracker)),
            "0": ("  Back to main menu",           lambda: None)
        }

        for key, (label, _) in options.items():
            print(f"  {key}. {label}")

        choice = get_valid_input(
            "\n  Choose option (0-10): ",
            list(options.keys())
        )

        if choice == "0":
            break

        clear_screen()
        _, action = options[choice]
        action()

        input("\n  Press Enter to continue...")
        clear_screen()


def handle_modify_habit(conn, tracker: HabitTracker) -> None:
    """
    Function that allows the user to modify the habits allowed fields (description and start date if the habit has no completions yet).

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
        is_sample: boolean indication if the habit is a sample or not.
    """
    print_header("Modify Habit")

    habit = select_habit_from_list(tracker)

    if habit is None:
        return

    # show current values
    print(f"\n  Current values:")
    print(f"    Description : {habit.description or 'None'}")
    print(f"    Start date  : {habit.start_date}")
    if habit.completions:
        print(f"\n Start date cannot be changed since the habit has already been started.")

    print("\n  What would you like to modify?")
    print("  1. Description")

    # only show start date option if no completions
    if not habit.completions:
        print("  2. Start date")
        print("  3. Back")
        valid = ["1", "2", "3"]
    else:
        print("  2. Back")
        valid = ["1", "2"]

    choice = get_valid_input("\n  Choose option: ", valid)

    # back option differs depending on whether start date is shown
    back_option = "3" if not habit.completions else "2"

    if choice == back_option:
        return

    elif choice == "1":
        new_desc = input(
            f"\nNew description (Enter to clear): "
        ).strip()
        habit.description = new_desc if new_desc else None

        try:
            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
                print(f"\nDescription updated.")
            else:
                print(f"\nDescription updated.")
                print("Sample Habit, the change will not be permanently stored.")

        except Exception as e:
            print(f"\nCould not save: {e}")

    elif choice == "2" and not habit.completions:
        new_date = get_valid_date(
            "\nNew start date (YYYY-MM-DD): ",
            allow_empty = False, reject_past = True)

        try:
            habit.start_date = new_date

            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
                print(f"\nStart date updated to {new_date} and saved.")
            else:
                print(f"\nStart date updated to {new_date}.")
                print("\nSample Habit, the change will not be permanently stored.")

        except ValueError as e:
            print(f"\n{e}")


# --- Main Loop Definition ---

def main() -> None:
    """
    Main entry point. Handles startup, the interactive menu loop, and shutdown.
    """
    clear_screen()
    print_header("Welcome to Habit Tracker")

    conn, tracker, is_sample = startup()

    # main menu options — same dispatch pattern as analytics
    menu_options = {
        "1":  ("  View all habits",           lambda: handle_view_habits(tracker)),
        "2":  ("  View habit details",        lambda: handle_view_habit_details(tracker)),
        "3":  ("  Add a new habit",           lambda: handle_add_habit(conn, tracker, is_sample)),
        "4":  ("  Complete a habit",          lambda: handle_complete_habit(conn, tracker)),
        "5":  ("  Record late completion",    lambda: handle_complete_late(conn, tracker)),
        "6":  ("  Add a note",                lambda: handle_add_note(conn, tracker)),
        "7":  ("  Pause / Resume habit",      lambda: handle_pause_resume(conn, tracker)),
        "8":  ("  Modify a habit",            lambda: handle_modify_habit(conn, tracker)),
        "9":  ("  Delete a habit",            lambda: handle_delete_habit(conn, tracker)),
        "10": (" Analytics",                  lambda: handle_analytics(tracker)),
        "0":  ("  Exit",                       None)
    }

    while True:
        print_header("Main Menu")

        if is_sample: 
            print("Sample data is not stored permanently. Real habits added will be saved.")

        for key, (label, _) in menu_options.items():
            print(f"  {key}. {label}")

        choice = get_valid_input(
            "\n  Choose option (0-10): ",
            list(menu_options.keys())
        )

        clear_screen()

        if choice == "0":
            shutdown(conn, tracker, is_sample)
            break

        _, action = menu_options[choice]
        action()

        input("\n  Press Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main()