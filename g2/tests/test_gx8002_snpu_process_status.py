# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_process_status import ROOT,ADDRESS,decode,execute,Case,expected,STATE
class SnpuProcessStatusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/snpu-process-status-candidate.disassembly.txt').read_text())
    def run_case(self,case=Case(),code=None):return execute(self.code if code is None else code,ADDRESS,0,case)
    def mutate(self,op,args,newop,newargs):
        c=self.code.copy();matches=[pc for pc,(o,a,w) in c.items() if o==op and a==args]
        self.assertEqual(len(matches),1);pc=matches[0];c[pc]=(newop,newargs,c[pc][2]);return c
    def test_all_event_priority_combinations(self):
        for events in range(128):self.assertEqual(self.run_case(Case(events=events)),expected(Case(events=events)))
    def test_completion_overrides_error_bits(self):
        trace=self.run_case(Case(events=127))[0]
        self.assertTrue(any(r[0]=='completed' for r in trace));self.assertFalse(any(r[0] in ('overtime','overflow_address') for r in trace))
    def test_duplicate_completion_does_not_walk_ring(self):
        trace=self.run_case(Case(duplicate=True))[0]
        self.assertFalse(any(r[0] in ('callback','suspend','write') for r in trace))
    def test_overtime_has_priority_over_overflow(self):
        trace=self.run_case(Case(events=44))[0];self.assertIn(['overtime'],trace);self.assertFalse(any(r[0]=='overflow_address' for r in trace))
    def test_no_event_returns_two(self):self.assertEqual(self.run_case(Case(events=0))[2],2)
    def test_bit64_returns_one(self):self.assertEqual(self.run_case(Case(events=64))[2],1)
    def test_bit16_does_not_enter_overflow_path(self):self.assertEqual(self.run_case(Case(events=16))[2],2)
    def test_wrap_and_sticky_stall(self):
        trace=self.run_case(Case(start=9,end=0,target=1))[0]
        self.assertEqual([r[3] for r in trace if r[0]=='callback'],[2,2,2])
    def test_end_snapshot_survives_callback_mutation(self):
        case=Case(start=9,end=2,target=4,mutation='all');self.assertEqual(self.run_case(case),expected(case))
    def test_callback_args_survive_suspend(self):
        trace=self.run_case(Case(start=9,end=0,target=9,mutation='all'))[0]
        callback=next(r for r in trace if r[0]=='callback');self.assertEqual(callback[2:],[0x80000009,2,0x21000090])
    def test_null_callbacks_still_advance(self):
        result=self.run_case(Case(start=8,target=1,callbacks=0));self.assertEqual(result[1][STATE+0x5b0],2)
    def test_nonmatching_completion_prefix(self):
        case=Case(target=None,prefix=32,mutation='all');self.assertEqual(self.run_case(case),expected(case));self.assertEqual(self.run_case(case)[3],'ring_prefix')
    def test_wrong_priority_detected(self):
        c=self.mutate('andi','r6, r3, 1','andi','r6, r3, 2');self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_private_restore_detected(self):
        c=self.mutate('ld.w','r2, (r14, 0x0)','ld.w','r2, (r14, 0x4)');case=Case(start=9,end=0,target=9,mutation='all');self.assertNotEqual(self.run_case(case,c),self.run_case(case))
    def test_wrong_final_index_store_detected(self):
        c=self.mutate('st.w','r5, (r4, 0x5b0)','st.w','r6, (r4, 0x5b0)');self.assertNotEqual(self.run_case(code=c),self.run_case())
    def test_wrong_return_selection_detected(self):
        c=self.mutate('inct','r0, r3, 0','inct','r0, r3, 1');case=Case(events=64);self.assertNotEqual(self.run_case(case,c),self.run_case(case))
    def test_wrong_scratch_frame_detected(self):
        c=self.mutate('subi','r14, r14, 12','subi','r14, r14, 16')
        with self.assertRaisesRegex(ValueError,'scratch allocation'):self.run_case(code=c)
    def test_wrong_pop_detected(self):
        c=self.mutate('pop','r4-r10, r15','pop','r4-r9, r15')
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(code=c)
if __name__=='__main__':unittest.main()
