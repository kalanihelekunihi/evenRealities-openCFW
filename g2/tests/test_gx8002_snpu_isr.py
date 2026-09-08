# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_isr import ROOT,ADDRESS,STATE,HELPER,decode,execute
class SnpuIsrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-isr-candidate.disassembly.txt').read_text())
    def run_case(self,state=1,result=0xffffffff,code=None):return execute(self.code if code is None else code,ADDRESS,0,state,result,0xdeadbeef)
    def test_state_two_skips_and_returns_two(self):self.assertEqual(self.run_case(2),([['read',STATE,2]],2))
    def test_other_states_forward_result(self):
        for state in (0,1,3,0x80000000,0xffffffff):self.assertEqual(self.run_case(state),([['read',STATE,state],['call',HELPER]],0xffffffff))
    def test_wrong_state_gate(self):
        c=self.code.copy();c[ADDRESS+6]=('cmpnei','r0, 1',2)
        self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_state_address(self):
        c=self.code.copy();c[ADDRESS+2]=('lrw','r3, 0x20027354',2)
        with self.assertRaisesRegex(ValueError,'state address'):self.run_case(code=c)
    def test_wrong_helper(self):
        c=self.code.copy();c[ADDRESS+10]=('bsr','0x10205bdc',4)
        with self.assertRaisesRegex(ValueError,'helper'):self.run_case(code=c)
    def test_wrong_frame(self):
        c=self.code.copy();c[ADDRESS+14]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(code=c)
if __name__=='__main__':unittest.main()
