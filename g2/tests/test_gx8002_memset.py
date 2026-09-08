# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_memset import ROOT,decode,execute,expected
class MemsetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/memset-candidate.disassembly.txt').read_text())
    def run_case(self,code,address=0x20010001,count=19,value=0x12345678):return execute(code,0x102099cc,address,value,count)
    def test_zero_does_not_store(self):self.assertEqual(self.run_case(self.code,count=0)['trace'],[])
    def test_alignment_and_store_width(self):
        self.assertEqual(self.run_case(self.code),expected(0x20010001,0x12345678,19))
    def test_high_signed_count_has_bounded_tail(self):
        self.assertEqual(len(self.run_case(self.code,address=0x20010000,count=0x80000000)['trace']),3)
    def test_alignment_can_cross_signed_boundary(self):
        got=execute(self.code,0x102099cc,0x20010001,7,0x80000000,prefix=32)
        self.assertEqual(got,expected(0x20010001,7,0x80000000,32));self.assertTrue(got['checkpoint'])
    def test_wrong_byte_mask(self):
        c=self.code.copy();c[0x102099d2]=('mov','r12, r0',2)
        self.assertNotEqual(self.run_case(c),expected(0x20010001,0x12345678,19))
    def test_wrong_word_offset(self):
        c=self.code.copy();c[0x10209a24]=('st.w','r1, (r3, 0x8)',2)
        self.assertNotEqual(self.run_case(c),expected(0x20010001,0x12345678,19))
    def test_wrong_return_register(self):
        c=self.code.copy();c[0x10209a0c]=('mov','r0, r1',2);c[0x10209a0e]=('rts','',2)
        self.assertNotEqual(self.run_case(c,address=0x20010000,count=0)['result'],0x20010000)
    def test_word_store_requires_alignment(self):
        c=self.code.copy();c[0x10209a10]=('st.w','r12, (r3, 0x0)',4)
        with self.assertRaisesRegex(ValueError,'unaligned'):self.run_case(c)
if __name__=='__main__':unittest.main()
