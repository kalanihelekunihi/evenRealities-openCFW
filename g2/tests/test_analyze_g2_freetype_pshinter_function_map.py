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
ANALYZER = G2 / "tools/analyze_g2_freetype_pshinter_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-pshinter-function-map.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("pshinter_function_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class PSHinterFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.run_audit()

    def test_pshinter_is_the_largest_authenticated_remaining_module(self) -> None:
        rows = {row["module"]: row for row in self.report["selection"]["candidates"]}
        self.assertEqual(self.report["selected_module"], "pshinter")
        self.assertEqual(
            (rows["pshinter"]["source_backed_functions"], rows["pshinter"]["source_backed_bytes"]),
            (67, 8480),
        )
        self.assertEqual(
            (rows["psaux"]["source_backed_functions"], rows["psaux"]["source_backed_bytes"]),
            (57, 7114),
        )
        self.assertEqual(rows["psnames"]["source_backed_bytes"], 1010)
        self.assertEqual(rows["smooth-raster"]["direct_callback_targets"], 7)

    def test_direct_dispatch_rows_have_complete_independent_evidence(self) -> None:
        high = self.report["records"]["high"]
        self.assertEqual((len(high), sum(row["bytes"] for row in high)), (18, 1554))
        self.assertEqual(len({row["pointer_reference"] for row in high}), 18)
        self.assertEqual(len({row["start"] for row in high}), 18)
        for row in high:
            self.assertIn("stock-module-interface-or-nested-table-pointer", row["evidence"])
            self.assertIn("exact-freetype-2.9.1-definition", row["evidence"])
            self.assertIn("complete-thumb-body-boundary", row["evidence"])
            self.assertIn("whole-body-sha256", row["evidence"])
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1, int(row["start"], 16))
            self.assertFalse(row["compiler_byte_identity_claimed"])
        recovered = {
            row["symbol"] for row in high
            if row["mapping_origin"] == "recovered-direct-dispatch-callback"
        }
        self.assertEqual(recovered, {
            "psh_globals_new", "ps_hinter_done", "ps_hinter_init",
            "pshinter_get_globals_funcs", "pshinter_get_t1_funcs",
            "pshinter_get_t2_funcs", "ps_hints_t1reset", "ps_hints_close",
            "t1_hints_open", "t1_hints_stem", "t2_hints_open",
            "t2_hints_stems",
        })

    def test_recovered_small_leaf_and_large_body_boundaries_are_exact(self) -> None:
        rows = {row["symbol"]: row for row in self.report["records"]["high"]}
        expected = {
            "psh_globals_new": (
                "0x005D8908", "0x005D8A48", 320,
                "a06f5654c8da09df4594adb0640337110be76bcc802406ef175a8465ae7aae47",
            ),
            "pshinter_get_globals_funcs": (
                "0x005D8B04", "0x005D8B08", 4,
                "bb032f155683c89edf09051c3d3462ec154b68b40628e75fe8849a7b51ed70e8",
            ),
            "t2_hints_stems": (
                "0x005D93E0", "0x005D9462", 130,
                "6a0e297d368ddfd262a0b29398d5ea2da9c19244bbbc6b56bfb8029c138da6d4",
            ),
        }
        for symbol, wanted in expected.items():
            row = rows[symbol]
            self.assertEqual(
                (row["start"], row["end_exclusive"], row["bytes"], row["body_sha256"]),
                wanted,
            )

    def test_confidence_and_movement_do_not_inflate_prior_census(self) -> None:
        confidence = self.report["confidence"]
        self.assertEqual(confidence["exact"]["functions"], 0)
        self.assertEqual(confidence["high"], {"functions": 18, "bytes": 1554})
        self.assertEqual(confidence["medium"], {"functions": 61, "bytes": 7634})
        self.assertEqual(confidence["mapped_total"], {"functions": 79, "bytes": 9188})
        self.assertEqual(
            confidence["unresolved_code"],
            {"functions": 0, "bytes": 0, "source_identities_complete": True},
        )
        self.assertEqual(
            self.report["movement"],
            {
                "retained_census_promoted_to_high": {"functions": 6, "bytes": 846},
                "retained_census_medium": {"functions": 61, "bytes": 7634},
                "recovered_direct_callbacks": {"functions": 12, "bytes": 708},
                "new_beyond_closed_census": {"functions": 12, "bytes": 708},
            },
        )

    def test_physical_complement_is_complete_noncallable_data(self) -> None:
        scope = self.report["scope"]
        self.assertEqual(scope["bytes"], 9244)
        self.assertEqual(scope["ghidra_recognized"], {
            "functions": 67, "bytes": 8480, "unmapped_functions": 0,
        })
        self.assertEqual(scope["residual_physical"], {
            "intervals": 2,
            "bytes": 56,
            "category_bytes": {"literal-constant-pool": 4, "function-pointer-table": 52},
            "unclassified_bytes": 0,
            "callable_code_bytes": 0,
        })
        physical = self.report["records"]["physical_classification"]
        self.assertEqual([row["bytes"] for row in physical], [4, 52])
        self.assertTrue(all(not row["source_identity_claimed"] for row in physical))

    def test_summary_manifest_matches_deterministic_report(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest["status"], self.report["status"])
        self.assertEqual(manifest["mapping_sha256"], self.report["mapping_sha256"])
        self.assertEqual(manifest["confidence"]["high"], self.report["confidence"]["high"])
        self.assertEqual(manifest["confidence"]["medium"], self.report["confidence"]["medium"])
        self.assertEqual(manifest["confidence"]["mapped_total"], self.report["confidence"]["mapped_total"])
        self.assertFalse(manifest["production_routed"])
        self.assertFalse(manifest["binary_overlay_ready"])

    def test_no_overlay_or_core_builder_routes_the_research_map(self) -> None:
        text = "\n".join(path.read_text() for path in (
            G2 / "components/apollo_main/core_overlay/overlay.json",
            G2 / "components/apollo_main/core_overlay/build_component.py",
        ))
        self.assertNotIn("freetype_pshinter", text)
        self.assertNotIn("g2-freetype-pshinter", text)
        self.assertFalse(self.report["production_routed"])

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
        first = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["mapping_sha256"], self.report["mapping_sha256"])


if __name__ == "__main__":
    unittest.main()
