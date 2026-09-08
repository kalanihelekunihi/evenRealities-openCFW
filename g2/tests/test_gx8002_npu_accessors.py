# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_accessors import ROOT,FUNCTIONS,DELTA,decode,execute,expected
class NpuAccessorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/npu-accessor-candidate.disassembly.txt').read_text());cls.primitive=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text());cls.entries={n:o+DELTA for n,o,_ in FUNCTIONS}
    def run_case(self,name,code=None,index=3,alias=False):return execute(self.code if code is None else code,self.primitive,self.entries[name],0,name,0xa0b00000,index,0xabcdef01,alias,0xffffffff)
    def test_getter_output_and_return(self):
        n='npu_get_over_cmd_addr';self.assertEqual(self.run_case(n),expected(n,0xa0b00000,3,0xabcdef01,False))
    def test_output_alias(self):
        n='npu_get_task_head';self.assertEqual(self.run_case(n,alias=True),expected(n,0xa0b00000,3,0xabcdef01,True))
    def test_index_wrap(self):
        n='npu_get_base_addr';self.assertEqual(self.run_case(n,index=0x40000000),expected(n,0xa0b00000,0x40000000,0xabcdef01,False))
    def test_reset_order(self):
        n='npu_reset';self.assertEqual(self.run_case(n),expected(n,0xa0b00000,3,0xabcdef01,False))
    def test_setter_argument(self):
        n='npu_set_task_head';self.assertEqual(self.run_case(n,index=0x80000000),expected(n,0xa0b00000,0x80000000,0xabcdef01,False))
    def test_wrong_output_address(self):
        n='npu_get_over_cmd_addr';c=self.code.copy();c[self.entries[n]+12]=('st.w','r0, (r4, 0x4)',2)
        with self.assertRaisesRegex(ValueError,'output address'):self.run_case(n,c)
    def test_reset_pointer_must_survive_call(self):
        n='npu_reset';c=self.code.copy();c[self.entries[n]+14]=('addi','r0, r0, 8',2)
        with self.assertRaisesRegex(ValueError,'register address'):self.run_case(n,c)
    def test_wrong_reset_bit(self):
        n='npu_reset';c=self.code.copy();c[self.entries[n]+4]=('movi','r1, 4',2)
        self.assertNotEqual(self.run_case(n,c),expected(n,0xa0b00000,3,0xabcdef01,False))
    def test_wrong_index_scale(self):
        n='npu_get_base_addr';c=self.code.copy();c[self.entries[n]+2]=('lsli','r1, r1, 3',2)
        with self.assertRaisesRegex(ValueError,'register address'):self.run_case(n,c)
    def test_wrong_frame(self):
        n='npu_get_cur_cmd_addr';c=self.code.copy();c[self.entries[n]+12]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(n,c)
if __name__=='__main__':unittest.main()
