# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_snpu_submit_task as v
class SubmitTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=v.verify();cls.old,cls.new=v.programs()
    def test_cases(self):self.assertEqual(self.report['cases'],3360)
    def test_empty_tail(self):
        trace,words=v.execute(self.new,v.ADDRESS,0,v.Case())
        self.assertEqual([x[0] for x in trace if x[0] not in ('read','write')],['set_head','flush_descriptor','enable'])
    def test_running_tail(self):
        case=v.Case(previous=0x20028000,state=1,mutation=True)
        self.assertEqual(v.execute(self.new,v.ADDRESS,0,case),v.expected(case))
    def test_stalled_restart_head(self):
        case=v.Case(previous=0x20028000,state=2,completed=0x40000,head=0x87654321,mutation=True)
        trace,words=v.execute(self.new,v.ADDRESS,0,case)
        self.assertIn(('set_head',0xa0c00100,0x87654321),trace)
    def change(self,op,args):
        code=self.new.copy();pc=next(pc for pc,(o,a,w) in code.items() if o==op);o,a,w=code[pc];code[pc]=(o,args,w);return code
    def test_wrong_command_offset(self):
        case=v.Case()
        self.assertNotEqual(v.execute(self.change('addi','r5, r0, 12'),v.ADDRESS,0,case),v.expected(case))
    def test_wrong_helper(self):
        with self.assertRaisesRegex(ValueError,'target'):v.execute(self.change('bsr','0x10000000'),v.ADDRESS,0,v.Case())
    def test_bad_frame(self):
        with self.assertRaisesRegex(ValueError,'frame'):v.execute(self.change('pop','r15'),v.ADDRESS,0,v.Case())
    def test_wrong_state(self):
        case=v.Case(previous=0x20028000,state=1)
        self.assertNotEqual(v.execute(self.change('cmpnei','r3, 1'),v.ADDRESS,0,case),v.expected(case))
if __name__=='__main__':unittest.main()
