# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_clock_lookup import execute

class ClockLookupInterpreterTests(unittest.TestCase):
    def test_null_write_rejected(self):
        with self.assertRaisesRegex(ValueError,'unmapped access'):
            execute({0:('st.w','r0, (r1, 0x0)',2)},0,1,0,list(range(26)))

    def test_table_write_rejected(self):
        with self.assertRaisesRegex(ValueError,'unexpected write'):
            execute({0:('st.w','r0, (r1, 0x0)',2)},0,1,0x200266e0,list(range(26)))

    def test_unknown_instruction_rejected(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('bkpt','',2)},0,0,0,list(range(26)))

    def test_callee_saved_clobber_rejected(self):
        with self.assertRaisesRegex(ValueError,'ABI mismatch'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,0,0,list(range(26)))

if __name__=='__main__':unittest.main()
