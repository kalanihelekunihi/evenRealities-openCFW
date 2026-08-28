# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave12.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave12/source_boundaries.tsv"
ADMISSION = G2 / "research/admission/apollo_opacity_wave12"
FIXTURE = G2 / "tests/fixtures/apollo_opacity_wave12_provider_host.c"
DOC = G2 / "docs/research/g2-apollo-opacity-wave12-mspi-device-source-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave12", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave11_residual_and_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave11_residual"], {"functions": 1309, "bytes": 142400})
        self.assertEqual(self.report["before"], self.report["wave11_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x004BFED6", "end_exclusive": "0x004C0644"})

    def test_complete_call_and_range_closure(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 1, "positive_bytes": 1902, "closure_depth_max": 0, "terminal_functions": 0, "static_call_edges": 0})
        self.assertEqual(self.report["range_partition"], {"functions": 1, "contiguous_functions": 1, "interior_islands": 0, "interior_physical_bytes": 0})

    def test_ambiq_source_and_bsd_license_are_authenticated(self) -> None:
        self.assertEqual(self.report["source_attributed"], {"functions": 1, "bytes": 1902, "provider": "AmbiqSuite-SDK-5.1.0-5efc0228528a8adce5eae0d226fac85d2551eb3b", "license": "BSD-3-Clause"})
        self.assertEqual(self.report["record"]["symbol"], "mspi_device_configure")
        self.assertTrue(self.report["record"]["source_identity_authenticated"])

    def test_data_graph_is_exact_and_not_double_counted(self) -> None:
        self.assertEqual(self.report["shared_data"], {"direct_cells": 4, "physical_bytes": 16, "additional_function_bytes": 0})

    def test_pure_provider_model_covers_all_26_modes(self) -> None:
        self.assertEqual(self.report["provider_model"], {"device_modes": 26, "pure_register_plan": True, "mmio_operations": 0})
        compiler = shutil.which("cc") or shutil.which("clang") or shutil.which("gcc")
        if compiler is None:
            self.skipTest("host C compiler unavailable")
        with tempfile.TemporaryDirectory() as temp:
            executable = Path(temp) / "wave12-provider-host"
            subprocess.run([
                compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                "-I", str(ADMISSION),
                str(ADMISSION / "runtime_mspi_device_configure_provider.c"),
                str(FIXTURE), "-o", str(executable),
            ], check=True, capture_output=True, text=True)
            subprocess.run([str(executable)], check=True)

    def test_residual_and_next_root_are_deterministic(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1308, "bytes": 140498})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x00438FB8", "envelope_bytes": 1710})
        self.assertEqual(self.report["mapping_sha256"], "9aa2da878028103b19d56a0bba82102586a8d3cf75b77de57b2ce49f6f53bdc7")

    def test_boundary_mutation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            boundary = Path(temp) / "source.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t1902\t1902\t", "\t1900\t1902\t", 1))
            old = self.analyzer.BOUNDARY
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old

    def test_research_only_cli_and_production_exclusion(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        self.assertIn("dual-profile IAR Cortex-M55 codegen", self.report["production_blocker"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave12", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        cli = json.loads(subprocess.run([sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True).stdout)
        self.assertEqual(cli["mapping_sha256"], self.report["mapping_sha256"])


if __name__ == "__main__":
    unittest.main()
