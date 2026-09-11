# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_transmit_complete_leaves import verify
class UartTransmitCompleteLeavesTest(unittest.TestCase):
    def test_release_deallocation_and_drain(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],2304)
        self.assertGreater(result['decoded_gate_calls'],0)
if __name__=='__main__':unittest.main()
