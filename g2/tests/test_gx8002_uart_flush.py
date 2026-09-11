# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_flush import verify
class UartFlushTest(unittest.TestCase):
    def test_decoded_completion_and_stall(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],160)
        self.assertEqual(result['stalled_prefixes'],40)
        self.assertTrue(result['candidate']['fits'])
        self.assertTrue(result['source_admitted'])
if __name__=='__main__':unittest.main()
