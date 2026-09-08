# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_max_initialize import ROOT,decode,execute,expected
class MaxInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/max-initialize-candidate.disassembly.txt').read_text())
    def run_case(self,code,count=2):return execute(code,0x10208944,0,count,0xffffffff)
    def test_expected_count_skips_logging(self):self.assertEqual(self.run_case(self.code),expected(2))
    def test_wrong_count_still_initializes(self):self.assertEqual(self.run_case(self.code,0xffffffff),expected(0xffffffff))
    def test_wrong_expected_count(self):
        c=self.code.copy();c[0x1020894a]=('cmpnei','r3, 3',2)
        self.assertNotEqual(self.run_case(c),expected(2))
    def test_wrong_count_address(self):
        c=self.code.copy();c[0x10208948]=('ld.w','r3, (r3, 0x4)',2)
        with self.assertRaisesRegex(ValueError,'count address'):self.run_case(c)
    def test_wrong_helper(self):
        c=self.code.copy();c[0x10208954]=('bsr','0x10208964',4)
        with self.assertRaisesRegex(ValueError,'unknown helper'):self.run_case(c)
    def test_wrong_pop(self):
        c=self.code.copy();c[0x10208958]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
