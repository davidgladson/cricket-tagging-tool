BASE_DATA_PATH = "data"
MATCH_DETAILS_PATH = "{}/match_details.csv".format(BASE_DATA_PATH)
SQUADS_PATH = "test_data/squads.csv"

VENUE_LIST = ["Sharjah Cricket Stadium", "Dubai International Cricket Stadium"]
TOSS_CHOICE_LIST = ["Batting", "Fielding"]

EXTRAS_LIST = ["No Ball", "Wide", "Byes", "Leg Byes"]
WICKET_TYPE_LIST = ["Bowled", "LBW", "Caught", "Stumped", "Run Out", "Hit Wicket", "Timed Out", "Obstructing the Field", 
                    "Hit Ball Twice", "Handling The Ball"]

SHOT_TYPE_OPTIONS = ["DEFENDED", "CUT_SHOT", "FLICK", "ON_DRIVE", "PULL", "LEG_GLANCE", "STEERED", "PUSH", "SQUARE_DRIVE", 
                     "LEFT_ALONE", "COVER_DRIVE", "STRAIGHT_DRIVE", "SLOG_SHOT", "DAB", "UPPER_CUT", "SWEEP_SHOT", "HOOK", 
                     "REVERSE_SWEEP", "VERTICAL_FORWARD_ATTACK", "PULL_HOOK_ON_BACK_FOOT", "BACK_DEFENCE", "SWEEP", "PUSH_SHOT", 
                     "FORWARD_DEFENCE", "NO_SHOT", "CUT_SHOT_ON_BACK_FOOT", "SLOG_SWEEP", "PADDLE_SWEEP", "RAMP", "REVERSE_PULL", 
                     "DROP_AND_RUN", "PADDLE_AWAY", "REVERSE_SCOOP", "LATE_CUT", "MISSED", "STEP_OUT_AND_DRIVE", "STEP_OUT_AND_LOFT", 
                     "STRAIGHT_TO_BOWLER"]

BALL_LINE_OPTIONS = ["On Stumps", "Outside Off Stump", "Outside Leg Stump", "Wide Outside Off Stump", "Wide Outside Leg Stump"]
BALL_LENGTH_OPTIONS = ["Short", "Short of Good Length", "Good Length", "Full", "Yorker", "Full Toss"]

# Sort All Dropdown options
EXTRAS_LIST.sort()
SHOT_TYPE_OPTIONS.sort()
BALL_LINE_OPTIONS.sort()
BALL_LENGTH_OPTIONS.sort()

BBB_DOWNLOADABLE_COLUMNS = ["match_id", "innings_num", "over_num", "ball_num", "ball_id",
                            "batting_team", "batter_id", "batter_name", "batting_hand", "non_striker_id", "non_striker_name", 
                            "bowling_team", "bowler_id", "bowler_name", "bowling_hand", "bowling_pace_spin", "bowling_style",
                            "ball_speed", "ball_line", "ball_length", 
                            "runs_scored", "batter_runs", "shot_type", "batter_control",
                            "is_extras", "extras_type", "extras_runs", 
                            "wide_runs", "no_ball_runs", "byes_runs", "leg_byes_runs", 
                            "is_wicket", "wicket_type", "out_batter", "fielder_name", "is_sub_fielder",
                            "current_runs", "current_wickets"]

# DB Details

USERNAME = "tagging-app"
PASSWORD = "CricketTaggingApp10"
DB_URI = "mongodb+srv://{}:{}@crictaggingcluster.17mgb.mongodb.net/?retryWrites=true&w=majority&appName=CricTaggingCluster".format(USERNAME, PASSWORD)

DATABASE_NAME = "tagging_app"
SQUADS_COLLECTION = "squads"
MATCH_LIST_COLLECTION = "matches"
BALL_BY_BALL_DATA_COLLECTION = "ball_by_ball"
LINEUPS_COLLECTION = "lineups"

