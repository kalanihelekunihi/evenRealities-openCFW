#!/usr/bin/env python3
"""Guard the clean-room G2 BLE WSF-thread closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_thread_ble_wsf.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_thread_ble_wsf", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ThreadBleWsfAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_physical_translation_unit_is_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["bounded_bodies"], 12)
        self.assertEqual(surface["body_bytes"], 656)
        self.assertEqual(surface["physical_bytes"], 728)
        self.assertEqual(surface["literal_pool_bytes"], 72)

    def test_static_thread_configuration_is_pinned(self) -> None:
        thread = self.report["thread"]
        self.assertEqual(thread["name"], "ble_wsf")
        self.assertEqual(thread["entry"], 0x004D0A4C)
        self.assertEqual(thread["control_block"], 0x20004068)
        self.assertEqual(thread["cmsis_control_block"], 0x20072140)
        self.assertEqual(thread["cmsis_control_block_bytes"], 0x70)
        self.assertEqual(thread["stack"], 0x20043A98)
        self.assertEqual(thread["stack_bytes"], 0x4000)
        self.assertEqual(thread["priority"], 0x31)
        self.assertEqual(thread["semaphore_max_count"], 1)
        self.assertEqual(thread["semaphore_initial_count"], 1)

    def test_tx_flow_control_is_pinned(self) -> None:
        flow = self.report["flow_control"]
        self.assertEqual(flow["immediate_take_timeout"], 0)
        self.assertEqual(flow["retry_take_timeout"], 10)
        self.assertEqual(flow["retry_delay_ticks"], 10)
        self.assertEqual(flow["max_retry_count"], 20)
        self.assertEqual(flow["diagnostic_bound_ms"], 400)
        self.assertTrue(flow["release_only_when_count_zero"])

    def test_ingress_is_fail_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["direct_bl_ingress_sites"], 27)
        self.assertEqual(surface["direct_provider_calls"], 50)
        self.assertEqual(
            surface["stored_entry_pointers"], [(0x004D0CF8, 0x004D0A4D)]
        )
        self.assertEqual(
            surface["excluded_unaligned_entry_lookalikes"],
            [(0x007940DD, 0x004D0AF7)],
        )
        self.assertEqual(surface["stored_strict_interior_pointers"], 0)
        self.assertEqual(surface["direct_strict_interior_branches"], 0)
        self.assertEqual(surface["wide_branch_entry_targets"], 0)

    def test_source_claim_is_conservative(self) -> None:
        lineage = self.report["lineage"]
        self.assertFalse(lineage["exact_product_source_recovered"])
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertFalse(self.report["production"]["vendor_source_copied"])


if __name__ == "__main__":
    unittest.main()
