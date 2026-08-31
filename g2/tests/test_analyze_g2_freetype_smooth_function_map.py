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
ANALYZER = G2 / "tools/analyze_g2_freetype_smooth_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-smooth-function-map.json"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("smooth_function_map", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SmoothFunctionMapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = load_analyzer()
        cls.report = cls.module.run_audit()

    def test_complete_callable_and_physical_accounting(self) -> None:
        confidence = self.report["confidence"]
        self.assertEqual(confidence["mapped_total"], {"functions": 29, "bytes": 4310})
        self.assertEqual(confidence["high"], {"functions": 16, "bytes": 804})
        self.assertEqual(confidence["medium"], {"functions": 13, "bytes": 3506})
        self.assertEqual(confidence["unresolved_code"], {
            "functions": 0, "bytes": 0, "source_identities_complete": True,
        })
        scope = self.report["scope"]
        self.assertEqual(scope["bytes"], 4328)
        self.assertEqual(scope["residual_physical"], {
            "intervals": 2, "bytes": 18,
            "category_bytes": {"alignment-padding": 2, "literal-constant-pool": 16},
            "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
        })

    def test_zero_census_moves_to_complete_authenticated_map(self) -> None:
        self.assertEqual(self.report["movement"], {
            "initial_retained_census": {"functions": 0, "bytes": 0},
            "authenticated_complete_map": {"functions": 29, "bytes": 4310},
            "newly_classified_physical": {"intervals": 2, "bytes": 18},
        })

    def test_three_renderer_classes_preserve_distinct_semantics(self) -> None:
        self.assertEqual(self.report["renderer_classes"], [
            {
                "class_address": "0x00718D9C", "name": "smooth",
                "render_callback": "0x005E2648",
                "required_mode": "FT_RENDER_MODE_NORMAL",
                "raster_table": "0x0077BEFC",
            },
            {
                "class_address": "0x00718DD8", "name": "smooth-lcd",
                "render_callback": "0x005E2660",
                "required_mode": "FT_RENDER_MODE_LCD",
                "raster_table": "0x0077BEFC",
            },
            {
                "class_address": "0x00718E14", "name": "smooth-lcdv",
                "render_callback": "0x005E266E",
                "required_mode": "FT_RENDER_MODE_LCD_V",
                "raster_table": "0x0077BEFC",
            },
        ])
        self.assertEqual(len({row["render_callback"] for row in self.report["renderer_classes"]}), 3)

    def test_recovered_callback_boundaries_are_complete(self) -> None:
        rows = {row["symbol"]: row for row in self.report["records"]["smooth"]}
        expected = {
            "gray_move_to": ("0x005E1D6C", "0x005E1D92", 38),
            "gray_raster_reset": ("0x005E2256", "0x005E2258", 2),
            "ft_smooth_init": ("0x005E225C", "0x005E2272", 22),
            "ft_smooth_render": ("0x005E2648", "0x005E2660", 24),
            "ft_smooth_render_lcd": ("0x005E2660", "0x005E266E", 14),
            "ft_smooth_render_lcd_v": ("0x005E266E", "0x005E267C", 14),
        }
        for symbol, wanted in expected.items():
            row = rows[symbol]
            self.assertEqual((row["start"], row["end_exclusive"], row["bytes"]), wanted)
            self.assertEqual(len(row["body_sha256"]), 64)

    def test_high_confidence_rows_have_stock_table_evidence(self) -> None:
        rows = [
            row for row in self.report["records"]["smooth"]
            if row["confidence"] == "high"
        ]
        self.assertEqual((len(rows), sum(row["bytes"] for row in rows)), (16, 804))
        for row in rows:
            self.assertTrue(row["pointer_references"])
            self.assertIn("stock-renderer-outline-or-raster-table-pointer", row["evidence"])
            self.assertEqual(int(row["thumb_pointer"], 16) & ~1,
                             int(row["start"], 16))

    def test_manifest_is_exact_and_deterministic(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        self.assertEqual(manifest, self.report)
        first = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            check=True, capture_output=True, text=True,
        ).stdout
        second = subprocess.run(
            [sys.executable, str(ANALYZER)], check=True, capture_output=True, text=True,
        ).stdout
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), self.report)

    def test_renderer_class_tamper_fails_closed(self) -> None:
        image = bytearray(self.module.IMAGE.read_bytes())
        image[0x00718DD8 - self.module.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-smooth-map-") as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.module, "IMAGE", changed):
                with self.assertRaises(self.module.MapError):
                    self.module.run_audit()

    def test_no_route_or_hardware_claim(self) -> None:
        text = "\n".join(path.read_text() for path in (
            G2 / "components/apollo_main/core_overlay/overlay.json",
            G2 / "components/apollo_main/core_overlay/build_component.py",
        ))
        self.assertNotIn("freetype_smooth", text)
        self.assertFalse(self.report["production_routed"])
        self.assertFalse(self.report["hardware_operations"])


if __name__ == "__main__":
    unittest.main()
