# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_console_boundary import execute,programs


class ConsoleBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=programs()[0][1]

    def test_selected_port_and_character(self):
        calls=[]
        trace=execute(self.code,0x102037f0,0x102035b4,10,2,lambda p,c:calls.append((p,c)))
        self.assertEqual(trace,[('read',0x2002731c,2),('uart',2,10)])
        self.assertEqual(calls,[(2,10)])

    def test_wrong_uart_target(self):
        with self.assertRaisesRegex(ValueError,'target'):
            execute(self.code,0x102037f0,0x102035b8,10,0,lambda p,c:None)
