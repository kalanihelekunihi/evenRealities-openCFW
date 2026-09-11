# SPDX-License-Identifier: MIT
import unittest
from link_gx8002_uart_configure_source import build
class UartInitializeSourceLinkTest(unittest.TestCase):
    def test_clock_and_uart_source_closure(self):
        result=build(include_initialize=True)
        self.assertEqual(result['unresolved_symbols'],[])
        self.assertEqual(len(result['function_addresses']),20)
        self.assertEqual(result['uart_descriptor_bytes'],256)
        self.assertFalse(result['source_admitted'])
if __name__=='__main__':unittest.main()
