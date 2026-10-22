import streamlit as st
from supabase import ClientOptions, create_client


def get_supabase():
    if "supabase_client" not in st.session_state:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_PUBLISHABLE_KEY"]

        if not key.startswith("sb_publishable_"):
            raise ValueError("Use your Supabase publishable key.")

        st.session_state["supabase_client"] = create_client(
            url,
            key,
            options=ClientOptions(
                auto_refresh_token=True,
                persist_session=True,
            ),
        )

    return st.session_state["supabase_client"]