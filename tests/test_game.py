"""Mystery Island rules: the ten brief tests, the economy, and the bug-hunt cases.

Run with: python -m unittest discover -s tests -v
Every test drives game.state directly; no input() is used.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import art
from game import state as g


def fresh():
    return g.new_player("Ada")


class StartTests(unittest.TestCase):
    def test_t1_new_game_starts_at_beach_with_full_energy_and_empty_bag(self):
        p = fresh()
        self.assertEqual(p["location"], "Beach")
        self.assertEqual(p["energy"], g.ENERGY_START)
        self.assertEqual(p["inventory"], [])
        self.assertEqual(p["turns"], 0)


class InputSafetyTests(unittest.TestCase):
    def test_t2_invalid_command_leaves_state_unchanged(self):
        p = fresh()
        before = dict(p, inventory=list(p["inventory"]))
        # Moving somewhere that is not connected is the rule-level "invalid input".
        result = g.move(p, "Lighthouse")
        self.assertFalse(result["ok"])
        self.assertEqual(p, before)


class MovementTests(unittest.TestCase):
    def test_t3_legal_move_changes_location_and_costs_one_energy(self):
        p = fresh()
        result = g.move(p, "Jungle")
        self.assertTrue(result["ok"])
        self.assertEqual(p["location"], "Jungle")
        self.assertEqual(p["energy"], g.ENERGY_START - 1)

    def test_t4_wrong_direction_is_free(self):
        p = fresh()
        self.assertFalse(g.move(p, "Cave")["ok"])
        self.assertEqual(p["energy"], g.ENERGY_START)

    def test_dark_cave_entry_costs_one_extra(self):
        p = fresh()
        g.move(p, "Jungle")
        energy_before = p["energy"]
        result = g.move(p, "Cave")
        self.assertEqual(p["energy"], energy_before - 1)
        self.assertIn("bark your shins", result["message"])


class ItemTests(unittest.TestCase):
    def test_t5_rope_collected_once(self):
        p = fresh()
        g.move(p, "Jungle")
        self.assertTrue(g.search(p)["ok"])
        self.assertIn("rope", p["inventory"])
        again = g.search(p)
        self.assertFalse(again["ok"])
        self.assertEqual(p["inventory"].count("rope"), 1)

    def test_lantern_needs_a_blind_search_in_the_dark_and_costs_energy(self):
        p = fresh()
        g.move(p, "Jungle")
        g.move(p, "Cave")
        before = p["energy"]
        result = g.search(p)
        self.assertTrue(result["ok"])
        self.assertIn("lantern", p["inventory"])
        self.assertEqual(p["energy"], before - 1)

    def test_breadfruit_climb_once_then_eat_restores_two(self):
        p = fresh()
        g.move(p, "Jungle")
        self.assertTrue(g.climb(p)["ok"])
        self.assertIn("breadfruit", p["inventory"])
        self.assertFalse(g.climb(p)["ok"])
        g.move(p, "Cave")           # spend a little so eating is not wasted
        energy = p["energy"]
        self.assertTrue(g.eat(p)["ok"])
        self.assertEqual(p["energy"], min(g.ENERGY_START, energy + 2))
        self.assertNotIn("breadfruit", p["inventory"])
        self.assertFalse(g.eat(p)["ok"])


class GateTests(unittest.TestCase):
    def test_t6_bridge_needs_rope(self):
        p = fresh()
        for target in ("Jungle", "Cave", "Old Bridge"):
            g.move(p, target)
        result = g.cross_bridge(p)
        self.assertFalse(result["ok"])
        self.assertEqual(p["location"], "Old Bridge")

    def test_t7_beacon_needs_lantern(self):
        p = fresh()
        g.move(p, "Jungle")
        g.search(p)
        g.move(p, "Cave")
        g.move(p, "Old Bridge")
        g.cross_bridge(p)
        result = g.light_beacon(p)
        self.assertFalse(result["ok"])
        self.assertFalse(p["won"])

    def test_beacon_needs_one_energy_left(self):
        p = fresh()
        p["location"] = "Lighthouse"
        p["inventory"] = ["lantern"]
        p["energy"] = 0
        result = g.light_beacon(p)
        self.assertFalse(result["ok"])
        self.assertIn("One energy", result["message"])


class EconomyTests(unittest.TestCase):
    def test_t8_the_winning_line_requires_the_breadfruit(self):
        p = fresh()
        g.move(p, "Jungle"); g.search(p); g.climb(p); g.eat(p)
        g.move(p, "Cave"); g.search(p)
        g.move(p, "Old Bridge"); g.cross_bridge(p)
        result = g.light_beacon(p)
        self.assertTrue(result["ok"])
        self.assertTrue(p["won"])
        self.assertEqual(p["energy"], 0)

    def test_t8b_without_the_breadfruit_the_line_dies_at_the_bridge(self):
        p = fresh()
        g.move(p, "Jungle"); g.search(p)
        g.move(p, "Cave"); g.search(p)
        g.move(p, "Old Bridge")
        result = g.cross_bridge(p)
        self.assertEqual(p["energy"], 0)
        self.assertTrue(p["game_over"])
        self.assertFalse(p["won"])

    def test_gull_is_a_gamble_that_kills_a_desperate_player(self):
        p = fresh()
        g.move(p, "Jungle"); g.search(p)
        g.move(p, "Cave"); g.search(p)
        g.move(p, "Old Bridge")
        p["energy"] = 1
        result = g.free_gull(p)
        self.assertTrue(p["game_over"])
        self.assertFalse(p["won"])
        self.assertIn("legs give out", result["message"])

    def test_gull_crossing_is_free_when_affordable(self):
        p = fresh()
        g.move(p, "Jungle"); g.search(p); g.climb(p); g.eat(p)
        g.move(p, "Cave"); g.search(p)
        g.move(p, "Old Bridge")
        self.assertTrue(g.free_gull(p)["ok"])
        energy = p["energy"]
        g.cross_bridge(p)
        self.assertEqual(p["energy"], energy)

    def test_t9_running_out_of_energy_loses(self):
        p = fresh()
        for target in ("Jungle", "Beach", "Jungle", "Beach"):
            g.move(p, target)
        self.assertEqual(p["energy"], 1)
        g.move(p, "Jungle")
        self.assertEqual(p["energy"], 0)
        self.assertTrue(p["game_over"])
        self.assertFalse(p["won"])

    def test_energy_never_goes_negative_even_with_the_wade_trap(self):
        p = fresh()
        p["energy"] = 1
        g.risky_crossing(p)
        self.assertEqual(p["energy"], 0)
        self.assertTrue(p["game_over"])


class TideTests(unittest.TestCase):
    def test_leaving_the_beach_late_costs_double(self):
        p = fresh()
        p["turns"] = g.TIDE_AFTER_TURNS   # dawdled: the tide is already in
        result = g.move(p, "Jungle")
        self.assertEqual(p["energy"], g.ENERGY_START - 2)
        self.assertIn("tide", result["message"].lower())

    def test_leaving_the_beach_early_costs_one(self):
        p = fresh()
        g.move(p, "Jungle")
        self.assertEqual(p["energy"], 4)

    def test_tide_warning_is_exposed_in_status(self):
        p = fresh()
        for _ in range(g.TIDE_AFTER_TURNS - 1):
            p["turns"] += 1
        self.assertTrue(g.status(p)["tide"])


class TerminalTests(unittest.TestCase):
    def test_t10_replay_resets_everything(self):
        p = fresh()
        g.move(p, "Jungle"); g.search(p)
        p["game_over"] = True
        q = g.new_player("Ada")
        self.assertEqual((q["location"], q["energy"], q["inventory"], q["turns"]),
                         ("Beach", g.ENERGY_START, [], 0))
        self.assertNotEqual(q["inventory"], p["inventory"])

    def test_no_action_works_after_game_over(self):
        p = fresh()
        p["game_over"] = True
        for action in (lambda: g.move(p, "Jungle"), lambda: g.search(p), lambda: g.climb(p),
                       lambda: g.eat(p), lambda: g.cross_bridge(p), lambda: g.light_beacon(p),
                       lambda: g.free_gull(p), lambda: g.risky_crossing(p)):
            self.assertFalse(action()["ok"])
        self.assertEqual(p["location"], "Beach")


class ArtTests(unittest.TestCase):
    def test_every_location_has_art_and_a_fallback_exists(self):
        for spot in ("Beach", "Jungle", "Cave", "Old Bridge", "Lighthouse"):
            self.assertTrue(art.scene(spot).strip())
        self.assertIn("nowhere", art.scene("nowhere"))

    def test_win_and_lose_art_exist(self):
        self.assertIn("BEACON", art.WIN)
        self.assertIn("island", art.LOSE)


class ImmutabilityTests(unittest.TestCase):
    def test_status_does_not_mutate(self):
        p = fresh()
        before = dict(p, inventory=list(p["inventory"]))
        snap = g.status(p)
        snap["inventory"].append("cheat")
        self.assertEqual(p, before)


if __name__ == "__main__":
    unittest.main()
