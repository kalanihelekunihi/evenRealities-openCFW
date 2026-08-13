#!/usr/bin/env python3
"""Focused tests for the G2 CMSIS-FreeRTOS linked-function census."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "analyze_g2_cmsis_freertos_linked_census.py"

SPEC = importlib.util.spec_from_file_location("cmsis_linked_census", TOOL)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class CmsisFreeRTOSLinkedCensusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = MODULE.audit()
        package = MODULE.DEFAULT_IMAGE.read_bytes()
        cls.application = package[MODULE.PACKAGE_PREAMBLE:]
        cls.source = MODULE.DEFAULT_SOURCE.read_bytes()
        cls.functions = MODULE.load_function_map()

    def test_complete_linked_object_contract(self) -> None:
        linked = self.report["linked_object"]
        self.assertEqual(linked["start"], "0x0044900E")
        self.assertEqual(linked["end_exclusive"], "0x00449ED2")
        self.assertEqual(linked["bytes"], 3_780)
        self.assertEqual(linked["function_count"], 43)
        self.assertEqual(linked["public_api_count"], 38)
        self.assertEqual(linked["function_bytes"], 3_758)
        self.assertEqual(linked["literal_pool_bytes"], 22)

        names = [item["name"] for item in linked["functions"]]
        self.assertEqual(names[0], "IRQ_Context")
        self.assertEqual(names[-3:], ["CreateBlock", "AllocBlock", "FreeBlock"])
        self.assertIn("osThreadNew", names)
        self.assertIn("osMessageQueueGet", names)
        self.assertIn("osMemoryPoolFree", names)

    def test_reference_topology_is_closed(self) -> None:
        topology = self.report["topology"]
        self.assertEqual(topology["direct_bl_total"], 872)
        self.assertEqual(topology["external_direct_bl"], 831)
        self.assertEqual(topology["internal_direct_bl"], 41)
        self.assertEqual(topology["external_interior_wide"], [])
        self.assertEqual(topology["external_interior_narrow"], [])
        self.assertEqual(
            topology["aligned_stored_entries"],
            [{"word_address": "0x00449DD0", "target": "0x00449398"}],
        )

    def test_version_and_history_boundary(self) -> None:
        upstream = self.report["upstream"]
        self.assertEqual(upstream["selected_tag"], "v10.5.1")
        self.assertEqual(
            upstream["selected_commit"],
            "d213f261b5be6bb29a7cce8b84071706b72f4d53",
        )
        self.assertEqual(
            upstream["source_blob_introduced_commit"],
            "13acfbef7be85119fc6bc56832c455d4547d92c7",
        )
        self.assertEqual(
            upstream["linked_behavior_lower_commit"],
            "600ba38a66b38105817bd7351be6f6718cd1c2be",
        )
        self.assertEqual(
            upstream["next_excluded_linked_change"],
            "bb8a350a84567e5a000020abfbd6ab45ea9f6b46",
        )
        discriminators = self.report["version_discriminators"]
        self.assertEqual(len(discriminators["v10_4_6_excluded"]), 3)
        self.assertIn("re-notification", discriminators["post_bb8a350_excluded"])

    def test_dead_stripping_is_explicit(self) -> None:
        dead = self.report["dead_stripped"]
        self.assertEqual(dead["public_api_count"], 33)
        self.assertIn("osThreadGetState", dead["public_apis"])
        self.assertIn("osMessageQueueReset", dead["public_apis"])
        self.assertIn("osMemoryPoolDelete", dead["public_apis"])
        self.assertNotIn("osThreadNew", dead["public_apis"])

    def test_body_and_source_mutations_fail_closed(self) -> None:
        mutated_application = bytearray(self.application)
        offset = 0x0044_90CC - MODULE.APPLICATION_BASE
        mutated_application[offset] ^= 0x01
        with self.assertRaisesRegex(MODULE.AuditError, "osKernelGetTickCount"):
            MODULE.verify_function_bytes(bytes(mutated_application), self.functions)

        mutated_source = bytearray(self.source)
        mutated_source[100] ^= 0x01
        with self.assertRaisesRegex(MODULE.AuditError, "source identity"):
            MODULE.verify_source(bytes(mutated_source), self.functions)

    def test_cli_json_contract(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(TOOL), "--json"],
            cwd=ROOT.parent,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)
        report = json.loads(completed.stdout)
        self.assertEqual(report["linked_object"]["function_count"], 43)
        self.assertEqual(report["topology"]["external_direct_bl"], 831)


if __name__ == "__main__":
    unittest.main()
