# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_dcache_clean_range as v
class CacheCleanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.old,cls.new=v.programs()
    def test_cases(self):
        self.assertEqual(self.report['cases'],12864)
        self.assertEqual(self.report['prefix_cases'],144)
    def test_negative_and_zero(self):
        for size in (0,0xffffffff,0x80000000):self.assertEqual(v.execute(self.new,v.ADDRESS,0x20027350,size,0),([],True))
    def test_unaligned_does_not_expand_size(self):
        self.assertEqual(v.execute(self.new,v.ADDRESS,0x2002735f,16,0),([(v.PORT,0x20027358)],True))
    def test_wrap(self):
        self.assertEqual(v.execute(self.new,v.ADDRESS,0xfffffff8,17,0),([(v.PORT,0xfffffff8),(v.PORT,8)],True))
    def change(self,op,args):
        code=self.new.copy();pc=next(pc for pc,(o,a,w) in code.items() if o==op);o,a,w=code[pc];code[pc]=(o,args,w);return code
    def test_wrong_operation(self):
        self.assertNotEqual(v.execute(self.change('ori','r3, r0, 10'),v.ADDRESS,0,16,0),(v.expected(0,16),True))
    def test_wrong_port(self):
        with self.assertRaisesRegex(ValueError,'MMIO'):v.execute(self.change('lrw','r2, 0xe000f010'),v.ADDRESS,0,128,0)
    def test_wrong_unrolled_stride(self):
        self.assertNotEqual(v.execute(self.change('addi','r0, r3, 32'),v.ADDRESS,0,128,0),(v.expected(0,128),True))
    def test_abi(self):
        code=self.new.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='rts');code[pc]=('movi','r4, 0',2);code[pc+2]=('rts','',2)
        with self.assertRaisesRegex(ValueError,'ABI'):v.execute(code,v.ADDRESS,0,0,0)
if __name__=='__main__':unittest.main()
