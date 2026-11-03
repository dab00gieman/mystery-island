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

Unix, macOS and Windows (use `python` instead of `python3` there).

## How to play (you only need the number keys)

Every turn prints the choices that actually work where you stand, and you pick
one by typing its number:

```
  1) Go to Jungle
  2) Look around
  3) Check your bag
  4) Help
  5) Quit
```

Typing the words still works too (`go jungle`, `search`, `cross`, `light`,
`bag`, `help`, `quit`), in any case and with extra spaces. Nothing you can type
crashes the game, and a wrong entry never costs energy. If you get stuck, the
hint under the menu changes with your situation, and `help` prints the full
rules.

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
What should the island call you? Ada

[#####] 5/5 | Beach | turns: 0 | carrying: nothing
  1) Go to Jungle
  2) Look around
  3) Check your bag
  4) Help
  5) Quit
 > 1                     You walk to Jungle.            (4 energy)
 > 3                     You found the rope!
 > 3                     You climb the tree.            (3 energy, breadfruit)
 > 3                     You eat the breadfruit.        (5 energy)
 > 2                     You feel your way into the Cave in total dark.
 > 3                     You grope blindly (-1 energy) and find the lantern!
 > 2                     You walk to Old Bridge.        (2 energy)
 > 3                     Rope anchored, you cross.      (1 energy)
 > 2                     You spend your last strength turning the wick.
                         THE BEACON BURNS — you win, turns 9, energy 0
```

The winning line costs exactly the 5 energy you start with, so the breadfruit
trade is mandatory. Every wasted action is fatal.

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
