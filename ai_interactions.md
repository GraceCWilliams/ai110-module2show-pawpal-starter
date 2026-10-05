# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

<!-- Describe the goal you asked the agent to accomplish -->

**What did the agent do?**

<!-- List the steps the agent took (files edited, commands run, etc.) -->

**What did you have to verify or fix manually?**

<!-- Describe anything the agent got wrong or that required human review -->

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

I compared two prompting strategies for the same task, writing pytest tests for `pawpal_system.py`: an **open-ended prompt** versus a **specific, single-behavior prompt**. Both were sent to the same tool, one right after the other, in the same chat session.

| | Option A: open-ended prompt | Option B: specific prompt |
|-|----------|----------|
| **Model / tool used** | Claude Code in VS Code (Claude Opus 5.5) | Claude Code in VS Code (Claude Opus 5.5) |
| **Prompt** | "Create a file named tests/test_pawpal.py" | "add a simple test to Verify that adding a task to a Pet increases that pet's task count." |
| **Response summary** | Created the `tests/` folder with **15 tests**. They covered task validation, recurring tasks, `add_task` tagging, owner lookups, sorting, filtering and conflicts. It also added a `pytest.ini` config file, ran the suite, and reported that all 15 passed. | Added **one test**, `test_add_task_increases_task_count`. It checks the pet's task count at 0, then 1, then 2 as tasks are added. The AI ran the suite and explained why the test checks the count after each add. |
| **What was useful** | Fast, broad coverage. It showed me which behaviors could be tested, and every test passed. | Exactly what I asked for. The test was short enough to read and fully understand, and the explanation taught me why checking a value before and after an action matters. |
| **Problems noticed** | Far more than I asked for. I hadn't decided what to test yet, and I didn't understand all 15 tests. It also added a config file I didn't want. When I asked for only my two tests, it removed the extra tests but kept `pytest.ini` until I asked a second time. | Because the 15 tests from Option A were still in the file, the new test was added alongside them ("All 17 tests now pass"). A specific prompt alone didn't undo the earlier overreach. It also only covers one behavior, so I needed several prompts to build a suite. |
| **Decision** | Rejected. I had the AI cut the file down to only the tests I asked for, and delete `pytest.ini`, so the setup is just `tests/test_pawpal.py` run with `python -m pytest`. | Adopted. I kept this test and the similar `mark_complete()` test as my first two tests, and used specific prompts for the rest of the project. |

**Which approach did you use in your final implementation and why?**

I used specific prompts. With the open-ended prompt, the AI decided what my tests should be, and I ended up with code I hadn't reviewed and a config file I didn't need. With the specific prompt, I decided what to test and could check every line of the result. When I later built the full suite, I combined the two approaches. First I asked the AI for a list of core behaviors to verify, then for a test plan I could review, and only then asked it to draft the tests from that plan. That gave me broad coverage, with 22 tests, while I still knew what each test checked and why. It worked because I made the decisions before any code was written.
