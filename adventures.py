import streamlit as st


st.title("🧭 Our Adventures", anchor=False)
st.caption("Practice mode — these destinations last only for this browser session.")

# Create an empty list the first time this page opens.
if "practice_adventures" not in st.session_state:
    st.session_state["practice_adventures"] = []

adventures = st.session_state["practice_adventures"]

st.metric("Adventure ideas", len(adventures))

with st.form("add_adventure", clear_on_submit=True):
    name = st.text_input("Adventure name")
    location = st.text_input("Location")

    status = st.selectbox(
        "Status",
        ["Someday", "Planning", "Booked", "Visited"],)
    notes = st.text_area("Notes")
    submitted = st.form_submit_button ("Add Adventure")
if submitted:
        if name.strip():
            adventures.append({
                "Adventure": name.strip(),
                "Location": location.strip(),
                "Status": status,
                "Notes": notes.strip(),})
            st.rerun()
        else: st.warning("Enter an adventure name first.")
st.subheader("Our destination list", anchor=False)
search_text = st.text_input(
    "Search adventures",
    placeholder="Search by name, location, or notes",
).strip().casefold()
status_filter = st.selectbox(
    "Show status",
    ["All", "Someday", "Planning", "Booked", "Visited"],
) 
#Remember the positions of the adventures matching the filter.
matching_indexes= [
    index
    for index, adventure in enumerate(adventures)
    if (status_filter == "All" or adventure["Status"] == status_filter
        or adventure["Status"] == status_filter)
    and (
        not search_text
        or any(
            search_text in str(adventure.get(field) or "").casefold()
            for field in ["Adventure", "Location", "Notes"])
        )
    ]
visible_adventures = [
    adventures[index].copy()
    for index in matching_indexes
]
st.caption(
    f"Showing {len(visible_adventures)} of {len(adventures)} adventures")
if not adventures:
    st.info("Add your first adventure using the form above.")

elif not visible_adventures:
    st.info("No adventures match your search and status filter.")

else:
    on = st.toggle("Edit form")

    if on:
        with st.form("edit_adventures"):
            edited_adventures = st.data_editor(
                visible_adventures,
                hide_index=True,
                width="stretch",
                num_rows="fixed",
                column_config={
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Someday", "Planning", "Booked", "Visited"],
                        required=True,
                    ),
                },
            )

            save_changes = st.form_submit_button("Save changes")

        if save_changes:
            missing_name = any(
                not (row["Adventure"] or "").strip()
                for row in edited_adventures
            )

            if missing_name:
                st.warning("Each adventure needs a name.")
            else:
                # Save visible rows without changing hidden rows.
                for index, edited_row in zip(
                    matching_indexes, edited_adventures
                ):
                    adventures[index] = edited_row

                st.session_state["practice_adventures"] = adventures
                st.rerun()

    else:
        st.dataframe(
            visible_adventures,
            hide_index=True,
            width="stretch",
        )