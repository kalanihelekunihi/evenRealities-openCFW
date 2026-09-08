# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_dw_spi_cleanup as v


class CleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.code=v.decode((v.ROOT/'build/gx8002-board/dw-spi-cleanup-candidate.disassembly.txt').read_text())

    def test_pointer_chain(self):
        self.assertEqual(self.report['semantics']['pointer_read_offsets'],[0,24,4])
        self.assertEqual(self.report['semantics']['final_store_offset'],8)

    def test_wrong_private_field(self):
        code=self.code.copy();code[v.ADDRESS+4]=('ld.w','r3, (r3, 0x14)',2)
        with self.assertRaises(ValueError):v.prove(code)

    def test_wrong_register(self):
        code=self.code.copy();code[v.ADDRESS+8]=('st.w','r2, (r3, 0xc)',2)
        with self.assertRaises(ValueError):v.prove(code)

    def test_nonzero_write_rejected(self):
        code=self.code.copy();code[v.ADDRESS+2]=('movi','r2, 1',2)
        with self.assertRaises(ValueError):v.prove(code)


if __name__=='__main__':unittest.main()
