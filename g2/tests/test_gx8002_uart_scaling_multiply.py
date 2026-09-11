# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_scaling_multiply import verify


class UartScalingMultiplyTest(unittest.TestCase):
    def test_stock_and_upstream_decoded_scaling(self):
        result = verify()
        self.assertEqual(result['integer_helper_cases'], 2097)
        self.assertEqual(result['input_cases'], 6180)
        self.assertEqual(result['executions'], 12360)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
