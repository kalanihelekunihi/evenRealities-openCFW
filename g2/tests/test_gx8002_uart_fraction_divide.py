# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_fraction_divide import verify


class UartFractionDivideTest(unittest.TestCase):
    def test_decoded_fraction_arithmetic_chain(self):
        result = verify()
        self.assertEqual(result['input_cases'], 2234)
        self.assertEqual(result['executions'], 4468)
        self.assertEqual(result['chain_executions'], 4468)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
