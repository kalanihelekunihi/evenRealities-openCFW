# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_clock_divider as v

class DividerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        v.build();cls.code=v.decode((v.ROOT/'build/gx8002-board/clock-divider-candidate.disassembly.txt').read_text())

    def test_absent_descriptor_returns_zero_without_mmio(self):
        self.assertEqual(v.execute(self.code,v.ADDRESS,False,0xa0010000,128,8,63,0xffffffff),([('read',v.PARAM+8,4,0)],0))

    def test_zero_and_max_divider(self):
        for word,want in ((0,0),(63<<8,64)):
            self.assertEqual(v.execute(self.code,v.ADDRESS,True,0xa0010000,128,8,63,word)[1],want)

    def test_mask_read_width_mutation_rejected(self):
        code=self.code.copy();pc=next(pc for pc,(op,a,w) in code.items() if op=='ld.h')
        op,args,w=code[pc];code[pc]=('ld.b',args,w)
        with self.assertRaisesRegex(ValueError,'address/width'):v.execute(code,v.ADDRESS,True,0xa0010000,128,8,63,0)

if __name__=='__main__':unittest.main()
