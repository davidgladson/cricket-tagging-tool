import streamlit as st
import pandas as pd
import os

EXTRAS_LIST = ["No Ball", "Wide", "Byes", "Leg Byes"]
WICKET_TYPE_LIST = ["Bowled", "LBW", "Caught", "Stumped", "Run Out", "Hit Wicket"]

BASE_DATA_PATH = "data"
MATCH_DETAILS_PATH = "{}/match_details.csv".format(BASE_DATA_PATH)

if "runs" not in st.session_state:
    st.session_state.runs = 0
    
if "wickets" not in st.session_state:
    st.session_state.wickets = 0

if "over_num" not in st.session_state:
    st.session_state.over_num = 1
    
if "ball_num" not in st.session_state:
    st.session_state.ball_num = 1
    
def store_data_on_local_csv(store_path, df):
    if os.path.exists(store_path):
        df.to_csv(store_path, mode="a", header=False, index=False)
    else:
        df.to_csv(store_path, index=False)

@st.cache_data
def fetch_running_match_data(match_id):
    match_details_df = pd.read_csv(MATCH_DETAILS_PATH)
    match_details = match_details_df[match_details_df["match_id"] == match_id]
    
    players_data_path = "{}/{}/players.csv".format(BASE_DATA_PATH, match_id)
    players_df = pd.read_csv(players_data_path)
    
    return match_details.iloc[0], players_df

@st.cache_data
def move_to_next_ball(over_num, ball_num):
    if ball_num == 6:
        next_ball_num = 1
        next_over_num = over_num + 1
    else:
        next_ball_num = ball_num + 1
        next_over_num = over_num
        
    return next_over_num, next_ball_num

def save_and_next_ball(over_num, ball_num,
                       batter_name, non_striker_name, bowler_name,
                       runs, is_extras, extras_type, extras_runs, 
                       is_wicket, wicket_type, out_batter):
        
    data_df = pd.DataFrame([{
        "match_id": st.session_state.match_id, 
        "innings_num": st.session_state.innings_num, 
        "over_num": over_num,
        "ball_num": ball_num,
        "ball_id": None, 
        "batter_id": None,
        "batter_name": batter_name, 
        "non_striker_id": None, 
        "non_striker_name": non_striker_name, 
        "bowler_id": None,
        "bowler_name": bowler_name, 
        "runs_scored": runs, 
        "is_extras": is_extras, 
        "extras_type": extras_type, 
        "extras_runs": extras_runs, 
        "is_wicket": is_wicket, 
        "wicket_type": wicket_type, 
        "out_batter": out_batter      
    }])
    store_data_on_local_csv(st.session_state.match_ball_by_ball_path, data_df)
    
    # Increment Current Scores
    st.session_state.runs += runs
        
    if is_wicket:
        st.session_state.wickets += 1
    
    if not is_extras:
        st.session_state.over_num, st.session_state.ball_num = move_to_next_ball(over_num, ball_num)
    

st.set_page_config(
    page_title="Tagging Page",
    initial_sidebar_state="collapsed"
)

st.write("#### Tagging Page")

if ("match_id" not in st.session_state) or ("innings_num" not in st.session_state):
    st.warning("Please select a match and an inning to score!", icon="⚠️")
    st.switch_page("home_page.py")
    
match_details_fetched, players_data_fetched = fetch_running_match_data(st.session_state.match_id)   
 
st.session_state.match_ball_by_ball_path = "{}/{}/ball_by_ball.csv".format(BASE_DATA_PATH, 
                                                                           st.session_state.match_id)    

match_venue = match_details_fetched["venue"]
match_date = match_details_fetched["match_start_date"]
team_1_name = match_details_fetched["team_1"]
team_2_name = match_details_fetched["team_2"]
toss_winner = match_details_fetched["toss_winner"]
toss_choice = match_details_fetched["toss_choice"]

print(st.session_state.match_id)
print(st.session_state.innings_num)

if toss_choice == "Batting":
    odd_inning_batting_team = toss_winner
    even_inning_batting_team = team_1_name if team_1_name != odd_inning_batting_team else team_2_name    
else:
    even_inning_batting_team = toss_winner
    odd_inning_batting_team = team_1_name if team_1_name != even_inning_batting_team else team_2_name
    
batting_team = odd_inning_batting_team if int(st.session_state.innings_num) % 2 == 1 else even_inning_batting_team
bowling_team = even_inning_batting_team if int(st.session_state.innings_num) % 2 == 1 else odd_inning_batting_team

batter_list = players_data_fetched[players_data_fetched["team_name"] == batting_team].player_name.unique().tolist()
bowler_list = players_data_fetched[players_data_fetched["team_name"] == bowling_team].player_name.unique().tolist()
    

col_1, col_2 = st.columns(2)

with col_1:
    st.text("Match Venue: {}".format(match_venue))
    st.text("Match Date: {}".format(match_date))
    st.text("Batting Team: {}".format(batting_team))
    st.text("Bowling Team: {}".format(bowling_team))
    st.text("Innings: {}".format(st.session_state.innings_num))
    st.text("Current Score: {}/{}".format(st.session_state.runs, st.session_state.wickets))
    
with col_2:
    st.image("images/coming_soon.png")
    
    
col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)    

with col_1:
    over_num_input = st.number_input("Over Number:", value=st.session_state.over_num)
    ball_num_input = st.number_input("Ball Number:", value=st.session_state.ball_num)
    
with col_2:
    batter_name_input = st.selectbox("Batter:", batter_list)
    non_striker_name_input = st.selectbox("Non Striker:", batter_list)
    
with col_3:
    bowler_name_input = st.selectbox("Bowler:", bowler_list)

with col_4:
    runs_input = st.number_input("Total Runs", value=None)

with col_5:
    is_extras_input = st.checkbox("Extras?", value=False)
    if is_extras_input:
        extras_type_input = st.selectbox("Extra Type:", EXTRAS_LIST)
        extras_runs_input = st.number_input("Extra Runs", value=None)
    else:
        extras_type_input = None
        extras_runs_input = None
    
with col_6:
    is_wicket_input = st.checkbox("Wicket?", value=False)
    if is_wicket_input:
        wicket_type_input = st.selectbox("Wicket Type:", WICKET_TYPE_LIST)
        out_batter_input = st.selectbox("Dismissed Batter:", batter_list)
    else:
        wicket_type_input = None
        out_batter_input = None

col_1, col_2, col_3, col_4, col_5, col_6 = st.columns(6)  

with col_1: 
    if st.button("End Inning"):
        st.session_state.innings_num += 1
        st.session_state.over_num = 1
        st.session_state.ball_num = 1
        st.session_state.runs = 0
        st.session_state.wickets = 0
        st.rerun()
        
with col_5: 
    if st.button("Pause"):
        st.switch_page("home_page.py")

with col_6: 
    if st.button("Save and Next"):
        save_and_next_ball(over_num_input, ball_num_input, 
                           batter_name_input, non_striker_name_input, bowler_name_input,
                           runs_input, is_extras_input, extras_type_input, extras_runs_input, 
                           is_wicket_input, wicket_type_input, out_batter_input)
        st.rerun()