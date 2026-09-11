# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_uart_flush_relocated import verify
class UartFlushRelocatedTest(unittest.TestCase):
    def test_source_descriptor_drain_wait(self):
        result=verify()
        self.assertEqual(result['decoded_cases'],160)
        self.assertEqual(result['candidate']['unresolved_symbols'],[])
if __name__=='__main__':unittest.main()
