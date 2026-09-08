# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_word_io import execute,oracle

class WordIoTests(unittest.TestCase):
    def test_short_buffer(self):
        with self.assertRaisesRegex(ValueError,'word buffer overrun'):
            execute({0:('stbi.w','r0, (r1)',4)},0,0,0x20028000,3,[],0)
    def test_unaligned_buffer(self):
        with self.assertRaisesRegex(ValueError,'word buffer overrun'):
            execute({0:('ldbi.w','r0, (r1)',4)},0,0,0x20028001,4,[],0)
    def test_unknown_helper(self):
        with self.assertRaisesRegex(ValueError,'unknown word I/O helper'):
            execute({0:('bsr','0x20',4)},0,0,0,0,[],0)
    def test_zero_length_distinction(self):
        self.assertEqual(oracle(False,0,0,0,0,0),[])
        self.assertTrue(oracle(True,0,0,0,0,0))

if __name__=='__main__':unittest.main()
