from pawpal_system import Task, Pet, Owner, Scheduler


def print_table(title: str, tasks: list[Task]) -> None:
    """Print tasks as an aligned table under a centered title."""
    headers = ["Time", "Task", "Pet", "Duration", "Priority", "Done"]
    rows = [
        [t.time, t.description, t.pet_name, f"{t.duration_minutes} min", t.priority,
         "yes" if t.completed else "no"]
        for t in tasks
    ]
    # Size each column to its longest value so names of any length line up.
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    line_width = sum(widths) + 3 * (len(widths) - 1)

    def format_row(row: list[str]) -> str:
        return " | ".join(cell.ljust(w) for cell, w in zip(row, widths))

    print()
    print("=" * line_width)
    print(title.center(line_width))
    print("=" * line_width)
    print(format_row(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(format_row(row))
    if not rows:
        print("(no tasks)")
    print("-" * line_width)


def main() -> None:
    owner = Owner(name="Grace", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="dog", age=3)
    fluffy = Pet(name="Fluffy", species="cat", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(fluffy)

    # Added out of order on purpose so the output shows sorting by time.
    biscuit.add_task(Task("Evening walk", "18:00", duration_minutes=30, priority="high", frequency="daily"))
    fluffy.add_task(Task("Vet appointment", "15:30", duration_minutes=45, priority="medium"))
    biscuit.add_task(Task("Morning walk", "07:30", duration_minutes=30, priority="high", frequency="daily"))
    fluffy.add_task(Task("Brush fur", "12:00", duration_minutes=15, priority="low", frequency="weekly"))
    biscuit.add_task(Task("Give medicine", "09:15", duration_minutes=5, priority="high"))
    fluffy.add_task(Task("Breakfast", "08:00", duration_minutes=10, priority="high", frequency="daily"))
    # Same time as Fluffy's breakfast on purpose so the conflict check has something to catch.
    biscuit.add_task(Task("Breakfast", "08:00", duration_minutes=10, priority="high", frequency="daily"))

    scheduler = Scheduler(owner)

    # Sorting
    print_table("All tasks (order added)", owner.get_all_tasks())
    print_table("All tasks (sorted by time)", scheduler.sort_by_time(owner.get_all_tasks()))

    # Complete a one-time task so the completion filter has something to show.
    medicine = next(t for t in biscuit.tasks if t.description == "Give medicine")
    scheduler.mark_task_complete(medicine)

    # Filtering
    print_table("Completed tasks", scheduler.filter_tasks(completed=True))
    print_table("Incomplete tasks (sorted)", scheduler.sort_by_time(scheduler.filter_tasks(completed=False)))
    print_table("Fluffy's tasks (sorted)", scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Fluffy")))
    print_table(
        "Biscuit's incomplete tasks (sorted)",
        scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit", completed=False)),
    )

    # Daily plan
    scheduled, skipped = scheduler.generate_daily_plan()
    print_table(f"Today's Schedule for {owner.name}", scheduled)
    for task, reason in skipped:
        print(f"Skipped: {task.description} ({task.pet_name}) — {reason}")
    used = sum(t.duration_minutes for t in scheduled)
    print(f"Total: {used} of {owner.available_minutes} min used")

    # Conflict check: warnings come back as strings, so the program keeps running.
    print()
    print("Conflict check:")
    conflicts = scheduler.detect_conflicts(scheduled)
    for warning in conflicts:
        print(f"  Warning: {warning}")
    if not conflicts:
        print("  No conflicts found.")


if __name__ == "__main__":
    main()
