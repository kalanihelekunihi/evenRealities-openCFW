# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_dump import ROOT,ADDRESS,FORMAT,NEWLINE,decode,execute,expected
class SnpuDumpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-overtime-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,changing=True):return execute(self.code if code is None else code,ADDRESS,0,0x20030000,0x12345678,changing)
    def test_exact_word_reads(self):self.assertEqual([r[1] for r in self.run_case()[0] if r[0]=='read'],[0x20030000+4*i for i in range(32)])
    def test_line_break_positions(self):
        words=0;positions=[]
        for row in self.run_case()[0]:
            if row[:2]==['printf',FORMAT]:words+=1
            elif row==['printf',NEWLINE]:positions.append(words)
        self.assertEqual(positions,[10,20,30,32])
    def test_changing_reads(self):self.assertEqual(self.run_case(),expected(0x20030000,0x12345678,True))
    def test_final_printf_return(self):self.assertEqual(self.run_case()[1],0x12345678^36^0xcafe0000)
    def test_wrong_line_count_detected(self):
        c=self.code.copy();c[ADDRESS+8]=('movi','r5, 9',2)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_read_stride_detected(self):
        c=self.code.copy();c[ADDRESS+38]=('addi','r4, 8',2)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_printf_target_rejected(self):
        c=self.code.copy();c[ADDRESS+22]=('bsr','0x10206c28',4)
        with self.assertRaisesRegex(ValueError,'helper target'):self.run_case(c)
    def test_wrong_frame_rejected(self):
        c=self.code.copy();c[ADDRESS+50]=('pop','r4-r7, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
