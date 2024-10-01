import streamlit as st
import pandas as pd

from db_utils import MongoDBConnector

from constants import DB_URI


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

st.set_page_config(
    page_title="Scorecard View",
    initial_sidebar_state="collapsed"
)

@st.cache_resource
def connect_db(db_uri):
    return MongoDBConnector(DB_URI=db_uri)

connector = connect_db(DB_URI)

st.write("# This is Scorecard View!")
if st.button("Tagging Home"):
    st.switch_page("pages/tagging_home_page.py")
current_match = st.session_state.match_id
match_details = connector.get_single_match_details(st.session_state.match_id)
df = pd.DataFrame(match_details.get("ball_by_ball_data", []))


# def get_current_scores(match_details,df):
    

    

#     return team_stats
# team_stats = get_team_stats(df)
# st.write(team_stats)
def get_match_stats(df):
    
    teams = df[['batting_team', 'bowling_team']].drop_duplicates().values
    team1, team2 = teams[0]  
    
    team1_innings = df[df['batting_team'] == team1]
    team2_innings = df[df['batting_team'] == team2]
    
    # Team 1 stats (first innings)
    team1_runs = team1_innings['runs_scored'].sum()
    team1_wickets = team1_innings['is_wicket'].sum()
    team1_valid_balls = team1_innings[(team1_innings['extras_type'] != 'Wide') & (team1_innings['extras_type'] != 'No Ball')]
    team1_overs_bowled = team1_valid_balls.shape[0] // 6
    team1_balls_in_current_over = team1_valid_balls.shape[0] % 6
    
    #for run rate lets calculate first the total overs:
    total_overs = team1_overs_bowled + (team1_balls_in_current_over/6)
    if total_overs:
        team1_run_rate = round(team1_runs/total_overs,1)
    else:
        team1_run_rate = None
    

    # Team 2 stats (second innings, if started)
    team2_runs = team2_innings['runs_scored'].sum()
    team2_wickets = team2_innings['is_wicket'].sum()
    
    team2_valid_balls = team2_innings[(team2_innings['extras_type'] != 'Wide') & (team2_innings['extras_type'] != 'No Ball')]
    team2_overs_bowled = team2_valid_balls.shape[0] // 6
    team2_balls_in_current_over = team2_valid_balls.shape[0] % 6

    #for run rate lets calculate first the total overs:
    team2_total_overs = team2_overs_bowled + (team2_balls_in_current_over/6)
    if team2_total_overs:
        team2_run_rate = round(team1_runs/team2_total_overs,1)
    else:
        team2_run_rate =None
    
    return {
        'team1': {
            'name': team1,
            'score': f"{int(team1_runs)}/{int(team1_wickets)} ({team1_overs_bowled}.{team1_balls_in_current_over} overs)",
            'run_rate':team1_run_rate
        },
        'team2': {
            'name': team2,
            'score': f"{int(team2_runs)}/{int(team2_wickets)} ({team2_overs_bowled}.{team2_balls_in_current_over} overs)",
            'run_rate':team2_run_rate
        }
    }

def get_current_stats(df):
    # Get the latest row to find the current batter and non-striker
    latest_stat = df.iloc[-1]
    current_batters = latest_stat[['batter_name', 'non_striker_name']].values
    
    # Filter out wide balls to calculate stats properly
    df_innings_no_wide = df[df['extras_type'] != 'Wide']
    
    # Calculate stats for batters who faced balls
    batter_stats = df_innings_no_wide.groupby('batter_name').agg({
        'batter_runs': 'sum', 
        'ball_id': 'count'
    }).reset_index()

    # Create a DataFrame for the current batters (striker and non-striker)
    current_batters_df = pd.DataFrame(current_batters, columns=['batter_name']).drop_duplicates()

    # Perform a left join to include batters who haven't faced a ball (non-striker or those who didn't face)
    current_batter_stats = pd.merge(current_batters_df, batter_stats, on='batter_name', how='left').fillna({
        'batter_runs': 0,   # Set default runs to 0 for batters who haven't faced a ball
        'ball_id': 0        # Set default balls faced to 0 for batters who haven't faced a ball
    })
    
    # Get the latest two bowlers
    current_bowlers = df[['bowler_id', 'bowler_name']].drop_duplicates(subset='bowler_id', keep='last').tail(2)

    # Filter out wides and no balls to calculate valid deliveries
    valid_balls_df = df[(df['extras_type'] != 'Wide') & (df['extras_type'] != 'No Ball')]
    
    # Exclude byes and leg byes for proper bowler stats
    df_no_byes_legbyes = df[~df['extras_type'].isin(['Byes', 'Leg Byes'])]
    # Calculate bowler stats (runs conceded, etc.)
    bowler_stats = df_no_byes_legbyes.groupby('bowler_name').agg({
        'runs_scored': 'sum'
    }).reset_index()

    # Calculate ball count and wickets for bowlers
    bowler_ball_stats = valid_balls_df.groupby('bowler_name').agg({
        'ball_id': 'count',
        'is_wicket': 'sum'
    }).reset_index()

    # Merge the bowler stats with the ball stats
    bowler_stats = bowler_stats.merge(bowler_ball_stats, on='bowler_name')

    # Calculate overs bowled by bowlers
    bowler_stats['overs_bowled'] = bowler_stats['ball_id'] // 6
    bowler_stats['balls_in_over'] = bowler_stats['ball_id'] % 6
    bowler_stats['overs_bowled'] = bowler_stats.apply(lambda row: f"{row['overs_bowled']}.{row['balls_in_over']}", axis=1)

    # Filter stats for the current bowlers (latest two)
    current_bowler_stats = bowler_stats[bowler_stats['bowler_name'].isin(current_bowlers['bowler_name'])]
    
    return current_batter_stats, current_bowler_stats

