import streamlit as st
from httpx import HTTPError
from supabase_auth.errors import AuthApiError
from database import get_supabase



def show_login():
    st.title("🌿 Welcome to Life HQ", anchor=False)
    st.caption("Sign in to open your spaces.")

    with st.form("login_form", clear_on_submit=True):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if not email.strip() or not password:
            st.warning("Enter your email and password.")
            return

        supabase = get_supabase()

        try:
            response = supabase.auth.sign_in_with_password(
                {
                    "email": email.strip(),
                    "password": password,
                }
            )
        except AuthApiError:
            st.error(
                "Sign-in failed. Check your email and password "
                "and make sure your account is confirmed."
            )
        except HTTPError:
            st.error("Could not connect. Please try again.")
        else:
            if response.session:
                st.session_state["go_home_after_login"] = True
                st.rerun()
            else:
                st.error("Sign-in could not be completed.")
def require_login():
    supabase = get_supabase()

    try:
        session = supabase.auth.get_session()

        if session is None:
            show_login()
            st.stop()

        response = supabase.auth.get_user()

    except AuthApiError as error:
        if error.status in (401, 403):
            show_login()
        else:
            st.error("Could not check your login. Please try again.")

        st.stop()

    except HTTPError:
        st.error("Could not connect. Your login has not been cleared.")
        st.stop()

    if response is None or response.user is None:
        show_login()
        st.stop()

    return response.user