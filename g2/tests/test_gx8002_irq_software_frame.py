# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_software_frame import execute

class SoftwareIRQFrameTests(unittest.TestCase):
    def test_missing_hardware_entry(self):
        with self.assertRaisesRegex(ValueError,'hardware save order'):
            execute({0:('ipush','',2)},0,0)
    def test_unbalanced_frame(self):
        with self.assertRaisesRegex(ValueError,'unbalanced software frame'):
            execute({0:('nie','',2),2:('ipush','',2),4:('subi','r14, r14, 4',2),6:('ipop','',2)},0,0)
    def test_restore_without_save(self):
        with self.assertRaisesRegex(ValueError,'uninitialized restore'):
            execute({0:('subi','r14, r14, 68',2),2:('ldm','r15-r31, (r14)',4)},0,0)

if __name__=='__main__':unittest.main()
