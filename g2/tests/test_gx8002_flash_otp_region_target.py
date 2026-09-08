# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_otp_region import execute,oracle

class OtpRegionTests(unittest.TestCase):
    def test_unsigned_rejection(self):
        result,events=oracle('set',0xffffffff,3,0,512)
        self.assertEqual(result,0xffffffff)
        self.assertFalse(any(e[0]=='write' for e in events))
    def test_region_is_not_independently_masked(self):
        result,events=oracle('set',8,9,0,512)
        self.assertEqual((result,events[-1]),(0,['write',0x20029110,8]))
    def test_extra_access(self):
        with self.assertRaisesRegex(ValueError,'extra access'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,0,[])
    def test_wrong_pointer(self):
        with self.assertRaisesRegex(ValueError,'access mismatch'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,0,[['read',0x200264f0,0]])

if __name__=='__main__':unittest.main()
