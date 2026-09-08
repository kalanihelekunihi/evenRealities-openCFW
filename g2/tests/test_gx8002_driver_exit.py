# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_driver_exit import ROOT,decode,execute,expected
class DriverExitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/driver-exit-candidate.disassembly.txt').read_text())
    def run_case(self,code=None,pc=0x10205d40,result=0):return execute(self.code if code is None else code,pc,0,0xdeadbeef,result)
    def test_success_exits_device(self):self.assertEqual(self.run_case(),expected('gx_snpu_exit',0))
    def test_failure_still_unmasks(self):self.assertEqual(self.run_case(result=0xffffffff),expected('gx_snpu_exit',0xffffffff))
    def test_audio_order(self):self.assertEqual(self.run_case(pc=0x10204984),expected('gx_audio_in_exit',0))
    def test_wrong_irq(self):
        c=self.code.copy();c[0x10205d4e]=('movi','r0, 11',2)
        self.assertNotEqual(self.run_case(c),expected('gx_snpu_exit',0))
    def test_return_must_survive_helper_clobber(self):
        c=self.code.copy();c[0x10205d5c]=('mov','r0, r1',2)
        self.assertNotEqual(self.run_case(c,result=5),expected('gx_snpu_exit',5))
    def test_wrong_branch(self):
        c=self.code.copy();c[0x10205d54]=('bnez','r4, 0x10205d58',4)
        self.assertNotEqual(self.run_case(c,result=1),expected('gx_snpu_exit',1))
    def test_wrong_gate(self):
        c=self.code.copy();c[0x1020499c]=('movi','r0, 7',2)
        self.assertNotEqual(self.run_case(c,pc=0x10204984),expected('gx_audio_in_exit',0))
    def test_wrong_frame(self):
        c=self.code.copy();c[0x10205d5e]=('pop','r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):self.run_case(c)
if __name__=='__main__':unittest.main()
