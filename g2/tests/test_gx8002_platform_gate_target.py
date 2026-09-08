# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_platform_gate import execute

class GateInterpreterTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,bytes(148),bytes(416),0,0,0,0)
    def test_invalid_switch_target(self):
        with self.assertRaisesRegex(ValueError,'invalid switch target'):
            self.run_code({0:('movi','r0, 0x1234',2),2:('jmp','r0',2)})
    def test_unexpected_write(self):
        with self.assertRaisesRegex(ValueError,'unexpected write'):
            self.run_code({0:('st.w','r0, (r1, 0x0)',2)})
    def test_wrong_lookup(self):
        with self.assertRaisesRegex(ValueError,'unexpected lookup'):
            self.run_code({0:('bsr','0x1234',4)})
    def test_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            self.run_code({0:('bkpt','',2)})

if __name__=='__main__':unittest.main()