#===============================================================================================================
#===============================================================================================================


# def generate_scorecard(df, innings_num):
#     # Filter data by innings
#     df_innings = df[df['innings_num'] == innings_num]

#     df_innings['batter_order'] = df_innings.groupby('batter_name').cumcount() + 1
#     current_score = df.iloc[-1]['current_runs']
#     df_innings['cumulative_score'] = current_score
#     first_appearance = df_innings.drop_duplicates('batter_name', keep='first')[['batter_name', 'batter_order']]

#     df_innings_no_wide = df_innings[df_innings['extras_type'] != 'Wide']

#     batter_scores = df_innings_no_wide.groupby('batter_name').agg(
#         how_out=('is_wicket', lambda x: df_innings.loc[x.index, 'wicket_type'].dropna().iloc[0] if x.sum() > 0 else 'not out'),
#         total_runs=('batter_runs', 'sum'),
#         balls_faced=('ball_id', 'count'),
#         dot_balls=('batter_runs', lambda x: (x == 0).sum()),
#         singles=('batter_runs', lambda x: (x == 1).sum()),
#         fours=('batter_runs', lambda x: (x == 4).sum()),
#         sixes=('batter_runs', lambda x: (x == 6).sum())
#     ).reset_index()

    
#     batter_scores = pd.merge(first_appearance, batter_scores, on='batter_name')
    
    
#     batter_scores = batter_scores.sort_values('batter_order').drop(columns=['batter_order'])

    
#     batter_scores.columns = ['batter_name', 'how_out', 'total_runs', 'balls_faced', 'dot_balls', 'singles', 'fours', 'sixes']
    
    
#     batter_scores['Strike Rate'] = (round(batter_scores['total_runs'] / batter_scores['balls_faced'], 2)) * 100
    
   
#     extras = df_innings[['wide_runs', 'no_ball_runs', 'byes_runs', 'leg_byes_runs']].sum().sum()  # Summing all extras
#     extras_row = pd.DataFrame([['Extras', extras, '-', '-', '-', '-', '-', '-','-']], columns=batter_scores.columns)

    
#     total_score = df_innings['runs_scored'].sum()
#     total_row = pd.DataFrame([['Total', total_score, '-', '-', '-', '-', '-', '-','-']], columns=batter_scores.columns)

   
#     batter_scores = pd.concat([batter_scores, extras_row, total_row], ignore_index=True)
    
    
#     batter_scores['batter_name'] = batter_scores.apply(
#         lambda row: row['batter_name'] + '*' if row['how_out'] == 'not out' else row['batter_name'], axis=1
#     )

#     batter_scores = batter_scores.rename(columns={
#         'batter_name': 'Batter Name',
#         'how_out': 'How Out',
#         'total_runs': 'Total Runs',
#         'balls_faced': 'Balls Faced',
#         'dot_balls': 'Dot Balls',
#         'singles': '1s',
#         'fours': '4s',
#         'sixes': '6s'
#     })

#     # Display wickets type and score at which the batter got out
#     wicket_info = df_innings[df_innings['is_wicket'] == True][['batter_name', 'wicket_type', 'current_runs']]
#     wicket_info = wicket_info.rename(columns={
#         'batter_name': 'Batter Name',
#         'wicket_type': 'Wicket Type',
#         'current_runs': 'Score at Wicket'
#     })

