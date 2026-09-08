# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_read import oracle,execute
class ReadTests(unittest.TestCase):
    def test_zero_still_waits(self):self.assertEqual(oracle(0,0,0),(0,[['wait']]))
    def test_negative_signed_length_single_callback(self):
        trace=oracle(0,0,0x80000000)[1]
        self.assertEqual(len(trace),3)
        self.assertEqual(trace[-1][-1],0x80000000)
    def test_reload_and_wrap(self):
        reads=[e for e in oracle(0xffff0000,0xffff0000,65537)[1] if e[0]=='read']
        self.assertEqual(reads[1],['read',0x10028000,0,0,1])
    def test_callback_needs_pointer_read(self):
        with self.assertRaisesRegex(ValueError,'callback dispatch'):
            execute({0:('jsr','r3',2)},0,0,0,0,0,0)
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'read frame'):
            execute({0:('push','r15',2)},0,0,0,0,0,0)
if __name__=='__main__':unittest.main()
