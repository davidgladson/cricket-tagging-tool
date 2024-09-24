import streamlit as st
import pandas as pd
import os

from constants import EXTRAS_LIST, WICKET_TYPE_LIST, MATCH_DETAILS_PATH, BASE_DATA_PATH, DB_URI

from utils import store_data_on_local_csv, get_over_string, get_current_run_rate

from db_utils import MongoDBConnector

if "runs" not in st.session_state:
    st.session_state.runs = 0
    
if "wickets" not in st.session_state:
    st.session_state.wickets = 0

if "over_num" not in st.session_state:
    st.session_state.over_num = 1
    
if "ball_num" not in st.session_state:
    st.session_state.ball_num = 1
    
if "prev_over_num" not in st.session_state:
    st.session_state.prev_over_num = 0
    
if "prev_ball_num" not in st.session_state:
    st.session_state.prev_ball_num = 0
    
if "over_ball_ctr" not in st.session_state:
    st.session_state.over_ball_ctr = 1
    

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


def reset_match_state_for_new_inning(new_inning_num):
    st.session_state.innings_num = new_inning_num
    st.session_state.over_num = 1
    st.session_state.ball_num = 1
    st.session_state.over_ball_ctr = 1
    st.session_state.runs = 0
    st.session_state.wickets = 0
    st.session_state.out_batters = set()


def clear_match_state():
    del st.session_state.innings_num
    del st.session_state.over_num
    del st.session_state.ball_num
    del st.session_state.over_ball_ctr
    del st.session_state.runs
    del st.session_state.wickets
    # del st.session_state.match_ball_by_ball_path
    del st.session_state.match_id
    del st.session_state.out_batters
    del st.session_state.prev_over_num
    del st.session_state.prev_ball_num


def parse_extras_data(extras_type_input, extras_runs_input):
    wide_runs, no_ball_runs, byes_runs, leg_byes_runs = 0, 0, 0, 0
    
    if extras_type_input == "Wide":
        wide_runs += extras_runs_input
    elif extras_type_input == "No Ball":
        no_ball_runs += extras_runs_input
    elif extras_type_input == "Byes":
        byes_runs += extras_runs_input
    elif extras_type_input == "Leg Byes":
        leg_byes_runs += extras_runs_input
        
    return wide_runs, no_ball_runs, byes_runs, leg_byes_runs


def save_and_next_ball(conn, over_num, ball_num,
                       batting_team_name, batter_name, batter_id, non_striker_name, non_striker_id, 
                       bowling_team_name, bowler_name, bowler_id,
                       batter_runs, is_extras, extras_type, extras_runs, 
                       is_wicket, wicket_type, out_batter, fielder_name):
    
    # Increment Current Scores
    total_ball_runs = batter_runs + extras_runs
    st.session_state.runs += total_ball_runs
    
    if is_wicket:
        st.session_state.wickets += 1
        st.session_state.out_batters.add(out_batter)
        
    wide_runs, no_ball_runs, byes_runs, leg_byes_runs = parse_extras_data(extras_type, extras_runs)
        
    bbb_data_list = [{
        "match_id": st.session_state.match_id, 
        "innings_num": st.session_state.innings_num, 
        "over_num": over_num,
        "ball_num": ball_num,
        "ball_id":  str(st.session_state.innings_num).zfill(1) + str(over_num).zfill(3) + str(st.session_state.over_ball_ctr).zfill(2), 
        "batting_team": batting_team_name,
        "batter_id": int(batter_id),
        "batter_name": batter_name, 
        "non_striker_id": int(non_striker_id), 
        "non_striker_name": non_striker_name,
        "bowling_team": bowling_team_name, 
        "bowler_id": int(bowler_id),
        "bowler_name": bowler_name, 
        "runs_scored": total_ball_runs,
        "batter_runs": batter_runs, 
        "is_extras": is_extras, 
        "extras_type": extras_type, 
        "extras_runs": extras_runs,
        "wide_runs": wide_runs,  
        "no_ball_runs": no_ball_runs, 
        "byes_runs": byes_runs, 
        "leg_byes_runs": leg_byes_runs, 
        "is_wicket": is_wicket, 
        "wicket_type": wicket_type, 
        "out_batter": out_batter, 
        "fielder_name": fielder_name, 
        "current_runs": st.session_state.runs, 
        "current_wickets": st.session_state.wickets  
    }]
    conn.add_new_bbb(bbb_data_list)
    
    if not is_extras:
        st.session_state.prev_over_num, st.session_state.prev_ball_num = st.session_state.over_num, st.session_state.ball_num
        st.session_state.over_num, st.session_state.ball_num, \
            st.session_state.over_ball_ctr = move_to_next_ball(over_num, ball_num, st.session_state.over_ball_ctr)
    else:
        st.session_state.over_ball_ctr += 1
    

st.set_page_config(
    page_title="Tagging Page",
    initial_sidebar_state="collapsed", 
    layout="wide"
)

@st.cache_resource
def connect_db(db_uri):
    return MongoDBConnector(DB_URI=db_uri)

connector = connect_db(DB_URI)

if ("match_id" not in st.session_state) or ("innings_num" not in st.session_state):
    st.warning("Please select a match and an inning to score!", icon="⚠️")
    st.switch_page("home_page.py")
    
match_details_fetched = connector.get_single_match_details(match_id=st.session_state.match_id)
ball_by_ball_data = match_details_fetched.get("ball_by_ball_data", None)
players_data_fetched = match_details_fetched.get("lineups", None)

if "out_batters" not in st.session_state:
    if ball_by_ball_data is not None and len(ball_by_ball_data) > 0:
        data_df = pd.DataFrame(ball_by_ball_data)
        st.session_state.out_batters = set(data_df[data_df["is_wicket"]].out_batter.unique())
    else:
        st.session_state.out_batters = set()

