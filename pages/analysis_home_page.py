
st.set_page_config(page_title='WT20I Performance Analysis Portal', layout='wide')
st.title('WT20I Performance Analysis Portal')
#============================================Password Check Function===================
# Password check function
def check_password():
    if st.session_state.get("password_correct", False):
        return True

    st.error("Unauthorized access! Please login from the main page.")
    return False

# Check if the password is correct before allowing access to this page
if not check_password():
    st.switch_page("home_page.py")
#================================================================================
import streamlit as st
import pandas as pd
import math as mt
import numpy as np
import matplotlib.pyplot as plt
pdf = pd.read_csv("Analysis_datasets/Mydataset.csv",low_memory=False)
pdfn = pd.read_csv("Analysis_datasets/wwc_2024_final.csv",low_memory=False)
pdfn['bowler'] = pdfn['bowler'].replace('AC Jayangani', 'Chamari Athapaththu')
pdfn['batsman'] = pdfn['batsman'].replace('AC Jayangani', 'Chamari Athapaththu')
pdfn['non_striker'] = pdfn['non_striker'].replace('AC Jayangani', 'Chamari Athapaththu')
idf = pd.read_csv("Analysis_datasets/lifesaver_bat.csv",low_memory=False)
idf['batsman'] = idf['batsman'].replace('AC Jayangani', 'Chamari Athapaththu')
info_df=pd.read_csv("Analysis_datasets/player_info_k.csv",low_memory=False)
bpdf=pd.read_csv("Analysis_datasets/Mydataset.csv",low_memory=False)
bpdfn = pd.read_csv("Analysis_datasets/wwc_2024_final.csv",low_memory=False)
bpdfn['bowler'] = bpdfn['bowler'].replace('AC Jayangani', 'Chamari Athapaththu')
bpdfn['batsman'] = bpdfn['batsman'].replace('AC Jayangani', 'Chamari Athapaththu')
bpdfn['non_striker'] = bpdfn['non_striker'].replace('AC Jayangani', 'Chamari Athapaththu')
bidf=pd.read_csv("Analysis_datasets/lifesaver_bowl.csv",low_memory=False)
bidf['bowler'] = bidf['bowler'].replace('AC Jayangani', 'Chamari Athapaththu')
info_df=info_df.rename(columns={'Player':'Player_name'})
cols_conv=['season','match_id']
pdfn[cols_conv] = pdfn[cols_conv].astype(str)
bpdfn[cols_conv] = bpdfn[cols_conv].astype(str)
pdfn=pdfn.drop(columns=['Unnamed: 0'])
pdf=pdf.drop(columns=['penalty'])
bpdfn=bpdfn.drop(columns=['Unnamed: 0'])
bpdf=bpdf.drop(columns=['penalty'])
idf=idf[(idf['final_year']=='2024/25')]
pdfn = pdfn.drop_duplicates(subset=['match_id', 'ball','inning'], keep='first')
bpdfn = bpdfn.drop_duplicates(subset=['match_id', 'ball','inning'], keep='first')
idf=idf.drop(columns=['Unnamed: 0'])
bidf=bidf.drop(columns=['Unnamed: 0'])
if 'batting Style' in pdfn.columns and 'bowling Style' in pdfn.columns:
    pdfn = pdfn.rename(columns={'batting Style': 'batting_style', 'bowling Style': 'bowling_style'})
else:
    print("Columns 'batting Style' and/or 'bowling Style' not found.")


# Ensure that 'common_columns' match the order and columns in df2
common_columns = [col for col in pdf.columns if col in pdf.columns]

# Combine df2 columns in order and add any additional columns from df1 at the end
all_columns = common_columns + [col for col in pdfn.columns if col not in common_columns]

# Reorder df1 columns to match df2's order, with extra df1 columns appended at the end
pdfn = pdfn[all_columns]

# Concatenate df1 and df2 along the rows, ensuring column alignment
merged_df = pd.concat([pdfn, pdf], ignore_index=True)
pdf=merged_df
pdfn['bowler'] = pdf['bowler'].replace('AC Jayangani', 'Chamari Athapaththu')
pdf['batsman'] = pdf['batsman'].replace('AC Jayangani', 'Chamari Athapaththu')
pdf['non_striker'] = pdf['non_striker'].replace('AC Jayangani', 'Chamari Athapaththu')
bpdf=merged_df
# Display the merged DataFrame
print("Merged DataFrame:")
print(merged_df.head())

pdf[['noballs', 'wides','byes','legbyes']] = pdf[['noballs', 'wides','byes','legbyes']].fillna(0).astype(int)
pdf['valid_ball'] = pdf.apply(lambda x: 1 if (x['wides'] == 0 and x['noballs'] == 0) else 0, axis=1)
pdfn['valid_ball'] = pdfn.apply(lambda x: 1 if (x['wides'] == 0 and x['noballs'] == 0) else 0, axis=1)
# Group by 'bowler' and 'match_id' to sum the 'bowler_wkt'
dismissals_count = bpdf.groupby(['bowler', 'match_id'])['bowler_wkt'].sum()
bbi = dismissals_count.groupby('bowler').max().reset_index().rename(columns={'bowler_wkt': 'bbi'})
bidf = pd.merge(bidf, bbi, on='bowler')

def show_match_details(match_id):
    print("Hello")
    match_id = str(match_id)
    # Filter match details for the selected match_id
    match_details = pdf[pdf['match_id'] == match_id]
    print(match_details.head())
    print("DHENDNHEHCBDHBEDHBD")
    # First, remove duplicates based on match_id and ball within the same match
    print(f"Before removing duplicates based on 'match_id' and 'ball': {match_details.shape}")
    match_details = match_details.drop_duplicates(subset=['match_id', 'ball', 'inning','batsman','bowler','over'], keep='first')
    print(f"After removing duplicates based on 'match_id' and 'ball': {match_details.shape}")
    print("Hello")
    
    if not match_details.empty:
        st.write(f"### Match Details - Match ID: {match_id}")
        # Split the data by innings
        innings_1 = match_details[match_details['inning'] == 1]
        innings_2 = match_details[match_details['inning'] == 2]

        # Get batting teams for both innings
        batting_team_1 = innings_1['batting_team'].unique()[0] if not innings_1.empty else "Unknown"
        batting_team_2 = innings_2['batting_team'].unique()[0] if not innings_2.empty else "Unknown"

        # Show the scorecard for each innings
        if not innings_1.empty:
            total_runs_1 = innings_1['total_runs'].sum()
            total_balls_1 = (innings_1['valid_ball'].sum())%6
            total_overs_1=innings_1['over'].iloc[-1]
            # Handle special case for exactly 20 overs
            if (total_balls_1==0):
                overs_display = f"{total_overs_1}.{total_balls_1}"  # +1 because overs start from 1
            else:            
                overs_display = f"{total_overs_1-1}.{total_balls_1}"  # +1 because overs start from 1
            # Display innings result
            st.markdown(f"<h5 style='font-size: 30px;'>{innings_1['batting_team'].iloc[0]} Innings: {total_runs_1}/{innings_1['is_wkt'].sum()} ({overs_display} ov)</h5>", unsafe_allow_html=True)


            show_innings_scorecard(innings_1, f"Innings 1: {batting_team_1} Women")
        if not innings_2.empty:
            total_runs_2 = innings_2['total_runs'].sum()
            total_balls_2 = (innings_2['valid_ball'].sum())%6
            total_overs_2=innings_2['over'].iloc[-1]
            if (total_balls_2==0):
                overs_display = f"{total_overs_2}.{total_balls_2}"  # +1 because overs start from 1
            else:            
                overs_display = f"{total_overs_2-1}.{total_balls_2}"  # +1 because overs start from 1
            # Display innings result
            st.markdown(f"<h5 style='font-size: 30px;'>{innings_2['batting_team'].iloc[0]} Innings: {total_runs_2}/{innings_2['is_wkt'].sum()} ({overs_display} ov)</h5>", unsafe_allow_html=True)



            show_innings_scorecard(innings_2, f"Innings 2: {batting_team_2} Women")
    else:
        st.write("No match details found.")

