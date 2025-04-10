import sys

from api_client import get_my_games
def print_my_games():
    response = get_my_games()
    print("📋 My Games:\n")

    if response and "myGames" in response:
        print(f"{'Game ID':<8} | {'Team 1':<6} | {'Team 2':<6} | {'Status':<10}")
        print("-" * 40)
        for game in response["myGames"]:
            for game_id, info in game.items():
                parts = info.split(":")
                team1 = parts[0]
                team2 = parts[1]
                status = parts[2] if len(parts) > 2 else "-"
                print(f"{game_id:<8} | {team1:<6} | {team2:<6} | {status:<10}")
    else:
        print("⚠️ No games found or API error.")





from api_client import get_board_string
def print_board_string(game_id):
    data = get_board_string(game_id)

    if not data or data.get("code") != "OK":
        print("⚠️ Failed to fetch board.")
        return

    board_lines = data["output"].strip().split("\n")
    target = data.get("target", "?")
    size = len(board_lines)
    cell_width = 3

    # Header with proper alignment and vertical bar
    col_header = "    " + "".join(f"{i:>{cell_width}} " for i in range(size))
    print(col_header)

    # Divider row
    divider = "    +" + "+".join(["-" * (cell_width)] * size) + "+"

    for i, row in enumerate(board_lines):
        print(divider)
        row_str = " | ".join(f"{c}" for c in row)
        print(f"{i:>2}  | {row_str} |")
    print(divider)

    print(f"\n🎯 Target to win: {target} \n")





from api_client import get_moves
def print_moves(game_id, count=2):
    data = get_moves(game_id, count)
    if not data or data.get("code") != "OK":
        print("⚠️ Could not fetch moves.")
        return

    moves_list = data.get("moves", [])
    if not moves_list:
        print(f"No recent moves found for game {game_id}.")
        return

    print(f"\n🎮 Game {game_id} - Last {count} Moves:\n")
    # Print a table header
    print(f"{'MoveID':<8} | {'TeamID':<6} | {'Symbol':<6} | {'Move':<5}")
    print("-" * 40)

    for move in moves_list:
        move_id = move.get("moveId", "-")
        team_id = move.get("teamId", "-")
        symbol = move.get("symbol", "-")
        move_coord = move.get("move", "-")
        print(f"{move_id:<8} | {team_id:<6} | {symbol:<6} | {move_coord:<5}")
    print()





from api_client import get_game_details
def print_game_details(game_id):
    data = get_game_details(game_id)

    if not data or data.get("code") != "OK":
        print("⚠️ Failed to fetch game details.")
        return

    game_raw = data.get("game", "{}")
    try:
        # Convert the nested JSON string to a dictionary
        import json
        game = json.loads(game_raw)
    except Exception as e:
        print("❌ Error parsing game details:", e)
        return

    print(f"\n🎮 Game Details for Game ID: {game.get('gameid')}")
    print("-" * 40)
    print(f"Type:         {game.get('gametype')}")
    print(f"Board Size:   {game.get('boardsize')} x {game.get('boardsize')}")
    print(f"Target:       {game.get('target')} in a row")
    print(f"Team 1:       {game.get('team1Name')} (ID: {game.get('team1id')})")
    print(f"Team 2:       {game.get('team2Name')} (ID: {game.get('team2id')})")
    print(f"Status:       {'Completed' if game.get('status') == 'C' else 'Ongoing'}")
    print(f"Winner Team:  {game.get('winnerteamid')}")
    print(f"Turn Team:    {game.get('turnteamid')}")
    print(f"Move Count:   {game.get('moves')}")
    print(f"Time per move:{game.get('secondspermove')}s")
    print()




##### Testing ####

# import json
# from api_client import get_game_details, get_board_map

# # Cache for storing boardsize & target once per game
# _game_info_cache = {}

# def print_full_board_map(game_id):
#     """
#     Uses cached boardsize & target from get_game_details,
#     then calls get_board_map to get the actual board moves.
#     Renders the board with the same box style as print_board_string.
#     """

#     # (A) Check if we have the size/target cached; if not, fetch from game details
#     if game_id not in _game_info_cache:
#         details = get_game_details(game_id)
#         if not details or details.get("code") != "OK":
#             print("⚠️ Could not fetch game details for board size.")
#             return
        
#         game_raw = details.get("game", "{}")
#         try:
#             game_data = json.loads(game_raw)
#         except json.JSONDecodeError:
#             print("❌ Could not parse game details JSON.")
#             return

