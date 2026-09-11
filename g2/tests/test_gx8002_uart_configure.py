# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_configure import verify


class UartConfigureTest(unittest.TestCase):
    def test_decoded_ordered_configuration(self):
        result = verify()
        self.assertEqual(result['cases'], 400)
        self.assertEqual(result['arithmetic_cases'], 333)
        self.assertFalse(result['source_admitted'])
        self.assertFalse(result['hardware_qualified'])


if __name__ == '__main__':
    unittest.main()
