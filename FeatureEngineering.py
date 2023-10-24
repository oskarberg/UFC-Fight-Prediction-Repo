#%% Data Cleaning
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# Load the CSV file into a DataFrame
df = pd.read_csv('fight_data_all.csv')

# Display the first few rows of the DataFrame
print(df.head())

# Filter out rows where 'Fighter 1 Ctrl' is '--'
df = df[df['Fighter 1 Ctrl'] != '--']


# 1. Convert Ctrl to minutes
df['Fighter 1 Ctrl'] = df['Fighter 1 Ctrl'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
df['Fighter 2 Ctrl'] = df['Fighter 2 Ctrl'].apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)

# 2. Extract Method
df['Method'] = df['Method'].apply(lambda x: x.split(':')[1].strip())
df['Round'] = df['Round'].apply(lambda x: x.split(':')[1].strip())
df['Round'] = pd.to_numeric(df['Round'], errors='coerce')



# Mapping of results to numeric values
result_mapping = {'W': 1, 'L': 0, 'D': 0.5}  # Adjust as per your use case

# Apply the mapping to the results columns
df['Fighter 1 Result'] = df['Fighter 1 Result'].map(result_mapping)
df['Fighter 2 Result'] = df['Fighter 2 Result'].map(result_mapping)



# 3. Combine Round and Time
df['Time'] = df['Time'].str.replace('Time:', '').apply(lambda x: int(x.split(':')[0]) + int(x.split(':')[1])/60)
df['Total Time'] = df['Time'] + (df['Round'] - 1) * 5  # Add extra minutes based on round number


columns_to_split = [
    'Fighter 1 SIG STR', 'Fighter 1 TD', 'Fighter 1 Distance', 
    'Fighter 1 Clinch', 'Fighter 1 Ground',
    'Fighter 2 SIG STR', 'Fighter 2 TD', 'Fighter 2 Distance', 
    'Fighter 2 Clinch', 'Fighter 2 Ground'
]

for col in columns_to_split:
    df[[f'{col} Landed', f'{col} Attempted']] = df[col].str.split(' of ').apply(pd.Series)
    df[[f'{col} Landed', f'{col} Attempted']] = df[[f'{col} Landed', f'{col} Attempted']].apply(pd.to_numeric, errors='coerce')



# df['Win_by_KOTKO'] = (df['Method'] == 'KO/TKO').astype(int)
# df['Win_by_Submission'] = (df['Method'] == 'Submission').astype(int)

# Columns to drop
columns_to_drop = [
#    'Round', 
    'Time', 
    'Fighter 1 SIG STR', 
    'Fighter 1 TD', 
    'Fighter 1 Distance', 
    'Fighter 1 Clinch', 
    'Fighter 1 Ground',
    'Fighter 2 SIG STR', 
    'Fighter 2 TD', 
    'Fighter 2 Clinch', 
    'Fighter 2 Distance', 
    'Fighter 2 Ground',
]

# Drop the columns
df = df.drop(columns=columns_to_drop)



#%% ELO rating

def update_elo(rating_winner, rating_loser, method, round, k=32):
    """
    Update Elo ratings after a fight, considering method and round.
    
    Parameters:
        rating_winner (float): Elo rating of the winner before the fight.
        rating_loser (float): Elo rating of the loser before the fight.
        method (str): Method of win (e.g., 'Decision - Unanimous', 'KO/TKO', etc.).
        round (int): Round in which the fight ended.
        k (int): K-factor, determines the weight of the tournament (default=32).
        
    Returns:
        tuple: New Elo ratings (new_rating_winner, new_rating_loser).
    """
    expected_winner = 1 / (1 + 10**((rating_loser - rating_winner) / 400))
    expected_loser = 1 / (1 + 10**((rating_winner - rating_loser) / 400))
    
    # Adjust k based on method
    if 'KO/TKO' in method:
        k *= 1.3  # Example: Increase k by 20% for KO/TKO
    elif 'Submission' in method:
        k *= 1.3  # Example: Increase k by 10% for Submission
    elif 'Decision - Unanimous' in method:
        k *= 1.15  # Example: Increase k by 5% for Unanimous Decision
    elif 'Decision - Majority' in method:
        k *= 1.10  # Example: Increase k by 5% for Unanimous Decision
    elif 'Decision - Split' in method:
        k *= 1.00  # Example: Increase k by 2% for Split Decision
    elif 'DQ' in method:
        k = 0
    
    
    new_rating_winner = rating_winner + k * (1 - expected_winner)
    new_rating_loser = rating_loser + k * (0 - expected_loser)
    
    return new_rating_winner, new_rating_loser



# Initialize a dictionary to store the Elo ratings of each fighter
elo_ratings = {}

# Set initial Elo rating
initial_elo = 1500

