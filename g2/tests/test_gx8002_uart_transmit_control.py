# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_control import verify
class UartTransmitControlTest(unittest.TestCase):
    def test_start_stop_order_and_irq_token(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],192)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
