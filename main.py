"""Mystery Island: the terminal front end.

Input and output live here; every rule lives in game/. The choice layer is
numbered and location-aware, so a first-time player can finish the game by
typing digits alone. Invalid input never costs energy and never crashes.
"""

import sys

from game import art
from game import menu
from game import state as g

BAR_FULL, BAR_EMPTY = "#", "."

RULES = [
    "Goal: light the lighthouse beacon before your 5 energy runs out.",
    "Every move costs energy. Search, climb and the bridge cost extra.",
    "You need the rope for the bridge and the lantern for the beacon.",
    "Pick a choice by typing its number, or type a word like 'search'.",
]


def energy_bar(energy):
    return "[{}{}] {}/{}".format(BAR_FULL * max(0, energy),
                                 BAR_EMPTY * max(0, g.ENERGY_START - energy),
                                 max(0, energy), g.ENERGY_START)


def show_header(player):
    carried = ", ".join(player["inventory"]) if player["inventory"] else "nothing"
    print()
    print(energy_bar(player["energy"]),
          "| {} | turns: {} | carrying: {}".format(player["location"],
                                                   player["turns"], carried))


def show_scene(player):
    print(art.scene(player["location"]))
    print(" " + g.LOCATION_STORIES.get(player["location"], ""))
    if g.tide_rising(player):
        print(" ! The tide is climbing. Leave the Beach now or pay double.")


def show_menu(player, fumbles=0):
    actions = menu.available_actions(player)
    print()
    for number, action in enumerate(actions, 1):
        print("  {}) {}".format(number, action["label"]))
    hint = menu.tip(player, fumbles)
    if hint:
        print("\n " + hint)


def show_help():
    print()
    print(" MYSTERY ISLAND - how it works")
    for line in RULES:
        print("  - " + line)
    print()
    print("  Commands: go <place>, search, climb, eat, free gull, cross,")
    print("            light, look, bag, help, quit. Numbers work everywhere.")
    print("  Walking costs 1 energy. The bridge crossing costs 1.")
    print("  Climbing the breadfruit tree costs 1; eating restores 2.")
    print("  Freeing the gull costs 1 and makes the crossing free (a gamble).")
    print("  Lighting the beacon costs your final energy, so arrive with 1 spare.")


def do_turn(player, action):
    """Run one chosen action and narrate it."""
    verb = action["verb"]
    if verb == menu.QUIT:
        return "quit"
    if verb == menu.HELP:
        show_help()
        return "ok"
    if verb == menu.LOOK:
        show_scene(player)
        show_header(player)
        return "ok"
    if verb == menu.BAG:
        print(" You carry: {}".format(
            ", ".join(player["inventory"]) if player["inventory"] else "nothing"))
        return "ok"
    if verb == "status":
        print(" " + g.status(player))
        return "ok"
    if verb == "go":
        result = g.move(player, action["arg"])
    elif verb == "search":
        result = g.search(player)
    elif verb == "climb":
        result = g.climb(player)
    elif verb == "eat":
        result = g.eat(player)
    elif verb == "free":
        result = g.free_gull(player)
    elif verb == "cross":
        result = g.cross_bridge(player)
    elif verb == "light":
        result = g.light_beacon(player)
    elif verb == "wade":
        result = g.risky_crossing(player)
    else:
        result = {"ok": False, "event": "rejected",
                  "message": "That action isn't available here."}

    print(" " + result["message"])
    if result["event"] == "moved":
        show_scene(player)
    if result["ok"] and result["event"] in ("moved", "found", "freed", "ate"):
        show_header(player)
    return "ok" if result["ok"] else "refused"


def one_game(name):
    player = g.new_player(name)
    show_scene(player)
    show_header(player)
    fumbles = 0
    while not g.is_over(player):
        show_menu(player, fumbles)
        try:
            raw = input("\n > ")
        except (EOFError, KeyboardInterrupt):
            print("\n The island swallows the rest of your story.")
            return player
        if not raw.strip():
            continue
        action, message = menu.choose(player, raw)
        if action is None:
            if message:
                print(" " + message)
                fumbles += 1
            continue
        fumbles = 0
        outcome = do_turn(player, action)
        if outcome == "quit":
            try:
                sure = input(" Leave the island unfinished? (y/N) ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n Goodbye.")
                return player
            if sure == "y":
                print(" You leave the island unfinished.")
                return player
    print(art.WIN if player["won"] else art.LOSE)
    if player["won"]:
        print(" You win! Turns: {} | energy left: {}".format(player["turns"],
                                                             player["energy"]))
    else:
        print(" Game over. Turns: {}. The lighthouse stays dark.".format(player["turns"]))
    return player


def main():
    print(art.TITLE)
    print()
    for line in RULES:
        print(" " + line)
    try:
        name = input("\n What should the island call you? ").strip() or "Castaway"
    except (EOFError, KeyboardInterrupt):
        print("\n The island waits for nobody.")
        return 0
    while True:
        one_game(name)
        try:
            again = input("\n Play again? (Y/n) ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n Goodbye.")
            return 0
        if again in ("n", "no"):
            print(" Thanks for playing Mystery Island.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