# Ensure the DataFrame is sorted from oldest to newest
df = df.iloc[::-1]

# Define the update_elo function here (as provided in the previous message)

# Loop through each row in the DataFrame
for idx, row in df.iterrows():
    # Get the names of the fighters
    fighter_1_name = row['Fighter 1 Name']
    fighter_2_name = row['Fighter 2 Name']
    
    # If the fighters are not in the elo_ratings dictionary, add them with the initial Elo rating
    if fighter_1_name not in elo_ratings:
        elo_ratings[fighter_1_name] = initial_elo
    if fighter_2_name not in elo_ratings:
        elo_ratings[fighter_2_name] = initial_elo
    
    # Get the current Elo ratings for the fighters
    elo_fighter_1 = elo_ratings[fighter_1_name]
    elo_fighter_2 = elo_ratings[fighter_2_name]


    # Update Elo ratings based on fight result
    if row['Fighter 1 Result'] == 1.0:  # Fighter 1 wins
        elo_fighter_1, elo_fighter_2 = update_elo(elo_fighter_1, elo_fighter_2, row['Method'], row['Round'])
    elif row['Fighter 2 Result'] == 1.0:  # Fighter 2 wins
        elo_fighter_2, elo_fighter_1 = update_elo(elo_fighter_2, elo_fighter_1, row['Method'], row['Round'])
    # Note: If you want to handle draws, add an additional condition here
    
    # Store the updated Elo ratings back in the dictionary
    elo_ratings[fighter_1_name] = elo_fighter_1
    elo_ratings[fighter_2_name] = elo_fighter_2
    
    # store the updated Elo ratings in the DataFrame as well
    df.at[idx, 'Elo Fighter 1'] = elo_fighter_1
    df.at[idx, 'Elo Fighter 2'] = elo_fighter_2


df = df.iloc[::-1]


#%% Ploting ELO over time (for specific fighter)



def get_elo_for_fighter(df, fighter_name):
    # Filter rows where the fighter is either Fighter 1 or Fighter 2
    df = df.iloc[::-1]
    fighter_rows = df[(df['Fighter 1 Name'] == fighter_name) | (df['Fighter 2 Name'] == fighter_name)]
    
    # Extract the corresponding Elo ratings
    elos = []
    for _, row in fighter_rows.iterrows():
        if row['Fighter 1 Name'] == fighter_name:
            elos.append(row['Elo Fighter 1'])
        else:
            elos.append(row['Elo Fighter 2'])
    
    return fighter_rows['Date'], elos  # Assuming you have a 'Date' column

# Get data for the specific fighter
fighter_name = "Jan Blachowicz"  # Replace with the name of the fighter you're interested in
dates, elo_ratings_time = get_elo_for_fighter(df, fighter_name)

# Plot the Elo ratings over time
plt.figure(figsize=(10, 6))
plt.plot(dates, elo_ratings_time, marker='o', linestyle='-')
plt.title(f"Elo Rating Over Time for {fighter_name}")
plt.xlabel("Date")
plt.ylabel("Elo Rating")
plt.grid(True)
plt.tight_layout()
plt.show()



#%% Aggregation

# Create a copy and swap fighter 1 and fighter 2 columns
df_swapped = df.copy()
df_swapped.columns = df.columns.str.replace(' 1 ', ' Temp ').str.replace(' 2 ', ' 1 ').str.replace(' Temp ', ' 2 ')



# Concatenate the original and swapped DataFrames
df_combined = pd.concat([df, df_swapped], ignore_index=True)


df_combined['Win_by_KOTKO'] = ((df_combined['Fighter 1 Result'] == 1) & (df_combined['Method'] == 'KO/TKO')).astype(int)
df_combined['Win_by_Submission'] = ((df_combined['Fighter 1 Result'] == 1) & (df_combined['Method'] == 'Submission')).astype(int)


grouped = df_combined.groupby('Fighter 1 Name').agg({
    'Fighter 1 Name': 'count',
    'Total Time': 'sum',
    'Fighter 1 Ctrl': 'sum',
    'Fighter 1 Result': 'sum',
    'Fighter 1 KD': 'sum',
    'Fighter 1 SUB ATT': 'sum',
    'Fighter 1 REV': 'sum',
    
    'Fighter 1 TD Landed': 'sum',
    'Fighter 1 TD Attempted': 'sum',
    
    'Fighter 1 SIG STR Landed': 'sum',
    'Fighter 1 SIG STR Attempted': 'sum',
    'Fighter 1 Distance Landed': 'sum',
    'Fighter 1 Clinch Landed': 'sum',
    'Fighter 1 Ground Landed': 'sum',

    'Fighter 2 Ctrl': 'sum',
    'Fighter 2 Result': 'sum',
    'Fighter 2 KD': 'sum',
    'Fighter 2 SUB ATT': 'sum',
    'Fighter 2 REV': 'sum',
    
    'Fighter 2 TD Landed': 'sum',
    'Fighter 2 TD Attempted': 'sum',
    
    'Fighter 2 SIG STR Landed': 'sum',
    'Fighter 2 SIG STR Attempted': 'sum',
    'Fighter 2 Distance Landed': 'sum',
    'Fighter 2 Clinch Landed': 'sum',
    'Fighter 2 Ground Landed': 'sum',
    'Win_by_KOTKO': 'sum',
    'Win_by_Submission': 'sum'
})

