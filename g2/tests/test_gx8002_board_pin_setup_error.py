# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_setup_error import validate


class BoardPinSetupErrorTests(unittest.TestCase):
    def test_exact_layout(self):
        validate(b'!!!pin set error!\n Please check Board Options!!!\0')

    def test_missing_leading_space(self):
        with self.assertRaises(ValueError):
            validate(b'!!!pin set error!\nPlease check Board Options!!!\0')

    def test_extra_final_newline(self):
        with self.assertRaises(ValueError):
            validate(b'!!!pin set error!\n Please check Board Options!!!\n\0')
