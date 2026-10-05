"""Core logic for PawPal+: tasks, pets, owners, and the scheduler."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import date, time, timedelta

PRIORITY_RANK = {"high": 0, "medium": 1, "low": 2}
FREQUENCY_STEP = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet care activity."""

    description: str
    time: str  # "HH:MM", 24-hour clock
    duration_minutes: int = 15
    priority: str = "medium"  # "low" | "medium" | "high"
    frequency: str = "once"  # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)
    pet_name: str = ""  # filled in by Pet.add_task

    def __post_init__(self) -> None:
        """Validate the time, priority, frequency, and duration."""
        time.fromisoformat(self.time)  # raises ValueError on a bad time
        if self.priority not in PRIORITY_RANK:
            raise ValueError(f"priority must be one of {list(PRIORITY_RANK)}")
        if self.frequency not in ("once", *FREQUENCY_STEP):
            raise ValueError("frequency must be 'once', 'daily', or 'weekly'")
        if self.duration_minutes <= 0:
            raise ValueError("duration_minutes must be positive")

    def mark_complete(self) -> Task | None:
        """Mark this task done and return the next occurrence if it recurs.

        The next due date counts from today (e.g. daily -> today + 1 day),
        or from the original due date if the task was finished early.
        """
        self.completed = True
        step = FREQUENCY_STEP.get(self.frequency)
        if step is None:
            return None
        base = max(self.due_date, date.today())
        return replace(self, completed=False, due_date=base + step)

    def start_minutes(self) -> int:
        """Minutes since midnight when this task starts."""
        t = time.fromisoformat(self.time)
        return t.hour * 60 + t.minute

    def end_minutes(self) -> int:
        """Minutes since midnight when this task ends."""
        return self.start_minutes() + self.duration_minutes


@dataclass
class Pet:
    """A pet and the care tasks it needs."""

    name: str
    species: str
    age: int = 0
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet and tag it with the pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from this pet."""
        self.tasks.remove(task)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    available_minutes: int = 120  # time available for pet care per day
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return the pet with the given name, or None if there isn't one."""
        return next((p for p in self.pets if p.name == name), None)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """Retrieves, organizes, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner) -> None:
        """Create a scheduler for the given owner's pets and tasks."""
        self.owner = owner

    def get_tasks_for_date(self, day: date | None = None) -> list[Task]:
        """Incomplete tasks due on the given day (default: today)."""
        day = day or date.today()
        return [
            t for t in self.owner.get_all_tasks()
            if t.due_date == day and not t.completed
        ]

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return the tasks sorted by start time, earliest first.

        Sorts on minutes since midnight (Task.start_minutes), the same key
        detect_conflicts and generate_daily_plan use. Returns a new list;
        the original list isn't changed.
        """
        return sorted(tasks, key=Task.start_minutes)

    def filter_tasks(
        self, pet_name: str | None = None, completed: bool | None = None
    ) -> list[Task]:
        """Filter all tasks by pet name and/or completion status.

        A filter left as None is skipped, so filter_tasks() returns every
        task and filter_tasks(pet_name="Mochi", completed=False) returns
        Mochi's unfinished tasks. Order follows Owner.get_all_tasks.
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """Return a warning for each pair of tasks on the same day whose times overlap.

        Each warning says whether the tasks start at the same time or just
        overlap, and whether they're for the same pet or different pets.
        """
        warnings = []
        # Sort by day, then start time, so overlapping tasks end up next to each other.
        ordered = sorted(tasks, key=lambda t: (t.due_date, t.start_minutes()))
        for i, a in enumerate(ordered):
            for b in ordered[i + 1:]:
                # Every later task is on a later day or starts after `a` ends.
                if b.due_date != a.due_date or b.start_minutes() >= a.end_minutes():
                    break
                kind = "Same time" if a.time == b.time else "Overlap"
                who = (f"same pet ({a.pet_name})" if a.pet_name == b.pet_name
                       else f"different pets ({a.pet_name}, {b.pet_name})")
                warnings.append(
                    f"{kind}: '{a.description}' at {a.time} and "
                    f"'{b.description}' at {b.time}, {who}"
                )
        return warnings

    def mark_task_complete(self, task: Task) -> Task | None:
        """Complete a task; if it recurs, add the next occurrence to its pet.

        Task.mark_complete works out the next due date (daily: +1 day,
        weekly: +1 week). Returns the new task, or None for a one-time task.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            pet = self.owner.get_pet(task.pet_name)
            if pet is not None:
                pet.add_task(next_task)
        return next_task

    def generate_daily_plan(
        self, day: date | None = None
    ) -> tuple[list[Task], list[tuple[Task, str]]]:
        """Pick tasks for the day within the owner's available time.

        Tasks are chosen by priority (then earliest time) until the time
        budget runs out. Returns (scheduled tasks in time order, skipped
        tasks with the reason each was skipped).
        """
        candidates = sorted(
            self.get_tasks_for_date(day),
            key=lambda t: (PRIORITY_RANK[t.priority], t.start_minutes()),
        )
        remaining = self.owner.available_minutes
        scheduled, skipped = [], []
        for task in candidates:
            if task.duration_minutes <= remaining:
                scheduled.append(task)
                remaining -= task.duration_minutes
            else:
                skipped.append(
                    (task, f"needs {task.duration_minutes} min, only {remaining} min left")
                )
        return self.sort_by_time(scheduled), skipped

    def explain_plan(self, day: date | None = None) -> str:
        """Human-readable plan with reasoning and any conflict warnings."""
        scheduled, skipped = self.generate_daily_plan(day)
        lines = [f"Daily plan for {self.owner.name}:"]
        for t in scheduled:
            lines.append(
                f"  {t.time} — {t.description} for {t.pet_name} "
                f"({t.duration_minutes} min) [priority: {t.priority}]"
            )
        for t, reason in skipped:
            lines.append(f"  Skipped: {t.description} for {t.pet_name} — {reason}")
        for warning in self.detect_conflicts(scheduled):
            lines.append(f"  Warning: {warning}")
        used = sum(t.duration_minutes for t in scheduled)
        lines.append(f"Total: {used} of {self.owner.available_minutes} min used.")
        return "\n".join(lines)
