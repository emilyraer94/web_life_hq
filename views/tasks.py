import streamlit as st
from datetime import date


st.title("✅ Tasks", anchor=False)
st.caption("Practice mode — tasks last only for this browser session.")

# Create the task list when this page first opens.
if "practice_tasks" not in st.session_state:
    st.session_state["practice_tasks"] = []

tasks = st.session_state["practice_tasks"]

for task in tasks:
    task.setdefault("XP", 10)

unfinished = sum(not task["Complete"] for task in tasks)
st.metric("Tasks to do", unfinished)

with st.form("add_task", clear_on_submit=True):
    task_name = st.text_input("Task name")

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

    submitted = st.form_submit_button("Add task")

if submitted:
    if task_name.strip():
        tasks.append({
            "Task": task_name.strip(),
            "Priority": priority,
            "XP": xp_reward,
            "Due date": due_date,
            "Complete": False,
        })
        st.rerun()
    else:
        st.warning("Enter a task name first.")

st.subheader("My tasks", anchor=False)

if tasks:
    edit_mode = st.toggle("Edit form", key="edit_tasks")

    if edit_mode:
        with st.form("edit_tasks_form"):
            edited_tasks = st.data_editor(
                tasks,
                hide_index=True,
                width="stretch",
                num_rows="fixed",
                column_config={
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
                    "Complete": st.column_config.CheckboxColumn(
                        "Complete",
                        required=True,
                    ),
                },
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            missing_name = any(
                not (task["Task"] or "").strip()
                for task in edited_tasks
            )

            if missing_name:
                st.warning("Each task needs a name.")
            else:
                #Turn completed tasks into XP history entries.
                completed_entries = [
                    {
                        "Task": task["Task"].strip(),
                        "XP": int(task["XP"]),
                        "Completed":date.today(),
                    }
                     for task in edited_tasks
                    if task["Complete"]
                ]

                # Keep unfinished tasks on this page.
                remaining_tasks = [
                    task
                    for task in edited_tasks
                    if not task["Complete"]
                ]

                # Preserve the existing XP history and add new completions.
                xp_history = st.session_state.get("practice_xp", [])

                st.session_state["practice_xp"] = (
                    xp_history + completed_entries
                )
                st.session_state["practice_tasks"] = remaining_tasks

                st.rerun()

    else:
        st.dataframe(
            tasks,
            hide_index=True,
            width="stretch",
        )

else:
    st.info("Add your first task using the form above.")