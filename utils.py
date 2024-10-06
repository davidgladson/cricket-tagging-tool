import streamlit as st
import os
import pandas as pd

from constants import BBB_DOWNLOADABLE_COLUMNS, BBB_BASE_DATA_COLUMNS, BBB_ADVANCED_DATA_COLUMNS, BBB_MERGE_COLUMNS

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


def prepare_download_bbb_data(conn, match_id, data_mode):
    match_details_fetched = conn.get_single_match_details(match_id)
    
    if match_details_fetched is None:
        return pd.DataFrame()
    
    ball_by_ball_data = pd.DataFrame(match_details_fetched["ball_by_ball_data"])
    ball_by_ball_advanced_data = pd.DataFrame(match_details_fetched["ball_by_ball_data_advanced"])    
    lineups = pd.DataFrame(match_details_fetched["lineups"])
    
    if data_mode == "base":
        data_candidate_df = ball_by_ball_data.copy()
        
    elif data_mode == "advanced":
        data_candidate_df = ball_by_ball_advanced_data[BBB_ADVANCED_DATA_COLUMNS]
        
    elif data_mode == "combined":
        if ball_by_ball_advanced_data is not None and len(ball_by_ball_advanced_data) > 0:
            data_candidate_df = ball_by_ball_data[BBB_BASE_DATA_COLUMNS].merge(ball_by_ball_advanced_data[BBB_ADVANCED_DATA_COLUMNS], 
                                                                               on=BBB_MERGE_COLUMNS, 
                                                                               how="left")
        else:
            data_candidate_df = ball_by_ball_data.copy()        
    
    else:
        print("Download Mode Not Supported!")
        return pd.DataFrame()
    
    if data_mode in ["base", "combined"]:
        bbb_batter_info = data_candidate_df.merge(lineups[["player_id", "player_name", "batting_hand"]], 
                                                left_on=["batter_id", "batter_name"], 
                                                right_on=["player_id", "player_name"])
        
        bbb_with_bowler_info = bbb_batter_info.merge(lineups[["player_id", "player_name", 
                                                            "bowling_hand", "bowling_pace_spin", "bowling_style"]], 
                                                    left_on=["bowler_id", "bowler_name"], 
                                                    right_on=["player_id", "player_name"])
        try:
            final_downloadable_df = bbb_with_bowler_info[BBB_DOWNLOADABLE_COLUMNS]
        except Exception as e:
            final_downloadable_df = bbb_with_bowler_info.copy()
    
    else:
        final_downloadable_df = data_candidate_df.copy()
    
    return final_downloadable_df


def get_next_ball_players(last_ball_row):    
    next_ball_striker = None
    next_ball_non_striker = None
    next_ball_bowler = None
    
    is_wicket = last_ball_row["is_wicket"]
    is_extra = last_ball_row["is_extras"]
    last_ball_num = int(last_ball_row["ball_num"])
    last_ball_striker = last_ball_row["batter_name"]
    last_ball_non_striker = last_ball_row["non_striker_name"]
    last_ball_bowler = last_ball_row["bowler_name"]
    batter_runs = int(last_ball_row["batter_runs"]) + int(last_ball_row["byes_runs"]) + int(last_ball_row["leg_byes_runs"])
    out_batter = last_ball_row["out_batter"]
    
    print("Pre Processing", last_ball_striker, last_ball_non_striker, last_ball_bowler, batter_runs, last_ball_num)
    
    if is_wicket:
        last_ball_striker = None if last_ball_striker == out_batter else last_ball_striker
        last_ball_non_striker = None if last_ball_non_striker == out_batter else last_ball_non_striker
    
    if is_extra:
        # If the ball is an extra, bowler remains the same
        next_ball_bowler = last_ball_bowler        
        
        if batter_runs % 2 == 0:
            next_ball_striker = last_ball_striker
            next_ball_non_striker = last_ball_non_striker
        else:
            next_ball_striker = last_ball_non_striker
            next_ball_non_striker = last_ball_striker        
    else:   
        # IF not an extra, bowler changes if previous ball == last ball of the over
        if last_ball_num == 6:
            next_ball_bowler = None
            if batter_runs % 2 == 0:
                next_ball_striker = last_ball_non_striker
                next_ball_non_striker = last_ball_striker
            else:
                next_ball_striker = last_ball_striker
                next_ball_non_striker = last_ball_non_striker
        else:
            next_ball_bowler = last_ball_bowler
            
            if batter_runs % 2 == 0:
                next_ball_striker = last_ball_striker
                next_ball_non_striker = last_ball_non_striker
            else:
                next_ball_striker = last_ball_non_striker
                next_ball_non_striker = last_ball_striker  
    
    print("Post Processing", next_ball_striker, next_ball_non_striker, next_ball_bowler)
    
    return next_ball_striker, next_ball_non_striker, next_ball_bowler