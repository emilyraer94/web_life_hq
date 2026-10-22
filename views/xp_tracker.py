from datetime import date

import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError

from auth import require_login
from xp_data import add_completed_task, load_completed_tasks


st.title("⭐ XP Tracker", anchor=False)
st.caption("Your completed tasks are saved privately in Supabase.")

user = require_login()

# Read your saved records.
try:
    records = load_completed_tasks(user.id)
except (APIError, HTTPError):
    st.error("Could not load your XP history. Please refresh to try again.")
    st.stop()

# Convert database fields into the labels shown on the page.
entries = [
    {
        "Task": record["title"],
        "XP": record["xp"],
        "Completed": (
            date.fromisoformat(record["completed_on"])
            if record["completed_on"]
            else None
        ),
    }
    for record in records
]

total_xp = sum(entry["XP"] for entry in entries)
st.metric("Total XP", total_xp)

# Collect a previously completed task.
with st.form("add_xp", clear_on_submit=True):
    task_name = st.text_input(
        "Completed task",
        max_chars=160,
    )

    xp_earned = st.number_input(
        "XP earned",
        min_value=1,
        max_value=100000,
        value=10,
        step=1,
    )

    completed_on = st.date_input(
        "Completion date",
        value=date.today(),
        max_value=date.today(),
    )

    submitted = st.form_submit_button("Add completed task")

# Save only when the form is submitted.
if submitted:
    if not task_name.strip():
        st.warning("Enter a task name first.")
    else:
        try:
            add_completed_task(
                owner_id=user.id,
                task_name=task_name,
                xp=xp_earned,
                completed_on=completed_on,
            )
        except APIError:
            st.error("Supabase could not save this entry.")
        except HTTPError:
            st.error(
                "The connection was interrupted. Refresh and check "
                "your history before submitting again."
            )
        else:
            st.rerun()

st.subheader("Completed tasks", anchor=False)

if entries:
    st.dataframe(
        entries,
        hide_index=True,
        width="stretch",
        column_config={
            "Completed": st.column_config.DateColumn(
                "Completed",
                format="MMM D, YYYY",
            ),
        },
    )
else:
    st.info("Add your first completed task using the form above.")