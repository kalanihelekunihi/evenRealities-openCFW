# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_interrupt_stall import verify

class UartInterruptStallTest(unittest.TestCase):
    def test_stalled_transmitter_prefix(self):
        result = verify()
        self.assertEqual(result['cases'], 36)
        self.assertFalse(result['source_admitted'])

if __name__ == '__main__':
    unittest.main()
