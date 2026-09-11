# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_initialize import verify
class UartInitializeTest(unittest.TestCase):
    def test_clock_rounding_and_calls(self):
        result=verify()
        self.assertEqual(result['cases'],1080)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
