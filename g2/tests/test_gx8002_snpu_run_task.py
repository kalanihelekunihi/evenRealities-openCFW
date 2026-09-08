# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_snpu_run_task as v
class RunTaskTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.report=v.verify();cls.old,cls.new=v.programs()
    def test_cases(self):self.assertEqual(self.report['cases'],1802)
    def test_callback_private_patterns(self):
        for value in (0,0xffffffff,*[1<<i for i in range(32)]):
            case=v.Case(callback=value,private=value,state=2,mutation=True)
            self.assertEqual(v.execute(self.new,v.ADDRESS,0,case),v.expected(case))
    def test_all_rejections(self):
        for case in (v.Case(task=0),v.Case(registers=0),v.Case(start=0,end=9)):
            self.assertEqual(v.execute(self.new,v.ADDRESS,0,case),v.expected(case))
    def changed(self,op,args):
        code=self.new.copy();pc=next(pc for pc,(o,a,w) in code.items() if o==op);o,a,w=code[pc];code[pc]=(o,args,w);return code
    def test_wrong_descriptor(self):
        case=v.Case()
        code=self.new.copy();pc=next(pc for pc,(op,args,w) in code.items() if op=='addi' and args=='r4, r3, 16')
        op,args,w=code[pc];code[pc]=(op,'r4, r3, 12',w)
        self.assertNotEqual(v.execute(code,v.ADDRESS,0,case),v.expected(case))
    def test_wrong_helper(self):
        with self.assertRaisesRegex(ValueError,'target'):v.execute(self.changed('bsr','0x10000000'),v.ADDRESS,0,v.Case(state=2))
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'frame'):v.execute(self.changed('pop','r15'),v.ADDRESS,0,v.Case())
    def test_wrong_write_offset(self):
        case=v.Case()
        self.assertNotEqual(v.execute(self.changed('st.w','r1, (r3, 0x8c)'),v.ADDRESS,0,case),v.expected(case))
if __name__=='__main__':unittest.main()
