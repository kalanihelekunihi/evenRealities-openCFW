# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_transfer import verify
class UartTransmitDmaTransferTest(unittest.TestCase):
    def test_nested_transfer_and_error_semantics(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],144)
        self.assertEqual(result['decoded_transfer_calls'],96)
        self.assertEqual(result['decoded_cache_calls'],48)
if __name__=='__main__':unittest.main()
