import streamlit as st
import datetime
import pandas as pd
import os

from constants import VENUE_LIST, TEAM_LIST, TOSS_CHOICE_LIST, BASE_DATA_PATH, MATCH_DETAILS_PATH
from utils import create_path_if_not_exists, store_data_on_local_csv

if "match_id" not in st.session_state:
    st.session_state.match_id = None

def store_match_details(venue, date, time, team_1_name, team_1_list, team_2_name, team_2_list, toss_winner, toss_choice):
    unique_match_id = "{}_{}_{}".format(str(team_1_name).replace(" ", "_").upper().strip(), 
                                        str(team_2_name).replace(" ", "_").upper().strip(), 
                                        date.strftime('%Y%m%d'))
    
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
    team_1_player_rows = [{"match_id": unique_match_id, "team_name": team_1_name, "player_name": player_name.strip()} 
                          for player_name in team_1_player_names]
    team_2_player_rows = [{"match_id": unique_match_id, "team_name": team_2_name, "player_name": player_name.strip()} 
                          for player_name in team_2_player_names]
    
    player_data_df = pd.DataFrame(team_1_player_rows + team_2_player_rows)
    player_data_df_path = "{}/players.csv".format(match_data_path)
    store_data_on_local_csv(player_data_df_path, player_data_df)


@st.cache_data
def move_to_next_ball(over_num, ball_num, over_ball_ctr):
    if ball_num == 6:
        next_ball_num = 1
        next_over_num = over_num + 1
        next_over_ball_ctr = 1
    else:
        next_ball_num = ball_num + 1
        next_over_num = over_num
        next_over_ball_ctr = over_ball_ctr + 1
        
    return next_over_num, next_ball_num, next_over_ball_ctr


st.set_page_config(
    page_title="Cricket Tagging Tool",
    initial_sidebar_state="collapsed"
)

st.write("#### Welcome to Cricket Tagging Tool!")

tab_1, tab_2 = st.tabs(["Select From Existing Games", "Start A New Match"])

with tab_1:
    if os.path.exists(MATCH_DETAILS_PATH):
        matches = pd.read_csv(MATCH_DETAILS_PATH)
        match_id_list = matches.match_id.unique().tolist()
    else:
        match_id_list = []
    match_id_in = st.selectbox("Select a Match to View Details/Score:", match_id_list)
    
    if st.button("Select Match"):
        st.session_state.match_id = match_id_in
        
        st.session_state.match_ball_by_ball_path = "{}/{}/ball_by_ball.csv".format(BASE_DATA_PATH,
                                                                                   st.session_state.match_id)  
        
        if os.path.exists(st.session_state.match_ball_by_ball_path):
            ball_by_ball_data = pd.read_csv(st.session_state.match_ball_by_ball_path)
            ball_by_ball_data = ball_by_ball_data.sort_values(by=["ball_id"])
        else:
            ball_by_ball_data = None
        
        match_details_fetched = matches[matches["match_id"] == st.session_state.match_id].iloc[0]
        
        match_venue = match_details_fetched["venue"]
        match_date = match_details_fetched["match_start_date"]
        team_1_name = match_details_fetched["team_1"]
        team_2_name = match_details_fetched["team_2"]

        st.text("{} vs {}".format(team_1_name, team_2_name))
        st.text("Match Venue: {}".format(match_venue))
        st.text("Match Date: {}".format(match_date))
        
        if ball_by_ball_data is not None:
            last_ball = ball_by_ball_data.iloc[-1]
            current_over_num = last_ball["over_num"]
            current_ball_num = last_ball["ball_num"]
            current_over_ball_ctr = int(str(last_ball["ball_id"])[-2:])
            current_inning = ball_by_ball_data.innings_num.max()
            
            st.session_state.innings_num = current_inning
            st.session_state.over_num, st.session_state.ball_num, \
                st.session_state.over_ball_ctr = move_to_next_ball(current_over_num, current_ball_num, current_over_ball_ctr)
            st.session_state.runs = int(last_ball["current_runs"])
            st.session_state.wickets = int(last_ball["current_wickets"])

            st.text("Current Inning: {}".format(st.session_state.innings_num))
            st.text("Current Score: {}/{}".format(st.session_state.runs, st.session_state.wickets))
        else:
            st.text("No Ball By Ball Data Available Yet!")
            st.session_state.innings_num = 1
            st.session_state.over_num, st.session_state.ball_num, \
                st.session_state.over_ball_ctr = 1, 1, 1
            st.session_state.runs = 0
            st.session_state.wickets = 0
            
    st.divider()

    sub_col_1, sub_col_2, sub_col_3, sub_col_4 = st.columns(4)
        
    with sub_col_1:
        current_inning_num_index = st.session_state.get("innings_num", None)
        if current_inning_num_index is not None:
            current_inning_num_index = int(current_inning_num_index) - 1
        innings_num_in= st.selectbox("Select Innings: ", [1,2,3,4], index=current_inning_num_index)
    
    with sub_col_2:
        if st.button("Start/Resume Scoring"):
            st.session_state.innings_num = int(innings_num_in)
            st.switch_page("pages/tagging_page.py")
            
    with sub_col_3:
        if st.button("End Match"):
            st.switch_page("home_page.py")

    with sub_col_4:
        if st.button("View Scorecard"):
            st.switch_page("pages/scorecard_page.py")

with tab_2:
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