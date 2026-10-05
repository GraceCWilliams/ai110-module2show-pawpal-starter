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

## ✨ Features

- **Sorting by time:** Tasks are ordered by start time, earliest first, by turning each `"HH:MM"` time into minutes since midnight. (`Scheduler.sort_by_time()`)
- **Priority-first daily planning:** The planner goes through today's tasks from high to low priority, with earlier tasks first when priorities tie. It adds each task that still fits in the owner's available minutes, then shows the chosen tasks in time order. (`Scheduler.generate_daily_plan()`)
- **Skipped-task reasons:** Tasks that don't fit in the remaining time are listed with the reason, such as "needs 45 min, only 10 min left". (`Scheduler.generate_daily_plan()`)
- **Filtering by pet and status:** Tasks can be narrowed to one pet, to finished or unfinished tasks, or both. (`Scheduler.filter_tasks()`)
- **Due-date filtering:** The daily plan only considers unfinished tasks due that day. (`Scheduler.get_tasks_for_date()`)
- **Conflict warnings:** Tasks on the same day whose times overlap are flagged, whether they start at the same minute or one starts before the other ends. Each warning says whether it's the same pet or different pets. Tasks are sorted first, so each task is only compared with the tasks right after it. Conflicts produce warnings, not errors, so the program keeps running. (`Scheduler.find_conflicts()`, `Scheduler.detect_conflicts()`)
- **Suggested fixes in the app:** The Streamlit app shows each conflict in plain words, marks the clashing tasks in the table, and suggests moving the later task to when the earlier one ends. (`app.py`)
- **Daily and weekly recurrence:** Completing a daily or weekly task automatically adds the next occurrence to the same pet, using `timedelta` for the date math. The next date counts from today, so an overdue task doesn't come back with a date in the past. (`Task.mark_complete()`, `Scheduler.mark_task_complete()`)
- **Plan explanation:** The plan can be printed as plain text, with each task, every skipped task and its reason, conflict warnings and the total time used. (`Scheduler.explain_plan()`)
- **Input validation:** A task with an invalid time, priority, frequency or duration is rejected when it's created, so bad data never reaches the scheduler. (`Task.__post_init__()`)

