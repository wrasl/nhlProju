# import HTTP fetching library
import requests
import json

# declare API URL as constant
API_URL = "https://api-web.nhle.com/v1/"

# JSON format
response = requests.get(API_URL + "player/8477424/landing", params={"Content-Type": "application/json"})
data = response.json()

with open("test_turbo", "w") as json_file:
    json.dump(data, json_file, indent=4)

print(data["firstName"]["default"], data["lastName"]["default"], data["birthCountry"])

"""
# loop and filter games by points
games =[x for x in data["gameLog"] if x["points"] > 1]
for game in games or []:
    # initial ratio value
    ratio = 'N/A'

    # let's find the ratio and format it.
    # there is a condition because we do not want to catch
    # Zero devision problem :)
    if game["goals"] > 0:
        ratio = "{0:.2f}".format(game['shots'] / game['goals'])

    # let's print it into the 1 line
    print(f"Game: {game['gameId']}, points={game['points']}, goals={game['goals']}, assists={game['assists']}, shots={game['shots']}, ratio={ratio}")

"""