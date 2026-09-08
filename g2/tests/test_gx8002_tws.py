# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_tws import ROOT,decode,execute,expected
class TwsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/tws-candidate.disassembly.txt').read_text())
    def run_case(self,code,previous=65535,wakeup=2,result=0):return execute(code,0x10208670,0,previous,wakeup,result,0xffffffff)
    def test_resume(self):self.assertEqual(self.run_case(self.code),expected(65535,2,0))
    def test_failure_has_no_standby_writes(self):self.assertEqual(self.run_case(self.code,0,0,1),expected(0,0,1))
    def test_wrong_queue_size(self):
        c=self.code.copy();c[0x10208676]=('movi','r2, 64',2)
        self.assertNotEqual(self.run_case(c),expected(65535,2,0))
    def test_wrong_wakeup_threshold(self):
        c=self.code.copy();c[0x1020869a]=('cmphsi','r4, 3',2)
        self.assertNotEqual(self.run_case(c),expected(65535,2,0))
    def test_wrong_countdown(self):
        c=self.code.copy();c[0x102086be]=('movi','r2, 18',2)
        self.assertNotEqual(self.run_case(c),expected(65535,2,0))
    def test_unknown_helper(self):
        c=self.code.copy();c[0x10208682]=('bsr','0x10000000',4)
        with self.assertRaisesRegex(ValueError,'unknown TWS helper'):self.run_case(c)
    def test_wrong_pop(self):
        c=self.code.copy();c[0x102086b2]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
