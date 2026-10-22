import streamlit as st

st.title("🌿 Life HQ", anchor=False)
st.write("A home for my plans, progress, and adventures.")

with st.container(border=True):
    st.subheader("🧭 Our Adventures", anchor=False)
    st.write("Keep track of places we want to explore together.")
    st.page_link(
        "views/adventures.py",
        label="Open Our Adventures",
    )
with st.container(border=True):
    st.subheader("🛣️ Someday DTR", anchor=False)
    st.write("Keep track what we want to do together.")
    st.page_link(
        "views/somedayDTR.py",
        label="Open Someday DTR",
    )
with st.container(border=True):
    st.subheader("📋 Tasks", anchor=False)
    st.write("Keep organized and know what your tasks are.")
    st.page_link(
        "views/tasks.py",
        label="Open Tasks",
    )
with st.container(border=True):
    st.subheader("⭐ XP Tracker", anchor=False)
    st.write("Log completed tasks and celebrate your progress.")

    st.page_link(
        "views/xp_tracker.py",
        label="Open XP Tracker",
    )

