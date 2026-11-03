"""Game state and the pure rules over it.

The player is one dictionary passed to every rule function, so the state lives
outside the input handler. Rules return values; only main.py prints stories.

v2 additions (all deterministic, no randomness):
- Energy is a tight economy: the only way to win is to spend one energy early
  to climb for breadfruit, which pays back two later.
- The tide punishes dawdling: leaving the Beach after three actions costs 2.
- The Cave is dark without the lantern: the first entry costs extra.
- The gull at the bridge is a genuine gamble: one energy to free it, and the
  crossing becomes free, but a desperate player dies freeing it.
- Lighting the beacon costs the last energy: you win with 0 left, not before.
"""

ENERGY_START = 5
TIDE_AFTER_TURNS = 3          # leaving the Beach this late costs 2 energy
FRUIT_CAP = 1                 # one breadfruit per game
FRUIT_ENERGY = 2              # eating it restores this much

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
    "Beach": "Wet sand, a wrecked dinghy, and a storm still grumbling offshore. "
             "The tide is already licking at the wreck.",
    "Jungle": "Vines and shade. A breadfruit tree leans over the path, and something "
              "coils in the undergrowth.",
    "Cave": "Dark and dripping. Without a light you're walking on your own shins.",
    "Old Bridge": "A rope-and-plank bridge sways over a black gap. A gull is tangled "
                  "in the rigging, screaming.",
    "Lighthouse": "The tower door hangs open. A stair spirals up to the cold beacon.",
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
        "climbed": False,
        "gull_freed": False,
        "tide_warned": False,
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


def _spend(player, amount):
    """Deduct energy through one path, so 0 energy always means the same thing."""
    player["energy"] = max(0, player["energy"] - amount)
    player["turns"] += 1
    return player["energy"] <= 0


def _exhausted(player, where):
    _finish(player, False)
    return {"ok": False, "event": "lost",
            "message": "Your legs give out in the {}. The island keeps its secret.".format(where)}


def tide_rising(player):
    """True when leaving the Beach would now cost double."""
    return player["location"] == "Beach" and player["turns"] >= TIDE_AFTER_TURNS - 1


def move(player, destination):
    """Move to an adjacent location. Rejections are free; a legal move costs energy."""
    if is_over(player):
        return {"ok": False, "message": "The game is over. Replay to start again.", "event": "rejected"}
    here = player["location"]
    target = destination.strip().title() if isinstance(destination, str) else destination
    if target not in connections(here):
        return {"ok": False,
                "message": "You can't go from {} to {}. Paths: {}.".format(
                    here, destination, ", ".join(connections(here))),
                "event": "rejected"}
    cost = 1
    message = "You walk to {}.".format(target)
    if here == "Beach" and player["turns"] >= TIDE_AFTER_TURNS:
        cost = 2
        message = "You splash out of the rising tide toward {} — it costs you 2 energy.".format(target)
    elif target == "Cave" and not has_item(player, "lantern"):
        cost = 1
        message = "You feel your way into the Cave in total dark and bark your shins."
    player["location"] = target
    dead = _spend(player, cost)
    result = {"ok": True, "message": message, "event": "moved"}
    if dead:
        result.update(_exhausted(player, target))
    return result


def search(player):
    """Look around for an item. Each spot holds one item, collectable once."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    spot = player["location"]
    item = ITEM_SPOTS.get(spot)
    if spot == "Cave" and item and not has_item(player, "lantern"):
        # Blind search: it costs an energy and your hands get cut, but it works.
        dead = _spend(player, 1)
        player["inventory"].append(item)
        result = {"ok": True, "event": "found",
                  "message": "You grope blindly along the wall (-1 energy), cut your hand "
                             "on old metal — and close your fingers around the lantern!"}
        if dead:
            result.update(_exhausted(player, "Cave"))
        return result
    if item is None:
        return {"ok": False, "message": "You search, but there is nothing useful here.",
                "event": "nothing"}
    if has_item(player, item):
        return {"ok": False, "message": "You already carry the {}.".format(item),
                "event": "nothing"}
    player["inventory"].append(item)
    player["turns"] += 1
    return {"ok": True, "message": "You found the {}!".format(item), "event": "found"}


def climb(player):
    """One breadfruit per game. Costs 1 now, eats for 2 later: the key decision."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Jungle":
        return {"ok": False, "message": "There is nothing to climb here.", "event": "rejected"}
    if player["climbed"]:
        return {"ok": False, "message": "You've already stripped the tree.", "event": "rejected"}
    player["climbed"] = True
    dead = _spend(player, 1)
    player["inventory"].append("breadfruit")
    result = {"ok": True, "event": "found",
              "message": "You climb the breadfruit tree (-1 energy) and take one fruit."}
    if dead:
        result.update(_exhausted(player, "Jungle"))
    return result


