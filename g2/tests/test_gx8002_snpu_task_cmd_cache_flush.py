# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_snpu_task_cmd_cache_flush as v
class DescriptorCacheTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.old,cls.new=v.programs()
    def test_cases(self):self.assertEqual(self.report['cases'],2485)
    def test_ranges_and_wrap(self):
        for pointer in (0x20027360,0xfffffff8):
            calls,result=v.execute(self.new,v.ADDRESS,0,pointer,0)
            self.assertEqual(calls,[(v.TARGET,pointer,8),(v.TARGET,(pointer+16)&v.MASK,108)])
    def mutated(self,op,args):
        code=self.new.copy();pc=next(pc for pc,(o,a,w) in code.items() if o==op)
        o,a,w=code[pc];code[pc]=(o,args,w);return code
    def test_wrong_length(self):
        code=self.mutated('movi','r1, 12')
        self.assertNotEqual(v.execute(code,v.ADDRESS,0,0x20027360,0),v.execute(self.new,v.ADDRESS,0,0x20027360,0))
    def test_wrong_block_offset(self):
        code=self.mutated('addi','r0, r4, 12')
        self.assertNotEqual(v.execute(code,v.ADDRESS,0,0x20027360,0),v.execute(self.new,v.ADDRESS,0,0x20027360,0))
    def test_wrong_target(self):
        with self.assertRaisesRegex(ValueError,'target'):v.execute(self.mutated('bsr','0x10025668'),v.ADDRESS,0,0,0)
    def test_frame_rejected(self):
        with self.assertRaisesRegex(ValueError,'frame'):v.execute(self.mutated('pop','r15'),v.ADDRESS,0,0,0)
    def test_pointer_preserved_across_clobber(self):
        code=self.mutated('mov','r4, r1')
        self.assertNotEqual(v.execute(code,v.ADDRESS,0,0x20027360,0),v.execute(self.new,v.ADDRESS,0,0x20027360,0))
if __name__=='__main__':unittest.main()
