# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_npu_registers import ROOT,FUNCTIONS,DELTA,decode,execute,expected
class NpuRegisterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/npu-register-native.disassembly.txt').read_text());cls.entries={n:o+DELTA for n,o,_ in FUNCTIONS}
    def run_case(self,name,argument,value=0xabcdef01,code=None,address=0xa0b00000):return execute(self.code if code is None else code,self.entries[name],name,address,value,argument,0xffffffff)
    def test_get_count_32_zero(self):self.assertEqual(self.run_case('get_bit',32)[2],0)
    def test_count_64_wraps_to_zero(self):self.assertEqual(self.run_case('get_bit',64)[2],1)
    def test_set_count_32_still_writes(self):self.assertEqual(self.run_case('set_bit',32),expected('set_bit',0xa0b00000,0xabcdef01,32))
    def test_clear_count_32_clears_word(self):self.assertEqual(self.run_case('clear_bit',32)[1],0)
    def test_clear_count_63_clears_word(self):self.assertEqual(self.run_case('clear_bit',0xffffffff)[1],0)
    def test_high_bits_ignored(self):self.assertEqual(self.run_case('clear_bit',0x80000001),self.run_case('clear_bit',1))
    def test_word_read(self):self.assertEqual(self.run_case('get_value',123),expected('get_value',0xa0b00000,0xabcdef01,123))
    def test_word_write(self):self.assertEqual(self.run_case('set_value',0x80000000),expected('set_value',0xa0b00000,0xabcdef01,0x80000000))
    def test_wrong_shift_direction(self):
        c=self.code.copy();c[self.entries['get_bit']+2]=('lsl','r0, r1',2)
        self.assertNotEqual(self.run_case('get_bit',8,code=c),expected('get_bit',0xa0b00000,0xabcdef01,8))
    def test_rotate_not_left_shift(self):
        c=self.code.copy();c[self.entries['clear_bit']+6]=('lsl','r3, r1',2)
        self.assertNotEqual(self.run_case('clear_bit',31,code=c),expected('clear_bit',0xa0b00000,0xabcdef01,31))
    def test_misaligned_access_rejected(self):
        with self.assertRaisesRegex(ValueError,'alignment'):self.run_case('get_value',0,address=0xa0b00002)
    def test_abi_clobber(self):
        c=self.code.copy();c[self.entries['get_value']]=('ld.w','r4, (r0, 0x0)',2)
        with self.assertRaisesRegex(ValueError,'ABI/frame'):self.run_case('get_value',0,code=c)
if __name__=='__main__':unittest.main()
