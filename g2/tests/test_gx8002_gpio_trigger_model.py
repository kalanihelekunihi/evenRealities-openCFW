# SPDX-License-Identifier: MIT
import unittest
from tools import model_gx8002_gpio_trigger as m


class TriggerModelTests(unittest.TestCase):
    def test_invalid_port_has_no_effects(self):
        for port in (32, 0xffffffff, 0x80000000):
            trace, words, result = m.expected(m.Case(port=port))
            self.assertEqual((trace, result), ([], 0xffffffff))

    def test_unsupported_trigger_still_registers(self):
        for trigger in (0, 5, 6, 7, 9, 0xffffffff):
            trace, words, result = m.expected(m.Case(trigger=trigger))
            self.assertEqual(trace[0], ('direction', 0, 0))
            self.assertEqual(trace[-1], ('request_irq', 1, 0x10205ee0, 0))
            self.assertFalse(any(x[0] == 'read' for x in trace))

    def test_pin31_mask(self):
        for trigger, offset in m.TRIGGER_OFFSETS.items():
            case = m.Case(port=31, trigger=trigger, seed=0xffffffff)
            trace, words, result = m.expected(case)
            self.assertTrue(words[m.BASE + offset] & 0x80000000)
            self.assertEqual(words[m.TABLE + 31 * 12 + 4], case.callback)
            self.assertLess(next(i for i, x in enumerate(trace) if x[0] == 'read'), len(trace)-1)


if __name__ == '__main__':
    unittest.main()
