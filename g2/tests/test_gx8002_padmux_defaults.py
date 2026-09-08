# SPDX-License-Identifier: MIT
import unittest
from tools.verify_gx8002_padmux_defaults import validate

class PadmuxDefaultsTests(unittest.TestCase):
    def test_semantic_policy(self):
        validate(bytes(v for pin in range(32) for v in (pin,0)))

    def test_wrong_pin_and_function_rejected(self):
        for offset in (0,1,62,63):
            data=bytearray(v for pin in range(32) for v in (pin,0));data[offset]^=1
            with self.assertRaisesRegex(ValueError,'policy'):validate(data)

    def test_extra_pin_rejected(self):
        with self.assertRaisesRegex(ValueError,'length'):validate(bytes(v for pin in range(33) for v in (pin,0)))

if __name__=='__main__':unittest.main()
