# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_complete_flush import verify
class UartTransmitCompleteFlushTest(unittest.TestCase):
    def test_drain_gates_callback_delivery(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],108)
        self.assertEqual(result['stalled_prefixes'],36)
if __name__=='__main__':unittest.main()
