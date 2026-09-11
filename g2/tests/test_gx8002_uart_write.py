# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_write import verify
class UartWriteTest(unittest.TestCase):
    def test_signed_lengths_and_byte_loads(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],84)
        self.assertTrue(result['candidate']['fits'])
if __name__=='__main__':unittest.main()
