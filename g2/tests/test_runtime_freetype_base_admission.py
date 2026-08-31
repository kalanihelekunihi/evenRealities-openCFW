# SPDX-License-Identifier: MIT

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_runtime_freetype_base_candidate import minimal_truetype_font


ROOT = Path(__file__).resolve().parents[1]
ANALYZER = ROOT / "tools/analyze_g2_freetype_base_source_admission.py"
MAP_ANALYZER = ROOT / "tools/analyze_g2_freetype_base_function_map.py"
MANIFEST = ROOT / "tools/manifests/g2-freetype-base-source-admission.json"
MAP_MANIFEST = ROOT / "tools/manifests/g2-freetype-base-function-map.json"
COMPONENT = ROOT / "components/shared/freetype_base"
SOURCE = COMPONENT / "runtime_freetype_base.c"
HEADER = COMPONENT / "runtime_freetype_base.h"
FACE_SOURCE = COMPONENT / "runtime_freetype_base_face.c"
FACE_HEADER = COMPONENT / "runtime_freetype_base_face.h"
ADMISSION = COMPONENT / "source_admission.json"
RESEARCH = ROOT / "research/candidates/freetype"
SYSTEM_SOURCE = RESEARCH / "runtime_freetype_system_candidate.c"
FIXTURE = ROOT / "tests/fixtures/runtime_freetype_base_admission_host.c"
SNAPSHOT = ROOT / "third_party/freetype"
INCLUDE = SNAPSHOT / "include"
G2_MODULE_CONFIG = SNAPSHOT / "g2-config"
G2_OPTION_CONFIG = RESEARCH / "g2_config"
TARGET_COMPAT = RESEARCH / "target_compat"

FREETYPE_SOURCES = (
    SNAPSHOT / "src/base/ftbase.c",
    SNAPSHOT / "src/base/ftinit.c",
    SNAPSHOT / "src/base/ftbitmap.c",
    SNAPSHOT / "src/autofit/autofit.c",
    SNAPSHOT / "src/truetype/truetype.c",
    SNAPSHOT / "src/cff/cff.c",
    SNAPSHOT / "src/psaux/psaux.c",
    SNAPSHOT / "src/psnames/psnames.c",
    SNAPSHOT / "src/pshinter/pshinter.c",
    SNAPSHOT / "src/sfnt/sfnt.c",
    SNAPSHOT / "src/smooth/smooth.c",
)
TARGET_FLAGS = (
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
    "-Wno-cast-function-type-mismatch",
    "-DFT2_BUILD_LIBRARY",
    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
)
MODULE_NAMES = (
    "autofitter", "truetype", "cff", "psaux", "psnames", "pshinter",
    "sfnt", "smooth", "smooth-lcd", "smooth-lcdv",
)


