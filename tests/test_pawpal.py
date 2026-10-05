"""Tests for the core PawPal+ scheduling logic."""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Scheduler, Task

TODAY = date.today()


@pytest.fixture
def home():
    """An owner with 90 minutes, two pets with no tasks, and a scheduler."""
    owner = Owner(name="Grace", available_minutes=90)
    biscuit = Pet(name="Biscuit", species="dog")
    fluffy = Pet(name="Fluffy", species="cat")
    owner.add_pet(biscuit)
    owner.add_pet(fluffy)
    return owner, biscuit, fluffy, Scheduler(owner)


def test_mark_complete_changes_task_status():
    task = Task("Morning walk", "07:30")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_task_count():
    pet = Pet(name="Biscuit", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Morning walk", "07:30"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Breakfast", "08:00"))
    assert len(pet.tasks) == 2


# --- 1. Sorting ---

def test_sort_by_time_orders_out_of_order_tasks(home):
    _, _, _, scheduler = home
    tasks = [Task("Evening walk", "18:00"), Task("Morning walk", "07:30"), Task("Lunch", "12:00")]
    result = scheduler.sort_by_time(tasks)
    assert [t.time for t in result] == ["07:30", "12:00", "18:00"]


def test_sort_by_time_keeps_same_time_tasks(home):
    _, _, _, scheduler = home
    tasks = [Task("Breakfast", "08:00"), Task("Medicine", "08:00"), Task("Wake up", "07:00")]
    result = scheduler.sort_by_time(tasks)
    assert len(result) == 3
    assert result[0].time == "07:00"


def test_sort_by_time_does_not_change_input_list(home):
    _, _, _, scheduler = home
    tasks = [Task("Evening walk", "18:00"), Task("Morning walk", "07:30")]
    scheduler.sort_by_time(tasks)
    assert [t.time for t in tasks] == ["18:00", "07:30"]


# --- 2. Filtering ---

