import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError

from auth import require_login
from adventure_data import (
    add_adventure,
    get_shared_workspace_id,
    load_adventures,
    save_adventure,
)


STATUSES = ["Someday", "Planning", "Booked", "Visited"]

st.title("🧭 Our Adventures", anchor=False)
st.caption("Your destinations are saved in your shared Supabase workspace.")

user = require_login()

# Find your shared workspace and load its destinations.
try:
    workspace_id = get_shared_workspace_id(user.id)
    records = load_adventures(workspace_id)
except ValueError:
    st.error("This account needs a shared workspace membership.")
    st.stop()
except (APIError, HTTPError):
    st.error("Could not load your adventures. Please refresh to try again.")
    st.stop()

# Convert database fields into the labels used on this page.
adventures = [
    {
        "id": record["id"],
        "Adventure": record["title"],
        "Location": record["location"],
        "Status": record["status"],
        "Notes": record["notes"],
    }
    for record in records
]

st.metric("Adventure ideas", len(adventures))

# Add a destination.
with st.form("add_adventure", clear_on_submit=True):
    name = st.text_input("Adventure name", max_chars=160)
    location = st.text_input("Location", max_chars=240)
    status = st.selectbox("Status", STATUSES)
    notes = st.text_area("Notes", max_chars=10000)

    submitted = st.form_submit_button("Add Adventure")

if submitted:
    if not name.strip():
        st.warning("Enter an adventure name first.")
    else:
        try:
            add_adventure(
                user_id=user.id,
                workspace_id=workspace_id,
                name=name,
                location=location,
                status=status,
                notes=notes,
            )
        except APIError:
            st.error("Supabase could not save this adventure.")
        except HTTPError:
            st.error(
                "The connection was interrupted. Refresh and check "
                "your destinations before submitting again."
            )
        else:
            st.rerun()

st.subheader("Our destination list", anchor=False)

search_text = st.text_input(
    "Search adventures",
    placeholder="Search by name, location, or notes",
).strip().casefold()

status_filter = st.selectbox(
    "Show status",
    ["All"] + STATUSES,
)

# Keep only destinations matching both filters.
visible_adventures = [
    adventure.copy()
    for adventure in adventures
    if (
        status_filter == "All"
        or adventure["Status"] == status_filter
    )
    and (
        not search_text
        or any(
            search_text in str(adventure.get(field) or "").casefold()
            for field in ["Adventure", "Location", "Notes"]
        )
    )
]

st.caption(
    f"Showing {len(visible_adventures)} of {len(adventures)} adventures"
)

if not adventures:
    st.info("Add your first adventure using the form above.")

elif not visible_adventures:
    st.info("No adventures match your search and status filter.")

else:
    edit_mode = st.toggle("Edit form", key="edit_adventures_toggle")

    if edit_mode:
        with st.form("edit_adventures"):
            edited_adventures = st.data_editor(
                visible_adventures,
                hide_index=True,
                width="stretch",
                num_rows="fixed",
                disabled=["id"],
                column_config={
                    "id": None,
                    "Adventure": st.column_config.TextColumn(
                        "Adventure",
                        required=True,
                        max_chars=160,
                    ),
                    "Location": st.column_config.TextColumn(
                        "Location",
                        max_chars=240,
                    ),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=STATUSES,
                        required=True,
                    ),
                    "Notes": st.column_config.TextColumn(
                        "Notes",
                        max_chars=10000,
                    ),
                },
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            invalid_entry = any(
                not (row["Adventure"] or "").strip()
                or len((row["Adventure"] or "").strip()) > 160
                or len(row["Location"] or "") > 240
                or len(row["Notes"] or "") > 10000
                or row["Status"] not in STATUSES
                for row in edited_adventures
            )

            if invalid_entry:
                st.warning(
                    "Check that each adventure has a name and status, "
                    "and that its text fits the field limits."
                )
            else:
                try:
                    # Save changed visible rows using their database IDs.
                    for original, edited in zip(
                        visible_adventures, edited_adventures
                    ):
                        if original != edited:
                            updated_adventure = {
                                **edited,
                                "id": original["id"],
                            }
                            save_adventure(
                                workspace_id,
                                updated_adventure,
                            )

                except (APIError, HTTPError, ValueError):
                    st.error(
                        "Some changes could not be saved. Earlier rows "
                        "may already be saved. Refresh to check your "
                        "destinations before editing again."
                    )
                else:
                    st.rerun()

    else:
        display_adventures = [
            {
                key: value
                for key, value in adventure.items()
                if key != "id"
            }
            for adventure in visible_adventures
        ]

        st.dataframe(
            display_adventures,
            hide_index=True,
            width="stretch",
        )