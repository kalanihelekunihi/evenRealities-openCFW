# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_suspend import ROOT,ADDRESS,decode,execute,expected,PTRS
class SnpuSuspendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-suspend-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,state=1,pointer=PTRS[0],enabled=1,delay=3,mutation='alternate',prefix=None):return execute(self.code if code is None else code,ADDRESS,0,0xdeadbeef,state,pointer,enabled,delay,mutation,prefix)
    def test_live_pointer_reloads(self):self.assertEqual(self.run_case(),expected(0xdeadbeef,1,PTRS[0],1,3,'alternate'))
    def test_null_before_state(self):
        result=self.run_case(pointer=0);self.assertEqual(result,expected(0xdeadbeef,1,0,1,3,'alternate'));self.assertEqual(len(result[0]),1)
    def test_suspended_skips_helpers(self):self.assertEqual(self.run_case(state=2),expected(0xdeadbeef,2,PTRS[0],1,3,'alternate'))
    def test_disabled_gates_immediately(self):self.assertEqual(self.run_case(enabled=0),expected(0xdeadbeef,1,PTRS[0],0,3,'alternate'))
    def test_never_idle_prefix(self):self.assertEqual(self.run_case(delay=None,prefix=32),expected(0xdeadbeef,1,PTRS[0],1,None,'alternate',32))
    def test_stale_poll_pointer(self):
        c=self.code.copy();c[ADDRESS+0x22]=('lrw','r0, '+hex(PTRS[0]),4)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,1,PTRS[0],1,3,'alternate'))
    def test_wrong_final_state(self):
        c=self.code.copy();c[ADDRESS+0x34]=('movi','r3, 1',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,1,PTRS[0],1,3,'alternate'))
    def test_clock_mutation_overwritten(self):self.assertEqual(self.run_case(mutation='clock_state'),expected(0xdeadbeef,1,PTRS[0],1,3,'clock_state'))
    def test_wrong_clock_argument(self):
        c=self.code.copy();c[ADDRESS+0x2e]=('movi','r0, 1',2)
        self.assertNotEqual(self.run_case(c),expected(0xdeadbeef,1,PTRS[0],1,3,'alternate'))
    def test_wrong_return_frame(self):
        c=self.code.copy();c[ADDRESS+0x3a]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
