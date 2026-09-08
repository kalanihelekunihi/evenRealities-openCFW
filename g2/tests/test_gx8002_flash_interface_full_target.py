# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from compare_gx8002_flash_interface_full import execute
class InterfaceFullTests(unittest.TestCase):
    def run_code(self,code):return execute(code,0,0,0,0,0,0,0)
    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError,'unexpected setup frame'):
            self.run_code({0:('push','r15',2)})
    def test_saved_register_overwrite(self):
        code={0:('push','r4-r7, r15',2),2:('st.w','r0, (r14, 0x0)',2)}
        with self.assertRaisesRegex(ValueError,'overwrites saved register'):self.run_code(code)
    def test_xip_requires_initialized_arguments(self):
        with self.assertRaisesRegex(ValueError,'uninitialized XIP argument'):
            self.run_code({0:('bsr','0x1002436c',4)})
    def test_command_requires_local_byte(self):
        with self.assertRaisesRegex(ValueError,'command pointer'):
            self.run_code({0:('bsr','0x100236dc',4)})
    def test_unknown_call(self):
        with self.assertRaisesRegex(ValueError,'unknown setup call'):
            self.run_code({0:('bsr','0x12345678',4)})
if __name__=='__main__':unittest.main()
