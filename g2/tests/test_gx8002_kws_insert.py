# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_kws_insert import ROOT,BASE,decode,execute,expected,fixture
class ActivationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/kws-insert-candidate.disassembly.txt').read_text())
    def run_case(self,code,mem,score=0x40000000):return execute(code,0x10208980,0,mem,(55,66,7,0xdeadbeef),score)
    def test_first_match_only(self):
        m=fixture(8,0,0x3f800000);m[BASE+4+20*5]=55;m[BASE+8+20*5]=66
        self.assertEqual(self.run_case(self.code,m),expected(m,(55,66,7,0xdeadbeef),0x40000000))
    def test_signed_zero_does_not_update(self):
        m=fixture(1,0,0x80000000)
        self.assertEqual(self.run_case(self.code,m,0)['memory'],m)
    def test_partial_match_scans_on(self):
        m=fixture(2,1,0x3f800000);m[BASE+8]=66
        self.assertEqual(self.run_case(self.code,m),expected(m,(55,66,7,0xdeadbeef),0x40000000))
    def test_negative_count_logs_without_scan(self):
        m=fixture(0xffffffff,None,0)
        self.assertEqual(self.run_case(self.code,m)['trace'],[['read',BASE,0xffffffff],['printf',0x1020b34f]])
    def test_corrupted_positive_count_not_qualified(self):
        with self.assertRaisesRegex(ValueError,'read outside list'):self.run_case(self.code,fixture(9,None,0))
    def test_reversed_float_comparison(self):
        c=self.code.copy();c[0x102089c6]=('fcmplts','fr0, fr1',4);m=fixture(1,0,0x3f800000)
        self.assertNotEqual(self.run_case(c,m),expected(m,(55,66,7,0xdeadbeef),0x40000000))
    def test_wrong_score_register(self):
        c=self.code.copy();c[0x102089cc]=('fsts','fr1, (r3, 0xc)',4);m=fixture(1,0,0x3f800000)
        self.assertNotEqual(self.run_case(c,m),expected(m,(55,66,7,0xdeadbeef),0x40000000))
    def test_wrong_private_register(self):
        c=self.code.copy();c[0x102089fe]=('str.w','r3, (r13, r3 << 0)',4);m=fixture(0,None,0)
        self.assertNotEqual(self.run_case(c,m),expected(m,(55,66,7,0xdeadbeef),0x40000000))
    def test_wrong_return_frame(self):
        c=self.code.copy();c[0x102089d0]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c,fixture(1,0,0))
if __name__=='__main__':unittest.main()
