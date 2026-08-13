#!/usr/bin/env python3
"""Guard the clean-room G2 BLE-startup and adjacent-vector closure."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_app_ble_startup.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_app_ble_startup", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AppBleStartupAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_bounded_surface_preserves_mixed_ownership(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["bounded_bodies"], 13)
        self.assertEqual(surface["product_app_ble_bodies"], 12)
        self.assertEqual(surface["foreign_vector_bodies"], 1)
        self.assertEqual(surface["body_bytes"], 3_236)
        self.assertEqual(surface["product_body_bytes"], 3_192)
        self.assertEqual(surface["mixed_physical_bytes"], 3_242)
        self.assertFalse(surface["whole_contiguous_app_ble_object"])

    def test_gpio_vector_is_not_the_ble_transport_isr(self) -> None:
        vector = self.report["vector"]
        self.assertEqual(vector["cell"], 0x0043812C)
        self.assertEqual(vector["vector_index"], 75)
        self.assertEqual(vector["external_irq"], 59)
        self.assertEqual(vector["irq_enum"], "GPIO0_607F_IRQn")
        self.assertEqual(vector["handler"], 0x004B80BE)
        self.assertFalse(vector["calls_hci_drv_int_service"])

    def test_startup_configuration_is_pinned(self) -> None:
        startup = self.report["startup"]
        self.assertEqual(startup["buffer_pool_bytes"], 0x2940)
        self.assertEqual(startup["buffer_pool_memory"], 0x2004FA98)
        self.assertEqual(startup["buffer_pool_descriptor_input"], 0x200003B0)
        self.assertEqual(startup["max_rx_acl_length"], 251)
        self.assertEqual(startup["ble_address"], 0x200737BF)
        self.assertEqual(startup["delayed_callback_ms"], 10_000)
        self.assertEqual(startup["product_ble_control_block"], 0x200727F0)
        self.assertEqual(startup["runtime_smp_config"], 0x00774D44)
        self.assertEqual(startup["ccc_set_len"], 6)

    def test_ingress_is_fail_closed(self) -> None:
        surface = self.report["surface"]
        self.assertEqual(surface["direct_bl_ingress_sites"], 9)
        self.assertEqual(surface["direct_provider_calls"], 267)
        self.assertEqual(
            surface["stored_entry_pointers"],
            [
                (0x0043812C, 0x004B80BF),
                (0x004B7F60, 0x004B758B),
                (0x004B8734, 0x004B748D),
                (0x004B8738, 0x004B74F1),
                (0x004B8740, 0x004B7533),
                (0x004B8794, 0x004B7D33),
                (0x004B87A0, 0x004B758B),
            ],
        )
        self.assertEqual(surface["stored_strict_interior_pointers"], 0)
        self.assertEqual(surface["excluded_unaligned_interior_lookalikes"], 2)
        self.assertEqual(surface["direct_strict_interior_branches"], 0)

    def test_source_claim_is_conservative(self) -> None:
        lineage = self.report["lineage"]
        self.assertFalse(lineage["whole_file_source_exact"])
        self.assertFalse(lineage["historical_generating_commit_resolved"])
        self.assertFalse(self.report["production"]["vendor_source_copied"])


if __name__ == "__main__":
    unittest.main()
