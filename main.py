from pawpal_system import Task, Pet, Owner, Scheduler


def main() -> None:
    owner = Owner(name="Grace", available_minutes=90)

    biscuit = Pet(name="Biscuit", species="dog", age=3)
    fluffy = Pet(name="Fluffy", species="cat", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(fluffy)

    # Added out of order on purpose so the schedule shows sorting by time.
    biscuit.add_task(Task("Evening walk", "18:00", duration_minutes=30, priority="high", frequency="daily"))
    biscuit.add_task(Task("Morning walk", "07:30", duration_minutes=30, priority="high", frequency="daily"))
    fluffy.add_task(Task("Breakfast", "08:00", duration_minutes=10, priority="high", frequency="daily"))
    fluffy.add_task(Task("Brush fur", "12:00", duration_minutes=15, priority="low", frequency="weekly"))

    scheduler = Scheduler(owner)
    scheduled, skipped = scheduler.generate_daily_plan()

    headers = ["Time", "Task", "Pet", "Duration", "Priority"]
    rows = [
        [t.time, t.description, t.pet_name, f"{t.duration_minutes} min", t.priority]
        for t in scheduled
    ]
    # Size each column to its longest value so names of any length line up.
    widths = [max(len(row[i]) for row in [headers, *rows]) for i in range(len(headers))]
    line_width = sum(widths) + 3 * (len(widths) - 1)

    def format_row(row: list[str]) -> str:
        return " | ".join(cell.ljust(w) for cell, w in zip(row, widths))

    print("=" * line_width)
    print(f"Today's Schedule for {owner.name}".center(line_width))
    print("=" * line_width)
    print(format_row(headers))
    print("-+-".join("-" * w for w in widths))
    for row in rows:
        print(format_row(row))
    print("-" * line_width)

    for task, reason in skipped:
        print(f"Skipped: {task.description} ({task.pet_name}) — {reason}")
    for warning in scheduler.detect_conflicts(scheduled):
        print(f"Warning: {warning}")
    used = sum(t.duration_minutes for t in scheduled)
    print(f"Total: {used} of {owner.available_minutes} min used")


if __name__ == "__main__":
    main()
