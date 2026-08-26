#!/usr/bin/env python3
"""Guard the fail-closed G2 Cordio WSF string-helper report."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_cordio_wstr.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_cordio_wstr", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CordioWstrAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_stock_bounds_and_ingress(self) -> None:
        module = self.report["module"]
        self.assertEqual(
            (module["start"], module["end_exclusive"], module["size"]),
            (0x0056D8C4, 0x0056D93A, 118),
        )
        functions = {row["name"]: row for row in module["functions"]}
        self.assertEqual(len(functions["WStrReverseCpy"]["direct_bl_callers"]), 39)
        self.assertEqual(len(functions["WStrReverse"]["direct_bl_callers"]), 2)
        self.assertEqual(functions["WStrReverseCpy"]["direct_callees"], [])
        self.assertEqual(module["stored_entry_or_interior_pointers"], 0)
        self.assertEqual(module["external_interior_branches"], 0)

    def test_lineage_and_dead_strip_are_qualified(self) -> None:
        self.assertIn("Apache-2.0", self.report["lineage"]["exact_public_definition_route"])
        self.assertFalse(self.report["lineage"]["release_discriminator"])
        self.assertFalse(self.report["lineage"]["proprietary_source_copied"])
        self.assertEqual(self.report["source_inventory"]["dead_stripped"], ["WstrnCpy"])
        self.assertEqual(self.report["candidate"]["production"], "routed")
        self.assertEqual(
            (
                self.report["candidate"]["compiled_text_bytes"],
                self.report["candidate"]["alignment_bytes"],
                self.report["candidate"]["strict_relocations"],
                self.report["candidate"]["guarded_redirects"],
            ),
            (286, 2, 0, 2),
        )
        matrix = self.report["compiler_matrix"]
        self.assertEqual((matrix["compiler_profiles"], matrix["comparison_rows"]), (13, 26))
        self.assertEqual((matrix["raw_matches"], matrix["strict_normalized_matches"]), (0, 0))
        self.assertEqual(matrix["best_common_absolute_size_delta"], 10)

    def test_candidate_is_present_in_production_inputs(self) -> None:
        needle = "runtime_cordio_wstr_candidate"
        self.assertIn(
            needle,
            (ROOT / "components/apollo_main/core_overlay/overlay.json").read_text(),
        )

    def test_cli_json(self) -> None:
        parsed = json.loads(subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout)
        self.assertEqual(parsed["module"]["sha256"], self.report["module"]["sha256"])


if __name__ == "__main__":
    unittest.main()
