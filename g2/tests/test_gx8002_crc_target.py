# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_crc import execute

class CrcTargetTests(unittest.TestCase):
    def test_little_endian_post_increment_word(self):
        code={0:('ldbi.w','r3, (r1)',4),4:('ldbi.w','r0, (r1)',4),8:('rts','',2)}
        result,trace=execute(code,0,0,0x2000,bytes(range(8)))
        self.assertEqual(result,0x07060504)
        self.assertEqual(trace,[(0x2000,4),(0x2004,4)])

    def test_decrement_branch_and_wraparound(self):
        code={0:('subi','r0, 1',2),2:('bnezad','r2, 0x0',4),6:('rts','',2)}
        self.assertEqual(execute(code,0,0,0x2000,b'ab')[0],0xfffffffe)

    def test_outside_input_and_unknown_opcode_rejected(self):
        with self.assertRaisesRegex(ValueError,'out-of-bounds'):
            execute({0:('ld.b','r0, (r1, 0x0)',2)},0,0,0x2000,b'')
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('unknown','',2)},0,0,0x2000,b'')

if __name__=='__main__':unittest.main()
