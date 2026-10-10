# Habit Tracker - OOFPP DLBDSOOFPP

Application for habit tracking, built using Python, to demonstrate Object-Oriented and Functional Programming uses. It allows the user to create, deleted, and modify several habits that may have different tracking frequencies /requirements and to analyse his/her adherence to those habits throught time. 

The focus of this project is on the backend so the User Experience is managed in the command-line.

---
### Key Features

- Create habits with four frequency types (daily, twice-weekly, weekly, bi-weekly)
- Record completions with exact timestamps for time-of-day analytics
- Allow the user a grace period for recording both late completions and notes
- Auto-pause detection for abandoned habits
- Analytics dashboard with streak analysis, completion rates, and time-of-day patterns
- Persistent storage using SQLite 
- Pre-loaded sample data for demonstration purposes


## Project Structure

```
HabitTracker/
│
├── Models/
│   ├── habit.py              # Habit base class + child classes + Frequency enum
│   └── habit_management.py   # HabitTracker collection manager
│
├── Analytics/
│   └── habit_analyse.py      # Functional analysis functions
│
├── Storage/
│   ├── habit_database.py     # SQLite persistence layer
│   └── sample_data.py        # Pre-defined sample habits
│
├── Tests/
│   ├── conftest.py           # Shared test fixtures
│   ├── test_habit.py         # Tests for Habit class
│   ├── test_tracker.py       # Tests for HabitTracker
│   ├── test_analytics.py     # Tests for analytics functions
│   ├── test_database.py      # Tests for database layer
│   └── test_sample_data.py   # Tests for sample data integrity
│
├── database/
│   └── habits.db             # SQLite database (created automatically)
│
├── main.py                   # Entry point — interactive CLI
├── requirements.txt          # Project dependencies
└── README.md                 # This file
```


## Installation

### Prerequisites
- Python 3.2.10
- pip

### Steps

1. Clone or download the project:
```bash
git clone https://github.com/MarliseGSF/HABITTRACKER.git
cd HabitTracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

The database and sample data are created automatically on 
first run — no additional setup needed.


## Usage

Run the application:
```bash
python main.py
```

On first launch, six sample habits are loaded automatically 
for demonstration. Sample data is **not** permanently saved and will be deleted once the user starts using the real data. If the user deletes its habits the same sample habit will reappear. 

### Main Menu Options

```
1.  View all habits
2.  View habit details
3.  Add a new habit
4.  Complete a habit
5.  Record late completion
6.  Add a note
7.  Pause / Resume habit
8.  Modify a habit
9.  Delete a habit
10. Analytics
11. Exit
```

       
### Habit Frequencies

| Type | Description | Period |
|---|---|---|
| Daily | Once per day | 1 day, 1 required |
| Twice Weekly | Twice per week | 7 days, 2 required |
| Weekly | Once per week | 7 days, 1 required |
| Bi-weekly | Once every two weeks | 14 days, 1 required |

### Grace Period

Each frequency has a grace period for recording late 
completions and notes:

```
Grace period = (PERIOD_DAYS / 2) + 2 days
```

| Frequency | Grace Period |
|---|---|
| Daily | 2.5 days |
| Twice Weekly | 5.5 days |
| Weekly | 5.5 days |
| Bi-weekly | 9 days |

---

## Analytics

Available through option 10 in the main menu:

```
1.  Habits by Frequency
2.  Longest Streak 
3.  Struggling Habits
4.  Most Consistent Habit 
5.  Completion Time Analysis
6.  Oldest Habit 
7.  Newest Habit 
8.  Never Completed Habit
9.  Completion Rate by Frequency
10. Completions for a Date
11. Exit
```  
    
## Database Schema

Data is stored in a SQLite database (`database/habits.db`) 
with three tables:

### `habits`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-generated primary key |
| `name` | TEXT | Unique habit name |
| `frequency` | TEXT | Frequency value (e.g. "daily") |
| `start_date` | DATE | When tracking begins |
| `created_date` | DATE | When habit was created |
| `description` | TEXT | Optional description |
| `is_paused` | INTEGER | 0 = active, 1 = paused |

### `completions`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-generated primary key |
| `habit_id` | INTEGER | Foreign key → habits.id |
| `completion_dt` | DATETIME | Full datetime of completion |

### `notes`
| Column | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-generated primary key |
| `habit_id` | INTEGER | Foreign key → habits.id |
| `note_date` | DATE | Date the note refers to |
| `note` | TEXT | Note content |


## Running Tests

Run all tests:
```bash
python -m pytest Tests/ -v
```

Run a specific test file:
```bash
python -m pytest Tests/test_habit.py -v
```

Tests use a separate `database/test_habits.db` that is 
created and deleted automatically — the real data is 
never affected.


## Sample Data

Six pre-defined habits demonstrate all frequency types 
and completion patterns:

| Habit | Type | Pattern |
|---|---|---|
| [Sample] Exercise | Daily | Strong streak, a few missed days |
| [Sample] Drink Water | Daily | Perfect streak, never missed |
| [Sample] Gym | Twice Weekly | Inconsistent — some weeks good |
| [Sample] Review Finances | Weekly | Mostly consistent |
| [Sample] Meditation | Bi-weekly | Struggling, manually paused |
| [Sample] Journaling | Daily | Abandoned — auto-paused |

Sample data is loaded into memory only and never saved 
to the database. It reloads fresh each session until 
real habits are created.