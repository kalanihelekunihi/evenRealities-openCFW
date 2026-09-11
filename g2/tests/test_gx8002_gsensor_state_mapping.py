# SPDX-License-Identifier: MIT
"""Reject changed evidence before mapping a sensor state word."""
import copy
import unittest
from unittest.mock import patch
import analyze_gx8002_gsensor_state_references as state

class StateMappingTests(unittest.TestCase):
    def setUp(self):
        self.layout = state.section_map()
        self.sdk = state.ROOT/'build/upstream-nationalchip-lvp-kws'

    def test_known_word_and_section_endpoints(self):
        for address, offset in ((0x20026c70, 0x18c84), (0x200264e8, 0x184fc), (0x20026d78, 0x18d8c)):
            self.assertEqual(state.mapped_offset(address, self.layout, self.sdk), offset)

    def test_rejects_outside_and_unaligned_words(self):
        for address in (0x200264e4, 0x20026d7c, 0x20026c71, 0x10026c70):
            with self.assertRaises(ValueError):
                state.mapped_offset(address, self.layout, self.sdk)

    def test_rejects_changed_stock_layout(self):
        layout = copy.deepcopy(self.layout)
        layout['image_a']['stage2']['sram_data']['size'] -= 4
        with self.assertRaisesRegex(ValueError, 'section changed'):
            state.mapped_offset(0x20026c70, layout, self.sdk)

    def test_rejects_changed_sdk_evidence(self):
        with patch.object(state, 'SDK_EVIDENCE', {'arch/soc/grus/link.ld': '0'*64}):
            with self.assertRaisesRegex(ValueError, 'SDK memory-map evidence changed'):
                state.mapped_offset(0x20026c70, self.layout, self.sdk)
