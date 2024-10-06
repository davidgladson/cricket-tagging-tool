import streamlit as st
import pandas as pd
import os

from constants import EXTRAS_LIST, SHOT_TYPE_OPTIONS, DB_URI, BALL_LINE_OPTIONS, BALL_LENGTH_OPTIONS, WAGON_ZONE_OPTIONS

from utils import get_over_string, get_current_run_rate, get_next_ball_players

from db_utils import MongoDBConnector


st.set_page_config(
    page_title="Tagging Page Advanced Data",
    initial_sidebar_state="collapsed", 
    layout="wide"
)

#============================================Password Check Function===================
# Password check function
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.error("Unauthorized access! Please login from the main page.")
    return False

# Check if the password is correct before allowing access to this page
if not check_password():
    st.stop()
    
#============================================Password Check Function===================

if "over_num_adv" not in st.session_state:
    st.session_state.over_num_adv = 1
    
if "ball_num_adv" not in st.session_state:
    st.session_state.ball_num_adv = 1
    
if "prev_over_num_adv" not in st.session_state:
    st.session_state.prev_over_num_adv = 0
    
if "prev_ball_num_adv" not in st.session_state:
    st.session_state.prev_ball_num_adv = 0
    
if "over_ball_ctr_adv" not in st.session_state:
    st.session_state.over_ball_ctr_adv = 1
    

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
    st.session_state.innings_num_adv = new_inning_num
    st.session_state.over_num_adv = 1
    st.session_state.ball_num_adv = 1
    st.session_state.over_ball_ctr_adv = 1
    st.session_state.prev_over_num_adv = 0
    st.session_state.prev_ball_num_adv = 0


def clear_match_state():
    del st.session_state.innings_num_adv
    del st.session_state.over_num_adv
    del st.session_state.ball_num_adv
    del st.session_state.over_ball_ctr_adv
    del st.session_state.match_id
    del st.session_state.prev_over_num_adv
    del st.session_state.prev_ball_num_adv


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


def reset_inputs():
    st.session_state.ball_speed_in = None
    st.session_state.ball_line = None
    st.session_state.ball_length = None
    st.session_state.shot_type = None
    st.session_state.wagon_zone = None
    st.session_state.batter_control_in = False
    st.session_state.is_extras = False
    st.session_state.extras_type = None
    

@st.dialog("Inputs Missing!")
def inputs_missing():
    st.write("Entering All Details is Mandatory!")
    

def save_and_next_ball(conn, over_num, ball_num,
                       ball_speed, line, length, 
                       shot_type, batter_control, wagon_zone, 
                       is_extras, extras_type):
    
    if any([x is None for x in [over_num, ball_num, line, length, shot_type, batter_control]]):
        inputs_missing()
        return 
        
    bbb_advanced_data_list = [{
        "match_id": st.session_state.match_id, 
        "innings_num": st.session_state.innings_num_adv, 
        "over_num": over_num,
        "ball_num": ball_num,
        "ball_id":  str(st.session_state.innings_num_adv).zfill(1) + str(over_num).zfill(3) + str(st.session_state.over_ball_ctr_adv).zfill(2), 
        "ball_speed": ball_speed,
        "ball_line": line, 
        "ball_length": length,
        "shot_type": shot_type,
        "batter_control": None if batter_control is None else (1 if batter_control else 0),
        "wagon_zone": wagon_zone, 
        "is_extras": is_extras, 
        "extras_type": extras_type
    }]
    conn.add_new_bbb_advanced(bbb_advanced_data_list)
    
    if not is_extras or (is_extras and extras_type in ["Byes", "Leg Byes"]):
        st.session_state.prev_over_num_adv, st.session_state.prev_ball_num_adv = st.session_state.over_num_adv, st.session_state.ball_num_adv
        st.session_state.over_num_adv, st.session_state.ball_num_adv, \
            st.session_state.over_ball_ctr_adv = move_to_next_ball(over_num, ball_num, st.session_state.over_ball_ctr_adv)
    else:
        st.session_state.over_ball_ctr_adv += 1
    
    reset_inputs()


@st.cache_resource
def connect_db(db_uri):
    return MongoDBConnector(DB_URI=db_uri)

connector = connect_db(DB_URI)

if ("match_id" not in st.session_state) or ("innings_num" not in st.session_state):
    st.warning("Please select a match and an inning to score!", icon="⚠️")
    st.switch_page("pages/tagging_home_page.py")
    
match_details_fetched = connector.get_single_match_details(match_id=st.session_state.match_id)
ball_by_ball_data = match_details_fetched.get("ball_by_ball_data_advanced", None)
players_data_fetched = match_details_fetched.get("lineups", None)

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
    
batting_team = odd_inning_batting_team if int(st.session_state.innings_num_adv) % 2 == 1 else even_inning_batting_team
bowling_team = even_inning_batting_team if int(st.session_state.innings_num_adv) % 2 == 1 else odd_inning_batting_team

col_1, col_2 = st.columns(2)

with col_1:
    st.write("#### Tagging Page")

    st.text("Match Venue: {}".format(match_venue))
    st.text("Match Date: {}".format(match_date))
    st.text("Batting Team: {}".format(batting_team))
    st.text("Bowling Team: {}".format(bowling_team))
    st.text("Innings: {}".format(st.session_state.innings_num_adv))
    
    over_string = get_over_string(st.session_state.prev_over_num_adv, st.session_state.prev_ball_num_adv)    
        
    st.text("Overs Finished: {}".format(over_string))
    
    
with col_2:
    st.image("images/wagon_zone_info.png", caption="Wagon Zones for Reference")
    
st.divider()
    
col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)    

with col_1:
    over_num_input = st.number_input("Over Number:", value=st.session_state.over_num_adv, disabled=True)
    ball_num_input = st.number_input("Ball Number:", value=st.session_state.ball_num_adv, disabled=True)
    
with col_2:
    ball_speed_input = st.number_input("Ball Speed: ", value=None, min_value=0.0, key="ball_speed_in")

with col_3:
    line_input = st.selectbox("Ball Line:", BALL_LINE_OPTIONS, index=None, key="ball_line")
    length_input = st.selectbox("Ball Length:", BALL_LENGTH_OPTIONS, index=None, key="ball_length")

with col_4:
    shot_type_input = st.selectbox("Shot Type:", SHOT_TYPE_OPTIONS, index=None, key="shot_type")
    batter_control_input = st.toggle("Batter In Control of the shot?", key="batter_control_in")
    
with col_5:
    wagon_zone_input = st.selectbox("Wagon Zone:", WAGON_ZONE_OPTIONS, index=None, key="wagon_zone")

with col_6:
    is_extras_input = st.checkbox("Extras?", value=False, key="is_extras")
    if is_extras_input:
        extras_type_input = st.selectbox("Extra Type:", EXTRAS_LIST, index=None, key="extras_type")
    else:
        extras_type_input = None
            
st.divider()

col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)  

with col_1: 
    if st.button("End Inning"):
        reset_match_state_for_new_inning(st.session_state.innings_num_adv + 1)
        st.rerun()
        
with col_2: 
    if st.button("End Match"):
        clear_match_state()
        st.switch_page("pages/tagging_home_page.py")
        
with col_5: 
    if st.button("Pause"):
        clear_match_state()
        st.switch_page("pages/tagging_home_page.py")

with col_6: 
    st.button("Save and Next", on_click=save_and_next_ball, 
              args=(connector, over_num_input, ball_num_input,
                    ball_speed_input, line_input, length_input,
                    shot_type_input, batter_control_input, wagon_zone_input,
                    is_extras_input, extras_type_input))