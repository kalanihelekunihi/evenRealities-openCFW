# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from model_gx8002_flash_uid_read import expected,MASK
class UidModelTests(unittest.TestCase):
    def test_reject_count_zero_no_hardware(self):
        result,trace=expected(0,16,0x20029000,0)
        self.assertEqual(result,MASK);self.assertEqual(len(trace),3)
        self.assertEqual(trace[-1],['write',0x20029000,0])
    def test_zero_request_still_sends_prefix(self):
        result,trace=expected(0,0,0x20029000,0x85)
        self.assertEqual(result,0)
        self.assertEqual([e[2] for e in trace if e[:2]==['write',0xa2000060]],[0x4b,0,0,0,0])
        self.assertIn(['write',0xa2000004,MASK],trace)
    def test_byte_manufacturer_and_count_clamp(self):
        result,trace=expected(0xfffffffe,17,0x20029000,0xff85)
        self.assertEqual(result,0);self.assertEqual(trace[2],['write',0x20029000,16])
        self.assertEqual([e[1] for e in trace if e[0]=='byte-write'][:3],[0xfffffffe,0xffffffff,0])
    def test_count_store_precedes_idle_even_when_aliasing(self):
        _,trace=expected(0,1,0x200264f0,0x5e)
        self.assertEqual(trace[2],['write',0x200264f0,1]);self.assertEqual(trace[3],['call',0x1002364c,[]])
    def test_negative_count_not_silently_clamped(self):
        with self.assertRaisesRegex(ValueError,'negative UID capacity'):
            expected(0,MASK,0x20029000,0x85)
if __name__=='__main__':unittest.main()
