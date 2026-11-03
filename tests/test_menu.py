"""The user-facing layer: numbered choices, forgiving input, gentle tips.

Run with: python -m unittest discover -s tests -v
Pure functions only; no input() and no printing is exercised here.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game import menu
from game import state as g


def fresh():
    return g.new_player("Tester")


def labels(actions):
    return [a["label"] for a in actions]


class AvailableActionsTests(unittest.TestCase):
    def test_beach_offers_only_movement_and_utilities(self):
        self.assertEqual(labels(menu.available_actions(fresh()))[0], "Go to Jungle")
        self.assertNotIn("search", [a["verb"] for a in menu.available_actions(fresh())])

    def test_jungle_offers_search_and_climb(self):
        p = fresh()
        g.move(p, "Jungle")
        verbs = [a["verb"] for a in menu.available_actions(p)]
        self.assertIn("search", verbs)
        self.assertIn("climb", verbs)

    def test_search_and_climb_disappear_once_done(self):
        p = fresh()
        g.move(p, "Jungle")
        g.search(p)
        verbs = [a["verb"] for a in menu.available_actions(p)]
        self.assertNotIn("search", verbs)
        g.climb(p)
        verbs = [a["verb"] for a in menu.available_actions(p)]
        self.assertNotIn("climb", verbs)
        self.assertIn("eat", verbs)

    def test_bridge_offers_gull_and_cross(self):
        p = fresh()
        p["location"] = "Old Bridge"
        p["inventory"] = ["rope"]
        verbs = [a["verb"] for a in menu.available_actions(p)]
        self.assertIn("free", verbs)
        self.assertIn("cross", verbs)

    def test_lighthouse_offers_light(self):
        p = fresh()
        p["location"] = "Lighthouse"
        self.assertIn("light", [a["verb"] for a in menu.available_actions(p)])

    def test_game_over_menu_is_minimal(self):
        p = fresh()
        g._finish(p, False)
        self.assertEqual(labels(menu.available_actions(p)), ["Look around", "Quit"])


class ChooseTests(unittest.TestCase):
    def test_number_selects_the_matching_choice(self):
        p = fresh()
        action, message = menu.choose(p, "1")
        self.assertEqual((action["verb"], action["arg"], message), ("go", "Jungle", ""))

    def test_number_out_of_range_is_refused_with_guidance(self):
        action, message = menu.choose(fresh(), "99")
        self.assertIsNone(action)
        self.assertIn("1 to", message)

    def test_digits_alone_can_win_the_game(self):
        p = fresh()
        script = ["1", "3", "3", "3", "2", "3", "2", "3", "2"]
        for raw in script:
            action, _ = menu.choose(p, raw)
            self.assertIsNotNone(action, "choice {!r} was not understood".format(raw))
            verb = action["verb"]
            if verb == "go":
                g.move(p, action["arg"])
            elif verb == "search":
                g.search(p)
            elif verb == "climb":
                g.climb(p)
            elif verb == "eat":
                g.eat(p)
            elif verb == "cross":
                g.cross_bridge(p)
            elif verb == "light":
                g.light_beacon(p)
        self.assertTrue(p["won"], "digits alone failed to win")

    def test_case_spacing_and_bare_place_names_work(self):
        for raw in ("GO JUNGLE", "go   jungle", "  Jungle ", "jungle", "walk to jungle"):
            action, _ = menu.choose(fresh(), raw)
            self.assertIsNotNone(action, raw)
            self.assertEqual((action["verb"], action["arg"]), ("go", "Jungle"))

    def test_short_aliases_work(self):
        p = fresh()
        for raw, verb in (("i", "bag"), ("bag", "bag"), ("h", "help"), ("?", "help"),
                          ("q", "quit"), ("l", "look")):
            action, _ = menu.choose(p, raw)
            self.assertEqual(action["verb"], verb, raw)

    def test_unknown_input_names_the_problem_and_the_fix(self):
        action, message = menu.choose(fresh(), "fly away")
        self.assertIsNone(action)
        self.assertIn("I don't know", message)
        self.assertIn("help", message)

    def test_unreachable_move_lists_what_is_reachable(self):
        action, message = menu.choose(fresh(), "go lighthouse")
        self.assertIsNone(action)
        self.assertIn("Jungle", message)

    def test_blank_input_is_silent(self):
        self.assertEqual(menu.choose(fresh(), "   "), (None, ""))


class TipTests(unittest.TestCase):
    def test_context_tips_change_with_location(self):
        p = fresh()
        beach = menu.tip(p)
        p["location"] = "Old Bridge"
        bridge = menu.tip(p)
        self.assertIn("tide", beach.lower())
        self.assertIn("rope", bridge.lower())
        self.assertNotEqual(beach, bridge)

    def test_fumbling_beats_context(self):
        self.assertIn("number", menu.tip(fresh(), fumbles=2).lower())

    def test_no_tip_after_game_over(self):
        p = fresh()
        g._finish(p, False)
        self.assertEqual(menu.tip(p), "")


if __name__ == "__main__":
    unittest.main()
