# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_cleanup import verify
class UartTransmitDmaCleanupTest(unittest.TestCase):
    def test_invalid_port_releases_without_transfer(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],144)
        self.assertFalse(result['stock_equivalent'])
if __name__=='__main__':unittest.main()
