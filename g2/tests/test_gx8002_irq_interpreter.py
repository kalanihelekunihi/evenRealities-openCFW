# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_irq import execute

class IRQInterpreterTests(unittest.TestCase):
    def test_rejects_unknown_instruction(self):
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('bkpt','',2)},0,0)

    def test_rejects_wrong_call_target(self):
        with self.assertRaisesRegex(ValueError,'unexpected call'):
            execute({0:('bsr','0x20',4)},0,0,enable=0x40)

    def test_rejects_callee_saved_clobber(self):
        with self.assertRaisesRegex(ValueError,'ABI mismatch'):
            execute({0:('movi','r4, 0',2),2:('rts','',2)},0,0)

    def test_indexed_store_keeps_word_and_order(self):
        code={0:('movi','r3, 0x1000',2),2:('str.w','r2, (r3, r0 << 3)',4),6:('st.w','r1, (r3, 0x4)',2),8:('rts','',2)}
        self.assertEqual(execute(code,0,31,0xffffffff,0x12345678),[(0x10f8,0x12345678),(0x1004,0xffffffff)])

if __name__=='__main__':unittest.main()
