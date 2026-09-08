# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_xip import execute,oracle

class XipTests(unittest.TestCase):
    def test_unread_sixth_argument(self):
        with self.assertRaisesRegex(ValueError,'unexpected argument read'):
            execute({0:('ld.w','r0, (r14, 0x4)',4)},0,[0]*9)
    def test_unknown_mmio(self):
        with self.assertRaisesRegex(ValueError,'unexpected register write'):
            execute({0:('st.w','r0, (r14, 0x0)',4)},0,[0]*9)
    def test_undefined_branch(self):
        with self.assertRaisesRegex(ValueError,'undefined comparison'):
            execute({0:('bt','0x0',2)},0,[0]*9)
    def test_invalid_configuration_keeps_spi_disabled(self):
        self.assertEqual(oracle([235,9,1,24,4,0,1,4,4]),(0xffffffff,[[0xa2000008,0]]))

if __name__=='__main__':unittest.main()
