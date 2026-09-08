# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_uart_tick import execute

class UartTickTargetTests(unittest.TestCase):
    def test_halfword_zero_extension(self):
        code={0:('push','r15',2),2:('lrw','r1, 0x2002e360',2),4:('ld.h','r0, (r1, 0x0)',2),6:('pop','r15',2)}
        self.assertEqual(execute(code,0,{},None,b'\xff\xff',0,0),(65535,[]))

    def test_unknown_call_and_opcode_rejected(self):
        with self.assertRaisesRegex(ValueError,'unknown direct call'):
            execute({0:('bsr','0x100',4)},0,{},None,b'',0,0)
        with self.assertRaisesRegex(ValueError,'unsupported instruction'):
            execute({0:('unknown','',2)},0,{},None,b'',0,0)

if __name__=='__main__':unittest.main()
