"""Tests for the core PawPal+ scheduling logic."""

from pawpal_system import Pet, Task


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
