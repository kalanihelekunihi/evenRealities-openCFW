# SPDX-License-Identifier: FTL

from __future__ import annotations

import ctypes
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "research" / "candidates" / "freetype"
SOURCE = COMPONENT / "runtime_freetype_base_candidate.c"
HEADER = COMPONENT / "runtime_freetype_base_candidate.h"
SYSTEM_SOURCE = COMPONENT / "runtime_freetype_system_candidate.c"
SYSTEM_HEADER = COMPONENT / "runtime_freetype_system_candidate.h"
CLUSTER_SOURCE = COMPONENT / "runtime_freetype_base_cluster_candidate.c"
CLUSTER_HEADER = COMPONENT / "runtime_freetype_base_cluster_candidate.h"
TRUETYPE_COMPONENT = ROOT / "components" / "shared" / "freetype"
TRUETYPE_SOURCE = TRUETYPE_COMPONENT / "runtime_freetype_truetype.c"
TRUETYPE_HEADER = TRUETYPE_COMPONENT / "runtime_freetype_truetype.h"
JUMP_SOURCE = COMPONENT / "runtime_freetype_jump_candidate.c"
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_freetype_base_candidate_host.c"
SNAPSHOT = ROOT / "third_party" / "freetype"
INCLUDE = SNAPSHOT / "include"
G2_MODULE_CONFIG = SNAPSHOT / "g2-config"
G2_OPTION_CONFIG = COMPONENT / "g2_config"
TARGET_COMPAT = COMPONENT / "target_compat"

FREETYPE_SOURCES = (
    SNAPSHOT / "src" / "base" / "ftbase.c",
    SNAPSHOT / "src" / "base" / "ftinit.c",
    SNAPSHOT / "src" / "base" / "ftbitmap.c",
    SNAPSHOT / "src" / "autofit" / "autofit.c",
    SNAPSHOT / "src" / "truetype" / "truetype.c",
    SNAPSHOT / "src" / "cff" / "cff.c",
    SNAPSHOT / "src" / "psaux" / "psaux.c",
    SNAPSHOT / "src" / "psnames" / "psnames.c",
    SNAPSHOT / "src" / "pshinter" / "pshinter.c",
    SNAPSHOT / "src" / "sfnt" / "sfnt.c",
    SNAPSHOT / "src" / "smooth" / "smooth.c",
)

TARGET_ADMISSION_SOURCES = FREETYPE_SOURCES + (
    SYSTEM_SOURCE,
    CLUSTER_SOURCE,
    TRUETYPE_SOURCE,
    JUMP_SOURCE,
)

MODULE_NAMES = (
    "autofitter",
    "truetype",
    "cff",
    "psaux",
    "psnames",
    "pshinter",
    "sfnt",
    "smooth",
    "smooth-lcd",
    "smooth-lcdv",
)