def load_analyzer(path: Path = ANALYZER, name: str = "freetype_base_source_admission"):
    spec = importlib.util.spec_from_file_location(
        name, path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RuntimeFreeTypeBaseAdmissionTests(unittest.TestCase):
    OK = 0

    @classmethod
    def setUpClass(cls) -> None:
        cls.analyzer = load_analyzer()
        cls.mapper = load_analyzer(MAP_ANALYZER, "freetype_base_complete_map")
        cls.report = cls.analyzer.analyze()
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required for base admission")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-ft-base-")
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "freetype-base.dylib" if sys.platform == "darwin"
            else "freetype-base.so"
        )
        command = [
            cls.clang,
            "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-Wno-cast-function-type-mismatch", "-DFT2_BUILD_LIBRARY",
            "-I", str(G2_OPTION_CONFIG),
            "-I", str(G2_MODULE_CONFIG),
            "-I", str(INCLUDE),
            "-I", str(SNAPSHOT),
            "-I", str(COMPONENT),
            "-I", str(RESEARCH),
            str(SOURCE), str(FACE_SOURCE), str(SYSTEM_SOURCE), str(FIXTURE),
            *(str(path) for path in FREETYPE_SOURCES),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        configure = cls.library.open_cfw_test_freetype_system_configure
        configure.restype = ctypes.c_int
        if configure() != 0:
            raise RuntimeError("FreeType system fixture configuration failed")

        cls.reset = cls.library.open_cfw_test_freetype_reset
        cls.reset.argtypes = [ctypes.c_size_t]
        cls.init = cls.library.open_cfw_test_freetype_init
        cls.init.restype = ctypes.c_int
        cls.done = cls.library.open_cfw_test_freetype_done
        cls.done.restype = ctypes.c_int
        cls.get_library = cls.library.open_cfw_test_freetype_library
        cls.get_library.restype = ctypes.c_void_p
        cls.live_blocks = cls.library.open_cfw_test_freetype_live_blocks
        cls.live_blocks.restype = ctypes.c_size_t
        cls.allocation_calls = cls.library.open_cfw_test_freetype_allocation_calls
        cls.allocation_calls.restype = ctypes.c_size_t
        cls.ft_get_module = cls.library.FT_Get_Module
        cls.ft_get_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        cls.ft_get_module.restype = ctypes.c_void_p
        cls.open_memory = cls.library.open_cfw_test_freetype_open_memory_policy
        cls.open_memory.argtypes = [
            ctypes.c_void_p, ctypes.c_size_t, ctypes.c_long, ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.open_memory.restype = ctypes.c_int
        cls.release_face = cls.library.open_cfw_freetype_base_release_face
        cls.release_face.argtypes = [ctypes.c_void_p]
        cls.release_face.restype = ctypes.c_int
        cls.load_and_render = cls.library.open_cfw_freetype_base_load_and_render
        cls.load_and_render.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_int32, ctypes.c_int,
        ]
        cls.load_and_render.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_mapping_source_inventory_and_complete_physical_map_are_exact(self) -> None:
        retained = self.report["retained_source_evidence"]
        self.assertEqual(
            retained["mapped_callable_closure"]["mapped_total"],
            {"functions": 182, "bytes": 20_442},
        )
        self.assertEqual(
            retained["base_cluster"]["admitted_cluster"],
            {"functions": 83, "bytes": 7_874},
        )
        self.assertEqual(
            retained["base_cluster"]["remaining_cluster"],
            {"functions": 0, "bytes": 0, "rows": []},
        )
        inventory = self.report["base_source_inventory"]
        self.assertEqual((inventory["files"], inventory["bytes"]), (21, 429_079))
        self.assertEqual(len(inventory["records"]), 21)
        stock = self.mapper.run_audit()
        self.assertEqual(stock["scope"]["physical_bytes"], 20_676)
        self.assertEqual(stock["scope"]["residual_physical"], {
            "intervals": 15,
            "bytes": 234,
            "category_bytes": {
                "alignment-padding": 4,
                "literal-pointer-data-pool": 230,
            },
            "unclassified_bytes": 0,
            "unresolved_callable_bytes": 0,
        })
        intervals = [
            (int(row["start"], 16), int(row["end_exclusive"], 16))
            for row in stock["functions"] + stock["physical_residue"]
        ]
        cursor = 0x005242FC
        for start, end in sorted(intervals):
            self.assertEqual(start, cursor)
            cursor = end
        self.assertEqual(cursor, 0x005293C0)

    def test_narrow_candidate_and_ghidra_boundary_correction_remain_explicit(self) -> None:
        stock = self.mapper.run_audit()
        self.assertEqual(stock["candidate_distinction"], {
            "existing_candidate_functions": 90,
            "existing_candidate_bytes": 9_736,
            "newly_mapped_functions": 92,
            "newly_mapped_callable_bytes": 10_706,
            "existing_candidate_scope": (
                "83-function reachable base cluster plus seven Mac-resource "
                "mechanics; not a complete physical map"
            ),
            "this_scope": "complete stock base callable and physical envelope",
        })
        correction = stock["boundary_corrections"]
        self.assertEqual(correction["ghidra_internal_basic_block_removed"], "0x005292C8")
        self.assertEqual(correction["corrected_source_body"], {
            "symbol": "ft_mem_strcpyn",
            "start": "0x005292BC",
            "end_exclusive": "0x005292E6",
            "bytes": 42,
        })
        self.assertEqual(correction["ghidra_missed_complete_callables"], 5)

    def test_manifest_cli_and_production_exclusion_are_fail_closed(self) -> None:
        self.assertEqual(json.loads(MANIFEST.read_text()), self.report)
        self.assertEqual(json.loads(MAP_MANIFEST.read_text()), self.mapper.run_audit())
        result = subprocess.run(
            [sys.executable, str(ANALYZER), "--check-manifest"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        production = self.report["production"]
        self.assertTrue(
            production["authenticated_stock_initializer_sequence_recovered"]
        )
        self.assertFalse(production["authenticated_stock_teardown_entry_recovered"])
        self.assertFalse(production["authenticated_target_placement"])
        self.assertFalse(production["stock_image_overlay_routed"])
        self.assertFalse(
            json.loads(ADMISSION.read_text())["hardware_validation"]["performed"]
        )

    def test_inventory_identity_mutation_is_rejected(self) -> None:
        expected = self.analyzer.EXPECTED_INVENTORY_SHA256
        self.analyzer.EXPECTED_INVENTORY_SHA256 = "0" * 64
        try:
            with self.assertRaisesRegex(
                self.analyzer.AdmissionError,
                "base source inventory digest changed",
            ):
                self.analyzer.analyze()
        finally:
            self.analyzer.EXPECTED_INVENTORY_SHA256 = expected

    def test_image_corpus_source_and_residue_mutations_fail_closed(self) -> None:
        image = bytearray(self.mapper.IMAGE.read_bytes())
        image[0x00528272 - self.mapper.LOAD_BASE] ^= 1
        with tempfile.TemporaryDirectory(prefix="opencfw-ft-base-map-image-") as temporary:
            changed = Path(temporary) / "image.bin"
            changed.write_bytes(image)
            with mock.patch.object(self.mapper, "IMAGE", changed):
                with self.assertRaisesRegex(self.mapper.MapError, "input pin drift"):
                    self.mapper.run_audit()

        with tempfile.TemporaryDirectory(prefix="opencfw-ft-base-map-corpus-") as temporary:
            decomp = Path(temporary)
            for name in self.mapper.DECOMP_PINS:
                shutil.copy2(self.mapper.DECOMP / name, decomp / name)
            changed = decomp / "apollo-decomp-09.c"
            data = bytearray(changed.read_bytes())
            data[100] ^= 1
            changed.write_bytes(data)
            with mock.patch.object(self.mapper, "DECOMP", decomp):
                with self.assertRaisesRegex(self.mapper.MapError, "input pin drift"):
                    self.mapper.run_audit()

        with tempfile.TemporaryDirectory(prefix="opencfw-ft-base-map-source-") as temporary:
            snapshot = Path(temporary)
            shutil.copy2(self.mapper.PROVENANCE, snapshot / "PROVENANCE.json")
            shutil.copy2(self.mapper.LICENSE, snapshot / "LICENSE")
            for source in self.mapper.run_audit()["source_inventory"]["sha256_by_path"]:
                destination = snapshot / source
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.mapper.SNAPSHOT / source, destination)
            changed = snapshot / "src/base/fttrigon.c"
            data = bytearray(changed.read_bytes())
            data[-10] ^= 1
            changed.write_bytes(data)
            with mock.patch.multiple(
                self.mapper,
                SNAPSHOT=snapshot,
                PROVENANCE=snapshot / "PROVENANCE.json",
                LICENSE=snapshot / "LICENSE",
            ):
                with self.assertRaisesRegex(self.mapper.MapError, "source identity drift"):
                    self.mapper.run_audit()

        physical = list(self.mapper.PHYSICAL)
        start, end, category, _ = physical[0]
        physical[0] = (start, end, category, "0" * 64)
        with mock.patch.object(self.mapper, "PHYSICAL", tuple(physical)):
            with self.assertRaisesRegex(self.mapper.MapError, "physical residue drift"):
                self.mapper.run_audit()

    def test_maintained_allocator_lifecycle_and_exact_module_set(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        library = self.get_library()
        self.assertTrue(library)
        for name in MODULE_NAMES:
            self.assertTrue(self.ft_get_module(library, name.encode()), name)
        self.assertEqual(self.init(), -5)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)
        self.assertEqual(self.done(), -1)

    def test_every_injected_initialization_failure_is_leak_free(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        allocation_count = self.allocation_calls()
        self.assertEqual(self.done(), self.OK)
        for fail_at in range(1, allocation_count + 1):
            with self.subTest(fail_at=fail_at):
                self.reset(fail_at)
                if self.init() == self.OK:
                    self.assertEqual(self.done(), self.OK)
                self.assertEqual(self.live_blocks(), 0)

    def test_memory_face_policies_and_render_bridge_use_actual_freetype(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        font_bytes = minimal_truetype_font()
        font = (ctypes.c_ubyte * len(font_bytes)).from_buffer_copy(font_bytes)
        baseline = self.live_blocks()
        for policy in (0, 1):
            with self.subTest(policy=policy):
                face = ctypes.c_void_p()
                self.assertEqual(
                    self.open_memory(
                        font, len(font_bytes), 0, policy, ctypes.byref(face)
                    ),
                    0,
                )
                self.assertTrue(face.value)
                self.assertEqual(self.load_and_render(face, 0, 0, 0), 0)
                self.assertEqual(self.release_face(face), 0)
                self.assertEqual(self.live_blocks(), baseline)
        for policy in (2, 99):
            face = ctypes.c_void_p(1)
            self.assertNotEqual(
                self.open_memory(
                    font, len(font_bytes), 0, policy, ctypes.byref(face)
                ),
                0,
            )
            self.assertFalse(face.value)
            self.assertEqual(self.live_blocks(), baseline)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)

    def test_base_component_and_selected_translation_units_compile_for_m55(self) -> None:
        output_dir = Path(self.temporary.name) / "target"
        output_dir.mkdir()
        sources = (
            SOURCE, FACE_SOURCE,
            SNAPSHOT / "src/base/ftbase.c",
            SNAPSHOT / "src/base/ftinit.c",
            SNAPSHOT / "src/base/ftbitmap.c",
        )
        for source in sources:
            with self.subTest(source=source.name):
                output = output_dir / f"{source.stem}.o"
                subprocess.run(
                    [
                        self.clang, *TARGET_FLAGS,
                        "-I", str(TARGET_COMPAT),
                        "-I", str(G2_OPTION_CONFIG),
                        "-I", str(G2_MODULE_CONFIG),
                        "-I", str(INCLUDE),
                        "-I", str(SNAPSHOT),
                        "-I", str(COMPONENT),
                        "-c", str(source), "-o", str(output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertGreater(output.stat().st_size, 0)

    def test_component_surface_is_ftl_and_uses_only_public_lifecycle_apis(self) -> None:
        for path in (SOURCE, HEADER, FACE_SOURCE, FACE_HEADER):
            self.assertIn("SPDX-License-Identifier: FTL", path.read_text())
        combined = SOURCE.read_text() + FACE_SOURCE.read_text()
        for token in (
            "FT_New_Library", "FT_Add_Default_Modules", "FT_Done_Library",
            "FT_Open_Face", "FT_Done_Face", "FT_Render_Glyph",
        ):
            self.assertIn(token, combined)


if __name__ == "__main__":
    unittest.main()
