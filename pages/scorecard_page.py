import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Scorecard View",
    initial_sidebar_state="collapsed"
)

st.write("# This is Scorecard View!")
# print("current match",st.session_state.match_id)
if st.button("Home"):
    st.switch_page("home_page.py")
# current_match = st.session_state.match_id 
# print(current_match,"match")
df = pd.read_csv(f"test_data/sample_tagged_data.csv")

# def get_team_stats(df):
#     team_stats = df.groupby('innings_num').agg({'runs_scored':'sum','is_wicket':'sum'}).reset_index()
#     # Filter valid balls (excluding wides and no-balls)
#     valid_balls_df = df[(df['wide'] == 0) & (df['no_ball'] == 0)]
#     overs_stats = valid_balls_df.groupby('innings_num')
    
    

#     return team_stats
# team_stats = get_team_stats(df)
# st.write(team_stats)

def get_current_stats(df):
    latest_stat = df.iloc[-1]
    current_batters = latest_stat[['batter_name','non_striker_name']].values

    batter_stats = df.groupby('batter_name').agg({'runs_scored':'sum', 'ball_num':'count'}).reset_index()
    current_batter_stats = batter_stats[batter_stats['batter_name'].isin(current_batters)]
    


    # Get the last two bowlers
    current_bowlers = df[['bowler_id', 'bowler_name']].drop_duplicates(subset='bowler_id', keep='last').tail(2)

    # Filter valid balls (excluding wides and no-balls)
    valid_balls_df = df[(df['wide'] == 0) & (df['no_ball'] == 0)]

    # Calculate bowler stats (runs conceded and valid balls bowled)
    bowler_stats = valid_balls_df.groupby('bowler_name').agg({'runs_scored': 'sum', 'ball_num': 'count','is_wicket':'sum'}).reset_index()

    # Calculate overs as overs.ball (e.g., 3.2 overs means 3 overs and 2 balls)
    bowler_stats['overs_bowled'] = bowler_stats['ball_num'] // 6
    bowler_stats['balls_in_over'] = bowler_stats['ball_num'] % 6
    bowler_stats['overs_bowled'] = bowler_stats.apply(lambda row: f"{row['overs_bowled']}.{row['balls_in_over']}", axis=1)

    # Filter for the current bowlers
    current_bowler_stats = bowler_stats[bowler_stats['bowler_name'].isin(current_bowlers['bowler_name'])]
    
    return current_batter_stats,current_bowler_stats
current_batters,current_bowlers = get_current_stats(df)
col1, col2 = st.columns(2)

# Display batter stats on the left
with col1:
    for index, row in current_batters.iterrows():
        st.write(f"**{row['batter_name']}** - {row['runs_scored']}({row['ball_num']})")

# Display bowler stats on the right
with col2:  
    for index, row in current_bowlers.iterrows():
        st.write(f"**{row['bowler_name']}** - {row['is_wicket']}/{row['runs_scored']} ({row['overs_bowled']})")
