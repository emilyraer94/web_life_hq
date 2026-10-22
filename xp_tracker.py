from datetime import date

import streamlit as st


st.title("⭐ XP Tracker")
st.caption("Practice mode — these entries last only for this browser session.")

# Create sample entries the first time this page opens.
if "practice_xp" not in st.session_state:
    st.session_state["practice_xp"] = [
        {"Task": "Example: read a chapter", "XP": 25, "Completed": date.today()},
        {"Task": "Example: tidy my desk", "XP": 10, "Completed": date.today()},
    ]

entries = st.session_state["practice_xp"]

# Calculate the total from the entries.
total_xp = sum(entry["XP"] for entry in entries)
st.metric("Practice XP", total_xp)

# Group the inputs into a form.
with st.form("add_xp", clear_on_submit=True):
    task_name = st.text_input("Completed task")
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

# Process the form when its button is clicked.
if submitted:
    if task_name.strip():
        entries.append({
            "Task": task_name.strip(),
            "XP": xp_earned,
            "Completed": completed_on,
        })
        st.rerun()
    else:
        st.warning("Enter a task name first.")

st.subheader("Completed tasks")
st.dataframe(entries, hide_index=True, use_container_width=True)