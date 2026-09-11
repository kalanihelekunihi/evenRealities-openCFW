# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_owned_defaults import verify
class UartFullClockCompositionTest(unittest.TestCase):
    def test_decoded_clock_to_uart_dispatch(self):
        result=verify(initialize=True,decoded_frequency=True)
        self.assertEqual(result['cases'],40)
        self.assertEqual(result['decoded_control_calls'],80)
        self.assertEqual(result['decoded_frequency_calls'],40)
        self.assertEqual(result['decoded_gate_calls'],40)
        self.assertEqual(result['dispatched_handlers'],40)
if __name__=='__main__':unittest.main()
