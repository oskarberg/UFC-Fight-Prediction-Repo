#%%  Feature Engineering


# Creating a new DataFrame for normalized variables and additional metrics
fighter_profiles = pd.DataFrame(index=grouped.index)

# Number of Fights
fighter_profiles['Number of Fights'] = grouped['Fighter 1 Result'] + grouped['Fighter 2 Result']

# Win Rate
fighter_profiles['Win rate'] = grouped['Fighter 1 Result'] / fighter_profiles['Number of Fights']

fighter_profiles['KOTKO_Rate'] = grouped['Win_by_KOTKO'] / fighter_profiles['Number of Fights']
fighter_profiles['Submission_Rate'] = grouped['Win_by_Submission'] / fighter_profiles['Number of Fights']


# Takedown Success Rate
fighter_profiles['TD Success Rate'] = grouped['Fighter 1 TD Landed'] / grouped['Fighter 1 TD Attempted']

# Takedown Attempt Rate
fighter_profiles['TD Attempt Rate'] = grouped['Fighter 1 TD Attempted'] / grouped['Total Time']

#  KNOCKDOWN Rate
fighter_profiles['KD Rate'] = grouped['Fighter 1 KD'] / fighter_profiles['Number of Fights']

#REV and sub att rate
fighter_profiles['REV SUB ATT Rate'] = (grouped['Fighter 1 REV'] + grouped['Fighter 1 SUB ATT'])  / fighter_profiles['Number of Fights']

# Significant Strike Accuracy
fighter_profiles['SIG STR Accuracy'] = grouped['Fighter 1 SIG STR Landed'] / grouped['Fighter 1 SIG STR Attempted']

fighter_profiles['Control Time Rate'] = grouped['Fighter 1 Ctrl'] / grouped['Total Time']

# Proportions of Strikes Landed (Distance, Clinch, Ground)
fighter_profiles['Prop Distance Strikes'] = grouped['Fighter 1 Distance Landed'] / grouped['Fighter 1 SIG STR Landed']
fighter_profiles['Prop Clinch Strikes'] = grouped['Fighter 1 Clinch Landed'] / grouped['Fighter 1 SIG STR Landed']
fighter_profiles['Prop Ground Strikes'] = grouped['Fighter 1 Ground Landed'] / grouped['Fighter 1 SIG STR Landed']

# Activity Measure
# Note: Adjust weights as per your domain knowledge and analysis needs
fighter_profiles['Activity Measure'] = (
    grouped['Fighter 1 SIG STR Landed'] + 
    grouped['Fighter 1 REV'] + 
    grouped['Fighter 1 SUB ATT'] + 
    grouped['Fighter 1 TD Landed']
) / grouped['Total Time']



fighter_profiles['TD Defense Rate'] = 1 - (grouped['Fighter 2 TD Landed'] / grouped['Fighter 2 TD Attempted'])
fighter_profiles['Striking Defense Rate'] = 1 - (grouped['Fighter 2 SIG STR Landed'] / grouped['Fighter 2 SIG STR Attempted'])
fighter_profiles['Uncontrolled Time Rate'] = 1 - (grouped['Fighter 2 Ctrl'] / grouped['Total Time'])



#%% Cluster visualization using t-SNE (exploratory)


import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler


# Assuming 'Number of Fights' is a column in your fighter_profiles DataFrame
filtered_fighters = fighter_profiles[fighter_profiles['Number of Fights'] >= 10]
filtered_fighters = filtered_fighters.fillna(0)


# Drop 'Number of Fights' and 'Win Rate' columns
filtered_fighters = filtered_fighters.drop(columns=['Number of Fights', 'Win rate', 'Activity Measure'])


scaler = StandardScaler()
scaled_fighters = pd.DataFrame(scaler.fit_transform(filtered_fighters), columns=filtered_fighters.columns, index=filtered_fighters.index)

# Applying t-SNE
tsne = TSNE(n_components=2, random_state=42)
fighters_tsne = tsne.fit_transform(scaled_fighters)

# Creating a DataFrame for easier plotting
tsne_df = pd.DataFrame(fighters_tsne, columns=['Component 1', 'Component 2'])
tsne_df['Name'] = scaled_fighters.index  # Assuming the names are the index

# Plotting
plt.figure(figsize=(10, 8))
plt.scatter(tsne_df['Component 1'], tsne_df['Component 2'], alpha=0.5)

# Annotating specific fighters
names_to_annotate = ['Khabib Nurmagomedov', 'Conor McGregor', 'Justin Gaethje', 
                     'Merab Dvalishvili', 'Dustin Poirier', 'Yoel Romero', 'Kamaru Usman', 
                     'Colby Covington', 'Islam Makhachev', 'Georges St-Pierre', 'Max Holloway', 
                     'Alexander Volkanovski', 'Jon Jones', 'Daniel Cormier', 'Aljamain Sterling', 
                     'Charles Oliveira', 'Leon Edwards']
for name in names_to_annotate:
    point = tsne_df[tsne_df['Name'] == name]
    plt.annotate(name, (point['Component 1'], point['Component 2']))

plt.xlabel('Component 1')
plt.ylabel('Component 2')
plt.title('t-SNE of Fighters')
plt.show()