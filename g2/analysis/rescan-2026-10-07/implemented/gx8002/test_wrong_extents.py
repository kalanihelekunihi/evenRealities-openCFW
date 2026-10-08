#!/usr/bin/env python3
"""Positive and wrong-boundary tests for verify_model.py."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import verify_model


class ModelExtentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.codec = verify_model.DEFAULT_CODEC.read_bytes()

    def test_locked_image_and_extents_pass(self):
        result = verify_model.verify(self.codec)
        self.assertEqual(result["image_a_model"]["commands"]["size"], 9164)
        self.assertEqual(result["image_a_model"]["weights"]["size"], 120800)
        self.assertEqual(result["image_a_model"]["weights"]["segment_extent"],
                         [0x11BD0, 0x2F3B0])

    def assert_rejected(self, **kwargs):
        with self.assertRaises(verify_model.VerificationError):
            verify_model.verify(self.codec, **kwargs)

    def test_wrong_command_start_rejected(self):
        self.assert_rejected(command_start=0xF800)

    def test_wrong_command_length_rejected(self):
        self.assert_rejected(command_size=9160)

    def test_wrong_weight_start_rejected(self):
        self.assert_rejected(weight_start=0x11BCC)

    def test_wrong_weight_length_rejected(self):
        self.assert_rejected(weight_size=120796)


if __name__ == "__main__":
    unittest.main()
