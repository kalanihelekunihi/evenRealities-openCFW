#!/usr/bin/env python3
"""Guard EM9305 exact-neighbor link-order recovery invariants."""

from __future__ import annotations

import importlib.util
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools/analyze_em9305_sdk_link_order.py"


def load_tool():
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        spec = importlib.util.spec_from_file_location("analyze_em9305_sdk_link_order", TOOL)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


def function(name, size, matches, *, compared=16, masked=0):
    return {
        "name": name,
        "size": size,
        "matches": matches,
        "compared_byte_count": compared,
        "masked_byte_count": masked,
        "normalized_sha256": name.lower() * 4,
        "object": f"{name}.c.obj",
    }


class Em9305SdkLinkOrderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tool = load_tool()

    def test_exact_size_gap_resolves_nonunique_body(self) -> None:
        report = {"functions": [
            function("AnchorA", 16, [0x100]),
            function("Between", 16, [0x110, 0x900], compared=12, masked=4),
            function("ClosingAnchor", 16, [0x120]),
        ]}
        known = [
            {"address": 0x100, "end": 0x110},
            {"address": 0x120, "end": 0x130},
        ]
        placements = self.tool.discover_placements(report, known)
        self.assertEqual(len(placements), 1)
        self.assertEqual(placements[0]["address"], 0x110)
        self.assertEqual(
            placements[0]["status"], "sdk_archive_exact_link_order_resolved"
        )

    def test_gap_with_existing_exact_interval_is_not_claimed(self) -> None:
        report = {"functions": [
            function("AnchorA", 8, [0x100]),
            function("Between", 8, []),
            function("ClosingAnchor", 8, [0x110]),
        ]}
        known = [
            {"address": 0x100, "end": 0x108},
            {"address": 0x10A, "end": 0x10C},
            {"address": 0x110, "end": 0x118},
        ]
        self.assertEqual(self.tool.discover_placements(report, known), [])

    def test_pinned_totals_partition_all_identified_bytes(self) -> None:
        self.assertEqual(sum(self.tool.EXPECTED_STATUS_COUNTS.values()), 46)
        self.assertEqual(sum(self.tool.EXPECTED_STATUS_BYTES.values()), 2116)
        self.assertEqual(sum(self.tool.EXPECTED_NOP_AWARE_STATUS_COUNTS.values()), 156)
        self.assertEqual(sum(self.tool.EXPECTED_NOP_AWARE_STATUS_BYTES.values()), 9818)
        self.assertEqual(len(self.tool.EXPECTED_MODIFIED), 9)
        self.assertEqual(sum(self.tool.EXPECTED_VECTOR_HANDLER_STATUS_COUNTS.values()), 4)
        self.assertEqual(sum(self.tool.EXPECTED_VECTOR_HANDLER_STATUS_BYTES.values()), 760)
        self.assertEqual(self.tool.EXPECTED_SHORT_PREFIX_FUNCTIONS, 6)
        self.assertEqual(self.tool.EXPECTED_ALL_EXACT_FUNCTIONS, 1494)
        self.assertEqual(self.tool.EXPECTED_ALL_EXACT_BYTES, 157122)
        self.assertEqual(self.tool.EXPECTED_ALL_PROVENANCE_BYTES, 167684)

    def test_nop_aware_gap_trims_alignment_before_tiling(self) -> None:
        report = {"functions": [
            function("AnchorA", 8, [0x100]),
            function("Between", 8, []),
            function("ClosingAnchor", 8, [0x114]),
        ]}
        known = [
            {"address": 0x100, "end": 0x108, "names": ["AnchorA"]},
            {"address": 0x114, "end": 0x11C, "names": ["ClosingAnchor"]},
        ]
        application = bytearray(0x200)
        application[0x108:0x10A] = b"\xe0\x78"
        application[0x112:0x114] = b"\xe0\x78"
        old_base = self.tool.discovery.APP_BASE
        self.tool.discovery.APP_BASE = 0
        try:
            placements = self.tool.discover_nop_aware_placements(
                report, known, [], bytes(application)
            )
        finally:
            self.tool.discovery.APP_BASE = old_base
        self.assertEqual([(item["address"], item["end"]) for item in placements], [(0x10A, 0x112)])

    def test_vector_abi_disambiguates_duplicate_interrupt_bodies(self) -> None:
        application = bytearray(self.tool.discovery.APP_SIZE)
        definitions = [
            (16, "IRQHandler_ArcTimer0", 0x00305B1C, 194),
            (17, "IRQHandler_ArcTimer1", 0x00305BE0, 194),
            (36, "IRQHandler_RadioTx", 0x00306440, 186),
            (37, "IRQHandler_RadioRx", 0x00306384, 186),
        ]
        for vector_index, _name, address, size in definitions:
            struct.pack_into("<I", application, vector_index * 4, address)
            offset = address + size - self.tool.discovery.APP_BASE
            application[offset:offset + 2] = b"\xe0\x78"

        timer_matches = [0x00305B1C, 0x00305BE0]
        radio_matches = [0x00306384, 0x00306440]
        timer0 = function("IRQHandler_ArcTimer0", 194, timer_matches, compared=190, masked=4)
        timer1 = function("IRQHandler_ArcTimer1", 194, timer_matches, compared=190, masked=4)
        timer0["normalized_sha256"] = timer1["normalized_sha256"] = "a" * 64
        radio_tx = function("IRQHandler_RadioTx", 380, [], compared=368, masked=12)
        radio_rx = function("IRQHandler_RadioRx", 186, radio_matches, compared=182, masked=4)
        em_hw = {
            "identity": {
                "archive_kind": "em_hw_api",
                "archive_git_blob": "729ca978bb728f0289db4b3ee743e333670e4dc1",
                "archive_sha256": "74888e6952ff261b080e50c6267eed3e77d3a931dbe2dbb12f910068ca229865",
                "compiler_anchors_matched": True,
            },
            "functions": [timer0, timer1],
        }
        radio = {
            "identity": {
                "archive_kind": "radio",
                "archive_git_blob": "00ce66bc3ff9968c8b233fd740332fde85d061b4",
                "archive_sha256": "de6ae31e5bf6436533296efa116c17a4fa37c3cce7652118b0b3e9e2474759cc",
                "compiler_anchors_matched": True,
            },
            "functions": [radio_tx, radio_rx],
        }
        placements = self.tool.discover_vector_handler_placements(
            em_hw, radio, bytes(application)
        )
        self.assertEqual([item["name"] for item in placements], [item[1] for item in definitions])
        self.assertEqual(
            placements[2]["status"],
            "sdk_archive_vector_identified_vendor_modified_size_delta",
        )
        self.assertEqual(placements[2]["size_delta"], -194)
        self.assertEqual(placements[2]["implementation_alias"], "IRQHandler_RadioRx")


if __name__ == "__main__":
    unittest.main()
