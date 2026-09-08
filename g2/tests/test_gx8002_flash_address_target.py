# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_address import execute,oracle

class AddressTests(unittest.TestCase):
    def test_three_byte_address_has_zero_tail(self):
        self.assertEqual([e[2] for e in oracle(0x12345678,[3]*4) if e[0]=='write'],[0x34,0x56,0x78,0])
    def test_bad_output_address(self):
        with self.assertRaisesRegex(ValueError,'access mismatch'):
            execute({0:('st.b','r1, (r2, 0x0)',2)},0,0,[['write',0x20028101,0]])
    def test_missing_reload(self):
        with self.assertRaisesRegex(ValueError,'return state mismatch'):
            execute({0:('rts','',2)},0,0,[['read',0x20028000,3]])

if __name__=='__main__':unittest.main()
