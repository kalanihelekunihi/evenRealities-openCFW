# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_snpu_device import ROOT,FUNCTIONS,DELTA,decode,execute

class SnpuDeviceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode((ROOT/'build/gx8002-board/snpu-device-candidate.disassembly.txt').read_text())
        cls.entries={n:o+DELTA for n,o,size in FUNCTIONS}

    def run_case(self,name,handler=0x10026000,data=0x20020000,code=None):
        return execute(self.code if code is None else code,self.entries[name],0,name,handler,data,0xffffffff)

    def test_original_empty_hooks(self):
        for name in ('snpu_device_init','snpu_device_exit'):self.assertEqual(self.run_case(name),[])

    def test_irq_forwarding(self):
        self.assertEqual(self.run_case('snpu_request_irq'),[[0x1002553c,12,0x10026000,0x20020000]])

    def test_null_forwarded_for_helper_validation(self):
        self.assertEqual(self.run_case('snpu_request_irq',0,0xffffffff),[[0x1002553c,12,0,0xffffffff]])

    def test_wrong_irq_detected(self):
        c=self.code.copy();c[self.entries['snpu_request_irq']+6]=('movi','r0, 11',2)
        self.assertNotEqual(self.run_case('snpu_request_irq',code=c),self.run_case('snpu_request_irq'))

    def test_swapped_data_detected(self):
        c=self.code.copy();c[self.entries['snpu_request_irq']+2]=('mov','r2, r0',2)
        self.assertNotEqual(self.run_case('snpu_request_irq',code=c),self.run_case('snpu_request_irq'))

    def test_wrong_helper_rejected(self):
        c=self.code.copy();c[self.entries['snpu_request_irq']+8]=('bsr','0x100254ac',4)
        with self.assertRaisesRegex(ValueError,'unknown helper'):self.run_case('snpu_request_irq',code=c)

    def test_frame_not_restored_rejected(self):
        c=self.code.copy();c[self.entries['snpu_request_irq']+12]=('rts','',2)
        with self.assertRaisesRegex(ValueError,'changed state'):self.run_case('snpu_request_irq',code=c)

    def test_empty_hook_state_change_rejected(self):
        c=self.code.copy();pc=self.entries['snpu_device_init'];c[pc]=('movi','r0, 0',2);c[pc+2]=('rts','',2)
        with self.assertRaisesRegex(ValueError,'changed state'):self.run_case('snpu_device_init',code=c)

if __name__=='__main__':unittest.main()
