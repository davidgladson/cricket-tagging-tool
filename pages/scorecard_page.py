import streamlit as st

st.set_page_config(
    page_title="Scorecard View",
    initial_sidebar_state="collapsed"
)

st.write("# This is Scorecard View!")

if st.button("Home"):
    st.switch_page("home_page.py")