st.divider()
# st.dataframe(data=df)
def generate_scorecard(df):
    # Add batter order to maintain the batting sequence
    df['batter_order'] = df.groupby('batter_name').cumcount() + 1
    df['cumulative_score'] = df['runs_scored'].cumsum()
    first_appearance = df.drop_duplicates('batter_name', keep='first')[['batter_name', 'batter_order']]
    
    # Group by batter to get their individual score summary
    batter_scores = df.groupby('batter_name').agg(
        how_out=('is_wicket', lambda x: df.loc[x.index, 'wicket_type'].dropna().iloc[0] if x.sum() > 0 else 'not out'),  # Show how out or "Not Out"
        total_runs=('runs_scored', 'sum'),  # Total runs
        balls_faced=('ball_id', 'count'),  # Balls faced
        wickets=('is_wicket', 'sum'),  # Wickets (times got out)
        dot_balls=('runs_scored', lambda x: (x == 0).sum()),  # 0's
        singles=('runs_scored', lambda x: (x == 1).sum()),  # 1's
        fours=('runs_scored', lambda x: (x == 4).sum()),  # 4's
        sixes=('runs_scored', lambda x: (x == 6).sum())  # 6's

    ).reset_index()

    # Merge the first appearance to maintain the batting order
    batter_scores = pd.merge(first_appearance, batter_scores, on='batter_name')
    
    # Sort by the batter order and drop unnecessary columns
    batter_scores = batter_scores.sort_values('batter_order').drop(columns=['batter_order'])
    
    # Rename columns appropriately
    batter_scores.columns = ['batter_name','wicket_type', 'total_runs', 'balls_faced', 'wickets', 'dot_balls', 'singles', 'fours', 'sixes']
    
    # Calculate strike rate
    batter_scores['Strike Rate'] = (round(batter_scores['total_runs'] / batter_scores['balls_faced'],2)) * 100
    
    # Adding Extras row
    extras = df[['wide', 'no_ball', 'byes', 'leg_byes']].sum().sum()  # Summing all extras
    extras_row = pd.DataFrame([['Extras', extras, '-','-', '-', '-', '-', '-', '-', '-']], columns=batter_scores.columns)

    # Calculate the total team score
    total_score = df['runs_scored'].sum() + extras
    total_row = pd.DataFrame([['Total', total_score, '-','-', '-', '-', '-', '-', '-', '-']], columns=batter_scores.columns)

    # Append Extras and Total to the batter_scores DataFrame
    batter_scores = pd.concat([batter_scores, extras_row, total_row], ignore_index=True)
    # Add asterisks for batters who are not out
    batter_scores['batter_name'] = batter_scores.apply(
        lambda row: row['batter_name'] + '*' if row['wickets'] == 0 else row['batter_name'], axis=1
    )
    batter_scores = batter_scores.drop(columns=['wickets'])
    batter_scores = batter_scores.rename(columns={
    'batter_name': 'Batter Name',
    'wicket_type': 'How Out',
    'total_runs': 'Total Runs',
    'balls_faced': 'Balls Faced',
    'dot_balls': 'Dot Balls',
    'singles': '1s',
    'fours': '4s',
    'sixes': '6s'
    })
    
    # Reset the index (just in case)
    batter_scores.reset_index(drop=True, inplace=True)
    
    # Display wickets type and score at which the batter got out
    wicket_info = df[df['is_wicket'] == 1][['batter_name', 'wicket_type', 'cumulative_score']]
    wicket_info = wicket_info.rename(columns={
        'batter_name': 'Batter Name',
        'wicket_type': 'Wicket Type',
        'cumulative_score': 'Score at Wicket'
    })
    return batter_scores, wicket_info

def generate_bowler_stats(df):
    # Group by bowler and over to calculate maiden overs (over with no runs conceded)
    maidens_df = df.groupby(['bowler_name', 'over_num']).agg(total_runs_per_over=('runs_scored', 'sum')).reset_index()
    maidens_df['is_maiden'] = maidens_df['total_runs_per_over'] == 0
    maidens = maidens_df.groupby('bowler_name')['is_maiden'].sum().reset_index()  # Count maiden overs
    
    # Group by bowler to get bowling stats
    bowler_stats = df.groupby('bowler_name').agg(
        balls_bowled=('ball_id', 'count'),  # Balls bowled
        runs_conceded=('runs_scored', 'sum'),  # Runs conceded
        wickets=('is_wicket', 'sum'),  # Wickets taken
        wides=('wide', 'sum'),  # Wide balls
        no_balls=('no_ball', 'sum')  # No balls
    ).reset_index()

    # Calculate overs bowled (1 over = 6 legit balls, excluding wides and no-balls)
    legit_balls = bowler_stats['balls_bowled'] - (bowler_stats['wides'] + bowler_stats['no_balls'])
    bowler_stats['overs'] = legit_balls // 6 + (legit_balls % 6) / 10  # Fractional part for partial overs

    # Merge maidens information
    bowler_stats = pd.merge(bowler_stats, maidens, on='bowler_name', how='left')

    # Calculate economy rate (runs conceded per over)
    bowler_stats['economy'] = bowler_stats['runs_conceded'] / bowler_stats['overs']

    # If a bowler hasn't bowled enough legitimate balls, set overs and economy to 0
    bowler_stats['overs'] = bowler_stats['overs'].fillna(0)
    bowler_stats['economy'] = bowler_stats['economy'].fillna(0)

    # Re-arrange columns: Add overs after bowler_name, maiden overs after overs
    bowler_stats = bowler_stats[['bowler_name', 'overs', 'is_maiden', 'balls_bowled', 'runs_conceded', 'wickets', 'wides', 'no_balls', 'economy']]
    bowler_stats.rename(columns={
        'is_maiden': 'Maiden Overs',
        'bowler_name':'Bowler Name',
        'overs':'Overs',
        'balls_bowled':'Balls Bowled',
        'runs_conceded':'Runs Conceded',
        'no_balls':'no balls'
        }, inplace=True)

    return bowler_stats


# Generate the scorecard data
batter_scores, wicket_info = generate_scorecard(df)

# Display the scorecard using Streamlit
st.title("Cricket Scorecard")

st.subheader("Batting Summary")
st.dataframe(batter_scores,hide_index=True)

# Generate bowlers' statistics
bowler_stats = generate_bowler_stats(df)

# Display the bowlers' statistics using Streamlit
st.subheader("Bowling Summary")
st.dataframe(bowler_stats,hide_index=True)

st.subheader("Wicket Information")
st.dataframe(wicket_info,hide_index=True)
