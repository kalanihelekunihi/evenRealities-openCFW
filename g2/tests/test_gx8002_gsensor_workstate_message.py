# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_gsensor_workstate_message import validate


class GsensorMessageTests(unittest.TestCase):
    def test_text(self):validate(b'gsensor_workstate =%d\n\0')

    def test_missing_space(self):
        with self.assertRaises(ValueError):validate(b'gsensor_workstate=%d\n\0')

    def test_unsigned_conversion(self):
        with self.assertRaises(ValueError):validate(b'gsensor_workstate =%u\n\0')
