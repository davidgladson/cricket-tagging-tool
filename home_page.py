import streamlit as st

st.set_page_config(
    page_title="Cricket Tagging Tool",
    initial_sidebar_state="collapsed"
)

st.write("# Welcome to Cricket Tagging Tool! 👋")

if st.button("Home"):
    st.switch_page("home_page.py")
if st.button("Tagging Page"):
    st.switch_page("pages/tagging_page.py")
if st.button("Scorecard View"):
    st.switch_page("pages/scorecard_page.py")