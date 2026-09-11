# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_callback import verify
class UartTransmitDmaCallbackTest(unittest.TestCase):
    def test_registration_slots_and_transfer_order(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],48)
        self.assertEqual(result['decoded_callback_calls'],32)
if __name__=='__main__':unittest.main()
