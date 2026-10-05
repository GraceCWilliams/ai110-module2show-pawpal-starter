from datetime import time

import streamlit as st
from pawpal_system import Pet, Owner, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# Keep the Owner in session state so pets and tasks survive Streamlit reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")
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
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age", min_value=0, max_value=40, value=0)

if st.button("Add pet"):
    if not pet_name.strip():
        st.error("Pet name can't be empty.")
    elif owner.get_pet(pet_name) is not None:
        st.error(f"{owner.name} already has a pet named {pet_name}.")
    else:
        owner.add_pet(Pet(name=pet_name, species=species, age=int(age)))
        st.success(f"Added {pet_name}.")

if owner.pets:
    st.table(
        [{"name": p.name, "species": p.species, "age": p.age, "tasks": len(p.tasks)}
         for p in owner.pets]
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

    tasks = scheduler.sort_by_time(scheduler.filter_tasks(completed=False))
    if tasks:
        st.write("Current tasks:")
        st.table(
            [{"pet": t.pet_name, "time": t.time, "task": t.description,
              "minutes": t.duration_minutes, "priority": t.priority,
              "frequency": t.frequency, "due": t.due_date.isoformat()}
             for t in tasks]
        )
    else:
        st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    scheduled, skipped = scheduler.generate_daily_plan()
    if not scheduled and not skipped:
        st.info("No tasks due today.")
    else:
        if scheduled:
            st.table(
                [{"time": t.time, "pet": t.pet_name, "task": t.description,
                  "minutes": t.duration_minutes, "priority": t.priority}
                 for t in scheduled]
            )
        for t, reason in skipped:
            st.warning(f"Skipped '{t.description}' for {t.pet_name}: {reason}")
        for warning in scheduler.detect_conflicts(scheduled):
            st.warning(warning)
        used = sum(t.duration_minutes for t in scheduled)
        st.caption(f"{used} of {owner.available_minutes} minutes used.")
        with st.expander("Plan explanation"):
            st.text(scheduler.explain_plan())
