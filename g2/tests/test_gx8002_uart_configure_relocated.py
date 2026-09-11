# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_configure_relocated import verify


class UartConfigureRelocatedTest(unittest.TestCase):
    def test_decoded_source_cluster(self):
        result = verify()
        self.assertEqual(result['cases'], 1200)
        self.assertEqual(result['arithmetic_cases'], 1000)
        self.assertEqual(result['irq_executions'], 2400)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
