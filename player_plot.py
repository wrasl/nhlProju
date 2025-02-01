import requests
import matplotlib.pyplot as plt

player_id = 8478402#8481035
#8481035

# Fetching the data from the API
url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
headers = {"Content-Type": "application/json"}
response = requests.get(url, headers=headers)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()
else:
    print(f"Failed to retrieve data: {response.status_code}")
    exit()

# Extract season totals from the JSON response
season_totals = data['seasonTotals']
playerPosition = data['position']

# Prepare lists to hold the stats for plotting
seasons = []
goals = []
assists = []
points = []
save_pctg = []
shutouts = []

for season_data in season_totals:
    if season_data['leagueAbbrev'] == 'NHL' and season_data["gameTypeId"] == 2:
        seasons.append(season_data['season'])
        if playerPosition == 'G':
            save_pctg.append(season_data['savePctg'])
            shutouts.append(season_data['shutouts'])
        else:
            goals.append(season_data['goals'])
            assists.append(season_data['assists'])
            points.append(season_data['points'])

season_labels = [f"{str(season)[:4][2:]}-{str(season)[4:][2:]}" for season in seasons]

if playerPosition == 'G':
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot Save Percentage on the first axis (left plot)
    ax1.plot(season_labels, save_pctg, label="Save%", marker='o', color='blue')
    ax1.set_xlabel('Season')
    ax1.set_ylabel('Save Percentage')
    ax1.set_title(f'{player_id} Save Percentage Over Seasons')
    ax1.set_ylim(0, 1)  # Save percentage is between 0 and 1
    ax1.grid(True)
    ax1.legend()

    # Plot Shutouts on the second axis (right plot)
    ax2.plot(season_labels, shutouts, label="Shutouts", marker='o', color='green')
    ax2.set_xlabel('Season')
    ax2.set_ylabel('Shutouts')
    ax2.set_title(f'{player_id} Shutouts Over Seasons')
    ax2.grid(True)
    ax2.legend()

else:
    # Plotting the data
    plt.figure(figsize=(10, 6))

    plt.plot(season_labels, goals, label="Goals", marker='o')
    plt.plot(season_labels, assists, label="Assists", marker='o')
    plt.plot(season_labels, points, label="Points", marker='o')

    # Adding labels and title
    plt.xlabel('Season')
    plt.ylabel('Stats')
    plt.title(f'{player_id} NHL Career Stats Over Seasons')
    plt.legend()

    # Display the plot
    plt.xticks(rotation=45)  # Rotate the season labels if needed
    plt.grid(True)

plt.tight_layout()
plt.show()
