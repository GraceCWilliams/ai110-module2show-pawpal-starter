# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🛠️ Implementation Summary

The scheduling logic lives in `pawpal_system.py` and is built from four classes:

- **`Task`** is one care activity, such as a walk or a feeding. It stores a start time, duration, priority (low, medium or high), frequency (once, daily or weekly), due date and whether it's done. It checks its own values when created, and `mark_complete()` marks it done and returns the next occurrence if the task repeats.
- **`Pet`** holds a list of tasks. `add_task()` adds a task and tags it with the pet's name, so the task can be traced back to its pet later.
- **`Owner`** holds a list of pets and the number of minutes available for pet care each day. `get_all_tasks()` gathers the tasks from every pet into one list.
- **`Scheduler`** takes an owner and does the planning. `generate_daily_plan()` collects the unfinished tasks due that day, picks them by priority (earliest first when priorities tie) until the owner's time runs out, and returns the chosen tasks in time order along with any skipped tasks and the reason each was skipped. It can also filter tasks, flag overlapping times, and add the next occurrence of a repeating task to its pet once the current one is completed.

The classes form a chain: an `Owner` has `Pet`s, each `Pet` has `Task`s, and the `Scheduler` works through the `Owner` to reach every task. `main.py` builds a sample owner, pets and tasks and prints the resulting plan, shown below.

## 🖥️ Sample Output

Output from running `python main.py`, which creates an owner with two pets (Biscuit the dog and Fluffy the cat), adds four tasks out of time order, and prints the generated plan:

```
====================================================
             Today's Schedule for Grace
====================================================
Time  | Task         | Pet     | Duration | Priority
------+--------------+---------+----------+---------
07:30 | Morning walk | Biscuit | 30 min   | high
08:00 | Breakfast    | Fluffy  | 10 min   | high
12:00 | Brush fur    | Fluffy  | 15 min   | low
18:00 | Evening walk | Biscuit | 30 min   | high
----------------------------------------------------
Total: 85 of 90 min used
```

The tasks are sorted by start time, and all four fit within Grace's 90-minute daily budget, so none were skipped and no time conflicts were reported.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

All of these features live in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.generate_daily_plan()` | By start time; the planner picks by priority, then time |
| Filtering | `Scheduler.filter_tasks()`, `Scheduler.get_tasks_for_date()` | By pet, by completion status, or by due date |
| Conflict handling | `Scheduler.detect_conflicts()` | Same start time or overlapping durations, on the same day |
| Recurring tasks | `Task.mark_complete()`, `Scheduler.mark_task_complete()` | Daily repeats the next day, weekly repeats a week later |

### Sorting

- **`Scheduler.sort_by_time(tasks)`** returns a new list ordered by start time, earliest first. It sorts on `Task.start_minutes()`, which turns the `"HH:MM"` time into minutes since midnight, so the times are compared as numbers rather than text.
- **`Scheduler.generate_daily_plan()`** sorts in two steps. First it orders candidate tasks by priority (high, then medium, then low), breaking ties by earlier start time, to decide which tasks fit in the owner's time. Then it sorts the chosen tasks by time so the plan reads like a day's timeline.

### Filtering

- **`Scheduler.filter_tasks(pet_name=None, completed=None)`** filters all of the owner's tasks by pet, by completion status, or by both. A filter left as `None` is skipped:
  ```python
  scheduler.filter_tasks(completed=False)                    # all unfinished tasks
  scheduler.filter_tasks(pet_name="Fluffy")                  # all of Fluffy's tasks
  scheduler.filter_tasks(pet_name="Biscuit", completed=False) # Biscuit's unfinished tasks
  ```
- **`Scheduler.get_tasks_for_date(day)`** returns the unfinished tasks due on a given day (today by default). The daily plan starts from this list.
- **`Scheduler.generate_daily_plan()`** also leaves out tasks that don't fit in the remaining time. It returns each skipped task with a reason, such as "needs 45 min, only 10 min left".

### Conflict detection

**`Scheduler.detect_conflicts(tasks)`** finds pairs of tasks on the same day whose times clash and returns one warning message per pair:

```
Same time: 'Breakfast' at 08:00 and 'Breakfast' at 08:00, different pets (Biscuit, Fluffy)
```

- **Same time vs. overlap:** It catches tasks that start at the same minute, and also tasks where one starts before the other ends (for example, a 30-minute walk at 08:00 and grooming at 08:20).
- **Same pet vs. different pets:** Each warning says which. Same pet means that pet is double-booked; different pets means the owner would need to be in two places at once.
- **Not counted as conflicts:** tasks that run back to back (one ends at 08:30, the next starts at 08:30) and tasks at the same time on different days.
- **How it works:** It sorts tasks by due date and then start time, so tasks that could clash end up next to each other. For each task it checks the tasks after it and stops as soon as one starts after the current task ends, so it doesn't compare every pair.
- **Warnings, not errors:** It returns messages instead of raising an exception, so a conflict never crashes the program. Both tasks stay in the plan, and the owner decides what to change. `main.py`, `app.py` and `Scheduler.explain_plan()` all show these warnings.

### Recurring tasks

- **`Task.mark_complete()`** marks a task done. If the task's frequency is `"daily"` or `"weekly"`, it returns a copy of the task that isn't done yet and has the next due date. For a `"once"` task it returns `None`.
- **`Scheduler.mark_task_complete(task)`** calls `Task.mark_complete()` and adds the new copy to the right pet, so the next occurrence shows up automatically. Call this method rather than `Task.mark_complete()` directly, or the new copy won't be added to the pet.
- **Next due date:** It's calculated with `timedelta` (`timedelta(days=1)` for daily, `timedelta(weeks=1)` for weekly), which handles month and year boundaries. It counts from today, or from the task's due date if the task was finished early:

  | Case | Was due | Next due |
  |---|---|---|
  | Daily, done on time (Oct 5) | Oct 5 | Oct 6 |
  | Weekly, done on time (Oct 5) | Oct 5 | Oct 12 |
  | Daily, done 3 days late (Oct 5) | Oct 2 | Oct 6 |
  | Daily, done a day early (Oct 5) | Oct 6 | Oct 7 |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