def show_innings_scorecard(inning_data, title):
    # Batting scorecard
    st.write("Batting")
    batting_order = []
    
    # Iterate through the innings data to establish the batting order
    for i, row in inning_data.iterrows():
        batsman = row['batsman']
        non_striker = row['non_striker']
        
        if batsman not in batting_order:
            batting_order.append(batsman)
        if non_striker not in batting_order:
            batting_order.append(non_striker)
    
    # Calculate total extras
    total_extras = inning_data['extras'].sum()
    
    # Aggregate batting data for runs, balls faced, fours, and sixes
    batting_data = inning_data.groupby(['batsman']).agg({
        'batsman_runs': 'sum',
        'valid_ball': 'sum',
        'is_four': 'sum',
        'is_six': 'sum'
    }).reset_index()
    
    # Initialize columns for Wicket and Dismissal Kind
    batting_data['Wicket'] = "Not Out"  # Default value if no dismissal
    batting_data['Dismissal Kind'] = "-"  # Default value if no dismissal
    
    # Populate Wicket and Dismissal Kind based on dismissal events
    for index, row in batting_data.iterrows():
        batsman = row['batsman']
        
        # Check if this batsman was dismissed
        dismissed_data = inning_data[(inning_data['batsman'] == batsman) & (inning_data['is_wkt'] == 1)]
        
        if not dismissed_data.empty:
            dismissal_event = dismissed_data.iloc[0]
            
            # If bowler_wkt is 1, the bowler took the wicket
            if dismissal_event['bowler_wkt'] == 1:
                batting_data.at[index, 'Wicket'] = dismissal_event['bowler']
            else:
                batting_data.at[index, 'Wicket'] = "-"
            
            # Update dismissal kind
            batting_data.at[index, 'Dismissal Kind'] = dismissal_event['dismissal_kind']
        
        # Handle retired cases
        retired_data = inning_data[(inning_data['batsman'] == batsman) & (inning_data['dismissal_kind'] == 'retired')]
        if not retired_data.empty:
            retired_event = retired_data.iloc[-1]
            batting_data.at[index, 'Wicket'] = "-"
            batting_data.at[index, 'Dismissal Kind'] = retired_event['dismissal_kind']
    
    # Now handle players who are dismissed but have no valid balls faced
    for player in inning_data['player_dismissed'].unique():
        # Check if player is already in the batting_data
        if player not in batting_data['batsman'].values:
            # Get data for the dismissed player
            player_data = (inning_data[inning_data['player_dismissed'] == player])
            p_data = inning_data[inning_data['batsman'] == player]
            valid_ball_sum = p_data['valid_ball'].sum()         
            
            # Handling the case where the player is dismissed without facing a legal ball
            if valid_ball_sum == 0:
                dismissal_event = inning_data[inning_data['player_dismissed'] == player]  # Get the first row since it's a single dismissal event
                # dismissal_event = inning_data[inning_data['player_dismissed'] == player].iloc[0]
                if not dismissal_event.empty:
                    # bowler_wkt = dismissal_event['bowler_wkt'] #if isinstance(dismissal_event['bowler_wkt'], pd.Series) else dismissal_event['bowler_wkt']
                    
                    # Create a new row for the player to be added to the batting data
                    new_row = pd.DataFrame({
                        'batsman': [player],
                        'batsman_runs': [0],
                        'valid_ball': [0],
                        'is_four': [0],
                        'is_six': [0],
                        # 'Wicket': [dismissal_event['bowler'] if dismissal_event['bowler_wkt'] == 1 else '-'],
                        # 'Dismissal Kind': [dismissal_event['dismissal_kind']]
                        'Wicket': ["-"],  # Default value for Wicket
                        'Dismissal Kind': ["-"]
                    })
                    # Check if 'bowler_wkt' exists in the dismissal event data
                    new_row.at[0, 'Dismissal Kind'] = dismissal_event['dismissal_kind'].values[0] if isinstance(dismissal_event['dismissal_kind'], pd.Series) else dismissal_event['dismissal_kind']
                # Use pd.concat to add the new row to the existing DataFrame
                    batting_data = pd.concat([batting_data, new_row], ignore_index=True)
    
    # Calculate strike rate
    batting_data['batter_sr'] = (batting_data['batsman_runs'] / batting_data['valid_ball']).replace({0 : 0}) * 100
    
    # Rename columns for the batting scorecard
    batting_data.columns = ['Batsman', 'R', 'B', '4s', '6s', 'Wicket', 'Dismissal Kind', 'SR']
    
    # Filter out batsmen with 0 runs (if needed)
    batting_data['order'] = batting_data['Batsman'].apply(lambda x: batting_order.index(x) if x in batting_order else -1)
    batting_data = batting_data.sort_values(by='order').drop(columns='order').reset_index(drop=True)
    batting_data.index = batting_data.index + 1
    batting_data['Last Name'] = batting_data['Batsman'].apply(lambda x: x.split()[-1])

    # Step 2: Identify batsmen to remove based on the condition
    to_remove = []
    
    for idx, row in batting_data.iterrows():
        if row['R'] == 0 and row['B'] == 0 and row['Wicket'] == '-':
            # If last name appears again with non-zero R and B, mark for removal
            last_name = row['Last Name']
            if any((batting_data['Last Name'] == last_name) & ((batting_data['B'] == 0))):
                to_remove.append(idx)
    to_remove += batting_data[batting_data['Batsman'] == 'AC Jayangani'].index.tolist()
    to_remove += batting_data[batting_data['Batsman'] == 'H Madavi'].index.tolist()
    to_remove += batting_data[batting_data['Batsman'] == 'SIP Fernando'].index.tolist()
    
    # Step 3: Remove batsmen identified
    batting_data_filtered = batting_data.drop(to_remove).reset_index(drop=True)
    
    # Step 4: Reset index and remove the 'Last Name' column
    batting_data_filtered = batting_data_filtered.drop(columns='Last Name')
    batting_data_filtered.index = batting_data_filtered.index + 1

    # Display the batting table
    st.table(batting_data_filtered)
    
    # Show extras
    st.write(f"**Extras:** {total_extras}")


    
    # Bowling scorecard
    st.write("Bowling")
    bowling_order = []
    
    for i, row in inning_data.iterrows():
        bowler = row['bowler']
        
        if bowler not in bowling_order:
            bowling_order.append(bowler)
    
    inning_data['adjusted_runs'] = inning_data.apply(lambda row: row['total_runs'] - (row['byes'] + row['legbyes']), axis=1)
    bowling_data = inning_data.groupby(['bowler']).agg({
        'valid_ball': 'sum',
        'adjusted_runs': 'sum',
        'bowler_wkt': 'sum',
        'wides': 'sum',
        'noballs': 'sum'
    }).reset_index()
    
    # Calculate overs bowled (converting balls to overs)
    bowling_data['Overs'] = (bowling_data['valid_ball'] // 6).astype(str) + "." + (bowling_data['valid_ball'] % 6).astype(str)
    
    # Calculate economy rate (total runs / overs)
    bowling_data['econ'] = bowling_data['adjusted_runs'] / (bowling_data['valid_ball'] / 6)
    
    # Calculate bowling strike rate (balls per wicket, avoid division by zero)
    bowling_data['bowl_sr'] = bowling_data['valid_ball'] / bowling_data['bowler_wkt']
    bowling_data['bowl_sr'] = bowling_data['bowl_sr'].replace([float('inf'), float('nan')], 0)
    
    # Select and rename columns for the bowling scorecard
    bowling_data = bowling_data[['bowler', 'Overs', 'adjusted_runs', 'bowler_wkt', 'wides', 'noballs', 'econ', 'bowl_sr']]
    bowling_data.columns = ['Bowler', 'O', 'R', 'W', 'WD', 'NB', 'Econ', 'SR']
    bowling_data = bowling_data[(bowling_data.Bowler) != '0']
    
    # Display bowling scorecard
    bowling_data['order'] =bowling_data['Bowler'].apply(lambda x: bowling_order.index(x))
    bowling_data = bowling_data.sort_values(by='order').drop(columns='order').reset_index(drop=True)
    bowling_data.index = bowling_data.index + 1
    st.table(bowling_data)


def categorize_phase(over):
              if over <= 6:
                  return 'Powerplay'
              elif 6 < over < 16:
                  return 'Middle'
              else:
                  return 'Death'
pdf['phase'] = pdf['over'].apply(categorize_phase)
def is_bowlers_wkt(player_dismissed,dismissal_kind):
  if type(player_dismissed)== str :
    if dismissal_kind not in ['run out','retired hurt','obstructing the field']:
      return 1
    else :
      return 0
  else:
    return 0
bpdf['bowler_wkt']=bpdf.apply(lambda x: (is_bowlers_wkt(x['player_dismissed'],x['dismissal_kind'])),axis=1)
# def round_up_floats(df, decimal_places=2):
#     # Round up only for float columns
#     float_cols = df.select_dtypes(include=['float'])
#     df[float_cols.columns] = np.ceil(float_cols * (10 ** decimal_places)) / (10 ** decimal_places)
#     return df
def round_up_floats(df, decimal_places=2):
    # Select only float columns from the DataFrame
    float_cols = df.select_dtypes(include=['float64', 'float32'])  # Ensure to catch all float types
    
    # Round up the float columns and maintain the same shape
    rounded_floats = np.ceil(float_cols * (10 ** decimal_places)) / (10 ** decimal_places)
    
    # Assign the rounded values back to the original DataFrame
    df[float_cols.columns] = rounded_floats
    
    return df

def standardize_season(season):
    if '/' in season:  # Check if the season is in 'YYYY/YY' format
          year = season.split('/')[0]  # Get the first part
    else:
          year = season  # Use as is if already in 'YYYY' format
    return year.strip()  # Return the year stripped of whitespace
def get_current_form(bpdf, player_name):
    # Filter for matches where the player batted or bowled
    player_matches = bpdf[(bpdf['batsman'] == player_name) | (bpdf['bowler'] == player_name)]
    player_matches['start_date'] = pd.to_datetime(player_matches['start_date'], format='%m/%d/%Y')
    player_matches = player_matches.sort_values(by='start_date', ascending=False)
    bpdf['start_date'] = pd.to_datetime(bpdf['start_date'], format='%m/%d/%Y')
    
    # Get the last 10 unique match IDs
    last_10_matches = player_matches['start_date'].drop_duplicates().sort_values(ascending=False).head(10)

    # Prepare the result DataFrame
    results = []

    for date in last_10_matches:
        # Get batting stats for this match
        bat_match_data = bpdf[(bpdf['start_date'] == date) & (bpdf['batsman'] == player_name)]
        match_id = None
        venue = None
        opp = None
        fan_pts_bat = 0
        fan_pts_bowl = 0
        
        if not bat_match_data.empty:
            runs = bat_match_data['batsman_runs'].sum() 
            balls_faced = bat_match_data['ball'].count()  # Sum balls faced
            SR = (runs / balls_faced) * 100 if balls_faced > 0 else 0.0
            venue = bat_match_data['venue'].iloc[0]
            match_id = bat_match_data['match_id'].iloc[0]
            date = bat_match_data['start_date'].iloc[0]
            opp = bat_match_data['bowling_team'].iloc[0]
            fan_pts_bat = bat_match_data['bat_fantasy_pts'].sum()
        else:
            runs = 0
            balls_faced = 0
            SR = 0.0
            fan_pts_bat = 0
        
        # Get bowling stats for this match
        bowl_match_data = bpdf[(bpdf['start_date'] == date) & (bpdf['bowler'] == player_name)]
        
        if not bowl_match_data.empty:
            balls_bowled = bowl_match_data['ball'].count()  # Sum balls bowled
            runs_given = bowl_match_data['total_runs'].sum()  # Sum runs given
            wickets = bowl_match_data['bowler_wkt'].sum()  # Sum wickets taken
            econ = (runs_given / (balls_bowled / 6)) if balls_bowled > 0 else 0.0  # Calculate Econ
            venue = bowl_match_data['venue'].iloc[0]
            match_id = bowl_match_data['match_id'].iloc[0]
            date = bowl_match_data['start_date'].iloc[0]
            opp = bowl_match_data['batting_team'].iloc[0]
            fan_pts_bowl = bowl_match_data['ball_fantasy_pts'].sum()
        else:
            balls_bowled = 0
            runs_given = 0
            wickets = 0
            econ = 0.0
            fan_pts_bowl = 0
        results.append({
            "Date" : date,
            "Match ID": match_id,
            "Runs": runs,
            "Balls Faced": balls_faced,
            "SR": SR,
            "Balls Bowled": balls_bowled,
            "Runs Given": runs_given,
            "Wickets": wickets,
            "Econ": econ,
            "Venue": venue,
            "Opponent" : opp,
            "Batting_Fantasy_Pts" : fan_pts_bat,
            "Bowling_Fantasy_Pts" : fan_pts_bowl,
            
        })
    
    return pd.DataFrame(results)
# Define the columns related to runs
columns_to_convert = ['runs', 'hundreds', 'fifties', 'thirties', 'highest_scores']
# pdf = pdf.drop_duplicates(subset=['match_id', 'ball'], keep='first')

def cumulator(temp_df):
    # First, remove duplicates based on match_id and ball within the same match
    print(f"Before removing duplicates based on 'match_id' and 'ball': {temp_df.shape}")
    temp_df = temp_df.drop_duplicates(subset=['match_id', 'ball','inning'], keep='first')
    print(f"After removing duplicates based on 'match_id' and 'ball': {temp_df.shape}")

    # Ensure 'total_runs' exists
    if 'total_runs' not in temp_df.columns:
        raise KeyError("Column 'total_runs' does not exist in temp_df.")

    # Calculate runs, balls faced, innings, dismissals, etc.
    runs = temp_df.groupby(['batsman'])['batsman_runs'].sum().reset_index().rename(columns={'batsman_runs': 'runs'})
    balls = temp_df.groupby(['batsman'])['ball'].count().reset_index()
    inn = temp_df.groupby(['batsman'])['match_id'].apply(lambda x: len(list(np.unique(x)))).reset_index().rename(columns={'match_id': 'innings'})
    matches = temp_df.groupby(['batsman'])['match_id'].nunique().reset_index().rename(columns={'match_id': 'matches'})
    dis = temp_df.groupby(['batsman'])['player_dismissed'].count().reset_index().rename(columns={'player_dismissed': 'dismissals'})
    sixes = temp_df.groupby(['batsman'])['is_six'].sum().reset_index().rename(columns={'is_six': 'sixes'})
    fours = temp_df.groupby(['batsman'])['is_four'].sum().reset_index().rename(columns={'is_four': 'fours'})
    dots = temp_df.groupby(['batsman'])['is_dot'].sum().reset_index().rename(columns={'is_dot': 'dots'})
    ones = temp_df.groupby(['batsman'])['is_one'].sum().reset_index().rename(columns={'is_one': 'ones'})
    twos = temp_df.groupby(['batsman'])['is_two'].sum().reset_index().rename(columns={'is_two': 'twos'})
    threes = temp_df.groupby(['batsman'])['is_three'].sum().reset_index().rename(columns={'is_three': 'threes'})
    bat_team = temp_df.groupby(['batsman'])['batting_team'].unique().reset_index()
    fpi = pd.DataFrame(temp_df.groupby(['batsman'])['bat_fantasy_pts'].sum()).reset_index().rename(columns={'bat_fantasy_pts': 'fantasy_points'})
    print(1)
    matches = temp_df.groupby(['batsman'])['match_id'].nunique().reset_index(name='matches')
    print(0)

    # Convert the array of countries to a string without brackets
    bat_team['batting_team'] = bat_team['batting_team'].apply(lambda x: ', '.join(x)).str.replace('[', '').str.replace(']', '')

    match_runs = temp_df.groupby(['batsman', 'match_id'])['batsman_runs'].sum().reset_index()

    # Count 100s, 50s, and 30s
    hundreds = match_runs[match_runs['batsman_runs'] >= 100].groupby('batsman').size().reset_index(name='hundreds')
    fifties = match_runs[(match_runs['batsman_runs'] >= 50) & (match_runs['batsman_runs'] < 100)].groupby('batsman').size().reset_index(name='fifties')
    thirties = match_runs[(match_runs['batsman_runs'] >= 30) & (match_runs['batsman_runs'] < 50)].groupby('batsman').size().reset_index(name='thirties')

    # Calculate the highest score for each batsman
    highest_scores = match_runs.groupby('batsman')['batsman_runs'].max().reset_index().rename(columns={'batsman_runs': 'highest_score'})

    # Merge all the calculated metrics into a single DataFrame
    summary_df = runs.merge(balls, on='batsman', how='left')
    summary_df = summary_df.merge(inn, on='batsman', how='left')
    summary_df = summary_df.merge(matches, on='batsman', how='left')
    summary_df = summary_df.merge(dis, on='batsman', how='left')
    summary_df = summary_df.merge(sixes, on='batsman', how='left')
    summary_df = summary_df.merge(fours, on='batsman', how='left')
    summary_df = summary_df.merge(dots, on='batsman', how='left')
    summary_df = summary_df.merge(ones, on='batsman', how='left')
    summary_df = summary_df.merge(twos, on='batsman', how='left')
    summary_df = summary_df.merge(threes, on='batsman', how='left')
    summary_df = summary_df.merge(bat_team, on='batsman', how='left')
    summary_df = summary_df.merge(hundreds, on='batsman', how='left')
    summary_df = summary_df.merge(fifties, on='batsman', how='left')
    summary_df = summary_df.merge(thirties, on='batsman', how='left')
    summary_df = summary_df.merge(highest_scores, on='batsman', how='left')
    summary_df = summary_df.merge(matches, on='batsman', how='left')
    summary_df = summary_df.merge(fpi, on='batsman', how='left')
          # Calculating additional columns
    def bpd(balls, dis):
      return balls if dis == 0 else balls / dis
    
    def bpb(balls, bdry):
      return balls if bdry == 0 else balls / bdry
    
    def avg(runs, dis, inn):
      return runs / inn if dis == 0 else runs / dis
    
    def DP(balls, dots):
      return (dots / balls) * 100
    
    summary_df['SR'] = summary_df.apply(lambda x: (x['runs'] / x['ball']) * 100, axis=1)
    
    summary_df['BPD'] = summary_df.apply(lambda x: bpd(x['ball'], x['dismissals']), axis=1)
    summary_df['BPB'] = summary_df.apply(lambda x: bpb(x['ball'], (x['fours'] + x['sixes'])), axis=1)
    summary_df['nbdry_sr'] = summary_df.apply(lambda x: ((x['dots'] * 0 + x['ones'] * 1 + x['twos'] * 2 + x['threes'] * 3) /(x['dots'] + x['ones'] + x['twos'] + x['threes']) * 100) if (x['dots'] + x['ones'] + x['twos'] + x['threes']) > 0 else 0,axis=1)
    summary_df['AVG'] =summary_df.apply(lambda x: avg(x['runs'], x['dismissals'], x['innings']), axis=1)
    summary_df['dot_percentage'] = (summary_df['dots'] / summary_df['ball']) * 100
    summary_df['fantasy_points_per_match'] = summary_df['fantasy_points'] / summary_df['innings'].replace(0, np.nan)


    debut_year = temp_df.groupby('batsman')['season'].min().reset_index()
    final_year = temp_df.groupby('batsman')['season'].max().reset_index()
    debut_year.rename(columns={'season': 'debut_year'}, inplace=True)
    final_year.rename(columns={'season': 'final_year'}, inplace=True)
    summary_df = summary_df.merge(debut_year, on='batsman').merge(final_year, on='batsman')


    # Merging matches data
    summary_df = summary_df.merge(matches, on='batsman', how='left')

    return summary_df

def bcum(df):
    # First, remove duplicates based on match_id and ball within the same match
    print(f"Before removing duplicates based on 'match_id' and 'ball': {df.shape}")
    df = df.drop_duplicates(subset=['match_id', 'ball','inning'], keep='first')
    print(f"After removing duplicates based on 'match_id' and 'ball': {df.shape}")
    # df['total_runs']=df['batsman_runs']+df['extras']
  
    # Create various aggregates
    runs = pd.DataFrame(df.groupby(['bowler'])['batsman_runs'].sum()).reset_index().rename(columns={'batsman_runs': 'runs'})
    innings = pd.DataFrame(df.groupby(['bowler'])['match_id'].nunique()).reset_index().rename(columns={'match_id': 'innings'})
    balls = pd.DataFrame(df.groupby(['bowler'])['ball'].count()).reset_index().rename(columns={'ball': 'balls'})
    wkts = pd.DataFrame(df.groupby(['bowler'])['bowler_wkt'].sum()).reset_index().rename(columns={'bowler_wkt': 'wkts'})
    dots = pd.DataFrame(df.groupby(['bowler'])['is_dot'].sum()).reset_index().rename(columns={'is_dot': 'dots'})
    ones = pd.DataFrame(df.groupby(['bowler'])['is_one'].sum()).reset_index().rename(columns={'is_one': 'ones'})
    twos = pd.DataFrame(df.groupby(['bowler'])['is_two'].sum()).reset_index().rename(columns={'is_two': 'twos'})
    threes = pd.DataFrame(df.groupby(['bowler'])['is_three'].sum()).reset_index().rename(columns={'is_three': 'threes'})
    fours = pd.DataFrame(df.groupby(['bowler'])['is_four'].sum()).reset_index().rename(columns={'is_four': 'fours'})
    sixes = pd.DataFrame(df.groupby(['bowler'])['is_six'].sum()).reset_index().rename(columns={'is_six': 'sixes'})
    fpi = pd.DataFrame(df.groupby(['bowler'])['ball_fantasy_pts'].sum()).reset_index().rename(columns={'ball_fantasy_pts': 'fantasy_points'})

    
    dismissals_count = df.groupby(['bowler', 'match_id'])['bowler_wkt'].sum()
    three_wicket_hauls = dismissals_count[dismissals_count >= 3].groupby('bowler').count().reset_index().rename(columns={'bowler_wkt': 'three_wicket_hauls'})
    bbi = dismissals_count.groupby('bowler').max().reset_index().rename(columns={'bowler_wkt': 'bbi'})

    
    # Identify maiden overs (group by match and over, check if total_runs == 0)
    df['over'] = df['ball'].apply(lambda x: int(x))  # Assuming ball represents the ball within an over
    maiden_overs = df.groupby(['bowler', 'match_id', 'over']).filter(lambda x: x['total_runs'].sum() == 0)
    maiden_overs_count = maiden_overs.groupby('bowler')['over'].count().reset_index().rename(columns={'over': 'maiden_overs'})

    # Merge all metrics into a single DataFrame
    bowl_rec = pd.merge(innings, balls, on='bowler')\
                 .merge(runs, on='bowler')\
                 .merge(wkts, on='bowler')\
                 .merge(sixes, on='bowler')\
                 .merge(fours, on='bowler')\
                 .merge(dots, on='bowler')\
                 .merge(three_wicket_hauls, on='bowler', how='left')\
                 .merge(maiden_overs_count, on='bowler', how='left')\
                 .merge(fpi, on='bowler', how='left')\
                 .merge(bbi, on='bowler', how='left')
                  

    # Fill NaN values for bowlers with no 3W hauls or maiden overs
    bowl_rec['three_wicket_hauls'] = bowl_rec['three_wicket_hauls'].fillna(0)
    bowl_rec['maiden_overs'] = bowl_rec['maiden_overs'].fillna(0)
    debut_year = df.groupby('bowler')['season'].min().reset_index()
    final_year = df.groupby('bowler')['season'].max().reset_index()
    debut_year.rename(columns={'season': 'debut_year'}, inplace=True)
    final_year.rename(columns={'season': 'final_year'}, inplace=True)
    bowl_rec = bowl_rec.merge(debut_year, on='bowler').merge(final_year, on='bowler')


    # Calculate additional metrics
    bowl_rec['dot%'] = (bowl_rec['dots'] / bowl_rec['balls']) * 100

    # Check for zeros before performing calculations
    bowl_rec['avg'] = bowl_rec['runs'] / bowl_rec['wkts'].replace(0, np.nan)
    bowl_rec['sr'] = bowl_rec['balls'] / bowl_rec['wkts'].replace(0, np.nan)
    bowl_rec['econ'] = (bowl_rec['runs'] * 6 / bowl_rec['balls'].replace(0, np.nan))
    bowl_rec['fantasy_points_per_match'] = bowl_rec['fantasy_points'] / bowl_rec['innings'].replace(0, np.nan)

    return bowl_rec
    
venue_country_map = {
    'Melbourne Cricket Ground': 'Australia',
    'Simonds Stadium, South Geelong': 'Australia',
    'Adelaide Oval': 'Australia',
    'Sinhalese Sports Club Ground': 'Sri Lanka',
    'Saxton Oval': 'New Zealand',
    'Asian Institute of Technology Ground': 'Thailand',
    'North Sydney Oval': 'Australia',
    'Manuka Oval': 'Australia',
    'Coolidge Cricket Ground': 'West Indies',
    'Sharjah Cricket Stadium': 'UAE',
    'Senwes Park': 'South Africa',
    'Buffalo Park': 'South Africa',
    'The Wanderers Stadium': 'South Africa',
    'SuperSport Park': 'South Africa',
    'Newlands': 'South Africa',
    'The Cooper Associates County Ground': 'England',
    'County Ground': 'England',
    'Brabourne Stadium': 'India',
    'Bay Oval': 'New Zealand',
    'Pukekura Park': 'New Zealand',
    'Seddon Park': 'New Zealand',
    'Nondescripts Cricket Club Ground': 'Sri Lanka',
    'Mangaung Oval': 'South Africa',
    'Allan Border Field': 'Australia',
    'YMCA Cricket Club': 'Ireland',
    'The Village, Malahide, Dublin': 'Ireland',
    'Pembroke Cricket Club, Sandymount': 'Ireland',
    'VRA Ground': 'Netherlands',
    'Sportpark Maarschalkerweerd': 'Netherlands',
    'Kinrara Academy Oval': 'Malaysia',
    'Royal Selangor Club': 'Malaysia',
    'Providence Stadium': 'West Indies',
    'Daren Sammy National Cricket Stadium, Gros Islet': 'West Indies',
    'Sir Vivian Richards Stadium, North Sound': 'West Indies',
    'Westpac Stadium': 'New Zealand',
    'Eden Park': 'New Zealand',
    'Brian Lara Stadium, Tarouba': 'West Indies',
    'Colts Cricket Club Ground': 'Sri Lanka',
    'Colombo Cricket Club Ground': 'Sri Lanka',
    'Chilaw Marians Cricket Club Ground': 'Sri Lanka',
    'County Ground, Hove': 'England',
    'Barsapara Cricket Stadium': 'India',
    'Southend Club Cricket Stadium': 'Pakistan',
    'Sydney Showground Stadium': 'Australia',
    'W.A.C.A. Ground': 'Australia',
    'Junction Oval': 'Australia',
    'Sydney Cricket Ground': 'Australia',
    'P Sara Oval': 'Sri Lanka',
    'LC de Villiers Oval': 'South Africa',
    'City Oval': 'South Africa',
    'Willowmoore Park': 'South Africa',
    'Sydney Parade': 'Ireland',
    'Basin Reserve': 'New Zealand',
    'La Manga Club Top Ground': 'Spain',
    'Sportpark Het Schootsveld': 'Netherlands',
    'Forthill': 'Scotland',
    'Lochlands': 'Scotland',
    'Kensington Oval, Barbados': 'West Indies',
    'Lalabhai Contractor Stadium': 'India',
    'Darren Sammy National Cricket Stadium, St Lucia': 'West Indies',
    'Providence Stadium, Guyana': 'West Indies',
    'Gaddafi Stadium': 'Pakistan',
    'Pokhara Rangasala': 'Nepal',
    'Kingsmead': 'South Africa',
    'Sky Stadium': 'New Zealand',
    'McLean Park': 'New Zealand',
    'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium': 'India',
    'County Ground, Northampton': 'England',
    'County Ground, Chelmsford': 'England',
    'The Cooper Associates County Ground, Taunton': 'England',
    'Civil Service Cricket Club, Stormont, Belfast': 'Northern Ireland',
    'Carrara Oval': 'Australia',
    'Sir Vivian Richards Stadium, North Sound, Antigua': 'West Indies',
    'Coolidge Cricket Ground, Antigua': 'West Indies',
    'La Manga Club Bottom Ground': 'Spain',
    'John Davies Oval, Queenstown': 'New Zealand',
    'Edgbaston, Birmingham': 'England',
    'Kinrara Academy Oval, Kuala Lumpur': 'Malaysia',
    'County Ground, New Road, Worcester': 'England',
    'County Ground, Derby': 'England',
    'Riverside Ground, Chester-le-Street': 'England',
    'County Ground, Bristol': 'England',
    'Gaddafi Stadium, Lahore': 'Pakistan',
    'Southend Club Cricket Stadium, Karachi': 'Pakistan',
    'Pembroke Cricket Club, Sandymount, Dublin': 'Ireland',
    'Bready Cricket Club, Magheramason, Bready': 'Ireland',
    'Rangiri Dambulla International Stadium': 'Sri Lanka',
    'Grange Cricket Club Ground, Raeburn Place, Edinburgh': 'Scotland',
    'Sheikh Zayed Stadium, Abu Dhabi': 'UAE',
    'Tolerance Oval, Abu Dhabi': 'UAE',
    'Sylhet International Cricket Stadium, Academy Ground': 'Bangladesh',
    'Sylhet International Cricket Stadium': 'Bangladesh',
    'Kennington Oval, London': 'England',
    "Lord's, London": 'England',
    'Newlands, Cape Town': 'South Africa',
    'Boland Park, Paarl': 'South Africa',
    "St George's Park, Gqeberha": 'South Africa',
    'Kensington Oval, Bridgetown, Barbados': 'West Indies',
    'Buffalo Park, East London': 'South Africa',
    'Hagley Oval, Christchurch': 'New Zealand',
    'University Oval, Dunedin': 'New Zealand',
    'North Sydney Oval, Sydney': 'Australia',
    'Bellerive Oval, Hobart': 'Australia',
    'Dr DY Patil Sports Academy, Mumbai': 'India',
    'Brabourne Stadium, Mumbai': 'India',
    'Sinhalese Sports Club Ground, Colombo': 'Sri Lanka',
    'Allan Border Field, Brisbane': 'Australia',
    'Manuka Oval, Canberra': 'Australia',
    'Daren Sammy National Cricket Stadium, Gros Islet, St Lucia': 'West Indies',
    'P Sara Oval, Colombo': 'Sri Lanka',
    'National Stadium, Karachi': 'Pakistan',
    'Shere Bangla National Stadium, Mirpur': 'Bangladesh',
    'Sportpark Maarschalkerweerd, Utrecht': 'Netherlands',
    'Saxton Oval, Nelson': 'New Zealand',
    'Basin Reserve, Wellington': 'New Zealand',
    'Willowmoore Park, Benoni': 'South Africa',
    'Desert Springs Cricket Ground, Almeria': 'Spain',
    'Diamond Oval, Kimberley': 'South Africa',
    'Senwes Park, Potchefstroom': 'South Africa',
    'Headingley, Leeds': 'England',
    'The Rose Bowl, Southampton': 'England',
    'St Lawrence Ground, Canterbury': 'England',
    'Zhejiang University of Technology Cricket Field': 'China',
    'Zahur Ahmed Chowdhury Stadium, Chattogram': 'Bangladesh',
    'Wankhede Stadium, Mumbai': 'India',
    'Achimota Senior Secondary School A Field, Accra': 'Ghana',
    'Zayed Cricket Stadium, Abu Dhabi': 'UAE',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'India',
    'Mahinda Rajapaksa International Cricket Stadium, Sooriyawewa, Hambantota': 'Sri Lanka',
    'VRA Ground, Amstelveen': 'Netherlands',
    'Trent Bridge': 'England',
    'Kennington Oval': 'England',
    'Beausejour Stadium, Gros Islet': 'West Indies',
    'Kensington Oval, Bridgetown': 'West Indies',
    'Boland Bank Park': 'South Africa',
    'Galle International Stadium': 'Sri Lanka',
    'R Premadasa Stadium': 'Sri Lanka',
    'St Lawrence Ground': 'England',
    'Riverside Ground': 'England',
    'Old Trafford': 'England',
    'Arundel Castle Cricket Club Ground': 'England',
    'Haslegrave Ground': 'England',
    'Guanggong International Cricket Stadium': 'China',
    'The Rose Bowl': 'England',
    'Stadium Australia': 'Australia',
    'Sylhet Stadium': 'Bangladesh',
    'Shere Bangla National Stadium': 'Bangladesh',
    'Edgbaston': 'England',
    'West End Park International Cricket Stadium': 'Qatar',
    'Kerrydale Oval': 'Australia',
    'Mercantile Cricket Association Ground': 'Sri Lanka',
    'Sophia Gardens': 'Wales',
    'Terdthai Cricket Ground': 'Thailand',
    "National Cricket Stadium, St George's": 'Grenada',
    'Boland Park': 'South Africa',
    'New Wanderers Stadium': 'South Africa',
    'M Chinnaswamy Stadium': 'India',
    'Feroz Shah Kotla': 'India',
    'MA Chidambaram Stadium, Chepauk': 'India',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'India',
    'Vidarbha Cricket Association Stadium, Jamtha': 'India',
    'Himachal Pradesh Cricket Association Stadium': 'India',
    'Wankhede Stadium': 'India',
    'Eden Gardens': 'India',
    'Bready Cricket Club, Magheramason': 'Ireland',
    'Desert Springs Cricket Ground': 'Spain'
}


# Preprocess the debut column to extract the year
idf['debut_year'] = idf['debut_year'].str.split('/').str[0]  # Extract the year from "YYYY/YY"
pdf.rename(columns={'batting Style': 'batting_style','bowling Style': 'bowling_style'}, inplace=True)
bowling_style_mapping = {
    'Righ-arm medium fast ': 'Right-arm medium fast',
    'Right arm Medium fast': 'Right-arm medium fast',
    'Right-arm Medium fast': 'Right-arm medium fast',
    'Right-arm medium fast': 'Right-arm medium fast',
    'Right-arm Offbreak': 'Right-arm off-break',
    'Right-arm fast seam': 'Right-arm fast',
    'Right arm fast': 'Right-arm fast',
    'Right-arm fast': 'Right-arm fast',
    'Right-arm fast-medium/Off-spin': 'Right-arm fast-medium',
    'Right-arm off-break, Legbreak': 'Right-arm off-break and Legbreak',
    'Right-Arm Off Spin': 'Right-arm off-break',
    'Legbreak Googly': 'Right-arm leg-spin',  # Updated mapping
    'Righ-arm leg-spin': 'Right-arm leg-spin',
    'Left arm Medium': 'Left-arm medium',
    'Left-arm orthodox': 'Slow left-arm orthodox',
    'Left arm wrist spin': 'Left-arm wrist spin',
    'Right-arm off break': 'Right-arm off-break',
    'Righ-arm medium': 'Right-arm medium fast',  # Mapping to Right-arm medium fast
    'Right arm medium fast': 'Right-arm medium fast',  # Mapping to Right-arm medium fast
    'Right arm Medium': 'Right-arm medium fast',  # Mapping to Right-arm medium fast
}

# Apply the mapping to the 'bowling_style' column in the PDF dataframe
pdf['bowling_style'] = pdf['bowling_style'].replace(bowling_style_mapping)


# Sidebar for selecting between "Player Profile" and "Matchup Analysis"
sidebar_option = st.sidebar.radio(
    "Select an option:",
    ("Player Profile", "Matchup Analysis","Strength vs Weakness","ICC WT20I 2024 Analysis")
)

if sidebar_option == "Player Profile":
    st.header("Player Profile")

    # Player search input (selectbox)
    player_name = st.selectbox("Search for a player", idf['batsman'].unique())

    # Filter the data for the selected player
    player_info = idf[idf['batsman'] == player_name].iloc[0]

    # Check if the player exists in info_df
    matching_rows = info_df[info_df['Player_name'] == player_name]

    if not matching_rows.empty:
        # If there is a matching row, access the first one
        p_info = matching_rows.iloc[0]
    else:
        # st.write(f"No player found with the name '{player_name}'")
        p_info = None  # Set a fallback

    # Tabs for "Overview", "Career Statistics", and "Current Form"
    tab1, tab2, tab3 = st.tabs(["Overview", "Career Statistics", "Current Form"])

    with tab1:
        st.header("Overview")

        # Create columns for the first row (full name, country, age)
        col1, col2, col3 = st.columns(3)

        # Display player profile information
        with col1:
            st.markdown("FULL NAME:")
            st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{player_info['batsman']}</span>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("COUNTRY:")
            st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{player_info['batting_team'].upper()}</span>", unsafe_allow_html=True)
        
        with col3:
            st.markdown("AGE:")
            if p_info is not None:
                st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{p_info['Age']}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size: 20px; font-weight: bold;'>N/A</span>", unsafe_allow_html=True)

        # Create columns for the second row (batting style, bowling style, playing role)
        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("BATTING STYLE:")
            if p_info is not None:
                st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{p_info['Batting Style'].upper()}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size: 20px; font-weight: bold;'>N/A</span>", unsafe_allow_html=True)

        with col5:
            st.markdown("BOWLING STYLE:")
            if p_info is not None:
                if p_info['Bowling Style'] == 'N/A':
                    st.markdown("<span style='font-size: 20px; font-weight: bold;'>NONE</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{p_info['Bowling Style'].upper()}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size: 20px; font-weight: bold;'>N/A</span>", unsafe_allow_html=True)

        with col6:
            st.markdown("PLAYING ROLE:")
            if p_info is not None:
                st.markdown(f"<span style='font-size: 20px; font-weight: bold;'>{p_info['Role'].upper()}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span style='font-size: 20px; font-weight: bold;'>N/A</span>", unsafe_allow_html=True)

    with tab2:
        st.header("Career Statistics")

        # Dropdown for Batting or Bowling selection
        option = st.selectbox("Select Career Stat Type", ("Batting", "Bowling"))

        # Show Career Averages based on the dropdown
        st.subheader("Career Performance")

        # Display Career Averages based on selection
        if option == "Batting":
            # Create a temporary DataFrame and filter the player's row
            temp_df = idf.drop(columns=['final_year', 'matches_x', 'matches_y','matches','batting_team'])
            player_stats = temp_df[temp_df['batsman'] == player_name]  # Filter for the selected player

            # Convert column names to uppercase and replace underscores with spaces
            player_stats.columns = [col.upper().replace('_', ' ') for col in player_stats.columns]
            player_stats=round_up_floats(player_stats)
            # Display the player's statistics in a table format with bold headers
            st.markdown("### Batting Statistics")
            columns_to_convert = ['RUNS','HUNDREDS', 'FIFTIES','THIRTIES', 'HIGHEST SCORE']

               # Fill NaN values with 0
            player_stats[columns_to_convert] = player_stats[columns_to_convert].fillna(0)
                
               # Convert the specified columns to integer type
            player_stats[columns_to_convert] = player_stats[columns_to_convert].astype(int)
            st.table(player_stats.style.set_table_attributes("style='font-weight: bold;'"))
            
            allowed_countries = ['India', 'England', 'Australia', 'Pakistan', 'Bangladesh', 
                                 'West Indies', 'Scotland', 'South Africa', 'New Zealand', 'Sri Lanka']
            
            # Initializing an empty DataFrame for results and a counter
            result_df = pd.DataFrame()
            i = 0
            
            # Checking if 'total_runs', 'batsman_runs', 'dismissal_kind', 'batsman', and 'over' are already in bpdf
            if 'total_runs' not in pdf.columns:
                pdf['total_runs'] = pdf['runs_off_bat'] + pdf['extras']  # Create total_runs column
            
                # Renaming necessary columns if they don't exist in the desired format
                pdf = pdf.rename(columns={
                    'runs_off_bat': 'batsman_runs', 
                    'wicket_type': 'dismissal_kind', 
                    'striker': 'batsman', 
                    'innings': 'inning', 
                    'bowler': 'bowler_name'
                })
            
                # Drop rows where 'ball' is missing, if not already done
                pdf = pdf.dropna(subset=['ball'])
            
            # Convert the 'ball' column to numeric if it's not already
            if not pd.api.types.is_numeric_dtype(pdf['ball']):
                pdf['ball'] = pd.to_numeric(pdf['ball'], errors='coerce')
            
            # Calculate 'over' by applying lambda function (check if the 'over' column is already present)
            if 'over' not in pdf.columns:
                pdf['over'] = pdf['ball'].apply(lambda x: mt.floor(x) + 1 if pd.notnull(x) else None)
            
            # Iterate over allowed countries for batting analysis
            for country in allowed_countries:
                temp_df = pdf[pdf['batsman'] == player_name]  # Filter data for the selected batsman
                
                # Filter for the specific country
                temp_df = temp_df[temp_df['bowling_team'] == country]
            
                # Apply the cumulative function (bcum)
                temp_df = cumulator(temp_df)
            
                # If the DataFrame is empty after applying `bcum`, skip this iteration
                if temp_df.empty:
                    continue
            
                # Add the country column with the current country's value
                temp_df['opponent'] = country.upper()
            
                # Reorder columns to make 'country' the first column
                cols = temp_df.columns.tolist()
                new_order = ['opponent'] + [col for col in cols if col != 'opponent']
                temp_df = temp_df[new_order]
                
            
                # Concatenate results into result_df
                if i == 0:
                    result_df = temp_df
                    i += 1
                else:
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
            
            # Display the final result_df
            result_df = result_df.drop(columns=['matches_x','matches_y','batsman','debut_year','final_year','batting_team'])
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            columns_to_convert = ['HUNDREDS', 'FIFTIES','THIRTIES', 'RUNS','HIGHEST SCORE']

            #    # Fill NaN values with 0
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
                
            #    # Convert the specified columns to integer type
            result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
            result_df=round_up_floats(result_df)
            cols = result_df.columns.tolist()

            #    # Specify the desired order with 'year' first
            new_order = ['OPPONENT', 'MATCHES'] + [col for col in cols if col not in ['MATCHES', 'OPPONENT']]
                         
            # #    # Reindex the DataFrame with the new column order
            result_df =result_df[new_order]
 
            st.markdown("### Opponentwise Performance")
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
            
        
            tdf = pdf[pdf['batsman'] == player_name]

            def standardize_season(season):
                if '/' in season:  # Check if the season is in 'YYYY/YY' format
                    year = season.split('/')[0]  # Get the first part
                else:
                    year = season  # Use as is if already in 'YYYY' format
                return year.strip()  # Return the year stripped of whitespace
            tdf['season'] =tdf['season'].apply(standardize_season)
            
            # Populate an array of unique seasons
            unique_seasons = tdf['season'].unique()
            
            # Optional: Convert to a sorted list (if needed)
            unique_seasons = sorted(set(unique_seasons))
            # print(unique_seasons)
            tdf=pd.DataFrame(tdf)
            # print(temp_df.head(50))
            tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
            tdf['total_runs'] = tdf['total_runs'].astype(int)
            # Run a for loop and pass temp_df to a cumulative function
            i=0
            for season in unique_seasons:
                print(i)
                temp_df = tdf[(tdf['season'] == season)]
                print(temp_df.head())
                temp_df = cumulator(temp_df)
                if i==0:
                    result_df = temp_df  # Initialize with the first result_df
                    i=1+i
                else:
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
                result_df = result_df.drop(columns=['batsman', 'batting_team','debut_year','matches_x','matches_y','matches','batting_team'])
                # Convert specific columns to integers
                # Round off the remaining float columns to 2 decimal places
                float_cols = result_df.select_dtypes(include=['float']).columns
                result_df[float_cols] = result_df[float_cols].round(2)
                # columns_to_convert = ['runs', 'hundreds', 'fifties', 'thirties', 'highest_score']

               # Fill NaN values with 0
                # temp_df[columns_to_convert] = temp_df[columns_to_convert].fillna(0)
                
            #    # Convert the specified columns to integer type
                # temp_df[columns_to_convert] = temp_df[columns_to_convert].astype(int)
            # columns_to_convert = ['runs', 'hundreds', 'fifties', 'thirties', 'highest_score']

               # Fill NaN values with 0
            # temp_df[columns_to_convert] = temp_df[columns_to_convert].fillna(0)
                
               # Convert the specified columns to integer type
            # temp_df[columns_to_convert] = temp_df[columns_to_convert].astype(int)
            result_df=result_df.rename(columns={'final_year':'year'})
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            result_df = round_up_floats(result_df)
            columns_to_convert = ['RUNS', 'HUNDREDS', 'FIFTIES', 'THIRTIES', 'HIGHEST SCORE']

               # Fill NaN values with 0
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
                
               # Convert the specified columns to integer type
            result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
                    
            # Display the results
            st.markdown(f"### **Yearwise Performnce**")
            cols = result_df.columns.tolist()

            # # Specify the desired order with 'year' first
            new_order = ['YEAR'] + [col for col in cols if col != 'YEAR']
                     
            # # Reindex the DataFrame with the new column order
            result_df = result_df[new_order]
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))

            tdf = pdf[pdf['batsman'] == player_name]
            temp_df=tdf[(tdf['inning']==1)]
            temp_df=cumulator(temp_df)
            temp_df['inning']=1
            cols = temp_df.columns.tolist()
            new_order = ['inning'] + [col for col in cols if col != 'inning']          
            # Reindex the DataFrame with the new column order
            temp_df =temp_df[new_order] 
            result_df = temp_df
            temp_df=tdf[(tdf['inning']==2)]
            temp_df=cumulator(temp_df)
            temp_df['inning']=2
            cols = temp_df.columns.tolist()
            new_order = ['inning'] + [col for col in cols if col != 'inning']          
            # Reindex the DataFrame with the new column order
            temp_df =temp_df[new_order] 
            result_df = pd.concat([result_df, temp_df], ignore_index=True)
            result_df = result_df.drop(columns=['batsman', 'batting_team','debut_year','matches_x','matches_y','final_year','batting_team'])
            # Convert specific columns to integers
            # Round off the remaining float columns to 2 decimal places
            float_cols = result_df.select_dtypes(include=['float']).columns
            result_df[float_cols] = result_df[float_cols].round(2)
            
            result_df=result_df.rename(columns={'final_year':'year'})
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            columns_to_convert = ['RUNS', 'HUNDREDS', 'FIFTIES', 'THIRTIES', 'HIGHEST SCORE']

               # Fill NaN values with 0
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
                
            #    # Convert the specified columns to integer type
            result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
                    
            # Display the results
            result_df = result_df.drop(columns=['MATCHES'])
            st.markdown(f"### **Inningwise Performnce**")
            st.table(result_df.reset_index(drop=True).style.set_table_attributes("style='font-weight: bold;'"))
        

            
            # Creating a DataFrame to display venues and their corresponding countries
            pdf['country'] = pdf['venue'].map(venue_country_map).fillna('Unknown')
            allowed_countries = ['India', 'England', 'Australia', 'Pakistan', 'Bangladesh',
                     'West Indies', 'Scotland', 'South Africa', 'New Zealand', 'Sri Lanka']
            i=0
            for country in allowed_countries:
                temp_df = pdf[pdf['batsman'] == player_name]
                # print(temp_df.match_id.unique())
                # print(temp_df.head(20))
                temp_df = temp_df[(temp_df['country'] == country)]
                temp_df = cumulator(temp_df)
                temp_df['country']=country.upper()
                cols = temp_df.columns.tolist()
                new_order = ['country'] + [col for col in cols if col != 'country']
                # Reindex the DataFrame with the new column order
                temp_df =temp_df[new_order]
                # print(temp_df)
             # If temp_df is empty after applying cumulator, skip to the next iteration
                if len(temp_df) == 0:
                   continue
                elif i==0:
                    result_df = temp_df
                    i=i+1
                else:
                    result_df = result_df.reset_index(drop=True)
                    temp_df = temp_df.reset_index(drop=True)
                    result_df = result_df.loc[:, ~result_df.columns.duplicated()]
            
                    result_df = pd.concat([result_df, temp_df],ignore_index=True)
                    
            
                result_df = result_df.drop(columns=['batsman', 'batting_team','debut_year','final_year','matches_x','matches_y','batting_team'])
                # Round off the remaining float columns to 2 decimal places
                float_cols = result_df.select_dtypes(include=['float']).columns
                result_df[float_cols] = result_df[float_cols].round(2)
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            result_df = round_up_floats(result_df)
            columns_to_convert = ['RUNS', 'HUNDREDS', 'FIFTIES', 'THIRTIES', 'HIGHEST SCORE']

            #    # Fill NaN values with 0
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
                
            #    # Convert the specified columns to integer type
            result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
            cols = result_df.columns.tolist()
            if 'COUNTRY' in cols:
                new_order = ['COUNTRY'] + [col for col in cols if col != 'COUNTRY']
                result_df = result_df[new_order]
            # result_df = result_df.loc[:, ~result_df.columns.duplicated()]
                result_df = result_df.drop(columns=['MATCHES'])
            st.markdown(f"### **In Host Country**")
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
              

        elif option == "Bowling":
            # Prepare the DataFrame for displaying player-specific bowling statistics
            temp_df = bidf
                
                # Filter for the selected player
            player_stats = temp_df[temp_df['bowler'] == player_name]  # Assuming bidf has bowler data
            if player_stats.empty:
                st.markdown("No Bowling stats available")
            else:   
                    # Convert column names to uppercase and replace underscores with spaces
                    player_stats.columns = [col.upper().replace('_', ' ') for col in player_stats.columns]
                    player_stats=player_stats.rename(columns={'BBI X':'BBI'})
                    player_stats=player_stats.drop(columns=['BBI Y'])
                        
                        # Function to round float values if necessary (assuming round_up_floats exists)
                    player_stats = round_up_floats(player_stats)
                    columns_to_convert = ['RUNS','THREE WICKET HAULS', 'MAIDEN OVERS']
        
                    #    # Fill NaN values with 0
                    player_stats[columns_to_convert] =  player_stats[columns_to_convert].fillna(0)
                        
                    #    # Convert the specified columns to integer type
                    player_stats[columns_to_convert] =  player_stats[columns_to_convert].astype(int)
                        
                        # Display the player's bowling statistics in a table format with bold headers
                    player_stats = player_stats.drop(columns=['BOWLER'])
                    st.markdown("### Bowling Statistics")
                    st.table(player_stats.style.set_table_attributes("style='font-weight: bold;'"))  # Display the filtered DataFrame as a table
                    allowed_countries = ['India', 'England', 'Australia', 'Pakistan', 'Bangladesh', 
                                         'West Indies', 'Scotland', 'South Africa', 'New Zealand', 'Sri Lanka']
                    
                    # Initializing an empty DataFrame for results and a counter
                    result_df = pd.DataFrame()
                    i = 0
                    
                    # Checking if 'total_runs', 'batsman_runs', 'dismissal_kind', 'batsman', and 'over' are already in bpdf
                    if 'total_runs' not in bpdf.columns:
                        bpdf['total_runs'] = bpdf['runs_off_bat'] + bpdf['extras']  # Create total_runs column
                    
                        # Renaming necessary columns if they don't exist in the desired format
                        bpdf = bpdf.rename(columns={
                            'runs_off_bat': 'batsman_runs', 
                            'wicket_type': 'dismissal_kind', 
                            'striker': 'batsman', 
                            'innings': 'inning', 
                            'bowler': 'bowler_name'
                        })
                        # Drop rows where 'ball' is missing, if not already done
                        bpdf = bpdf.dropna(subset=['ball'])
                    
                    # Convert the 'ball' column to numeric if it's not already
                    if not pd.api.types.is_numeric_dtype(bpdf['ball']):
                        bpdf['ball'] = pd.to_numeric(bpdf['ball'], errors='coerce')
                    
                    # Calculate 'over' by applying lambda function (check if the 'over' column is already present)
                    if 'over' not in bpdf.columns:
                        bpdf['over'] = bpdf['ball'].apply(lambda x: mt.floor(x) + 1 if pd.notnull(x) else None)
                    st.markdown("### Opponentwise Performance")
                    for country in allowed_countries:
                                # Iterate over allowed countries for batting analysis
                                temp_df = bpdf[bpdf['bowler'] == player_name]  # Filter data for the selected batsman
                                    
                                # Filter for the specific country
                                temp_df = temp_df[temp_df['batting_team'] == country]
                        
                                # Apply the cumulative function (bcum)
                                temp_df = bcum(temp_df)
                            
                                # If the DataFrame is empty after applying `bcum`, skip this iteration
                                if temp_df.empty:
                                    continue
                            
                                # Add the country column with the current country's value
                                temp_df['opponent'] = country.upper()
                            
                                # Reorder columns to make 'country' the first column
                                cols = temp_df.columns.tolist()
                                new_order = ['opponent'] + [col for col in cols if col != 'opponent']
                                temp_df = temp_df[new_order]
                                
                            
                                # Concatenate results into result_df
                                if i == 0:
                                    result_df = temp_df
                                    i += 1
                                else:
                                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
                    # Display the final result_df
                    result_df = result_df.drop(columns=['bowler','debut_year','final_year'])
                    result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
                    columns_to_convert = ['RUNS','THREE WICKET HAULS', 'MAIDEN OVERS']
        
                       # Fill NaN values with 0
                    result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
                        
                       # Convert the specified columns to integer type
                    result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
                    # result_df=round_up_floats(result_df)
                    st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
          
                    
                    tdf = bpdf[bpdf['bowler'] == player_name]  # Filter data for the specific bowler
        
                    def standardize_season(season):
                                    if '/' in season:  # Check if the season is in 'YYYY/YY' format
                                        year = season.split('/')[0]  # Get the first part
                                    else:
                                        year = season  # Use as is if already in 'YYYY' format
                                    return year.strip()  # Return the year stripped of whitespace
                                # Standardize the 'season' column
                    tdf['season'] = tdf['season'].apply(standardize_season)
                    
                                # Populate an array of unique seasons
                    unique_seasons = sorted(set(tdf['season'].unique()))  # Optional: Sorted list of unique seasons
                    
                                # Initialize an empty DataFrame to store the final results
                    i = 0
                    for season in unique_seasons:
                            temp_df = tdf[tdf['season'] == season]  # Filter data for the current season
                            temp_df = bcum(temp_df)  # Apply the cumulative function (specific to your logic)
                            temp_df['YEAR'] = season
                                
                            if i == 0:
                                    result_df = temp_df  # Initialize the result_df with the first season's data
                                    i += 1
                            else:
                                    result_df = pd.concat([result_df, temp_df], ignore_index=True)  # Append subsequent data
                                      
                    result_df = result_df.drop(columns=['bowler','debut_year','final_year'])
                    result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
                    columns_to_convert = ['THREE WICKET HAULS', 'MAIDEN OVERS']

                       # Fill NaN values with 0
                    result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
            
                       # Convert the specified columns to integer type
                    result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
                    result_df=round_up_floats(result_df)
                    # result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
        
                    # No need to convert columns to integer (for bowling-specific data)
        
                    # Display the results
                    st.markdown(f"### **Yearwise Bowling Performance**")
                    cols = result_df.columns.tolist()
        
                    # Specify the desired order with 'YEAR' first
                    new_order = ['YEAR'] + [col for col in cols if col != 'YEAR']
        
                    # Reindex the DataFrame with the new column order
                    result_df = result_df[new_order]
        
                    # Display the table with bold headers
                    st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
    
        

                    # Filter data for the specific bowler
                    tdf = bpdf[bpdf['bowler'] == player_name]

                            
                    
                    # Process for the first inning
                    temp_df = tdf[(tdf['inning'] == 1)]
                    temp_df = bcum(temp_df)  # Apply the cumulative function specific to bowlers
                    temp_df['inning'] = 1  # Add the inning number
        
                    # Reorder columns to have 'inning' first
                    cols = temp_df.columns.tolist()
                    new_order = ['inning'] + [col for col in cols if col != 'inning']          
                    temp_df = temp_df[new_order] 
        
                    # Initialize result_df with the first inning's data
                    result_df = temp_df
        
                    # Process for the second inning
                    temp_df = tdf[(tdf['inning'] == 2)]
                    temp_df = bcum(temp_df)  # Apply the cumulative function specific to bowlers
                    temp_df['inning'] = 2  # Add the inning number
        
                    # Reorder columns to have 'inning' first
                    cols = temp_df.columns.tolist()
                    new_order = ['inning'] + [col for col in cols if col != 'inning']          
                    temp_df = temp_df[new_order] 
        
                    # Concatenate the results for both innings
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
        
                    # Drop unnecessary columns
                    result_df = result_df.drop(columns=['bowler','debut_year','final_year'])
                    result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
                    columns_to_convert = ['THREE WICKET HAULS', 'MAIDEN OVERS']

                       # Fill NaN values with 0
                    result_df[columns_to_convert] =  result_df[columns_to_convert].fillna(0)
            
                       # Convert the specified columns to integer type
                    result_df[columns_to_convert] =  result_df[columns_to_convert].astype(int)
                    result_df=round_up_floats(result_df)
        
                    # Display the results
                    st.markdown(f"### **Inningwise Bowling Performance**")
                    st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))

        
        
                    # Creating a DataFrame to display venues and their corresponding countries
                    bpdf['country'] = bpdf['venue'].map(venue_country_map)
                    allowed_countries = ['India', 'England', 'Australia', 'Pakistan', 'Bangladesh',
                                         'West Indies', 'Scotland', 'South Africa', 'New Zealand', 'Sri Lanka']
        
                    i = 0
                    for country in allowed_countries:
                        temp_df = bpdf[bpdf['bowler'] == player_name] 
                        temp_df = temp_df[(temp_df['country'] == country)]
                        temp_df = bcum(temp_df)
                        temp_df.insert(0, 'country', country.upper())
            
        
                        # If temp_df is empty after applying bcum, skip to the next iteration
                        if len(temp_df) == 0:
                            continue
                        elif i == 0:
                            result_df = temp_df
                            i += 1
                        else:
                            result_df = result_df.reset_index(drop=True)
                            temp_df = temp_df.reset_index(drop=True)
                            result_df = result_df.loc[:, ~result_df.columns.duplicated()]
        
                            result_df = pd.concat([result_df, temp_df], ignore_index=True)
        
                    if 'bowler' in result_df.columns:
                        result_df = result_df.drop(columns=['bowler','debut_year','final_year'])
                    result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
                    columns_to_convert = ['RUNS','THREE WICKET HAULS', 'MAIDEN OVERS']

                       # Fill NaN values with 0
                    result_df[columns_to_convert] =  result_df[columns_to_convert].fillna(0)
            
                       # Convert the specified columns to integer type
                    result_df[columns_to_convert] =  result_df[columns_to_convert].astype(int)
                    result_df=round_up_floats(result_df)
        
                    st.markdown(f"### **In Host Country**")
                    st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))

    with tab3:
            st.header("Current Form")
            current_form_df = get_current_form(bpdf, player_name)
            
            if not current_form_df.empty:
                current_form_df.columns = [col.upper() for col in current_form_df.columns]
                
                # Rearranging columns
                cols = current_form_df.columns.tolist()
                new_order = ['MATCH ID', 'DATE'] + [col for col in cols if col not in ['MATCH ID', 'DATE']]
                current_form_df = current_form_df[new_order]
                current_form_df = current_form_df.loc[:, ~current_form_df.columns.duplicated()]
                
                # Formatting the date
                current_form_df['DATE'] = pd.to_datetime(current_form_df['DATE'], format='%m/%d/%Y')
                current_form_df = current_form_df.sort_values(by='DATE', ascending=False)
                current_form_df = current_form_df.reset_index(drop=True)
                current_form_df['DATE'] = current_form_df['DATE'].dt.strftime('%m/%d/%Y')
                
                # Displaying the table with clickable MATCH ID
                current_form_df.index = current_form_df.index + 1
                st.markdown(current_form_df.to_html(escape=False), unsafe_allow_html=True)
                
                # Handling clicks on MATCH ID links
                for match_id in current_form_df['MATCH ID']:
                    if st.button(f'View Match {match_id}'):
                        print("Fn called")
                        print(match_id)
                        show_match_details(match_id)
            else:
                st.write("No recent matches found for this player.")
    