#     return batter_scores, wicket_info
def generate_scorecard(df, innings_num):
    # Filter data by innings
    df_innings = df[df['innings_num'] == innings_num]

    # Get the batter order based on their appearance
    df_innings['batter_order'] = df_innings.groupby('batter_name').cumcount() + 1
    current_score = df.iloc[-1]['current_runs']
    df_innings['cumulative_score'] = current_score

    # Track first appearance of both batter and non-striker
    first_appearance_batters = df_innings.drop_duplicates('batter_name', keep='first')[['batter_name', 'batter_order']]
    first_appearance_non_strikers = df_innings.drop_duplicates('non_striker_name', keep='first')[['non_striker_name']].rename(columns={'non_striker_name': 'batter_name'})

    # Combine batter and non-striker appearances
    all_batters = pd.concat([first_appearance_batters, first_appearance_non_strikers]).drop_duplicates('batter_name').reset_index(drop=True)

    df_innings_no_wide = df_innings[df_innings['extras_type'] != 'Wide']

    # Generate batter scores, but use a left join to include all batters
    batter_scores = df_innings_no_wide.groupby('batter_name').agg(
        how_out=('is_wicket', lambda x: df_innings.loc[x.index, 'wicket_type'].dropna().iloc[0] if x.sum() > 0 else 'not out'),
        total_runs=('batter_runs', 'sum'),
        balls_faced=('ball_id', 'count'),
        dot_balls=('batter_runs', lambda x: (x == 0).sum()),
        singles=('batter_runs', lambda x: (x == 1).sum()),
        fours=('batter_runs', lambda x: (x == 4).sum()),
        sixes=('batter_runs', lambda x: (x == 6).sum())
    ).reset_index()

    # Merge with all batters (including non-strikers who may not have faced balls)
    batter_scores = pd.merge(all_batters, batter_scores, on='batter_name', how='left').fillna({
        'how_out': 'not out',
        'total_runs': 0,
        'balls_faced': 0,
        'dot_balls': 0,
        'singles': 0,
        'fours': 0,
        'sixes': 0
    })

    # Sort based on batter order and drop unnecessary column
    batter_scores = batter_scores.sort_values('batter_order').drop(columns=['batter_order'])

    # Set up column names
    batter_scores.columns = ['batter_name', 'how_out', 'total_runs', 'balls_faced', 'dot_balls', 'singles', 'fours', 'sixes']

    # Calculate Strike Rate
    batter_scores['Strike Rate'] = (round(batter_scores['total_runs'] / batter_scores['balls_faced'], 2)) * 100

    # Add extras and total rows
    extras = df_innings[['wide_runs', 'no_ball_runs', 'byes_runs', 'leg_byes_runs']].sum().sum()  # Summing all extras
    extras_row = pd.DataFrame([['Extras', extras, '-', '-', '-', '-', '-', '-', '-']], columns=batter_scores.columns)

    total_score = df_innings['runs_scored'].sum()
    total_row = pd.DataFrame([['Total', total_score, '-', '-', '-', '-', '-', '-', '-']], columns=batter_scores.columns)

    # Concatenate batter scores with extras and total
    batter_scores = pd.concat([batter_scores, extras_row, total_row], ignore_index=True)

    # Mark batters as 'not out' if applicable
    batter_scores['batter_name'] = batter_scores.apply(
        lambda row: row['batter_name'] + '*' if row['how_out'] == 'not out' else row['batter_name'], axis=1
    )

    # Rename columns for final output
    batter_scores = batter_scores.rename(columns={
        'batter_name': 'Batter Name',
        'how_out': 'How Out',
        'total_runs': 'Total Runs',
        'balls_faced': 'Balls Faced',
        'dot_balls': 'Dot Balls',
        'singles': '1s',
        'fours': '4s',
        'sixes': '6s'
    })

    # Display wickets type and score at which the batter got out
    wicket_info = df_innings[df_innings['is_wicket'] == True][['batter_name', 'wicket_type', 'current_runs']]
    wicket_info = wicket_info.rename(columns={
        'batter_name': 'Batter Name',
        'wicket_type': 'Wicket Type',
        'current_runs': 'Score at Wicket'
    })

    return batter_scores, wicket_info


