import streamlit as st
import datetime
import pandas as pd
import os

VENUE_LIST = ["Wankhede", "MCG", "Chinnaswamy"]
TEAM_LIST = ["India", "NEW Zealand", "Australia"]
TOSS_CHOICE_LIST = ["Batting", "Fielding"]

BASE_DATA_PATH = "data"
MATCH_DETAILS_PATH = "{}/match_details.csv".format(BASE_DATA_PATH)

if "match_id" not in st.session_state:
    st.session_state.match_id = None

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

def store_match_details(venue, date, time, team_1_name, team_1_list, team_2_name, team_2_list, toss_winner, toss_choice):
    unique_match_id = "{}_{}_{}".format(str(team_1_name).replace(" ", "_").upper().strip(), 
                                        str(team_2_name).replace(" ", "_").upper().strip(), 
                                        date.strftime('%Y%m%d'))
        
    st.session_state.match_id = unique_match_id
    
    match_data_path = "{}/{}".format(BASE_DATA_PATH, unique_match_id)
    create_path_if_not_exists(match_data_path)
    
    data_df = pd.DataFrame([{
        "match_id": unique_match_id, 
        "venue": venue, 
        "match_start_date": date.strftime("%Y-%m-%d"),
        "match_start_time": time.strftime("%H:%M"),
        "team_1": team_1_name, 
        "team_2": team_2_name, 
        "toss_winner": toss_winner, 
        "toss_choice": toss_choice        
    }])
    store_data_on_local_csv(MATCH_DETAILS_PATH, data_df)
    
    team_1_player_names = str(team_1_list).split(",")
    team_2_player_names = str(team_2_list).split(",")    
    team_1_player_rows = [{"player_name": player_name.strip(), "team_name": team_1_name} for player_name in team_1_player_names]
    team_2_player_rows = [{"player_name": player_name.strip(), "team_name": team_2_name} for player_name in team_2_player_names]
    
    player_data_df = pd.DataFrame(team_1_player_rows + team_2_player_rows)
    player_data_df_path = "{}/players.csv".format(match_data_path)
    store_data_on_local_csv(player_data_df_path, player_data_df)


st.set_page_config(
    page_title="Cricket Tagging Tool",
    initial_sidebar_state="collapsed"
)

st.write("#### Welcome to Cricket Tagging Tool!")
st.divider()

# Match Details Input Section
        
col_1, col_2 = st.columns(2)

with col_1:
    venue_in = st.selectbox("Match Venue:", VENUE_LIST)
        
    st.divider()
    
    team_name_1_in = st.selectbox("Team 1:", TEAM_LIST)    
    team_list_1_in = st.text_area("Playing XI Team 1:")
    
    st.divider()
    
    toss_winner_in = st.selectbox("Toss Won By:", TEAM_LIST)
    

with col_2:
    sub_col_1, sub_col_2 = st.columns(2)
    
    with sub_col_1:
        date_in = st.date_input("Match Start Date:", datetime.datetime.now())
    
    with sub_col_2:
        time_in = st.time_input("Match Start Time:", datetime.datetime.now())
        
    st.divider()
    
    team_name_2_in = st.selectbox("Team 2:", TEAM_LIST)
    team_list_2_in = st.text_area("Playing XI Team 2:")
    
    st.divider()
    
    toss_choice_in = st.selectbox("Toss Choice:", TOSS_CHOICE_LIST)
    
col_1, col_2, col_3 = st.columns(3)
    
with col_2:
    if st.button("Save Match Details"):
        store_match_details(venue_in, date_in, time_in, 
                            team_name_1_in, team_list_1_in, team_name_2_in, team_list_2_in, 
                            toss_winner_in, toss_choice_in)
        st.switch_page("home_page.py")

        
st.divider()
    

col_1, col_2 = st.columns(2)

with col_1:
    
    sub_col_1, sub_col_2, sub_col_3 = st.columns(3)
    
    with sub_col_1:
        innings_num_in= st.selectbox("Select Innings: ", [1,2])
    
    with sub_col_2:
        if st.button("Start"):
            st.session_state.innings_num = int(innings_num_in)
            st.switch_page("pages/tagging_page.py")
            
    with sub_col_3:
        if st.button("Resume"):
            st.session_state.innings_num = int(innings_num_in)
            st.switch_page("pages/tagging_page.py")

with col_2:
    sub_col_1, sub_col_2 = st.columns(2)
    
    with sub_col_1:
        if st.button("End Match"):
            st.switch_page("home_page.py")
    
    with sub_col_2:
        if st.button("View Scorecard"):
            st.switch_page("pages/scorecard_page.py")