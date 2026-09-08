# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_max_list import ROOT,decode,execute,expected,COUNT,POINTER,ALTERNATE
class MaxListTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/max-list-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,changes=None):return execute(self.code if code is None else code,0x10208880,0,0xffffffff,changes or {})
    def test_initial_state_overwritten(self):self.assertEqual(self.run_case(),expected(0xffffffff,{}))
    def test_header_can_stop_listing(self):
        changes={0:[(COUNT,0)]};result=self.run_case(changes=changes)
        self.assertEqual(result,expected(0xffffffff,changes));self.assertEqual(sum(t[0]=='printf' for t in result[0]),1)
    def test_midrow_shrink_finishes_row(self):
        changes={1:[(COUNT,0),(POINTER,ALTERNATE)]};result=self.run_case(changes=changes)
        self.assertEqual(result,expected(0xffffffff,changes));self.assertEqual(sum(t[0]=='printf' for t in result[0]),5)
    def test_stale_pointer_rejected(self):
        changes={1:[(POINTER,ALTERNATE)]};c=self.code.copy();c[0x102088b6]=('lrw','r3, 0x20026c7c',2)
        self.assertNotEqual(self.run_case(c,changes),expected(0xffffffff,changes))
    def test_cached_count_rejected(self):
        changes={0:[(COUNT,0)]};c=self.code.copy();c[0x102088a4]=('movi','r3, 2',2)
        self.assertNotEqual(self.run_case(c,changes),expected(0xffffffff,changes))
    def test_wrong_field_rejected(self):
        c=self.code.copy();c[0x102088bc]=('ld.w','r1, (r3, 0x4c)',2)
        self.assertNotEqual(self.run_case(c),expected(0xffffffff,{}))
    def test_wrong_stride_rejected(self):
        c=self.code.copy();c[0x102088d6]=('addi','r5, 84',2)
        with self.assertRaisesRegex(ValueError,'invalid read/storage'):self.run_case(c)
    def test_wrong_frame_rejected(self):
        c=self.code.copy();c[0x102088aa]=('pop','r4-r9, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
    def test_invalid_count_not_clamped(self):
        with self.assertRaisesRegex(ValueError,'outside valid storage'):self.run_case(changes={0:[(COUNT,3)]})
if __name__=='__main__':unittest.main()
