from datetime import date, time, timedelta

import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler

PRIORITY_LABEL = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}


def clock(minutes: int) -> str:
    """Format minutes since midnight as HH:MM."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def due_label(day: date) -> str:
    """Show today and tomorrow by name, and other days as a short date."""
    if day == date.today():
        return "Today"
    if day == date.today() + timedelta(days=1):
        return "Tomorrow"
    return day.strftime("%a %b %d")


def task_rows(tasks: list[Task], conflicted: set[int] = frozenset()) -> list[dict]:
    """Table rows for tasks; `conflicted` holds the ids of tasks in a time clash."""
    return [
        {
            "Time": t.time,
            "Pet": t.pet_name,
            "Task": t.description,
            "Duration": f"{t.duration_minutes} min",
            "Priority": PRIORITY_LABEL[t.priority],
            "Repeats": t.frequency.capitalize(),
            "Due": due_label(t.due_date),
            "Status": "✅ Done" if t.completed else "⚠️ Conflict" if id(t) in conflicted else "To do",
        }
        for t in tasks
    ]


def show_conflicts(conflicts: list[tuple[Task, Task]]) -> None:
    """Show one warning per clash, in plain words, with a suggested new time."""
    for a, b in conflicts:
        a_end = clock(a.end_minutes())
        if a.pet_name == b.pet_name:
            problem = f"{a.pet_name} is booked for two things at once."
        else:
            problem = f"You'd be caring for {a.pet_name} and {b.pet_name} at the same time."
        st.warning(
            f"**{due_label(a.due_date)}: {a.description} ({a.pet_name}, {a.time}–{a_end}) "
            f"overlaps {b.description} ({b.pet_name}, {b.time})**\n\n"
            f"{problem} **Suggestion:** move {b.pet_name}'s {b.description} to {a_end}, "
            f"when {a.pet_name}'s {a.description} ends. If you can do both together (like feeding two "
            f"pets), you can ignore this.",
            icon="⚠️",
        )


st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. It plans each day's care tasks for all of your
pets based on how much time you have, each task's priority, and when it's scheduled.
"""
)

with st.expander("How to use PawPal+", expanded=False):
    st.markdown(
        """
1. **Owner:** set your name and how many minutes you have for pet care today.
2. **Add a Pet:** add each of your pets.
3. **Schedule a Task:** add care tasks with a time, duration, priority, and how often they repeat.
4. **Tasks:** filter the list by pet or status, check any time conflicts, and mark tasks complete.
   Daily and weekly tasks automatically come back for their next occurrence.
5. **Build Schedule:** generate today's plan. High-priority tasks are planned first, and tasks
   that don't fit in your time are listed with the reason.
"""
    )

st.divider()

# Keep the Owner in session state so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Grace", available_minutes=90)
owner = st.session_state.owner
scheduler = Scheduler(owner)

st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.available_minutes = int(
        st.number_input(
            "Available minutes today",
            min_value=1,
            max_value=1440,
            value=owner.available_minutes,
        )
    )

st.subheader("Add a Pet")
# Suggest the same sample pets as main.py, one at a time, until both are added.
SAMPLE_PETS = [("Biscuit", "dog"), ("Fluffy", "cat")]
suggested_name, suggested_species = next(
    ((n, s) for n, s in SAMPLE_PETS if owner.get_pet(n) is None), ("", "dog")
)
SPECIES = ["dog", "cat", "other"]
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value=suggested_name)
with col2:
    species = st.selectbox("Species", SPECIES, index=SPECIES.index(suggested_species))
