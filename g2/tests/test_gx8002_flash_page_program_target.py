# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_page_program import oracle,execute
class PageProgramTests(unittest.TestCase):
    def test_zero_does_not_read_state(self):self.assertEqual(oracle(0xffffffff,0,0,0),(0,[]))
    def test_wrapped_sum_single_large_call(self):
        result,trace=oracle(1,0,0xffffffff,0)
        self.assertEqual(result,0)
        self.assertEqual([e[-1] for e in trace if e[0]=='read'],[0xffffffff])
    def test_page_split_reload(self):
        result,trace=oracle(255,0,258,1024)
        self.assertEqual(result,0)
        self.assertEqual([e[-1] for e in trace if e[0]=='read'],[1,256,1])
        self.assertEqual(sum(e==['wait'] for e in trace),1)
        self.assertEqual(sum(e==['enable'] for e in trace),3)
    def test_bounds_failure_has_no_helper(self):
        self.assertEqual(oracle(256,0,1,256),(0xffffffea,[['size',256]]))
    def test_callback_without_reload(self):
        with self.assertRaisesRegex(ValueError,'callback dispatch'):
            execute({0:('jsr','r3',2)},0,0,0,0,0,0,0)
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'read frame'):
            execute({0:('push','r15',2)},0,0,0,0,0,0,0)
if __name__=='__main__':unittest.main()
