#!/usr/bin/env python3
"""Guard the G2 BLE message TX/RX thread closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_thread_ble_messages.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_thread_ble_messages", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ThreadBleMessageAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_both_physical_translation_units_are_closed(self) -> None:
        tx = self.report["transmit"]["surface"]
        rx = self.report["receive"]["surface"]
        self.assertEqual((tx["bounded_bodies"], tx["body_bytes"]), (21, 3096))
        self.assertEqual((tx["physical_bytes"], tx["data_island_bytes"]), (3376, 280))
        self.assertEqual((rx["bounded_bodies"], rx["body_bytes"]), (13, 1390))
        self.assertEqual((rx["physical_bytes"], rx["data_island_bytes"]), (1524, 134))

    def test_static_thread_configuration_is_pinned(self) -> None:
        tx = self.report["transmit"]["thread"]
        rx = self.report["receive"]["thread"]
        self.assertEqual(
            (tx["name"], tx["entry"], tx["control_block"], tx["lifecycle_state"]),
            ("ble_msgtx", 0x00475290, 0x20004020, 8),
        )
        self.assertEqual(
            (rx["name"], rx["entry"], rx["control_block"], rx["lifecycle_state"]),
            ("ble_msgrx", 0x0048EDB0, 0x20003FFC, 7),
        )
        for thread, cb, stack in (
            (tx, 0x200721B0, 0x20047A98),
            (rx, 0x20072220, 0x2004BA98),
        ):
            self.assertEqual(thread["cmsis_control_block"], cb)
            self.assertEqual(thread["cmsis_control_block_bytes"], 0x70)
            self.assertEqual(thread["stack"], stack)
            self.assertEqual(thread["stack_bytes"], 0x4000)
            self.assertEqual(thread["priority"], 0x30)
            self.assertEqual(thread["queue_capacity"], 150)
            self.assertEqual(thread["queue_item_bytes"], 4)

    def test_queue_protocols_are_pinned(self) -> None:
        tx = self.report["transmit"]["protocol"]
        rx = self.report["receive"]["protocol"]
        for protocol in (tx, rx):
            self.assertEqual(protocol["queue_flag"], 0x00400000)
            self.assertEqual(protocol["exit_flag"], 0x00800000)
            self.assertEqual(protocol["wait_mask"], 0x00FFFFFF)
            self.assertEqual(protocol["queue_put_timeout"], 500)
        self.assertEqual(tx["queue_message_types"], [1, 2, 4, 8])
        self.assertEqual(tx["wsf_ready_probe_timeout"], 50)
        self.assertEqual(
            rx["queue_message_types"],
            [0x80, 0xC0, 0xC1, 0xC2, 0xC3, 0xC4, 0xC5, 0xC6, 0xC7, 0x200, 0x400],
        )
        self.assertEqual(rx["record_header_bytes"], 8)
        self.assertEqual(rx["payload_offset"], 8)

    def test_ingress_is_fail_closed(self) -> None:
        tx = self.report["transmit"]["surface"]
        rx = self.report["receive"]["surface"]
        self.assertEqual(tx["direct_bl_ingress_sites"], 151)
        self.assertEqual(tx["direct_provider_calls"], 190)
        self.assertEqual(
            tx["stored_entry_pointers"],
            [(0x00475E68, 0x00475291), (0x007940C8, 0x00475349)],
        )
        self.assertEqual(rx["direct_bl_ingress_sites"], 12)
        self.assertEqual(rx["direct_provider_calls"], 93)
        self.assertEqual(
            rx["stored_entry_pointers"],
            [(0x0048F340, 0x0048EDB1), (0x004C9C64, 0x0048F12D)],
        )
        self.assertEqual(
            rx["excluded_unaligned_entry_lookalikes"],
            [(0x00791D72, 0x0048F12D), (0x007940BD, 0x0048EE69)],
        )
        self.assertEqual(
            rx["excluded_false_bl_interiors"], [(0x0048DF70, 0x0048F0CE)]
        )
        for surface in (tx, rx):
            self.assertEqual(surface["stored_strict_interior_pointers"], 0)
            self.assertEqual(surface["direct_strict_interior_branches"], 0)
            self.assertEqual(surface["wide_branch_entry_targets"], 0)

    def test_source_claim_is_conservative(self) -> None:
        lineage = self.report["lineage"]
        self.assertFalse(lineage["exact_product_source_recovered"])
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertTrue(lineage["tx_clean_room_reconstruction_present"])
        self.assertFalse(lineage["rx_clean_room_reconstruction_present"])
        self.assertFalse(self.report["production"]["vendor_source_copied"])


if __name__ == "__main__":
    unittest.main()
