# SPDX-License-Identifier: MIT
import unittest
from tools import model_gx8002_gpio_isr as m


class GPIOModelTests(unittest.TestCase):
    def test_empty_snapshot(self):
        trace, words, result = m.expected(m.Case())
        self.assertEqual(trace, [('read', m.PENDING, 0)])

    def test_ack_without_callback(self):
        trace, words, result = m.expected(m.Case(pending=8, callbacks=0))
        self.assertEqual(trace[-1], ('write', m.PENDING, 8))
        self.assertFalse(any(x[0] == 'callback' for x in trace))

    def test_snapshot_ignores_new_pending_bits(self):
        trace, words, result = m.expected(m.Case(pending=1, mutation=True))
        self.assertEqual(sum(x[0] == 'callback' for x in trace), 1)
        self.assertEqual(sum(x[:2] == ('read', m.PENDING) for x in trace), 1)

    def test_later_callback_is_live(self):
        trace, words, result = m.expected(m.Case(pending=3, callbacks=1, mutation=True))
        callbacks = [x for x in trace if x[0] == 'callback']
        self.assertEqual([x[1] for x in callbacks], [0x10201000, 0x10202004])


if __name__ == '__main__':
    unittest.main()
