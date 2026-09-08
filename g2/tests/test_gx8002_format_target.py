# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_format import execute

class FormatTargetTests(unittest.TestCase):
    def test_stack_storage_multiply_and_character_call(self):
        code={0:('push','r4, r15',2),2:('subi','r14, r14, 4',2),
              4:('movi','r3, 5',2),6:('movi','r2, 6',2),8:('movi','r1, 35',2),
              10:('mula.32.l','r1, r2, r3',4),14:('st.w','r1, (r14, 0x0)',2),
              16:('ld.w','r1, (r14, 0x0)',2),18:('bsr','0x100',4),
              22:('addi','r14, r14, 4',2),24:('pop','r4, r15',2)}
        self.assertEqual(execute(code,0,{256:'character'},b'',[]),(1,b'A'))
        self.assertEqual(execute(code,0,{256:'character'},b'',[],1),(0,b'A'))

    def test_outside_arguments_and_unknown_helper_rejected(self):
        with self.assertRaisesRegex(ValueError,'outside memory'):
            execute({0:('ldbi.w','r0, (r2)',4)},0,{},b'',[])
        with self.assertRaisesRegex(ValueError,'unknown helper'):
            execute({0:('bsr','0x100',4)},0,{},b'',[])

if __name__=='__main__':unittest.main()
