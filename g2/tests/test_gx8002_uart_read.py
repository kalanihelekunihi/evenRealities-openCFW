# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_read import verify
class UartReadTest(unittest.TestCase):
    def test_signed_lengths_and_byte_stores(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],84)
        self.assertTrue(result['candidate']['fits'])
if __name__=='__main__':unittest.main()
