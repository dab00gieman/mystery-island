"""The user-facing choice layer: numbered, location-aware, forgiving.

Pure functions only: available_actions() says what makes sense where the player
stands, choose() maps typed input (a number, a word, a phrase) onto one of
those actions, and tip() offers a gentle nudge when someone keeps fumbling.
Nothing here prints or reads input.
"""

from . import state as g

LOOK, BAG, HELP, QUIT = "look", "bag", "help", "quit"


def _act(label, verb, arg=None):
    return {"label": label, "verb": verb, "arg": arg}


def available_actions(player):
    """Every legal action here, in a stable, human order."""
    if g.is_over(player):
        return [_act("Look around", LOOK), _act("Quit", QUIT)]
    location = player["location"]
    actions = []
    for place in g.connections(location):
        actions.append(_act("Go to " + place, "go", place))
    if location in g.ITEM_SPOTS and not g.has_item(player, g.ITEM_SPOTS[location]):
        actions.append(_act("Search for something useful", "search"))
    if location == "Jungle" and not player.get("climbed"):
        actions.append(_act("Climb the breadfruit tree (1 energy)", "climb"))
    if g.has_item(player, "breadfruit"):
        actions.append(_act("Eat the breadfruit (+2 energy)", "eat"))
    if location == "Old Bridge" and not player.get("gull_freed"):
        actions.append(_act("Free the tangled gull (1 energy)", "free", "gull"))
    if location == "Old Bridge":
        actions.append(_act("Cross the bridge", "cross"))
    if location == "Lighthouse":
        actions.append(_act("Light the beacon (1 energy)", "light"))
    actions.append(_act("Look around", LOOK))
    actions.append(_act("Check your bag", BAG))
    actions.append(_act("Help", HELP))
    actions.append(_act("Quit", QUIT))
    return actions


ALIASES = {
    "l": LOOK, "look": LOOK, "look around": LOOK, "where am i": LOOK,
    "i": BAG, "bag": BAG, "inventory": BAG, "items": BAG,
    "h": HELP, "help": HELP, "?": HELP, "how": HELP,
    "q": QUIT, "quit": QUIT, "exit": QUIT,
    "s": "search", "search": "search", "take": "search", "find": "search",
    "c": "climb", "climb": "climb", "tree": "climb",
    "e": "eat", "eat": "eat", "fruit": "eat",
    "cross": "cross", "cross bridge": "cross", "bridge": "cross",
    "light": "light", "light beacon": "light", "light the beacon": "light",
    "free": "free", "gull": "free", "free gull": "free", "free the gull": "free",
    "wade": "wade", "status": "status",
}

MOVE_PREFIXES = ("go to ", "go ", "walk to ", "walk ", "move to ", "move ", "to ")


def choose(player, raw):
    """Map typed input onto an action. Never raises.

    Returns (action or None, message). The message is only set when the input
    could not be understood or resolved, and it always says what to do next.
    """
    text = (raw or "").strip().lower()
    if not text:
        return None, ""
    actions = available_actions(player)

    if text.isdigit():
        number = int(text)
        if 1 <= number <= len(actions):
            return actions[number - 1], ""
        return None, "There is no choice {}. Pick a number from 1 to {}.".format(
            number, len(actions))

    for prefix in MOVE_PREFIXES:
        if text.startswith(prefix):
            target = text[len(prefix):].strip().title()
            if target in g.connections(player["location"]):
                return _act("Go to " + target, "go", target), ""
            return None, "From {} you can go to {}. Type the number to choose.".format(
                player["location"], " or ".join(g.connections(player["location"])))

    if text.title() in g.connections(player["location"]):
        target = text.title()
        return _act("Go to " + target, "go", target), ""

    verb = ALIASES.get(text)
    if verb is not None:
        if verb == "free" and not g.has_item(player, "rope") and not player.get("gull_freed"):
            return None, "Free what? The gull is tangled on the other side of the gap."
        return _act(text, verb), ""

    return None, "I don't know '{}'. Type the number of a choice, or help.".format(
        raw.strip()[:30])


TIPS = {
    "start": "Tip: numbers are enough. 1 and 2 move you, and the menu only shows "
             "what works where you stand.",
    "energy": "Tip: energy is the whole game. The breadfruit tree buys you energy; "
              "climbing costs 1 and eating returns 2.",
    "beach": "Tip: the tide doubles the price of leaving the Beach after two more "
             "actions. Don't sightsee there.",
    "bridge": "Tip: the bridge needs the rope from the Jungle. Crossing costs 1 "
              "energy, and the gull can make it free.",
    "cave": "Tip: the Cave is dark. Search anyway; your hands will find the lantern.",
    "lighthouse": "Tip: light the beacon. It costs your last energy, so arrive with "
                  "at least 1.",
    "fumbling": "Tip: type the number in front of a choice, or 'help' for the full "
                "rules and commands.",
}


def tip(player, fumbles=0):
    """One contextual hint. Deterministic: same state, same tip."""
    if fumbles >= 2:
        return TIPS["fumbling"]
    if g.is_over(player):
        return ""
    location = player["location"]
    if location == "Beach":
        return TIPS["beach"]
    if location == "Jungle":
        return TIPS["energy"]
    if location == "Cave":
        return TIPS["cave"]
    if location == "Old Bridge":
        return TIPS["bridge"]
    if location == "Lighthouse":
        return TIPS["lighthouse"]
    return TIPS["start"]
