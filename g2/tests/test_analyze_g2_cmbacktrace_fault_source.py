#!/usr/bin/env python3
"""Tests for the CmBacktrace fault source/build closure."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cmbacktrace_fault_source.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cmbacktrace_fault_source", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class CmBacktraceFaultSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.audit()

    def test_complete_upstream_api_compiles_for_cortex_m55(self) -> None:
        self.assertEqual(self.report["software_gap_count"], 0)
        self.assertEqual(
            self.report["source"]["exports"],
            [
                "cm_backtrace_assert",
                "cm_backtrace_call_stack",
                "cm_backtrace_call_stack_any",
                "cm_backtrace_fault",
                "cm_backtrace_firmware_info",
                "cm_backtrace_init",
            ],
        )
        self.assertEqual(self.report["stock_evidence"]["fault_size"], 786)

    def test_fault_entry_has_explicit_register_contract(self) -> None:
        self.assertEqual(
            self.report["source"]["fault_entry_contract"],
            ["r0 = EXC_RETURN (lr)", "r1 = exception sp", "call cm_backtrace_fault", "trap on return"],
        )
        self.assertEqual(
            self.report["source"]["fault_entry_export"],
            "open_cfw_cmbacktrace_hardfault_entry",
        )

    def test_hardware_validation_is_explicitly_blocked(self) -> None:
        self.assertEqual(self.report["status"], "implemented-in-source / hardware-validation-blocked")
        self.assertFalse(self.report["production_registration"]["hardfault_vector_replaced"])
        self.assertTrue(self.report["production_registration"]["stock_path_retained"])
        self.assertFalse(self.report["hardware_block"]["physical_evidence_available"])
        self.assertIn("fault-injection", self.report["hardware_block"]["required_evidence"])

    def test_source_mutation_is_rejected(self) -> None:
        path = self.module.ENTRY_H
        original = self.module.FILE_PINS[path]
        try:
            self.module.FILE_PINS[path] = (original[0], "0" * 64)
            with self.assertRaises(self.module.AuditError):
                self.module.audit()
        finally:
            self.module.FILE_PINS[path] = original

    def test_cli_json_mode(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        self.assertEqual(parsed["software_gap_count"], 0)
        self.assertIn("no hardware", parsed["analysis_mode"])


if __name__ == "__main__":
    unittest.main()
