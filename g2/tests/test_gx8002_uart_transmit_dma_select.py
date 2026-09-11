# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_select import verify
class UartTransmitDmaSelectTest(unittest.TestCase):
    def test_channel_allocation_handoff(self):
        self.assertEqual(verify()['decoded_cases'],96)
if __name__=='__main__':unittest.main()
