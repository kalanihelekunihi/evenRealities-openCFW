# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_app_initialize import execute

class StartupInterpreterTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,0,0,0,(0,0,0),False)
    def test_invalid_record_pointer(self):
        with self.assertRaisesRegex(ValueError,'invalid record pointer'):
            self.run_code({0:('bsr','0x102076c0',4)})
    def test_unmapped_read(self):
        with self.assertRaisesRegex(ValueError,'unmapped read'):
            self.run_code({0:('ld.w','r0, (r1, 0x0)',2)})
    def test_unexpected_stack_write(self):
        with self.assertRaisesRegex(ValueError,'unexpected stack write'):
            self.run_code({0:('st.w','r0, (r1, 0x0)',2)})
    def test_unknown_callback(self):
        with self.assertRaisesRegex(ValueError,'unexpected callback'):
            self.run_code({0:('jsr','r0',2)})

if __name__=='__main__':unittest.main()
