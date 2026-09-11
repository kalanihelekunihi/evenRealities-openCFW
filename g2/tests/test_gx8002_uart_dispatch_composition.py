# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_dispatch_composition import verify

class UartDispatchCompositionTest(unittest.TestCase):
    def test_relocated_dispatch_to_uart(self):
        result = verify()
        self.assertEqual(result['cases'], 72)
        self.assertFalse(result['source_admitted'])

if __name__ == '__main__':
    unittest.main()
