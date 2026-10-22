import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError
from supabase_auth.errors import AuthError

from auth import require_login
from database import get_supabase


st.set_page_config(
    page_title="Life HQ",
    page_icon="🌿",
    layout="centered",
)

user = require_login()
supabase = get_supabase()

if st.sidebar.button("Sign out"):
    try:
        supabase.auth.sign_out(options={"scope": "local"})
    except (AuthError, HTTPError):
        st.error("Could not sign out. Please try again.")
        st.stop()

    st.session_state.clear()
    st.rerun()

# Check permissions using protected database tables.
try:
    owner_rows = (
        supabase.table("app_owners")
        .select("user_id")
        .eq("user_id", str(user.id))
        .execute()
    )

    membership_rows = (
        supabase.table("workspace_members")
        .select("workspace_id")
        .eq("user_id", str(user.id))
        .execute()
    )
except (APIError, HTTPError):
    st.error("Could not check your page permissions. Please try again.")
    st.stop()

is_owner = bool(owner_rows.data)
has_shared_access = bool(membership_rows.data)

if not is_owner and not has_shared_access:
    st.info("This account needs shared workspace membership.")
    st.stop()

# Refresh these permissions on every run for the Home page.
st.session_state["is_owner"] = is_owner
st.session_state["has_shared_access"] = has_shared_access

pages = [
    st.Page("views/home.py", title="Home", default=True),
]

if has_shared_access:
    pages.extend([
        st.Page("views/adventures.py", title="Our Adventures"),
        st.Page("views/somedayDTR.py", title="Someday DTR"),
        st.Page("views/calendar.py", title="Calendar")
    ])

if is_owner:
    pages.extend([
        st.Page("views/tasks.py", title="Tasks"),
        st.Page("views/xp_tracker.py", title="XP Tracker"),
    ])

selected_page = st.navigation(pages, position="hidden")

if st.session_state.pop("go_home_after_login", False):
    st.switch_page("views/home.py")

st.sidebar.title("🌿 Life HQ", anchor=False)
st.sidebar.subheader("Your spaces", anchor=False)

for page in pages:
    st.sidebar.page_link(page)

selected_page.run()