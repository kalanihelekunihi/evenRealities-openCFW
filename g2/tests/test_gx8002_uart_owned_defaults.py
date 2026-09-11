# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_owned_defaults import verify

class UartOwnedDefaultsTest(unittest.TestCase):
    def test_configuration_uses_source_descriptors(self):
        result = verify()
        self.assertEqual(result['cases'], 24)
        self.assertEqual(result['dispatched_handlers'], 24)
        self.assertFalse(result['source_admitted'])

if __name__ == '__main__':
    unittest.main()
