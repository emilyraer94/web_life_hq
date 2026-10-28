from datetime import date

import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError

from auth import require_login
from task_data import add_task, load_tasks, save_task

st.title("✅ Tasks", anchor=False)
st.caption("Your tasks are saved privately in Supabase.")

user = require_login()

# Load unfinished tasks from the database.
try:
    records = load_tasks(user.id)
except (APIError, HTTPError):
    st.error("Could not load your tasks. Please refresh to try again.")
    st.stop()

# Convert database fields into the labels used on this page.
tasks = [
    {
        "id": record["id"],
        "Task": record["task_name"],
        "Priority": record.get("priority") or "Medium",
        "XP": record.get("xp") if record.get("xp") is not None else 10,
        "Due date": (
            date.fromisoformat(record["due_date"])
            if record["due_date"]
            else None
        ),
        "Notes": record.get("notes") or "",
        "Complete": False,
    }
    for record in records
]

st.metric("Tasks to do", len(tasks))

# Add a new task.
with st.form("add_task", clear_on_submit=True):
    task_name = st.text_input("Task name", max_chars=160)

    priority = st.selectbox(
        "Priority",
        ["Low", "Medium", "High"],
        index=1,
    )

    xp_reward = st.number_input(
        "XP for completing this task",
        min_value=1,
        max_value=100000,
        value=10,
        step=1,
    )

    due_date = st.date_input("Due date (optional)", value=None)
    notes = st.text_area("Notes", max_chars=1000)
    submitted = st.form_submit_button("Add task")

if submitted:
    if not task_name.strip():
        st.warning("Enter a task name first.")
    else:
        try:
            add_task(
                owner_id=user.id,
                task_name=task_name,
                priority=priority,
                xp=xp_reward,
                due_date=due_date,
                notes=notes,
            )
        except APIError:
            st.error("Supabase could not save this task.")
        except HTTPError:
            st.error(
                "The connection was interrupted. Refresh and check "
                "your tasks before submitting again."
            )
        else:
            st.rerun()

st.subheader("My tasks", anchor=False)

if not tasks:
    st.info("Add your first task using the form above.")

else:
    edit_mode = st.toggle("Edit form", key="edit_tasks")

    if edit_mode:
        with st.form("edit_tasks_form"):
            edited_tasks = st.data_editor(
                tasks,
                hide_index=True,
                width="stretch",
                num_rows="fixed",
                disabled=["id"],
                column_config={
                    "id": None,
                    "Task": st.column_config.TextColumn(
                        "Task",
                        required=True,
                        max_chars=160,
                    ),
                    "Priority": st.column_config.SelectboxColumn(
                        "Priority",
                        options=["Low", "Medium", "High"],
                        required=True,
                    ),
                    "XP": st.column_config.NumberColumn(
                        "XP",
                        min_value=1,
                        max_value=100000,
                        step=1,
                        required=True,
                    ),
                    "Due date": st.column_config.DateColumn(
                        "Due date",
                    ),
                    "Notes": st.column_config.TextColumn(
                                            "Notes",
                                            required=False,
                                            max_chars=1000,
                    ),
                    "Complete": st.column_config.CheckboxColumn(
                        "Complete",
                        required=True,
                    ),
                },
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            invalid_name = any(
                not (task["Task"] or "").strip()
                or len((task["Task"] or "").strip()) > 160
                for task in edited_tasks
            )

            if invalid_name:
                st.warning("Each task needs a name of 1–160 characters.")

            else:
                try:
                    # Save only rows that changed.
                    for original, edited in zip(tasks, edited_tasks):
                        if original != edited:
                            updated_task = {
                                **edited,
                                "id": original["id"],
                            }
                            save_task(user.id, updated_task)

                except (APIError, HTTPError, ValueError):
                    st.error(
                        "Some changes could not be saved. Earlier rows "
                        "may already be saved. Refresh to check your "
                        "tasks before editing again."
                    )
                else:
                    st.rerun()

    else:
        # Keep database IDs out of the displayed table.
        display_tasks = [
            {
                key: value
                for key, value in task.items()
                if key != "id"
            }
            for task in tasks
        ]

        st.dataframe(
            display_tasks,
            hide_index=True,
            width="stretch",
        )