# If "Matchup Analysis" is selected
elif sidebar_option == "Matchup Analysis":
    
    st.header("Matchup Analysis")
    
    # Filter unique batters and bowlers from the DataFrame
    unique_batters = pdf['batsman'].unique()  # Adjust the column name as per your PDF data structure
    unique_bowlers = pdf['bowler'].unique()    # Adjust the column name as per your PDF data structure
    unique_batters = unique_batters[unique_batters != '0']  # Filter out '0'
    unique_bowlers = unique_bowlers[unique_bowlers != '0']  # Filter out '0'

    # Search box for Batters
    batter_name = st.selectbox("Select a Batter", unique_batters)

    # Search box for Bowlers
    bowler_name = st.selectbox("Select a Bowler", unique_bowlers)

    # Dropdown for grouping options
    grouping_option = st.selectbox("Group By", ["Year", "Match", "Venue", "Inning"])
    matchup_df = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]

    # Step 3: Create a download option for the DataFrame
    if not matchup_df.empty:
        # Convert the DataFrame to CSV format
        csv = matchup_df.to_csv(index=False)  # Generate CSV string
        
        # Step 4: Create the download button
        st.download_button(
            label="Download Matchup Data as CSV",
            data=csv,  # Pass the CSV string directly
            file_name=f"{batter_name}_vs_{bowler_name}_matchup.csv",
            mime="text/csv"  # Specify the MIME type for CSV
        )
        if grouping_option == "Year":
            tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]
    
            def standardize_season(season):
                if '/' in season:  # Check if the season is in 'YYYY/YY' format
                    year = season.split('/')[0]  # Get the first part
                else:
                    year = season  # Use as is if already in 'YYYY' format
                return year.strip()  # Return the year stripped of whitespace
    
            tdf['season'] = tdf['season'].apply(standardize_season)
    
            # Populate an array of unique seasons
            unique_seasons = tdf['season'].unique()
            
            # Optional: Convert to a sorted list (if needed)
            unique_seasons = sorted(set(unique_seasons))
    
            # Ensure tdf is a DataFrame
            tdf = pd.DataFrame(tdf)
            tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
            tdf['total_runs'] = tdf['total_runs'].astype(int)
    
            # Initialize an empty result DataFrame
            result_df = pd.DataFrame()
            i=0
            # Run a for loop and pass temp_df to a cumulative function
            for season in unique_seasons:
                temp_df = tdf[tdf['season'] == season]
                temp_df = cumulator(temp_df)
    
                if i==0:
                        result_df = temp_df  # Initialize with the first result_df
                        i=1+i
                else:
                        result_df = pd.concat([result_df, temp_df], ignore_index=True)
            # Drop unnecessary columns related to performance metrics
            columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score','matches']
            result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
    
            # Convert specific columns to integers and fill NaN values
            columns_to_convert = ['runs','dismissals']
            for col in columns_to_convert:
                result_df[col] = result_df[col].fillna(0).astype(int)
    
            result_df = result_df.rename(columns={'final_year': 'year'})
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
    
            # Display the results
            st.markdown("### **Yearwise Performance**")
            cols = result_df.columns.tolist()
    
            # Specify the desired order with 'year' first
            new_order = ['YEAR'] + [col for col in cols if col != 'YEAR']
                      
            # Reindex the DataFrame with the new column order
            result_df = result_df[new_order]
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
        elif grouping_option == "Match":
            tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]
    
            # Populate an array of unique match IDs
            unique_matches = sorted(set(tdf['match_id'].unique()))
    
            # Ensure tdf is a DataFrame
            tdf = pd.DataFrame(tdf)
            tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
            tdf['total_runs'] = tdf['total_runs'].astype(int)
    
            # Initialize an empty result DataFrame
            result_df = pd.DataFrame()
            i = 0
    
            # Run a for loop and pass temp_df to a cumulative function
            for match_id in unique_matches:
                temp_df = tdf[tdf['match_id'] == match_id]
                current_match_id = match_id
                temp_df = cumulator(temp_df)
                temp_df.insert(0, 'MATCH_ID', current_match_id)
    
                if i == 0:
                    result_df = temp_df  # Initialize with the first result_df
                    i = 1 + i
                else:
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
            columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 
                               'fifties', 'hundreds', 'thirties', 'highest_score', 'season','matches']
            result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
    
            # Convert specific columns to integers and fill NaN values
            columns_to_convert = ['runs', 'dismissals']
            for col in columns_to_convert:
                result_df[col] = result_df[col].fillna(0).astype(int)
    
            # Rename columns for better presentation
            result_df = result_df.rename(columns={'match_id': 'MATCH ID'})
            
            
            
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            result_df['FINAL YEAR']=result_df['FINAL YEAR'].apply(standardize_season)
            
            result_df = result_df.rename(columns={'FINAL YEAR': 'YEAR'})  
    
            # Display the results
            st.markdown("### **Matchwise Performance**")
            cols = result_df.columns.tolist()
    
            # Reindex the DataFrame with the new column order
            result_df=result_df.sort_values('YEAR',ascending=True)
            result_df=result_df[['MATCH ID'] + ['YEAR'] + [col for col in result_df.columns if col not in ['MATCH ID','YEAR']]]
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
            for match_id in result_df['MATCH ID']:
                        if st.button(f'View Match {match_id}'):
                            show_match_details(match_id)
            
                     
        elif grouping_option == "Venue":
            # Filter the DataFrame for the selected batsman and bowler
            tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]
        
            # Ensure tdf is a DataFrame and populate unique venue values
            tdf = pd.DataFrame(tdf)
            tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
            tdf['total_runs'] = tdf['total_runs'].astype(int)
        
            # Initialize an empty result DataFrame
            result_df = pd.DataFrame()
            i = 0
        
            # Populate an array of unique venues
            unique_venues = tdf['venue'].unique()
            
            for venue in unique_venues:
                # Filter temp_df for the current venue
                temp_df = tdf[tdf['venue'] == venue]
        
                # Store the current venue in a variable
                current_venue = venue
        
                # Call the cumulator function
                temp_df = cumulator(temp_df)
        
                # Insert the current venue as the first column in temp_df
                temp_df.insert(0, 'VENUE', current_venue)
        
                # Concatenate results
                if i == 0:
                    result_df = temp_df  # Initialize with the first result_df
                    i += 1
                else:
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
        
            # Drop unnecessary columns related to performance metrics
            columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score', 'matches']
            result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
        
            # Convert specific columns to integers and fill NaN values
            columns_to_convert = ['runs', 'dismissals']
            for col in columns_to_convert:
                result_df[col] = result_df[col].fillna(0).astype(int)
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            result_df['FINAL YEAR']=result_df['FINAL YEAR'].apply(standardize_season)
            
            result_df = result_df.rename(columns={'FINAL YEAR': 'YEAR'})   
        
            # Display the results
            st.markdown("### **Venuewise Performance**")
            cols = result_df.columns.tolist()
        
            # Specify the desired order with 'venue' first
            new_order = ['VENUE'] + [col for col in cols if col != 'VENUE']
            
                          
            # Reindex the DataFrame with the new column order
            result_df = result_df[new_order]
            result_df=result_df.sort_values('YEAR',ascending=True)
            result_df=result_df[['VENUE'] + ['YEAR'] + [col for col in result_df.columns if col not in ['VENUE','YEAR']]]
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
            
        else:
            # Assuming pdf is your main DataFrame
            # Filter for innings 1 and 2 and prepare to accumulate results
            innings = [1, 2]
            result_df = pd.DataFrame()  # Initialize an empty DataFrame for results
            
            for inning in innings:
                # Filter for the specific inning
                tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name) & (pdf['inning'] == inning)]
                
                # Check if there's any data for the current inning
                if not tdf.empty:
                    # Call the cumulator function
                    temp_df = cumulator(tdf)
            
                    # Add the inning as the first column in temp_df
                    temp_df.insert(0, 'INNING', inning)
            
                    # Concatenate to the main result DataFrame
                    result_df = pd.concat([result_df, temp_df], ignore_index=True)
            
            # After processing both innings, drop unnecessary columns if needed
            columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score', 'matches','last_year']
            result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
            
            # Convert specific columns to integers and fill NaN values
            columns_to_convert = ['runs', 'dismissals']
            for col in columns_to_convert:
                result_df[col] = result_df[col].fillna(0).astype(int)
            
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            
            # Display the results
            st.markdown("### **Innings Performance**")
            result_df=result_df[['INNING'] + [col for col in result_df.columns if col not in ['INNING']]]
            st.table(result_df.style.set_table_attributes("style='fsont-weight: bold;'"))
    else:
         st.warning("No data available for the selected matchup.")
    # if grouping_option == "Year":
    #     tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]

    #     def standardize_season(season):
    #         if '/' in season:  # Check if the season is in 'YYYY/YY' format
    #             year = season.split('/')[0]  # Get the first part
    #         else:
    #             year = season  # Use as is if already in 'YYYY' format
    #         return year.strip()  # Return the year stripped of whitespace

    #     tdf['season'] = tdf['season'].apply(standardize_season)

    #     # Populate an array of unique seasons
    #     unique_seasons = tdf['season'].unique()
        
    #     # Optional: Convert to a sorted list (if needed)
    #     unique_seasons = sorted(set(unique_seasons))

    #     # Ensure tdf is a DataFrame
    #     tdf = pd.DataFrame(tdf)
    #     tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
    #     tdf['total_runs'] = tdf['total_runs'].astype(int)

    #     # Initialize an empty result DataFrame
    #     result_df = pd.DataFrame()
    #     i=0
    #     # Run a for loop and pass temp_df to a cumulative function
    #     for season in unique_seasons:
    #         temp_df = tdf[tdf['season'] == season]
    #         temp_df = cumulator(temp_df)

    #         if i==0:
    #                 result_df = temp_df  # Initialize with the first result_df
    #                 i=1+i
    #         else:
    #                 result_df = pd.concat([result_df, temp_df], ignore_index=True)
    #     # Drop unnecessary columns related to performance metrics
    #     columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score','matches']
    #     result_df = result_df.drop(columns=columns_to_drop, errors='ignore')

    #     # Convert specific columns to integers and fill NaN values
    #     columns_to_convert = ['runs','dismissals']
    #     for col in columns_to_convert:
    #         result_df[col] = result_df[col].fillna(0).astype(int)

    #     result_df = result_df.rename(columns={'final_year': 'year'})
    #     result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]

    #     # Display the results
    #     st.markdown("### **Yearwise Performance**")
    #     cols = result_df.columns.tolist()

    #     # Specify the desired order with 'year' first
    #     new_order = ['YEAR'] + [col for col in cols if col != 'YEAR']
                  
    #     # Reindex the DataFrame with the new column order
    #     result_df = result_df[new_order]
    #     st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
    # elif grouping_option == "Match":
    #     tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]

    #     # Populate an array of unique match IDs
    #     unique_matches = sorted(set(tdf['match_id'].unique()))

    #     # Ensure tdf is a DataFrame
    #     tdf = pd.DataFrame(tdf)
    #     tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
    #     tdf['total_runs'] = tdf['total_runs'].astype(int)

    #     # Initialize an empty result DataFrame
    #     result_df = pd.DataFrame()
    #     i = 0

    #     # Run a for loop and pass temp_df to a cumulative function
    #     for match_id in unique_matches:
    #         temp_df = tdf[tdf['match_id'] == match_id]
    #         current_match_id = match_id
    #         temp_df = cumulator(temp_df)
    #         temp_df.insert(0, 'MATCH_ID', current_match_id)

    #         if i == 0:
    #             result_df = temp_df  # Initialize with the first result_df
    #             i = 1 + i
    #         else:
    #             result_df = pd.concat([result_df, temp_df], ignore_index=True)
    #     columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 
    #                        'fifties', 'hundreds', 'thirties', 'highest_score', 'season','matches']
    #     result_df = result_df.drop(columns=columns_to_drop, errors='ignore')

    #     # Convert specific columns to integers and fill NaN values
    #     columns_to_convert = ['runs', 'dismissals']
    #     for col in columns_to_convert:
    #         result_df[col] = result_df[col].fillna(0).astype(int)

    #     # Rename columns for better presentation
    #     result_df = result_df.rename(columns={'match_id': 'MATCH ID'})
        
        
    #     result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
    #     result_df['FINAL YEAR']=result_df['FINAL YEAR'].apply(standardize_season)
        
    #     result_df = result_df.rename(columns={'FINAL YEAR': 'YEAR'})  

    #     # Display the results
    #     st.markdown("### **Matchwise Performance**")
    #     cols = result_df.columns.tolist()

    #     # Reindex the DataFrame with the new column order
    #     result_df=result_df.sort_values('YEAR',ascending=True)
    #     result_df=result_df[['MATCH ID'] + ['YEAR'] + [col for col in result_df.columns if col not in ['MATCH ID','YEAR']]]
    #     st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
    #     for match_id in result_df['MATCH ID']:
    #                 if st.button(f'View Match {match_id}'):
    #                     show_match_details(match_id)
        
                 
    # elif grouping_option == "Venue":
    #     # Filter the DataFrame for the selected batsman and bowler
    #     tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name)]
    
    #     # Ensure tdf is a DataFrame and populate unique venue values
    #     tdf = pd.DataFrame(tdf)
    #     tdf['batsman_runs'] = tdf['batsman_runs'].astype(int)
    #     tdf['total_runs'] = tdf['total_runs'].astype(int)
    
    #     # Initialize an empty result DataFrame
    #     result_df = pd.DataFrame()
    #     i = 0
    
    #     # Populate an array of unique venues
    #     unique_venues = tdf['venue'].unique()
        
    #     for venue in unique_venues:
    #         # Filter temp_df for the current venue
    #         temp_df = tdf[tdf['venue'] == venue]
    
    #         # Store the current venue in a variable
    #         current_venue = venue
    
    #         # Call the cumulator function
    #         temp_df = cumulator(temp_df)
    
    #         # Insert the current venue as the first column in temp_df
    #         temp_df.insert(0, 'VENUE', current_venue)
    
    #         # Concatenate results
    #         if i == 0:
    #             result_df = temp_df  # Initialize with the first result_df
    #             i += 1
    #         else:
    #             result_df = pd.concat([result_df, temp_df], ignore_index=True)
    
    #     # Drop unnecessary columns related to performance metrics
    #     columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score', 'matches']
    #     result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
    
    #     # Convert specific columns to integers and fill NaN values
    #     columns_to_convert = ['runs', 'dismissals']
    #     for col in columns_to_convert:
    #         result_df[col] = result_df[col].fillna(0).astype(int)
    #     result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
    #     result_df['FINAL YEAR']=result_df['FINAL YEAR'].apply(standardize_season)
        
    #     result_df = result_df.rename(columns={'FINAL YEAR': 'YEAR'})   
    
    #     # Display the results
    #     st.markdown("### **Venuewise Performance**")
    #     cols = result_df.columns.tolist()
    
    #     # Specify the desired order with 'venue' first
    #     new_order = ['VENUE'] + [col for col in cols if col != 'VENUE']
        
                      
    #     # Reindex the DataFrame with the new column order
    #     result_df = result_df[new_order]
    #     result_df=result_df.sort_values('YEAR',ascending=True)
    #     result_df=result_df[['VENUE'] + ['YEAR'] + [col for col in result_df.columns if col not in ['VENUE','YEAR']]]
    #     st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
        
    # else:
    #     # Assuming pdf is your main DataFrame
    #     # Filter for innings 1 and 2 and prepare to accumulate results
    #     innings = [1, 2]
    #     result_df = pd.DataFrame()  # Initialize an empty DataFrame for results
        
    #     for inning in innings:
    #         # Filter for the specific inning
    #         tdf = pdf[(pdf['batsman'] == batter_name) & (pdf['bowler'] == bowler_name) & (pdf['inning'] == inning)]
            
    #         # Check if there's any data for the current inning
    #         if not tdf.empty:
    #             # Call the cumulator function
    #             temp_df = cumulator(tdf)
        
    #             # Add the inning as the first column in temp_df
    #             temp_df.insert(0, 'INNING', inning)
        
    #             # Concatenate to the main result DataFrame
    #             result_df = pd.concat([result_df, temp_df], ignore_index=True)
        
    #     # After processing both innings, drop unnecessary columns if needed
    #     columns_to_drop = ['batsman', 'bowler', 'batting_team', 'debut_year', 'matches_x', 'matches_y', 'fifties', 'hundreds', 'thirties', 'highest_score', 'matches','last_year']
    #     result_df = result_df.drop(columns=columns_to_drop, errors='ignore')
        
    #     # Convert specific columns to integers and fill NaN values
    #     columns_to_convert = ['runs', 'dismissals']
    #     for col in columns_to_convert:
    #         result_df[col] = result_df[col].fillna(0).astype(int)
        
    #     result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
        
    #     # Display the results
    #     st.markdown("### **Innings Performance**")
    #     result_df=result_df[['INNING'] + [col for col in result_df.columns if col not in ['INNING']]]
    #     st.table(result_df.style.set_table_attributes("style='fsont-weight: bold;'"))
      
