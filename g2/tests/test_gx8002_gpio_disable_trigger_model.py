# SPDX-License-Identifier: MIT
import unittest
from tools import model_gx8002_gpio_disable_trigger as m


class DisableTriggerModelTests(unittest.TestCase):
    def test_invalid_port_no_effects(self):
        trace, words, result = m.expected(m.Case(port=32))
        self.assertEqual((trace, result), ([], m.MASK))

    def test_order_and_cleanup(self):
        trace, words, result = m.expected(m.Case(port=31))
        self.assertEqual(trace[0], ('direction', 31, 2))
        self.assertEqual([event[1]-m.BASE for event in trace if event[0]=='read'], [0x14,0x18,0x28,0x2c,0x24])
        self.assertEqual([words[m.TABLE+31*12+offset] for offset in (0,4,8)], [255,0,0])

    def test_other_pins_preserved(self):
        case=m.Case(port=7,seed=0x12345678)
        initial=m.Model(case).words
        trace,words,result=m.expected(case)
        for offset in (0x14,0x18,0x28,0x2c,0x24):
            address=m.BASE+offset
            self.assertEqual(words[address],initial[address]&~128)


if __name__=='__main__':unittest.main()
