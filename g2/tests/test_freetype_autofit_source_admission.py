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
ANALYZER = G2 / "tools/analyze_g2_freetype_autofit_source_admission.py"
MAP_ANALYZER = G2 / "tools/analyze_g2_freetype_autofit_function_map.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-autofit-source-admission.json"
MAP_MANIFEST = G2 / "tools/manifests/g2-freetype-autofit-function-map.json"
COMPONENT = G2 / "components/shared/freetype_autofit"
ADMISSION = COMPONENT / "source_admission.json"
SOURCE = G2 / "third_party/freetype/src/autofit/autofit.c"
FREETYPE = G2 / "third_party/freetype"
CANDIDATE = G2 / "research/candidates/freetype"


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypeAutofitSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load(ANALYZER, "freetype_autofit_admission")
        cls.mapper = load(MAP_ANALYZER, "freetype_autofit_map")
        cls.report = cls.analyzer.analyze()

    def test_callable_and_physical_closure_are_total(self) -> None:
        mapped = self.report["mapped_callable_closure"]
        self.assertEqual({
            key: mapped[key] for key in
            ("functions", "bytes", "high", "medium", "unresolved_callable_bytes")
        }, {
            "functions": 87, "bytes": 23_612,
            "high": {"functions": 29, "bytes": 3_270},
            "medium": {"functions": 58, "bytes": 20_342},
            "unresolved_callable_bytes": 0,
        })
        stock = self.mapper.run_audit()
        self.assertEqual(stock["scope"]["physical_bytes"], 23_704)
        self.assertEqual(stock["scope"]["residual_physical"], {
            "intervals": 5, "bytes": 92,
            "category_bytes": {"literal-constant-pool": 92},
            "unclassified_bytes": 0, "unresolved_callable_bytes": 0,
        })
        intervals = [
            (int(row["start"], 16), int(row["end_exclusive"], 16))
            for row in stock["functions"] + stock["physical_residue"]
        ]
        cursor = 0x005A6260
        for start, end in sorted(intervals):
            self.assertEqual(start, cursor)
            cursor = end
        self.assertEqual(cursor, 0x005ABEF8)

    def test_inventory_and_single_object_order_are_pinned(self) -> None:
        self.assertEqual(self.report["autofit_source_inventory"], {
            "files": 37, "bytes": 650_482,
            "inventory_sha256": "12275283b95378cb5d8695e420b4a39776915ea84d0fd6591deb11653bd0c205",
        })
        unit = self.report["translation_unit"]
        source = SOURCE.read_text(encoding="utf-8")
        positions = [source.index(f'#include "{name}"') for name in unit["single_object_includes"]]
        self.assertEqual(positions, sorted(positions))
        self.assertEqual(unit["compatibility_warning_exception"],
                         "-Wno-cast-function-type-mismatch")

    def test_cortex_m55_hard_float_translation_unit_compiles_strictly(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("Clang is required for target compilation")
        with tempfile.TemporaryDirectory(prefix="opencfw-autofit-") as temporary:
            output = Path(temporary) / "autofit.o"
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-mfloat-abi=hard", "-std=c11", "-O2", "-fshort-enums",
                "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                "-Wno-cast-function-type-mismatch", "-DFT2_BUILD_LIBRARY",
                "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                "-I", str(CANDIDATE / "target_compat"),
                "-I", str(CANDIDATE / "g2_config"),
                "-I", str(FREETYPE / "g2-config"),
                "-I", str(FREETYPE / "include"),
                "-I", str(FREETYPE),
                "-c", str(SOURCE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            elf = output.read_bytes()
            self.assertGreater(len(elf), 50_000)
            self.assertEqual(elf[:4], b"\x7fELF")
            self.assertEqual(struct.unpack_from("<H", elf, 18)[0], 40)

    def test_manifests_and_component_metadata_are_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            check=True, capture_output=True, text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        self.assertEqual(json.loads(MAP_MANIFEST.read_text()), self.mapper.run_audit())
        admission = json.loads(ADMISSION.read_text())
        self.assertTrue(admission["build"]["community_source"])
        self.assertFalse(admission["build"]["production_overlay"])
        self.assertFalse(admission["build"]["authenticated_target_placement"])
        self.assertFalse(admission["hardware_validation"]["performed"])

    def test_image_and_source_mutations_fail_closed(self) -> None:
        image = bytearray(self.mapper.IMAGE.read_bytes())
        image[0x005A6260 - self.mapper.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-autofit-image-") as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.mapper, "IMAGE", changed):
                with self.assertRaisesRegex(self.mapper.MapError, "pin drift"):
                    self.mapper.run_audit()
        source = bytearray(SOURCE.read_bytes())
        source[-10] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-autofit-source-") as temporary:
            changed = Path(temporary) / "autofit.c"
            changed.write_bytes(source)
            with mock.patch.object(self.analyzer, "TRANSLATION_UNIT", changed):
                with self.assertRaisesRegex(self.analyzer.AdmissionError, "input pin drift"):
                    self.analyzer.analyze()

    def test_no_overlay_route_or_hardware_claim_is_added(self) -> None:
        self.assertFalse(self.report["production"]["stock_image_overlay_routed"])
        self.assertFalse(self.report["production"]["authenticated_target_placement"])
        self.assertFalse(self.report["evidence_bounds"]["hardware_operations"])
        overlay = G2 / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("freetype_autofit", overlay.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
