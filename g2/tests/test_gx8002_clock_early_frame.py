# SPDX-License-Identifier: MIT
import struct
import unittest
from tools import verify_gx8002_clock_early_frame as v

class EarlyFrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.analyze();out=v.ROOT/'build/gx8002-clock-frequency-table-probe'
        cls.code=v.decode((out/'placement.disassembly.txt').read_text())
        elf=v.Elf32((out/'placement.elf').read_bytes(),'early frame')
        cls.table=struct.unpack('<19I',elf.contents(next(s for s in elf.sections if s['name']=='.rodata.open_cfw_gx8002_clock_frequency')))
    def test_early_paths_restore_frame(self):
        for module,result in ((7,0),(0,1),(0,0)):
            self.assertEqual(v.execute(self.code,self.table,module,result,255)[0],0)
    def test_wrong_stack_allocation_rejected(self):
        code=self.code.copy();op,args,width=code[0x10025212]
        code[0x10025212]=(op,'r14, r14, 20',width)
        with self.assertRaisesRegex(ValueError,'lookup ABI'):v.execute(code,self.table,0,1,255)
    def test_wrong_restore_rejected(self):
        code=self.code.copy();op,args,width=code[0x10025248]
        code[0x10025248]=(op,'r14, r14, 20',width)
        with self.assertRaises(ValueError):v.execute(code,self.table,7,0,255)

if __name__=='__main__':unittest.main()
