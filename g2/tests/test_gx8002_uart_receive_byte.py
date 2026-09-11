# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_receive_byte import verify
class UartReceiveByteTest(unittest.TestCase):
    def test_polling_and_full_width_read(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],800)
        self.assertTrue(result['candidate']['fits'])
if __name__=='__main__':unittest.main()
