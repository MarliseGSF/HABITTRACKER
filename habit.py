from datetime import date, datetime
from enum import Enum
from typing import Optional

class Frequency(Enum):
    """
    Support class that defines the type of frequencies a habit can have.
    """

    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "bi-weekly"


class Habit:
    """
    Class that represents a habit with a name, frequency, and completion history.
    """
    
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
            freq: the frequency of the habit, must be DAILY, WEEKLY or BIWEEKLY; cannot be changed once defined;
            begn_date: date when the user wants to start tracking the habit, optional argument, if not defined defaults to the date the habit was created, can only be changed if there were no checks yet; 
            descp: description of the habit, optional argument, can be changed at any time. 

        Raises: 
            ValueError: if name is empty or whitespace.
            TypeError: if Frequency is not a Frequency(Enum) value.

        """
        
        if not name or not name.strip():
            raise ValueError("The Habit must have a name.")
        
        if not isinstance(freq, Frequency):
            raise TypeError("The habit must be daily, weekly or bi-weekly")
        
        self._name = name
        self._frequency = freq
        self._start_date = begn_date or date.today()
        self._created_date = date.today()
        self.description = descp
        self.completions: list[date] = []
        self.is_active: bool = True
        self.notes: dict[date, str] = {}

    # --- Properties Definition ---

    @property #Blocks the name field from being altered. 
    def name(self) -> str: 
        return self._name
    
    @property #Blocks the frequency field from being altered. 
    def frequency(self) -> Frequency: 
        return self._frequency

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
        
        if self.completions:
            raise ValueError("The start date cannot be changed after completions have already been recorded.")
        
        self._start_date = value

    @property #Conditional block on the created_date field.
    def created_date(self) -> date: 
        return self._created_date
    
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
        """

        if check_datetime is None: check_datetime = datetime.now()

        if not isinstance(check_datetime, date):
            raise TypeError(f"Wrong check_date format. Must be datetime, got {type(check_datetime).__name__}")

        # Only one completion per day so the comparison is done on a daily granularity. 
        already_checked = any(c.date() == check_datetime.date() for c in self.completions)
        
        if already_checked: return False

        self.completions.append(check_datetime)
        return True
    
    def add_note(self,
                 note_date: date,
                 note: str) -> None:
        """
        Function to allow the user to add notes to the habit. It can be used to add justifications for missing completion.

        Arguments: 
            note_date: date to which the note refers to;
            note: string with the note's content.
        
        Raises: 
            TypeError: if note_date is not a date
        """
    
        if not isinstance(note_date, date):
            raise TypeError("The note must be associated with a correct date.")
        
        self.notes[note_date] = note

    def __str__(self) -> str:
        return f"{self.name} ({self.frequency.value})"
    
    def __repr__(self) -> str:
        return f"Habit(name={self.name!r}, frequency={self.frequency})"

   
   
   
   ################################################################################################################################################################ 
        


class DailyHabit(Habit):
    """Child Class that represents a daily habit"""

    def __init__(self, name):
        super().__init__(name = name,freq=Frequency.DAILY)


class DailyHabit(Habit):
    """Child Class that represents a weekly habit"""

    def __init__(self, name):
        super().__init__(name = name,freq=Frequency.WEEKLY)


class DailyHabit(Habit):
    """Child Class that represents a bi-weekly habit"""

    def __init__(self, name):
        super().__init__(name = name,freq=Frequency.BIWEEKLY)

#add date limitations for the notes and the check-ins can a user change the frequency on the same habit? 
#criar os métodos: check habit late habit (different for each habit, delete habit, analyse habit, modidy habit)
#Ligação à base de dados 
#Separar em classes, database operations, UI, etc
#Criar a command-line interface 
#clarify whether additional user interaction tools might be needed in the future
#Plan for unit tests using unittest or pytest
#Create dummy data 
#Check requirements folder for more 

obj = Habit("foo", freq=Frequency.DAILY)
dobj = DailyHabit("foo")

