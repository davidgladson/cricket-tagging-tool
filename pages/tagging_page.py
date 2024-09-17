import streamlit as st

st.set_page_config(
    page_title="Tagging Page",
    initial_sidebar_state="collapsed"
)


st.write("# This is Tagging Page!")

if st.button("Home"):
    st.switch_page("home_page.py")
    
if "runs" not in st.session_state:
    st.session_state.runs = 0
    
if "wickets" not in st.session_state:
    st.session_state.wickets = 0

if "over_num" not in st.session_state:
    st.session_state.over_num = 1
    
if "ball_num" not in st.session_state:
    st.session_state.ball_num = 1
    
st.write("Current Score: {}/{}".format(st.session_state.runs, st.session_state.wickets))
    

def save_and_next_ball(runs, wickets):
    st.session_state.runs += runs
    st.session_state.wickets += wickets
    

runs_input = st.number_input(
    "Runs", value=None, placeholder="Type a number..."
)
wickets_input = st.number_input(
    "Wickets", value=None, placeholder="Type a number..."
)



if st.button("Save and Next"):
    save_and_next_ball(runs_input, wickets_input)
    st.rerun()