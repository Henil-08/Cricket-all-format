import pandas as pd

# File paths (replace with actual file paths)
file_paths = {
    "Bowling_ODI": 'Data/Bowling_ODI.csv',
    "Batting_ODI": 'Data/Batting_ODI.csv',
    "Bowling_T20": 'Data/Bowling_T20.csv',
    "Batting_T20": 'Data/Batting_T20.csv',
    "Bowling_Test": 'Data/Bowling_Test.csv',
    "Batting_Test": 'Data/Batting_Test.csv'
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

# Convert necessary columns to numeric types
numeric_cols = ['Inns', 'NO', 'Runs', 'Ave', 'BF', 'SR', '100', '50', '0', 'Balls', 'Wkts', 'BBI', 'Econ', '4', '5', 'Mat']
for col in numeric_cols:
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')

# Aggregate data to ensure unique player-format combinations
batting_agg = combined_df[combined_df['Role'] == 'Batting'].groupby(['Player', 'Format']).agg({
    'Inns': 'sum',
    'NO': 'sum',
    'Runs': 'sum',
    'HS': 'max',
    'Ave': 'mean',
    'BF': 'sum',
    'SR': 'mean',
    '100': 'sum',
    '50': 'sum',
    '0': 'sum',
    'Mat': 'first'
}).reset_index()

bowling_agg = combined_df[combined_df['Role'] == 'Bowling'].groupby(['Player', 'Format']).agg({
    'Inns': 'sum',
    'Balls': 'sum',
    'Runs': 'sum',
    'Wkts': 'sum',
    'BBI': 'max',
    'Ave': 'mean',
    'Econ': 'mean',
    'SR': 'mean',
    '4': 'sum',
    '5': 'sum',
    'Mat': 'first'
}).reset_index()

# Pivot the data to have separate columns for each format
batting_pivot = batting_agg.pivot(index='Player', columns='Format', values=['Inns', 'NO', 'Runs', 'HS', 'Ave', 'BF', 'SR', '100', '50', '0'])
bowling_pivot = bowling_agg.pivot(index='Player', columns='Format', values=['Inns', 'Balls', 'Runs', 'Wkts', 'BBI', 'Ave', 'Econ', 'SR', '4', '5'])

# Flatten the multi-level columns
batting_pivot.columns = ['_'.join(col).strip() for col in batting_pivot.columns.values]
bowling_pivot.columns = ['_'.join(col).strip() for col in bowling_pivot.columns.values]

# Merging batting and bowling dataframes
merged_df = batting_pivot.join(bowling_pivot, lsuffix='_batting', rsuffix='_bowling')

# Adding columns for matches played in each format
merged_df['ODI_Matches'] = combined_df[combined_df['Format'] == 'ODI'].groupby('Player')['Mat'].first()
merged_df['T20_Matches'] = combined_df[combined_df['Format'] == 'T20'].groupby('Player')['Mat'].first()
merged_df['Test_Matches'] = combined_df[combined_df['Format'] == 'Test'].groupby('Player')['Mat'].first()

# Function to determine the role
def determine_role(row):
    total_batting_inns = sum(row[col] for col in ['Inns_ODI_batting', 'Inns_T20_batting', 'Inns_Test_batting'] if not pd.isna(row[col]))
    total_bowling_inns = sum(row[col] for col in ['Inns_ODI_bowling', 'Inns_T20_bowling', 'Inns_Test_bowling'] if not pd.isna(row[col]))
    
    if total_batting_inns > total_bowling_inns * 1.5:
        return 'Batter'
    elif total_bowling_inns > total_batting_inns * 1.5:
        return 'Bowler'
    else:
        return 'All-rounder'

# Apply the function to determine the role
merged_df['Role'] = merged_df.apply(determine_role, axis=1)

# Filter players who have played at least one match in each format
filtered_df = merged_df.dropna(subset=['ODI_Matches', 'T20_Matches', 'Test_Matches'])

# Resetting index for a cleaner DataFrame
final_df = filtered_df.reset_index()

# Save the final combined DataFrame to a CSV file
final_df.to_csv('Data/New_combined_cricket_stats.csv', index=False)

print("Combined cricket stats saved to 'combined_cricket_stats.csv'")