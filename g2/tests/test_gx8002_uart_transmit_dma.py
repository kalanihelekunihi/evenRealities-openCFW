# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma import verify
class UartTransmitDmaTest(unittest.TestCase):
    def test_valid_port_stock_source_setup(self):
        self.assertEqual(verify()['decoded_cases'],384)
if __name__=='__main__':unittest.main()
