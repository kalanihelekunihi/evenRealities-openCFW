# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_dma_cache import verify
class UartTransmitDmaCacheTest(unittest.TestCase):
    def test_clean_commands_precede_selection(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],336)
        self.assertEqual(result['decoded_cache_calls'],336)
if __name__=='__main__':unittest.main()
