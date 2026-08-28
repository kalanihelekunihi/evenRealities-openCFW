# SPDX-License-Identifier: MIT
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_apollo_opacity_wave11.py"
BOUNDARY = G2 / "research/admission/apollo_opacity_wave11/source_boundaries.tsv"
SHARED = G2 / "research/admission/apollo_opacity_wave11/shared_data.tsv"
DOC = G2 / "docs/research/g2-apollo-opacity-wave11-freetype-cff-source-closure.md"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("apollo_opacity_wave11", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ApolloOpacityWave11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.run_audit()

    def test_wave10_residual_and_selected_root_are_pinned(self) -> None:
        self.assertEqual(self.report["wave10_residual"], {"functions": 1352, "bytes": 152498})
        self.assertEqual(self.report["before"], self.report["wave10_residual"])
        self.assertEqual(self.report["selected_root_range"], {"start": "0x005AF88C", "end_exclusive": "0x005B0004"})

    def test_complete_residual_static_closure_is_accounted(self) -> None:
        self.assertEqual(self.report["actionable_graph"], {"positive_functions": 43, "positive_bytes": 10098, "closure_depth_max": 5, "terminal_functions": 23, "terminal_edges": 78})
        self.assertEqual(self.report["range_partition"], {"functions": 43, "contiguous_functions": 43, "interior_islands": 0, "interior_physical_bytes": 0})
        self.assertEqual(len(self.report["frontier_records"]), 23)

    def test_freetype_source_and_license_identity_are_retained(self) -> None:
        self.assertEqual(self.report["source_attributed"], {"functions": 42, "bytes": 10056, "provider": "FreeType-2.9.1-VER-2-9-1", "license": "FTL"})
        root = next(row for row in self.report["records"] if row["entry"] == "0x005AF88C")
        self.assertEqual(root["symbol"], "cff_face_init")
        self.assertEqual(root["source_path"], "g2/third_party/freetype/src/cff/cffobjs.c")
        self.assertTrue(root["source_identity_authenticated"])

    def test_iAR_strncmp_body_remains_fail_closed(self) -> None:
        self.assertEqual(self.report["typed_unavailable"], {"functions": 1, "bytes": 42, "provider": "IAR-DLIB-proprietary-runtime"})
        runtime = next(row for row in self.report["records"] if row["entry"] == "0x0044B610")
        self.assertEqual(runtime["symbol"], "strncmp")
        self.assertEqual(runtime["license_status"], "unavailable")
        self.assertFalse(runtime["source_identity_authenticated"])

    def test_direct_shared_data_and_strings_are_closed_without_double_count(self) -> None:
        self.assertEqual(self.report["shared_data"], {"direct_cells": 34, "physical_bytes": 136, "diagnostic_pointer_targets": 8, "additional_function_bytes": 0})
        self.assertTrue(all(row["wave11_additional_function_bytes"] == "0" for row in self.report["frontier_records"]))

    def test_residual_and_next_envelope_are_deterministic(self) -> None:
        self.assertEqual(self.report["after"], {"functions": 1309, "bytes": 142400})
        self.assertEqual(self.report["largest_remaining"], {"entry": "0x004BFED6", "envelope_bytes": 1902})
        self.assertEqual(self.report["mapping_sha256"], "f41ec3591b16f531406cffe042c9644b76ec1d13350c816a7cac9bb93cf518cc")

    def test_boundary_and_data_mutations_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            boundary = root / "source.tsv"
            boundary.write_text(BOUNDARY.read_text().replace("\t1912\t1912\t", "\t1910\t1912\t", 1))
            shared = root / "shared.tsv"
            shared.write_text(SHARED.read_text().replace("\t6c09ffff\t", "\t00000000\t", 1))
            old_boundary, old_shared = self.analyzer.BOUNDARY, self.analyzer.SHARED
            try:
                self.analyzer.BOUNDARY = boundary
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.SHARED = shared
                with self.assertRaises(self.analyzer.WaveError):
                    self.analyzer.run_audit()
            finally:
                self.analyzer.BOUNDARY = old_boundary
                self.analyzer.SHARED = old_shared

    def test_research_only_cli_and_production_exclusion(self) -> None:
        self.assertTrue(self.report["read_only"])
        self.assertFalse(self.report["hardware_operations"])
        self.assertFalse(self.report["production_routed"])
        self.assertIn("dual-profile Cortex-M55 codegen", self.report["production_blocker"])
        for path in (G2 / "Makefile", G2 / "tools/open_cfw.py", G2 / "tools/apollo_overlay.py"):
            self.assertNotIn("apollo_opacity_wave11", path.read_text(errors="ignore"))
        self.assertIn("## Production admission", DOC.read_text())
        cli = json.loads(subprocess.run([sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True).stdout)
        self.assertEqual(cli["mapping_sha256"], self.report["mapping_sha256"])


if __name__ == "__main__":
    unittest.main()
