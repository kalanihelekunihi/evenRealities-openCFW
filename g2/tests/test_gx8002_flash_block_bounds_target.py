# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_block_bounds import execute,expected,STATE,MASK
class BlockBoundsTests(unittest.TestCase):
    def test_partial_block_excluded(self):
        self.assertEqual(expected(4096,0,8191,1,2),
            (MASK,[['write',2,0],['write',1,0],['read',STATE,0],['read',STATE+4,8191]]))
    def test_last_full_block(self):
        self.assertEqual(expected(8191,0,8192,1,2)[1][-2:],
                         [['write',1,4096],['write',2,8192]])
    def test_alias_index_cleared_before_read(self):
        result,events=expected(1,-1,4096,STATE,2)
        self.assertEqual(result,0)
        self.assertEqual(events[2],['read',STATE,0])
    def test_alias_size_cleared_before_read(self):
        self.assertEqual(expected(1,0,4096,1,STATE+4)[0],MASK)
    def test_negative_index_skips_size(self):
        self.assertEqual(len(expected(1,-1,4096,1,2)[1]),3)
    def test_saved_register_rejected(self):
        with self.assertRaisesRegex(ValueError,'saved register'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,0,0,0,1,2)
    def test_unknown_instruction_rejected(self):
        with self.assertRaisesRegex(ValueError,'unknown instruction'):
            execute({0:('invalid','',2)},0,0,0,0,1,2)
if __name__=='__main__':unittest.main()
