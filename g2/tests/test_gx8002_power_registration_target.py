# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_power_registration import execute

class RegistryTargetTests(unittest.TestCase):
    def test_indexed_word_load(self):
        code={0:('push','r4, r15',2),2:('lrw','r4, 0x2002dfbc',2),4:('movi','r2, 1',2),6:('ldr.w','r0, (r4, r2 << 3)',4),10:('pop','r4, r15',2)}
        state=bytes(range(144))
        self.assertEqual(execute(code,0,256,state,b'\0'*8),(0x0b0a0908,state,[]))

    def test_bad_copy_rejected(self):
        with self.assertRaisesRegex(ValueError,'bad copy call'):
            execute({0:('bsr','0x102',4)},0,256,b'\0'*144,b'\0'*8)

if __name__=='__main__':unittest.main()
