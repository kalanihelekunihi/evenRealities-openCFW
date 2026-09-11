# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_write_relocated import verify
class UartWriteRelocatedTest(unittest.TestCase):
    def test_source_linked_nested_transmit(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],108)
        self.assertEqual(result['stalled_prefixes'],30)
if __name__=='__main__':unittest.main()
