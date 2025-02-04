from flask import Flask, render_template, request, jsonify, send_file, url_for
import requests
import json

app = Flask(__name__)

with open('logos.json', 'r') as f:
    logos_data = json.load(f)

TEAM_LOGO_MAPPING = {
    "Anaheim": "anaheim",
    "Arizona": "arizona",
    "Carolina Hurricanes": "carolina"
}

@app.route('/')
def index():
    return render_template('tables.html')

@app.route('/matches_stats')
def matches():

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
                    "game_id": game["id"],
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
    with open("static/matches.json", "w") as f:
        json.dump(MATCHES, f, indent=4)

    print("Matches saved to matches.json")

    # Check if there are any finished games
    finished_games = [match for match in MATCHES if match["status"] == "Finished"]

    # If no finished games, return early and print a message
    if not finished_games:
        print("No games have been played yet. Exiting without fetching player data.")

        with open('static/finnish_players.json', 'w') as json_file:
            json.dump([], json_file, indent=4)

        return render_template('matches.html', matches=[], finnish_players=[])

    # Use game IDs to fetch info for all the players from the games played
    for game_id in GAME_IDS:

        if not any(match["game_id"] == game_id for match in finished_games):
            continue

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

        if not any(match["game_id"] == game_id for match in finished_games):
            continue  # Skip if the game_id is not in the finished games

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
    with open('static/finnish_players.json', 'w') as json_file:
        json.dump(output_data, json_file, indent=4)

    print("Player data has been saved to finnish_players.json")

    end = time.time()

    # Show the results: this can be altered however you like
    if not PLAYERS:
        print("No Finnish players played in today's games.")

    print("It took", int(end - start), "seconds!")

    with open('static/matches.json', 'r') as f:
        matches = json.load(f)

    with open('static/finnish_players.json', 'r') as f:
        finnish_players = json.load(f)

    return render_template('matches.html', matches=matches, finnish_players=finnish_players)

@app.route('/player/<int:player_id>')
def player_stats(player_id):
    # Fetch the player data from the API
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return f"Error: Failed to fetch data for player {player_id}", 404

    data = response.json()
    season_totals = data['seasonTotals']
    player_position = data['position']
    player_headshot = data['headshot']
    player_name = f"{data['firstName']['default']} {data['lastName']['default']}"
    player_number = data['sweaterNumber']

    season_stats = {}
    team_logos = {}

    for season_data in season_totals:
        if season_data['leagueAbbrev'] == 'NHL' and season_data["gameTypeId"] == 2:
            season = season_data['season']
            team_name = season_data['teamName']['default']

            if season not in season_stats:
                season_stats[season] = {
                    'teams': set(),
                    'goals': 0,
                    'assists': 0,
                    'points': 0,
                    'save_pctg': 0,
                    'shutouts': 0,
                    'games': 0
                }

            season_stats[season]['teams'].add(team_name)

            if player_position == 'G':
                season_stats[season]['save_pctg'] += season_data['savePctg']
                season_stats[season]['shutouts'] += season_data['shutouts']
                season_stats[season]['games'] += season_data['gamesPlayed']
            else:
                season_stats[season]['goals'] += season_data['goals']
                season_stats[season]['assists'] += season_data['assists']
                season_stats[season]['points'] += season_data['points']

            team_logo_key = TEAM_LOGO_MAPPING.get(team_name)
            if team_logo_key:
                team_logos[season] = logos_data.get(team_logo_key)


    # Prepare data for plotting
    seasons = [str(season)[:4][2:] + "-" + str(season)[4:][2:] for season in season_stats]
    seasons_key = [int(season) for season in season_stats]
    goals = [stats['goals'] if player_position != 'G' else stats['save_pctg'] for stats in season_stats.values()]
    assists = [stats['assists'] if player_position != 'G' else stats['shutouts'] for stats in season_stats.values()]
    points = [stats['points'] if player_position != 'G' else stats['games'] for stats in season_stats.values()]

    avg_goals = sum(goals) / len(goals) if goals else 0
    avg_assists = sum(assists) / len(assists) if assists else 0
    avg_points = sum(points) / len(points) if points else 0

    # Render the template for the player stats page
    return render_template('player_stats.html', 
                           player_id=player_id, 
                           player_name=player_name,
                           player_number=player_number,
                           player_headshot=player_headshot, 
                           seasons=seasons,
                           seasons_key=seasons_key, 
                           goals=goals, 
                           assists=assists, 
                           points=points,
                           team_logos=team_logos,
                           avg_goals=avg_goals,
                           avg_assists=avg_assists,
                           avg_points=avg_points)


if __name__ == '__main__':
    app.run(debug=True)

