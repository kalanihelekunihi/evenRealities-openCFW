# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_snpu_run_task import Case,expected,STATE,MASK
class RunTaskModelTests(unittest.TestCase):
    def test_all_ring_positions(self):
        for start in range(10):
            for end in range(10):
                trace,words,result=expected(Case(start=start,end=end))
                self.assertEqual(result,MASK if (end+1)%10==start else 0)
                self.assertEqual(words[STATE+0x5b4],end if result else (end+1)%10)
    def test_null_task_reads_nothing(self):self.assertEqual(expected(Case(task=0))[0],[])
    def test_uninitialized_reads_only_register_pointer(self):
        self.assertEqual(expected(Case(registers=0))[0],[('read',STATE+0x5c4,0)])
    def test_full_ring_writes_nothing(self):
        self.assertFalse(any(x[0]=='write' for x in expected(Case(start=0,end=9))[0]))
    def test_resume_mutation_preserves_selected_descriptor(self):
        trace,words,result=expected(Case(end=9,start=1,state=2,mutation=True))
        self.assertIn(('submit',STATE+9*144+16),trace)
        self.assertEqual([x[0] for x in trace if x[0] in ('resume','submit')],['resume','submit'])
    def test_callback_bits_preserved(self):
        for value in (0,MASK,0x80000000):
            trace,words,result=expected(Case(callback=value,private=value))
            self.assertEqual(words[STATE+0x90],value);self.assertEqual(words[STATE+0x98],value)
if __name__=='__main__':unittest.main()
