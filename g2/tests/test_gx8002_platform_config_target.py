# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_platform_config import execute,oracle

class ConfigTests(unittest.TestCase):
    def test_unexpected_record_read(self):
        with self.assertRaisesRegex(ValueError,'extra memory effect'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,0,[],6,[])
    def test_wrong_width(self):
        with self.assertRaisesRegex(ValueError,'memory effect mismatch'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,0,[],0,[['read16',0x20028000,0]])
    def test_undefined_branch(self):
        with self.assertRaisesRegex(ValueError,'undefined comparison'):
            execute({0:('bt','0x0',2)},0,0,[],0,[])
    def test_distinct_second_read(self):
        result,events=oracle(9,bytes(16),1)
        self.assertEqual(result,0)
        self.assertEqual(events,[['read32',0x20028000,0],['write',0xa000003c,0],['read32',0x20028000,1],['write',0x20027314,1]])

if __name__=='__main__':unittest.main()
