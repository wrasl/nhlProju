"""
Fetch games played in the NHL last night from Finland's POV
Get all the Finnish players that played on fetched games
Print their stats from the game
If no Finnish players played, print it out
Still show games played and their results
"""

# IMPORTS
import requests
from datetime import datetime, timedelta
import time
import json

start = time.time()

# Lists for handling
GAME_IDS = []
PLAYER_IDS = set()
FINNISH_PLAYERS = {}
MATCHES = []

PLAYERS = []

# Get the date for last night
yesterday = datetime.today() - timedelta(days=1)

# Format the date as 'YYYY-MM-DD'
yesterday = yesterday.strftime('%Y-%m-%d')

# Base URL
API_URL = "https://api-web.nhle.com/v1/"

# Fetch game list for yesterday
r = requests.get(API_URL + f"schedule/{yesterday}", params={"Content-Type": "application/json"})
data = r.json()

# Get games and their IDs of last night, show results
for date in data["gameWeek"]:
    if date["date"] == yesterday:
        for game in date["games"]:
            GAME_IDS.append(game["id"])
            game_status = "Finished" if game['gameState'] == "OFF" else ("Ongoing" if game['gameState'] == "LIVE" else "Not played")

            game_info = {
                "homeTeam": game["homeTeam"]["abbrev"],
                "awayTeam": game["awayTeam"]["abbrev"],
                "score": (
                    f"{game['homeTeam']['score'] if 'score' in game['homeTeam'] else ''}"
                    f"-"
                    f"{game['awayTeam']['score'] if 'score' in game['awayTeam'] else ''}"
                ),
                "status": game_status,
                "homeLogo": game["homeTeam"]["logo"],
                "awayLogo": game["awayTeam"]["logo"]
            }
            MATCHES.append(game_info)

# Write matches data to a JSON file
with open("matches.json", "w") as f:
    json.dump(MATCHES, f, indent=4)

print("Matches saved to matches.json")

# Check if there are any finished games
finished_games = [match for match in MATCHES if match["status"] == "Finished"]

# If no finished games, return early and print a message
if not finished_games:
    print("No games have been played yet. Exiting without fetching player data.")
    exit()  # Exit the script here

# Use game IDs to fetch info for all the players from the games played
for game_id in GAME_IDS:
    r = requests.get(API_URL + f"gamecenter/{game_id}/boxscore", params={"Content-Type": "application/json"})
    new_data = r.json()

    # List of player categories and team status
    teams = ["awayTeam", "homeTeam"]
    player_categories = ["forwards", "defense", "goalies"]

    # Loop through each team and category to extract player IDs
    for team in teams:
        for category in player_categories:
            player_ids = [player["playerId"] for player in new_data["playerByGameStats"][team][category]]
            PLAYER_IDS.update(player_ids)  # Add all player IDs from this game to the set

    time.sleep(0.1)  # Sleep for 100ms to avoid rate-limiting issues

# Get Finnish players' IDs and photo links (avoiding multiple API requests)
with open("players.txt", "r") as file:
    for line in file:
        parts = line.split()
        playerid = int(parts[-3])
        photo_link = parts[-1]
        nationality = parts[-2]

        # Store Finnish players' data in the dictionary for fast lookup
        if nationality == "FIN":
            FINNISH_PLAYERS[playerid] = photo_link

# Loop through each game and fetch stats for Finnish players
for game_id in GAME_IDS:
    r = requests.get(API_URL + f"gamecenter/{game_id}/boxscore", params={"Content-Type": "application/json"})
    new_data = r.json()

    for team in teams:
        for category in player_categories:
            for player in new_data["playerByGameStats"][team][category]:
                if player["playerId"] in FINNISH_PLAYERS and player["playerId"] in PLAYER_IDS:
                    wanted_data = {}

                    # Get the player's photo link from the FINNISH_PLAYERS dictionary
                    photo_link = FINNISH_PLAYERS.get(player["playerId"])

                    # Extract relevant stats
                    if category in ['forwards', 'defense']:
                        wanted_data.update({
                            'team': new_data[team]["abbrev"],
                            'name': player["name"]["default"],
                            'sweater_number': player["sweaterNumber"],
                            'position': player["position"],
                            'points': player["points"],
                            'goals': player["goals"],
                            'assists': player["assists"],
                            'plus_minus': player["plusMinus"],
                            'toi': player["toi"],
                            'player_id': player["playerId"],
                            'photo_link': photo_link
                        })
                    elif category == 'goalies':
                        wanted_data.update({
                            'team': new_data[team]["abbrev"],
                            'name': player["name"]["default"],
                            'sweater_number': player["sweaterNumber"],
                            'position': player["position"],
                            'shots_against': player["shotsAgainst"],
                            'saves': player["saves"],
                            'save_pctg': round(player["saves"] / player["shotsAgainst"], 3) if player["shotsAgainst"] != 0 else 0.000,
                            'toi': player["toi"],
                            'player_id': player["playerId"],
                            'photo_link': photo_link
                        })

                    # Append the player data to the list
                    PLAYERS.append(wanted_data)

# Separate forwards/defense and goalies
forwards_and_defense = [stats for stats in PLAYERS if stats['position'] != 'G']
goalies = [stats for stats in PLAYERS if stats['position'] == 'G']

# Structure the output data
output_data = {
    "forwards_and_defense": forwards_and_defense,
    "goalies": goalies
}

# Save the data to a JSON file
with open('finnish_players.json', 'w') as json_file:
    json.dump(output_data, json_file, indent=4)

print("Player data has been saved to finnish_players.json")

end = time.time()

# Show the results: this can be altered however you like
if not PLAYERS:
    print("No Finnish players played in today's games.")

print("It took", int(end - start), "seconds!")