def generate_bowler_stats(df, innings_num):
    df_innings = df[df['innings_num'] == innings_num]

    # Group by bowler and over to calculate maiden overs
    maidens_df = df_innings.groupby(['bowler_name', 'over_num']).agg(total_runs_per_over=('runs_scored', 'sum')).reset_index()
    maidens_df['is_maiden'] = maidens_df['total_runs_per_over'] == 0
    maidens = maidens_df.groupby('bowler_name')['is_maiden'].sum().reset_index()

    # Aggregate bowler stats
    bowler_stats = df_innings.groupby('bowler_name').agg(
        balls_bowled=('ball_id', 'count'),
        wickets=('is_wicket', 'sum'),
        wides=('wide_runs', 'sum'),
        no_balls=('no_ball_runs', 'sum')
    ).reset_index()

    # Calculate legitimate balls (excluding wides and no-balls)
    legit_balls = bowler_stats['balls_bowled'] - (bowler_stats['wides'] + bowler_stats['no_balls'])
    bowler_stats['overs'] = legit_balls // 6 + (legit_balls % 6) / 10  # Calculate overs with remaining balls as decimal

    # Filter out byes and leg byes for runs conceded
    ball_with_not_byes = df_innings[~df_innings['extras_type'].isin(['Byes', 'Leg Byes'])]
    runs_conceded = ball_with_not_byes.groupby('bowler_name')['runs_scored'].sum().reset_index()
    runs_conceded.rename(columns={'runs_scored': 'runs_conceded'}, inplace=True)

    # Merge runs conceded and maidens into bowler stats
    bowler_stats = pd.merge(bowler_stats, runs_conceded, on='bowler_name', how='left')
    bowler_stats = pd.merge(bowler_stats, maidens, on='bowler_name', how='left')

    # Calculate economy rate from legitimate balls only (runs_conceded / overs)
    bowler_stats['economy'] = bowler_stats['runs_conceded'] / bowler_stats['overs']
    
    # Rearrange columns and clean up
    bowler_stats = bowler_stats[['bowler_name', 'overs', 'is_maiden', 'balls_bowled', 'runs_conceded', 'wickets', 'wides', 'no_balls', 'economy']]
    bowler_stats.rename(columns={
        'bowler_name': 'Bowler Name',
        'is_maiden': 'Maiden Overs',
        'wides': 'Wide Balls',
        'no_balls': 'No Balls'
    }, inplace=True)

    # Drop balls_bowled if not needed for the output
    bowler_stats.drop(columns=['balls_bowled'], inplace=True)

    # Calculate total byes and leg byes for the innings
    byes = df_innings['byes_runs'].sum()
    leg_byes = df_innings['leg_byes_runs'].sum()

    return bowler_stats, byes, leg_byes


innings_options = df['innings_num'].unique()

#===============================================================================================================
                                    #Current Stats For Teams
#===============================================================================================================
stats = get_match_stats(df)
col1, col2, col3 = st.columns([3, 1, 3])

# Team 1 (Left side)
with col1:
    
    st.header(stats['team1']['name'])
    st.subheader(stats['team1']['score'])
    st.text("1st Innings")
    run_rate = stats['team1']['run_rate']

    st.text(f"Run Rate: {run_rate}" if run_rate>0 else "Innings Not Yet Started")

# Spacer (Middle Column)
with col2:
    st.write("")  

# Team 2 (Right side)
with col3:
      
    st.header(stats['team2']['name'])
    st.subheader(stats['team2']['score'])
    st.text("2nd Innings")
    run_rate = 0.0
    st.text(f"Run Rate: {run_rate}" if run_rate else "Innings Not Yet Started")
st.divider()
#=======================================================================================================================

#=======================================================Current Batter and Bowler Stats=================================
current_batters,current_bowlers = get_current_stats(df)
col1, col2 = st.columns(2)

# Display batter stats on the left
with col1:
    st.subheader("Current Batters")
    for index, row in current_batters.iterrows():
        st.write(f"**{row['batter_name']}** - {row['batter_runs']}({row['ball_id']})")

# Display bowler stats on the right
with col2:  
    st.subheader("Current Bowlers")
    for index, row in current_bowlers.iterrows():
        st.write(f"**{row['bowler_name']}** - {row['is_wicket']}/{row['runs_scored']} ({row['overs_bowled']})")
st.divider()

#======================================================================================================================

#=====================================================Match Summary================================================================
#dropdown to select innings
selected_innings = st.selectbox("Select Innings", innings_options)

# Generate the scorecard data for selected innings
batter_scores, wicket_info = generate_scorecard(df, selected_innings)

# Display the scorecard
st.subheader(f"Innings {selected_innings} - Batting Summary")
st.dataframe(batter_scores,hide_index=True)

# Generate and display bowler stats
bowler_stats,byes,leg_byes = generate_bowler_stats(df, selected_innings)
st.subheader(f"Innings {selected_innings} - Bowling Summary")
st.dataframe(bowler_stats,hide_index=True)

# Display wicket information
if not wicket_info.empty: 
    st.subheader(f"Innings {selected_innings} - Wicket Information")
    st.dataframe(wicket_info,hide_index=True)

st.write(f"Extras(b{int(byes)},lb{int(leg_byes)})")