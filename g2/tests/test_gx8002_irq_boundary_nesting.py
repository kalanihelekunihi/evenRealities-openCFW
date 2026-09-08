# SPDX-License-Identifier: MIT
import sys,unittest,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_software_frame import ROOT,decode,execute
class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code=decode(subprocess.check_output([str(ROOT/'build/csky-macos/install/bin/csky-unknown-elf-objdump'),'-d',str(ROOT/'build/gx8002-irq/entry.elf')],text=True))
    def test_unreachable_injection_rejected(self):
        with self.assertRaisesRegex(ValueError,'injection point not reached'):
            execute(self.code,0x10025574,0,1,architecture=True,interrupt_pc=0x1234)
    def test_boundary_requires_architecture(self):
        with self.assertRaisesRegex(ValueError,'requires architecture'):
            execute(self.code,0x10025574,0,1,interrupt_pc=0x10025574)
    def test_nested_initial_values_preserved(self):
        r={f'r{i}':0xa5a50000+i for i in range(32)}
        r.update({f'fr{i}':0x5a5a0000+i for i in range(8)})
        result=execute(self.code,0x10025574,0,2,architecture=True,interrupt_pc=0x10025574,initial_registers=r)
        self.assertEqual(result['calls'],1)
    def test_occupied_stack_rejected(self):
        with self.assertRaisesRegex(ValueError,'overlaps saved state'):
            execute(self.code,0x10025574,0,1,stack={0x7ffc:123},architecture=True,interrupt_pc=0x10025574)
if __name__=='__main__':unittest.main()
