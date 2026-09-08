# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from model_gx8002_flash_otp_write import expected,MASK,STATE
class OtpWriteModelTests(unittest.TestCase):
    def test_zero_reads_descriptor_only(self):
        result,trace=expected(0,0,0,512,4096,4096,0,0x85)
        self.assertEqual(result,MASK);self.assertEqual(len(trace),3)
    def test_bounds_excludes_manufacturer(self):
        result,trace=expected(511,0,2,512,4096,4096,0,0x85)
        self.assertEqual(result,MASK);self.assertEqual(len(trace),4)
    def test_pages_and_mutating_width(self):
        result,trace=expected(255,0xfffffffe,258,1024,4096,4096,0,0x85)
        calls=[e[2] for e in trace if e[:2]==['call',0x10023e14]]
        self.assertEqual(result,258)
        self.assertEqual(calls,[[5,0xfffffffe,1],[7,0xffffffff,256],[9,255,1]])
    def test_wrapped_sum_takes_single_huge_transfer(self):
        result,trace=expected(1,0,0xffffffff,0,4096,4096,0,0x85)
        self.assertEqual(result,MASK)
        self.assertEqual(len([e for e in trace if e[:2]==['call',0x10023e14]]),1)
if __name__=='__main__':unittest.main()
