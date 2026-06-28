#Shouldthis be the CLI layer? If so add here not a date catch and habit completion information

# main.py — coordinates both layers:
def handle_remove_habit(tracker, conn, name):
    if tracker.remove_habit(name):        # 1. remove from memory
        delete_habit_from_db(conn, name)  # 2. remove from database
        print(f"'{name}' removed.")
    else:
        print(f"No habit named '{name}' found.")

# main.py
def handle_delete_habit(tracker: HabitTracker, conn: sqlite3.Connection, name: str) -> bool:
    """
    Remove a habit from both memory and database in one operation.
    This is the function the CLI calls — user only needs to trigger this once.
    """
    if tracker.remove_habit(name):           # 1. remove from memory
        delete_habit_from_db(conn, name)     # 2. remove from database
        return True
    return False

from storage.database import init_db, load_habits, save_all_habits, delete_habit
from models.tracker import HabitTracker

# startup
conn = init_db("habits.db")
tracker = load_habits(conn)

if not tracker.habits:
    from storage.sample_data import create_sample_habits
    for habit in create_sample_habits():
        tracker.add_habit(habit)
    save_all_habits(conn, tracker)

# ... program runs ...

# shutdown
save_all_habits(conn, tracker)
conn.close()