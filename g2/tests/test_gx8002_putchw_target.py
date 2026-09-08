# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_putchw import execute

class PaddingTargetTests(unittest.TestCase):
    def test_output_failure_return_and_save(self):
        code={0:('push','r4, r15',2),2:('movi','r1, 65',2),4:('bsr','0x100',4),8:('pop','r4, r15',2)}
        args=(0,0,0,0,10,0,b'',1)
        self.assertEqual(execute(code,0,256,*args),(0,b'A'))
        self.assertEqual(execute(code,0,256,*args[:-1],0),(1,b'A'))

    def test_bad_call_and_unknown_instruction_rejected(self):
        args=(0,0,0,0,10,0,b'',0)
        with self.assertRaisesRegex(ValueError,'unexpected output call'):
            execute({0:('bsr','0x102',4)},0,256,*args)
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('unknown','',2)},0,256,*args)

if __name__=='__main__':unittest.main()