elif sidebar_option == "Strength vs Weakness":
    st.header("Strength and Weakness Analysis")
    player_name = st.selectbox("Search for a player", idf['batsman'].unique())
    
    # Dropdown for Batting or Bowling selection
    option = st.selectbox("Select Role", ("Batting", "Bowling"))
    
    if option == "Batting":
        # st.subheader("Batsman vs Bowling Style Analysis")
          allowed_bowling_styles = {
          'pace': [
              'Right-arm medium fast', 'Right arm medium fast', 
              'Right-arm fast', 'Right-arm fast-medium', 
              'Left-arm medium'
                  ],
          'spin': [
              'Right-arm off-break', 'Right-arm off-break and Legbreak', 
              'Right-arm leg-spin', 'Slow left-arm orthodox', 
              'Left-arm wrist spin'
                  ]
                  }
      
        # Add 'bowl_kind' column in pdf
          def add_bowl_kind(pdf):
              pdf['bowl_kind'] = pdf['bowling_style'].apply(
                  lambda x: 'pace' if x in allowed_bowling_styles['pace'] else 'spin' if x in allowed_bowling_styles['spin'] else 'unknown'
              )
              return pdf
          
          # Apply the function to add the 'bowl_kind' column
          pdf = add_bowl_kind(pdf)
          
          result_df = pd.DataFrame()
          i = 0
          
          # Loop over pace and spin bowling types
          for bowl_kind in ['pace', 'spin']:
              temp_df = pdf[pdf['batsman'] == player_name]  # Filter data for the selected batsman
              
              # Filter for the specific 'bowl_kind'
              temp_df = temp_df[temp_df['bowl_kind'] == bowl_kind]
              
              # Apply the cumulative function (bcum)
              temp_df = cumulator(temp_df)
              
              # If the DataFrame is empty after applying `bcum`, skip this iteration
              if temp_df.empty:
                  continue
              
              # Add the bowl_kind column
              temp_df['bowl_kind'] = bowl_kind
              
              # Reorder columns to make 'bowl_kind' the first column
              cols = temp_df.columns.tolist()
              new_order = ['bowl_kind'] + [col for col in cols if col != 'bowl_kind']
              temp_df = temp_df[new_order]
              
              # Concatenate results into result_df
              if i == 0:
                  result_df = temp_df
                  i += 1
              else:
                  result_df = pd.concat([result_df, temp_df], ignore_index=True)
          
          # Display the final result_df
          result_df = result_df.drop(columns=['matches_x', 'matches_y', 'batsman', 'debut_year', 'final_year','hundreds','fifties','thirties','highest_score','batting_team','matches'])
          result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
          columns_to_convert = ['RUNS']
          
          # Fill NaN values with 0
          # result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
          
          # Convert the specified columns to integer type
          # result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
          result_df = round_up_floats(result_df)
          
          # Specify the desired order with 'bowl_kind' first
          cols = result_df.columns.tolist()
          # new_order = ['BOWL KIND', 'INNINGS'] + [col for col in cols if col not in ['BOWL KIND', 'INNINGS']]
          
          # Reindex the DataFrame with the new column order
          # result_df = result_df[new_order]
          result_df['BOWL KIND'] = result_df['BOWL KIND'].str.capitalize()
          st.markdown("### Performance Against Bowling Types (Pace vs Spin)")
          st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
          
          # Set thresholds for strengths and weaknesses for Women's T20Is
          strength_thresholds = {
              'SR': 125,               # Threshold for Strike Rate
              'AVG': 30,               # Threshold for Average
              'DOT PERCENTAGE': 25,    # Threshold for Dot Percentage
              'BPB': 5,                # Threshold for Boundary Percentage Batsman
              'BPD': 20                # Threshold for Boundary Percentage Delivery
          }
          
          weakness_thresholds = {
              'SR': 90,                # Threshold for Strike Rate
              'AVG': 15,               # Threshold for Average
              'DOT PERCENTAGE': 40,    # Threshold for Dot Percentage
              'BPB': 7,                # Threshold for Boundary Percentage Batsman
              'BPD': 15                # Threshold for Boundary Percentage Delivery
          }
          
          # Initialize lists to hold strengths and weaknesses
          strong_against = []
          weak_against = []
          
          # Check each bowling kind's stats against the thresholds
          for index, row in result_df.iterrows():
              strong_count = 0
              weak_count = 0
              if row['INNINGS'] >= 3:
                  # Evaluate strengths
                  if row['SR'] >= strength_thresholds['SR']:
                      strong_count += 1
                  if row['AVG'] >= strength_thresholds['AVG']:
                      strong_count += 1
                  if row['DOT PERCENTAGE'] <= strength_thresholds['DOT PERCENTAGE']:
                      strong_count += 1
                  if row['BPB'] <= strength_thresholds['BPB']:
                      strong_count += 1
                  if row['BPD'] >= strength_thresholds['BPD']:
                      strong_count += 1
                  
                  # Evaluate weaknesses
                  if row['SR'] <= weakness_thresholds['SR']:
                      weak_count += 1
                  if row['AVG'] <= weakness_thresholds['AVG']:
                      weak_count += 1
                  if row['DOT PERCENTAGE'] >= weakness_thresholds['DOT PERCENTAGE']:
                      weak_count += 1
                  if row['BPB'] >= weakness_thresholds['BPB']:
                      weak_count += 1
                  if row['BPD'] <= weakness_thresholds['BPD']:
                      weak_count += 1
                  
                  # Determine strong/weak based on counts
                  if strong_count >= 3:
                      strong_against.append(row['BOWL KIND'])
                  if weak_count >= 3:
                      weak_against.append(row['BOWL KIND'])
                  
                  # Format the output message
                  if strong_against:
                        strong_message = f"{player_name} is strong against: {', '.join(strong_against)}."
                  else:
                        strong_message = f"{player_name} has no clear strengths against any bowling type."
                      
                  if weak_against:
                        weak_message = f"{player_name} is weak against: {', '.join(weak_against)}."
                  else:
                        weak_message = f"{player_name} has no clear weaknesses against any bowling type."
          
              else:
                  continue
          
          # Display strengths and weaknesses messages
          st.markdown("##### Strengths and Weaknesses Against Bowling Types")
          st.write(strong_message)
          st.write(weak_message)

        
          allowed_bowling_styles = [
              'Right-arm medium fast', 'Right arm medium fast', 
              'Right-arm off-break', 'Right-arm fast', 
              'Right-arm fast-medium', 'Right-arm off-break and Legbreak',
              'Right-arm leg-spin', 'Left-arm medium',
              'Slow left-arm orthodox', 'Left-arm wrist spin'
              ]
              
          result_df = pd.DataFrame()
          i = 0
              
          for bowling_style in allowed_bowling_styles:
              temp_df = pdf[pdf['batsman'] == player_name]  # Filter data for the selected batsman
              
              # Filter for the specific bowling style
              temp_df = temp_df[temp_df['bowling_style'] == bowling_style]
              
              # Apply the cumulative function (bcum)
              temp_df = cumulator(temp_df)
              
              # If the DataFrame is empty after applying `bcum`, skip this iteration
              if temp_df.empty:
                  continue
              
              # Add the bowling style column
              temp_df['bowling_style'] = bowling_style
              
              # Reorder columns to make 'bowling_style' the first column
              cols = temp_df.columns.tolist()
              new_order = ['bowling_style'] + [col for col in cols if col != 'bowling_style']
              temp_df = temp_df[new_order]
              
              # Concatenate results into result_df
              if i == 0:
                  result_df = temp_df
                  i += 1
              else:
                  result_df = pd.concat([result_df, temp_df], ignore_index=True)
          
          # Display the final result_df
          result_df = result_df.drop(columns=['matches_x', 'matches_y', 'batsman', 'debut_year', 'final_year','hundreds','fifties','thirties','highest_score','batting_team','matches'])
          result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
          columns_to_convert = ['RUNS']
  
          # Fill NaN values with 0
          result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
  
          # Convert the specified columns to integer type
          result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
          result_df = round_up_floats(result_df)
          cols = result_df.columns.tolist()
  
          # Specify the desired order with 'bowling_style' first
          new_order = ['BOWLING STYLE', 'INNINGS'] + [col for col in cols if col not in ['BOWLING STYLE','INNINGS',]]
  
          # Reindex the DataFrame with the new column order
          result_df = result_df[new_order]
  
          st.markdown("### Performance Against Bowling Styles")
          st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
          
          strong_against = []
          weak_against = []
          
          # Check each bowling style's stats against the thresholds
          for index, row in result_df.iterrows():
              strong_count = 0
              weak_count = 0
              if row['INNINGS']>=3:
                  # Evaluate strengths
                  if row['SR'] >= strength_thresholds['SR']:
                      strong_count += 1
                  if row['AVG'] >= strength_thresholds['AVG']:
                      strong_count += 1
                  if row['DOT PERCENTAGE'] <= strength_thresholds['DOT PERCENTAGE']:
                      strong_count += 1
                  if row['BPB'] <= strength_thresholds['BPB']:
                      strong_count += 1
                  if row['BPD'] >= strength_thresholds['BPD']:
                      strong_count += 1
              
                  # Evaluate weaknesses
                  if row['SR'] <= weakness_thresholds['SR']:
                      weak_count += 1
                  if row['AVG'] <= weakness_thresholds['AVG']:
                      weak_count += 1
                  if row['DOT PERCENTAGE'] >= weakness_thresholds['DOT PERCENTAGE']:
                      weak_count += 1
                  if row['BPB'] >= weakness_thresholds['BPB']:
                      weak_count += 1
                  if row['BPD'] <= weakness_thresholds['BPD']:
                      weak_count += 1
              
                  # Determine strong/weak based on counts
                  if strong_count >= 3:
                      strong_against.append(row['BOWLING STYLE'])
                  if weak_count >= 3:
                      weak_against.append(row['BOWLING STYLE'])
                  
                  # Format the output message
                  if strong_against:
                        strong_message = f"{player_name} is strong against: {', '.join(strong_against)}."
                  else:
                        strong_message = f"{player_name} has no clear strengths against any bowling style."
                      
                  if weak_against:
                        weak_message = f"{player_name} is weak against: {', '.join(weak_against)}."
                  else:
                        weak_message = f"{player_name} has no clear weaknesses against any bowling style."
  
        
              else:
                  continue
          # Display strengths and weaknesses messages
          st.markdown("##### Strengths and Weaknesses")
          st.write(strong_message)
          st.write(weak_message)

          
          # Streamlit header
          # st.header("Phase-wise Strength and Weakness Analysis")
          strength_thresholds_pp = {
              'SR': 135,               # Threshold for Strike Rate
              'AVG': 20,               # Threshold for Average
              'DOT PERCENTAGE': 25,    # Threshold for Dot Percentage
              'BPB': 4,                # Threshold for Boundary Percentage Batsman
              'BPD': 18                # Threshold for Boundary Percentage Delivery
                                }
          
          weakness_thresholds_pp = {
              'SR': 120,                # Threshold for Strike Rate
              'AVG': 10,               # Threshold for Average
              'DOT PERCENTAGE': 30,    # Threshold for Dot Percentage
              'BPB': 7,                # Threshold for Boundary Percentage Batsman
              'BPD': 15                # Threshold for Boundary Percentage Delivery
                                }
          strength_thresholds_m = {
              'SR': 120,               # Threshold for Strike Rate
              'AVG': 30,               # Threshold for Average
              'DOT PERCENTAGE': 32,    # Threshold for Dot Percentage
              'BPB': 6,                # Threshold for Boundary Percentage Batsman
              'BPD': 23                # Threshold for Boundary Percentage Delivery
                                }
          
          weakness_thresholds_m = {
              'SR': 110,                # Threshold for Strike Rate
              'AVG': 25,               # Threshold for Average
              'DOT PERCENTAGE': 40,    # Threshold for Dot Percentage
              'BPB': 7,                # Threshold for Boundary Percentage Batsman
              'BPD': 18                # Threshold for Boundary Percentage Delivery
                                }
          strength_thresholds_d = {
              'SR': 145,               # Threshold for Strike Rate
              'AVG': 20,               # Threshold for Average
              'DOT PERCENTAGE': 25,    # Threshold for Dot Percentage
              'BPB': 4,                # Threshold for Boundary Percentage Batsman
              'BPD': 15                # Threshold for Boundary Percentage Delivery
                                }
          
          weakness_thresholds_d = {
              'SR': 130,                # Threshold for Strike Rate
              'AVG': 10,               # Threshold for Average
              'DOT PERCENTAGE': 32,    # Threshold for Dot Percentage
              'BPB': 6,                # Threshold for Boundary Percentage Batsman
              'BPD': 10                # Threshold for Boundary Percentage Delivery
                                }
          
          # DataFrame to hold results
          result_df = pd.DataFrame()
          i = 0
          
          # Phases to analyze
          phases = ['Powerplay', 'Middle', 'Death']
          
          for phase in phases:
              temp_df = pdf[pdf['batsman'] == player_name]  # Filter data for the selected batsman
              
              # Filter for the specific phase
              temp_df = temp_df[temp_df['phase'] == phase]
              
              # Apply the cumulative function (assuming `cumulator` is defined)
              temp_df = cumulator(temp_df)
              
              # If the DataFrame is empty after applying `cumulator`, skip this iteration
              if temp_df.empty:
                  continue
              
              # Add the phase column
              temp_df['phase'] = phase
              
              # Reorder columns to make 'phase' the first column
              cols = temp_df.columns.tolist()
              new_order = ['phase'] + [col for col in cols if col != 'phase']
              temp_df = temp_df[new_order]
              
              # Concatenate results into result_df
              if i == 0:
                  result_df = temp_df
                  i += 1
              else:
                  result_df = pd.concat([result_df, temp_df], ignore_index=True)
          
          # Display the final result_df
          result_df = result_df.drop(columns=['matches_x', 'matches_y', 'batsman', 'debut_year', 'final_year','hundreds','fifties','thirties','highest_score','batting_team','matches'])
          result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
          columns_to_convert = ['RUNS']
          
          # Fill NaN values with 0
          result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0)
          
          # Convert the specified columns to integer type
          result_df[columns_to_convert] = result_df[columns_to_convert].astype(int)
          result_df = round_up_floats(result_df)
          cols = result_df.columns.tolist()
          
          # Specify the desired order with 'phase' first
          new_order = ['PHASE', 'INNINGS'] + [col for col in cols if col not in ['PHASE','INNINGS']]
          result_df = result_df[new_order]
          
          st.markdown("### Performance in Different Phases")
          st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
          
          
          strong_against = []
          weak_against = []
          
          # Check each phase's stats against the thresholds
          for index, row in result_df.iterrows():
              strong_count = 0
              weak_count = 0
              if row['PHASE']=='Powerplay':
                  if row['INNINGS'] >= 3:
                      # Evaluate strengths
                      if row['SR'] >= strength_thresholds_pp['SR']:
                          strong_count += 1
                      if row['AVG'] >= strength_thresholds_pp['AVG']:
                          strong_count += 1
                      if row['DOT PERCENTAGE'] <= strength_thresholds_pp['DOT PERCENTAGE']:
                          strong_count += 1
                      if row['BPB'] <= strength_thresholds_pp['BPB']:
                          strong_count += 1
                      if row['BPD'] >= strength_thresholds_pp['BPD']:
                          strong_count += 1
                      
                      # Evaluate weaknesses
                      if row['SR'] <= weakness_thresholds_pp['SR']:
                          weak_count += 1
                      if row['AVG'] <= weakness_thresholds_pp['AVG']:
                          weak_count += 1
                      if row['DOT PERCENTAGE'] >= weakness_thresholds_pp['DOT PERCENTAGE']:
                          weak_count += 1
                      if row['BPB'] >= weakness_thresholds_pp['BPB']:
                          weak_count += 1
                      if row['BPD'] <= weakness_thresholds_pp['BPD']:
                          weak_count += 1
                      
                      # Determine strong/weak based on counts
                      if strong_count >= 3:
                          strong_against.append(row['PHASE'])
                      if weak_count >= 3:
                          weak_against.append(row['PHASE'])
                                              
              if row['PHASE']=='Middle':
                  if row['INNINGS'] >= 3:
                      # Evaluate strengths
                      if row['SR'] >= strength_thresholds_m['SR']:
                          strong_count += 1
                      if row['AVG'] >= strength_thresholds_m['AVG']:
                          strong_count += 1
                      if row['DOT PERCENTAGE'] <= strength_thresholds_m['DOT PERCENTAGE']:
                          strong_count += 1
                      if row['BPB'] <= strength_thresholds_m['BPB']:
                          strong_count += 1
                      if row['BPD'] >= strength_thresholds_m['BPD']:
                          strong_count += 1
                      
                      # Evaluate weaknesses
                      if row['SR'] <= weakness_thresholds_m['SR']:
                          weak_count += 1
                      if row['AVG'] <= weakness_thresholds_m['AVG']:
                          weak_count += 1
                      if row['DOT PERCENTAGE'] >= weakness_thresholds_m['DOT PERCENTAGE']:
                          weak_count += 1
                      if row['BPB'] >= weakness_thresholds_m['BPB']:
                          weak_count += 1
                      if row['BPD'] <= weakness_thresholds_m['BPD']:
                          weak_count += 1
                      
                      # Determine strong/weak based on counts
                      if strong_count >= 3:
                          strong_against.append(row['PHASE'])
                      if weak_count >= 3:
                          weak_against.append(row['PHASE'])
              if row['PHASE']=='Death':
                  if row['INNINGS'] >= 3:
                      # Evaluate strengths
                      if row['SR'] >= strength_thresholds_d['SR']:
                          strong_count += 1
                      if row['AVG'] >= strength_thresholds_d['AVG']:
                          strong_count += 1
                      if row['DOT PERCENTAGE'] <= strength_thresholds_d['DOT PERCENTAGE']:
                          strong_count += 1
                      if row['BPB'] <= strength_thresholds_d['BPB']:
                          strong_count += 1
                      if row['BPD'] >= strength_thresholds_d['BPD']:
                          strong_count += 1
                      
                      # Evaluate weaknesses
                      if row['SR'] <= weakness_thresholds_d['SR']:
                          weak_count += 1
                      if row['AVG'] <= weakness_thresholds_d['AVG']:
                          weak_count += 1
                      if row['DOT PERCENTAGE'] >=weakness_thresholds_d['DOT PERCENTAGE']:
                          weak_count += 1
                      if row['BPB'] >= weakness_thresholds_d['BPB']:
                          weak_count += 1
                      if row['BPD'] <= weakness_thresholds_d['BPD']:
                          weak_count += 1
                      
                      # Determine strong/weak based on counts
                      if strong_count >= 3:
                          strong_against.append(row['PHASE'])
                      if weak_count >= 3:
                          weak_against.append(row['PHASE'])      
    
          # Format the output message
          strong_message = f"{player_name} is strong in: {', '.join(strong_against) if strong_against else 'no clear strengths in any phase.'}."
          weak_message = f"{player_name} is weak in: {', '.join(weak_against) if weak_against else 'no clear weaknesses in any phase.'}."
          
          # Display strengths and weaknesses messages
          st.markdown("##### Strengths and Weaknesses")
          st.write(strong_message)
          st.write(weak_message)
          player_data = pdf[pdf['batsman'] == player_name]
          
          # Group by dismissal_kind and count the number of dismissals
          dismissal_counts = player_data.groupby('dismissal_kind').size().reset_index(name='count')
          
          # Sort the dismissal kinds by count
          dismissal_counts = dismissal_counts.sort_values(by='count', ascending=True)
          dismissal_counts['dismissal_kind'] = dismissal_counts['dismissal_kind'].str.upper()
          plt.figure(figsize=(10, 6))
          plt.barh(dismissal_counts['dismissal_kind'], dismissal_counts['count'], color='skyblue')
          plt.xlabel('Number of Dismissals', fontsize=14)
          plt.ylabel('Dismissal Type', fontsize=14)
          plt.title(f'Number of Dismissals by Dismissal Type for {player_name}',fontsize=18)
          plt.grid(axis='x', linestyle='--', alpha=0.7)
          plt.tight_layout()
          
          # Display the plot in Streamlit
          st.pyplot(plt)
          import pandas as pd
          import matplotlib.pyplot as plt
            
            # Copy the original dataset to a new DataFrame
          df_ball_wise = pdf.copy()
          df_ball_wise = df_ball_wise[df_ball_wise['batsman']==player_name] 
            
            # Step 1: Filter for valid balls (valid_ball == 1)
          df_ball_wise = df_ball_wise[df_ball_wise['valid_ball'] == 1]
            
            # Step 2: Define ball ranges
          def ball_range(ball_count):
              if ball_count <= 10:
                  return '0-10'
              elif ball_count <= 20:
                  return '11-20'
              elif ball_count <= 30:
                  return '21-30'
              elif ball_count <= 40:
                  return '31-40'
              else:
                  return '>40'
            
            # Step 3: Initialize an empty dictionary to store SR for each range
          range_sr_dict = {'0-10': [], '11-20': [], '21-30': [], '31-40': [], '>40': []}
          
          # Step 4: Loop through each match_id
          for match_id in df_ball_wise['match_id'].unique():
              # Filter data for the current match_id
              match_data = df_ball_wise[df_ball_wise['match_id'] == match_id]
              
                # Step 5: Create ball_count column for the current match
              match_data['ball_count'] = match_data.groupby(['batsman']).cumcount() + 1
                
                # Step 6: Apply ball range categorization
              match_data['ball_range'] = match_data['ball_count'].apply(ball_range)
                
                # Step 7: Calculate SR for each ball range within the current match
              sr_by_range = match_data.groupby('ball_range').agg({'batsman_runs': 'sum', 'ball_count': 'count'}).reset_index()
              sr_by_range['strike_rate'] = (sr_by_range['batsman_runs'] / sr_by_range['ball_count']) * 100

                
                # Step 8: Store the SR in the range_sr_dict for each range
              for idx, row in sr_by_range.iterrows():
                  range_sr_dict[row['ball_range']].append(row['strike_rate'])
            
            # Step 9: Calculate the mean SR for each range across all matches
          mean_sr_by_range = {range_: (sum(sr_list) / len(sr_list)) if sr_list else 0 for range_, sr_list in range_sr_dict.items()}
            
            # Step 10: Convert the dictionary to a DataFrame for plotting
          sr_df = pd.DataFrame(list(mean_sr_by_range.items()), columns=['ball_range', 'avg_strike_rate'])
            
            # Step 11: Plot the bar graph
          plt.figure(figsize=(8,6))
          plt.bar(sr_df['ball_range'], sr_df['avg_strike_rate'], color='lightpink')
            
            # Customize the plot
          plt.title('Ball-wise Average Strike Rate Across Matches', fontsize=14)
          plt.xlabel('Ball Range', fontsize=12)
          plt.ylabel('Average Strike Rate (SR)', fontsize=12)
          plt.grid(True, axis='y', linestyle='--', alpha=0.6)
            
            # Show the plot
          st.pyplot(plt)

      
    if option == "Bowling":
        # st.subheader("Bowler vs Batting Style Analysis")
        allowed_batting_styles = ['Left-hand bat', 'Right-hand bat']  # Define the two batting styles
        result_df = pd.DataFrame()
        temp_df = pdf[pdf['bowler'] == player_name]
        if temp_df.empty :
            st.markdown('Bowling stats do not exist')
        else:
            # Loop over left-hand and right-hand batting styles
            for bat_style in allowed_batting_styles:
                temp_df = pdf[pdf['bowler'] == player_name]  # Filter data for the selected bowler
                
                # Filter for the specific batting style
                temp_df = temp_df[temp_df['batting_style'] == bat_style]
                
                # Apply the cumulative function (bcum) for bowling
                temp_df = bcum(temp_df)
                
                # If the DataFrame is empty after applying bcum, skip this iteration
                if temp_df.empty:
                    continue
                
                # Add the batting style as a column for later distinction
                temp_df['batting_style'] = bat_style
                
                # Concatenate results into result_df
                result_df = pd.concat([result_df, temp_df], ignore_index=True)
        
            # Drop unwanted columns from the result DataFrame
            result_df = result_df.drop(columns=['bowler', 'debut_year', 'final_year'])
        
            # Standardize column names
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            
            # Convert the relevant columns to integers and fill NaN values
            columns_to_convert = ['WKTS']
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0).astype(int)
            result_df = round_up_floats(result_df)
            cols = result_df.columns.tolist()
              
              # Specify the desired order with 'phase' first
            new_order = ['BATTING STYLE'] + [col for col in cols if col not in 'BATTING STYLE']
            result_df = result_df[new_order]
        
            # Display the final table
            st.markdown("### Cumulative Bowling Performance Against Batting Styles")
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
        
            # Set thresholds for strengths and weaknesses for Women's T20Is (Bowling performance)
            strength_thresholds = {
                'SR': 20,               # Strike Rate (balls per wicket)
                'AVG': 16.5,              # Average (runs per wicket)
                'DOT%': 45,   # Dot ball percentage
                'Econ': 6, 
            }
        
            weakness_thresholds = {
                'SR': 30,               # Strike Rate (balls per wicket)
                'AVG': 26,              # Average (runs per wicket)
                'DOT%': 38,   # Dot ball percentage
                'Econ':8,
            }
        
            # Initialize lists to hold strengths and weaknesses
            strong_against = []
            weak_against = []
        
            # Check each batting style's stats against the thresholds
            for index, row in result_df.iterrows():
                strong_count = 0
                weak_count = 0
                if row['INNINGS'] >= 3:
                    # Evaluate strengths
                    if row['SR'] <= strength_thresholds['SR']:
                        strong_count += 1
                    if row['AVG'] <= strength_thresholds['AVG']:
                        strong_count += 1
                    if row['DOT%'] >= strength_thresholds['DOT%']:
                        strong_count += 1
                    if row['ECON'] <= strength_thresholds['Econ']:
                        strong_count += 1
                   
                    
                    # Evaluate weaknesses
                    if row['SR'] >= weakness_thresholds['SR']:
                        weak_count += 1
                    if row['AVG'] >= weakness_thresholds['AVG']:
                        weak_count += 1
                    if row['DOT%'] <= weakness_thresholds['DOT%']:
                        weak_count += 1
                    if row['ECON'] >= strength_thresholds['Econ']:
                        weak_count += 1
                    
                    # Determine strong/weak based on counts
                    if strong_count >= 3:
                        strong_against.append(row['BATTING STYLE'])
                    if weak_count >= 3:
                        weak_against.append(row['BATTING STYLE'])
                    
            # Format the output message
            strong_message = f"{player_name} is strong against: {', '.join(strong_against)}." if strong_against else f"{player_name} has no clear strengths against any batting style."
            weak_message = f"{player_name} is weak against: {', '.join(weak_against)}." if weak_against else f"{player_name} has no clear weaknesses against any batting style."
        
            # Display strengths and weaknesses messages
            st.markdown("##### Strengths and Weaknesses Against Batting Styles")
            st.write(strong_message)
            st.write(weak_message)
    
            # Define the match phases
            allowed_phases = ['Powerplay', 'Middle', 'Death']  # Define the three phases
            strength_thresholds_pp = {
                'SR': 14,               # Strike Rate (balls per wicket)
                'AVG': 14.5,              # Average (runs per wicket)
                'DOT%': 35,   # Dot ball percentage
                'Econ': 7, 
            }
        
            weakness_thresholds_pp= {
                'SR': 28,               # Strike Rate (balls per wicket)
                'AVG': 24,              # Average (runs per wicket)
                'DOT%': 25,   # Dot ball percentage
                'Econ':8,
            }
            strength_thresholds_m = {
                'SR': 23,               # Strike Rate (balls per wicket)
                'AVG': 16.5,              # Average (runs per wicket)
                'DOT%': 45,   # Dot ball percentage
                'Econ': 6.3, 
            }
        
            weakness_thresholds_m = {
                'SR': 33,               # Strike Rate (balls per wicket)
                'AVG': 26,              # Average (runs per wicket)
                'DOT%': 38,   # Dot ball percentage
                'Econ':7.5,
            }
            strength_thresholds_d = {
                'SR': 22,               # Strike Rate (balls per wicket)
                'AVG': 20.5,              # Average (runs per wicket)
                'DOT%': 38,   # Dot ball percentage
                'Econ': 7.8, 
            }
        
            weakness_thresholds_d = {
                'SR': 30,               # Strike Rate (balls per wicket)
                'AVG': 26,              # Average (runs per wicket)
                'DOT%': 30 ,   # Dot ball percentage
                'Econ':8.5,
            }
            
            result_df = pd.DataFrame()
            
            # Loop over each phase
            for phase in allowed_phases:
                temp_df = pdf[pdf['bowler'] == player_name]  # Filter data for the selected bowler
                
                # Filter for the specific phase
                temp_df = temp_df[temp_df['phase'] == phase]
                
                # Apply the cumulative function (bcum) for bowling
                temp_df = bcum(temp_df)
                
                # If the DataFrame is empty after applying bcum, skip this iteration
                if temp_df.empty:
                    continue
                
                # Add the phase as a column for later distinction
                temp_df['phase'] = phase
                
                # Concatenate results into result_df
                result_df = pd.concat([result_df, temp_df], ignore_index=True)
            
            # Drop unwanted columns from the result DataFrame
            result_df = result_df.drop(columns=['bowler', 'debut_year', 'final_year'])
            
            # Standardize column names
            result_df.columns = [col.upper().replace('_', ' ') for col in result_df.columns]
            
            # Convert the relevant columns to integers and fill NaN values
            columns_to_convert = ['WKTS']
            result_df[columns_to_convert] = result_df[columns_to_convert].fillna(0).astype(int)
            result_df = round_up_floats(result_df)
            
            # Specify the desired column order with 'PHASE' first
            cols = result_df.columns.tolist()
            new_order = ['PHASE'] + [col for col in cols if col not in 'PHASE']
            result_df = result_df[new_order]
            
            # Display the final table
            st.markdown("### Cumulative Bowling Performance Across Phases")
            st.table(result_df.style.set_table_attributes("style='font-weight: bold;'"))
           
            strong_against = []
            weak_against = []
            
            # Check each phase's stats against the thresholds
            for index, row in result_df.iterrows():
                strong_count = 0
                weak_count = 0
                if row['PHASE']=='Powerplay':
                    if row['INNINGS'] >= 3:
                        # Evaluate strengths
                        if row['SR'] <= strength_thresholds_pp['SR']:
                            strong_count += 1
                        if row['AVG'] <= strength_thresholds_pp['AVG']:
                            strong_count += 1
                        if row['DOT%'] >= strength_thresholds_pp['DOT%']:
                            strong_count += 1
                        if row['ECON'] <= strength_thresholds_pp['Econ']:
                            strong_count += 1
                
                        # Evaluate weaknesses
                        if row['SR'] >= weakness_thresholds_pp['SR']:
                            weak_count += 1
                        if row['AVG'] >= weakness_thresholds_pp['AVG']:
                            weak_count += 1
                        if row['DOT%'] <= weakness_thresholds_pp['DOT%']:
                            weak_count += 1
                        if row['ECON'] >= weakness_thresholds_pp['Econ']:
                            weak_count += 1
                
                        # Determine strong/weak based on counts
                        if strong_count >= 3:
                            strong_against.append(row['PHASE'])
                        if weak_count >= 3:
                            weak_against.append(row['PHASE'])
                if row['PHASE']=='Middle':
                    if row['INNINGS'] >= 3:
                        # Evaluate strengths
                        if row['SR'] <= strength_thresholds_m['SR']:
                            strong_count += 1
                        if row['AVG'] <= strength_thresholds_m['AVG']:
                            strong_count += 1
                        if row['DOT%'] >= strength_thresholds_m['DOT%']:
                            strong_count += 1
                        if row['ECON'] <= strength_thresholds_m['Econ']:
                            strong_count += 1
                
                        # Evaluate weaknesses
                        if row['SR'] >= weakness_thresholds_m['SR']:
                            weak_count += 1
                        if row['AVG'] >= weakness_thresholds_m['AVG']:
                            weak_count += 1
                        if row['DOT%'] <= weakness_thresholds_m['DOT%']:
                            weak_count += 1
                        if row['ECON'] >=weakness_thresholds_m['Econ']:
                            weak_count += 1
                
                        # Determine strong/weak based on counts
                        if strong_count >= 3:
                            strong_against.append(row['PHASE'])
                        if weak_count >= 3:
                            weak_against.append(row['PHASE'])
                if row['PHASE']=='Death':
                    if row['INNINGS'] >= 3:
                        # Evaluate strengths
                        if row['SR'] <= strength_thresholds_d['SR']:
                            strong_count += 1
                        if row['AVG'] <= strength_thresholds_d['AVG']:
                            strong_count += 1
                        if row['DOT%'] >= strength_thresholds_d['DOT%']:
                            strong_count += 1
                        if row['ECON'] <= strength_thresholds_d['Econ']:
                            strong_count += 1
                
                        # Evaluate weaknesses
                        if row['SR'] >= weakness_thresholds_d['SR']:
                            weak_count += 1
                        if row['AVG'] >= weakness_thresholds_d['AVG']:
                            weak_count += 1
                        if row['DOT%'] <= weakness_thresholds_d['DOT%']:
                            weak_count += 1
                        if row['ECON'] >=weakness_thresholds_d['Econ']:
                            weak_count += 1
                
                        # Determine strong/weak based on counts
                        if strong_count >= 3:
                            strong_against.append(row['PHASE'])
                        if weak_count >= 3:
                            weak_against.append(row['PHASE'])
                
            
            # Format the output message
            strong_message = f"{player_name} is strong during: {', '.join(strong_against)}." if strong_against else f"{player_name} has no clear strengths in any phase."
            weak_message = f"{player_name} is weak during: {', '.join(weak_against)}." if weak_against else f"{player_name} has no clear weaknesses in any phase."
            
            # Display strengths and weaknesses messages
            st.markdown("##### Strengths and Weaknesses Across Phases")
            st.write(strong_message)
            st.write(weak_message)
    
            # Filter for the selected bowler's data
            bowler_data = pdf[pdf['bowler'] == player_name]
            
            # Filter only the rows where the bowler has taken a wicket
            bowler_wickets = bowler_data[bowler_data['bowler_wkt'] == 1]
            
            # Group by dismissal_kind and count the number of dismissals
            bowler_dismissal_counts = bowler_wickets.groupby('dismissal_kind').size().reset_index(name='count')
            
            # Sort the dismissal kinds by count
            bowler_dismissal_counts = bowler_dismissal_counts.sort_values(by='count', ascending=True)
            bowler_dismissal_counts['dismissal_kind'] = bowler_dismissal_counts['dismissal_kind'].str.upper()
            
            # Plotting the horizontal bar chart for bowler's wickets by dismissal kind
            plt.figure(figsize=(10, 6))
            plt.barh(bowler_dismissal_counts['dismissal_kind'], bowler_dismissal_counts['count'], color='lightgreen')
            plt.xlabel('Number of Wickets',fontsize=14)
            plt.ylabel('Dismissal Type',fontsize=14)
            plt.title(f'Number of Wickets by Dismissal Type for {player_name}',fontsize=18)
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            plt.tight_layout()
            st.pyplot(plt)

