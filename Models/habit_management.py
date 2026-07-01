from Models.habit import Frequency, Habit

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
    
    
    # --- Methods Definition ---

    def create_new_habit(self, habit: Habit) -> bool:
        """
        Function to add a new habit to the tracker. 

        Arguments: 
            habit: Habit object to be created.

        Returns: 
            True if the habit was successfully created. 
            False if the habit was not created.

        Raises:
            TypeError: if habit is not a Habit instance.
            ValueError: if a habit with the same name already exists.
        """
        if not isinstance(habit, Habit):
            raise TypeError("The habit must be a Habit instance")
        if any(h.name.lower() == habit.name.lower() for h in self._habits):
            raise ValueError(f"A habit named '{habit.name}' already exists")

        self._habits.append(habit)
        return True
    
    
    def remove_habit(self, name: str) -> bool:
        """
        Function that deletes a habit from the habit tracker. 

        Arguments: 
            name: the name of the habit that will be removed. 

        Returns: 
            True if the habit was successfully removed, false if the habit is not found.

        Raises: 
            TypeError: if the name of the habit is not a string.
        """
        habit = self.find_habit_by_name(name)
        if habit:
            self._habits.remove(habit)
            return True
        return False
    

    # --- Filter Methods ---

    def find_habit_by_name(self, name: str) -> "Habit | None":
        """
        Functions that allows the user to fetch a tracked habit by its name. The function is not case sensitive. 

        Arguments: 
            name: recorded name of the habit being called on. 

        Returns: 
            If the corresponding habit exists, it will be fetched, if not it will return None. 

        Raises: 
            TypeError: if the name is not a string. 
        """
        if not isinstance(name, str):
            raise TypeError("The habit name must be a string")

        return next(
            (h for h in self._habits if h.name.lower() == name.lower()),
            None
        )
    

    def get_habits_from_status(self, active: bool = True) -> list[Habit]:
        """
        Function that allows the user to get a list of all the habits that match the status condition (if a habit is or not active). 

        Arguments: 
            active: if True indicates that the user wants to see active habits. 
                    if False indicates that the user wants a list of inactive habits. 
                    Defaults to True.

        Returns: List of habits that match the status requested. Empty list if no habit that matches that status is found. 

        Raises: 
            TypeError: if the active variable is not a boolean value.
        """
        if not isinstance(active, bool):
            raise TypeError("The habit status must be a boolean variable.")

        return [h for h in self._habits if h.is_active == active]
    

    def get_habits_by_frequency(self, frequency: Frequency) -> list[Habit]:
        """
        Function that allows the users to get all the habits that match a frequenct.

        Arguments: 
            frequency: the Frequency class that we want to filter on. 

        Returns: 
            List of all the habits that match the frequency chosen.
            If no habit matches the chosen frequency returns None. 

        Raises: 
            TypeError: if frequency is not a Frequency enum value 
        """
        if not isinstance(frequency, Frequency):
            raise TypeError("The frequency must belong to the Frequency(Enum) Class.")

        return [h for h in self._habits if h.frequency == frequency]
    

    # --- Display ---

    def __str__(self) -> str:
        if not self._habits:
            return "HabitTracker (no habits)"
        habit_names = ", ".join(h.name for h in self._habits)
        return f"HabitTracker ({len(self._habits)} habits: {habit_names})"
    

    def __repr__(self) -> str:
        return f"HabitTracker(habits={self._habits!r})"
