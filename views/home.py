import streamlit as st
from httpx import HTTPError
from supabase_auth.errors import AuthError

from auth import require_login
from database import get_supabase


user = require_login()

is_owner = st.session_state.get("is_owner", False)
has_shared_access = st.session_state.get("has_shared_access", False)

st.title("🌿 Life HQ", anchor=False)

name = str(user.user_metadata.get("display_name") or "").strip()

if name:
    st.write(f"Welcome, {name}!")

if is_owner:
    st.write("A home for my plans, progress, and adventures.")
else:
    st.write("A home for our shared plans and adventures.")

if has_shared_access:
    with st.container(border=True):
        st.subheader("🧭 Our Adventures", anchor=False)
        st.write("Keep track of places we want to explore together.")
        st.page_link(
            "views/adventures.py",
            label="Open Our Adventures",
        )
    with st.container(border=True):
        st.subheader("🛣️ Someday DTR", anchor=False)
        st.write("Keep track of what we want to do together.")
        st.page_link(
            "views/somedayDTR.py",
            label="Open Someday DTR",
        )
    with st.container(border=True):
        st.subheader("🗓️ Calendar", anchor=False)
        st.write("Keep track of our shared plans and events.")
        st.page_link(
            "views/calendar.py",
            label="Open Calendar",
        )

if is_owner:

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
