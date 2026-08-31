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
ANALYZER = G2 / "tools/analyze_g2_freetype_pshinter_source_admission.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-pshinter-source-admission.json"
COMPONENT = G2 / "components/shared/freetype_pshinter"
ADMISSION = COMPONENT / "source_admission.json"
PSHINTER_SOURCE = G2 / "third_party/freetype/src/pshinter/pshinter.c"
FREETYPE = G2 / "third_party/freetype"
FREETYPE_CANDIDATE = G2 / "research/candidates/freetype"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("freetype_pshinter_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypePshinterSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_complete_callable_map_and_source_inventory_are_pinned(self) -> None:
        mapped = self.report["mapped_callable_closure"]
        self.assertEqual(
            {
                key: mapped[key]
                for key in (
                    "functions", "bytes", "high", "medium",
                    "unresolved_callable_bytes",
                )
            },
            {
                "functions": 79,
                "bytes": 9188,
                "high": {"functions": 18, "bytes": 1554},
                "medium": {"functions": 61, "bytes": 7634},
                "unresolved_callable_bytes": 0,
            },
        )
        self.assertFalse(mapped["compiler_byte_identity_claimed"])
        self.assertEqual(
            self.report["pshinter_source_inventory"],
            {
                "files": 12,
                "bytes": 147127,
                "inventory_sha256": (
                    "7001cfa7703fbb1dd13930c9383be836"
                    "f1743485007e4236b274fa9a6763dc07"
                ),
            },
        )

    def test_single_object_translation_unit_is_explicit(self) -> None:
        unit = self.report["translation_unit"]
        self.assertEqual(unit["path"], "third_party/freetype/src/pshinter/pshinter.c")
        self.assertEqual(
            unit["single_object_includes"],
            ["pshalgo.c", "pshglob.c", "pshmod.c", "pshpic.c", "pshrec.c"],
        )
        source = PSHINTER_SOURCE.read_text(encoding="utf-8")
        self.assertIn("FT_MAKE_OPTION_SINGLE_OBJECT", source)
        for name in unit["single_object_includes"]:
            self.assertIn(f'#include "{name}"', source)

    def test_cortex_m55_hard_float_translation_unit_compiles(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("Clang is required for target compilation")
        with tempfile.TemporaryDirectory(prefix="opencfw-pshinter-") as temporary:
            output = Path(temporary) / "pshinter.o"
            subprocess.run(
                [
                    clang,
                    "--target=arm-none-eabi",
                    "-mcpu=cortex-m55",
                    "-mthumb",
                    "-mfloat-abi=hard",
                    "-std=c11",
                    "-O2",
                    "-fshort-enums",
                    "-ffreestanding",
                    "-fno-builtin",
                    "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables",
                    "-Wall",
                    "-Wextra",
                    "-Werror",
                    "-DFT2_BUILD_LIBRARY",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                    "-I", str(FREETYPE_CANDIDATE / "target_compat"),
                    "-I", str(FREETYPE_CANDIDATE / "g2_config"),
                    "-I", str(FREETYPE / "g2-config"),
                    "-I", str(FREETYPE / "include"),
                    "-I", str(FREETYPE),
                    "-c", str(PSHINTER_SOURCE),
                    "-o", str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            elf = output.read_bytes()
            self.assertGreater(len(elf), 1000)
            self.assertEqual(elf[:4], b"\x7fELF")
            self.assertEqual(struct.unpack_from("<H", elf, 18)[0], 40)  # EM_ARM

    def test_manifest_cli_and_component_metadata_are_deterministic(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(result.stdout), self.report)
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        admission = json.loads(ADMISSION.read_text())
        self.assertTrue(admission["build"]["community_source"])
        self.assertFalse(admission["build"]["production_overlay"])
        self.assertFalse(admission["build"]["authenticated_target_placement"])
        self.assertFalse(admission["hardware_validation"]["performed"])

    def test_provenance_mutation_fails_closed(self) -> None:
        data = bytearray(self.analyzer.PROVENANCE.read_bytes())
        data[32] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-pshinter-evidence-") as temporary:
            changed = Path(temporary) / "PROVENANCE.json"
            changed.write_bytes(data)
            with mock.patch.object(self.analyzer, "PROVENANCE", changed):
                with self.assertRaisesRegex(self.analyzer.AdmissionError, "input pin drift"):
                    self.analyzer.analyze()

    def test_no_stock_overlay_or_hardware_claim_is_added(self) -> None:
        production = self.report["production"]
        self.assertFalse(production["stock_image_overlay_routed"])
        self.assertFalse(production["authenticated_target_placement"])
        self.assertFalse(self.report["evidence_bounds"]["hardware_operations"])
        overlay = G2 / "components/apollo_main/core_overlay/overlay.json"
        self.assertNotIn("freetype_pshinter", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
