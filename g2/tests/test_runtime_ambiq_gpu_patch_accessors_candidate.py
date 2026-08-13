#!/usr/bin/env python3
"""Qualify the production-excluded Ambiq GPU-patch accessor candidates."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/shared/lvgl/runtime_ambiq_gpu_patch_accessors_candidate.c"
HEADER = SOURCE.with_suffix(".h")
FIXTURE = ROOT / "tests/fixtures/runtime_ambiq_gpu_patch_accessors_candidate_host.c"
MANIFEST = ROOT / "tools/manifests/g2-nemagfx-ambiq-provenance.json"
AUDIT = ROOT / "docs/research/ambiq-gpu-patch-accessor-source-candidate-audit.md"
PUBLIC_HEADER = (
    ROOT.parent.parent
    / "evenrealitiesg2-swiftsdk/openCFW/sdks/AmbiqSuite_v5/components/graphics/"
      "NemaGFX_SDK/extensions/gpu_patch.h"
)

FUNCTIONS = {
    "open_cfw_ambiq_gpu_get_paint_texture_candidate",
    "open_cfw_ambiq_gpu_get_path_aabb_candidate",
    "open_cfw_ambiq_gpu_get_path_vbuf_candidate",
}

TARGET_FLAGS = [
    "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-std=c11",
    "-O2", "-ffreestanding", "-ffunction-sections", "-fdata-sections",
    "-fno-builtin", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables",
    "-Wall", "-Wextra", "-Werror",
]

# The exact public GCC archive sections are independent evidence, not expected
# byte matches for this clean-room Clang candidate.
PUBLIC_ARCHIVE_SECTIONS = {
    "lv_ambiq_get_vg_paint_tex": (
        16, "f3a3a1a552751faddd5cc8a53cbcd5a030048dc39572004d56221486e5d44633"
    ),
    "lv_ambiq_get_path_aabb": (
        24, "e51f6519f355e32c18447d6b26329e6da16cd2e54f0515586f883171de7e2e5c"
    ),
    "lv_ambiq_get_path_vbuf": (
        28, "bdf5a63391e7b275cff1f7b393b3f34ee7bb564d6733dd023e7d107dcecef2af"
    ),
}


class AmbiqGpuPatchAccessorCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if not cls.clang:
            raise unittest.SkipTest("clang is unavailable")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ambiq-gpu-accessors-")
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "accessors.dylib" if sys.platform == "darwin" else "accessors.so"
        )
        host_command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            "-DOPEN_CFW_AMBIQ_GPU_PATCH_HOST_MODEL=1",
            str(SOURCE), str(FIXTURE),
            *( ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"] ),
            "-o", str(library),
        ]
        subprocess.run(host_command, cwd=ROOT, check=True, capture_output=True, text=True)
        cls.lib = ctypes.CDLL(str(library))
        cls.lib.open_cfw_test_ambiq_gpu_set_paint.argtypes = [ctypes.c_uint32] * 3
        cls.lib.open_cfw_test_ambiq_gpu_set_vbuf.argtypes = [ctypes.c_uint32] * 4
        cls.lib.open_cfw_test_ambiq_gpu_set_bounds.argtypes = [ctypes.c_float] * 4
        for name in (
            "get_image", "get_palette", "get_segments", "get_data",
            "get_segment_size", "get_data_size",
        ):
            getattr(cls.lib, "open_cfw_test_ambiq_gpu_" + name).restype = ctypes.c_uint32
        cls.lib.open_cfw_test_ambiq_gpu_get_bound.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_test_ambiq_gpu_get_bound.restype = ctypes.c_float

        cls.target_object = temporary / "accessors.o"
        subprocess.run(
            [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)],
            cwd=ROOT, check=True, capture_output=True, text=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.lib.open_cfw_test_ambiq_gpu_reset()

    def test_paint_accessor_sets_image_and_lut_palette(self) -> None:
        self.lib.open_cfw_test_ambiq_gpu_set_paint(0x11223344, 0x55667788, 1)
        self.lib.open_cfw_test_ambiq_gpu_run_paint()
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_image(), 0x11223344)
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_palette(), 0x55667788)

    def test_non_lut_palette_is_zeroed_as_archive_and_header_require(self) -> None:
        self.lib.open_cfw_test_ambiq_gpu_set_paint(0x12345678, 0xDEADBEEF, 0)
        self.lib.open_cfw_test_ambiq_gpu_run_paint()
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_image(), 0x12345678)
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_palette(), 0)

    def test_path_aabb_returns_untransformed_minimum_and_maximum(self) -> None:
        expected = (-7.25, 3.5, 91.0, 104.125)
        self.lib.open_cfw_test_ambiq_gpu_set_bounds(*expected)
        self.lib.open_cfw_test_ambiq_gpu_run_bounds()
        self.assertEqual(
            tuple(self.lib.open_cfw_test_ambiq_gpu_get_bound(index) for index in range(4)),
            expected,
        )

    def test_path_vbuf_returns_four_leading_fields(self) -> None:
        self.lib.open_cfw_test_ambiq_gpu_set_vbuf(17, 88, 0x20001234, 0x20005678)
        self.lib.open_cfw_test_ambiq_gpu_run_vbuf()
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_segment_size(), 17)
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_data_size(), 88)
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_segments(), 0x20001234)
        self.assertEqual(self.lib.open_cfw_test_ambiq_gpu_get_data(), 0x20005678)

    def test_target_layout_assertions_compile_and_functions_are_relocation_free(self) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(self.target_object)
        names = {str(section["name"]): section for section in sections}
        for function in FUNCTIONS:
            section = names[".text." + function]
            self.assertGreater(int(section["size"]), 0)
            self.assertEqual(int(section["alignment"]), 4)
            relocation_sections = [
                candidate for candidate in sections
                if int(candidate["type"]) == 9
                and int(candidate["info"]) == int(section["index"])
                and int(candidate["size"]) != 0
            ]
            self.assertEqual(relocation_sections, [])
        self.assertTrue(data.startswith(b"\x7fELF"))

    def test_manifest_pins_exact_public_archive_sections_and_private_layouts(self) -> None:
        manifest = json.loads(MANIFEST.read_text())
        recovery = manifest["gpu_patch"]["binary_recovery"]
        observed = {
            item["function"]: (item["section_size"], item["section_sha256"])
            for item in recovery["accessors"]
        }
        self.assertEqual(observed, PUBLIC_ARCHIVE_SECTIONS)
        self.assertEqual(recovery["dwarf_source"], "gpu_patch/ambiq_nema_extension.c")
        self.assertEqual(recovery["private_layouts"]["nema_vg_paint_t"], 0xE0)
        self.assertEqual(recovery["private_layouts"]["nema_vg_path_t"], 0x88)
        self.assertEqual(recovery["private_layouts"]["nema_vbuf_t_"], 0x60)

    def test_public_header_and_candidate_document_the_same_non_lut_contract(self) -> None:
        if PUBLIC_HEADER.is_file():
            text = PUBLIC_HEADER.read_text(errors="replace")
            self.assertIn("If the texture is not a LUT", text)
            self.assertIn("set to NULL", text)
        candidate = SOURCE.read_text()
        self.assertIn(": (open_cfw_ambiq_gpu_address)0", candidate)

    def test_candidate_is_separately_named_and_production_excluded(self) -> None:
        source = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: GPL-3.0-only", source)
        for exported in (
            "lv_ambiq_get_vg_paint_tex", "lv_ambiq_get_path_aabb", "lv_ambiq_get_path_vbuf"
        ):
            self.assertNotIn("void " + exported + "(", source)
        production = "\n".join(
            path.read_text(errors="replace")
            for path in (
                ROOT / "components/apollo_main/core_overlay/overlay.json",
                ROOT / "manifests/g2-2.2.6.10-core-source.json",
            )
        )
        for function in FUNCTIONS:
            self.assertNotIn(function, production)


if __name__ == "__main__":
    unittest.main()
