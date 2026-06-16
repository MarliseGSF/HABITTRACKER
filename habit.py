from datetime import date
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
        self.start_date = begn_date or date.today()
        self.created_date = date.today()
        self._description = descp
        self._frequency = freq 
        self.completions: list[date] = []
        self.is_active: bool = True
        self.notes: dict[date, str] = {}

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
            raise ValueError("")
        
        self._start_date = value

#############################################################################################################################################################

    def __str__(self) -> str:
        return f"{self.name} ({self.frequency.value})"
    
    def __repr__(self) -> str:
        return f"Habit(name={self.name!r}, frequency={self.frequency})"
    
    @property
    def description(self) -> str | None: 
        return self._description
    
    @description.setter
    def description(self, value: str | None) -> None: 
        if value is not None and not isinstance(value, str):
            raise TypeError("description must be a string or None")
        self._description = value
    
    
    
    def check_habit_completion(self, 
                               check_date: date = None) -> bool: 
        """Function to mark habit has having been completed during the defined timefram."""

        if not isinstance(check_date, date):
            raise TypeError(f"Wrong check_date format. Must be date, got {type(entry_date).__name__}")

        if check_date is None: check_date = date.today()

        if check_date in self.completions:
            return False

        self.completions.append(check_date)
        return True

    def add_note(self,
                 note_date: date,
                 note: str) -> None:
        """Function to allow the user to add notes to the habit. It can be used to add justifications for missing completion."""
    
        if not isinstance(note_date, date):
            raise TypeError("entry_date must be a date")
        
        self.notes[note_date] = note
    





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
#Staging no git 
#Ligação à base de dados 
#Separar em classes, database operations, UI, etc
#Criar a command-line interface 
#clarify whether additional user interaction tools might be needed in the future
#Plan for unit tests using unittest or pytest
#Create dummy data 
#Check requirements folder for more 

obj = Habit("foo", freq=Frequency.DAILY)
dobj = DailyHabit("foo")

