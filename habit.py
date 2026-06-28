from datetime import date, datetime
from enum import Enum
from typing import Optional
from collections import Counter

class Frequency(Enum):
    """
    Support class that defines the type of frequencies a habit can have.
    """

    DAILY = "daily"
    WEEKLY = "weekly"
    TWICEWEEKLY = "twice a week"
    BIWEEKLY = "bi-weekly"



class Habit:
    """
    Class that represents a habit with a name, frequency, and completion history.
    """
    
    PERIOD_DAYS: int = 1
    REQUIRED_PER_PERIOD: int = 1

    def __init__(self, 
                 name: str, 
                 freq: Frequency,
                 begn_date: Optional[date] = None, 
                 descp: Optional[str] = None
                 ):
        """
        Function that initializes a new habit

        Arguments: 
            name: the name of the habit, cannot be empty and cannot be changed once defined;
            freq: the frequency of the habit, must be DAILY, WEEKLY, TWICEWEEKLY or BIWEEKLY; cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if name is not a string or Frequency is not a Frequency(Enum) value.

        """
        if not name or not name.strip():
            raise ValueError("The Habit must have a name.")
        
        if not isinstance(name, str):
            raise TypeError("The habit name must be a string.")
        
        if not isinstance(freq, Frequency):
            raise TypeError("The habit must be daily, weekly, twice a week, or bi-weekly,")
        
        self._name = name
        self._frequency = freq
        self._start_date = begn_date or date.today()
        self._created_date = date.today()
        self.description = descp
        self._completions: list[datetime] = []
        self._manually_paused: bool = False
        self.notes: dict[date, str] = {}
        

    # --- Properties Definition ---


    @property #Blocks the name field from being altered. 
    def name(self) -> str: 
        return self._name
    
    
    @property #Blocks the frequency field from being altered. 
    def frequency(self) -> Frequency: 
        return self._frequency
    
    
    @property #Conditional block on the created_date field.
    def created_date(self) -> date: 
        return self._created_date
    

    @property #Conditional block on the start_date field.
    def start_date(self) -> date: 
        return self._start_date
    
    
    @start_date.setter
    def start_date(self, value: date) -> None: 
        """
        Function that allows the user to change the start date if habit has not been started yet. 

        Raises: 
            TypeError: if value is not a date.
            Value Error: if completions already exist. 
        """
        if not isinstance(value, date):
            raise TypeError("The value must be a date.")
        
        if self._completions:
            raise ValueError("The start date cannot be changed after completions have already been recorded.")
        
        self._start_date = value

    
    @property #Flag that verifies if an habit has started yet. 
    def habit_has_started(self) -> bool: 
        """
        A Habit has started if it is passed the start date, regardless of completions.
        """
        return date.today() >= self.start_date
    
    
    @property #Read-only block on the completion history in order to prevent changes.
    def completions(self) -> list[datetime]:
        return self._completions.copy()
    
    
    @property #Flag to check if a habit is active
    def is_active(self) -> bool:
        """
        Fuction that returns if a habit is active. 
        A habit is active if: 
            - it has already started;
            - has not been manually paused using the deactivate_habit function;
            - has not been abandoned. 
        A habit is considered abandoned if it has no completions for two times the length of its grace period. 
        """
        if not self.habit_has_started: 
            return False
        if self._manually_paused: 
            return False 
        if not self._completions: 
            return True #The habit is after the start date but does not have any completions yet

        last_completion = max(c.date() for c in self._completions)
        days_since = (date.today() - last_completion).days
        abandonment_threshold = 2 * ((self.PERIOD_DAYS / 2) + 2)
        return days_since <= abandonment_threshold
    
    
    @property
    def is_habit_completed_for_current_period(self) -> bool:
        """
        Function that defines if all the required completions per period have been satisfied.
        """
        if not self._completions:
            return False

        today = date.today()
        current_period_count = sum(
            1 for d in self._completions
            if (today - d.date()).days // self.PERIOD_DAYS == 0
        )
        return current_period_count >= self.REQUIRED_PER_PERIOD
    
    
