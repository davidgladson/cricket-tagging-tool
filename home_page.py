import streamlit as st
import datetime
import pandas as pd
import os

from constants import VENUE_LIST, TOSS_CHOICE_LIST, BASE_DATA_PATH, MATCH_DETAILS_PATH, DB_URI
from utils import create_path_if_not_exists, store_data_on_local_csv, get_over_string, get_current_run_rate, get_squad_details, \
    match_list_formatter, move_to_next_ball, get_lineup_display_data, parse_squad_data_input
from db_utils import MongoDBConnector

if "match_id" not in st.session_state:
    st.session_state.match_id = None
    
if "ball_by_ball_data" not in st.session_state:
    st.session_state.ball_by_ball_data = None

def store_match_details(conn, venue, date, time, team_1_name, team_1_df, team_2_name, team_2_df, toss_winner, toss_choice):
    unique_match_id = "{}_{}_{}".format(str(team_1_name).replace(" ", "-").upper().strip(), 
                                        str(team_2_name).replace(" ", "-").upper().strip(), 
                                        date.strftime('%Y%m%d'))
    
    match_data_path = "{}/{}".format(BASE_DATA_PATH, unique_match_id)
    create_path_if_not_exists(match_data_path)
    
    match_details = [{
        "match_id": unique_match_id, 
        "venue": venue, 
        "match_start_date": date.strftime("%Y-%m-%d"),
        "match_start_time": time.strftime("%H:%M"),
        "team_1": team_1_name, 
        "team_2": team_2_name, 
        "toss_winner": toss_winner, 
        "toss_choice": toss_choice        
    }]
    conn.add_new_matches(match_details)    
    
    player_data_df = pd.concat([team_1_df[team_1_df["playing"]], team_2_df[team_2_df["playing"]]])
    player_data_df["match_id"] = unique_match_id
    conn.add_new_lineups(player_data_df.to_dict('records'))

