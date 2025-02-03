import requests
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
player_id = 8481554 #8477424

# Fetching the data from the API
url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
headers = {"Content-Type": "application/json"}
response = requests.get(url, headers=headers)

# Check if the response is successful
if response.status_code == 200:
    data = response.json()

    # Save the data to a file called test.json
    with open('test.json', 'w') as json_file:
        json.dump(data, json_file, indent=4)

    exit()

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

# Prepare the data for the JavaScript plot
seasons = []
goals = []
assists = []
points = []

for season, stats in season_stats.items():
    seasons.append(str(season)[:4][2:] + "-" + str(season)[4:][2:])
    if playerPosition == 'G':
        # For goalies, we use save_pctg and shutouts (you can plot those similarly)
        # Just for simplicity, we'll use goals, assists, and points.
        goals.append(stats['save_pctg'])
        assists.append(stats['shutouts'])
        points.append(stats['games'])
    else:
        goals.append(stats['goals'])
        assists.append(stats['assists'])
        points.append(stats['points'])

# Generate the HTML content with the data injected
html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Player Stats Visualization</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            text-align: center;
            margin: 0;
            padding: 0;
        }}
        .plot-title {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin-top: 50px;  /* Adds space to bring the title lower */
            margin-bottom: 20px;  /* Adds space between title and plot */
        }}
        .plot-title img {{
            border-radius: 50%;
            max-width: 50px;  /* Adjust max-width to desired size */
            max-height: 50px; /* Adjust max-height to desired size */
            margin-right: 15px;
        }}
        #plot {{
            display: block;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="plot-title">
        <h1>Player Stats Over Seasons</h1>
        <img src="{playerHeadshot}" alt="Player Headshot">
    </div>
    <div id="plot"></div>

    <script>
        var seasons = {json.dumps(seasons)};
        var goals = {json.dumps(goals)};
        var assists = {json.dumps(assists)};
        var points = {json.dumps(points)};

        var trace1 = {{
            x: seasons,
            y: goals,
            mode: 'lines+markers',
            name: 'Goals'
        }};

        var trace2 = {{
            x: seasons,
            y: assists,
            mode: 'lines+markers',
            name: 'Assists'
        }};

        var trace3 = {{
            x: seasons,
            y: points,
            mode: 'lines+markers',
            name: 'Points'
        }};

        var layout = {{
            title: '',
            xaxis: {{ title: 'Seasons' }},
            yaxis: {{ title: 'Stats' }}
        }};

        var data = [trace1, trace2, trace3];
        Plotly.newPlot('plot', data, layout);
    </script>
</body>
</html>
"""

# Save the HTML content to a file
with open('plot.html', 'w') as f:
    f.write(html_content)

print("HTML file with plot saved as 'plot.html'")


