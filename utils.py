import streamlit as st
import os

@st.cache_data
def create_path_if_not_exists(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    return dir_name

def store_data_on_local_csv(store_path, df):
    if os.path.exists(store_path):
        df.to_csv(store_path, mode="a", header=False, index=False)
    else:
        df.to_csv(store_path, index=False)
