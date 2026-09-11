# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_initialize_error import validate


class InitializerErrorTests(unittest.TestCase):
    def test_text(self):validate(b'pin %d set error!\n\0')

    def test_unsigned_conversion_rejected(self):
        with self.assertRaises(ValueError):validate(b'pin %u set error!\n\0')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):validate(b'pin %d set error!\n')
