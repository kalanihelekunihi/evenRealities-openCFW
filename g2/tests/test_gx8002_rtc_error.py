# SPDX-License-Identifier: MIT
import unittest
from tools.verify_gx8002_rtc_error import validate

class RtcDiagnosticTests(unittest.TestCase):
    def test_exact_diagnostic(self):
        validate(b'RTC prescaler error!\n\0')

    def test_missing_terminator_rejected(self):
        with self.assertRaisesRegex(ValueError,'terminator'):validate(b'RTC prescaler error!\n')

    def test_missing_newline_rejected(self):
        with self.assertRaisesRegex(ValueError,'terminator'):validate(b'RTC prescaler error!\0')

if __name__=='__main__':unittest.main()
