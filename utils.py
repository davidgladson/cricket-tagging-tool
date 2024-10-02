import streamlit as st
import os
import pandas as pd

from constants import BBB_DOWNLOADABLE_COLUMNS

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
            "Player Name",
            width="medium",
            disabled=True),
        "playing": st.column_config.CheckboxColumn(
            "Playing",
            default=True), 
        "team_name": None, 
        "player_id": None, 
        "batting_hand": None, 
        "bowling_hand": None, 
        "bowling_pace_spin": None, 
        "bowling_style": None, 
        "primary_role": None, 
        "_id": None,
        "age": None, 
        "debut_year": None
        }
    return team_squad, column_config


def prepare_download_bbb_data(conn, match_id):
    match_details_fetched = conn.get_single_match_details(match_id)
    
    if match_details_fetched is None:
        return pd.DataFrame()
    
    ball_by_ball_data = pd.DataFrame(match_details_fetched["ball_by_ball_data"])
    lineups = pd.DataFrame(match_details_fetched["lineups"])
    
    bbb_batter_info = ball_by_ball_data.merge(lineups[["player_id", "player_name", "batting_hand"]], 
                                              left_on=["batter_id", "batter_name"], 
                                              right_on=["player_id", "player_name"])
    
    bbb_with_bowler_info = bbb_batter_info.merge(lineups[["player_id", "player_name", 
                                                          "bowling_hand", "bowling_pace_spin", "bowling_style"]], 
                                                 left_on=["bowler_id", "bowler_name"], 
                                                 right_on=["player_id", "player_name"])
    
    bbb_downloadable = bbb_with_bowler_info[BBB_DOWNLOADABLE_COLUMNS]
    
    return bbb_downloadable
