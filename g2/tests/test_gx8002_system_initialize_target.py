# SPDX-License-Identifier: MIT
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_system_mpu import execute


class SystemInitializeTests(unittest.TestCase):
    def test_unknown_service(self):
        with self.assertRaisesRegex(ValueError,'unexpected service call'):
            execute({0:('bsr','0x1234',4)},0,{},full=True)

    def test_unknown_mmio(self):
        with self.assertRaisesRegex(ValueError,'unexpected MMIO address'):
            execute({0:('movi','r3, 0',2),2:('st.w','r0, (r3, 0x0)',4)},0,{},full=True)

    def test_missing_return_frame(self):
        with self.assertRaisesRegex(ValueError,'unexpected return frame'):
            execute({0:('pop','r15',2)},0,{},full=True)

    def test_missing_exception_enable(self):
        with self.assertRaisesRegex(ValueError,'unexpected PSR enable'):
            execute({0:('psrset','ie',4)},0,{},full=True)


if __name__=='__main__':unittest.main()