#         board_size = int(game_data.get("boardsize", 3))
#         target_val = int(game_data.get("target", 3))
#         _game_info_cache[game_id] = {"size": board_size, "target": target_val}

#     board_size = _game_info_cache[game_id]["size"]
#     target_val = _game_info_cache[game_id]["target"]

#     # (B) Now fetch the board map to see the actual placed moves
#     response = get_board_map(game_id)
#     if not response or response.get("code") != "OK":
#         print("⚠️ Failed to fetch board map.")
#         return

#     # The 'output' is typically a stringified dictionary of moves
#     try:
#         board_dict = json.loads(response.get("output", "{}"))
#     except json.JSONDecodeError:
#         print("❌ Failed to decode board map JSON.")
#         return

#     # (C) Initialize an NxN board of '-'
#     board = [["-" for _ in range(board_size)] for _ in range(board_size)]
    
#     # (D) Fill in the moves: e.g. {"0,0":"X","0,1":"O", ...}
#     for pos_str, symbol in board_dict.items():
#         r, c = map(int, pos_str.split(","))
#         board[r][c] = symbol

#     # (E) Pretty-print in the same style as print_board_string
#     cell_width = 3

#     print(f"\n🧭 Board Map View (Game {game_id}) — Target: {target_val}\n")

#     # Header row: indices across the top
#     col_header = "    " + "".join(f"{i:>{cell_width}} " for i in range(board_size))
#     print(col_header)

#     # Divider line (like +---+---+...)
#     divider = "    +" + "+".join(["-" * cell_width] * board_size) + "+"

#     # Print each row
#     for row_index, row_data in enumerate(board):
#         print(divider)
#         row_str = " | ".join(str(cell) for cell in row_data)
#         print(f"{row_index:>2}  | {row_str} |")
#     print(divider)

#     print(f"\n🎯 Target to win: {target_val}\n")











######################## # Main Functionality ###########################

def usage_instructions():
    print("\nUsage:")
    print("  python game_utils.py 1")
    print("       -> Prints your available games\n")
    print("  python game_utils.py 2 <game_id>")
    print("       -> Prints the board string for a specific game ID\n")
    print("  python game_utils.py 3 <game_id> <count>")
    print("       -> Prints the last 'count' moves for a game\n")
    print("  python game_utils.py 4 <game_id>")
    print("       -> Print Game Details\n")
    print("  python game_utils.py 5 <game_id>")
    print("       -> Print Board Map\n")


if __name__ == "__main__":
    # If no arguments given, show usage & menu
    if len(sys.argv) == 1:
        print("Select an option:")          # 
        print("1) Print My Games")          # 
        print("2) Print Board String")      # 
        print("3) Print Moves")             # "Get Moves"
        print("4) Print Game Details")      # 
        print("5) Print Board Map")         # 
        usage_instructions()
        sys.exit(0)

    # If the first argument is '1', print my games
    if sys.argv[1] == "1":
        print_my_games()

    # If the first argument is '2', we need a second argument for the game_id
    elif sys.argv[1] == "2":
        if len(sys.argv) < 3:
            print("❌ Missing game ID for option 2.\n")
            usage_instructions()
        else:
            try:
                game_id = int(sys.argv[2])
                print_board_string(game_id)
            except ValueError:
                print("❌ Invalid game ID. Must be an integer.\n")
                usage_instructions()

    elif sys.argv[1] == "3":
        if len(sys.argv) < 3:
            print("❌ Missing <game_id>.\n")
            usage_instructions()
        else:
            game_id = int(sys.argv[2])
            count = 100  # Default
            if len(sys.argv) >= 4:
                count = int(sys.argv[3])
            print_moves(game_id, count)

    elif sys.argv[1] == "4":
        if len(sys.argv) < 3:
            print("❌ Missing <game_id>.\n")
            usage_instructions()
        else:
            try:
                game_id = int(sys.argv[2])
                print_game_details(game_id)
            except ValueError:
                print("❌ Invalid game ID. Must be an integer.\n")
                usage_instructions()

    # elif sys.argv[1] == "5":
    #     if len(sys.argv) < 3:
    #         print("❌ Missing <game_id>.\n")
    #         usage_instructions()
    #     else:
    #         try:
    #             game_id = int(sys.argv[2].strip())
    #             print_full_board_map(game_id)
    #         except ValueError:
    #             print("❌ Invalid game ID. Must be an integer.\n")
    #             usage_instructions()


    # Otherwise, unrecognized option
    else:
        print(f"❌ Unrecognized option: {sys.argv[1]}")
        usage_instructions()