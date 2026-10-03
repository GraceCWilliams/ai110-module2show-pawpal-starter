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

    print("=" * 50)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 50)
    for task in scheduled:
        print(
            f"{task.time}  {task.description:<14} {task.pet_name:<6} "
            f"{task.duration_minutes:>3} min  [{task.priority}]"
        )
    for task, reason in skipped:
        print(f"Skipped: {task.description} ({task.pet_name}) — {reason}")
    for warning in scheduler.detect_conflicts(scheduled):
        print(f"Warning: {warning}")
    used = sum(t.duration_minutes for t in scheduled)
    print("-" * 50)
    print(f"Total: {used} of {owner.available_minutes} min used")


if __name__ == "__main__":
    main()
