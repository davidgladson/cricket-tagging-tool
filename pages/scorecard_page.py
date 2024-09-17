import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Scorecard View",
    initial_sidebar_state="collapsed"
)

st.write("# This is Scorecard View!")

if st.button("Home"):
    st.switch_page("home_page.py")
    
data_df = pd.read_csv("test_data/sample_tagged_data.csv")

st.dataframe(data=data_df)