# Rename the column after aggregation
grouped = grouped.rename(columns={'Fighter 1 Name': 'Number of Fights'})

# Add the Elo values from the dictionary
grouped['Elo'] = grouped.index.map(elo_ratings)


filtered_grouped = grouped[grouped['Number of Fights'] >= 8]


sns.histplot(filtered_grouped['Elo'], bins=30, kde=True)
plt.title('Distribution of Elo Ratings with KDE')
plt.xlabel('Elo Rating')
plt.ylabel('Number of Fighters')
plt.show()


INITIAL_VARIANCE = 3143.535434794006

def update_variance(num_matches, initial_variance=INITIAL_VARIANCE):
    # This is a simple heuristic: the variance decreases as the number of matches increases.
    return initial_variance / (1 + num_matches)

# Compute the variance for each fighter
grouped['Variance'] = grouped['Number of Fights'].apply(update_variance)



filtered_grouped = grouped[grouped['Number of Fights'] >= 8].copy()


#variance_difference = variance_fighter_1 + variance_fighter_2


def get_elo_momentum_for_fighter(df, fighter_name, short_term_period=3, long_term_period=7):
    # Filter rows where the fighter is either Fighter 1 or Fighter 2
    df = df.iloc[::-1]
    fighter_rows = df[(df['Fighter 1 Name'] == fighter_name) | (df['Fighter 2 Name'] == fighter_name)]
    
    # Extract the corresponding Elo ratings
    elos = []
    for _, row in fighter_rows.iterrows():
        if row['Fighter 1 Name'] == fighter_name:
            elos.append(row['Elo Fighter 1'])
        else:
            elos.append(row['Elo Fighter 2'])
    
    # Calculate short-term momentum
    if len(elos) >= short_term_period + 1:  # +1 because we're considering differences between fights
        short_term_diffs = [(elos[-1] - elos[-(i+2)]) for i in range(short_term_period)]
        short_term = sum(short_term_diffs) / short_term_period
    else:
        short_term = None  # or set to 0 or any default value
    
    # Calculate long-term momentum
    if len(elos) >= long_term_period + 1:  # +1 because we're considering differences between fights
        long_term_diffs = [(elos[-1] - elos[-(i+2)]) for i in range(long_term_period)]
        long_term = sum(long_term_diffs) / long_term_period
    else:
        long_term = None  # or set to 0 or any default value
    
    return short_term, long_term


# Create columns for short-term and long-term momentum in the filtered_grouped DataFrame
filtered_grouped['Short Term Momentum'] = 0
filtered_grouped['Long Term Momentum'] = 0

for fighter_name in filtered_grouped.index:
    short_term, long_term = get_elo_momentum_for_fighter(df, fighter_name)
    filtered_grouped.at[fighter_name, 'Short Term Momentum'] = short_term
    filtered_grouped.at[fighter_name, 'Long Term Momentum'] = long_term



#%%  Feature Engineering



# Creating a new DataFrame for normalized variables and additional metrics
fighter_profiles = pd.DataFrame(index=filtered_grouped.index)

fighter_profiles['Number of Fights'] = filtered_grouped['Number of Fights']

# Win Rate
fighter_profiles['Win rate'] = filtered_grouped['Fighter 1 Result'] / filtered_grouped['Number of Fights']

fighter_profiles['KOTKO_Rate'] = filtered_grouped['Win_by_KOTKO'] / filtered_grouped['Number of Fights']
fighter_profiles['Submission_Rate'] = filtered_grouped['Win_by_Submission'] / filtered_grouped['Number of Fights']


# Takedown Success Rate
fighter_profiles['TD Success Rate'] = filtered_grouped['Fighter 1 TD Landed'] / filtered_grouped['Fighter 1 TD Attempted']

# Takedown Attempt Rate
fighter_profiles['TD landed per minute'] = filtered_grouped['Fighter 1 TD Landed'] / filtered_grouped['Total Time']

#  KNOCKDOWN Rate
fighter_profiles['KD Rate'] = filtered_grouped['Fighter 1 KD'] / filtered_grouped['Number of Fights']

