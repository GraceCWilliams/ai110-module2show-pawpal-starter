# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Before drafting the UML, I identified three core actions a user should be able to perform in PawPal+:

1. **Enter owner and pet information.** The user sets up a basic profile: the owner's name and how much time they have for pet care each day, plus the pet's name, species or breed, and any special needs. The scheduler needs this context to know whose plan it is building and what time limit it has to work within.

2. **Add and edit care tasks.** The user creates the care tasks their pet needs, such as walks, feeding, medication, enrichment, or grooming. Each task has at least a duration and a priority level. A task can also have a preferred time of day or say how often it repeats. The user can update or remove tasks as their routine changes.

3. **Generate and view today's plan.** The user asks the app to build a daily schedule. The app orders tasks by priority, fits them into the owner's available time, and leaves out or flags any task that doesn't fit. It then shows the plan in time order with a short explanation of why each task was placed where it was.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes. My draft (`diagrams/uml.mmd`) had the same four classes as the final design (`diagrams/uml_final.mmd`): `Owner`, `Pet`, `Task` and `Scheduler`. But `Task` started as plain data: a title, duration, priority, preferred time and frequency. In the final version, `Task` gained a required start `time`, a `due_date`, a `completed` flag and a `pet_name`, plus methods of its own. I made this change because the scheduling features needed more information about each task. Sorting and conflict detection need an exact start time, not just a preference. Recurring tasks need a due date, so that completing a daily walk can create tomorrow's walk with `mark_complete()`.

The biggest change was adding `pet_name` to `Task`. In my draft, tasks were only reachable by going from an owner to a pet to its tasks. But `Scheduler` works with one flat list of every task, and when a repeating task is completed, the scheduler has to know which pet to add the next occurrence to. `Pet.add_task()` now tags each task with the pet's name, and the scheduler uses `owner.get_pet(task.pet_name)` to find the pet. I also left out features from my draft that I didn't need yet: a pet's breed and special needs, and the owner's preferences.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers five things:

1. **Available time:** the owner's `available_minutes` for the day. The plan never goes over this.
2. **Priority:** high, medium or low.
3. **Start time:** used to put the plan in order and to find conflicts.
4. **Due date:** only tasks due today are planned. Daily and weekly tasks get new due dates when they're completed.
5. **Completion:** finished tasks are left out.

I decided that available time and priority mattered most. Available time is a hard limit, because an owner can't spend more time than they have. Priority decides what to drop when time runs out. Missing a dose of medicine or a meal is worse than skipping a grooming session, so `generate_daily_plan()` picks tasks from highest to lowest priority and only uses start time to break ties. Start time matters for how the plan reads and for spotting clashes, but I didn't let it decide which tasks get done. Owner preferences were in my first design, but I left them out to keep the scheduler simple and testable.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler detects time conflicts but doesn't resolve them. When it builds the daily plan, it chooses tasks by priority and the owner's total available minutes. It doesn't check whether a task's time slot is already taken. After the plan is built, `detect_conflicts()` looks for tasks on the same day whose times overlap. That includes tasks that start at the same time and tasks where one starts before the other ends. It returns a warning message for each pair, such as "Same time: 'Breakfast' at 08:00 and 'Breakfast' at 08:00, different pets (Biscuit, Fluffy)." The program keeps running, and both tasks stay in the plan. The scheduler doesn't move one of them to a free slot or drop it.

I think this tradeoff is reasonable for a pet owner. Some conflicts aren't real problems. For example, feeding two pets at 08:00 is something one person can usually do together. If the scheduler moved or removed a task by itself, it could push a meal or a dose of medicine to a time the owner didn't choose. Warning the owner leaves the decision with the person who knows their pets and routine. Warnings are also simple to build and test: the check is one sorted pass over the plan, and it can't crash the program. The downside is that the owner has to read the warnings and fix conflicts themselves. A future version could suggest the next free time slot instead of only reporting the problem.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code as a coding assistant inside VS Code. I asked it to write `main.py` as a demo script that creates an owner, two pets and several tasks and then prints today's schedule. I also asked it to clean up how the schedule looked in the terminal, set up two simple pytests, and to add docstrings to the methods in `pawpal_system.py`.

The most helpful prompts were short, specific requests that named the file and the exact behavior I wanted, such as "add a simple test to verify that adding a task to a Pet increases that pet's task count." When a request was more open-ended, like "create a file named tests/test_pawpal.py," the AI filled in much more than I requested.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When I asked the AI to create `tests/test_pawpal.py`, it wrote 15 tests covering every class and also added a `pytest.ini` config file. The tests passed, but I hadn't asked for them, and I wanted to build up my tests step by step so I understood each one. I had it cut the file down to the two simple tests I had actually asked for: one checking that `mark_complete()` changes a task's status, and one checking that `add_task()` increases a pet's task count. I also rejected the `pytest.ini` file. I wanted the setup to be just the test file, run with `python -m pytest`. The AI explained that `python -m pytest` already lets the tests import `pawpal_system`, so the config file wasn't needed, and it removed the file.

I accepted the terminal formatting change, but only after checking the output myself. The AI's first version of `main.py` lined up the columns with fixed widths, and after I renamed the pets to Biscuit and Fluffy, the "Biscuit" rows no longer lined up. The AI switched to columns that size themselves to the longest value and added a header row, and I confirmed the new table lined up by running `main.py` again.

