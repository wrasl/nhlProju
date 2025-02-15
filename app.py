from flask import Flask, render_template, request, jsonify, send_file, url_for
import requests
import json

app = Flask(__name__)

# with open('/static/logos.json', 'r') as f:
#    logos_data = json.load(f)

@app.route('/')
def index():
    return render_template('tables.html')

@app.route('/matches_stats')
def matches():

    from util import fetch_matches_players

    try:
        fetch_matches_players()
    except ValueError as e:
        print(e)
        return render_template('tables.html')

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

    # Prepare data for plotting
    seasons = [str(season)[:4][2:] + "-" + str(season)[4:][2:] for season in season_stats]
    seasons_key = [int(season) for season in season_stats]
    if player_position == 'G':
        save_pctg = [stats['save_pctg'] for stats in season_stats.values()]
        shutouts = [stats['shutouts'] for stats in season_stats.values()]
        games = [stats['games'] for stats in season_stats.values()]
    else:
        goals = [stats['goals'] for stats in season_stats.values()]
        assists = [stats['assists'] for stats in season_stats.values()]
        points = [stats['points'] for stats in season_stats.values()]

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

@app.route('/update_player_data', methods=['GET'])
def update_player_data():

    from util import all_stats

    try:
        all_stats()
        return "Player data updated!", 200
    except Exception as e:
        return f"Error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True)

