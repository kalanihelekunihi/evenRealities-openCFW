# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_configure import verify


class UartConfigureFifoTest(unittest.TestCase):
    def test_decoded_fifo_composition(self):
        result = verify(composed_fifo=True)
        self.assertEqual(result['cases'], 1200)
        self.assertEqual(result['arithmetic_cases'], 1000)
        self.assertEqual(result['fifo_executions'], 2400)
        self.assertTrue(result['composed_fifo'])
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
