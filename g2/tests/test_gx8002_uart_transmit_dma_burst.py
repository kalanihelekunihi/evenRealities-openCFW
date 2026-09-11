# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_burst import verify
class UartTransmitDmaBurstTest(unittest.TestCase):
    def test_decoded_burst_fields(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],120)
        self.assertEqual(result['burst_calls'],240)
if __name__=='__main__':unittest.main()
