#!/usr/bin/env python3
"""Guard the stock exclusion and public build readiness of dm_dev_priv.c."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_dm_dev_priv.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location(
        "analyze_g2_cordio_dm_dev_priv", ANALYZER
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioDmDevPrivAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()

    def test_optional_privacy_tu_is_default_routed_and_absent(self) -> None:
        report = self.analyzer.analyze()
        module = report["module"]
        routing = report["default_routing"]
        self.assertEqual(module["classification"], "not_linked_or_dead_stripped")
        self.assertEqual(module["linked_function_count"], 0)
        self.assertEqual(module["linked_function_bytes"], 0)
        self.assertEqual(module["source_inventory_functions"], 18)
        self.assertEqual(len(module["source_only_functions"]), 18)
        self.assertEqual(module["retained_path_anchors"], 0)
        self.assertEqual(routing["component_slots"], 21)
        self.assertEqual(routing["device_privacy_component_id"], 1)
        self.assertEqual(routing["boot_slot_value"], routing["default_interface"])
        self.assertEqual(routing["default_reset"], 0x004D29BF)
        self.assertEqual(routing["default_hci_handler"], 0x004D29C1)
        self.assertEqual(routing["default_message_handler"], 0x004D29C1)
        self.assertEqual(len(routing["table_base_literal_cells"]), 9)
        self.assertNotIn(4, routing["component_install_offsets"])
        self.assertEqual(routing["device_privacy_installations"], 0)
        readiness = report["readiness"]
        self.assertEqual(readiness["source_functions_built"], 18)
        self.assertEqual(readiness["provider_seams"], 24)
        self.assertEqual(readiness["valid_non_vacuous_closure_profiles"], 2)
        self.assertEqual(readiness["linked_unresolved_symbols"], 0)
        self.assertFalse(report["lineage"]["stock_body_version_discriminated"])
        self.assertEqual(report["production"]["source_owned_bytes_added"], 0)


if __name__ == "__main__":
    unittest.main()
