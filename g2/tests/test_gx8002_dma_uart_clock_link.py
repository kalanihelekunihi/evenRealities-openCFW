# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_dma_uart_clock_link import verify

class LinkedClockTest(unittest.TestCase):
    def test_gate_and_lookup_execute_together(self):
        result=verify()
        self.assertEqual(result['cases'],16864)
        self.assertFalse(result['hardware_qualified'])

if __name__=='__main__':
    unittest.main()
