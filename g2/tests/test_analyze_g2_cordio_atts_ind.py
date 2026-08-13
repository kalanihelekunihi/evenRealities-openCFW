#!/usr/bin/env python3
"""Guard the stock inclusion and EATT ABI of Cordio atts_ind.c."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_ind.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_ind", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsIndAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_eatt_indication_core_is_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        architecture = report["architecture"]
        self.assertEqual(module["classification"], "linked_eatt_indication_core")
        self.assertEqual(module["physical_bytes"], 1608)
        self.assertEqual(module["linked_function_count"], 13)
        self.assertEqual(module["linked_function_bytes"], 1552)
        self.assertEqual(module["owned_noncode_bytes"], 56)
        self.assertEqual(module["source_inventory_functions"], 15)
        self.assertEqual(module["direct_bl_ingress_sites"], 22)
        self.assertEqual(module["registered_function_pointers"], 3)
        self.assertEqual(module["initializer_stream_entry_windows"], 1)
        self.assertEqual(module["strict_interior_pointers"], 0)
        self.assertTrue(architecture["eatt_aware"])
        self.assertEqual(architecture["server_ccb_count"], 9)
        self.assertEqual(architecture["server_ccb_stride"], 64)
        self.assertEqual(architecture["simultaneous_notifications"], 10)

    def test_only_zero_copy_public_wrappers_are_stripped(self) -> None:
        report = self.analyzer.analyze()
        self.assertEqual(
            report["module"]["source_only_functions"],
            ["AttsHandleValueIndZeroCpy", "AttsHandleValueNtfZeroCpy"],
        )
        self.assertTrue(report["architecture"]["ordinary_indication_linked"])
        self.assertTrue(report["architecture"]["ordinary_notification_linked"])
        self.assertFalse(report["architecture"]["zero_copy_indication_linked"])
        self.assertFalse(report["architecture"]["zero_copy_notification_linked"])

    def test_r20_interface_and_control_block_abi_are_exact(self) -> None:
        report = self.analyzer.analyze()
        self.assertEqual(report["abi"]["atts_cb"], 0x2006E5F0)
        self.assertEqual(report["abi"]["p_ind_offset"], 0x260)
        self.assertEqual(report["abi"]["outstanding_indication_offset"], 0x26)
        self.assertEqual(report["abi"]["pending_notification_array_offset"], 0x2A)
        self.assertEqual(report["dispatch"]["interface"], 0x7852C0)
        self.assertEqual(report["dispatch"]["value_confirmation_method"], 15)
        self.assertEqual(report["dispatch"]["processor_table_live_sram"], 0x2000045C)
        self.assertEqual(report["dispatch"]["value_confirmation_live_cell"], 0x20000498)
        self.assertTrue(report["dispatch"]["initializer_stream_is_not_runtime_table"])
        self.assertTrue(report["lineage"]["r20_through_r20c_invariant"])
        self.assertTrue(report["lineage"]["later_r44_byte_identical"])
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
