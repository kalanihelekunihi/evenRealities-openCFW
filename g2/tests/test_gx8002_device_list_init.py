# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_device_list_init as v


class DeviceListInitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.code=v.decode((v.ROOT/'build/gx8002-board/device-list-init-candidate.disassembly.txt').read_text())

    def test_circular_heads(self):
        self.assertEqual(self.report['semantics']['ordered_writes'],[[0x20027ad0,0x20027ad0],[0x20027ad4,0x20027ad0],[0x20027ad8,0x20027ad8],[0x20027adc,0x20027ad8]])

    def test_wrong_second_head(self):
        code=self.code.copy();code[v.ADDRESS+2]=('addi','r2, r3, 4',2)
        with self.assertRaises(ValueError):v.prove(code)

    def test_crosslinked_head_rejected(self):
        code=self.code.copy();code[v.ADDRESS+8]=('st.w','r3, (r3, 0x8)',2)
        with self.assertRaises(ValueError):v.prove(code)


if __name__=='__main__':unittest.main()
