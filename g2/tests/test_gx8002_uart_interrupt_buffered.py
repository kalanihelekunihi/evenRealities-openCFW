# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_interrupt_buffered import verify


class UartInterruptBufferedTest(unittest.TestCase):
    def test_decoded_buffers_and_drain(self):
        result = verify()
        self.assertEqual(result['cases'], 1152)
        self.assertEqual(result['poll_reads'], 2560)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
