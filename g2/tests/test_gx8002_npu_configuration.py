# SPDX-License-Identifier: MIT
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_configuration import ROOT, FUNCTIONS, DELTA, decode, execute, expected

class NpuConfigurationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/npu-configuration-candidate.disassembly.txt').read_text())
        cls.primitive=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text())
        cls.entries={n:o+DELTA for n,o,size in FUNCTIONS}

    def run_case(self, name, argument, value=0xabcdef01, code=None):
        return execute(self.code if code is None else code,self.primitive,self.entries[name],0,name,0xa0b00000,argument,value,False,0xffffffff)

    def test_clock_full_width_nonzero(self):
        for value in (0,1,0x80000000,0xffffffff):
            self.assertEqual(self.run_case('npu_set_clock_gate',value),expected('npu_set_clock_gate',0xa0b00000,value,0xabcdef01,False))

    def test_idle_reversed_polarity(self):
        self.assertEqual(self.run_case('npu_set_idle_mode',0)[1][0xa0b00000],0xabcdef11)
        self.assertEqual(self.run_case('npu_set_idle_mode',0x80000000,0xffffffff)[1][0xa0b00000],0xffffffef)

    def test_cycle_halfwords_and_helper_clobbers(self):
        self.assertEqual(self.run_case('npu_set_idle_cycle',0x12345678)[1][0xa0b00000],0x5678ef01)

    def test_threshold_full_word_and_offset(self):
        self.assertEqual(self.run_case('npu_set_overtime_thr',0xfedcba98)[0],[['call',0x102055f0,0xa0b00014,0xfedcba98],['write',0xa0b00014,0xfedcba98]])

    def test_wrong_idle_polarity_detected(self):
        c=self.code.copy();pc=self.entries['npu_set_idle_mode']+2;op,args,width=c[pc];c[pc]=('bez',args,width)
        self.assertNotEqual(self.run_case('npu_set_idle_mode',0,code=c),self.run_case('npu_set_idle_mode',0))

    def test_wrong_halfword_detected(self):
        c=self.code.copy();pc=self.entries['npu_set_idle_cycle']+10;op,args,width=c[pc];self.assertEqual(op,'zexth');c[pc]=('mov',args,width)
        self.assertNotEqual(self.run_case('npu_set_idle_cycle',0,code=c),self.run_case('npu_set_idle_cycle',0))

    def test_lost_pointer_detected(self):
        c=self.code.copy();pc=self.entries['npu_set_idle_cycle']+16;op,args,width=c[pc];self.assertEqual(op,'mov');c[pc]=('mov','r0, r2',width)
        with self.assertRaisesRegex(ValueError,'register address'):self.run_case('npu_set_idle_cycle',1,code=c)

    def test_wrong_threshold_offset_detected(self):
        c=self.code.copy();c[self.entries['npu_set_overtime_thr']+2]=('addi','r0, 16',2)
        with self.assertRaisesRegex(ValueError,'register address'):self.run_case('npu_set_overtime_thr',1,code=c)

    def test_wrong_pop_detected(self):
        c=self.code.copy();c[self.entries['npu_set_idle_cycle']+22]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case('npu_set_idle_cycle',1,code=c)

if __name__=='__main__':unittest.main()
