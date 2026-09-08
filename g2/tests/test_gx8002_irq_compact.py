# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_compact import ROOT,decode,execute
class CompactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-irq/compact.disassembly.txt').read_text())
    def test_missing_link_save_rejected(self):
        code=self.code.copy();pc=next(p for p,row in code.items() if row[0]=='push');code[pc]=('addi','r14, r14, 0',2)
        with self.assertRaisesRegex(ValueError,'callback contract'):execute(code,32,0x10026000,0)
    def test_wrong_slot_stride_rejected(self):
        code=self.code.copy();pc=next(p for p,row in code.items() if row[0]=='ldr.w');code[pc]=('ldr.w','r2, (r3, r0 << 2)',4)
        with self.assertRaisesRegex(ValueError,'slot addressing'):execute(code,32,0,0)
    def test_missing_fp_restore_rejected(self):
        code=self.code.copy();pc=next(p for p,row in code.items() if row[0]=='fldms');code[pc]=('fldms','fr0-fr6, (r14)',4)
        with self.assertRaisesRegex(ValueError,'context restoration'):execute(code,32,0x10026000,0)
    def test_unreachable_nested_point_rejected(self):
        with self.assertRaisesRegex(ValueError,'injection point not reached'):
            execute(self.code,32,0,0,depth=1,interrupt_pc=0x1234)
    def test_nested_entry_preserves_outer_stack(self):
        outer={0x8004:123}
        result=execute(self.code,32,0x10026000,0,depth=3,interrupt_pc=0x10025576,stack=outer)
        self.assertEqual(outer,{0x8004:123})
        self.assertEqual(result['peak_bytes'],148)
    def test_pre_nie_nesting_rejected(self):
        with self.assertRaisesRegex(ValueError,'control not yet saved'):
            execute(self.code,32,0,0,depth=1,interrupt_pc=0x10025574)
    def test_null_handler_does_not_read_private(self):
        result=execute(self.code,32,0,123)
        self.assertEqual(len(result['trace']),2)
        self.assertEqual(result['peak_bytes'],124)
if __name__=='__main__':unittest.main()
