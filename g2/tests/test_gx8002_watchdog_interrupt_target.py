# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_watchdog_interrupt import execute

class WatchdogInterruptInterpreterTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,11,0,0,0,0)
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            self.run_code({0:('bkpt','',2)})
    def test_null_callback(self):
        with self.assertRaisesRegex(ValueError,'unexpected callback'):
            self.run_code({0:('jsr','r1',2)})
    def test_unmapped_read(self):
        with self.assertRaisesRegex(ValueError,'unexpected read'):
            self.run_code({0:('ld.w','r0, (r1, 0x0)',2)})
    def test_restore_requires_save(self):
        with self.assertRaisesRegex(ValueError,'unexpected restore'):
            self.run_code({0:('pop','r15',2)})

if __name__=='__main__':unittest.main()
