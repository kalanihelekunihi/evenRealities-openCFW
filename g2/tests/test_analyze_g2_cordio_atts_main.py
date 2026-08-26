#!/usr/bin/env python3
"""Guard the stock Cordio ATT server owner and live dispatch ABI."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_atts_main.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_atts_main", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioAttsMainAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_server_owner_interval_and_ingress_are_closed(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        self.assertEqual(module["classification"], "linked_eatt_server_owner_dispatcher")
        self.assertEqual(module["physical_bytes"], 2812)
        self.assertEqual(module["linked_function_count"], 17)
        self.assertEqual(module["linked_function_bytes"], 2710)
        self.assertEqual(module["owned_noncode_bytes"], 102)
        self.assertEqual(module["source_inventory_functions"], 21)
        self.assertEqual(module["direct_bl_ingress_sites"], 45)
        self.assertEqual(module["registered_function_pointers"], 4)
        self.assertEqual(module["accepted_strict_interior_pointers"], 0)

    def test_live_initialized_processor_table_is_not_flash_cell(self) -> None:
        dispatch = self.analyzer.analyze()["dispatch"]
        self.assertEqual(dispatch["processor_table_live_sram"], 0x2000045C)
        self.assertEqual(len(dispatch["processor_table_entries"]), 18)
        self.assertEqual(dispatch["processor_table_entries"][15], 0x00533DD9)
        self.assertEqual(dispatch["processor_table_names"][15], "attsProcValueCnf")
        self.assertEqual(dispatch["processor_table_entries"][17], 0)
        self.assertFalse(dispatch["signed_write_processor_linked"])
        self.assertEqual(dispatch["initializer_stream_value_cell"], 0x00791AD0)
        self.assertTrue(dispatch["initializer_stream_is_not_runtime_table"])

    def test_r44_guards_eatt_abi_and_source_only_set_are_exact(self) -> None:
        report = self.analyzer.analyze()
        self.assertEqual(
            report["module"]["source_only_functions"],
            ["AttsAuthorRegister", "AttsSetAttr", "AttsGetAttr", "AttsErrorTest"],
        )
        self.assertTrue(report["architecture"]["eatt_aware"])
        self.assertTrue(report["architecture"]["r44_data_length_guards"])
        self.assertTrue(report["architecture"]["public_r20_missing_stock_guards"])
        self.assertEqual(report["architecture"]["server_ccb_count"], 9)
        self.assertEqual(report["abi"]["atts_cb"], 0x2006E5F0)
        self.assertEqual(report["abi"]["att_cb_server_interface_offset"], 0x40)
        self.assertEqual(report["lineage"]["selected_blob"], "bb99817115ce4da49ce26b5c52c4dd3418baaf88")
        production = report["production"]
        self.assertEqual(production["status"], "routed")
        self.assertEqual(production["source_owned_bytes_added"], 2622)
        self.assertEqual(production["stock_bytes_replaced"], 2710)
        self.assertEqual(production["alignment_bytes"], 30)
        self.assertEqual(production["strict_relocations"], 44)
        self.assertEqual(production["guarded_redirects"], 17)
        self.assertEqual(len(production["source_only_public_helpers"]), 4)


if __name__ == "__main__":
    unittest.main()