def test_filter_tasks_by_pet(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Morning walk", "07:30"))
    biscuit.add_task(Task("Evening walk", "18:00"))
    fluffy.add_task(Task("Breakfast", "08:00"))
    result = scheduler.filter_tasks(pet_name="Fluffy")
    assert [t.description for t in result] == ["Breakfast"]


def test_filter_tasks_by_completion(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Morning walk", "07:30", completed=True))
    biscuit.add_task(Task("Evening walk", "18:00"))
    fluffy.add_task(Task("Breakfast", "08:00"))
    assert [t.description for t in scheduler.filter_tasks(completed=True)] == ["Morning walk"]
    assert len(scheduler.filter_tasks(completed=False)) == 2


def test_filter_tasks_by_pet_and_completion(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Morning walk", "07:30", completed=True))
    biscuit.add_task(Task("Evening walk", "18:00"))
    fluffy.add_task(Task("Breakfast", "08:00"))
    result = scheduler.filter_tasks(pet_name="Biscuit", completed=False)
    assert [t.description for t in result] == ["Evening walk"]


def test_filter_tasks_with_no_filters_returns_all(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Morning walk", "07:30", completed=True))
    biscuit.add_task(Task("Evening walk", "18:00"))
    fluffy.add_task(Task("Breakfast", "08:00"))
    assert len(scheduler.filter_tasks()) == 3


# --- 3. Recurring tasks ---

def test_daily_task_repeats_tomorrow(home):
    _, biscuit, _, scheduler = home
    task = Task("Morning walk", "07:30", frequency="daily")
    biscuit.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert task.completed is True
    assert next_task.due_date == TODAY + timedelta(days=1)
    assert next_task.completed is False
    assert next_task.description == "Morning walk"
    assert next_task.pet_name == "Biscuit"
    assert len(biscuit.tasks) == 2


def test_weekly_task_repeats_in_a_week(home):
    _, _, fluffy, scheduler = home
    task = Task("Brush fur", "12:00", frequency="weekly")
    fluffy.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.due_date == TODAY + timedelta(weeks=1)


def test_once_task_does_not_repeat(home):
    _, biscuit, _, scheduler = home
    task = Task("Vet visit", "15:00", frequency="once")
    biscuit.add_task(task)
    assert scheduler.mark_task_complete(task) is None
    assert len(biscuit.tasks) == 1


def test_overdue_daily_task_repeats_from_today(home):
    _, biscuit, _, scheduler = home
    task = Task("Morning walk", "07:30", frequency="daily", due_date=TODAY - timedelta(days=3))
    biscuit.add_task(task)
    next_task = scheduler.mark_task_complete(task)
    assert next_task.due_date == TODAY + timedelta(days=1)


# --- 4. Conflict detection ---

def test_detect_conflicts_same_start_time(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Breakfast", "08:00"))
    fluffy.add_task(Task("Breakfast", "08:00"))
    warnings = scheduler.detect_conflicts(scheduler.owner.get_all_tasks())
    assert len(warnings) == 1
    assert warnings[0].startswith("Same time")
    assert "different pets" in warnings[0]


def test_detect_conflicts_overlapping_times(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Morning walk", "08:00", duration_minutes=30))
    fluffy.add_task(Task("Brush fur", "08:20"))
    warnings = scheduler.detect_conflicts(scheduler.owner.get_all_tasks())
    assert len(warnings) == 1
    assert warnings[0].startswith("Overlap")


def test_detect_conflicts_same_pet(home):
    _, biscuit, _, scheduler = home
    biscuit.add_task(Task("Morning walk", "08:00"))
    biscuit.add_task(Task("Medicine", "08:00"))
    warnings = scheduler.detect_conflicts(biscuit.tasks)
    assert len(warnings) == 1
    assert "same pet (Biscuit)" in warnings[0]


def test_detect_conflicts_back_to_back_is_fine(home):
    _, biscuit, _, scheduler = home
    biscuit.add_task(Task("Morning walk", "08:00", duration_minutes=30))
    biscuit.add_task(Task("Play", "08:30"))
    assert scheduler.detect_conflicts(biscuit.tasks) == []


def test_detect_conflicts_different_days_is_fine(home):
    _, biscuit, _, scheduler = home
    biscuit.add_task(Task("Morning walk", "08:00"))
    biscuit.add_task(Task("Morning walk", "08:00", due_date=TODAY + timedelta(days=1)))
    assert scheduler.detect_conflicts(biscuit.tasks) == []


# --- 5. Daily plan ---

def test_daily_plan_stays_within_budget(home):
    owner, biscuit, _, scheduler = home
    owner.available_minutes = 60
    for time in ["07:00", "09:00", "11:00"]:
        biscuit.add_task(Task("Walk", time, duration_minutes=30))
    scheduled, skipped = scheduler.generate_daily_plan()
    assert sum(t.duration_minutes for t in scheduled) <= 60
    assert len(skipped) == 1
    _, reason = skipped[0]
    assert reason  # each skipped task comes with a reason


def test_daily_plan_prefers_high_priority(home):
    owner, biscuit, _, scheduler = home
    owner.available_minutes = 30
    biscuit.add_task(Task("Play", "07:00", duration_minutes=30, priority="low"))
    biscuit.add_task(Task("Medicine", "09:00", duration_minutes=30, priority="high"))
    scheduled, skipped = scheduler.generate_daily_plan()
    assert [t.description for t in scheduled] == ["Medicine"]
    assert [t.description for t, _ in skipped] == ["Play"]


def test_daily_plan_is_in_time_order(home):
    _, biscuit, fluffy, scheduler = home
    biscuit.add_task(Task("Evening walk", "18:00", priority="high"))
    fluffy.add_task(Task("Brush fur", "12:00", priority="low"))
    biscuit.add_task(Task("Morning walk", "07:30", priority="medium"))
    scheduled, _ = scheduler.generate_daily_plan()
    assert [t.time for t in scheduled] == ["07:30", "12:00", "18:00"]


def test_daily_plan_skips_done_and_future_tasks(home):
    _, biscuit, _, scheduler = home
    biscuit.add_task(Task("Done already", "07:00", completed=True))
    biscuit.add_task(Task("Tomorrow", "08:00", due_date=TODAY + timedelta(days=1)))
    biscuit.add_task(Task("Today", "09:00"))
    scheduled, skipped = scheduler.generate_daily_plan()
    assert [t.description for t in scheduled] == ["Today"]
    assert skipped == []
