# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_start_mode import execute


class StartModeTests(unittest.TestCase):
    def test_unknown_read(self):
        with self.assertRaisesRegex(ValueError,'unknown MMIO read'):
            execute({0:('movi','r3, 0',2),2:('ld.w','r0, (r3, 0x0)',2)},0,{},100)

    def test_unknown_callee(self):
        with self.assertRaisesRegex(ValueError,'unknown nested call'):
            execute({0:('bsr','0x20',4)},0,{},100)

    def test_unbalanced_return(self):
        with self.assertRaisesRegex(ValueError,'unexpected return'):
            execute({0:('pop','r15',2)},0,{},100)

    def test_unsigned_reason_underflow(self):
        code={0:('movi','r0, 0',2),2:('subi','r0, 2',2),
              4:('cmphsi','r0, 4',2),6:('bt','0xc',2),
              8:('movi','r0, 99',2),10:('rts','',2),
              12:('movi','r0, 0',2),14:('rts','',2)}
        self.assertEqual(execute(code,0,{},100),(0,[]))


if __name__=='__main__':unittest.main()
