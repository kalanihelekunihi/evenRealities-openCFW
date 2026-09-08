# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_protection import execute,oracle

class ProtectionTests(unittest.TestCase):
    def test_matching_sentinel_stops_scan(self):
        result,events=oracle(False,0x20028000,0x85,17,29,
                            [(17,255,29,255,0xffffffff),(0,0,0,0,4096)],2,0)
        self.assertEqual(result,0xffffffff)
        self.assertEqual(events[-1],['write4',0x20028000,0xffffffff])
        self.assertEqual(sum(e[:2]==['read4',0x2002b100] for e in events),1)
    def test_output_alias_clears_profile_pointer(self):
        result,events=oracle(False,0x20029010,0x85,0,0,[],2,0)
        self.assertEqual(result,0xffffffff)
        self.assertFalse(any(e[0]=='call' for e in events))
        self.assertEqual(events[2],['read4',0x20029010,0])
    def test_output_alias_clears_matching_length(self):
        result,events=oracle(False,0x2002b204,0x85,0,0,[(0,0,0,0,0xffffffff)],2,0)
        self.assertEqual(result,0)
        self.assertEqual(events[-1],['write4',0x2002b204,0])
    def test_mode_does_not_require_count(self):
        result,events=oracle(True,0,0,0,0,[],2,0)
        self.assertEqual(result,1)
        self.assertEqual(len(events),3)
    def test_wrong_access_width(self):
        with self.assertRaisesRegex(ValueError,'effect'):
            execute({0:('ld.b','r0, (r0, 0x0)',2)},0,0,[['read4',64,0]],64,0)
    def test_extra_call(self):
        with self.assertRaisesRegex(ValueError,'extra effect'):
            execute({0:('bsr','0x1002375c',4)},0,0,[],0,0)
    def test_missing_effect(self):
        with self.assertRaisesRegex(ValueError,'return mismatch'):
            execute({0:('rts','',2)},0,0,[['read4',64,0]],0,0)
    def test_preserved_register(self):
        with self.assertRaisesRegex(ValueError,'return mismatch'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,0,[],0,0)
    def test_unknown_opcode(self):
        with self.assertRaisesRegex(ValueError,'instruction'):
            execute({0:('not-an-instruction','',2)},0,0,[],0,0)
if __name__=='__main__':unittest.main()