TARGET_FLAGS = (
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-mfloat-abi=hard",
    "-std=c11",
    "-O2",
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


def _checksum(data: bytes) -> int:
    padded = data + bytes((-len(data)) % 4)
    return sum(struct.unpack(f">{len(padded) // 4}I", padded)) & 0xFFFFFFFF


def minimal_truetype_font() -> bytes:
    """Build a deterministic one-empty-glyph SFNT for lifecycle tests."""

    head = bytearray(54)
    struct.pack_into(
        ">IIIIHHQQhhhhHHhhh",
        head,
        0,
        0x00010000,
        0x00010000,
        0,
        0x5F0F3CF5,
        0,
        1000,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        8,
        2,
        0,
        0,
    )
    hhea = bytearray(36)
    struct.pack_into(">IhhhH", hhea, 0, 0x00010000, 800, -200, 0, 500)
    struct.pack_into(">H", hhea, 34, 1)
    maxp = struct.pack(">IH", 0x00005000, 1)
    hmtx = struct.pack(">Hh", 500, 0)
    loca = struct.pack(">HH", 0, 0)
    cmap_subtable = struct.pack(">HHH", 0, 262, 0) + bytes(256)
    cmap = struct.pack(">HHHHI", 0, 1, 3, 1, 12) + cmap_subtable
    family = "OpenCFW".encode("utf-16-be")
    name = struct.pack(">HHH", 0, 1, 18)
    name += struct.pack(">HHHHHH", 3, 1, 0x0409, 1, len(family), 0)
    name += family
    post = struct.pack(">IihhIIIII", 0x00030000, 0, 0, 0, 0, 0, 0, 0, 0)

    tables = {
        b"cmap": cmap,
        b"glyf": b"",
        b"head": bytes(head),
        b"hhea": bytes(hhea),
        b"hmtx": hmtx,
        b"loca": loca,
        b"maxp": maxp,
        b"name": name,
        b"post": post,
    }
    count = len(tables)
    maximum_power = 1 << (count.bit_length() - 1)
    header = struct.pack(
        ">IHHHH",
        0x00010000,
        count,
        maximum_power * 16,
        maximum_power.bit_length() - 1,
        count * 16 - maximum_power * 16,
    )
    records = bytearray()
    body = bytearray()
    offset = 12 + 16 * count
    table_offsets: dict[bytes, int] = {}
    for tag, data in sorted(tables.items()):
        table_offsets[tag] = offset
        records += struct.pack(">4sIII", tag, _checksum(data), offset, len(data))
        body += data
        padding = (-len(data)) % 4
        body += bytes(padding)
        offset += len(data) + padding
    font = bytearray(header + records + body)
    adjustment_offset = table_offsets[b"head"] + 8
    adjustment = (0xB1B0AFBA - _checksum(font)) & 0xFFFFFFFF
    struct.pack_into(">I", font, adjustment_offset, adjustment)
    return bytes(font)


class RuntimeFreeTypeBaseCandidateTests(unittest.TestCase):
    OK = 0
    INVALID = -1
    BUSY = -5

    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required for candidate qualification")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-freetype-")
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "freetype-candidate.dylib"
            if sys.platform == "darwin"
            else "freetype-candidate.so"
        )
        command = [
            cls.clang,
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-cast-function-type-mismatch",
            "-DFT2_BUILD_LIBRARY",
            "-I",
            str(G2_OPTION_CONFIG),
            "-I",
            str(G2_MODULE_CONFIG),
            "-I",
            str(INCLUDE),
            "-I",
            str(SNAPSHOT),
            "-I",
            str(COMPONENT),
            str(SOURCE),
            str(SYSTEM_SOURCE),
            str(CLUSTER_SOURCE),
            str(TRUETYPE_SOURCE),
            str(FIXTURE),
            *(str(path) for path in FREETYPE_SOURCES),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(library))
        configure_system = cls.library.open_cfw_test_freetype_system_configure
        configure_system.restype = ctypes.c_int
        if configure_system() != 0:
            raise RuntimeError("FreeType test system provider configuration failed")

        cls.reset = cls.library.open_cfw_test_freetype_reset
        cls.reset.argtypes = [ctypes.c_size_t]
        cls.init = cls.library.open_cfw_test_freetype_init
        cls.init.restype = ctypes.c_int
        cls.done = cls.library.open_cfw_test_freetype_done
        cls.done.restype = ctypes.c_int
        cls.get_library = cls.library.open_cfw_test_freetype_library
        cls.get_library.restype = ctypes.c_void_p
        for name in (
            "allocation_calls",
            "release_calls",
            "live_blocks",
            "memory_size",
        ):
            function = getattr(cls.library, f"open_cfw_test_freetype_{name}")
            function.restype = ctypes.c_size_t
            setattr(cls, name, function)

        cls.ft_get_module = cls.library.FT_Get_Module
        cls.ft_get_module.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        cls.ft_get_module.restype = ctypes.c_void_p
        cls.ft_library_version = cls.library.FT_Library_Version
        cls.ft_library_version.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
            ctypes.POINTER(ctypes.c_int),
        ]
        cls.ft_init = cls.library.FT_Init_FreeType
        cls.ft_init.argtypes = [ctypes.POINTER(ctypes.c_void_p)]
        cls.ft_init.restype = ctypes.c_int
        cls.ft_done = cls.library.FT_Done_FreeType
        cls.ft_done.argtypes = [ctypes.c_void_p]
        cls.ft_done.restype = ctypes.c_int
        cls.ft_property_set = cls.library.FT_Property_Set
        cls.ft_property_set.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_void_p,
        ]
        cls.ft_property_set.restype = ctypes.c_int
        cls.ft_property_get = cls.library.FT_Property_Get
        cls.ft_property_get.argtypes = cls.ft_property_set.argtypes
        cls.ft_property_get.restype = ctypes.c_int
        cls.ft_new_memory_face = cls.library.FT_New_Memory_Face
        cls.ft_new_memory_face.argtypes = [
            ctypes.c_void_p,
            ctypes.c_void_p,
            ctypes.c_long,
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.ft_new_memory_face.restype = ctypes.c_int
        cls.ft_done_face = cls.library.FT_Done_Face
        cls.ft_done_face.argtypes = [ctypes.c_void_p]
        cls.ft_done_face.restype = ctypes.c_int
        cls.ft_new_face = cls.library.FT_New_Face
        cls.ft_new_face.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.ft_new_face.restype = ctypes.c_int
        cls.set_path_data = cls.library.open_cfw_test_freetype_set_path_data
        cls.set_path_data.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        cls.path_release_calls = (
            cls.library.open_cfw_test_freetype_path_release_calls
        )
        cls.path_release_calls.restype = ctypes.c_size_t
        cls.open_memory_policy = (
            cls.library.open_cfw_test_freetype_open_memory_policy
        )
        cls.open_memory_policy.argtypes = [
            ctypes.c_void_p,
            ctypes.c_size_t,
            ctypes.c_long,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_void_p),
        ]
        cls.open_memory_policy.restype = ctypes.c_int
        cls.reference_face = cls.library.open_cfw_freetype_base_reference_face
        cls.reference_face.argtypes = [ctypes.c_void_p]
        cls.reference_face.restype = ctypes.c_int
        cls.release_face = cls.library.open_cfw_freetype_base_release_face
        cls.release_face.argtypes = [ctypes.c_void_p]
        cls.release_face.restype = ctypes.c_int
        cls.load_and_render = cls.library.open_cfw_freetype_base_load_and_render
        cls.load_and_render.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint,
            ctypes.c_int32,
            ctypes.c_int,
        ]
        cls.load_and_render.restype = ctypes.c_int
        cls.set_tt_interpreter = (
            cls.library.open_cfw_freetype_truetype_set_interpreter
        )
        cls.set_tt_interpreter.argtypes = [ctypes.c_void_p, ctypes.c_uint]
        cls.set_tt_interpreter.restype = ctypes.c_int
        cls.get_tt_interpreter = (
            cls.library.open_cfw_freetype_truetype_get_interpreter
        )
        cls.get_tt_interpreter.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_uint),
        ]
        cls.get_tt_interpreter.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_recovered_allocator_lifecycle_and_exact_module_set(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        library = self.get_library()
        self.assertTrue(library)
        self.assertGreater(self.allocation_calls(), 1)
        self.assertGreater(self.live_blocks(), 1)
        for name in MODULE_NAMES:
            self.assertTrue(self.ft_get_module(library, name.encode("ascii")), name)
        for absent in ("type1", "raster1", "pcf", "bdf", "winfonts"):
            self.assertFalse(self.ft_get_module(library, absent.encode("ascii")))

        major = ctypes.c_int()
        minor = ctypes.c_int()
        patch = ctypes.c_int()
        self.ft_library_version(
            library, ctypes.byref(major), ctypes.byref(minor), ctypes.byref(patch)
        )
        self.assertEqual((major.value, minor.value, patch.value), (2, 9, 1))
        self.assertEqual(self.init(), self.BUSY)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)
        self.assertEqual(self.done(), self.INVALID)

    def test_base_property_set_get_entries(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        library = self.get_library()
        engine = ctypes.c_uint(1)
        self.assertEqual(
            self.ft_property_set(
                library, b"cff", b"hinting-engine", ctypes.byref(engine)
            ),
            0,
        )
        actual = ctypes.c_uint(0)
        self.assertEqual(
            self.ft_property_get(
                library, b"cff", b"hinting-engine", ctypes.byref(actual)
            ),
            0,
        )
        self.assertEqual(actual.value, 1)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)

    def test_truetype_interpreter_property_adapter(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        library = self.get_library()
        version = ctypes.c_uint(0)
        self.assertEqual(
            self.get_tt_interpreter(library, ctypes.byref(version)), self.OK
        )
        self.assertEqual(version.value, 40)
        self.assertEqual(self.set_tt_interpreter(library, 35), self.OK)
        self.assertEqual(
            self.get_tt_interpreter(library, ctypes.byref(version)), self.OK
        )
        self.assertEqual(version.value, 35)
        self.assertNotEqual(self.set_tt_interpreter(library, 38), self.OK)
        self.assertEqual(
            self.get_tt_interpreter(library, ctypes.byref(version)), self.OK
        )
        self.assertEqual(version.value, 35)
        self.assertEqual(self.set_tt_interpreter(library, 40), self.OK)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)

    def test_open_face_and_done_face_lifecycle(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        library = self.get_library()

        invalid_data = (ctypes.c_ubyte * 8)(*b"notfont")
        face = ctypes.c_void_p()
        self.assertNotEqual(
            self.ft_new_memory_face(
                library, invalid_data, len(invalid_data), 0, ctypes.byref(face)
            ),
            0,
        )
        self.assertFalse(face.value)

        font_data = minimal_truetype_font()
        font = (ctypes.c_ubyte * len(font_data)).from_buffer_copy(font_data)
        self.assertEqual(
            self.ft_new_memory_face(
                library, font, len(font_data), 0, ctypes.byref(face)
            ),
            0,
        )
        self.assertTrue(face.value)
        self.assertEqual(self.ft_done_face(face), 0)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)

    def test_explicit_loader_policy_and_reference_lifecycle(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        font_data = minimal_truetype_font()
        font = (ctypes.c_ubyte * len(font_data)).from_buffer_copy(font_data)
        baseline = self.live_blocks()

        # Stock-equivalent upstream autodetection remains available.
        face = ctypes.c_void_p()
        self.assertEqual(
            self.open_memory_policy(
                font, len(font_data), 0, 0, ctypes.byref(face)
            ),
            0,
        )
        self.assertTrue(face.value)
        self.assertEqual(self.release_face(face), 0)
        self.assertEqual(self.live_blocks(), baseline)

        # A known G2 TrueType asset can bypass every fallback loader.
        face = ctypes.c_void_p()
        self.assertEqual(
            self.open_memory_policy(
                font, len(font_data), 0, 1, ctypes.byref(face)
            ),
            0,
        )
        self.assertEqual(self.load_and_render(face, 0, 0, 0), 0)
        self.assertNotEqual(self.load_and_render(face, 1, 0, 0), 0)
        self.assertEqual(self.reference_face(face), 0)
        self.assertEqual(self.release_face(face), 0)
        self.assertGreater(self.live_blocks(), baseline)
        self.assertEqual(self.release_face(face), 0)
        self.assertEqual(self.live_blocks(), baseline)

        # Driver mismatch and unknown policy fail without retaining a face.
        for policy in (2, 99):
            face = ctypes.c_void_p(1)
            self.assertNotEqual(
                self.open_memory_policy(
                    font, len(font_data), 0, policy, ctypes.byref(face)
                ),
                0,
            )
            self.assertFalse(face.value)
            self.assertEqual(self.live_blocks(), baseline)
        self.assertNotEqual(self.reference_face(None), 0)
        self.assertNotEqual(self.release_face(None), 0)
        self.assertNotEqual(self.load_and_render(None, 0, 0, 0), 0)
        self.assertEqual(self.done(), self.OK)
        self.assertEqual(self.live_blocks(), 0)

    def test_conventional_upstream_init_entry_remains_source_callable(self) -> None:
        library = ctypes.c_void_p()
        self.assertEqual(self.ft_init(ctypes.byref(library)), 0)
        self.assertTrue(library.value)
        for name in MODULE_NAMES:
            self.assertTrue(self.ft_get_module(library, name.encode("ascii")), name)
        self.assertEqual(self.ft_done(library), 0)

    def test_typed_path_resolver_opens_and_releases_memory_view(self) -> None:
        library = ctypes.c_void_p()
        self.assertEqual(self.ft_init(ctypes.byref(library)), 0)
        font_data = minimal_truetype_font()
        font = (ctypes.c_ubyte * len(font_data)).from_buffer_copy(font_data)
        self.set_path_data(font, len(font_data))
        face = ctypes.c_void_p()
        self.assertEqual(
            self.ft_new_face(
                library, b"open-cfw-font", 0, ctypes.byref(face)
            ),
            0,
        )
        self.assertTrue(face.value)
        self.assertEqual(self.ft_done_face(face), 0)
        self.assertEqual(self.path_release_calls(), 1)
        missing = ctypes.c_void_p()
        self.assertNotEqual(
            self.ft_new_face(library, b"missing", 0, ctypes.byref(missing)),
            0,
        )
        self.assertFalse(missing.value)
        self.assertEqual(self.ft_done(library), 0)

    def test_every_injected_allocator_failure_is_leak_free(self) -> None:
        self.reset(0)
        self.assertEqual(self.init(), self.OK)
        successful_allocation_count = self.allocation_calls()
        self.assertEqual(self.done(), self.OK)
        for fail_at in range(1, successful_allocation_count + 1):
            with self.subTest(fail_at=fail_at):
                self.reset(fail_at)
                result = self.init()
                if result == self.OK:
                    self.assertEqual(self.done(), self.OK)
                self.assertEqual(self.live_blocks(), 0)

    def test_base_tranche_and_adapter_compile_for_cortex_m55(self) -> None:
        target = Path(self.temporary.name) / "target"
        target.mkdir()
        for source in (*TARGET_ADMISSION_SOURCES, SOURCE):
            with self.subTest(source=source.name):
                output = target / f"{source.stem}.o"
                subprocess.run(
                    [
                        self.clang,
                        *TARGET_FLAGS,
                        "-I",
                        str(TARGET_COMPAT),
                        "-I",
                        str(G2_OPTION_CONFIG),
                        "-I",
                        str(G2_MODULE_CONFIG),
                        "-I",
                        str(INCLUDE),
                        "-I",
                        str(SNAPSHOT),
                        "-I",
                        str(COMPONENT),
                        "-c",
                        str(source),
                        "-o",
                        str(output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertGreater(output.stat().st_size, 0)

    def test_target_jump_boundary_requires_selected_dimensions(self) -> None:
        output = Path(self.temporary.name) / "missing-jump-abi.o"
        result = subprocess.run(
            [
                self.clang,
                *(flag for flag in TARGET_FLAGS
                  if not flag.startswith("-DOPEN_CFW_FREETYPE_JMP_BUF_")),
                "-I",
                str(TARGET_COMPAT),
                "-I",
                str(G2_OPTION_CONFIG),
                "-I",
                str(G2_MODULE_CONFIG),
                "-I",
                str(INCLUDE),
                "-I",
                str(SNAPSHOT),
                "-c",
                str(SNAPSHOT / "src" / "smooth" / "smooth.c"),
                "-o",
                str(output),
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "select the target setjmp provider buffer size and alignment",
            result.stderr,
        )

    def test_snapshot_license_configuration_and_production_exclusion(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SNAPSHOT / "verify_snapshot.py")],
            cwd=SNAPSHOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SPDX-License-Identifier: FTL", SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", HEADER.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", SYSTEM_SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", SYSTEM_HEADER.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", CLUSTER_SOURCE.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", CLUSTER_HEADER.read_text())
        self.assertIn("SPDX-License-Identifier: FTL", TRUETYPE_HEADER.read_text())
        self.assertIn("SPDX-License-Identifier: MIT", JUMP_SOURCE.read_text())
        documentation = (COMPONENT / "README.md").read_text()
        self.assertIn("zero unresolved symbols", documentation)
        self.assertIn("JUMP_ABI_EVIDENCE.md", documentation)
        option = (G2_OPTION_CONFIG / "freetype" / "config" / "ftoption.h").read_text()
        self.assertIn("#undef FT_CONFIG_OPTION_ENVIRONMENT_PROPERTIES", option)
        self.assertIn("#undef FT_CONFIG_OPTION_USE_ZLIB", option)
        overlay = (
            ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
        ).read_text()
        self.assertNotIn("runtime_freetype_base_candidate", overlay)


if __name__ == "__main__":
    unittest.main()
