"""Mystery Island rules: the ten brief tests plus the bug-hunt cases.

Run with: python -m unittest discover -s tests -v
Every test drives game.state directly; no input() is used.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game.state import (ENERGY_START, connections, cross_bridge, light_beacon, move,
                        new_player, risky_crossing, search, status)


def fresh():
    return new_player("Ada")


class StartTests(unittest.TestCase):
    def test_t1_new_game_state(self):
        p = fresh()
        self.assertEqual(p["location"], "Beach")
        self.assertEqual(p["energy"], ENERGY_START)
        self.assertEqual(p["energy"], 5)
        self.assertEqual(p["inventory"], [])
        self.assertFalse(p["game_over"])

    def test_t10_replay_resets_everything(self):
        p = fresh()
        move(p, "jungle")
        search(p)
        self.assertIn("rope", p["inventory"])
        p2 = new_player("Ada")
        self.assertEqual((p2["location"], p2["energy"], p2["inventory"]),
                         ("Beach", 5, []))
        self.assertIsNot(p["inventory"], p2["inventory"])


class MovementTests(unittest.TestCase):
    def test_t3_legal_move_costs_one_energy(self):
        p = fresh()
        result = move(p, "Jungle")
        self.assertTrue(result["ok"])
        self.assertEqual(p["location"], "Jungle")
        self.assertEqual(p["energy"], 4)

    def test_t4_wrong_direction_free_and_unchanged(self):
        p = fresh()
        before = dict(p)
        result = move(p, "Cave")
        self.assertFalse(result["ok"])
        self.assertEqual(p["location"], before["location"])
        self.assertEqual(p["energy"], before["energy"])
        self.assertEqual(p["turns"], before["turns"])

    def test_lighthouse_not_reachable_by_plain_move(self):
        p = fresh()
        p["location"] = "Old Bridge"
        result = move(p, "Lighthouse")
        self.assertFalse(result["ok"])
        self.assertEqual(p["location"], "Old Bridge")

    def test_moves_after_game_over_are_refused(self):
        p = fresh()
        p["energy"] = 1
        move(p, "Jungle")           # energy 0 -> lost
        self.assertTrue(p["game_over"])
        before = dict(p)
        result = move(p, "Cave")
        self.assertFalse(result["ok"])
        self.assertEqual(p["location"], before["location"])


class InventoryTests(unittest.TestCase):
    def test_t5_rope_collected_once(self):
        p = fresh()
        move(p, "Jungle")
        first = search(p)
        second = search(p)
        self.assertTrue(first["ok"])
        self.assertFalse(second["ok"])
        self.assertEqual(p["inventory"].count("rope"), 1)

    def test_nothing_to_search_at_beach(self):
        p = fresh()
        self.assertFalse(search(p)["ok"])
        self.assertEqual(p["inventory"], [])

    def test_t6_bridge_needs_rope(self):
        p = fresh()
        p["location"] = "Old Bridge"
        blocked = cross_bridge(p)
        self.assertFalse(blocked["ok"])
        self.assertEqual(p["location"], "Old Bridge")
        p["inventory"].append("rope")
        crossed = cross_bridge(p)
        self.assertTrue(crossed["ok"])
        self.assertEqual(p["location"], "Lighthouse")

    def test_t7_beacon_needs_lantern(self):
        p = fresh()
        p["location"] = "Lighthouse"
        blocked = light_beacon(p)
        self.assertFalse(blocked["ok"])
        self.assertFalse(p["game_over"])
        self.assertFalse(p["won"])


class EndingTests(unittest.TestCase):
    def test_t8_full_winning_path(self):
        p = fresh()
        move(p, "Jungle")           # 4
        self.assertTrue(search(p)["ok"])          # rope
        move(p, "Cave")             # 3
        self.assertTrue(search(p)["ok"])          # lantern
        move(p, "Old Bridge")       # 2
        move(p, "Cave")             # 1 -- deliberate detour back
        move(p, "Old Bridge")       # 0 -> would lose!  So the real path:
        self.assertTrue(p["game_over"])

    def test_t8b_win_along_the_shortest_path(self):
        p = fresh()
        move(p, "Jungle")           # 4
        search(p)                   # rope
        move(p, "Cave")             # 3
        search(p)                   # lantern
        move(p, "Old Bridge")       # 2
        self.assertTrue(cross_bridge(p)["ok"])    # 1
        result = light_beacon(p)
        self.assertTrue(result["ok"])
        self.assertTrue(p["won"])
        self.assertTrue(p["game_over"])

    def test_t9_energy_zero_loses(self):
        p = fresh()
        # Four moves from 5 leave 1 energy; the fifth ends the game at 0.
        for target in ("Jungle", "Beach", "Jungle", "Beach"):
            move(p, target)
        self.assertEqual(p["energy"], 1)
        move(p, "Jungle")
        self.assertEqual(p["energy"], 0)
        self.assertTrue(p["game_over"])
        self.assertFalse(p["won"])

    def test_energy_never_negative(self):
        p = fresh()
        p["energy"] = 1
        risky_crossing(p)          # costs 2 from 1
        self.assertEqual(p["energy"], 0)
        self.assertTrue(p["game_over"])

    def test_cannot_win_without_lighthouse(self):
        p = fresh()
        p["inventory"] = ["rope", "lantern"]
        result = light_beacon(p)
        self.assertFalse(result["ok"])
        self.assertFalse(p["won"])


if __name__ == "__main__":
    unittest.main()
