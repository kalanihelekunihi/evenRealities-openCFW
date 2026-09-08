# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_irq_dispatch import execute

class IRQDispatchTests(unittest.TestCase):
    def test_invalid_vector_is_not_claimed(self):
        for status in (0,31,64,511):
            with self.assertRaisesRegex(ValueError,'outside qualified IRQ domain'):
                execute({},0,status,0,0)
    def test_unknown_read(self):
        with self.assertRaisesRegex(ValueError,'unexpected read'):
            execute({0:('ld.w','r0, (r1, 0x0)',2)},0,32,0,0)
    def test_unknown_handler(self):
        with self.assertRaisesRegex(ValueError,'unexpected handler'):
            execute({0:('jsr','r0',2)},0,32,0,0)

if __name__=='__main__':unittest.main()
