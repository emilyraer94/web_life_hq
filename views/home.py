import streamlit as st

st.title("🌿 Life HQ")
st.write("A home for my plans, progress, and adventures.")

with st.container(border=True):
    st.subheader("🧭 Our Adventures")
    st.write("Keep track of places we want to explore together.")

    st.page_link(
        "views/adventures.py",
        label="Open Our Adventures",
    )
with st.container(border=True):
    st.subheader("🛣️ Someday DTR")
    st.write("Keep track what we want to do together.")

    st.page_link(
        "views/somedayDTR.py",
        label="Open Someday DTR",
    )

with st.container(border=True):
    st.subheader("⭐ XP Tracker")
    st.write("Log completed tasks and celebrate your progress.")

    st.page_link(
        "views/xp_tracker.py",
        label="Open XP Tracker",
    )

