# SPDX-License-Identifier: MIT

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


G2 = Path(__file__).resolve().parents[1]
ANALYZER = G2 / "tools/analyze_g2_freetype_smooth_source_admission.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-smooth-source-admission.json"
COMPONENT = G2 / "components/shared/freetype_smooth"
ADMISSION = COMPONENT / "source_admission.json"
SMOOTH_SOURCE = G2 / "third_party/freetype/src/smooth/smooth.c"
FREETYPE = G2 / "third_party/freetype"
FREETYPE_CANDIDATE = G2 / "research/candidates/freetype"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("freetype_smooth_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeSmoothSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_complete_callable_map_and_source_inventory_are_pinned(self) -> None:
        mapped = self.report["mapped_callable_closure"]
        self.assertEqual({
            key: mapped[key]
            for key in (
                "functions", "bytes", "high", "medium",
                "unresolved_callable_bytes",
            )
        }, {
            "functions": 29, "bytes": 4310,
            "high": {"functions": 16, "bytes": 804},
            "medium": {"functions": 13, "bytes": 3506},
            "unresolved_callable_bytes": 0,
        })
        self.assertFalse(mapped["compiler_byte_identity_claimed"])
        self.assertEqual(self.report["smooth_source_inventory"], {
            "files": 8, "bytes": 88859,
            "inventory_sha256": (
                "c9a85d138aa31faa688e241ac7ffd70d"
                "8c8943eaf315f79b1c5419646fd20e08"
            ),
        })

    def test_three_renderer_modes_remain_distinct(self) -> None:
        self.assertEqual(self.report["renderer_semantics"], [
            {"name": "smooth", "required_mode": "FT_RENDER_MODE_NORMAL"},
            {"name": "smooth-lcd", "required_mode": "FT_RENDER_MODE_LCD"},
            {"name": "smooth-lcdv", "required_mode": "FT_RENDER_MODE_LCD_V"},
        ])

    def test_single_object_translation_unit_is_explicit(self) -> None:
        unit = self.report["translation_unit"]
        self.assertEqual(unit["path"], "third_party/freetype/src/smooth/smooth.c")
        self.assertEqual(unit["single_object_includes"],
                         ["ftgrays.c", "ftsmooth.c", "ftspic.c"])
        source = SMOOTH_SOURCE.read_text(encoding="utf-8")
        self.assertIn("FT_MAKE_OPTION_SINGLE_OBJECT", source)
        for name in unit["single_object_includes"]:
            self.assertIn(f'#include "{name}"', source)

    def test_cortex_m55_hard_float_translation_unit_compiles_strictly(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("Clang is required for target compilation")
        with tempfile.TemporaryDirectory(prefix="opencfw-smooth-") as temporary:
            output = Path(temporary) / "smooth.o"
            subprocess.run([
                clang,
                "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-mfloat-abi=hard", "-std=c11", "-O2", "-fshort-enums",
                "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                "-DFT2_BUILD_LIBRARY",
                "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                "-I", str(FREETYPE_CANDIDATE / "target_compat"),
                "-I", str(FREETYPE_CANDIDATE / "g2_config"),
                "-I", str(FREETYPE / "g2-config"),
                "-I", str(FREETYPE / "include"),
                "-I", str(FREETYPE),
                "-c", str(SMOOTH_SOURCE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            elf = output.read_bytes()
            self.assertGreater(len(elf), 1000)
            self.assertEqual(elf[:4], b"\x7fELF")
            self.assertEqual(struct.unpack_from("<H", elf, 18)[0], 40)  # EM_ARM
            self.assertIn(b"smooth\x00", elf)
            self.assertIn(b"smooth-lcd\x00", elf)
            self.assertIn(b"smooth-lcdv\x00", elf)

    def test_manifest_cli_and_component_metadata_are_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        admission = json.loads(ADMISSION.read_text())
        self.assertEqual(admission["renderers"], self.report["renderer_semantics"])
        self.assertTrue(admission["build"]["community_source"])
        self.assertFalse(admission["build"]["production_overlay"])
        self.assertFalse(admission["build"]["authenticated_target_placement"])
        self.assertFalse(admission["hardware_validation"]["performed"])

    def test_provenance_and_translation_unit_mutations_fail_closed(self) -> None:
        provenance = bytearray(self.analyzer.PROVENANCE.read_bytes())
        provenance[32] ^= 1
        source = bytearray(SMOOTH_SOURCE.read_bytes())
        source[-10] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-smooth-evidence-") as temporary:
            changed_provenance = Path(temporary) / "PROVENANCE.json"
            changed_source = Path(temporary) / "smooth.c"
            changed_provenance.write_bytes(provenance)
            changed_source.write_bytes(source)
            with mock.patch.object(self.analyzer, "PROVENANCE", changed_provenance):
                with self.assertRaisesRegex(self.analyzer.AdmissionError, "input pin drift"):
                    self.analyzer.analyze()
            with mock.patch.object(self.analyzer, "TRANSLATION_UNIT", changed_source):
                with self.assertRaisesRegex(self.analyzer.AdmissionError, "input pin drift"):
                    self.analyzer.analyze()

    def test_no_stock_overlay_or_hardware_claim_is_added(self) -> None:
        production = self.report["production"]
        self.assertFalse(production["stock_image_overlay_routed"])
        self.assertFalse(production["authenticated_target_placement"])
        self.assertFalse(self.report["evidence_bounds"]["hardware_operations"])
        overlay = G2 / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("freetype_smooth", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