To verify the AI's work, I ran the code instead of trusting its description of it. I ran `python main.py` after each change to the demo script, ran `python -m pytest` after each change to the tests or to `pawpal_system.py`, and checked `git status` to make sure only the files I wanted were being added. I also read each test to make sure it checked a value both before and after the action, so it couldn't pass by accident.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?
- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
- How did using separate chat sessions for different phases help you stay organized?
- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.

The most effective feature was that Claude Code could run code, not just write it. After each change it ran `python -m pytest` and `python main.py` and showed me the output, so I could see right away whether something worked. It also tested the Streamlit app without a browser, which caught a real bug: the "Mark complete" dropdown was handing back a copy of a task, so the copy was marked done instead of the real one. A second useful feature was pointing it at specific files with `@app.py` and `@pawpal_system.py`. Its suggestions were then based on my actual code. For example, it noticed that `explain_plan()` rebuilt the whole plan a second time, and that missed tasks dropped out of later plans.

One suggestion I modified was how to handle conflicts. Early on, the AI gave me a list of improvements that included automatically moving a conflicting task to the next free time slot, splitting the owner's time into availability windows, and using a knapsack algorithm to fill leftover minutes. I didn't take those. I kept conflicts as warnings, so the scheduler never moves a pet's meal or medicine without the owner deciding. Later, when the AI offered four ways to simplify the scheduling code, I only accepted one: using `Task.start_minutes` as the single sort key everywhere. The others were small changes that would have made the code harder for me to follow without a real benefit.

[Fill in from your own experience: which phases you split into separate chat sessions (for example, design, implementation, testing, and documentation), and how that helped, such as each chat staying focused on one goal, or starting a new chat when you moved from writing code to writing tests.]

What I learned about being the "lead architect" is that the AI is fast and capable, but it doesn't know what I want unless I decide and say so. When my requests were vague, it added more than I asked for, like 15 tests and a config file. When I was specific, it did exactly that. My job was to decide what the system should do, choose between the options it gave me, and check its work by running the code and reading it, not by trusting its summary. It also helped when the AI pushed back. When I asked it to document an "exact time match" tradeoff, it pointed out that my scheduler actually checks overlapping times, so writing that would have been wrong. I learned to treat it like a strong teammate whose work I review, not an authority that makes the design decisions.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

My test suite in `tests/test_pawpal.py` has 22 tests that cover six areas:

1. **Basics:** `mark_complete()` marks a task done, and `add_task()` adds a task to a pet.
2. **Sorting:** tasks added out of order come back in time order.
3. **Filtering:** by pet, by completion status, or both.
4. **Recurring tasks:** daily tasks repeat the next day, weekly tasks repeat in 7 days, one-time tasks don't repeat, and overdue tasks repeat from today.
5. **Conflict detection:** same-time and overlapping tasks are flagged, while back-to-back tasks and tasks on different days are not.
6. **The daily plan:** it stays within the time budget, keeps high-priority tasks, is in time order, and leaves out finished and future tasks.

These tests were important because the scheduling logic has many small rules that are easy to break without noticing. Examples include whether a task ending at 08:30 clashes with one starting at 08:30, or whether a daily task completed three days late comes back with a date in the past. Testing the edge cases, and not just the normal case, gave me confidence that the scheduler does what I described in the README.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'm fairly confident, about 4 out of 5. All 22 tests pass, and they check exact values like the order of times and the next due date, so they can't pass by accident. I also checked the app and `main.py` by running them. It isn't a 5 because I know of a few gaps. Completing the same repeating task twice adds two copies of the next occurrence. A task that was never completed doesn't carry over to the next day's plan, because the plan only looks at tasks due on that exact day. The Streamlit app is also only checked by hand.

If I had more time, I would test these edge cases next:

- Completing the same recurring task twice.
- A task late at night that runs past midnight, such as 23:50 for 30 minutes.
- An owner with no pets, or pets with no tasks.
- Two tasks that fit the time budget exactly, with 0 minutes left over.
- Completing a weekly task near the end of a month or year.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how conflicts are handled from start to finish. The `Scheduler` finds overlapping tasks with a simple sorted check. The tests cover the tricky cases, like back-to-back tasks and tasks on different days. The Streamlit app turns each conflict into a plain-language warning with a suggested new time, while still leaving the decision to the owner. It's one feature that goes through every layer of the project: the logic, the tests and the user interface.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

First, I would fix the gaps I found while testing. Unfinished tasks should carry over to the next day instead of disappearing, and completing a task twice shouldn't create duplicate copies. Next, I would let the owner edit and delete tasks in the app. `Pet.remove_task()` exists, but the app has no button for it. Finally, I would replace the single "available minutes" number with time windows, such as 7–9am and 5–8pm. Then the scheduler could place tasks in times the owner is actually free, and suggest a free slot instead of only warning about conflicts.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

My key takeaway is that a clear design makes AI help much more useful. Because my classes had clear jobs (`Pet` holds tasks, `Owner` holds pets, and `Scheduler` does the planning), I could ask for one feature at a time, like sorting, filtering or recurrence, and know exactly where it belonged. When the AI suggested something that didn't fit that design, it was easy to see and say no. The AI wrote code quickly, but the decisions about what the system should do, and checking that it actually did it, were still mine.
