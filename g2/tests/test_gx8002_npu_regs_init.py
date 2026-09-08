# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_regs_init import ROOT,decode,execute,expected

class NpuRegsInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/npu-regs-init-candidate.disassembly.txt').read_text())
    def run_case(self,pointers=(0xa0b00000,)*6,code=None):return execute(self.code if code is None else code,0x10205950,0,pointers,0xffffffff)
    def test_constant_pointer_call_sequence(self):self.assertEqual(self.run_case(),expected((0xa0b00000,)*6))
    def test_live_pointer_each_call(self):
        pointers=(0,0x10000000,0x20000000,0xa0b00000,0xffffffff,0x80000000)
        self.assertEqual(self.run_case(pointers),expected(pointers))
    def test_exact_initialization_arguments(self):self.assertEqual([r[-1] for r in self.run_case() if r[0]=='call'],[1,2000,0,111,109,0x100000])
    def test_wrong_slot_detected(self):
        c=self.code.copy();c[0x10205952]=('lrw','r4, 0x20027910',2)
        with self.assertRaisesRegex(ValueError,'pointer address'):self.run_case(code=c)
    def test_missing_reload_detected(self):
        c=self.code.copy();c[0x1020595e]=('mov','r0, r2',2)
        self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_mask_detected(self):
        c=self.code.copy();c[0x10205970]=('movi','r1, 127',2)
        self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_helper_order_detected(self):
        c=self.code.copy();c[0x10205972]=('bsr','0x1020566c',4)
        self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_frame_detected(self):
        c=self.code.copy();c[0x10205988]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(code=c)
if __name__=='__main__':unittest.main()
