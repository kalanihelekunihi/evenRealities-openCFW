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
ANALYZER = G2 / "tools/analyze_g2_freetype_psaux_source_admission.py"
MANIFEST = G2 / "tools/manifests/g2-freetype-psaux-source-admission.json"
COMPONENT = G2 / "components/shared/freetype_psaux"
ADMISSION = COMPONENT / "source_admission.json"
PSAUX_SOURCE = G2 / "third_party/freetype/src/psaux/psaux.c"
FREETYPE = G2 / "third_party/freetype"
FREETYPE_CANDIDATE = G2 / "research/candidates/freetype"


def load_analyzer():
    spec = importlib.util.spec_from_file_location("freetype_psaux_admission", ANALYZER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FreeTypePSAuxSourceAdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.report = cls.analyzer.analyze()

    def test_callable_map_and_complete_source_inventory_are_pinned(self) -> None:
        mapped = self.report["mapped_callable_closure"]
        self.assertEqual({key: mapped[key] for key in (
            "functions", "bytes", "high", "medium", "foreign_callable",
            "residual_noncode_bytes", "unresolved_callable_bytes",
        )}, {
            "functions": 199, "bytes": 29750,
            "high": {"functions": 65, "bytes": 7020},
            "medium": {"functions": 134, "bytes": 22730},
            "foreign_callable": {"functions": 2, "bytes": 762},
            "residual_noncode_bytes": 144, "unresolved_callable_bytes": 0,
        })
        self.assertEqual(self.report["psaux_source_inventory"], {
            "files": 37, "bytes": 625815,
            "inventory_sha256": "3e5cd97d8ebad001edc947962591689cb86780b8174a20e164da00d4a03ee9e1",
        })

    def test_single_object_translation_unit_is_explicit(self) -> None:
        unit = self.report["translation_unit"]
        self.assertEqual(unit["path"], "third_party/freetype/src/psaux/psaux.c")
        self.assertEqual(len(unit["single_object_includes"]), 16)
        source = PSAUX_SOURCE.read_text()
        self.assertIn("FT_MAKE_OPTION_SINGLE_OBJECT", source)
        positions = [source.index(f'#include "{name}"') for name in unit["single_object_includes"]]
        self.assertEqual(positions, sorted(positions))

    def test_cortex_m55_hard_float_translation_unit_compiles(self) -> None:
        clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if clang is None:
            self.skipTest("Clang is required for target compilation")
        with tempfile.TemporaryDirectory(prefix="opencfw-psaux-") as temporary:
            output = Path(temporary) / "psaux.o"
            subprocess.run([
                clang, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                "-mfloat-abi=hard", "-std=c11", "-O2", "-fshort-enums",
                "-ffreestanding", "-fno-builtin", "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                "-DFT2_BUILD_LIBRARY", "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
                "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
                "-I", str(FREETYPE_CANDIDATE / "target_compat"),
                "-I", str(FREETYPE_CANDIDATE / "g2_config"),
                "-I", str(FREETYPE / "g2-config"), "-I", str(FREETYPE / "include"),
                "-I", str(FREETYPE), "-c", str(PSAUX_SOURCE), "-o", str(output),
            ], check=True, capture_output=True, text=True)
            elf = output.read_bytes()
            self.assertGreater(len(elf), 1000)
            self.assertEqual(elf[:4], b"\x7fELF")
            self.assertEqual(struct.unpack_from("<H", elf, 18)[0], 40)

    def test_manifest_cli_and_component_metadata_are_deterministic(self) -> None:
        result = subprocess.run([sys.executable, str(ANALYZER), "--check-manifest"],
                                check=True, capture_output=True, text=True)
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
        with tempfile.TemporaryDirectory(prefix="opencfw-psaux-evidence-") as temporary:
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
        self.assertNotIn("freetype_psaux", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
