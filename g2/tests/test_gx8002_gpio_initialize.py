# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_gpio_initialize as v


class GPIOInitializeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report=v.verify();cls.code=v.decode((v.ROOT/'build/gx8002-board/gpio-initialize-candidate.disassembly.txt').read_text())

    def test_ordered_effects(self):
        self.assertEqual(self.report['semantics']['ordered_effects'],[['platform_gate',4,1],['write32',0xa0001034,0]])

    def test_wrong_helper(self):
        code=self.code.copy();code[v.ADDRESS+6]=('bsr','0x10025084',4)
        with self.assertRaises(ValueError):v.prove(code)

    def test_wrong_control_register(self):
        code=self.code.copy();code[v.ADDRESS+20]=('st.w','r0, (r3, 0x30)',2)
        with self.assertRaises(ValueError):v.prove(code)

    def test_wrong_frame(self):
        code=self.code.copy();code[v.ADDRESS]=('push','r4, r15',2)
        with self.assertRaises(ValueError):v.prove(code)


if __name__=='__main__':unittest.main()
