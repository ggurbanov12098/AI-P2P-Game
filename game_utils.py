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

    print(f"\n🎯 Target to win: {target}")






def usage_instructions():
    print("\nUsage:")
    print("  python game_utils.py 1")
    print("       -> Prints your available games")
    print("  python game_utils.py 2 <game_id>")
    print("       -> Prints the board string for a specific game ID\n")

if __name__ == "__main__":
    # If no arguments given, show usage & menu
    if len(sys.argv) == 1:
        print("Select an option:")
        print("1) Print My Games")
        print("2) Print Board String")
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

    # Otherwise, unrecognized option
    else:
        print(f"❌ Unrecognized option: {sys.argv[1]}")
        usage_instructions()