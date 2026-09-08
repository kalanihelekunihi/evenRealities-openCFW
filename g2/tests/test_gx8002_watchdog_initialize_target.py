# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_watchdog_initialize import execute

class WatchdogSetupInterpreterTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,0,1000,0,0,0,0)
    def test_unknown_call(self):
        with self.assertRaisesRegex(ValueError,'unexpected call'):
            self.run_code({0:('bsr','0x1234',4)})
    def test_invalid_write(self):
        with self.assertRaisesRegex(ValueError,'unexpected write'):
            self.run_code({0:('st.w','r0, (r0, 0x0)',2)})
    def test_invalid_read(self):
        with self.assertRaisesRegex(ValueError,'unexpected read'):
            self.run_code({0:('ld.w','r0, (r0, 0x0)',2)})
    def test_shift_bound(self):
        with self.assertRaisesRegex(ValueError,'invalid shift'):
            self.run_code({0:('lsli','r0, r0, 32',4)})

if __name__=='__main__':unittest.main()
