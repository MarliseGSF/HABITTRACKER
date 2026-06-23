from habit import Frequency, Habit

class HabitTracker: 
    """
    Class that manages the Habit objects.
    """
    
    def __init__(self): 
        """
        Function that initializes the habit tracker with a list of habits.
        """

        self._habits: list[Habit] = []

    # --- Properties Definition ---

    @property
    def habits(self) -> list[Habit]:
        """
        Function that returns a read-only view of all the habits in the tracker.
        Prevents external code from modifying the habits and bypassing the validated methods. 

        Returns:
            A copy of the full list of Habit objects. Empty list if no 
            habits have been added yet.
        
        """
        return self._habits.copy()

"""
class HabitTracker:
    # --- Core methods ---

    def add_habit(self, habit: Habit) -> bool:
        
        Add a new habit to the tracker.

        Args:
            habit: the Habit object to add.

        Returns:
            True if successfully added.

        Raises:
            TypeError: if habit is not a Habit instance.
            ValueError: if a habit with the same name already exists.
        
        if not isinstance(habit, Habit):
            raise TypeError("habit must be a Habit instance")
        if any(h.name.lower() == habit.name.lower() for h in self._habits):
            raise ValueError(f"A habit named '{habit.name}' already exists")

        self._habits.append(habit)
        return True

    def get_habit_by_name(self, name: str) -> "Habit | None":
        
        Find a habit by name (case-insensitive).

        Args:
            name: the name to search for.

        Returns:
            The matching Habit, or None if not found.

        Raises:
            TypeError: if name is not a string.
        
        if not isinstance(name, str):
            raise TypeError("name must be a string")

        return next(
            (h for h in self._habits if h.name.lower() == name.lower()),
            None
        )

    def remove_habit(self, name: str) -> bool:
        
        Remove a habit from the tracker by name.

        Args:
            name: the name of the habit to remove.

        Returns:
            True if removed, False if not found.

        Raises:
            TypeError: if name is not a string.
        
        habit = self.get_habit_by_name(name)
        if habit:
            self._habits.remove(habit)
            return True
        return False

    # --- Filter methods ---

    def get_active_habits(self) -> list[Habit]:
        
        Return all habits that are currently active.

        Returns:
            List of active Habit objects. Empty list if none.
        
        return [h for h in self._habits if h.is_active]

    def get_inactive_habits(self) -> list[Habit]:
        
        Return all habits that are currently inactive.

        Returns:
            List of inactive Habit objects. Empty list if none.
        
        return [h for h in self._habits if not h.is_active]

    def get_by_frequency(self, frequency: Frequency) -> list[Habit]:
        
        Return all habits matching a given frequency.

        Args:
            frequency: the Frequency enum value to filter by.

        Returns:
            List of matching Habit objects. Empty list if none.

        Raises:
            TypeError: if frequency is not a Frequency enum value.
        
        if not isinstance(frequency, Frequency):
            raise TypeError("frequency must be a Frequency enum value")

        return [h for h in self._habits if h.frequency == frequency]

    # --- Display ---

    def __str__(self) -> str:
        if not self._habits:
            return "HabitTracker (no habits)"
        habit_names = ", ".join(h.name for h in self._habits)
        return f"HabitTracker ({len(self._habits)} habits: {habit_names})"

    def __repr__(self) -> str:
        return f"HabitTracker(habits={self._habits!r})"
"""
"""
tracker = HabitTracker()
exercise = DailyHabit("Exercise")
gym = TwiceWeeklyHabit("Gym")

tracker.add_habit(exercise)
tracker.add_habit(gym)
tracker.add_habit(DailyHabit("Exercise"))  # ❌ raises ValueError — duplicate name

print(tracker)                              # HabitTracker (2 habits: Exercise, Gym)
print(tracker.get_by_frequency(Frequency.DAILY))   # [Exercise]
print(tracker.get_active_habits())          # [Exercise, Gym]
print(tracker.get_habit_by_name("gym"))     # TwiceWeeklyHabit — case insensitive
print(tracker.remove_habit("Exercise"))     # True
print(tracker.remove_habit("Yoga"))         # False — doesn't exist
"""

"""
class HabitTracker:
    def __init__(self)
    def add_habit(self, habit)
    def remove_habit(self, habit)
    def get_all_habits(self)
    def get_by_frequency(self, frequency)
    def get_active_habits(self)
    def get_habit_by_name(self, name)
    def __str__
    def __repr__
"""