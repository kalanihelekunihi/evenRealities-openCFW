# SPDX-License-Identifier: MIT
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from verify_gx8002_irq_mask import ROOT,decode,execute
class IrqMaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.code=decode((ROOT/'build/gx8002-board/irq-mask-candidate.disassembly.txt').read_text())
    def test_mask_disables(self):self.assertEqual(execute(self.code,0x100254fc,0,12,0),[[0x100254c8,12]])
    def test_unmask_enables(self):self.assertEqual(execute(self.code,0x10025504,0,12,0),[[0x100254ac,12]])
    def test_high_bits_preserved(self):
        for irq in (0x80000000,0xffffffff):self.assertEqual(execute(self.code,0x100254fc,0,irq,0xffffffff),[[0x100254c8,irq]])
    def test_reversed_operation_detected(self):
        c=self.code.copy();c[0x100254fe]=('bsr','0x100254ac',4)
        self.assertNotEqual(execute(c,0x100254fc,0,12,0),[[0x100254c8,12]])
    def test_wrong_frame(self):
        c=self.code.copy();c[0x10025502]=('pop','r4, r15',2)
        with self.assertRaisesRegex(ValueError,'return frame'):execute(c,0x100254fc,0,12,0)
if __name__=='__main__':unittest.main()
