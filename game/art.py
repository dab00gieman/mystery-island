"""ASCII art for the island. Pure strings, no printing here."""

TITLE = r'''
   __  __           _                    _____ _____
  |  \/  |_   _ ___| |_ ___ _ __ _   _  |_   _/ ____|
  | |\/| | | | / __| __/ _ \ '__| | | |   | || (___ 
  | |  | | |_| \__ \ ||  __/ |  | |_| |   | | \___ \
  |_|  |_|\__, |___/\__\___|_|   \__, |  _| |_____) |
          |___/                  |___/  |_____|_____|
                        ISLAND
'''

BEACH = r'''
      .  o  .
   .        .        ~~~~~~ ~  ~
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  |  \__/|    T H E   B E A C H
  |__/   |    a wrecked dinghy, a rising tide
  |______|    "leave before the water wins"
'''

JUNGLE = r'''
    &&&  &&&&   &&&
   &&&&& &&&&& &&&&&      T H E   J U N G L E
    |||   |||   |||       green teeth, one fruit tree
    |||   |||   |||       something coils in the dark
   _|||___|||___|||_
'''

CAVE = r'''
      /\
     /  \      _____
    /    \    /     \
   /      \  |  o o  |    T H E   C A V E
  /   /\   \ |       |    dark, dripping, blind
 /___/  \___\|_______|    bring your own light
'''

BRIDGE = r'''
       |          |          |
   ----+----------+----------+----
   ~~~~|~~~~~~~~~~|~~~~~~~~~~|~~~~   O L D   B R I D G E
       |          |          |       rope and rotten planks
  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~  "the gull knows"
       ~   ~   ~   ~   ~   ~   ~
'''

LIGHTHOUSE = r'''
            ________
           /  .  .  \
          / .  o  .  \        L I G H T H O U S E
         /___________ \       cold glass, one wick
         |  |     |  |        one last climb
         |  |     |  |
        _|__|_____|__|_
'''

WIN = r'''
   \   |   /        .-"""-.
    \  |  /        /  .-.  \
     \ | /        |  ( o )  |     THE BEACON BURNS
      \|/          \  '-'  /      a ship is coming
   ----+----        '-...-'       you are saved
      /|\
'''

LOSE = r'''
     .-.  .-.
    ( x ) ( x )        the island goes quiet
     '-'  '-'
      \    /           energy spent, story over
       \  /            the tide keeps its secret
        \/
'''

SCENES = {"Beach": BEACH, "Jungle": JUNGLE, "Cave": CAVE,
          "Old Bridge": BRIDGE, "Lighthouse": LIGHTHOUSE}


def scene(location):
    """Art for a location, or a plain fallback so an unknown place never crashes."""
    return SCENES.get(location, "\n  [ {} ]\n".format(location))
