# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_control import ROOT,FUNCTIONS,DELTA,decode,execute,expected
class NpuControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/npu-control-candidate.disassembly.txt').read_text());cls.primitive=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text());cls.entries={n:o+DELTA for n,o in FUNCTIONS}
    def run_case(self,name,value=0xabcdef00,code=None):return execute(self.code if code is None else code,self.primitive,self.entries[name],0,name,0xa0b00000,value,0xffffffff)
    def test_enable_sets_bit_zero(self):self.assertEqual(self.run_case('enable'),expected('enable',0xa0b00000,0xabcdef00))
    def test_disable_clears_bit_zero(self):self.assertEqual(self.run_case('disable',0xffffffff),expected('disable',0xa0b00000,0xffffffff))
    def test_enabled_result(self):self.assertEqual(self.run_case('is_enabled',1)[2],1)
    def test_idle_reads_offset_and_bit31(self):self.assertEqual(self.run_case('all_idle',0x80000000),expected('all_idle',0xa0b00000,0x80000000))
    def test_wrong_idle_offset(self):
        c=self.code.copy();c[self.entries['all_idle']+2]=('addi','r0, 8',2)
        self.assertNotEqual(self.run_case('all_idle',code=c),expected('all_idle',0xa0b00000,0xabcdef00))
    def test_wrong_disable_primitive(self):
        c=self.code.copy();c[self.entries['disable']+4]=('bsr','0x102055cc',4)
        self.assertNotEqual(self.run_case('disable',code=c),expected('disable',0xa0b00000,0xabcdef00))
    def test_wrong_frame(self):
        c=self.code.copy();c[self.entries['enable']+8]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case('enable',code=c)
if __name__=='__main__':unittest.main()
