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

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | | e.g., by priority, duration |
| Filtering | | e.g., skip tasks if time runs out |
| Conflict handling | | e.g., overlapping time slots |
| Recurring tasks | | e.g., daily vs. weekly |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
