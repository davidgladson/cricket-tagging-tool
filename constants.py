BASE_DATA_PATH = "data"
MATCH_DETAILS_PATH = "{}/match_details.csv".format(BASE_DATA_PATH)
SQUADS_PATH = "test_data/squads.csv"

VENUE_LIST = ["Sharjah Cricket Stadium", "Dubai International Cricket Stadium"]
TOSS_CHOICE_LIST = ["Batting", "Fielding"]

EXTRAS_LIST = ["No Ball", "Wide", "Byes", "Leg Byes"]
WICKET_TYPE_LIST = ["Bowled", "LBW", "Caught", "Stumped", "Run Out", "Hit Wicket", "Timed Out", "Obstructing the Field"]

# DB Details

USERNAME = "tagging-app"
PASSWORD = "CricketTaggingApp10"
DB_URI = "mongodb+srv://{}:{}@crictaggingcluster.17mgb.mongodb.net/?retryWrites=true&w=majority&appName=CricTaggingCluster".format(USERNAME, PASSWORD)

DATABASE_NAME = "tagging_app"
SQUADS_COLLECTION = "squads"
MATCH_LIST_COLLECTION = "matches"
BALL_BY_BALL_DATA_COLLECTION = "ball_by_ball"
LINEUPS_COLLECTION = "lineups"

