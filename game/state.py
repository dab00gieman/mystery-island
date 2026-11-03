"""Game state and the pure rules over it.

The player is one dictionary passed to every rule function, so the state lives
outside the input handler. Rules return values; only main.py prints stories.
"""

ENERGY_START = 5

# The island is a line; every connection works both ways.
MAP = {
    "Beach": ["Jungle"],
    "Jungle": ["Beach", "Cave"],
    "Cave": ["Jungle", "Old Bridge"],
    # No direct path to the Lighthouse: the bridge (cross_bridge) is the only way.
    "Old Bridge": ["Cave"],
    "Lighthouse": ["Old Bridge"],
}

ITEM_SPOTS = {"Jungle": "rope", "Cave": "lantern"}

LOCATION_STORIES = {
    "Beach": "Wet sand, a wrecked dinghy, and a storm still grumbling offshore.",
    "Jungle": "Vines and shade. Something coils in the undergrowth.",
    "Cave": "Dark and dripping. The air smells of old stone.",
    "Old Bridge": "A rope-and-plank bridge sways over a black gap.",
    "Lighthouse": "The tower door hangs open. A stair spirals up to the beacon.",
}


def new_player(name):
    """A fresh game: Beach, 5 energy, nothing carried. Replay calls this again."""
    return {
        "name": name,
        "location": "Beach",
        "energy": ENERGY_START,
        "inventory": [],
        "game_over": False,
        "won": False,
        "turns": 0,
    }


def connections(location):
    """Where the player may legally move from here."""
    return list(MAP.get(location, []))


def has_item(player, item):
    return item in player["inventory"]


def is_over(player):
    return bool(player["game_over"])


def _finish(player, won):
    """One terminal transition, so a game can never end twice."""
    player["game_over"] = True
    player["won"] = won
    return {"ok": True, "message": "", "event": "won" if won else "lost"}


def move(player, destination):
    """Move to an adjacent location, costing 1 energy. Rejections are free."""
    if is_over(player):
        return {"ok": False, "message": "The game is over. Replay to start again.", "event": "rejected"}
    here = player["location"]
    target = destination.strip().title() if isinstance(destination, str) else destination
    if target not in connections(here):
        return {"ok": False,
                "message": "You can't go from {} to {}. Paths: {}.".format(
                    here, destination, ", ".join(connections(here))),
                "event": "rejected"}
    player["location"] = target
    player["energy"] -= 1
    player["turns"] += 1
    result = {"ok": True, "message": "You walk to {}.".format(target), "event": "moved"}
    if player["energy"] <= 0 and not player["won"]:
        player["energy"] = 0
        _finish(player, False)
        result.update(event="lost",
                      message="Your energy runs out in the {}. Rescue never comes.".format(target))
    return result


def search(player):
    """Look around for an item. Each spot holds one item, collectable once."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    spot = player["location"]
    item = ITEM_SPOTS.get(spot)
    if item is None:
        return {"ok": False, "message": "You search, but there is nothing useful here.",
                "event": "nothing"}
    if has_item(player, item):
        return {"ok": False, "message": "You already carry the {}.".format(item),
                "event": "nothing"}
    player["inventory"].append(item)
    player["turns"] += 1
    return {"ok": True, "message": "You found the {}!".format(item), "event": "found"}


def cross_bridge(player):
    """The bridge only holds with a rope. Crossing it costs one energy."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Old Bridge":
        return {"ok": False, "message": "You are not at the bridge.", "event": "rejected"}
    if not has_item(player, "rope"):
        return {"ok": False,
                "message": "The planks are loose and the gap is black. You need a rope.",
                "event": "blocked"}
    if player["location"] == "Lighthouse":
        return {"ok": False, "message": "You already crossed.", "event": "rejected"}
    player["location"] = "Lighthouse"
    player["energy"] -= 1
    player["turns"] += 1
    return {"ok": True, "message": "Rope anchored, you cross to the Lighthouse.",
            "event": "moved"}


def light_beacon(player):
    """The only win: at the Lighthouse, with the lantern, energy left."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Lighthouse":
        return {"ok": False, "message": "There is no beacon to light here.", "event": "rejected"}
    if not has_item(player, "lantern"):
        return {"ok": False, "message": "The beacon is cold and dark. You need a lantern.",
                "event": "blocked"}
    if player["energy"] <= 0:
        return {"ok": False, "message": "Too weak to climb the stairs.", "event": "rejected"}
    player["turns"] += 1
    _finish(player, True)
    return {"ok": True, "event": "won",
            "message": "You light the beacon. A ship turns toward the island. You are saved!"}


def risky_crossing(player):
    """A tempting shortcut at the Beach: costs 2 energy and never works."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Beach":
        return {"ok": False, "message": "The shallows are back at the Beach.", "event": "rejected"}
    player["energy"] -= 2
    player["turns"] += 1
    result = {"ok": False,
              "message": "You wade into the shallows and the current shoves you back. "
                         "You lose 2 energy for nothing.",
              "event": "wasted"}
    if player["energy"] <= 0:
        player["energy"] = 0
        _finish(player, False)
        result.update(event="lost",
                      message="The current takes you. Your energy is gone. The island wins.")
    return result


def status(player):
    """Read-only snapshot for the UI: never mutates the player."""
    return {"name": player["name"], "location": player["location"],
            "energy": player["energy"], "inventory": list(player["inventory"]),
            "game_over": player["game_over"], "won": player["won"]}
