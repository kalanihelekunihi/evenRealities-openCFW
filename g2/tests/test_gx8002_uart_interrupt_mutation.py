# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_interrupt_mutation import verify


class UartInterruptMutationTest(unittest.TestCase):
    def test_receive_completion_changes_transmit_state(self):
        result = verify()
        self.assertEqual(result['cases'], 96)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
