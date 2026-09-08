# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_info import execute,oracle

class InfoTests(unittest.TestCase):
    def test_unexpected_memory(self):
        with self.assertRaisesRegex(ValueError,'extra memory effect'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,0,[],0,[])
    def test_invalid_table(self):
        with self.assertRaisesRegex(ValueError,'invalid dispatch lookup'):
            execute({0:('ldr.w','r3, (r3, r0 << 2)',4)},0,0,[],0,[])
    def test_page_count_unsupported(self):
        self.assertEqual(oracle(9,0,0,0x3f000),(0xffffffff,[]))
    def test_block_count_truncates(self):
        self.assertEqual(oracle(5,0,0,4097),(1,[['read32',0x200264e8,4097]]))

if __name__=='__main__':unittest.main()
