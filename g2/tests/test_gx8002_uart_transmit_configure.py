# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_configure import verify
class UartTransmitConfigureTest(unittest.TestCase):
    def test_uart_fields_reach_decoded_configuration(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],28)
        self.assertEqual(result['decoded_bus_calls'],80)
        self.assertEqual(result['decoded_descriptor_calls'],24)
        self.assertEqual(result['decoded_clear_calls'],28)
        self.assertEqual(result['decoded_cache_calls'],24)
if __name__=='__main__':unittest.main()
