# SPDX-License-Identifier: MIT
import unittest
from verify_gx8002_gsensor_workstate import build,programs,execute,expected,ADDRESS


class GsensorStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):build();cls.code=programs()[1]

    def test_changed_state_returned(self):
        self.assertEqual(execute(self.code,ADDRESS,1,2,37),expected(1,2))

    def test_printf_result_ignored(self):
        self.assertEqual(execute(self.code,ADDRESS,0xffffffff,0,0xffffffff),expected(0xffffffff,0))

    def test_wrong_second_read_address(self):
        code=self.code.copy();pc=max(p for p,row in code.items() if row[0]=='ld.w')
        code[pc]=('ld.w','r0, (r4, 0x74)',2)
        with self.assertRaisesRegex(ValueError,'address'):execute(code,ADDRESS,1,2,0)

    def test_printf_hook_first_value(self):
        calls=[]
        def output(pointer,value):calls.append((pointer,value));return 0xffffffff
        self.assertEqual(execute(self.code,ADDRESS,1,2,0,printf_hook=output),expected(1,2))
        self.assertEqual(calls,[(0x1020adaa,1)])