def eat(player):
    """Breadfruit restores 2 energy, capped at the starting maximum."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if not has_item(player, "breadfruit"):
        return {"ok": False, "message": "You have nothing to eat.", "event": "rejected"}
    player["inventory"].remove("breadfruit")
    player["energy"] = min(ENERGY_START, player["energy"] + FRUIT_ENERGY)
    player["turns"] += 1
    return {"ok": True, "event": "ate",
            "message": "You eat the breadfruit. Energy restored to {}.".format(player["energy"])}


def free_gull(player):
    """The gamble: one energy now, a free crossing later. At 1 energy it kills you."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Old Bridge":
        return {"ok": False, "message": "There is no gull here.", "event": "rejected"}
    if player["gull_freed"]:
        return {"ok": False, "message": "The gull is already free and circling.", "event": "rejected"}
    player["gull_freed"] = True
    dead = _spend(player, 1)
    result = {"ok": True, "event": "freed",
              "message": "You cut the gull loose (-1 energy). It circles the planks and "
                         "shows you which ones are sound: the crossing is now free."}
    if dead:
        result.update(_exhausted(player, "Old Bridge"))
    return result


def cross_bridge(player):
    """The bridge holds with a rope. The gull's map makes the crossing free."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Old Bridge":
        return {"ok": False, "message": "You are not at the bridge.", "event": "rejected"}
    if not has_item(player, "rope"):
        return {"ok": False,
                "message": "The planks are loose and the gap is black. You need a rope.",
                "event": "blocked"}
    cost = 0 if player["gull_freed"] else 1
    player["location"] = "Lighthouse"
    dead = _spend(player, cost)
    message = ("The gull's route is true. You cross without spending a step."
               if cost == 0 else "Rope anchored, you cross to the Lighthouse.")
    result = {"ok": True, "message": message, "event": "moved"}
    if dead:
        result.update(_exhausted(player, "Lighthouse"))
    return result


def light_beacon(player):
    """The win: at the Lighthouse, with the lantern, and one energy to climb."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Lighthouse":
        return {"ok": False, "message": "There is no beacon to light here.", "event": "rejected"}
    if not has_item(player, "lantern"):
        return {"ok": False, "message": "The beacon is cold and dark. You need a lantern.",
                "event": "blocked"}
    if player["energy"] < 1:
        return {"ok": False,
                "message": "You crawl to the stair and cannot lift yourself. One energy "
                           "short of rescue.", "event": "rejected"}
    _spend(player, 1)
    _finish(player, True)
    return {"ok": True, "event": "won",
            "message": "You spend your last strength turning the wick. The beacon blazes. "
                       "A ship turns toward the island. You are saved!"}


def risky_crossing(player):
    """A tempting shortcut at the Beach: costs 2 energy and never works."""
    if is_over(player):
        return {"ok": False, "message": "The game is over.", "event": "rejected"}
    if player["location"] != "Beach":
        return {"ok": False, "message": "The shallows are back at the Beach.", "event": "rejected"}
    dead = _spend(player, 2)
    result = {"ok": False,
              "message": "You wade into the shallows and the current shoves you back. "
                         "You lose 2 energy for nothing.",
              "event": "wasted"}
    if dead:
        result.update(_exhausted(player, "shallows"))
    return result


def status(player):
    """Read-only snapshot for the UI: never mutates the player."""
    return {"name": player["name"], "location": player["location"],
            "energy": player["energy"], "inventory": list(player["inventory"]),
            "game_over": player["game_over"], "won": player["won"],
            "turns": player["turns"], "gull_freed": player["gull_freed"],
            "tide": tide_rising(player)}
