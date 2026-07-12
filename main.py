import os
import Storage.habit_database as st
import Analytics.habit_analyse as an
from datetime import datetime, date
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
    status = "Active" if habit.is_active else "Paused"
    started = "Started" if habit.habit_has_started else "Not started yet"
    print(f"  {habit.name}")
    print(f"    Frequency      : {habit.frequency.value}")
    print(f"    Status         : {status} ({started})")
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
    Function that displays habits that do not have any completion.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Never Completed Habits")
    never = an.get_habits_never_completed(tracker.habits)
    if never:
        for h in never:
            print(f"→ {h.name} (started {h.start_date})")
    else:
        print("All habits have been completed at least once!")


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
        status = "Active" if habit.is_active else "Paused"
        print(f"    {i}. {habit.name} ({habit.frequency.value}, {status})")

    print(f"    0. Cancel")

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

    name = input("Habit name: ").strip()
    if not name:
        print("Name cannot be empty.")
        return
    
    if name.startswith("[Sample]"):
        print("Habit names cannot start with '[Sample]', this is reserved for demonstration habits.")
        return

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

    start_input = input("Start date (YYYY-MM-DD, press Enter for today): ").strip()
    if start_input:
        try:
            start_date = date.fromisoformat(start_input)

            """
            if start_date < date.today():
                print("Start date cannot be in the past — using today's date.")
                start_date = None
            """
        except ValueError:
            print("Invalid date format — using today's date.")
            start_date = None
    else:
        start_date = None

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

def handle_view_habit_details(conn, tracker: HabitTracker) -> None:
    """
    Function that displays all the information on a chosen habit.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Habit Details")

    habit = select_habit_from_list(tracker)
    if habit is None:
        return

    status = "Active" if habit.is_active else "Paused"
    started = "Started" if habit.habit_has_started else "Not started yet"
    print(f"\n ══ {habit.name} ══")
    print(f"\nGeneral")
    print(f"Frequency    : {habit.frequency.value}")
    print(f"Status       : {status} ({started})")
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

    if habit.notes:
        print(f"\nNotes")
        for note_date, note_text in sorted(habit.notes.items()):
            print(f"    {note_date}: {note_text}")
    else:
        print(f"\nNotes: None")


def handle_complete_habit(conn, tracker: HabitTracker, is_sample: bool) -> None:
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
        print(f"The habit '{habit.name}' has not started yet (starts {habit.start_date}).")
        return
    
    try:
        result = habit.check_habit_completion(datetime.now())

        if result:
            print(f"'Habit {habit.name}' marked complete for today!")
            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
            else: 
                print("Sample Habit, the completion will not be permanently stored.")
        else:
            print(f"Habit '{habit.name}' was already completed today.")

    except ValueError as e:
        print(f"\n{e}")

def handle_add_note(conn, tracker: HabitTracker, is_sample: bool) -> None:
    """
    Function to allow the user to add a note to a specific date. 

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
        is_sample: boolean indication if the habit is a sample or not. 
    """
    print_header("Add Note")

    habit = select_habit_from_list(tracker)

    if habit is None:
        return

    date_input = input("Date for note (YYYY-MM-DD, Enter for today): ").strip()
    if date_input:
        try:
            note_date = date.fromisoformat(date_input)
        except ValueError:
            print("Invalid date format.")
            return
    else:
        note_date = date.today()

    note = input("Note: ").strip()

    try:
        result = habit.add_note(note_date, note)
        if result:
            print(f"Note added for the {note_date} completion.")
            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
            else: 
                print("Sample Habit, the note will not be permanently stored.")
        else:
            print(f"Could not add note — date may be outside grace period.")
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


def handle_pause_resume(conn, tracker: HabitTracker, is_sample: bool) -> None:
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
    
    current_state = "paused" if habit._manually_paused else "active"
    print(f"\n  '{habit.name}' is currently {current_state}.")

    if habit._manually_paused:
        confirm = get_valid_input(
            f"Resume '{habit.name}'? (y/n): ",
            ["y", "n"]
        )
        if confirm == "n":
            print("No changes made.")
            return

        habit.reactivate_habit()
        print(f"\nThe habit '{habit.name}' was resumed.")

    else:
        confirm = get_valid_input(
            f"Pause '{habit.name}'? (y/n): ",
            ["y", "n"]
        )
        if confirm == "n":
            print("No changes made.")
            return

        habit.deactivate_habit()
        print(f"\n The habit '{habit.name}' was paused.")

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
    print_header("Analytics")

    # options dict — label and action defined together
    options = {
        "1": ("Habits by Frequency",          lambda: _show_by_frequency(tracker)),
        "2": ("Longest Streak",               lambda: _show_longest_streak(tracker)),
        "3": ("Struggling Habits",            lambda: _show_struggling(tracker)),
        "4": ("Most Consistent Habit",        lambda: _show_most_consistent(tracker)),
        "5": ("Completion Time Analysis",     lambda: _show_time_analysis(tracker)),
        "6": ("Oldest Habit",                 lambda: _show_oldest_habit(tracker)),      # ← new
        "7": ("Newest Habit",                 lambda: _show_newest_habit(tracker)),      # ← new
        "8": ("Never Completed Habits",       lambda: _show_never_completed(tracker)),   # ← new
        "9": ("Completion Rate by Frequency", lambda: _show_rate_by_frequency(tracker)), # ← new
        "10": ("Back to main menu",           lambda: None)
    }

    for key, (label, _) in options.items():
        print(f"  {key}. {label}")

    choice = get_valid_input(
        "\n  Choose option (1-10): ",
        list(options.keys())
    )

    _, action = options[choice]
    action()


def handle_modify_habit(conn, tracker: HabitTracker, is_sample) -> None:
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
        date_input = input(
            "\nNew start date (YYYY-MM-DD): "
        ).strip()
        try:
            new_date = date.fromisoformat(date_input)
            if new_date < date.today():
                print(f"\nStart date cannot be in the past.")
                return
            habit.start_date = new_date
            
            if not habit.name.startswith("[Sample]"):
                st.save_habit(conn, habit)
                print(f"Start date updated to {new_date} and saved.")
            else:
                print(f"\nStart date updated to {new_date}.")
                print("Sample Habit, the change will not be permanently stored.")

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
        "1": (" View all habits",       lambda: handle_view_habits(tracker)),
        "2": (" View habit details",    lambda: handle_view_habit_details(conn, tracker)),
        "3": (" Add a new habit",       lambda: handle_add_habit(conn, tracker, is_sample)),
        "4": (" Complete a habit",      lambda: handle_complete_habit(conn, tracker, is_sample)),
        "5": (" Add a note",            lambda: handle_add_note(conn, tracker, is_sample)),
        "6": (" Pause / Resume habit",  lambda: handle_pause_resume(conn, tracker, is_sample)),
        "7": (" Modify a habit",        lambda: handle_modify_habit(conn, tracker, is_sample)),
        "8": (" Delete a habit",        lambda: handle_delete_habit(conn, tracker)),
        "9": (" Analytics",             lambda: handle_analytics(tracker)),
        "10": ("Exit",                  None)
    }

    while True:
        print_header("Main Menu")

        if is_sample: 
            print("Sample data is not stored permanently. Real habits added will be saved.")

        for key, (label, _) in menu_options.items():
            print(f"  {key}. {label}")

        choice = get_valid_input(
            "\n  Choose option (1-10): ",
            list(menu_options.keys())
        )

        clear_screen()

        if choice == "10":
            shutdown(conn, tracker, is_sample)
            break

        _, action = menu_options[choice]
        action()

        input("\n  Press Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main()