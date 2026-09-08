# SPDX-License-Identifier: MIT
import sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_interrupt_masks import ROOT,FUNCTIONS,DELTA,decode,execute,expected

class NpuInterruptMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/npu-interrupt-mask-candidate.disassembly.txt').read_text())
        cls.primitive=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text())
        cls.entries={n:o+DELTA for n,o,size in FUNCTIONS}

    def run_case(self,name,mask,value=0,changing=False,code=None):
        return execute(self.code if code is None else code,self.primitive,self.entries[name],0,name,0xa0b00000,mask,value,changing,0xffffffff)

    def test_full_enable_order(self):
        calls=[r for r in self.run_case('npu_en_interrupt',127)[0] if r[0]=='call']
        self.assertEqual(calls,[['call',0x102055cc,0xa0b00004,bit] for bit in (0,4,8,12,13,14,16)])

    def test_clear_uses_set_bit_and_offset_eight(self):
        self.assertEqual(self.run_case('npu_clr_interrupt',1)[0],[['call',0x102055cc,0xa0b00008,0],['read',0xa0b00008,0],['write',0xa0b00008,1]])

    def test_no_overflow_excludes_both_flags(self):
        self.assertEqual(self.run_case('npu_clr_interrupt_without_overflow',48)[0],[])

    def test_overflow_only_excludes_other_flags(self):
        self.assertEqual(self.run_case('npu_clr_overflow_interrupt',79)[0],[])

    def test_ignored_high_bits_no_mmio(self):
        for name in self.entries:self.assertEqual(self.run_case(name,0xffffff80)[0],[])

    def test_changing_reads_are_preserved(self):
        name='npu_clr_interrupt'
        actual=self.run_case(name,127,0x12345678,True)
        self.assertEqual(actual,expected(name,0xa0b00000,127,0x12345678,True))
        reads=[r[2] for r in actual[0] if r[0]=='read']
        self.assertEqual(len(set(reads)),7)

    def test_wrong_flag_detected(self):
        name='npu_en_interrupt';c=self.code.copy();pc=self.entries[name]+2;op,args,width=c[pc];self.assertEqual(op,'andi');c[pc]=('andi','r3, r1, 2',width)
        self.assertNotEqual(self.run_case(name,1,code=c),self.run_case(name,1))

    def test_lost_saved_mask_detected(self):
        name='npu_en_interrupt';c=self.code.copy();pc=self.entries[name]+22;op,args,width=c[pc];self.assertEqual(op,'andi');c[pc]=('andi','r3, r1, 2',width)
        self.assertNotEqual(self.run_case(name,1,code=c),self.run_case(name,1))

    def test_wrong_frame_detected(self):
        name='npu_en_interrupt';c=self.code.copy();c[self.entries[name]+118]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(name,0,code=c)

if __name__=='__main__':unittest.main()
