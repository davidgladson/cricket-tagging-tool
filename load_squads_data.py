import pandas as pd
import os
import argparse

from constants import DB_URI
from db_utils import MongoDBConnector

def parse_player_info(input_path, output_path):
    player_data = pd.read_csv(input_path, encoding="latin-1")
    
    REQUIRED_COLS = ["player_id", "player_name", "team_name", "batting_hand", "bowling_hand", "bowling_pace_spin", 
                    "bowling_style", "primary_role", "age", "debut_year"]


    squads_data = []

    for _, row in player_data.iterrows():
        squad_row = {}
        
        squad_row["player_id"] = row["Cricinfo ID"]
        squad_row["player_name"] = str(row["Player"]).strip()
        squad_row["team_name"] = "{} Women".format(str(row["Country"]).strip())
        squad_row["primary_role"] = str(row["Role"]).strip()
        squad_row["debut_year"] = row["Debut Year"]
        squad_row["age"] = int(row["Age"])

        # Processing Batting Style Info
        batting_style = str(row["Batting Style"])
        batting_style = batting_style.strip().replace("-", " ").lower()
        if "left hand" in batting_style:
            squad_row["batting_hand"] = "Left"
        elif "right hand" in batting_style:
            squad_row["batting_hand"] = "Right"
        else:
            squad_row["batting_hand"] = None
        
        # Process Bowling Style Info
        bowling_style = str(row["Bowling Style"]).strip()
        
        if "N/A" in bowling_style:
            bowling_hand = None
            bowling_pace_spin = None
            bowling_style = None
        else:
            bowling_style = bowling_style.strip().replace("-", " ").lower()
            if "left arm" in bowling_style:
                bowling_hand = "Left"
            elif "right arm" in bowling_style:
                bowling_hand = "Right"
            else:
                bowling_hand = None
                
            if any([x in bowling_style for x in ["fast", "medium"]]):
                bowling_pace_spin = "Pace"
            elif any([x in bowling_style for x in ["off", "leg", "orthodox", "break", "spin"]]):
                bowling_pace_spin = "Spin"
            else: 
                bowling_pace_spin = None
        
        squad_row["bowling_hand"] = bowling_hand
        squad_row["bowling_pace_spin"] = bowling_pace_spin
        squad_row["bowling_style"] = bowling_style

        
        squads_data.append(squad_row)

    squads_data_df = pd.DataFrame(squads_data)
    
    print(player_data["Bowling Style"].unique())
    print(squads_data_df.team_name.unique())
    
    assert squads_data_df.team_name.nunique() == 10

    squads_data_df.to_csv(output_path, columns=REQUIRED_COLS, index=False)


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--update_db", action="store_true", help="Squad Updates to Push To DB or not")
    
    args = parser.parse_args()
    update_db = args.update_db
    
    input_path = "test_data/player_info.csv"
    output_path = "test_data/squads_compiled.csv"
    
    parse_player_info(input_path, output_path)
    
    if update_db:
        squads_data_df = pd.read_csv(output_path)
                
        connector = MongoDBConnector(DB_URI=DB_URI)

        connector.refresh_squads_data(squads_data_df.to_dict("records"))

        
    