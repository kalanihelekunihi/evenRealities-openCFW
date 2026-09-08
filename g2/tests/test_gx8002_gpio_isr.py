# SPDX-License-Identifier: MIT
import unittest
from tools import verify_gx8002_gpio_isr as v


class GPIOTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = v.verify()
        cls.old, cls.new = v.programs()

    def mutate(self, op, args):
        code = self.new.copy()
        pc = next(pc for pc, (o, a, w) in code.items() if o == op)
        _, _, width = code[pc]
        code[pc] = (op, args, width)
        return code

    def test_cases(self):
        self.assertEqual(self.report['cases'], 864)

    def test_live_callback_changes(self):
        case = v.Case(pending=0xffffffff, callbacks=1, mutation=True)
        self.assertEqual(v.execute(self.new, v.ADDRESS, case), v.expected(case))

    def test_wrong_ack_mask(self):
        case = v.Case(pending=3)
        code = self.mutate('st.w', 'r8, (r6, 0x30)')
        self.assertNotEqual(v.execute(code, v.ADDRESS, case), v.expected(case))

    def test_wrong_pending_address(self):
        code = self.mutate('ld.w', 'r8, (r6, 0x34)')
        with self.assertRaisesRegex(ValueError, 'bounds'):
            v.execute(code, v.ADDRESS, v.Case())

    def test_wrong_frame(self):
        with self.assertRaisesRegex(ValueError, 'frame'):
            v.execute(self.mutate('pop', 'r4-r8, r15'), v.ADDRESS, v.Case())

    def test_wrong_callback_target(self):
        case = v.Case(pending=1)
        self.assertNotEqual(v.execute(self.mutate('jsr', 'r2'), v.ADDRESS, case), v.expected(case))


if __name__ == '__main__':
    unittest.main()
