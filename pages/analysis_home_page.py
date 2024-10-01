import streamlit as st

st.set_page_config(
    page_title="Scorecard View",
    initial_sidebar_state="collapsed"
)


# Password check function
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.error("Unauthorized access! Please login from the main page.")
    return False

# Check if the password is correct before allowing access to this page
if not check_password():
    st.stop()



st.write("# This is Scorecard View!")
if st.button("Home"):
    st.switch_page("home_page.py")

st.write("Page under Development")