See [Smarter Scheduling](#-smarter-scheduling) below for more detail and examples.

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

Run the tests from the project folder:

```bash
python -m pytest
```

The tests are in `tests/test_pawpal.py` and cover the scheduling logic in `pawpal_system.py`:

- **Basics:** `mark_complete()` marks a task done, and `add_task()` adds a task to a pet.
- **Sorting:** tasks added out of order come back in time order, tasks at the same time are kept, and the original list isn't changed.
- **Filtering:** tasks can be filtered by pet, by completion status, by both, or not at all.
- **Recurring tasks:** a daily task repeats the next day, a weekly task repeats 7 days later, a one-time task doesn't repeat, and an overdue task repeats from today rather than from its old due date.
- **Conflict detection:** tasks at the same time and overlapping tasks are flagged, with the right "same pet" or "different pets" wording. Back-to-back tasks and same-time tasks on different days are not flagged.
- **Daily plan:** the plan stays within the owner's available minutes, keeps high-priority tasks over low ones when time is short, is in time order, and leaves out completed tasks and tasks due on other days.

Output of a successful run:

```
============================= test session starts ==============================
platform darwin -- Python 3.14.7, pytest-9.1.1, pluggy-1.6.0
rootdir: /Users/grace_computer/Library/Mobile Documents/com~apple~CloudDocs/AI110/ai110-module2show-pawpal-starter
plugins: anyio-4.15.1
collected 22 items

tests/test_pawpal.py ......................                              [100%]

============================== 22 passed in 0.02s ==============================
```

### Confidence Level: ★★★★☆ (4/5)

All 22 tests pass, and they cover each scheduling feature, including edge cases like back-to-back tasks, overdue recurring tasks and tasks due on other days. The tests check exact values, such as the order of times or the next due date, so they can't pass by accident.

It isn't 5 stars because some things aren't tested or aren't handled yet:

- The Streamlit app (`app.py`) is only checked by hand, not by automated tests.
- Completing the same recurring task twice adds two copies of the next occurrence.
- An overdue task that was never completed doesn't show up in later daily plans, because the plan only includes tasks due on that exact day.
- The planner warns about conflicts but doesn't move tasks to fix them.

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

PawPal+ can be used two ways: the Streamlit app (`streamlit run app.py`) for interactive planning, and the demo script (`python main.py`) that prints sample results to the terminal.

### Main UI features

The app is one page, from top to bottom:

| Section | What the user can do |
|---|---|
| **Owner** | Set the owner's name and how many minutes they have for pet care today (default 120). |
| **Add a Pet** | Enter a pet's name, species (dog, cat or other) and age, then click **Add pet**. Empty or duplicate names show an error. A table lists each pet and how many tasks it has. |
| **Schedule a Task** | Choose a pet and enter a task title, start time, duration, priority (low, medium or high) and frequency (once, daily or weekly), then click **Add task**. |
| **Tasks** | See tasks sorted by time, and filter them by pet (**Show pet**) and status (**Unfinished**, **Completed** or **All**). Tasks in a time clash are marked ⚠️ Conflict, with a warning and a suggested new time below the table. Choose a task under **Task to complete** and click **Mark complete**; a daily or weekly task then comes back for its next occurrence. |
| **Build Schedule** | Click **Generate schedule** to see today's plan: summary numbers (tasks planned, minutes used, tasks skipped, conflicts), a progress bar for time used, the plan in time order, a "Didn't fit today" table with reasons, and a **Plan explanation** in plain text. |

### Example workflow

1. **Set up the owner.** Leave the name as Jordan and the available time at 120 minutes.
2. **Add two pets.** Add Mochi, then change the name to Biscuit and add again. The pet table shows both with 0 tasks.
3. **Schedule two tasks at the same time.** For Mochi, add "Breakfast" at 08:00, 20 minutes, high priority, daily. Then switch the pet to Biscuit and add the same task. Both rows in the Tasks table are marked ⚠️ Conflict, and a warning appears right away:
   > **Today: Breakfast (Mochi, 08:00–08:20) overlaps Breakfast (Biscuit, 08:00)**
   > You'd be caring for Mochi and Biscuit at the same time. **Suggestion:** move Biscuit's Breakfast to 08:20, when Mochi's Breakfast ends. If you can do both together (like feeding two pets), you can ignore this.
4. **Add a task that's too long.** For Biscuit, add "Long walk" at 10:00 for 200 minutes. It appears in the table in time order, after the two breakfasts.
5. **Filter the list.** Set **Show pet** to Biscuit to see only Biscuit's tasks, or set **Show** to Completed to see finished ones.
6. **View today's schedule.** Click **Generate schedule**. The summary shows 2 planned, 40 / 120 minutes used, 1 skipped and 1 conflict. Both breakfasts are in the plan, and "Long walk" is under "Didn't fit today" with the reason "needs 200 min, only 80 min left".
7. **Complete a task.** Choose Mochi's Breakfast under **Task to complete** and click **Mark complete**. The app shows "Completed 'Breakfast' for Mochi. Next daily occurrence: Tomorrow." With **Show** set to All, today's breakfast is marked ✅ Done and a new one is due Tomorrow. The conflict warning goes away, because Mochi's breakfast is no longer on today's list.

### Key Scheduler behaviors shown

- **Sorting by time:** Tasks are always listed earliest first, however they were added. (`Scheduler.sort_by_time()`)
- **Filtering:** The **Show pet** and **Show** controls, and the filtered tables in `main.py`. (`Scheduler.filter_tasks()`)
- **Priority-first planning within a time budget:** The plan keeps high-priority tasks and skips what doesn't fit, with a reason for each. (`Scheduler.generate_daily_plan()`)
- **Conflict warnings:** Same-time and overlapping tasks are flagged as warnings, not errors, with a suggested new time in the app. (`Scheduler.find_conflicts()`, `Scheduler.detect_conflicts()`)
- **Daily and weekly recurrence:** Completing a repeating task adds its next occurrence automatically. (`Scheduler.mark_task_complete()`)

### Sample CLI output

`main.py` creates an owner (Grace, 90 minutes) with two pets, Biscuit the dog and Fluffy the cat. It adds seven tasks out of time order, including two breakfasts at 08:00, and marks "Give medicine" complete. It then prints the tasks as added, sorted by time, and filtered several ways, followed by today's schedule and a conflict check.

```bash
python main.py
```

```

==============================================================
                   All tasks (order added)
==============================================================
Time  | Task            | Pet     | Duration | Priority | Done
------+-----------------+---------+----------+----------+-----
18:00 | Evening walk    | Biscuit | 30 min   | high     | no
07:30 | Morning walk    | Biscuit | 30 min   | high     | no
09:15 | Give medicine   | Biscuit | 5 min    | high     | no
08:00 | Breakfast       | Biscuit | 10 min   | high     | no
15:30 | Vet appointment | Fluffy  | 45 min   | medium   | no
12:00 | Brush fur       | Fluffy  | 15 min   | low      | no
08:00 | Breakfast       | Fluffy  | 10 min   | high     | no
--------------------------------------------------------------

==============================================================
                  All tasks (sorted by time)
==============================================================
Time  | Task            | Pet     | Duration | Priority | Done
------+-----------------+---------+----------+----------+-----
07:30 | Morning walk    | Biscuit | 30 min   | high     | no
08:00 | Breakfast       | Biscuit | 10 min   | high     | no
08:00 | Breakfast       | Fluffy  | 10 min   | high     | no
09:15 | Give medicine   | Biscuit | 5 min    | high     | no
12:00 | Brush fur       | Fluffy  | 15 min   | low      | no
15:30 | Vet appointment | Fluffy  | 45 min   | medium   | no
18:00 | Evening walk    | Biscuit | 30 min   | high     | no
--------------------------------------------------------------

============================================================
                      Completed tasks
============================================================
Time  | Task          | Pet     | Duration | Priority | Done
------+---------------+---------+----------+----------+-----
09:15 | Give medicine | Biscuit | 5 min    | high     | yes
------------------------------------------------------------

==============================================================
                  Incomplete tasks (sorted)
==============================================================
Time  | Task            | Pet     | Duration | Priority | Done
------+-----------------+---------+----------+----------+-----
07:30 | Morning walk    | Biscuit | 30 min   | high     | no
08:00 | Breakfast       | Biscuit | 10 min   | high     | no
08:00 | Breakfast       | Fluffy  | 10 min   | high     | no
12:00 | Brush fur       | Fluffy  | 15 min   | low      | no
15:30 | Vet appointment | Fluffy  | 45 min   | medium   | no
18:00 | Evening walk    | Biscuit | 30 min   | high     | no
--------------------------------------------------------------

=============================================================
                   Fluffy's tasks (sorted)
=============================================================
Time  | Task            | Pet    | Duration | Priority | Done
------+-----------------+--------+----------+----------+-----
08:00 | Breakfast       | Fluffy | 10 min   | high     | no
12:00 | Brush fur       | Fluffy | 15 min   | low      | no
15:30 | Vet appointment | Fluffy | 45 min   | medium   | no
-------------------------------------------------------------

===========================================================
            Biscuit's incomplete tasks (sorted)
===========================================================
Time  | Task         | Pet     | Duration | Priority | Done
------+--------------+---------+----------+----------+-----
07:30 | Morning walk | Biscuit | 30 min   | high     | no
08:00 | Breakfast    | Biscuit | 10 min   | high     | no
18:00 | Evening walk | Biscuit | 30 min   | high     | no
-----------------------------------------------------------

===========================================================
                 Today's Schedule for Grace
===========================================================
Time  | Task         | Pet     | Duration | Priority | Done
------+--------------+---------+----------+----------+-----
07:30 | Morning walk | Biscuit | 30 min   | high     | no
08:00 | Breakfast    | Biscuit | 10 min   | high     | no
08:00 | Breakfast    | Fluffy  | 10 min   | high     | no
18:00 | Evening walk | Biscuit | 30 min   | high     | no
-----------------------------------------------------------
Skipped: Vet appointment (Fluffy) — needs 45 min, only 10 min left
Skipped: Brush fur (Fluffy) — needs 15 min, only 10 min left
Total: 80 of 90 min used

Conflict check:
  Warning: Same time: 'Breakfast' at 08:00 and 'Breakfast' at 08:00, different pets (Biscuit, Fluffy)
```

What the output shows:
- **Sorting:** The "sorted by time" table puts the tasks in order from 07:30 to 18:00.
- **Filtering:** "Completed tasks" shows only Give medicine, and the per-pet tables show only that pet's tasks.
- **Planning:** The schedule fits 80 of Grace's 90 minutes. The vet appointment and fur brushing are skipped because they're lower priority and don't fit in the 10 minutes left.
- **Conflict warning:** The two 08:00 breakfasts are flagged, and the program still finishes normally.

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
