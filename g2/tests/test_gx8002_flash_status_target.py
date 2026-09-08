# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_status import execute

class StatusTests(unittest.TestCase):
    def test_uninitialized_status(self):
        with self.assertRaisesRegex(ValueError,'uninitialized status byte'):
            execute({0:('ld.b','r0, (r14, 0x3)',4)},0,0,[])
    def test_unknown_transport(self):
        with self.assertRaisesRegex(ValueError,'unknown transport call'):
            execute({0:('bsr','0x20',4)},0,0,[])
    def test_invalid_write_command(self):
        with self.assertRaisesRegex(ValueError,'invalid write enable contract'):
            execute({0:('bsr','0x100236dc',4)},0,0,[])
    def test_unconsumed_status(self):
        code={0:('push','r15',2),2:('pop','r15',2)}
        with self.assertRaisesRegex(ValueError,'unconsumed status schedule'):
            execute(code,0,0,[1])

if __name__=='__main__':unittest.main()
