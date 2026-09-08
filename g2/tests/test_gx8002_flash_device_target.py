# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_device import execute

class FlashDeviceTests(unittest.TestCase):
    def test_uninitialized_byte(self):
        code={0:('push','r15',2),2:('subi','r14, r14, 4',2),4:('ld.b','r3, (r14, 0x3)',4)}
        with self.assertRaisesRegex(ValueError,'uninitialized status'):execute(code,0,0,0,0)
    def test_unknown_call(self):
        with self.assertRaisesRegex(ValueError,'unknown device call'):execute({0:('bsr','0x1234',4)},0,0,0,0)
    def test_unbalanced_frame(self):
        with self.assertRaisesRegex(ValueError,'unbalanced frame'):execute({0:('pop','r15',2)},0,0,0,0)

if __name__=='__main__':unittest.main()
