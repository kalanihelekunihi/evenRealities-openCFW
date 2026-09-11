# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_interrupt_dispatch import verify


class UartInterruptDispatchTest(unittest.TestCase):
    def test_decoded_dispatch_and_callback_mutations(self):
        result = verify()
        self.assertEqual(result['cases'], 1728)
        self.assertFalse(result['source_admitted'])
        self.assertFalse(result['hardware_qualified'])


if __name__ == '__main__':
    unittest.main()
