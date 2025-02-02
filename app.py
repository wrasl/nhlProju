import matplotlib
matplotlib.use('Agg')  # Use 'Agg' backend for server-side rendering (no GUI)

from flask import Flask, render_template, request, jsonify, send_file
import requests
import matplotlib.pyplot as plt
import json
from io import BytesIO

app = Flask(__name__)

TEAM_LOGOS = json.load(open('logos.json'))

@app.route('/')
def index():
    return render_template('tables.html')  # The HTML file you shared

@app.route('/player_plot/<int:player_id>', methods=['GET'])
def player_plot(player_id):
    # Fetch player data from the NHL API
    url = f"https://api-web.nhle.com/v1/player/{player_id}/landing"
    headers = {"Content-Type": "application/json"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return "Failed to retrieve data", 400

    data = response.json()
    season_totals = data['seasonTotals']
    player_position = data['position']

    # Prepare the lists for plotting
    seasons = []
    goals = []
    assists = []
    points = []
    save_pctg = []
    shutouts = []
    teams = []

    for season_data in season_totals:
        if season_data['leagueAbbrev'] == 'NHL' and season_data["gameTypeId"] == 2:
            seasons.append(season_data['season'])
            teams.append(season_data['teamName']['default'])

            if player_position == 'G':
                save_pctg.append(season_data['savePctg'])
                shutouts.append(season_data['shutouts'])
            else:
                goals.append(season_data['goals'])
                assists.append(season_data['assists'])
                points.append(season_data['points'])

    season_labels = [f"{str(season)[:4][2:]}-{str(season)[4:][2:]}" for season in seasons]

    # Generate the plot
    if player_position == 'G':
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
        # Plotting the data (your original code for the 'else' block)
        fig = plt.figure(figsize=(10, 6))

        plt.plot(season_labels, goals, label="Goals", marker='o')
        plt.plot(season_labels, assists, label="Assists", marker='o')
        plt.plot(season_labels, points, label="Points", marker='o')

        # Adding labels and title
        plt.xlabel('Season')
        plt.ylabel('Stats')
        plt.title(f'{player_id} NHL Career Stats Over Seasons')
        plt.legend()

        for i, txt in enumerate(goals):
            plt.text(season_labels[i], goals[i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker
        for i, txt in enumerate(assists):
            plt.text(season_labels[i], assists[i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker
        for i, txt in enumerate(points):
            plt.text(season_labels[i], points[i] + 0.1, f"{txt}", color='black', ha='center', va='bottom')  # Text above the marker

        plt.xticks(rotation=45)  # Rotate the season labels if needed
        plt.grid(True)

    # Save the plot to a BytesIO object to send as a response
    img_io = BytesIO()
    plt.savefig(img_io, format='png')
    img_io.seek(0)
    plt.close(fig)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)