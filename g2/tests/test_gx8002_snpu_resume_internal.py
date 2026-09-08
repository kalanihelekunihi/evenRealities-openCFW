# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_resume_internal import ROOT,ADDRESS,STATE,FIELDS,RESET,decode,execute,expected,PTRS
class SnpuResumeInternalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-resume-internal-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,enabled=1,delay=3,mutation='alternate',prefix=None):return execute(self.code if code is None else code,ADDRESS,0,0xdeadbeef,2,PTRS[0],enabled,delay,mutation,prefix)
    def test_live_state_and_pointer_changes(self):self.assertEqual(self.run_case(),expected(0xdeadbeef,2,PTRS[0],1,3,'alternate'))
    def test_three_initial_stores_before_clock(self):self.assertEqual(self.run_case()[0][:4],[*(['write',a,0] for a in FIELDS),['clock',1]])
    def test_disabled_skips_only_disable_and_poll(self):
        trace=self.run_case(enabled=0)[0]
        self.assertFalse(any(r[0] in ('disable','all_idle') for r in trace))
        self.assertTrue(any(r[0]=='reset' for r in trace));self.assertTrue(any(r[0]=='regs_init' for r in trace))
    def test_distinct_reset_pointer(self):
        trace=self.run_case(mutation='none')[0];self.assertIn(['reset',PTRS[0]+0x100],trace)
    def test_clock_mutation_not_overwritten(self):self.assertEqual(self.run_case(mutation='clock_state')[1][STATE],0xffffffff)
    def test_never_ready_does_not_reset(self):
        result=self.run_case(delay=None,prefix=32)
        self.assertEqual(result,expected(0xdeadbeef,2,PTRS[0],1,None,'alternate',32))
        self.assertFalse(any(r[0] in ('reset','regs_init') for r in result[0]))
    def test_wrong_reset_pointer_detected(self):
        c=self.code.copy();c[ADDRESS+0x36]=('ld.w','r0, (r4, 0x5c4)',4)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_stale_poll_pointer_detected(self):
        c=self.code.copy();c[ADDRESS+0x2a]=('lrw','r0, '+hex(PTRS[0]),4)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_clock_argument_detected(self):
        c=self.code.copy();c[ADDRESS+6]=('movi','r0, 0',2)
        self.assertNotEqual(self.run_case(c),self.run_case())
    def test_wrong_frame_detected(self):
        c=self.code.copy();c[ADDRESS+0x44]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
