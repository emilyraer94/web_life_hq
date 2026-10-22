import streamlit as st


st.title("🛣️Someday DTR")
st.caption("Practice mode — these items last only for this browser session.")

# Create an empty list the first time this page opens.
if "practice_list" not in st.session_state:
    st.session_state["practice_list"] = []

somedayDTR = st.session_state["practice_list"]

st.metric("Someday List", len(somedayDTR))

with st.form("add_item", clear_on_submit=True):
    name = st.text_input("Item name")
    notes = st.text_area("Notes")

    submitted = st.form_submit_button("Add item")

if submitted:
    if name.strip():
        somedayDTR.append({
            "Item": name.strip(),
            "Notes": notes.strip(),
        })
        st.rerun()
    else:
        st.warning("Enter an item name first.")

st.subheader("Our Someday Down the Road list")

if somedayDTR:
    st.dataframe(
        somedayDTR,
        hide_index=True,
        use_container_width=True,
    )
else:
    st.info("Add your first item using the form above.")