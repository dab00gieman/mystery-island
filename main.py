"""Mystery Island: the terminal front end.

Input and output live here; every rule lives in game/. The menu repeats until
the player wins, loses or quits, and invalid input is refused without a cost.
"""

import sys

from game import art
from game import state as g

ENERGY_BAR_FULL = "#"


def energy_bar(energy):
    return "[{}{}] {}/{}".format(ENERGY_BAR_FULL * energy,
                                 "." * max(0, g.ENERGY_START - energy),
                                 energy, g.ENERGY_START)


def show_header(p):
    print()
    print(energy_bar(p["energy"]),
          "| {} | turns: {} | carry: {}".format(
              p["location"], p["turns"],
              ", ".join(p["inventory"]) if p["inventory"] else "nothing"))


def show_scene(p):
    print(art.scene(p["location"]))
    print(" " + g.LOCATION_STORIES.get(p["location"], ""))
    if g.tide_rising(p):
        print(" ! The tide is climbing the sand. Leave the Beach now or pay double.")


def show_prompt(p):
    print("\n go <place> | search | climb | eat | free gull | cross | light | "
          "look | bag | help | quit")


def play(turn):
    """Give the player one action. Returns False when the game should stop."""
    if g.is_over(turn):
        return False
    try:
        cmd = input("> ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nThe island swallows the rest of your story.")
        return False
    if not cmd:
        return True
    parts = cmd.split()
    verb, rest = parts[0], " ".join(parts[1:])

    p = turn
    if verb in ("quit", "exit", "q"):
        print(" You leave the island unfinished.")
        return False
    if verb in ("help", "h", "?"):
        print(" Move with: go jungle, go cave, go old bridge, go beach.")
        print(" Bridge: needs the rope. Beacon: needs the lantern and 1 energy.")
        print(" climb gets one breadfruit (-1 energy, eats for +2). free gull saves")
        print(" the gull (-1 energy) and the crossing becomes free — but at 1 energy")
        print(" it kills you. The tide doubles the cost of leaving the Beach late.")
        return True
    if verb in ("look", "l"):
        show_scene(p)
        return True
    if verb in ("bag", "inventory", "i"):
        print(" You carry: {}".format(", ".join(p["inventory"]) if p["inventory"] else "nothing"))
        return True
    if verb == "status":
        print(" {}".format(g.status(p)))
        return True

    if verb in ("go", "walk", "move"):
        result = g.move(p, rest)
    elif verb in ("search", "take"):
        result = g.search(p)
    elif verb == "climb":
        result = g.climb(p)
    elif verb == "eat":
        result = g.eat(p)
    elif verb in ("free", "freegull"):
        result = g.free_gull(p) if rest in ("", "gull") else \
            {"ok": False, "message": "Free what? Try: free gull", "event": "rejected"}
    elif verb == "cross":
        result = g.cross_bridge(p)
    elif verb == "light":
        result = g.light_beacon(p)
    elif verb == "wade":
        result = g.risky_crossing(p)
    else:
        result = {"ok": False, "event": "rejected",
                  "message": "The island doesn't understand '{}'. Type help.".format(cmd)}

    print(" " + result["message"])
    if result["event"] == "moved":
        show_scene(p)
        show_header(p)
    elif result["ok"] and result["event"] in ("found", "freed", "ate"):
        show_header(p)
    return True


def one_game(name):
    p = g.new_player(name)
    show_scene(p)
    show_header(p)
    show_prompt(p)
    while not g.is_over(p):
        if not play(p):
            return p
    print(art.WIN if p["won"] else art.LOSE)
    if p["won"]:
        print(" You win! Turns: {} | energy left: {}".format(p["turns"], p["energy"]))
    else:
        print(" Game over. Turns: {}. The lighthouse stays dark.".format(p["turns"]))
    return p


def main():
    print(art.TITLE)
    print(" You wake on a beach after a storm. You have 5 energy.")
    print(" Light the lighthouse before it runs out. Every move costs energy.")
    print(" Type help at any prompt.")
    try:
        name = input("\n What should the island call you? ").strip() or "Castaway"
    except (EOFError, KeyboardInterrupt):
        print("\n The island waits for nobody.")
        return 0
    while True:
        one_game(name)
        try:
            again = input("\n Play again? (y/n) ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n Goodbye.")
            return 0
        if again not in ("y", "yes"):
            print(" Thanks for playing Mystery Island.")
            return 0


if __name__ == "__main__":
    sys.exit(main())
