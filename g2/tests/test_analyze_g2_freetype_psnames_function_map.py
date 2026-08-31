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
ANALYZER = G2 / "tools/analyze_g2_freetype_psnames_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-psnames-function-map.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("psnames_function_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PSNamesFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.run_audit()

    def test_complete_callable_and_physical_accounting(self) -> None:
        self.assertEqual(self.report["confidence"]["mapped_total"],
                         {"functions": 11, "bytes": 1132})
        self.assertEqual(self.report["confidence"]["high"],
                         {"functions": 8, "bytes": 844})
        self.assertEqual(self.report["confidence"]["medium"],
                         {"functions": 3, "bytes": 288})
        self.assertEqual(self.report["confidence"]["unresolved_code"], {
            "functions": 0, "bytes": 0, "source_identities_complete": True,
        })
        scope = self.report["scope"]
        self.assertEqual(scope["bytes"], 1168)
        self.assertEqual(scope["residual_physical"]["bytes"], 36)
        self.assertEqual(scope["residual_physical"]["unclassified_bytes"], 0)

    def test_recovered_callables_have_complete_boundaries_and_hashes(self) -> None:
        rows = {row["symbol"]: row for row in self.report["records"]["psnames"]}
        expected = {
            "compare_uni_maps": ("0x005D9672", "0x005D96B6", 68),
            "ps_get_macintosh_name": ("0x005D98F6", "0x005D990A", 20),
            "ps_get_standard_strings": ("0x005D990A", "0x005D9922", 24),
            "psnames_get_service": ("0x005D9922", "0x005D992C", 10),
        }
        for symbol, wanted in expected.items():
            row = rows[symbol]
            self.assertEqual((row["start"], row["end_exclusive"], row["bytes"]), wanted)
            self.assertEqual(len(row["body_sha256"]), 64)

    def test_high_confidence_rows_have_stock_pointer_evidence(self) -> None:
        rows = [
            row for row in self.report["records"]["psnames"]
            if row["confidence"] == "high"
        ]
        self.assertEqual((len(rows), sum(row["bytes"] for row in rows)), (8, 844))
        for row in rows:
            self.assertTrue(row["pointer_references"])
            self.assertIn("stock-interface-module-or-callback-pointer", row["evidence"])
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1,
                             int(row["start"], 16))
        self.assertIn("0x005D993C", {
            ref for row in rows if row["symbol"] == "compare_uni_maps"
            for ref in row["pointer_references"]
        })

    def test_literal_pool_is_non_callable_and_fully_pinned(self) -> None:
        self.assertEqual(self.report["records"]["physical_classification"], [{
            "start": "0x005D992C", "end_exclusive": "0x005D9950", "bytes": 36,
            "body_sha256": (
                "77d908f30b20762cb33ba71ee6947fe5"
                "20ee61aa88d8cbbaf2ae992ef8145a3f"
            ),
            "category": "literal-pointer-pool", "callable_code": False,
            "source_identity_claimed": False,
        }])

    def test_summary_manifest_matches(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest, self.report)
        self.assertFalse(manifest["production_routed"])
        self.assertFalse(manifest["compiler_byte_identity_claimed"])

    def test_image_and_interface_tamper_fail_closed(self) -> None:
        image = bytearray(self.module.IMAGE.read_bytes())
        image[self.module.INTERFACE - self.module.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-psnames-map-") as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.module, "IMAGE", changed):
                with self.assertRaises(self.module.MapError):
                    self.module.run_audit()

    def test_no_production_route_or_hardware_claim(self) -> None:
        text = "\n".join(path.read_text() for path in (
            G2 / "components/apollo_main/core_overlay/overlay.json",
            G2 / "components/apollo_main/core_overlay/build_component.py",
        ))
        self.assertNotIn("freetype_psnames", text)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["hardware_operations"])

    def test_cli_is_deterministic(self) -> None:
        first = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), self.report)


if __name__ == "__main__":
    unittest.main()