#REV and sub att rate
fighter_profiles['REV SUB ATT Rate'] = (filtered_grouped['Fighter 1 REV'] + filtered_grouped['Fighter 1 SUB ATT'])  / filtered_grouped['Number of Fights']

# Significant Strike Accuracy
fighter_profiles['SIG STR Accuracy'] = filtered_grouped['Fighter 1 SIG STR Landed'] / filtered_grouped['Fighter 1 SIG STR Attempted']

fighter_profiles['SIG STR per minute'] = filtered_grouped['Fighter 1 SIG STR Landed'] / filtered_grouped['Total Time']

fighter_profiles['Control Time Rate'] = filtered_grouped['Fighter 1 Ctrl'] / filtered_grouped['Total Time']

# Proportions of Strikes Landed (Distance, Clinch, Ground)
fighter_profiles['Prop Distance Strikes'] = filtered_grouped['Fighter 1 Distance Landed'] / filtered_grouped['Fighter 1 SIG STR Landed']
fighter_profiles['Prop Clinch Strikes'] = filtered_grouped['Fighter 1 Clinch Landed'] / filtered_grouped['Fighter 1 SIG STR Landed']
fighter_profiles['Prop Ground Strikes'] = filtered_grouped['Fighter 1 Ground Landed'] / filtered_grouped['Fighter 1 SIG STR Landed']

# Activity Measure
# Note: Adjust weights as per your domain knowledge and analysis needs
# fighter_profiles['Activity Measure'] = (
#     filtered_grouped['Fighter 1 SIG STR Landed'] + 
#     filtered_grouped['Fighter 1 REV'] + 
#     filtered_grouped['Fighter 1 SUB ATT'] + 
#     filtered_grouped['Fighter 1 TD Landed']
# ) / filtered_grouped['Total Time']



fighter_profiles['TD Defense Rate'] = 1 - (filtered_grouped['Fighter 2 TD Landed'] / filtered_grouped['Fighter 2 TD Attempted'])
fighter_profiles['Striking Defense Rate'] = 1 - (filtered_grouped['Fighter 2 SIG STR Landed'] / filtered_grouped['Fighter 2 SIG STR Attempted'])
fighter_profiles['Uncontrolled Time Rate'] = 1 - (filtered_grouped['Fighter 2 Ctrl'] / filtered_grouped['Total Time'])


# Add the additional columns
fighter_profiles['Elo'] = filtered_grouped['Elo']
fighter_profiles['Elo_Var'] = filtered_grouped['Variance']
fighter_profiles['Short Term Momentum'] = filtered_grouped['Short Term Momentum']
fighter_profiles['Long Term Momentum'] = filtered_grouped['Long Term Momentum']




#%% Cluster visualization using t-SNE (exploratory)



from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler


filtered_fighters = fighter_profiles[fighter_profiles['Number of Fights'] >= 10]
filtered_fighters = filtered_fighters.fillna(0)


# Drop columns
filtered_fighters = filtered_fighters.drop(columns=['Number of Fights','Win rate', 'Elo', 'Elo_Var', 'Short Term Momentum', 'Long Term Momentum'])


scaler = StandardScaler()
scaled_fighters = pd.DataFrame(scaler.fit_transform(filtered_fighters), columns=filtered_fighters.columns, index=filtered_fighters.index)

# Applying t-SNE
tsne = TSNE(n_components=2, random_state=42)
fighters_tsne = tsne.fit_transform(scaled_fighters)

# Creating a DataFrame for easier plotting
tsne_df = pd.DataFrame(fighters_tsne, columns=['Component 1', 'Component 2'])
tsne_df['Name'] = scaled_fighters.index  # Assuming the names are the index

# Plotting
plt.figure(figsize=(15, 15))
plt.scatter(tsne_df['Component 1'], tsne_df['Component 2'], alpha=0.5)



# Annotating specific fighters
names_to_annotate = ['Khabib Nurmagomedov', 'Conor McGregor', 'Justin Gaethje', 
                      'Merab Dvalishvili', 'Dustin Poirier', 'Yoel Romero', 'Kamaru Usman', 
                      'Colby Covington', 'Islam Makhachev', 'Georges St-Pierre', 'Max Holloway', 
                      'Alexander Volkanovski', 'Jon Jones', 'Daniel Cormier', 'Aljamain Sterling', 
                      'Charles Oliveira', 'Leon Edwards', 'Colby Covington', 'Jan Blachowicz',
                      'Gilbert Burns', 'Chris Weidman',  'Israel Adesanya', 'Glover Teixeira', 
                      'Kevin Holland', 'Brian Ortega', 'Cory Sandhagen']
for name in names_to_annotate:
    point = tsne_df[tsne_df['Name'] == name]
    plt.annotate(name, (point['Component 1'].iloc[0], point['Component 2'].iloc[0]))


plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.title('t-SNE of Fighters')
plt.show()


