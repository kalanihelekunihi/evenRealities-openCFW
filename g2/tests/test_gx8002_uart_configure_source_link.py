# SPDX-License-Identifier: MIT
import unittest
from link_gx8002_uart_configure_source import build


class UartConfigureSourceLinkTest(unittest.TestCase):
    def test_source_function_and_irq_storage_link(self):
        result = build()
        self.assertEqual(result['unresolved_symbols'], [])
        self.assertEqual(result['bss_bytes'], 264)
        self.assertEqual(result['uart_descriptor_bytes'], 256)
        self.assertEqual(result['uart_descriptor_address'], 0x20080000)
        self.assertEqual(len(set(result['function_addresses'].values())), 16)
        self.assertFalse(result['source_admitted'])


if __name__ == '__main__':
    unittest.main()
