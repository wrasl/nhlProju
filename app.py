from flask import Flask, render_template, request, jsonify, send_file
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

    # Render the template for the player stats page
    return render_template('player_stats.html', 
                           player_id=player_id, 
                           player_headshot=player_headshot, 
                           seasons=seasons,
                           seasons_key=seasons_key, 
                           goals=goals, 
                           assists=assists, 
                           points=points,
                           team_logos=team_logos)

if __name__ == '__main__':
    app.run(debug=True)