# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_initialize import ROOT,ADDRESS,STATE,decode,execute,expected
class SnpuInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-initialize-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,mutation='all'):return execute(self.code if code is None else code,ADDRESS,0,0xdeadbeef,mutation)
    def test_ordered_state_and_calls(self):self.assertEqual(self.run_case(),expected(0xdeadbeef,'all'))
    def test_final_state_overwrites_helper(self):self.assertEqual(self.run_case(mutation='last')[1][STATE],2)
    def test_isr_registration(self):self.assertIn(['request_irq',0x10205ce0,0],self.run_case()[0])
    def test_wrong_register_base(self):
        c=self.code.copy();c[ADDRESS+4]=('movih','r0, 41136',4)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_store_offset(self):
        c=self.code.copy();c[ADDRESS+16]=('st.w','r3, (r4, 0x5c8)',4)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_isr(self):
        c=self.code.copy();c[ADDRESS+50]=('lrw','r0, 0x10205ce4',2)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_nonzero_private_data(self):
        c=self.code.copy();c[ADDRESS+48]=('movi','r1, 1',2)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_return_frame(self):
        c=self.code.copy();c[ADDRESS+62]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
