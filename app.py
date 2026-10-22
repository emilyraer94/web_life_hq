import streamlit as st
from auth import require_login
from database import get_supabase
from httpx import HTTPError
from postgrest.exceptions import APIError

st.set_page_config(
    page_title="Life HQ",
    page_icon="🌿",
    layout="centered",
)
user = require_login()

# Check whether this account owns Life HQ.
try:
    owner_rows = (
        get_supabase()
        .table("app_owners")
        .select("user_id")
        .eq("user_id", str(user.id))
        .execute()
    )
except (APIError, HTTPError):
    st.error("Could not check your page permissions. Please try again.")
    st.stop()

if not owner_rows.data:
    st.info("Shared account access is being set up.")
    st.stop()

# Define the pages available in the app.
pages = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/adventures.py", title="Our Adventures"),
    st.Page("views/somedayDTR.py", title="Someday DTR"),
    st.Page("views/tasks.py", title="Tasks"),
    st.Page("views/xp_tracker.py", title="XP Tracker")]   

# Register the pages and identify the selected page.
selected_page = st.navigation(pages, position="hidden")

# Display our own sidebar links.
st.sidebar.title("🌿 Life HQ")
st.sidebar.subheader("Your spaces")

for page in pages:
    st.sidebar.page_link(page)

# Display the selected page's contents.
selected_page.run()