# --- Helper Methods Definition ---

    def _grace_period(self, check_date: date) -> bool: 
        """
        Function defines a grace period for the user to mark the habit as complete or add notes to it. 

        Arguments: 
            check_date: date of the note or completion the user wants to check. 

        Raises:
            TypeError: if check_date is not a date.
        """
        if not isinstance(check_date, datetime):
            raise TypeError(f"The argument must be a date, got {type(check_date).__name__}")

        days_since = (date.today() - check_date).days
        grace_period = (self.PERIOD_DAYS / 2) + 2
        return days_since <= self.PERIOD_DAYS + grace_period
    

# --- Methods Definition ---

    def check_habit_completion(self, 
                               check_datetime: datetime = None) -> bool: 
        """
        Function to allow the user to mark the habit as completed. 

        Arguments: 
            check_datetime: date and time of the completion. The default value is the current time. 
        
        Returns: 
            True if there is a new completion for the habit time period; 
            False if the habit has already been checked for that time period.

        Raises: 
            TypeError: if the check_datetime is not a datetime. 
            ValueError: if check_datetime is before the habit's start_date or for a date in the future
        """
        if check_datetime is None: check_datetime = datetime.now()

        if not isinstance(check_datetime, date):
            raise TypeError(f"Wrong check_date format. Must be datetime, got {type(check_datetime).__name__}")
        
        if check_datetime.date() < self.start_date:
            raise ValueError("Cannot record a completion before the habit's start date")
        
        if check_datetime.date() > date.today():
            raise ValueError("Cannot record a completion in the future. ")

        # Only one completion per day so the comparison is done on a daily granularity. 
        already_checked = any(c.date() == check_datetime.date() for c in self._completions)
        
        if already_checked: return False

        self._completions.append(check_datetime)
        return True


    def late_complete(self, check_datetime: datetime) -> bool:
        """
        Function that allows the user to retroactively mark a missed date as complete, if still within 
        the grace period for this habit's frequency.

        Args:
            check_datetime: the missed date/time to mark as complete.

        Returns:
            True if successfully recorded, False if outside the grace period.

        Raises:
            TypeError: if check_datetime is not a datetime.
            ValueError: if the date chosen is in the future.
        """
        if not isinstance(check_datetime, datetime):
            raise TypeError(f"The argument must be a datetime, got {type(check_datetime).__name__}")
        
        if check_datetime.date() > date.today():
            raise ValueError("Cannot record a completion in the future. ")

        if self._grace_period(check_datetime.date()):
            return self.check_habit_completion(check_datetime)
        return False
    
        
    def add_note(self,
                note_date: datetime,
                note: str) -> bool:
        """
        Function to allow the user to add notes to the habit. It can be used to add justifications for missing completion.
        Only allows the note creation during a specific period.
        Only allows for one note per day or it will be overwritten.

        Arguments: 
            note_date: date to which the note refers to;
            note: string with the note's content.
        
        Returns:
        True if the note was recorded, False if outside the grace period.

        Raises:
            TypeError: if note_date is not a date, or note is not a string.
            ValueError: if note is empty or only whitespace or the note_date is before start_date, if note_date is in the future.
        """
        if not isinstance(note_date, date):
            raise TypeError(f"The argument must be a date, got {type(note_date).__name__}")
        
        if note_date.date() < self.start_date:
            raise ValueError("Cannot add a note before the habit's start date.")
        
        if note_date.date() > date.today():
            raise ValueError("Cannot add a note for a date in the future.")
        
        if not self._grace_period(note_date.date()):
            return False
        
        if not isinstance(note, str):
            raise TypeError("The note must be a string")
        
        if not note.strip():
            raise ValueError("The note cannot be empty")
        
        self.notes[note_date] = note
        return True
    

    def get_current_habit_streak(self) -> int:
        """
        Function that checks how many consecutive periods (counting back from today) 
        have at least one completion.

        Returns:
            The current streak length, in periods. 0 if no completions are recorded or if the habit has not started yet.
        """
        if not self._completions:
            return 0

        today = date.today()
        completion_dates = [c.date() for c in self._completions]  # strip time
        
        #Counts the number of completions that fall into each period
        period_counts = Counter(
            (today - d).days // self.PERIOD_DAYS for d in completion_dates
        )

        streak = 0
        period = 0
        while period_counts.get(period, 0) >= self.REQUIRED_PER_PERIOD:
            streak += 1
            period += 1

        return streak
    

    def get_longest_habit_streak(self) -> int:
        """
        Function that returns the longest streak of consecutive periods this habit has ever achieved.

        Returns:
            The longest streak length, in periods. 0 if no completions are recorded.
        """
        if not self._completions:
            return 0

        completion_dates = [c.date() for c in self._completions]

        # Count completions per period (relative to start_date)
        period_counts = Counter(
            (d - self.start_date).days // self.PERIOD_DAYS for d in completion_dates
        )

        # Only keep periods that met the requirement
        satisfied_periods = sorted(
            period for period, count in period_counts.items()
            if count >= self.REQUIRED_PER_PERIOD
        )

        if not satisfied_periods:
            return 0

        longest = 1
        current = 1

        for i in range(1, len(satisfied_periods)):
            if satisfied_periods[i] == satisfied_periods[i - 1] + 1:
                current += 1
                longest = max(longest, current)
            else:
                current = 1

        return longest
    
    
    def deactivate_habit(self) -> None:
        """
        Function to allow the user to deactivate an habit without deleting its history.
        """
        self._manually_paused = False


    def reactivate_habit(self) -> None:
        """
        Function to allow the user to reactivate an habit.
        """
        self._manually_paused = True



