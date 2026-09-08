# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_erase import oracle,execute,execute_chip
class EraseTests(unittest.TestCase):
    def test_zero_length_unaligned_erases_sector(self):
        result,trace=oracle(1,0,65536)
        self.assertEqual(result,0)
        self.assertIn(['command',0x20,0x200264f5,3],trace)
    def test_zero_length_aligned_no_command(self):
        self.assertEqual(oracle(4096,0,65536),(0,[['size',65536]]))
    def test_out_of_range_rejected(self):
        self.assertEqual(oracle(65536,1,65536),(0xffffffea,[['size',65536]]))
    def test_aligned_block_selected(self):
        self.assertIn(['command',0xd8,0x200264f5,3],oracle(0,65536,65536)[1])
    def test_chip_requires_size_read(self):
        with self.assertRaisesRegex(ValueError,'chip arguments'):
            execute_chip({0:('bsr','0x10023d58',4)},0,0,4096,0)
    def test_chip_requires_balanced_frame(self):
        with self.assertRaisesRegex(ValueError,'chip return'):
            execute_chip({0:('pop','r15',2)},0,0,4096,0)
    def test_wrapped_address_reaches_zero(self):
        result,trace=oracle(0xfffff000,0x2000,0xffffffff)
        self.assertEqual(result,0)
        self.assertEqual([e[2] for e in trace if e[0]=='encode'],[0xfffff000,0])
    def test_unknown_helper(self):
        with self.assertRaisesRegex(ValueError,'erase helper'):
            execute({0:('bsr','0x1234',4)},0,0,0,0,0,0)
if __name__=='__main__':unittest.main()
