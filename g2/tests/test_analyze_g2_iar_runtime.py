#!/usr/bin/env python3
"""Guard the fail-closed G2 IAR runtime census."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_iar_runtime.py"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("analyze_g2_iar_runtime", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class IARRuntimeAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = load_analyzer().analyze()

    def test_runtime_boundaries_and_states_are_exact(self) -> None:
        segments = {item["name"]: item for item in self.report["segments"]}
        self.assertEqual(segments["sqrtf"]["size"], 28)
        self.assertEqual(
            segments["sqrtf"]["state"], "source_recreated_redirected"
        )
        self.assertEqual(segments["__aeabi_memcpy"]["size"], 166)
        self.assertEqual(
            segments["__aeabi_memcpy"]["state"], "source_recreated_redirected"
        )
        self.assertEqual(
            segments["__aeabi_memmove"]["state"], "source_recreated_redirected"
        )
        self.assertEqual(segments["runtime_literals"]["size"], 16)
        self.assertEqual(self.report["identity"]["errno_address"], 0x2007_4F14)

    def test_ingress_census_is_discriminating(self) -> None:
        ingress = {(item["target"], item["kind"]): item for item in self.report["ingress"]}
        self.assertEqual(ingress[(0x0043_97A8, "bl")]["count"], 68)
        self.assertEqual(ingress[(0x0043_9BE4, "bl")]["count"], 790)
        self.assertEqual(self.report["interior_entries"][0]["count"], 597)

    def test_scope_and_version_claims_remain_honest(self) -> None:
        self.assertFalse(self.report["identity"]["exact_release_proven"])
        self.assertEqual(
            self.report["identity"]["archive_comparison_priority"],
            ("9.60.2", "9.60.3", "9.70.x", "9.50.x"),
        )
        self.assertEqual(
            [(item["date"], item["time"]) for item in self.report["application_build_banners"]],
            [
                ("Jul  6 2026", "21:37:47"),
                ("Jul  6 2026", "21:37:52"),
                ("Jul  6 2026", "21:37:30"),
            ],
        )
        self.assertEqual(
            self.report["identity"]["archive_family_hypotheses"]["runtime"],
            "rt7M_tl.a",
        )
        recovery = self.report["recovery"]
        self.assertEqual(recovery["confirmed_runtime_code_units"], 10)
        self.assertEqual(recovery["source_recreated_units"], 10)
        self.assertEqual(recovery["production_integrated_units"], 10)
        self.assertEqual(recovery["retained_runtime_code_units"], 0)
        self.assertEqual(recovery["retained_units_with_qualified_source_candidates"], 0)
        self.assertEqual(recovery["retained_runtime_code_bytes"], 0)
        self.assertEqual(
            recovery["production_integration_percent_for_new_six"], 100
        )

    def test_cli_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--json"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn('"estimated_broader_runtime_identification_percent": "40-50"', result.stdout)


if __name__ == "__main__":
    unittest.main()