else :
    st.header("ICC WT20I 2024")
    df=pdfn
    df['wagonZone'] = df['wagonZone'].str.extract('(\d+)')
    
    # Replace NaN with -1 and convert the column to integers
    df['wagonZone'] = df['wagonZone'].fillna(-1).astype(int)
    temp_df=df
    
    st.sidebar.title("Match by Match Analysis")
    # Main section - Career Stat Type selection
    option = st.selectbox("Select Analysis Dimension", ("Batsman Analysis", "Bowler Analysis"))
    batsman_selected = st.selectbox("Select Batsman", options=temp_df["batsman"].unique())
    if option == 'Batsman Analysis':

        # Filter the data for the selected batsman
        final_df = temp_df[temp_df["batsman"] == batsman_selected]
        fdf=final_df
        # Calculate statistics
        total_runs = final_df["batsman_runs"].sum()
        total_balls = final_df['valid_ball'].sum()
        total_dismissals = final_df["is_wkt"].sum()
        strike_rate = (total_runs / total_balls) * 100 if total_balls > 0 else 0
        avg_runs = total_runs / total_dismissals if total_dismissals > 0 else inf
    
        # Count for each scoring shot type
        total_zeros = final_df["is_dot"].sum()
        total_ones = final_df["is_one"].sum()
        total_twos = final_df["is_two"].sum()
        total_threes = final_df["is_three"].sum()
        total_fours = final_df["is_four"].sum()
        total_sixes = final_df["is_six"].sum()
    
        # Calculate percentages
        total_balls_for_percentage = total_zeros + total_ones + total_twos + total_threes + total_fours + total_sixes
        
        def calc_percentage(value, total):
            return f"{(value / total * 100):.1f}%" if total > 0 else "0%"
        percent_zeros = (total_zeros / total_balls) * 100 if total_balls > 0 else 0
        percent_ones = (total_ones / total_balls) * 100 if total_balls > 0 else 0
        percent_twos = (total_twos / total_balls) * 100 if total_balls > 0 else 0
        percent_threes = (total_threes / total_balls) * 100 if total_balls > 0 else 0
        percent_fours = (total_fours / total_balls) * 100 if total_balls > 0 else 0
        percent_sixes = (total_sixes / total_balls) * 100 if total_balls > 0 else 0
        final_df = final_df[final_df['shot_type'].apply(lambda x: isinstance(x, str))]

        boundary_counts = {}

        # Loop through each row to count 4s and 6s for each shot type
        for _, row in final_df.iterrows():
            shot_type = row['shot_type']
            batsman_runs = row['batsman_runs']
            
            # Only consider valid shot types (non-null, string) and boundary runs (4s and 6s)
            if isinstance(shot_type, str) and batsman_runs in [4, 6]:
                # Increment the count for the shot type in boundary_counts
                if shot_type in boundary_counts:
                    boundary_counts[shot_type] += 1
                else:
                    boundary_counts[shot_type] = 1
        if "DEFENDED" in boundary_counts:
            del boundary_counts["DEFENDED"]

        # Find the shot type with the highest boundary count
        if boundary_counts:
            max_shot = max(boundary_counts, key=boundary_counts.get)  # Shot type with the most 4s and 6s
        else:
            max_shot = "N/A"  # Fallback if no boundary data

        with st.container():
            st.markdown(
                f"""
                <style>
                    .stats-box {{
                        background-color: #f0f0f0;
                        padding: 15px;
                        border-radius: 10px;
                        font-family: Arial, sans-serif;
                        color: #333;
                    }}
                    .stats-title {{
                        font-size: 20px;
                        font-weight: bold;
                        margin-bottom: 10px;
                    }}
                    .stats-details {{
                        font-size: 16px;
                        font-weight: bold;
                    }}
                    .compact-line {{
                        font-size: 14px;
                    }}
                    .bold {{
                        font-weight: bold;
                    }}
                    .highlight {{
                        color: #d9534f;
                        font-weight: bold;
                        font-size: 16px;
                        margin-top: 10px;
                    }}
                </style>
                """, unsafe_allow_html=True)
        
            # Define the main stats container
            stats_content = f"""
                <div class="stats-box">
                    <div class="stats-title">{batsman_selected}</div>
                    <div class="stats-details">Runs: {int(total_runs)}</div>
                    <div class="stats-details">Balls: {int(total_balls)}</div>
                    <div class="stats-details">Dismissals: {int(total_dismissals)} 🟥</div>
                    <div class="stats-details">S/R: {strike_rate:.1f}</div>
                    <div class="stats-details">Avg: {avg_runs:.1f}</div>
                    <div class="compact-line">
                        <span class="bold">0s:</span> <span class="white-square"></span> ({percent_zeros:.1f}%) | 
                        <span class="bold">1s:</span> {int(total_ones)} 🟩 ({percent_ones:.1f}%) | 
                        <span class="bold">2s:</span> {int(total_twos)} 🟦 ({percent_twos:.1f}%) | 
                        <span class="bold">3s:</span> {int(total_threes)} 🟪 ({percent_threes:.1f}%) | 
                        <span class="bold">4s:</span> {int(total_fours)} 🟨 ({percent_fours:.1f}%) | 
                        <span class="bold">6s:</span> {int(total_sixes)} 🟫 ({percent_sixes:.1f}%)
                    </div>
            """
            # Render the stats content
            st.markdown(stats_content, unsafe_allow_html=True)

        
        def get_sector_angle(zone, batting_style, offset=0):
            base_angles = {
                1: 45,   # Third Man
                2: 90,   # Point
                3: 135,  # Covers
                4: 180,  # Mid-off
                5: 225,  # Mid-on
                6: 270,  # Mid-wicket
                7: 315,  # Square leg
                8: 360   # Fine leg
            }
            angle = base_angles[zone] + offset
            # if batting_style == 'LHB':
            #     angle = (180 + angle) % 360
            return np.radians(angle)
    
        def get_line_properties(runs):
            properties = {
                1: {'color': 'darkgreen', 'length': 0.5, 'width': 3,'alpha':1},    
                2: {'color': 'darkblue', 'length': 0.65, 'width': 3.5},    
                3: {'color': 'darkviolet', 'length': 0.8, 'width': 3.8},   
                4: {'color': 'goldenrod', 'length': 1.0, 'width': 4.5},     
                6: {'color': 'maroon', 'length': 1.1, 'width': 5}     
            }
            return properties.get(runs, None)
    
        def draw_cricket_field_with_wagon_wheel(final_df):
            fig, ax = plt.subplots(figsize=(12, 12))
            ax.set_aspect('equal')
            ax.axis('off')
            
            # Draw base field elements with lighter outer green
            # boundary = plt.Circle((0, 0), 1, fill=True, color='#228B22', alpha=0.7) 
            boundary = plt.Circle((0, 0), 1, fill=True, color='#228B22', alpha=0.5)# Lighter green
            boundary_line = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=4)
            boundary_glow = plt.Circle((0, 0), 1, fill=False, color='black', linewidth=4, alpha=1)
            inner_circle = plt.Circle((0, 0), 0.5, fill=True, color='#90EE90')
            inner_circle_line = plt.Circle((0, 0), 0.5, fill=False, color='white', linewidth=1)
            
            # Add title
            plt.title('WAGON WHEEL', pad=2, color='white', size=8, fontweight='bold')
            
            # Draw sector lines
            angles = np.linspace(0, 2*np.pi, 9)[:-1]
            for angle in angles:
                x = np.cos(angle)
                y = np.sin(angle)
                ax.plot([0, x], [0, y], color='white', alpha=0.2, linewidth=1)
            
            # Draw pitch rectangle
            pitch_width = 0.08
            pitch_length = 0.16
            pitch_rect = plt.Rectangle((-pitch_width/2, -pitch_length/2), 
                                    pitch_width, pitch_length, 
                                    color='tan', alpha=1)
            
            # Add base elements to plot
            ax.add_patch(boundary)
            ax.add_patch(boundary_glow)
            ax.add_patch(boundary_line)
            ax.add_patch(inner_circle)
            ax.add_patch(inner_circle_line)
            ax.add_patch(pitch_rect)
            
            # Group shots by zone to handle overlapping
            for zone in range(1, 9):
                zone_shots = final_df[final_df['wagonZone'] == zone]
                zone_shots = zone_shots.sort_values('batsman_runs', ascending=False)
                
                num_shots = len(zone_shots)
                if num_shots > 1:
                    offsets = np.linspace(-15, 15, num_shots)
                else:
                    offsets = [0]
                
                for (_, shot), offset in zip(zone_shots.iterrows(), offsets):
                    angle = get_sector_angle(shot['wagonZone'], shot['batting_style'], offset)
                    props = get_line_properties(shot['batsman_runs'])
                    if props:
                        x = props['length'] * np.cos(angle)
                        y = props['length'] * np.sin(angle)
                        ax.plot([0, x], [0, y], 
                                color=props['color'], 
                                linewidth=props['width'], 
                                alpha=0.9,  # Increased line opacity
                                solid_capstyle='round')
                    # x = props['length'] * np.cos(angle)
                    # y = props['length'] * np.sin(angle)
                    
                    # ax.plot([0, x], [0, y], 
                    # color=props['color'], 
                    # linewidth=props['width'], 
                    # alpha=0.9,  # Increased line opacity
                    # solid_capstyle='round')
            
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-1.2, 1.2)
            plt.tight_layout(pad=0)
            return fig
        left_col, right_col = st.columns([2.8, 4])        
        with left_col:
            st.markdown("## WAGON WHEEL")
            fig = draw_cricket_field_with_wagon_wheel(final_df)
            st.pyplot(fig, use_container_width=True)
        
        with right_col:
            st.markdown("## PITCH MAP")
            import streamlit as st
            import plotly.graph_objects as go
            import pandas as pd
            import numpy as np
            
            # Define pitch zones with boundaries
            zones = {
                'Short': (8, 10),
                'Back of Length': (6, 8),
                'Good': (4, 6),
                'Full': (2, 4),
                'Yorker': (0, 2),
                'Full Toss': (-2, 0)
            }
            
            # Define adjusted line positions with compact spacing
            line_positions = {
                'Wide Outside Off Stump': -0.3,
                'Outside Off Stump': -0.15,
                'On Stumps': 0,
                'Outside Leg Stump': 0.15,
                'Wide Outside Leg Stump': 0.3
            }
            
            length_positions = {
                'Short': 9,
                'Back of Length': 7,
                'Good Length': 5,
                'Full': 3,
                'Yorker': 1,
                'Full Toss': -1
            }
            
            # Function to apply a small random offset to length while keeping line accurate
            def apply_length_offset(y_value, offset_range=(-0.95, 0.95), boundary=(-2, 10)):
                offset = np.random.uniform(offset_range[0], offset_range[1])
                if boundary[0] <= y_value + offset <= boundary[1]:
                    return y_value + offset
                return y_value
            
            def apply_line_offset(x_value, offset_range=(-0.05, 0.05), boundary=(-0.5,0.5)):
                offset = np.random.uniform(offset_range[0], offset_range[1])
                if boundary[0] <= x_value + offset <= boundary[1]:
                    return x_value + offset
                return x_value
            
            # Set up the 3D plot
            fig = go.Figure()
            
            # Define stumps and bails
            stump_positions = [-0.05, 0, 0.05]
            stump_height = 0.3
            stump_thickness = 2
            bail_height = stump_height + 0.002
            
            # Add stumps
            for x_pos in stump_positions:
                fig.add_trace(go.Scatter3d(
                    x=[x_pos, x_pos],
                    y=[0, 0],
                    z=[0, stump_height],
                    mode='lines',
                    line=dict(color='black', width=stump_thickness),
                    showlegend=False
                ))
            
            # Add bails
            fig.add_trace(go.Scatter3d(
                x=[stump_positions[0], stump_positions[1]],
                y=[0, 0],
                z=[bail_height, bail_height],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False
            ))
            fig.add_trace(go.Scatter3d(
                x=[stump_positions[1], stump_positions[2]],
                y=[0, 0],
                z=[bail_height, bail_height],
                mode='lines',
                line=dict(color='black', width=2),
                showlegend=False
            ))
            
            # Add pitch zones
            for zone_name, (y_min, y_max) in zones.items():
                fig.add_trace(go.Scatter3d(
                    x=[-0.5, 0.5, 0.5, -0.5, -0.5],
                    y=[y_min, y_min, y_max, y_max, y_min],
                    z=[0, 0, 0, 0, 0],
                    mode='lines+markers',
                    line=dict(color="gray", width=2),
                    marker=dict(size=0.1, opacity=0.2),
                    showlegend=False
                ))
            
            # Add length labels on the side of the pitch
            for length, y_position in length_positions.items():
                fig.add_trace(go.Scatter3d(
                    x=[0.6],  # Adjust X position to be to the side of the pitch
                    y=[y_position],
                    z=[0],
                    mode='text',
                    text=[length],
                    textposition="middle right",
                    textfont=dict(size=10, color="black"),
                    showlegend=False
                ))
            
            # Sample batting style (replace with data from `final_df`)
            batting_style = final_df['batting_style'].iloc[0] if 'batting_style' in final_df else 'Right-hand bat'
            st.write(f"Batting Style: {batting_style}")
            
            # Set a mirroring factor based on batting style
            mirror_factor = -1 if batting_style == 'Left-hand bat' else 1
            
            # Separate the data into wicket and non-wicket balls
            wicket_data = final_df[final_df['is_wkt'] == 1]
            non_wicket_data = final_df[final_df['is_wkt'] == 0]
        
            # Plot wicket balls first
            for index, row in wicket_data.iterrows():
                # Determine base X and Y positions from line and length
                x_base = line_positions.get(row['line'], 0) * mirror_factor
                y_base = length_positions.get(row['length'], 5)
        
                # Apply offset to length (y) while keeping line (x) accurate
                x_pos = apply_line_offset(x_base, boundary=(-0.5, 0.5))
                y_pos = apply_length_offset(y_base, boundary=(-2, 10))
                z_pos = 0
        
                # Set color and size for wickets
                color = 'red'
                size = 5
                opacity = 1  # Set opacity to a single value
        
                # Plot the wicket ball
                fig.add_trace(go.Scatter3d(
                    x=[x_pos],
                    y=[y_pos],
                    z=[z_pos],
                    mode='markers',
                    marker=dict(size=size, color=color, opacity=opacity),
                    hoverinfo="text",
                    text=f"Runs: {row['batsman_runs']} - Wicket"
                ))
        
            # Plot non-wicket balls next
            for index, row in non_wicket_data.iterrows():
                # Determine base X and Y positions from line and length
                x_base = line_positions.get(row['line'], 0) * mirror_factor
                y_base = length_positions.get(row['length'], 5)
        
                # Apply offset to length (y) while keeping line (x) accurate
                x_pos = apply_line_offset(x_base, boundary=(-0.5, 0.5))
                y_pos = apply_length_offset(y_base, boundary=(-2, 10))
                z_pos = 0
        
                # Set color based on runs
                batsman_runs = row['batsman_runs']
                color = {
                    1: 'green',
                    2: 'blue',
                    3: 'violet',
                    4: 'yellow',
                    6: 'orange'
                }.get(batsman_runs, 'gray')
                size = 5
                opacity = 1  # Set opacity to a single value for non-wicket balls
        
                # Plot the non-wicket ball
                fig.add_trace(go.Scatter3d(
                    x=[x_pos],
                    y=[y_pos],
                    z=[z_pos],
                    mode='markers',
                    marker=dict(size=size, color=color, opacity=opacity),
                    hoverinfo="text",
                    text=f"Runs: {row['batsman_runs']} - {'Run'}"
                ))
        
            # Twinkle effect for wickets (already added in the wicket balls loop)
        
            fig.update_layout(
                scene=dict(
                    xaxis=dict(title='X-axis', range=[-1, 1]),
                    yaxis=dict(title='Y-axis', range=[-2, 10]),
                    zaxis=dict(title='Z-axis (Height)', range=[0, 2]),
                ),
                width=1000,
                height=800,
                showlegend=False
            )
            st.plotly_chart(fig)
        
        import numpy as np
        import plotly.graph_objects as go
        import streamlit as st
        
        # Assuming final_df already exists in your environment with 'line', 'length', 'batsman_runs', and 'is_wkt' columns
        
        # Set up line and length mapping
        line_positions = {
            'Wide Outside Off Stump': 0,
            'Outside Off Stump': 1,
            'On Stumps': 2,
            'Outside Leg Stump': 3,
            'Wide Outside Leg Stump': 4
        }
        
        length_positions = {
            'Short': 0,
            'Back of Length': 1,
            'Good Length': 2,
            'Full': 3,
            'Yorker': 4
        }
        
        # Initialize 5x5 grids for ball frequency, run accumulation, and wicket counts
        run_count_grid = np.zeros((5, 5))
        wicket_count_grid = np.zeros((5, 5))
        
        # Fill the grids based on final_df data
        for _, row in final_df.iterrows():
            line = row['line']
            length = row['length']
            runs = row['batsman_runs']
            is_wkt = row['is_wkt']
            
            # Identify the correct cell for run count and wicket count
            line_idx = line_positions.get(line, 2)  # Default to 'On Stumps' if line not found
            length_idx = length_positions.get(length, 2)  # Default to 'Good Length' if length not found
            
            # Update run counts and wicket counts
            run_count_grid[length_idx, line_idx] += runs
            
            if is_wkt == 1:
                wicket_count_grid[length_idx, line_idx] += 1
        
        # Labels for line and length positions
        line_labels = ['Wide Outside Off', 'Outside Off', 'On Stumps', 'Outside Leg', 'Wide Outside Leg']
        length_labels = ['Short', 'Back of Length', 'Good Length', 'Full', 'Yorker']
        
        # Function to create heatmap figure for a 5x5 grid
        def create_heatmap(grid, title, annotations):
            fig = go.Figure(
                data=go.Heatmap(
                    z=grid,
                    colorscale='Reds',
                    colorbar=dict(title=title)
                )
            )
            # Add black text annotations to show actual counts
            for i in range(5):
                for j in range(5):
                    fig.add_annotation(
                        x=j, y=i,
                        text=f'{annotations[i, j]}',
                        showarrow=False,
                        font=dict(color="black", size=12)
                    )
            
            # Update layout for vertical orientation and labels
            fig.update_layout(
                xaxis=dict(showgrid=False, tickvals=list(range(5)), ticktext=line_labels, title="Line"),
                yaxis=dict(showgrid=False, tickvals=list(range(5)), ticktext=length_labels, title="Length"),
                height=700, width=300  # Adjusted size for compact display
            )
            return fig
        
        # Organize layouts in two columns to make them appear side-by-side
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("### Wicket Count")
            # Display the wicket count grid
            st.plotly_chart(create_heatmap(wicket_count_grid, "Wickets", wicket_count_grid), use_container_width=True)
        
        with col2:
            st.write("### Runs Scored")
            # Display the runs count grid
            st.plotly_chart(create_heatmap(run_count_grid, "Runs", run_count_grid), use_container_width=True)

    else:
        # Filter data for the selected bowler
        bowler_selected = batsman_selected
        final_df = temp_df[temp_df["bowler"] == bowler_selected]
        if not final_df.empty:
            # Calculate bowler's metrics
            total_runs_conceded = final_df["total_runs"].sum()
            total_balls_bowled = final_df["valid_ball"].sum()  # Only valid balls count towards economy
            total_wickets = final_df["bowler_wkt"].sum()
            economy_rate = (total_runs_conceded / (total_balls_bowled / 6)) if total_balls_bowled > 0 else 0
            bowling_sr = (total_balls_bowled / total_wickets) if total_wickets > 0 else float('inf')
            
            # Count dot balls for dot percentage
            total_dots = final_df["is_dot"].sum()
            dot_percentage = (total_dots / total_balls_bowled) * 100 if total_balls_bowled > 0 else 0
            
            # Count each scoring shot type
            total_ones = final_df["is_one"].sum()
            total_twos = final_df["is_two"].sum()
            total_threes = final_df["is_three"].sum()
            total_fours = final_df["is_four"].sum()
            total_sixes = final_df["is_six"].sum()
            
            # Calculate percentages for each shot type
            def calc_percentage(value, total):
                return f"{(value / total * 100):.1f}%" if total > 0 else "0%"
            
            percent_ones = calc_percentage(total_ones, total_balls_bowled)
            percent_twos = calc_percentage(total_twos, total_balls_bowled)
            percent_threes = calc_percentage(total_threes, total_balls_bowled)
            percent_fours = calc_percentage(total_fours, total_balls_bowled)
            percent_sixes = calc_percentage(total_sixes, total_balls_bowled)
            
            # Display the statistics in a styled container
            with st.container():
                # Style the display
                st.markdown(
                    f"""
                    <style>
                        .stats-box {{
                            background-color: #f0f0f0;
                            padding: 15px;
                            border-radius: 10px;
                            font-family: Arial, sans-serif;
                            color: #333;
                        }}
                        .stats-title {{
                            font-size: 20px;
                            font-weight: bold;
                            margin-bottom: 10px;
                        }}
                        .stats-details {{
                            font-size: 16px;
                            font-weight: bold;
                        }}
                        .compact-line {{
                            font-size: 14px;
                        }}
                        .bold {{
                            font-weight: bold;
                        }}
                    </style>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                    <div class="stats-box">
                        <div class="stats-title">{bowler_selected}</div>
                        <div class="stats-details">
                            Runs Conceded: {int(total_runs_conceded)}  
                        </div>
                        <div class="stats-details">
                            Balls Bowled: {int(total_balls_bowled)}  
                        </div>
                        <div class="stats-details">
                            Wickets: {int(total_wickets)} 🎯
                        </div>
                        <div class="stats-details">
                            Economy Rate: {economy_rate:.2f}  
                        </div>
                        <div class="stats-details">
                            Bowling S/R: {bowling_sr:.1f}
                        </div>
                        <div class="stats-details">
                            Dot %: {dot_percentage:.1f}%
                        </div>
                        <div class="compact-line">
                            <span class="bold">1s:</span> {int(total_ones)} 🟩 ({percent_ones}) | 
                            <span class="bold">2s:</span> {int(total_twos)} 🟦 ({percent_twos}) | 
                            <span class="bold">3s:</span> {int(total_threes)} 🟪 ({percent_threes}) | 
                            <span class="bold">4s:</span> {int(total_fours)} 🟨 ({percent_fours}) | 
                            <span class="bold">6s:</span> {int(total_sixes)} 🟫 ({percent_sixes})
                        </div>
                    </div>
                """, unsafe_allow_html=True)
    
            import streamlit as st
            import plotly.graph_objects as go
            import pandas as pd
            import numpy as np
            
            st.markdown("## PITCH MAP VS LEFT-HANDED AND RIGHT-HANDED BATSMEN")
            
            # Define pitch zones with boundaries
            zones = {
                'Short': (8, 10),
                'Back of Length': (6, 8),
                'Good': (4, 6),
                'Full': (2, 4),
                'Yorker': (0, 2),
                'Full Toss': (-2, 0)
            }
            
            # Define adjusted line positions with compact spacing
            line_positions = {
                'Wide Outside Off Stump': -0.3,
                'Outside Off Stump': -0.15,
                'On Stumps': 0,
                'Outside Leg Stump': 0.15,
                'Wide Outside Leg Stump': 0.3
            }
            
            length_positions = {
                'Short': 9,
                'Back of Length': 7,
                'Good Length': 5,
                'Full': 3,
                'Yorker': 1,
                'Full Toss': -1
            }
            
            # Function to apply a small random offset to length while keeping line accurate
            def apply_length_offset(y_value, offset_range=(-0.95, 0.95), boundary=(-2, 10)):
                offset = np.random.uniform(offset_range[0], offset_range[1])
                if boundary[0] <= y_value + offset <= boundary[1]:
                    return y_value + offset
                return y_value
            
            def apply_line_offset(x_value, offset_range=(-0.05, 0.05), boundary=(-0.5, 0.5)):
                offset = np.random.uniform(offset_range[0], offset_range[1])
                if boundary[0] <= x_value + offset <= boundary[1]:
                    return x_value + offset
                return x_value
            
            # Set up two columns for LHB and RHB views
            col1, col2 = st.columns(2)
            
            # Filter data for Left-Handed and Right-Handed Batsmen
            final_df = temp_df[temp_df["bowler"] == bowler_selected]
            lhb_data = final_df[final_df['batting_style'] == 'Left-hand bat']
            rhb_data = final_df[final_df['batting_style'] == 'Right-hand bat']
            
            # Function to create a 3D pitch map based on handedness
            def create_pitch_map(data, handedness):
                fig = go.Figure()
            
                # Define stumps and bails
                stump_positions = [-0.05, 0, 0.05]
                stump_height = 0.3
                stump_thickness = 2
                bail_height = stump_height + 0.002
            
                # Add stumps
                for x_pos in stump_positions:
                    fig.add_trace(go.Scatter3d(
                        x=[x_pos, x_pos],
                        y=[0, 0],
                        z=[0, stump_height],
                        mode='lines',
                        line=dict(color='black', width=stump_thickness),
                        showlegend=False
                    ))
            
                # Add bails
                fig.add_trace(go.Scatter3d(
                    x=[stump_positions[0], stump_positions[1]],
                    y=[0, 0],
                    z=[bail_height, bail_height],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False
                ))
                fig.add_trace(go.Scatter3d(
                    x=[stump_positions[1], stump_positions[2]],
                    y=[0, 0],
                    z=[bail_height, bail_height],
                    mode='lines',
                    line=dict(color='black', width=2),
                    showlegend=False
                ))
            
                # Add pitch zones
                for zone_name, (y_min, y_max) in zones.items():
                    fig.add_trace(go.Scatter3d(
                        x=[-0.5, 0.5, 0.5, -0.5, -0.5],
                        y=[y_min, y_min, y_max, y_max, y_min],
                        z=[0, 0, 0, 0, 0],
                        mode='lines+markers',
                        line=dict(color="gray", width=2),
                        marker=dict(size=0.1, opacity=0.2),
                        showlegend=False
                    ))
            
                # Add length labels on the side of the pitch
                for length, y_position in length_positions.items():
                    fig.add_trace(go.Scatter3d(
                        x=[0.6],  # Adjust X position to be to the side of the pitch
                        y=[y_position],
                        z=[0],
                        mode='text',
                        text=[length],
                        textposition="middle right",
                        textfont=dict(size=10, color="black"),
                        showlegend=False
                    ))
            
                # Set mirroring factor based on handedness
                if handedness == 'Left-hand bat':
                    mirror_factor = -1
                elif handedness == 'Right-hand bat':
                    mirror_factor = 1
                else:
                    mirror_factor = 0  # Default case if handedness is neither "Left-hand bat" nor "Right-hand bat"
            
                # Separate the data into wicket and non-wicket balls
                wicket_data = data[data['is_wkt'] == 1]
                non_wicket_data = data[data['is_wkt'] == 0]
            
                # Plot wicket balls first
                for index, row in wicket_data.iterrows():
                    # Determine base X and Y positions from line and length
                    x_base = line_positions.get(row['line'], 0) * mirror_factor
                    y_base = length_positions.get(row['length'], 5)
            
                    # Apply offset to length (y) while keeping line (x) accurate
                    x_pos = apply_line_offset(x_base, boundary=(-0.5, 0.5))
                    y_pos = apply_length_offset(y_base, boundary=(-2, 10))
                    z_pos = 0
            
                    # Set color and size for wickets
                    color = 'red'
                    size = 5
                    opacity = 1  # Set opacity to a single value
            
                    # Plot the wicket ball
                    fig.add_trace(go.Scatter3d(
                        x=[x_pos],
                        y=[y_pos],
                        z=[z_pos],
                        mode='markers',
                        marker=dict(size=size, color=color, opacity=opacity),
                        hoverinfo="text",
                        text=f"Runs: {row['batsman_runs']} - Wicket"
                    ))
            
                # Plot non-wicket balls next
                for index, row in non_wicket_data.iterrows():
                    # Determine base X and Y positions from line and length
                    x_base = line_positions.get(row['line'], 0) * mirror_factor
                    y_base = length_positions.get(row['length'], 5)
            
                    # Apply offset to length (y) while keeping line (x) accurate
                    x_pos = apply_line_offset(x_base, boundary=(-0.5, 0.5))
                    y_pos = apply_length_offset(y_base, boundary=(-2, 10))
                    z_pos = 0
            
                    # Set color based on runs
                    batsman_runs = row['batsman_runs']
                    color = {
                        1: 'green',
                        2: 'blue',
                        3: 'violet',
                        4: 'yellow',
                        6: 'orange'
                    }.get(batsman_runs, 'gray')
                    size = 5
                    opacity = 1  # Set opacity to a single value for non-wicket balls
            
                    # Plot the non-wicket ball
                    fig.add_trace(go.Scatter3d(
                        x=[x_pos],
                        y=[y_pos],
                        z=[z_pos],
                        mode='markers',
                        marker=dict(size=size, color=color, opacity=opacity),
                        hoverinfo="text",
                        text=f"Runs: {row['batsman_runs']} - {'Run'}"
                    ))
            
                # Twinkle effect for wickets (already added in the wicket balls loop)
            
                fig.update_layout(
                    scene=dict(
                        xaxis=dict(title='X-axis', range=[-1, 1]),
                        yaxis=dict(title='Y-axis', range=[-2, 10]),
                        zaxis=dict(title='Z-axis (Height)', range=[0, 2]),
                    ),
                    width=1200,
                    height=1000,
                    showlegend=False
                )
                return fig
    
            
            # Display each plot in the respective column
            with col1:
                st.write("### Against Left-Handed Batsmen")
                if lhb_data.empty:
                    st.write("No data for Left-Handed Batsmen")
                else:
                    st.plotly_chart(create_pitch_map(lhb_data, 'Left-hand bat'))
            
            with col2:
                st.write("### Against Right-Handed Batsmen")
                if rhb_data.empty:
                    st.write("No data for Right-Handed Batsmen")
                else:
                    st.plotly_chart(create_pitch_map(rhb_data, 'Right-hand bat'))
    
    
            import numpy as np
            import plotly.graph_objects as go
            import streamlit as st
            
            # Assuming final_df already exists with the following columns: 'line', 'length', 'batsman_runs', 'is_wkt'
            
            # Set up line and length mapping
            line_positions = {
                'Wide Outside Off Stump': 0,
                'Outside Off Stump': 1,
                'On Stumps': 2,
                'Outside Leg Stump': 3,
                'Wide Outside Leg Stump': 4
            }
            
            length_positions = {
                'Short': 0,
                'Back of Length': 1,
                'Good Length': 2,
                'Full': 3,
                'Yorker': 4
            }
            
            # Initialize 5x5 grids for wicket count and run accumulation
            wicket_count_grid = np.zeros((5, 5))
            run_count_grid_bowler = np.zeros((5, 5))
            
            # Fill the grids based on final_df data
            for _, row in final_df.iterrows():
                line = row['line']
                length = row['length']
                runs = row['batsman_runs']
                is_wkt = row['bowler_wkt']
            
                # Identify the correct cell for wicket count and run count
                line_idx = line_positions.get(line, 2)  # Default to 'On Stumps' if line not found
                length_idx = length_positions.get(length, 2)  # Default to 'Good Length' if length not found
            
                if is_wkt == 1:
                    # Update wicket count in the grid for the given line and length
                    wicket_count_grid[length_idx, line_idx] += 1
                
                # Update run count in the grid for the given line and length
                run_count_grid_bowler[length_idx, line_idx] += runs
            
            # Labels for line and length positions
            line_labels = ['Wide Outside Off', 'Outside Off', 'On Stumps', 'Outside Leg', 'Wide Outside Leg']
            length_labels = ['Short', 'Back of Length', 'Good Length', 'Full', 'Yorker']
            
            # Function to create heatmap figure for a 5x5 grid
            def create_heatmap(grid, title, annotations):
                fig = go.Figure(
                    data=go.Heatmap(
                        z=grid,
                        colorscale='Reds',
                        colorbar=dict(title=f'{title}')
                    )
                )
                # Add black text annotations to show values
                for i in range(5):
                    for j in range(5):
                        fig.add_annotation(
                            x=j, y=i,
                            text=f'{annotations[i, j]}',
                            showarrow=False,
                            font=dict(color="black", size=12)
                        )
                
                # Update layout for vertical orientation and labels
                fig.update_layout(
                    xaxis=dict(showgrid=False, tickvals=list(range(5)), ticktext=line_labels, title="Line"),
                    yaxis=dict(showgrid=False, tickvals=list(range(5)), ticktext=length_labels, title="Length"),
                    height=700, width=300  # Adjusted size for compact display
                )
                return fig
            
            # Organize layouts in two columns to make them appear side-by-side
            col1, col2 = st.columns(2)
            
            # First Column - Wicket Heatmap
            with col1:
                st.write("### Wicket Distribution")
                wicket_fig = create_heatmap(wicket_count_grid, "Wickets", wicket_count_grid)
                st.plotly_chart(wicket_fig, use_container_width=True)
            
            # Second Column - Run Distribution for Bowler
            with col2:
                st.write("### Runs Given")
                run_fig_bowler = create_heatmap(run_count_grid_bowler, "Runs", run_count_grid_bowler)
                st.plotly_chart(run_fig_bowler, use_container_width=True)
        else:
            st.write("## No Bowling Data Available")

                    
