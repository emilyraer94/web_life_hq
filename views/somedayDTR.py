import streamlit as st
from httpx import HTTPError
from postgrest.exceptions import APIError

from auth import require_login
from adventure_data import get_shared_workspace_id
from someday_data import (
    add_someday_item,
    load_someday_items,
    save_someday_item,
)
CATEGORIES = ["Movies", "To try", "Other"]

st.title("🛣️ Someday DTR", anchor=False)
st.caption("Our shared ideas for someday down the road.")

user = require_login()

# Find the shared workspace and load its items.
try:
    workspace_id = get_shared_workspace_id(user.id)
    records = load_someday_items(workspace_id)
except ValueError:
    st.error("This account needs a shared workspace membership.")
    st.stop()
except APIError as error:
    st.error(f"Database error ({error.code}): {error.message}")
    st.stop()
except HTTPError:
    st.error("Could not connect to Supabase. Please try again.")
    st.stop()

items = [
    {
        "id": record["id"],
        "Item": record["title"],
        "Category": record["category"],
        "Notes": record["notes"],
    }
    for record in records
]

st.metric("Someday list", len(items))

with st.form("add_someday_item", clear_on_submit=True):
    name = st.text_input("Item name", max_chars=160)
    category = st.selectbox(
    "Category",
    CATEGORIES,
    index=2,
)
    notes = st.text_area("Notes", max_chars=10000)

    submitted = st.form_submit_button("Add item")

if submitted:
    if not name.strip():
        st.warning("Enter an item name first.")
    else:
        try:
            add_someday_item(workspace_id, name, notes, category=category)
        except APIError:
            st.error("Supabase could not save this item.")
        except HTTPError:
            st.error(
                "The connection was interrupted. Refresh and check "
                "your list before submitting again."
            )
        else:
            st.rerun()

st.subheader("Our Someday Down the Road list", anchor=False)

if not items:
    st.info("Add your first item using the form above.")

else:
    edit_mode = st.toggle("Edit form", key="edit_someday_toggle")

    if edit_mode:
        with st.form("edit_someday_items"):
            edited_items = st.data_editor(
                items,
                hide_index=True,
                width="stretch",
                num_rows="fixed",
                disabled=["id"],
                column_config={
                    "id": None,
                    "Item": st.column_config.TextColumn(
                        "Item",
                        required=True,
                        max_chars=160,
                    ),
                    "Category": st.column_config.SelectboxColumn(
                        "Category",
                        options=CATEGORIES,
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
                not (item["Item"] or "").strip()
                or len((item["Item"] or "").strip()) > 160
                or len(item["Notes"] or "") > 10000
                or item["Category"] not in CATEGORIES
                for item in edited_items
            )

            if invalid_entry:
                st.warning(
                    "Each item needs a name of 1–160 characters. "
                    "Notes can contain up to 10,000 characters."
                )
            else:
                try:
                    for original, edited in zip(items, edited_items):
                        if original != edited:
                            updated_item = {
                                **edited,
                                "id": original["id"],
                            }
                            save_someday_item(
                                workspace_id,
                                updated_item,
                            )
                except (APIError, HTTPError, ValueError):
                    st.error(
                        "Some changes could not be saved. Earlier rows "
                        "may already be saved. Refresh to check your "
                        "list before editing again."
                    )
                else:
                    st.rerun()

    else:
        st.dataframe(
            [
                {"Item": item["Item"], "Category": item["Category"], "Notes": item["Notes"]}
                for item in items
            ],
            hide_index=True,
            width="stretch",
        )