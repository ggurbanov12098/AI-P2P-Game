import os
import math
import json
import requests
from dotenv import load_dotenv

##############################################################################
# Load environment variables for the API
##############################################################################
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
USER_ID = os.getenv("USER_ID")

HEADERS = {
    "x-api-key": API_KEY,
    "userid": USER_ID,
    "User-Agent": "PostmanRuntime/7.43.3",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

##############################################################################
# Constants & Symbols
##############################################################################
EMPTY = "-"
# Set these depending on which symbol your team is using in the game
MY_SYMBOL = "X"
OPPONENT_SYMBOL = "O"

##############################################################################
# API Calls
##############################################################################

def get_game_details(game_id):
    """
    Calls the 'gameDetails' API to get boardsize, target, and turn info.
    """
    params = {
        "type": "gameDetails",
        "gameId": game_id
    }
    response = requests.get(API_BASE_URL, headers=HEADERS, params=params)
    try:
        return response.json()
    except ValueError:
        print("ERROR: Could not parse JSON for game details.")
        print("Raw response:", response.text)
        return None

def get_board_map(game_id):
    """
    Calls the 'boardMap' API to get a dictionary of moves like:
    {
       "output": "{\"0,0\":\"X\",\"2,2\":\"O\"}",
       "target": 3,
       "code": "OK"
    }
    """
    params = {
        "type": "boardMap",
        "gameId": game_id
    }
    response = requests.get(API_BASE_URL, headers=HEADERS, params=params)
    try:
        return response.json()
    except ValueError:
        print("ERROR: Could not parse JSON for boardMap.")
        print("Raw response:", response.text)
        return None

def make_move(game_id, team_id, move):
    """
    Posts a move back to the server. 'move' = 'row,col' (0-indexed).
    """
    data = {
        "type": "move",
        "gameId": game_id,
        "teamId": team_id,
        "move": move
    }
    response = requests.post(API_BASE_URL, headers=HEADERS, data=data)
    try:
        return response.json()
    except ValueError:
        print("ERROR: Could not parse JSON for make_move.")
        print("Raw response:", response.text)
        return None

##############################################################################
# Board / Minimax Helpers
##############################################################################

def build_board_from_map(board_size, map_output):
    """
    Given board_size (N) and the stringified dictionary of placed moves,
    build and return a 2D array of shape N x N.
    """
    # Initialize NxN with '-'
    board = [[EMPTY for _ in range(board_size)] for _ in range(board_size)]

    # map_output is e.g. "{\"0,0\":\"X\",\"2,2\":\"O\"}"
    moves_dict = {}
    try:
        moves_dict = json.loads(map_output or "{}")
    except json.JSONDecodeError:
        print("❌ Failed to decode board map JSON.")
        return board

    # Fill in the moves
    for pos_str, symbol in moves_dict.items():
        r, c = map(int, pos_str.split(","))
        board[r][c] = symbol

    return board

def get_available_moves(board):
    moves = []
    for r in range(len(board)):
        for c in range(len(board[0])):
            if board[r][c] == EMPTY:
                moves.append((r, c))
    return moves

def is_win(board, row, col, target, symbol):
    """
    Check if placing 'symbol' at (row, col) has achieved 'target' in a row.
    We'll check:
      1. Horizontal
      2. Vertical
      3. Diagonal (top-left to bottom-right)
      4. Anti-diagonal (top-right to bottom-left)
    """
    n = len(board)

    # Check horizontal
    count = 0
    for c in range(n):
        if board[row][c] == symbol:
            count += 1
            if count >= target:
                return True
        else:
            count = 0

    # Check vertical
    count = 0
    for r in range(n):
        if board[r][col] == symbol:
            count += 1
            if count >= target:
                return True
        else:
            count = 0

    # Check main diagonal
    # We find offset from row-col
    # Then collect consecutive symbols
    # Easiest might be to do a small scan around (row, col)
    # but let's do a bigger approach.
    # We'll shift up-left as far as possible, then go down-right.
    # Start
    rstart, cstart = row, col
    while rstart > 0 and cstart > 0:
        rstart -= 1
        cstart -= 1

    r, c = rstart, cstart
    count = 0
    while r < n and c < n:
        if board[r][c] == symbol:
            count += 1
            if count >= target:
                return True
        else:
            count = 0
        r += 1
        c += 1

    # Check anti-diagonal
    rstart, cstart = row, col
    while rstart > 0 and cstart < n - 1:
        rstart -= 1
        cstart += 1

    r, c = rstart, cstart
    count = 0
    while r < n and c >= 0:
        if board[r][c] == symbol:
            count += 1
            if count >= target:
                return True
        else:
            count = 0
        r += 1
        c -= 1

    return False


def evaluate_terminal(board, target, my_symbol, opp_symbol):
    """
    Check if there's a terminal condition (win/loss/draw).
    Returns:
      +1  if my_symbol is the winner
      -1  if opp_symbol is the winner
       0  if draw
      None if not terminal
    """
    # Quick check for any winning move
    n = len(board)
    # Check who is the winner
    # If found, return +1 or -1
    # If board is full => 0
    # Otherwise None
    # We'll do a naive check: for all squares, see if it's a winning move
    # This is not super optimized, but straightforward.

    empty_found = False
    for r in range(n):
        for c in range(n):
            sym = board[r][c]
            if sym == EMPTY:
                empty_found = True
                continue
            if sym == my_symbol:
                if is_win(board, r, c, target, my_symbol):
                    return +1
            elif sym == opp_symbol:
                if is_win(board, r, c, target, opp_symbol):
                    return -1

    # If no winner found, check if board is full
    if not empty_found:
        return 0  # draw

    return None  # not terminal yet


def evaluate_heuristic(board, target, my_symbol, opp_symbol):
    """
    Scores the board from my_symbol's perspective.
    You can do a more advanced partial-lining approach; here's a simple example:
      +1 for each cell that is my_symbol
      -1 for each cell that is opp_symbol
    Or you can incorporate near-target threats etc.
    """
    score = 0
    n = len(board)
    for r in range(n):
        for c in range(n):
            if board[r][c] == my_symbol:
                score += 1
            elif board[r][c] == opp_symbol:
                score -= 1
    return score


def minimax(board, depth, alpha, beta, is_maximizing, target, my_symbol, opp_symbol):
    """
    Minimax with alpha-beta pruning plus threat checks.
    """
    # Terminal check
    result = evaluate_terminal(board, target, my_symbol, opp_symbol)
    if result is not None or depth == 0:
        # +1 if we are winning, -1 if losing, 0 if draw, or
        # fallback to the heuristic if not fully decided
        if result == +1:
            return 999999  # big pos
        elif result == -1:
            return -999999 # big neg
        elif result == 0:
            return 0
        # else not terminal => use the heuristic
        return evaluate_heuristic(board, target, my_symbol, opp_symbol)

    moves = get_available_moves(board)

    if is_maximizing:
        best_eval = -math.inf
        for (r, c) in moves:
            board[r][c] = my_symbol
            # If placing my_symbol here is an immediate win
            if is_win(board, r, c, target, my_symbol):
                val = 999999
            else:
                val = minimax(board, depth - 1, alpha, beta, False,
                              target, my_symbol, opp_symbol)
            board[r][c] = EMPTY

            best_eval = max(best_eval, val)
            alpha = max(alpha, val)
            if beta <= alpha:
                break
        return best_eval
    else:
        best_eval = math.inf
        for (r, c) in moves:
            board[r][c] = opp_symbol
            if is_win(board, r, c, target, opp_symbol):
                val = -999999
            else:
                val = minimax(board, depth - 1, alpha, beta, True,
                              target, my_symbol, opp_symbol)
            board[r][c] = EMPTY

            best_eval = min(best_eval, val)
            beta = min(beta, val)
            if beta <= alpha:
                break
        return best_eval


def choose_best_move(board, target, my_symbol=MY_SYMBOL, opp_symbol=OPPONENT_SYMBOL):
    """
    Return (row, col) for the best move using minimax + alpha-beta,
    factoring in immediate wins first.
    """
    moves = get_available_moves(board)
    best_value = -math.inf
    best_move = None

    # 1) If any move yields an immediate win, choose it
    for (r, c) in moves:
        board[r][c] = my_symbol
        if is_win(board, r, c, target, my_symbol):
            board[r][c] = EMPTY
            return (r, c)
        board[r][c] = EMPTY

    # 2) Otherwise, do a search
    depth = 3  # adjust as needed
    alpha, beta = -math.inf, math.inf

    for (r, c) in moves:
        board[r][c] = my_symbol
        move_val = minimax(board, depth, alpha, beta, False,
                           target, my_symbol, opp_symbol)
        board[r][c] = EMPTY

        if move_val > best_value:
            best_value = move_val
            best_move = (r, c)

        alpha = max(alpha, best_value)
        if beta <= alpha:
            break

    return best_move


##############################################################################
# Main AI: Grab the board state, pick the best move, and post it
##############################################################################

def ai_make_move(game_id, my_team_id):
    """
    1. Get game details => fetch boardSize, target, check whose turn
    2. Get board map => build the board
    3. Use minimax/alpha-beta to pick best move
    4. Post move back to the server
    """
    # 1) get details
    details = get_game_details(game_id)
    if not details or details.get("code") != "OK":
        print("⚠️ Could not fetch game details.")
        return

    # parse the 'game' field
    game_raw = details.get("game", "{}")
    try:
        game_data = json.loads(game_raw)
    except json.JSONDecodeError:
        print("❌ Could not parse 'game' JSON from details.")
        return

    board_size = int(game_data.get("boardsize", 3))
    target_val = int(game_data.get("target", 3))
    turn_team = str(game_data.get("turnteamid"))

    # If it's not my turn, do nothing
    if turn_team != str(my_team_id):
        print(f"Not my turn yet. Turn belongs to: {turn_team}")
        return

    # 2) get board map
    board_map_json = get_board_map(game_id)
    if not board_map_json or board_map_json.get("code") != "OK":
        print("⚠️ Could not fetch board map.")
        return

    board_map_str = board_map_json.get("output", "{}")

    # 3) build the board
    board = build_board_from_map(board_size, board_map_str)

    # 4) pick best move
    (best_r, best_c) = choose_best_move(board, target_val, MY_SYMBOL, OPPONENT_SYMBOL)
    if best_r is None or best_c is None:
        print("No valid moves left or no best move found.")
        return

    print(f"AI chosen move for game {game_id}: row={best_r}, col={best_c}")

    # 5) make the move
    move_str = f"{best_r},{best_c}"
    response = make_move(game_id, my_team_id, move_str)
    print("Move response:", response)


##############################################################################
# Optional: CLI usage
##############################################################################

if __name__ == "__main__":
    """
    Example usage:
      python ai.py <game_id> <my_team_id>
    This tries to make the best move if it's your turn.
    """
    import sys
    if len(sys.argv) < 3:
        print("Usage: python ai.py <game_id> <my_team_id>")
        sys.exit(0)

    game_id = int(sys.argv[1])
    my_team_id = int(sys.argv[2])
    ai_make_move(game_id, my_team_id)
