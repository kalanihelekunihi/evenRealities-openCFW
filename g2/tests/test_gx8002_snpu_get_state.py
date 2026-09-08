# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_snpu_get_state as v


class StateQueryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v.verify()
        cls.code = v.decode((v.ROOT / 'build/gx8002-board/snpu-get-state-candidate.disassembly.txt').read_text())

    def test_exact_single_load(self):
        self.assertEqual(self.report['semantics']['reads'], 1)
        self.assertEqual(self.report['evidence']['compiled_bytes'], 12)

    def test_wrong_state_address(self):
        code = self.code.copy()
        code[v.ADDRESS] = ('lrw', 'r3, 0x20027354', 2)
        with self.assertRaises(ValueError):
            v.prove(code)

    def test_write_instead_of_read(self):
        code = self.code.copy()
        code[v.ADDRESS + 2] = ('st.w', 'r0, (r3, 0x0)', 2)
        with self.assertRaises(ValueError):
            v.prove(code)

    def test_wrong_return_register(self):
        code = self.code.copy()
        code[v.ADDRESS + 2] = ('ld.w', 'r4, (r3, 0x0)', 2)
        with self.assertRaises(ValueError):
            v.prove(code)


if __name__ == '__main__':
    unittest.main()
