import pandas as pd

# File paths (replace with actual file paths)
file_paths = {
    "Bowling_ODI": 'Data/ODI_Bowling.csv',
    "Batting_ODI": 'Data/ODI_Batting.csv',
    "Bowling_T20": 'Data/T20_Bowling.csv',
    "Batting_T20": 'Data/T20_Batting.csv',
    "Bowling_Test": 'Data/Test_Bowling.csv',
    "Batting_Test": 'Data/Test_Batting.csv'
}

# Read the CSV files
dfs = {key: pd.read_csv(path) for key, path in file_paths.items()}

# Adding a format column to differentiate between ODI, T20, and Test
for key, df in dfs.items():
    format_type = key.split('_')[1]
    role_type = key.split('_')[0]
    df['Format'] = format_type
    df['Role'] = role_type
    dfs[key] = df

# Combine all data into one DataFrame
combined_df = pd.concat(dfs.values(), ignore_index=True)

# Split Span into Span Start and Span End
combined_df[['Span Start', 'Span End']] = combined_df['Span'].str.split('-', expand=True)

# Convert Span End to numeric to determine if the player is currently playing
combined_df['Span End'] = pd.to_numeric(combined_df['Span End'], errors='coerce')
combined_df['Current Status'] = combined_df['Span End'].apply(lambda x: 'Currently Playing' if x == 2024 else 'Retired')

# Convert necessary columns to numeric types
numeric_cols = ['Matches', 'Innings', 'NO', 'Runs', 'Ave', 'BF', 'SR', '100', '50', '0', 'Balls', 'Wickets', 'Econ', '4', '5', '10']
for col in numeric_cols:
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

# Filter players who have played at least one match in each format
odi_players = set(combined_df[combined_df['Format'] == 'ODI']['Player Name'])
t20_players = set(combined_df[combined_df['Format'] == 'T20']['Player Name'])
test_players = set(combined_df[combined_df['Format'] == 'Test']['Player Name'])

common_players = odi_players & t20_players & test_players

filtered_df = combined_df[combined_df['Player Name'].isin(common_players)]

# Aggregate data to ensure unique player-format combinations
batting_agg = filtered_df[filtered_df['Role'] == 'Batting'].groupby(['Player Name', 'Format']).agg({
    'Innings': 'sum',
    'NO': 'sum',
    'Runs': 'sum',
    'HS': 'max',
    'Ave': 'mean',
    'BF': 'sum',
    'SR': 'mean',
    '100': 'sum',
    '50': 'sum',
    '0': 'sum',
    'Matches': 'first',
    'Span Start': 'first',
    'Span End': 'first',
    'Current Status': 'first'
}).reset_index()

bowling_agg = filtered_df[filtered_df['Role'] == 'Bowling'].groupby(['Player Name', 'Format']).agg({
    'Innings': 'sum',
    'Balls': 'sum',
    'Runs': 'sum',
    'Wickets': 'sum',
    'BBI': 'first',
    'Ave': 'mean',
    'Econ': 'mean',
    'SR': 'mean',
    '4': 'sum',
    '5': 'sum',
    '10': 'sum',
    'Matches': 'first',
    'Span Start': 'first',
    'Span End': 'first',
    'Current Status': 'first'
}).reset_index()

# Pivot the data to have separate columns for each format
batting_pivot = batting_agg.pivot(index='Player Name', columns='Format', values=['Innings', 'NO', 'Runs', 'HS', 'Ave', 'BF', 'SR', '100', '50', '0', 'Span Start', 'Span End', 'Current Status'])
bowling_pivot = bowling_agg.pivot(index='Player Name', columns='Format', values=['Innings', 'Balls', 'Runs', 'Wickets', 'BBI', 'Ave', 'Econ', 'SR', '4', '5', '10', 'Span Start', 'Span End', 'Current Status'])

# Flatten the multi-level columns
batting_pivot.columns = ['_'.join(col).strip() for col in batting_pivot.columns.values]
bowling_pivot.columns = ['_'.join(col).strip() for col in bowling_pivot.columns.values]

# Merging batting and bowling dataframes
merged_df = batting_pivot.join(bowling_pivot, lsuffix='_batting', rsuffix='_bowling')

# Adding columns for matches played in each format
merged_df['ODI_Matches'] = filtered_df[filtered_df['Format'] == 'ODI'].groupby('Player Name')['Matches'].first()
merged_df['T20_Matches'] = filtered_df[filtered_df['Format'] == 'T20'].groupby('Player Name')['Matches'].first()
merged_df['Test_Matches'] = filtered_df[filtered_df['Format'] == 'Test'].groupby('Player Name')['Matches'].first()
merged_df = merged_df.reset_index()

# Merge with meta data
meta_data_cols = ['Player Name', 'Born', 'Age', 'Batting Style', 'Bowling Style', 'Playing Role', 'Height']
meta_data_df = combined_df[meta_data_cols].drop_duplicates(subset=['Player Name'])
final_df = merged_df.merge(meta_data_df, on='Player Name', how='left')

# Reorder columns to have meta data at the start
meta_data_cols.remove('Player Name')
final_df = final_df[['Player Name'] + meta_data_cols + [col for col in final_df.columns if col not in meta_data_cols + ['Player Name']]]

# Save the final combined DataFrame to a CSV file
final_df.to_csv('Data/New_combined_cricket_stats.csv', index=False)

print("Combined cricket stats saved to 'Data/New_combined_cricket_stats.csv'")
