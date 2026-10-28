import unittest

from storage import state_from_payload


class StorageTests(unittest.TestCase):
    def test_valid_payload_returns_state(self):
        payload = {"current_scene_id": "SCN002", "player": {"hp": 10}}
        self.assertEqual(state_from_payload(payload), ("SCN002", 10))

    def test_text_hp_is_rejected(self):
        payload = {"current_scene_id": "SCN002", "player": {"hp": "10"}}
        with self.assertRaisesRegex(TypeError, "целым числом"):
            state_from_payload(payload)
