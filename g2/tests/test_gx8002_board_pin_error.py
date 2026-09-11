# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_error import validate


class BoardPinErrorTests(unittest.TestCase):
    def test_exact_text(self):
        validate(b'pin %d function conflict !\n\0')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):
            validate(b'pin %d function conflict !\n')

    def test_unsigned_format_rejected(self):
        with self.assertRaises(ValueError):
            validate(b'pin %u function conflict !\n\0')
