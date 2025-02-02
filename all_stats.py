import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

start = time.time()

# Lists for handling
FINNISH_PLAYERS = {}

# Base URL
API_URL = "https://api-web.nhle.com/v1/"

# Get all the Finnish players and their IDs
with open("players.txt", "r") as file:
    for line in file:
        parts = line.split()
        playerid = int(parts[-3])
        photo_link = parts[-1]
        nationality = parts[-2]

        # Store Finnish players' data in the dictionary for fast lookup
        if nationality == "FIN":
            FINNISH_PLAYERS[playerid] = photo_link

# List to store all players' season data
all_season_data = []

# Function to fetch player data and extract relevant information
def fetch_player_data(player_id):
    response = requests.get(f"https://api-web.nhle.com/v1/player/{player_id}/landing", params={"Content-Type": "application/json"})
    data = response.json()

    # Extract the player's name and sweater number
    player_name = data.get("firstName", {}).get("default", "") + " " + data.get("lastName", {}).get("default", "")
    sweater_number = data.get("sweaterNumber", "")
    position = data.get("position", "")
    photo_link = FINNISH_PLAYERS.get(player_id)

    # Extract the season 2024-2025 data
    season_data = data.get("featuredStats", {}).get("regularSeason", {}).get("subSeason", {})

    # Prepare the player data with their name, sweater number, and season stats
    player_season_data = {
        "name": player_name,
        "sweater_number": sweater_number,
        "photo_link": photo_link,
        "position": position,
        "playerID": player_id,
        "season_2024_2025": season_data
    }

    return player_season_data

# Use ThreadPoolExecutor to make concurrent requests
with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(fetch_player_data, player_id): player_id for player_id in FINNISH_PLAYERS.keys()}
    
    # Wait for the results
    for future in as_completed(futures):
        player_season_data = future.result()
        all_season_data.append(player_season_data)
        print("Player saved.")

# Save all the Finnish players' season data to a JSON file
with open("season_20242025.json", "w") as f:
    json.dump(all_season_data, f, indent=4)

print("Season data for 2024-2025 has been saved to season_20242025.json")

end = time.time()
print(f"Process took {end - start} seconds.")