match_venue = match_details_fetched["venue"]
match_date = match_details_fetched["match_start_date"]
team_1_name = match_details_fetched["team_1"]
team_2_name = match_details_fetched["team_2"]
toss_winner = match_details_fetched["toss_winner"]
toss_choice = match_details_fetched["toss_choice"]

if toss_choice == "Batting":
    odd_inning_batting_team = toss_winner
    even_inning_batting_team = team_1_name if team_1_name != odd_inning_batting_team else team_2_name    
else:
    even_inning_batting_team = toss_winner
    odd_inning_batting_team = team_1_name if team_1_name != even_inning_batting_team else team_2_name
    
batting_team = odd_inning_batting_team if int(st.session_state.innings_num) % 2 == 1 else even_inning_batting_team
bowling_team = even_inning_batting_team if int(st.session_state.innings_num) % 2 == 1 else odd_inning_batting_team

if players_data_fetched is not None and len(players_data_fetched) > 0: 
    players_data_fetched = pd.DataFrame(players_data_fetched)
    batter_list = players_data_fetched[players_data_fetched["team_name"] == batting_team].player_name.unique().tolist()
    bowler_list = players_data_fetched[players_data_fetched["team_name"] == bowling_team].player_name.unique().tolist()
else:
    batter_list = []
    bowler_list = []

# Filter Out Dismissed Batters
batter_list = list(set(batter_list).difference(st.session_state.out_batters))
    

col_1, col_2 = st.columns(2)

with col_1:
    st.write("#### Tagging Page")

    st.text("Match Venue: {}".format(match_venue))
    st.text("Match Date: {}".format(match_date))
    st.text("Batting Team: {}".format(batting_team))
    st.text("Bowling Team: {}".format(bowling_team))
    st.text("Innings: {}".format(st.session_state.innings_num))
    
    over_string = get_over_string(st.session_state.prev_over_num, st.session_state.prev_ball_num)    
        
    st.text("Current Score: {}/{} {}".format(st.session_state.runs, st.session_state.wickets, over_string))    
    st.text("Current Run Rate: {:.2f}".format(get_current_run_rate(st.session_state.runs, 
                                                                   st.session_state.prev_over_num, 
                                                                   st.session_state.prev_ball_num)))
    
st.divider()
    
col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)    

with col_1:
    over_num_input = st.number_input("Over Number:", value=st.session_state.over_num, disabled=True)
    ball_num_input = st.number_input("Ball Number:", value=st.session_state.ball_num, disabled=True)
    
with col_2:
    batter_name_input = st.selectbox("Batter:", batter_list, index=None)
    
    if batter_name_input is not None:
        batter_id_input = players_data_fetched[players_data_fetched["player_name"] == batter_name_input]["player_id"].iloc[0]
        non_striker_list = set(batter_list).difference(set([batter_name_input]))
        non_striker_name_input = st.selectbox("Non Striker:", non_striker_list)
        
        if non_striker_name_input is not None:
            non_striker_id_input = players_data_fetched[players_data_fetched["player_name"] == non_striker_name_input]["player_id"].iloc[0]
        else:
            non_striker_id_input = None
    else:
        batter_id_input = None
        non_striker_name_input = st.selectbox("Non Striker:", batter_list, disabled=True)   
        non_striker_id_input = None 
    
with col_3:
    bowler_name_input = st.selectbox("Bowler:", bowler_list, index=None)
    if bowler_name_input is not None:
        bowler_id_input = players_data_fetched[players_data_fetched["player_name"] == bowler_name_input]["player_id"].iloc[0]
    else:
        bowler_id_input = None

with col_4:
    batter_runs_input = st.number_input("Batter Runs", value=0)

with col_5:
    is_extras_input = st.checkbox("Extras?", value=False)
    if is_extras_input:
        extras_type_input = st.selectbox("Extra Type:", EXTRAS_LIST, index=None)
        extras_runs_input = st.number_input("Extra Runs", value=None)
    else:
        extras_type_input = None
        extras_runs_input = 0
    
with col_6:
    is_wicket_input = st.checkbox("Wicket?", value=False)
    if is_wicket_input:
        
        out_batter_options = []
        if batter_name_input is not None:
            out_batter_options.append(batter_name_input)
        if non_striker_name_input is not None:
            out_batter_options.append(non_striker_name_input)
            
        wicket_type_input = st.selectbox("Wicket Type:", WICKET_TYPE_LIST, index=None)
        out_batter_input = st.selectbox("Dismissed Batter:", out_batter_options, index=None)
        fielder_name_input = st.selectbox("Fielder Name:", bowler_list, index=None)
    else:
        wicket_type_input = None
        out_batter_input = None
        fielder_name_input = None
        
st.divider()

col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)  

with col_1: 
    if st.button("End Inning"):
        reset_match_state_for_new_inning(st.session_state.innings_num + 1)
        st.rerun()
        
with col_2: 
    if st.button("End Match"):
        clear_match_state()
        st.switch_page("home_page.py")
        
with col_5: 
    if st.button("Pause"):
        clear_match_state()
        st.switch_page("home_page.py")

with col_6: 
    if st.button("Save and Next"):
        save_and_next_ball(connector, over_num_input, ball_num_input, 
                           batting_team, batter_name_input, batter_id_input, non_striker_name_input, non_striker_id_input, 
                           bowling_team, bowler_name_input, bowler_id_input,
                           batter_runs_input, is_extras_input, extras_type_input, extras_runs_input, 
                           is_wicket_input, wicket_type_input, out_batter_input, fielder_name_input)
        st.rerun()