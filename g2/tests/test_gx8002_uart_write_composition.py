# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_write_composition import verify
class UartWriteCompositionTest(unittest.TestCase):
    def test_nested_transmit_and_stalled_prefix(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],108)
        self.assertEqual(result['stalled_prefixes'],30)
if __name__=='__main__':unittest.main()