# --- Display Methods---

    def __str__(self) -> str:
        return f"{self.name} ({self.frequency.value})"
    

    def __repr__(self) -> str:
        return f"Habit(name={self.name!r}, frequency={self.frequency})"        


# --- Child Classes---

class DailyHabit(Habit):
    """
    Child Class that represents a habit that has to be completed daily.
    """

    PERIOD_DAYS = 1
    REQUIRED_PER_PERIOD = 1

    def __init__(self, name, begn_date=None, descp=None):
        """
        Function that initializes a new daily habit

        Arguments: 
            name: the name of the habit, cannot be empty and cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if Frequency is not a Frequency(Enum) value.
        """
        super().__init__(name, Frequency.DAILY, begn_date, descp)


class WeeklyHabit(Habit):
    """
    Child Class that represents a habit that has to be completed once a week.
    """

    PERIOD_DAYS = 7
    REQUIRED_PER_PERIOD = 1

    def __init__(self, name, begn_date=None, descp=None):
        """
        Function that initializes a new weekly habit

        Arguments: 
            name: the name of the habit, cannot be empty and cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if Frequency is not a Frequency(Enum) value.
        """
        super().__init__(name, Frequency.WEEKLY, begn_date, descp)



class TwiceWeeklyHabit(Habit):
    """
    Child Class that represents a habit that has to be completed twice every week.
    """

    PERIOD_DAYS = 7
    REQUIRED_PER_PERIOD = 2

    def __init__(self, name, begn_date=None, descp=None):
        """
        Function that initializes a new habit that needs to be completed twice a week

        Arguments: 
            name: the name of the habit, cannot be empty and cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if Frequency is not a Frequency(Enum) value.
        """
        super().__init__(name, Frequency.WEEKLY, begn_date, descp)



class BiWeeklyHabit(Habit):
    """
    Child Class that represents a habit that has to be completed twice every week.
    """

    PERIOD_DAYS = 14
    REQUIRED_PER_PERIOD = 1

    def __init__(self, name, begn_date=None, descp=None):
        """
        Function that initializes a new habit that needs to be completed once every two weeks.

        Arguments: 
            name: the name of the habit, cannot be empty and cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if Frequency is not a Frequency(Enum) value.
        """
        super().__init__(name, Frequency.WEEKLY, begn_date, descp)