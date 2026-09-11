# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_configure import verify


class UartConfigureIrqTest(unittest.TestCase):
    def test_decoded_irq_composition(self):
        result = verify(composed_fifo=True, composed_irq=True)
        self.assertEqual(result['cases'], 1200)
        self.assertEqual(result['irq_executions'], 2400)
        self.assertEqual(result['fifo_executions'], 2400)
        self.assertTrue(result['composed_irq'])
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
