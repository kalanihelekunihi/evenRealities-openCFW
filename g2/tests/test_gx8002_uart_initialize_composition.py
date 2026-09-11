# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_owned_defaults import verify
class UartInitializeCompositionTest(unittest.TestCase):
    def test_initializer_to_configuration_and_dispatch(self):
        result=verify(initialize=True)
        self.assertEqual(result['cases'],24)
        self.assertEqual(result['decoded_gate_calls'],24)
        self.assertTrue(result['initialization_composed'])
        self.assertEqual(result['dispatched_handlers'],24)
if __name__=='__main__':unittest.main()
