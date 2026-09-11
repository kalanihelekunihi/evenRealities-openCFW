# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_board_pin_defaults import validate


class BoardPinDefaultsTests(unittest.TestCase):
    def policy(self):return bytearray(v for pin in range(13) for v in (pin,0 if pin==2 else 1))

    def test_policy(self):validate(self.policy())

    def test_pin_two_special_function(self):
        data=self.policy();data[5]=1
        with self.assertRaises(ValueError):validate(data)

    def test_missing_pin(self):
        with self.assertRaises(ValueError):validate(self.policy()[:-2])

    def test_order(self):
        data=self.policy();data[0]=1
        with self.assertRaises(ValueError):validate(data)
