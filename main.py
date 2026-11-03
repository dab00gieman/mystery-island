"""Mystery Island entry point: python main.py

Input and output live here; the rules live in game/state.py.
"""

from game.state import (connections, cross_bridge, is_over, light_beacon, move,
                        new_player, risky_crossing, search, status)

COMMANDS = """
Commands: go <place>, search, cross, light, inventory, status, help, quit
"""


def ask_name():
    while True:
        name = input("What is your name, castaway? ").strip()
        if name:
            return name
        print("A name helps the rescue ship find you. Try again.")


def render(player):
    view = status(player)
    print("\n[{}] {} | energy {} | carrying: {}".format(
        view["location"], view["name"], view["energy"],
        ", ".join(view["inventory"]) or "nothing"))
    print("Paths: {}".format(", ".join(connections(view["location"])) or "none"))


def handle_command(player, raw):
    """Turn one line of input into one action. Pure dispatch, no crashes."""
    text = raw.strip().lower()
    if not text:
        return {"ok": False, "message": "Say something: type help for commands.", "event": "rejected"}
    if text in ("quit", "exit", "q"):
        return {"ok": True, "message": "You leave the island to its storm.", "event": "quit"}
    if text == "help":
        return {"ok": True, "message": COMMANDS.strip(), "event": "help"}
    if text in ("status", "look"):
        return {"ok": True, "message": "You are at the {}.".format(player["location"]),
                "event": "status"}
    if text == "inventory" or text == "i":
        carried = ", ".join(player["inventory"]) or "nothing at all"
        return {"ok": True, "message": "You carry: {}.".format(carried), "event": "status"}
    if text == "search":
        return search(player)
    if text == "cross":
        return cross_bridge(player)
    if text == "light":
        return light_beacon(player)
    if text == "wade":
        return risky_crossing(player)
    if text.startswith("go "):
        return move(player, text[3:])
    if text in ("north", "south", "east", "west"):
        return {"ok": False,
                "message": "There are no compass directions here. Type go <place>.",
                "event": "rejected"}
    return {"ok": False, "message": "I don't know that command. Type help.",
            "event": "rejected"}


def play_once():
    """One game, from title to ending. Returns True if the player wants a replay."""
    print("\n=== MYSTERY ISLAND ===")
    print("A storm wrecked your boat. Five points of energy stand between you")
    print("and the lighthouse on the far point. Find a rope and a lantern.")
    print(COMMANDS)
    player = new_player(ask_name())
    render(player)
    while not is_over(player):
        try:
            raw = input("\n> ")
        except EOFError:
            print("\nThe storm takes the silence as an answer. Goodbye.")
            return False
        result = handle_command(player, raw)
        if result["event"] == "quit":
            print(result["message"])
            return False
        if result["message"]:
            print(result["message"])
        if not is_over(player):
            render(player)
    print("\nYou win!" if player["won"] else "\nGame over.")
    print("Turns: {} | final energy: {}".format(player["turns"], player["energy"]))
    return input("Play again? (y/n) ").strip().lower() in ("y", "yes")


def main():
    while play_once():
        print("\nA new storm, a new island.")
    print("Thanks for playing Mystery Island.")


if __name__ == "__main__":
    main()
