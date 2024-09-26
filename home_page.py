import streamlit as st

st.set_page_config(
    page_title="Cricket Tagging And Analysis Tool",
    initial_sidebar_state="collapsed"
)

col_1, col_2, col_3, col_4 = st.columns(4)

with col_2:
    if st.button("Go To Ball Tagging"):
        st.switch_page("pages/tagging_home_page.py")
        
with col_3:
    if st.button("Go To Analysis"):
        st.switch_page("pages/analysis_home_page.py")