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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
