# Mystery Island

A small terminal text adventure in plain Python 3 (standard library only).

A storm wrecks your boat. You wake on a beach with **5 energy**. Somewhere on
the island are a **rope** and a **lantern**. Cross the bridge, light the
lighthouse beacon, and a rescue ship will see you. Run out of energy and the
island keeps you.

## Prerequisites

Python 3.8 or newer, no packages. Check with `python3 --version`.

## Run it

```
python main.py
```

## Rules and design decisions

- The island is a line: Beach, Jungle, Cave, Old Bridge, Lighthouse.
  Beach <-> Jungle <-> Cave <-> Old Bridge, and the Lighthouse is reachable
  **only** by crossing the bridge with the rope.
- Every legal move costs exactly 1 energy. Rejected input costs nothing.
- The rope is in the Jungle, the lantern is in the Cave. `search` takes each
  item once; searching where there is nothing wastes nothing but a turn.
- `cross` at the Old Bridge needs the rope. `light` at the Lighthouse needs the
  lantern. Lighting the beacon with energy left is the only win.
- Energy reaching 0 before rescue is a loss, and energy never goes below zero.
- `wade` at the Beach is a deliberate trap: a tempting shortcut that costs 2
  energy and never works. That is the third decision with consequences.
- The same state and the same action always give the same outcome: the game is
  fully deterministic, no randomness anywhere.
- Replay builds a brand-new player dictionary, so the old inventory cannot leak
  into the next run.

Controls:

```
go <place>   search   cross   light   wade   inventory   status   help   quit
```

## Example winning run

```
What is your name, castaway? Ada
> go jungle      You walk to Jungle.
> search         You found the rope!
> go cave        You walk to Cave.
> search         You found the lantern!
> go old bridge  You walk to Old Bridge.
> cross          Rope anchored, you cross to the Lighthouse.
> light          You light the beacon. A ship turns toward the island. You are saved!
You win!
Turns: 7 | final energy: 1
```

## Tests

```
python -m unittest discover -s tests -v
```

15 tests: fresh state, invalid input costs nothing, one energy per legal move,
rope collected once, bridge and beacon gates, both endings, energy never
negative, replay reset, and the wrong-direction refusal.

## Known limitations

- No save/load: a game lives for one sitting.
- One item per location and a fixed item map; there is no inventory screen art.
- Moving back and forth is allowed and will exhaust your energy, by design.
- The story text is short; the island is five rooms.
