# SPDX-License-Identifier: MIT
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_interrupt_status import ROOT,FUNCTIONS,DELTA,decode,execute,expected

class NpuInterruptStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/npu-interrupt-status-candidate.disassembly.txt').read_text())
        cls.primitive=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text())
        cls.entry=FUNCTIONS[0][1]+DELTA

    def run_case(self,value,changing=0,alias=False,code=None):
        return execute(self.code if code is None else code,self.primitive,self.entry,0,'npu_get_interrupt',0xa0b00000,changing,value,alias,0xffffffff)

    def test_first_two_flags_combine(self):
        self.assertEqual(self.run_case(17)[1][0x20021000],3)

    def test_return_preserves_status_bit16(self):
        self.assertEqual(self.run_case(0x10000)[2],65536)
        self.assertEqual(self.run_case(0x10000)[1][0x20021000],64)

    def test_ignored_status_bits(self):
        self.assertEqual(self.run_case(0xfffe8eee)[1][0x20021000],0)

    def test_all_flags_order(self):
        trace=self.run_case(0x17111)[0]
        self.assertEqual([r[2] for r in trace if r[0]=='output'],[3,7,15,31,63,127])
        self.assertEqual(sum(r[0]=='call' for r in trace),1)

    def test_alias_uses_status_snapshot(self):
        self.assertEqual(self.run_case(0x17111,alias=True),expected('npu_get_interrupt',0xa0b00000,0,0x17111,True))

    def test_live_output_reads(self):
        self.assertEqual(self.run_case(0x17111,0x12345678),expected('npu_get_interrupt',0xa0b00000,0x12345678,0x17111,False))

    def test_wrong_first_flags_detected(self):
        c=self.code.copy();pc=self.entry+22;op,args,width=c[pc];self.assertEqual(op,'ori');c[pc]=('movi','r3, 2',width)
        self.assertNotEqual(self.run_case(17,code=c),self.run_case(17))

    def test_cached_output_detected(self):
        c=self.code.copy();pc=self.entry+36;op,args,width=c[pc];self.assertEqual(op,'ld.w');c[pc]=('mov','r2, r3',width)
        self.assertNotEqual(self.run_case(0x17111,0x12345678,code=c),self.run_case(0x17111,0x12345678))

    def test_wrong_frame_detected(self):
        c=self.code.copy();c[self.entry+116]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(0,code=c)

if __name__=='__main__':unittest.main()
