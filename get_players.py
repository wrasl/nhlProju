import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

team_codes = []
# Get all teams
res = requests.get('https://api-web.nhle.com/v1/standings/now')
for team in res.json()['standings']:
    team_codes.append(team['teamAbbrev']['default'])

# Open player file to append player data
player_file = open('players.txt', "a", encoding='utf-8')

# URL to fetch player roster for a given team
url = 'https://api-web.nhle.com/v1/roster/{}/current'

# Store player details (including previous team) in a dictionary for tracking
players_data = {}

# Function to process each team's players
def process_team_roster(team):
    res = requests.get(url.format(team))
    players = [player for position in ['forwards', 'defensemen', 'goalies'] for player in res.json()[position]]
    
    team_players = []
    for player in players:
        player_id = player["id"]
        player_name = f'{player["firstName"]["default"]} {player["lastName"]["default"]}'
        player_team = team
        player_number = player.get("sweaterNumber", "N/A")  # Handle missing sweaterNumber
        player_position = player.get("positionCode", "Unknown")  # Handle missing positionCode
        player_birth_country = player.get("birthCountry", "Unknown")  # Handle missing birthCountry
        player_headshot = player.get("headshot", "N/A")  # Handle missing headshot
        
        # Check if player is already in the players_data (traded or moved player)
        if player_id in players_data:
            prev_team = players_data[player_id]["team"]
            if prev_team != player_team:
                print(f"Player {player_name} has been traded from {prev_team} to {player_team}")

        # Save or update player info (including previous team if traded)
        players_data[player_id] = {
            "team": player_team,
            "number": player_number,
            "position": player_position,
            "name": player_name,
            "birthCountry": player_birth_country,
            "headshot": player_headshot,
        }

        # Prepare the player's info for writing
        team_players.append(f'{player_team} | #{player_number} {player_position} {player_name} {player_id} {player_birth_country} {player_headshot}\n')
    
    return team_players

# Use ThreadPoolExecutor for concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:  # You can adjust the number of workers
    futures = [executor.submit(process_team_roster, team) for team in team_codes]
    
    # Process the results as they complete
    for future in as_completed(futures):
        team_players = future.result()  # Get the list of player info from this team
        for player_data in team_players:
            player_file.write(player_data)  # Write each player's data to the file

# Close the player file
player_file.close()