st.set_page_config(
    page_title="Cricket Tagging Tool",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def connect_db(db_uri):
    return MongoDBConnector(DB_URI=db_uri)

connector = connect_db(DB_URI)

st.write("#### Welcome to Cricket Tagging Tool!")

tab_1, tab_2 = st.tabs(["Select From Existing Games", "Start A New Match"])

with tab_1:
    if os.path.exists(MATCH_DETAILS_PATH):
        matches = pd.DataFrame(connector.get_matches())
        match_id_list = matches.match_id.unique().tolist()
    else:
        match_id_list = []
    match_id_in = st.selectbox("Select a Match to View Details/Score:", match_id_list, index=None, 
                               format_func=match_list_formatter)
    
    if st.button("Select Match"):
        st.session_state.match_id = match_id_in

        match_details_fetched = connector.get_single_match_details(match_id=st.session_state.match_id)
        st.session_state.ball_by_ball_data = match_details_fetched["ball_by_ball_data"]
        
        match_venue = match_details_fetched["venue"]
        match_date = match_details_fetched["match_start_date"]
        team_1_name = match_details_fetched["team_1"]
        team_2_name = match_details_fetched["team_2"]

        st.text("{} vs {}".format(team_1_name, team_2_name))
        st.text("Match Venue: {}".format(match_venue))
        st.text("Match Date: {}".format(match_date))
        
        if st.session_state.ball_by_ball_data is not None and len(st.session_state.ball_by_ball_data) > 0:
            last_ball = st.session_state.ball_by_ball_data[-1]
            current_over_num = last_ball["over_num"]
            current_ball_num = last_ball["ball_num"]
            current_over_ball_ctr = int(str(last_ball["ball_id"])[-2:])
            current_inning = max([x["innings_num"] for x in st.session_state.ball_by_ball_data])
            
            st.session_state.innings_num = current_inning
            st.session_state.over_num, st.session_state.ball_num, \
                st.session_state.over_ball_ctr = move_to_next_ball(current_over_num, current_ball_num, current_over_ball_ctr)
            st.session_state.runs = int(last_ball["current_runs"])
            st.session_state.wickets = int(last_ball["current_wickets"])
            st.session_state.prev_over_num = int(last_ball["over_num"])
            st.session_state.prev_ball_num = int(last_ball["ball_num"])
            
            over_string = get_over_string(st.session_state.prev_over_num, st.session_state.prev_ball_num)

            st.text("Current Inning: {}".format(st.session_state.innings_num))
            st.text("Current Score: {}/{} {}".format(st.session_state.runs, st.session_state.wickets, over_string))
            st.text("Current Run Rate: {:.2f}".format(get_current_run_rate(st.session_state.runs, 
                                                                           st.session_state.prev_over_num, 
                                                                           st.session_state.prev_ball_num)))
    
        else:
            st.text("No Ball By Ball Data Available Yet!")
            st.session_state.innings_num = 1
            st.session_state.over_num, st.session_state.ball_num, st.session_state.over_ball_ctr = 1, 1, 1
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
            if st.session_state.match_id is None or innings_num_in is None:
                st.rerun()
            else:
                st.session_state.innings_num = int(innings_num_in)
            st.switch_page("pages/tagging_page.py")
            
    with sub_col_3:
        if st.session_state.ball_by_ball_data is not None and len(st.session_state.ball_by_ball_data) > 0:
            bbb_data_download = pd.DataFrame(st.session_state.ball_by_ball_data)
            download_disabled = False
        else:
            bbb_data_download = pd.DataFrame()
            download_disabled = True
            
        st.download_button(
            label="Download Data",
            data=bbb_data_download.to_csv(index=False).encode("utf-8"),
            file_name="ball_by_ball_data.csv",
            mime="text/csv", 
            disabled=download_disabled)

    with sub_col_4:
        scorecard_disabled = (st.session_state.ball_by_ball_data is None) or (len(st.session_state.ball_by_ball_data) <= 0)
        if st.button("View Scorecard", disabled=scorecard_disabled):
            st.switch_page("pages/scorecard_page.py")

with tab_2:
    squads = pd.DataFrame(connector.get_squads())
    TEAM_LIST = squads.team_name.unique().tolist()
    
    # Match Details Input Section
            
    col_1, col_2 = st.columns(2)

    with col_1:
        venue_in = st.selectbox("Match Venue:", VENUE_LIST, index=None)
            
        st.divider()
        
        team_name_1_in = st.selectbox("Team 1:", TEAM_LIST, index=None)
        if team_name_1_in is not None:
            team_1_squad, col_config = get_lineup_display_data(squads, team_name_1_in)
            team_list_1_in = st.data_editor(team_1_squad, 
                                            num_rows="fixed", hide_index=True, column_config=col_config, height=563)

    with col_2:
        sub_col_1, sub_col_2 = st.columns(2)
        
        with sub_col_1:
            date_in = st.date_input("Match Start Date:", datetime.datetime.now())
        
        with sub_col_2:
            time_in = st.time_input("Match Start Time:", datetime.datetime.now())
            
        st.divider()
        
        if team_name_1_in is not None:
            other_team_list = set(TEAM_LIST).difference(set([team_name_1_in])) 
            other_team_picker_disabled = False
        else: 
            other_team_list = TEAM_LIST
            other_team_picker_disabled = True
        
        team_name_2_in = st.selectbox("Team 2:", other_team_list, index=None, disabled=other_team_picker_disabled)
        if team_name_2_in is not None:
            team_2_squad, col_config = get_lineup_display_data(squads, team_name_2_in)
            team_list_2_in = st.data_editor(team_2_squad, 
                                            num_rows="fixed", hide_index=True, column_config=col_config, height=563)
        
    with col_1:    
        toss_team_list = list(filter(lambda x: x is not None, [team_name_1_in, team_name_2_in]))
        toss_winner_in = st.selectbox("Toss Won By:", toss_team_list, index=None)
        
    with col_2:    
        toss_choice_in = st.selectbox("Toss Choice:", TOSS_CHOICE_LIST, index=None)
        
    _, _, col_3, _, _ = st.columns(5)
        
    with col_3:
        if st.button("Save Match Details"):
            store_match_details(connector, venue_in, date_in, time_in, 
                                team_name_1_in, team_list_1_in, team_name_2_in, team_list_2_in, 
                                toss_winner_in, toss_choice_in)
            st.switch_page("home_page.py")