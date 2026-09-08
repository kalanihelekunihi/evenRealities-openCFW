# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_spi_read import execute

class TransportTests(unittest.TestCase):
    def test_read_past_buffer(self):
        with self.assertRaisesRegex(ValueError,'buffer overrun'):
            execute({0:('ldbi.b','r2, (r1)',4)},0,0,0x20028000,0,[],0)
    def test_write_past_buffer(self):
        with self.assertRaisesRegex(ValueError,'buffer overrun'):
            execute({0:('stbi.b','r2, (r1)',4)},0,0,0x20028000,0,[],0)
    def test_wrong_mmio_order(self):
        code={0:('movi','r3, 0',2),2:('ld.w','r0, (r3, 0x0)',2)}
        with self.assertRaisesRegex(ValueError,'effect mismatch'):
            execute(code,0,0,0,0,[['read',0xa2000028,0]],0)
    def test_unknown_helper(self):
        with self.assertRaisesRegex(ValueError,'unknown polling helper'):
            execute({0:('bsr','0x20',4)},0,0,0,0,[],0)

if __name__=='__main__':unittest.main()
