import unittest
from choice import choose_next_scene

CHOICES = ({"next_scene_id": "WIN"}, {"next_scene_id": "LOSS"})


class ChoiceTests(unittest.TestCase):
    def test_second_choice_returns_loss(self):
        self.assertEqual(choose_next_scene(CHOICES, "2"), "LOSS")

    def test_missing_number_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "нет"):
            choose_next_scene(CHOICES, "3")
