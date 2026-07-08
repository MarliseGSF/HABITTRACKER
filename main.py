import os
import Storage.habit_database as st
import Analytics.habit_analyse as an
from datetime import datetime, date
from Storage.sample_data import create_sample_habits
from Models.habit import DailyHabit, WeeklyHabit, BiWeeklyHabit, TwiceWeeklyHabit, Frequency
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

        input("  Press Enter to continue...")
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

        print("\n  ─────────────────────────────────────────────")
        print("  SESSION SUMMARY")
        print("  ─────────────────────────────────────────────")

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
            print("\n No real habits were added this session.")
            print("  Sample data will reload on your next visit.")

        print("  ─────────────────────────────────────────────")

    else:
        # normal session — save everything
        saved = st.save_all_habits(conn, tracker)
        if saved:
            print(f"\n {len(tracker.habits)} habit(s) saved successfully.")
        else:
            print("\n Some habits may not have saved correctly.")

    conn.close()
    print("\n End of Session Goodbye!\n")


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
        habits = HabitTracker.get_habits_by_frequency(tracker.habits, freq)
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
        print(f"{best.name} → {best.get_longest_streak()} periods")
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
            print(f"  → {h.name} (best streak: {h.get_longest_streak()} periods)")
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
        print(f"The habit {best.name} is the one being achieved most consistently.")
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
    print(f"Overall most common time: {analysis['overall'] or 'No data'}\n")
    print("Per habit:")
    for habit_name, bracket in analysis["per_habit"].items():
        print(f"    {habit_name} → {bracket or 'No data'}")


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


def handle_add_habit(conn, tracker: HabitTracker) -> None:
    """
    Function that guides the user through creating a new habit.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracke to be added.
    """
    print_header("Add New Habit")

    name = input("Habit name: ").strip()
    if not name:
        print("Name cannot be empty.")
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
        except ValueError:
            print("Invalid date format — using today.")
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

    except ValueError as e:
        print(f"Could not add habit: {e}")


def handle_complete_habit(conn, tracker: HabitTracker) -> None:
    """
    Function that marks the habit has having been completed.

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Complete a Habit")

    name = input("Habit name: ").strip()
    habit = tracker.find_habit_by_name(name)

    if habit is None:
        print(f"No habit named '{name}' was found.")
        return

    if not habit.habit_has_started:
        print(f"The habit '{name}' has not started yet (starts {habit.start_date}).")
        return

    result = habit.check_habit_completion(datetime.now())

    if result:
        print(f"'Habit {name}' marked complete for today!")
        st.save_habit(conn, habit)
    else:
        print(f"Habit '{name}' was already completed today.")


def handle_add_note(conn, tracker: HabitTracker) -> None:
    """
    Function to allow the user to add a note to a specific date. 

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Add Note")

    name = input("Habit name: ").strip()
    habit = tracker.find_habit_by_name(name)

    if habit is None:
        print(f"No habit named '{name}' was found.")
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
            st.save_habit(conn, habit)
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

    name = input("Habit name to delete: ").strip()
    habit = tracker.find_habit_by_name(name)

    if habit is None:
        print(f"No habit named '{name}' was found.")
        return

    confirm = get_valid_input(
        f"Are you sure you want to delete '{name}'? Please note that once deleted it is not possible to restore it. (y/n) ",
        ["y", "n"]
    )

    if confirm == "y":
        tracker.remove_habit(name)
        result = st.delete_habit(conn, name)
        if result: 
            print(f"The habit: '{name}' was permanently deleted.")
        else: 
            print(f"The habit '{name}' was deleted from the session but could not be deleted from the database and it may reappear on restart.")
    else:
        print("Deletion cancelled.")


def handle_pause_resume(conn, tracker: HabitTracker) -> None:
    """
    Function that allows the user to pause, and resume his/hers habits. 

    Arguments: 
        conn: open database connection.
        tracker: the HabitTracker.
    """
    print_header("Pause / Resume Habit")

    name = input("Habit name: ").strip()
    habit = tracker.find_habit_by_name(name)

    if habit is None:
        print(f"No habit named '{name}' was found.")
        return

    if habit._manually_paused:
        habit.reactivate()
        print(f"The habit '{name}' was resumed.")
    else:
        habit.deactivate()
        print(f"The habit'{name}' was paused.")

    st.save_habit(conn, habit)


def handle_analytics(tracker: HabitTracker) -> None:
    """
    Function that creates a submenu with the different analysis position.

    Arguments: 
        tracker: the HabitTracker.
    """
    print_header("Analytics")

    # options dict — label and action defined together
    options = {
        "1": ("Habits by Frequency",     lambda: _show_by_frequency(tracker)),
        "2": ("Longest Streak",           lambda: _show_longest_streak(tracker)),
        "3": ("Struggling Habits",        lambda: _show_struggling(tracker)),
        "4": ("Most Consistent Habit",    lambda: _show_most_consistent(tracker)),
        "5": ("Completion Time Analysis", lambda: _show_time_analysis(tracker)),
        "6": ("Back to main menu",        lambda: None)
    }

    for key, (label, _) in options.items():
        print(f"  {key}. {label}")

    choice = get_valid_input(
        "\n  Choose option (1-6): ",
        list(options.keys())
    )

    _, action = options[choice]
    action()


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
        "1": ("View all habits",       lambda: handle_view_habits(tracker)),
        "2": ("Add a new habit",       lambda: handle_add_habit(conn, tracker)),
        "3": ("Complete a habit",      lambda: handle_complete_habit(conn, tracker)),
        "4": ("Add a note",            lambda: handle_add_note(conn, tracker)),
        "5": ("Pause / Resume habit",  lambda: handle_pause_resume(conn, tracker)),
        "6": ("Delete a habit",        lambda: handle_delete_habit(conn, tracker)),
        "7": ("Analytics",             lambda: handle_analytics(tracker)),
        "8": ("Exit",                  None)
    }

    while True:
        print_header("Main Menu")

        if is_sample: 
            print("Sample data is not stored permanently. Real habits added will be saved.")

        for key, (label, _) in menu_options.items():
            print(f"  {key}. {label}")

        choice = get_valid_input(
            "\n  Choose option (1-8): ",
            list(menu_options.keys())
        )

        clear_screen()

        if choice == "8":
            shutdown(conn, tracker)
            break

        _, action = menu_options[choice]
        action()

        input("\n  Press Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main()