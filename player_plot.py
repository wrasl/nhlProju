import requests
import matplotlib.pyplot as plt
import json


with open('logos.json') as file:
    TEAM_LOGOS = json.load(file)

# Mapping of full team names to simplified keys in TEAM_LOGOS
TEAM_NAME_MAPPING = {
    "Anaheim Ducks": "anaheim",
    "Boston Bruins": "boston",
    "Buffalo Sabres": "buffalo",
    "Calgary Flames": "calgary",
    "Carolina Hurricanes": "carolina",
    "Chicago Blackhawks": "chicago",
    "Colorado Avalanche": "colorado",
    "Columbus Blue Jackets": "columbus",
    "Dallas Stars": "dallas",
    "Detroit Red Wings": "detroit",
    "Edmonton Oilers": "edmonton",
    "Florida Panthers": "florida",
    "Los Angeles Kings": "losangeles",
    "Minnesota Wild": "minnesota",
    "Montreal Canadiens": "montreal",
    "Nashville Predators": "nashville",
    "New Jersey Devils": "newjersey",
    "New York Islanders": "newyorkislanders",
    "New York Rangers": "newyorkrangers",
    "Ottawa Senators": "ottawa",
    "Philadelphia Flyers": "philadelphia",
    "Pittsburgh Penguins": "pittsburgh",
    "San Jose Sharks": "sanjose",
    "Seattle Kraken": "seattle",
    "St. Louis Blues": "stlouis",
    "Tampa Bay Lightning": "tampa",
    "Toronto Maple Leafs": "toronto",
    "Utah Hockey Club": "utah",
    "Vancouver Canucks": "vancouver",
    "Vegas Golden Knights": "vegas",
    "Washington Capitals": "washington",
    "Winnipeg Jets": "winnipeg"
}

# THIS NEEDS TO BE REMOVED FROM THE FINAL CODE, GET THE ID FROM THE PLAYER INFO
player_id = 8481554#8477424 

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
playerHeadshot = data['headshot']

# Prepare a dictionary to store the aggregated stats for each season
season_stats = {}

for season_data in season_totals:
    if season_data['leagueAbbrev'] == 'NHL' and season_data["gameTypeId"] == 2:
        season = season_data['season']
        team_name = season_data['teamName']['default']

        if season not in season_stats:
            # Initialize the stats for this season
            season_stats[season] = {
                'teams': set(),
                'goals': 0,
                'assists': 0,
                'points': 0,
                'save_pctg': 0,
                'shutouts': 0,
                'games': 0
            }
        
        # Add the team to the season's set of teams
        season_stats[season]['teams'].add(team_name)

        if playerPosition == 'G':
            # For goalies, we aggregate save percentage and shutouts
            season_stats[season]['save_pctg'] += season_data['savePctg']
            season_stats[season]['shutouts'] += season_data['shutouts']
            season_stats[season]['games'] += season_data['gamesPlayed']
        else:
            # For skaters, we aggregate goals, assists, and points
            season_stats[season]['goals'] += season_data['goals']
            season_stats[season]['assists'] += season_data['assists']
            season_stats[season]['points'] += season_data['points']

# Create dictionaries for plotting
player_plot = {
    'goals': [],
    'assists': [],
    'points': [],
    'teams' : []
}

goalie_plot = {
    'save_pctg': [],
    'shutouts': [],
    'games': [],
    'teams' : []
}

seasons = []
teams = []

# Process the aggregated stats and update the dictionaries
for season, stats in season_stats.items():
    seasons.append(str(season)[:4][2:] + "-" + str(season)[4:][2:])
    teams.append(stats['teams'])

    if playerPosition == 'G':
        goalie_plot['save_pctg'].append(stats['save_pctg'])  # Average save percentage
        goalie_plot['shutouts'].append(stats['shutouts'])
        goalie_plot['games'].append(stats['games'])
        goalie_plot['teams'].append(stats['teams'])
    else:
        player_plot['goals'].append(stats['goals'])
        player_plot['assists'].append(stats['assists'])
        player_plot['points'].append(stats['points'])
        player_plot['teams'].append(stats['teams'])

# Plotting the data for goalies and skaters
if playerPosition == 'G':
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot Save Percentage on the first axis (left plot)
    ax1.plot(seasons, goalie_plot['save_pctg'], label="Save%", marker='o', color='blue')
    ax1.set_xlabel('Season')
    ax1.set_ylabel('Save Percentage')
    ax1.set_title(f'{player_id} Save Percentage Over Seasons')
    ax1.set_ylim(0, 1)  # Save percentage is between 0 and 1
    ax1.grid(True)
    ax1.legend()

    # Plot Shutouts on the second axis (right plot)
    ax2.plot(seasons, goalie_plot['shutouts'], label="Shutouts", marker='o', color='blue')
    ax2.plot(seasons, goalie_plot['games'], label="Games Played", marker='o', color='red', linestyle='--')
    ax2.set_xlabel('Season')
    ax2.set_ylabel('Shutouts and games played')
    ax2.set_title(f'{player_id} Shutouts And Games Played Over Seasons')
    ax2.grid(True)
    ax2.legend()

else:
    # Plotting the data for skaters (goals, assists, points)
    plt.figure(figsize=(10, 6))

    plt.plot(seasons, player_plot['goals'], label="Goals", marker='o')
    plt.plot(seasons, player_plot['assists'], label="Assists", marker='o')
    plt.plot(seasons, player_plot['points'], label="Points", marker='o')

    # Adding labels and title
    plt.xlabel('Season')
    plt.ylabel('Stats')
    plt.title(f'{player_id} NHL Career Stats Over Seasons')
    plt.legend()

    for i, txt in enumerate(player_plot['goals']):
        plt.text(seasons[i], player_plot['goals'][i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker
    for i, txt in enumerate(player_plot['assists']):
        plt.text(seasons[i], player_plot['assists'][i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker
    for i, txt in enumerate(player_plot['points']):
        plt.text(seasons[i], player_plot['points'][i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker

    # Display the plot
    plt.xticks(rotation=45)  # Rotate the season labels if needed
    plt.grid(True)

plt.tight_layout()
plt.show()