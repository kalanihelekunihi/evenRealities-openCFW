# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_discover import execute,oracle

class DiscoverTests(unittest.TestCase):
    def test_uninitialized_jedec(self):
        with self.assertRaisesRegex(ValueError,'uninitialized JEDEC byte'):
            execute({0:('ld.b','r0, (r14, 0x0)',4)},0,0,0,0,[],0)
    def test_unknown_call(self):
        with self.assertRaisesRegex(ValueError,'unknown discovery call'):
            execute({0:('bsr','0x20',4)},0,0,0,0,[],0)
    def test_wrong_write(self):
        with self.assertRaisesRegex(ValueError,'discovery effect mismatch'):
            execute({0:('st.w','r0, (r1, 0x0)',2)},0,0,0,0,[['write',0x200264e4,0xffffffff]],0)
    def test_fallback_selection_is_still_error(self):
        result,events=oracle(0x123456,0,[[0xc22016,0x10000],[0,0]])
        self.assertEqual(result,0xfffffffe)
        self.assertIn(['write',0x200264f0,0x20026624],events)

if __name__=='__main__':unittest.main()
