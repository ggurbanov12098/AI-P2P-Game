import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
USER_ID = os.getenv("USER_ID")
HEADERS = {
    "x-api-key": API_KEY,
    "userid": USER_ID,
    #
    "User-Agent": "PostmanRuntime/7.43.3",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

##########################################################

def get_my_games():
    params = {
        "type": "myGames"
    }
    response = requests.get(API_BASE_URL, headers=HEADERS, params=params)
    try:
        return response.json()
    except ValueError:
        print("ERROR: Could not parse JSON")
        print("Raw response:", response.text)
        return None


def get_board_string(game_id):
    """
    Fetches the board as a string for a given game ID.
    Returns JSON with fields: output, target, code.
    """
    params = {
        "type": "boardString",
        "gameId": game_id
    }
    response = requests.get(API_BASE_URL, headers=HEADERS, params=params)
    try:
        return response.json()
    except ValueError:
        print("ERROR: Could not parse board string JSON")
        print("Raw response:", response.text)
        return None