with col3:
    age = st.number_input("Age", min_value=0, max_value=40, value=0)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    elif owner.get_pet(pet_name) is not None:
        st.error(f"{owner.name} already has a pet named {pet_name}.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        st.session_state.pet_flash = f"Added {pet_name}."
        st.rerun()  # refresh so the form suggests the next sample pet right away

# Message from the last "Add pet" click, shown after the rerun.
if "pet_flash" in st.session_state:
    st.success(st.session_state.pop("pet_flash"))

if owner.pets:
    st.dataframe(
        [{"Name": p.name, "Species": p.species.capitalize(), "Age": p.age, "Tasks": len(p.tasks)}
         for p in owner.pets],
        hide_index=True,
    )
else:
    st.info("No pets yet. Add one above.")

st.subheader("Schedule a Task")

if not owner.pets:
    st.caption("Add a pet before scheduling tasks.")
else:
    col1, col2 = st.columns(2)
    with col1:
        task_pet = st.selectbox("Pet", [p.name for p in owner.pets])
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.time_input("Time", value=time(8, 0))
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add task"):
        owner.get_pet(task_pet).add_task(
            Task(
                description=task_title,
                time=task_time.strftime("%H:%M"),
                duration_minutes=int(duration),
                priority=priority,
                frequency=frequency,
            )
        )
        st.success(f"Added '{task_title}' for {task_pet}.")

    st.subheader("Tasks")

    # Message from the last "Mark complete" click, shown after the rerun.
    if "flash" in st.session_state:
        st.success(st.session_state.pop("flash"))

    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox("Show pet", ["All pets"] + [p.name for p in owner.pets])
    with col2:
        status_filter = st.radio("Show", ["Unfinished", "Completed", "All"], horizontal=True)

    # Check clashes among all unfinished tasks, so they show as soon as a task is added.
    open_conflicts = scheduler.find_conflicts(scheduler.filter_tasks(completed=False))
    conflicted = {id(t) for pair in open_conflicts for t in pair}

    tasks = scheduler.sort_by_time(scheduler.filter_tasks(
        pet_name=None if pet_filter == "All pets" else pet_filter,
        completed={"Unfinished": False, "Completed": True, "All": None}[status_filter],
    ))
    if tasks:
        st.dataframe(task_rows(tasks, conflicted), hide_index=True)
        st.caption(f"{len(tasks)} task(s), sorted by time.")
    else:
        st.info("No tasks match these filters.")

    show_conflicts(open_conflicts)

    unfinished = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if unfinished:
        col1, col2 = st.columns([3, 1])
        with col1:
            # Choose by position: Streamlit hands back a copy of an object option,
            # and the real task (not a copy) has to be the one marked complete.
            choice = st.selectbox(
                "Task to complete",
                range(len(unfinished)),
                format_func=lambda i: (f"{unfinished[i].time} · {unfinished[i].description} "
                                       f"({unfinished[i].pet_name}, {due_label(unfinished[i].due_date)})"),
            )
            to_complete = unfinished[choice]
        with col2:
            st.write("")  # line the button up with the selectbox
            if st.button("Mark complete"):
                next_task = scheduler.mark_task_complete(to_complete)
                message = f"Completed '{to_complete.description}' for {to_complete.pet_name}."
                if next_task is not None:
                    message += f" Next {next_task.frequency} occurrence: {due_label(next_task.due_date)}."
                st.session_state.flash = message
                st.rerun()  # redraw the table with the updated tasks

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduled, skipped = scheduler.generate_daily_plan()
    if not scheduled and not skipped:
        st.info("No tasks due today.")
    else:
        conflicts = scheduler.find_conflicts(scheduled)
        used = sum(t.duration_minutes for t in scheduled)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Planned", len(scheduled))
        col2.metric("Minutes used", f"{used} / {owner.available_minutes}")
        col3.metric("Skipped", len(skipped))
        col4.metric("Conflicts", len(conflicts))
        st.progress(min(used / owner.available_minutes, 1.0))

        # Problems first, so the owner sees what needs attention before the plan itself.
        show_conflicts(conflicts)
        if not conflicts and not skipped:
            st.success("Everything fits in today's time, with no time conflicts.")

        if scheduled:
            st.markdown("**Today's plan**")
            st.dataframe(
                task_rows(scheduled, {id(t) for pair in conflicts for t in pair}),
                hide_index=True,
            )
        if skipped:
            st.markdown("**Didn't fit today**")
            st.dataframe(
                [{"Time": t.time, "Pet": t.pet_name, "Task": t.description,
                  "Duration": f"{t.duration_minutes} min",
                  "Priority": PRIORITY_LABEL[t.priority], "Reason": reason}
                 for t, reason in skipped],
                hide_index=True,
            )
        with st.expander("Plan explanation"):
            st.text(scheduler.explain_plan())
