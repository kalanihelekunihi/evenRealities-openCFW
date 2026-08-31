# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_freetype_psaux_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-psaux-function-map.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("psaux_function_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PSAuxFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.run_audit()

    def test_complete_callable_and_physical_accounting(self) -> None:
        self.assertEqual(self.report["confidence"]["mapped_total"], {"functions": 199, "bytes": 29750})
        self.assertEqual(self.report["confidence"]["high"], {"functions": 65, "bytes": 7020})
        self.assertEqual(self.report["confidence"]["medium"], {"functions": 134, "bytes": 22730})
        self.assertEqual(self.report["confidence"]["unresolved_code"], {
            "functions": 0, "bytes": 0, "source_identities_complete": True,
        })
        scope = self.report["scope"]
        self.assertEqual(scope["bytes"], 30656)
        self.assertEqual(scope["foreign_callable"], {"functions": 2, "bytes": 762})
        self.assertEqual(scope["residual_physical"]["bytes"], 144)
        self.assertEqual(scope["residual_physical"]["unclassified_bytes"], 0)

    def test_census_expansion_and_corrected_identities_are_explicit(self) -> None:
        self.assertEqual(self.report["movement"], {
            "initial_retained_census": {"functions": 57, "bytes": 7114},
            "additional_authenticated_ghidra_source": {"functions": 116, "bytes": 21120},
            "recovered_outside_ghidra_relation": {"functions": 26, "bytes": 1516},
            "corrected_prior_source_identities": {"functions": 3, "bytes": 348},
        })
        rows = {int(row["start"], 16): row for row in self.report["records"]["psaux"]}
        self.assertEqual(rows[0x005D0414]["symbol"], "PS_Conv_ASCIIHexDecode")
        self.assertEqual(rows[0x005D049E]["symbol"], "PS_Conv_EexecDecode")
        self.assertEqual(rows[0x005D04E8]["symbol"], "ps_table_new")

    def test_recovered_boundaries_and_hashes_are_complete(self) -> None:
        rows = {row["symbol"]: row for row in self.report["records"]["psaux"]}
        expected = {
            "afm_compare_kern_pairs": ("0x005CFD12", "0x005CFD38", 38),
            "ps_parser_done": ("0x005D128A", "0x005D128C", 2),
            "t1_make_subfont": ("0x005D1B4A", "0x005D1D02", 440),
            "cf2_builder_cubeTo": ("0x005D2F80", "0x005D2FEE", 110),
        }
        for symbol, wanted in expected.items():
            row = rows[symbol]
            self.assertEqual((row["start"], row["end_exclusive"], row["bytes"]), wanted)
            self.assertEqual(len(row["body_sha256"]), 64)

    def test_high_confidence_rows_have_stock_pointer_evidence(self) -> None:
        rows = [row for row in self.report["records"]["psaux"] if row["confidence"] == "high"]
        self.assertEqual((len(rows), sum(row["bytes"] for row in rows)), (65, 7020))
        for row in rows:
            self.assertTrue(row["pointer_references"])
            self.assertIn("stock-interface-or-function-table-pointer", row["evidence"])
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1, int(row["start"], 16))

    def test_foreign_callable_code_remains_outside_psaux_identity(self) -> None:
        rows = self.report["records"]["foreign_callable"]
        self.assertEqual([row["start"] for row in rows], ["0x005D2BAE", "0x005D2E0C"])
        self.assertTrue(all(not row["psaux_source_identity_claimed"] for row in rows))

    def test_summary_manifest_matches(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(manifest["confidence"]["high"], self.report["confidence"]["high"])
        self.assertEqual(manifest["confidence"]["medium"], self.report["confidence"]["medium"])
        self.assertFalse(manifest["production_routed"])

    def test_no_production_route_or_hardware_claim(self) -> None:
        text = "\n".join(path.read_text() for path in (
            G2 / "components/apollo_main/core_overlay/overlay.json",
            G2 / "components/apollo_main/core_overlay/build_component.py",
        ))
        self.assertNotIn("freetype_psaux", text)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["hardware_operations"])

    def test_image_tamper_fails_closed(self) -> None:
        image = bytearray(self.module.IMAGE.read_bytes())
        image[self.module.MODULE_CLASS - self.module.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory() as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.module, "IMAGE", changed):
                with self.assertRaises(self.module.MapError):
                    self.module.run_audit()

    def test_cli_is_deterministic(self) -> None:
        first = subprocess.run([sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True).stdout
        second = subprocess.run([sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["mapping_sha256"], self.report["mapping_sha256"])


if __name__ == "__main__":
    unittest.main()
