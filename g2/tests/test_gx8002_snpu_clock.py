# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_clock import ROOT,ADDRESS,decode,execute,expected
class SnpuClockTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-clock-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,enable=1):return execute(self.code if code is None else code,ADDRESS,0,enable,0xabcdef12,0x80000240,0xdeadbeef)
    def test_enabled_clears_gate_bit(self):self.assertEqual(self.run_case(),expected(1,0xabcdef12,0x80000240))
    def test_disabled_sets_gate_bit(self):self.assertEqual(self.run_case(enable=0),expected(0,0xabcdef12,0x80000240))
    def test_negative_encoding_enables(self):self.assertEqual(self.run_case(enable=0x80000000),expected(0x80000000,0xabcdef12,0x80000240))
    def test_wrong_bit(self):
        c=self.code.copy();c[ADDRESS+0x12]=('andni','r1, r3, 512',4)
        self.assertNotEqual(self.run_case(c),expected(1,0xabcdef12,0x80000240))
    def test_wrong_restore_state(self):
        c=self.code.copy();c[ADDRESS+0x12]=('mov','r0, r3',4)
        self.assertNotEqual(self.run_case(c),expected(1,0xabcdef12,0x80000240))
    def test_wrong_register(self):
        c=self.code.copy();c[ADDRESS+0xc]=('ld.w','r3, (r2, 0x14)',2)
        with self.assertRaisesRegex(ValueError,'register address'):self.run_case(c)
    def test_restore_cannot_save_again(self):
        c=self.code.copy();c[ADDRESS+0x18]=('bsr','0x10025560',4)
        self.assertNotEqual(self.run_case(c),expected(1,0xabcdef12,0x80000240))
    def test_wrong_frame(self):
        c=self.code.copy();c[ADDRESS+0x1c]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
