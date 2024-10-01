import streamlit as st
import hmac
import streamlit as st


st.set_page_config(
    page_title="Cricket Tagging And Analysis Tool",
    initial_sidebar_state="collapsed"
)

# Inject CSS for background image
def add_bg_from_url():
    st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQNpdd96RgxYVJYtjUkQtWgxX_afdex-WYX0A&s");
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# Call the function to set background
add_bg_from_url()

def check_password():
    """Returns `True` if the user has entered the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        # Compare the entered password with the stored password (from secrets)
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password after verification.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is already validated
    if st.session_state.get("password_correct", False):
        return True

    # If not authenticated, show input for password
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    
    # If password was attempted but incorrect, show an error
    if st.session_state.get("password_correct") is False:
        st.error("😕 Password incorrect")
    
    return False

# Check if the password is correct before showing any content
if not check_password():
    # Stop execution here if the user is not authenticated
    st.stop()


st.success("Welcome To Cric Tagging Page")
col_1, col_2, col_3, col_4 = st.columns(4)

with col_2:
    if st.button("Go To Ball Tagging"):
        st.switch_page("pages/tagging_home_page.py")
        
with col_3:
    if st.button("Go To Analysis"):
        st.switch_page("pages/analysis_home_page.py")