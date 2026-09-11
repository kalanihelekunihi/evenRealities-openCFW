# SPDX-License-Identifier: MIT
import unittest
from execute_gx8002_uart_header_probe import execute
from execute_gx8002_uart_header_stock import execute as stock


class HeaderComparisonTests(unittest.TestCase):
    def test_partial_header_keeps_cursor_when_input_exhausted(self):
        for run in (execute, stock):
            r=run(0,4,b'abc',0)
            self.assertEqual((r['result'],r['count'],r['remaining'],r['consumed_pointer']),(0,7,0,0))
            self.assertEqual(r['header'][4:7],b'abc')
            self.assertEqual(r['crc_calls'],[])

    def test_crc_failure_clears_only_magic_and_resets_counter(self):
        payload=bytes(range(10))+b'xyz'
        for run in (execute, stock):
            r=run(1,4,payload,0)
            self.assertEqual((r['result'],r['count'],r['remaining'],r['consumed_pointer']),
                             (0xffffffff,4,3,10))
            self.assertEqual(r['header'],bytes(4)+payload[:10])

    def test_complete_counter_checks_crc_without_input(self):
        for run in (execute, stock):
            r=run(0,14,b'',0xa5a5a5a5)
            self.assertEqual((r['result'],r['count'],r['remaining']),(1,4,0))
            self.assertEqual(r['crc_calls'],[(0,10)])
