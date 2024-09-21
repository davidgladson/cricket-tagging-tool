import streamlit as st
import os
import pandas as pd

from constants import SQUADS_PATH

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


@st.cache_data
def get_squad_details():
    if os.path.exists(SQUADS_PATH):
        return pd.read_csv(SQUADS_PATH)
    return None
        

def match_list_formatter(match_id_str):
    if match_id_str is not None:
        splits = match_id_str.split("_")
        unparsed_date = str(splits[2])
        parsed_match_date = "{}-{}-{}".format(unparsed_date[-2:], unparsed_date[-4:-2], unparsed_date[:4])
        return "{} vs {} ({})".format(str(splits[0]).title(), str(splits[1]).title(), parsed_match_date)
    return None


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


def get_over_string(over_num, ball_num):
    if ball_num % 6 == 0:
        over_string = "({} Overs)".format(over_num)
    else:
        over_string = "({}.{} Overs)".format(over_num - 1, ball_num)
    return over_string


def get_current_run_rate(runs, over_num, ball_num):
    print(runs, over_num, ball_num)
    num_balls = (over_num - 1) * 6 + ball_num
    if num_balls > 0:
        return runs / num_balls * 6
    else:
        return 0
    
    
def get_lineup_display_data(squads, team_name):
    team_squad = squads[squads["team_name"] == team_name]
    team_squad["playing"] = True
    column_config = {
        "player_name": st.column_config.Column(
            "Streamlit Widgets",
            width="medium",
            disabled=True),
        "playing": st.column_config.CheckboxColumn(
            "Playing",
            help="Select your **favorite** widgets",
            default=True), 
        "team_name": None, 
        "player_id": None, 
        "batting_hand": None, 
        "bowling_hand": None, 
        "bowling_pace_spin": None, 
        "bowling_style": None, 
        "primary_role": None
        }
    return team_squad, column_config


def parse_squad_data_input(df):
    return df[df["playing"]][[""]]