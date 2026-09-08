# SPDX-License-Identifier: MIT
import unittest
from tools.model_gx8002_dw_spi_setup import Case, expected, DEVICE, FIXED_STATE, OTHER_STATE, MASK

class SetupModelTests(unittest.TestCase):
    def test_defaults(self):
        trace, result = expected(Case())
        self.assertEqual(result, 0)
        self.assertIn(('write8', DEVICE + 9, 8), trace)
        self.assertIn(('write32', DEVICE + 4, 10000000), trace)
        self.assertIn(('write32', FIXED_STATE + 8, 10), trace)
        self.assertEqual(trace[-1], ('write32', DEVICE + 12, FIXED_STATE))

    def test_busy_state_still_updates_initial_defaults(self):
        trace, result = expected(Case(owner=DEVICE))
        self.assertEqual(result, 0xfffffff4)
        self.assertEqual([t[0] for t in trace], ['write16', 'read8', 'write8', 'read32', 'read32'])

    def test_existing_state_ignores_fixed_owner(self):
        trace, result = expected(Case(state=OTHER_STATE, owner=DEVICE, bits=16, speed=25))
        self.assertEqual(result, 0)
        self.assertFalse(any(t[1] == FIXED_STATE for t in trace))
        self.assertNotIn(('write8', DEVICE + 9, 8), trace)

    def test_even_divider_boundaries(self):
        for clock, speed, want in [(0, 1, 0), (1, 1, 2), (2, 1, 2), (3, 1, 4),
                                   (100, 30, 4), (100, 25, 4), (101, 25, 6),
                                   (MASK, 1, 0), (MASK, MASK, 2)]:
            trace, _ = expected(Case(clock=clock, speed=speed))
            self.assertIn(('write32', FIXED_STATE + 8, want), trace)

    def test_live_helper_changes(self):
        trace, _ = expected(Case(speed=25, clock=100, speed_after_call=20,
                                 format=255, mode_after_call=0xffff))
        self.assertIn(('read32', DEVICE + 4, 20), trace)
        self.assertIn(('write32', FIXED_STATE + 8, 6), trace)
        self.assertIn(('write32', FIXED_STATE + 4, 0x80c00300), trace)

    def test_zero_after_helper_not_silently_defaulted(self):
        with self.assertRaises(ValueError):
            expected(Case(speed_after_call=0))

if __name__ == '__main__':
    unittest.main()
