# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_entry_relocated import verify

class UartEntryRelocatedTest(unittest.TestCase):
    def test_relocated_context_wrapper(self):
        result = verify()
        self.assertEqual(result['cases'], 48)
        self.assertFalse(result['hardware_qualified'])

if __name__ == '__main__':
    unittest.main()
