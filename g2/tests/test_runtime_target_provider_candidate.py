# SPDX-License-Identifier: MIT

from __future__ import annotations

import ctypes
import math
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "research" / "candidates" / "target_runtime"
SCALAR = COMPONENT / "runtime_target_scalar_candidate.c"
HEADER = COMPONENT / "runtime_target_scalar_candidate.h"
BRIDGE = COMPONENT / "runtime_target_aeabi_bridge.c"
README = COMPONENT / "README.md"
DIVMOD = ROOT / "components" / "apollo_main" / "core_overlay" / "aeabi_divmod.c"

LIBLC3 = ROOT / "third_party" / "liblc3"
LIBLC3_COMPONENT = ROOT / "components" / "shared" / "liblc3"
LIBLC3_SOURCES = tuple(
    LIBLC3 / "src" / name
    for name in (
        "attdet.c", "bits.c", "bwdet.c", "energy.c", "lc3.c", "ltpf.c",
        "mdct.c", "plc.c", "sns.c", "spec.c", "tables.c", "tns.c",
    )
) + (LIBLC3_COMPONENT / "runtime_liblc3_encoder_candidate.c",)

FREETYPE = ROOT / "third_party" / "freetype"
FREETYPE_COMPONENT = ROOT / "research" / "candidates" / "freetype"
FREETYPE_SYSTEM = FREETYPE_COMPONENT / "runtime_freetype_system_candidate.c"
FREETYPE_CLUSTER = (
    FREETYPE_COMPONENT / "runtime_freetype_base_cluster_candidate.c"
)
FREETYPE_TRUETYPE = (
    ROOT / "components/shared/freetype/runtime_freetype_truetype.c"
)
FREETYPE_CFF_COMPONENT = ROOT / "components/shared/freetype_cff"
FREETYPE_CFF = FREETYPE_CFF_COMPONENT / "runtime_freetype_cff.c"
FREETYPE_JUMP = FREETYPE_COMPONENT / "runtime_freetype_jump_candidate.c"
FREETYPE_SOURCES = tuple(
    FREETYPE / "src" / name
    for name in (
        "base/ftbase.c", "base/ftinit.c", "base/ftbitmap.c",
        "autofit/autofit.c", "truetype/truetype.c", "cff/cff.c",
        "psaux/psaux.c", "psnames/psnames.c", "pshinter/pshinter.c",
        "sfnt/sfnt.c", "smooth/smooth.c",
    )
) + (
    FREETYPE_COMPONENT / "runtime_freetype_base_candidate.c",
    FREETYPE_SYSTEM,
    FREETYPE_CLUSTER,
    FREETYPE_TRUETYPE,
    FREETYPE_CFF,
    FREETYPE_JUMP,
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
    "-DOPEN_CFW_FREETYPE_JMP_BUF_BYTES=128",
    "-DOPEN_CFW_FREETYPE_JMP_BUF_ALIGNMENT=8",
)

REMAINING_TARGET_SEAMS: set[str] = set()

CLOSED_PROVIDER_NAMES = {
    "__aeabi_memclr",
    "__aeabi_memclr4",
    "__aeabi_memcpy4",
    "__aeabi_uldivmod",
    "fabsf",
    "floorf",
    "fmaxf",
    "fminf",
    "memchr",
    "memcmp",
    "memcpy",
    "memmove",
    "memset",
    "qsort",
    "roundf",
    "sqrtf",
    "strcat",
    "strcmp",
    "strcpy",
    "strlen",
    "strncmp",
    "strncpy",
    "strrchr",
    "strstr",
    "truncf",
    "FT_Done_Memory",
    "FT_New_Memory",
    "FT_Stream_Open",
    "open_cfw_freetype_external_longjmp",
    "open_cfw_freetype_external_setjmp",
}


def _llvm_tool(name: str) -> str | None:
    discovered = shutil.which(name)
    if discovered:
        return discovered
    for prefix in (Path("/opt/homebrew/opt/llvm/bin"), Path("/usr/local/opt/llvm/bin")):
        candidate = prefix / name
        if candidate.exists():
            return str(candidate)
    return None


def _float_bits(value: float) -> int:
    return struct.unpack("=I", struct.pack("=f", value))[0]


class RuntimeTargetScalarHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.clang = os.environ.get("OPENCFW_CLANG") or shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required for provider qualification")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-target-runtime-")
        output = Path(cls.temporary.name) / (
            "target-runtime.dylib" if sys.platform == "darwin" else "target-runtime.so"
        )
        command = [
            cls.clang, "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            str(SCALAR),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(output)))
        else:
            command.extend(("-shared", "-fPIC", "-lm", "-o", str(output)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.library = ctypes.CDLL(str(output))

        for name in ("fabsf", "floorf", "roundf", "sqrtf", "truncf"):
            function = getattr(cls.library, f"open_cfw_target_{name}")
            function.argtypes = [ctypes.c_float]
            function.restype = ctypes.c_float
            setattr(cls, name, function)
        for name in ("fminf", "fmaxf"):
            function = getattr(cls.library, f"open_cfw_target_{name}")
            function.argtypes = [ctypes.c_float, ctypes.c_float]
            function.restype = ctypes.c_float
            setattr(cls, name, function)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_memory_overlap_search_and_unsigned_comparison(self) -> None:
        memmove = self.library.open_cfw_target_memmove
        memmove.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        memmove.restype = ctypes.c_void_p
        data = ctypes.create_string_buffer(b"abcdefgh", 9)
        returned = memmove(ctypes.byref(data, 2), data, 6)
        self.assertEqual(returned, ctypes.addressof(data) + 2)
        self.assertEqual(data.raw, b"ababcdef\x00")

        memchr = self.library.open_cfw_target_memchr
        memchr.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_size_t]
        memchr.restype = ctypes.c_void_p
        self.assertEqual(memchr(data, ord("d"), 8), ctypes.addressof(data) + 5)
        self.assertFalse(memchr(data, ord("z"), 8))

        memcmp = self.library.open_cfw_target_memcmp
        memcmp.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t]
        memcmp.restype = ctypes.c_int
        high = (ctypes.c_ubyte * 1)(0xFF)
        low = (ctypes.c_ubyte * 1)(0x01)
        self.assertGreater(memcmp(high, low, 1), 0)

    def test_string_surface_and_zero_padding(self) -> None:
        strcpy = self.library.open_cfw_target_strcpy
        strcpy.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        strcat = self.library.open_cfw_target_strcat
        strcat.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        strncpy = self.library.open_cfw_target_strncpy
        strncpy.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t]
        strstr = self.library.open_cfw_target_strstr
        strstr.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        strstr.restype = ctypes.c_void_p
        strrchr = self.library.open_cfw_target_strrchr
        strrchr.argtypes = [ctypes.c_char_p, ctypes.c_int]
        strrchr.restype = ctypes.c_void_p

        output = ctypes.create_string_buffer(16)
        strcpy(output, b"open")
        strcat(output, b"cfw")
        self.assertEqual(output.value, b"opencfw")
        self.assertEqual(strstr(output, b"enc"), ctypes.addressof(output) + 2)
        self.assertEqual(strrchr(output, ord("o")), ctypes.addressof(output))
        self.assertEqual(strrchr(output, 0), ctypes.addressof(output) + 7)
        padded = (ctypes.c_ubyte * 6)(*[0xA5] * 6)
        strncpy(padded, b"g2", 6)
        self.assertEqual(bytes(padded), b"g2\0\0\0\0")

    def test_qsort_orders_records_without_allocator_or_recursion(self) -> None:
        compare_type = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p)

        @compare_type
        def compare(first: int, second: int) -> int:
            left = ctypes.cast(first, ctypes.POINTER(ctypes.c_int))[0]
            right = ctypes.cast(second, ctypes.POINTER(ctypes.c_int))[0]
            return (left > right) - (left < right)

        qsort = self.library.open_cfw_target_qsort
        qsort.argtypes = [ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t, compare_type]
        values = (ctypes.c_int * 8)(7, -4, 7, 0, 2, -9, 1, 2)
        qsort(values, len(values), ctypes.sizeof(ctypes.c_int), compare)
        self.assertEqual(list(values), [-9, -4, 0, 1, 2, 2, 7, 7])

    def test_ieee_scalar_rounding_boundaries_and_special_values(self) -> None:
        self.assertEqual(_float_bits(self.fabsf(-0.0)), 0)
        self.assertEqual(_float_bits(self.truncf(-0.75)), 0x80000000)
        self.assertEqual(self.truncf(-3.75), -3.0)
        self.assertEqual(self.floorf(-3.25), -4.0)
        self.assertEqual(self.floorf(3.75), 3.0)
        self.assertEqual(self.roundf(ctypes.c_float.from_buffer_copy(struct.pack("=I", 0x3EFFFFFF)).value), 0.0)
        self.assertEqual(self.roundf(0.5), 1.0)
        self.assertEqual(self.roundf(-0.5), -1.0)
        self.assertEqual(self.roundf(2.5), 3.0)
        self.assertTrue(math.isinf(self.truncf(float("inf"))))
        self.assertTrue(math.isnan(self.floorf(float("nan"))))

    def test_minmax_signed_zero_nan_and_hardware_sqrt_contract(self) -> None:
        nan = float("nan")
        self.assertEqual(self.fminf(nan, 4.0), 4.0)
        self.assertEqual(self.fmaxf(4.0, nan), 4.0)
        self.assertEqual(_float_bits(self.fminf(0.0, -0.0)), 0x80000000)
        self.assertEqual(_float_bits(self.fmaxf(-0.0, 0.0)), 0)
        self.assertEqual(self.sqrtf(9.0), 3.0)
        self.assertEqual(_float_bits(self.sqrtf(-0.0)), 0x80000000)
        self.assertTrue(math.isnan(self.sqrtf(-1.0)))


class RuntimeTargetProviderLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.llvm_link = _llvm_tool("llvm-link")
        cls.llvm_nm = _llvm_tool("llvm-nm")
        if cls.llvm_link is None or cls.llvm_nm is None:
            raise unittest.SkipTest("LLVM link and symbol tools are required")
        adjacent_clang = str(Path(cls.llvm_link).with_name("clang"))
        cls.clang = adjacent_clang if Path(adjacent_clang).exists() else shutil.which("clang")
        if cls.clang is None:
            raise unittest.SkipTest("Clang is required for target link qualification")
        cls.temporary = tempfile.TemporaryDirectory(prefix="opencfw-target-irlink-")
        cls.output = Path(cls.temporary.name)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def _compile(self, source: Path, output: Path, extra: tuple[str, ...]) -> None:
        subprocess.run(
            [self.clang, *TARGET_FLAGS, *extra, "-emit-llvm", "-c", str(source), "-o", str(output)],
            check=True,
            capture_output=True,
            text=True,
        )

    def test_cortex_m55_link_closes_shared_runtime_and_exposes_only_policy_seams(self) -> None:
        objects: list[Path] = []
        liblc3_includes = (
            "-ffast-math",
            "-I", str(LIBLC3_COMPONENT / "target_compat"),
            "-I", str(LIBLC3 / "include"),
            "-I", str(LIBLC3 / "src"),
            "-I", str(LIBLC3_COMPONENT),
        )
        freetype_includes = (
            "-Wno-cast-function-type-mismatch", "-DFT2_BUILD_LIBRARY",
            "-I", str(FREETYPE_COMPONENT / "target_compat"),
            "-I", str(FREETYPE_COMPONENT / "g2_config"),
            "-I", str(FREETYPE / "g2-config"),
            "-I", str(FREETYPE / "include"),
            "-I", str(FREETYPE),
            "-I", str(FREETYPE_COMPONENT),
            "-I", str(FREETYPE_CFF_COMPONENT),
        )
        for index, source in enumerate(LIBLC3_SOURCES):
            output = self.output / f"liblc3-{index}.bc"
            self._compile(source, output, liblc3_includes)
            objects.append(output)
        for index, source in enumerate(FREETYPE_SOURCES):
            output = self.output / f"freetype-{index}.bc"
            self._compile(source, output, freetype_includes)
            objects.append(output)
        for index, source in enumerate((SCALAR, BRIDGE, DIVMOD)):
            output = self.output / f"provider-{index}.bc"
            self._compile(
                source,
                output,
                ("-DOPEN_CFW_TARGET_RUNTIME_EXPORT_NAMES",),
            )
            objects.append(output)

        linked = self.output / "g2-candidate-runtime-linked.bc"
        subprocess.run(
            [self.llvm_link, *(str(path) for path in objects), "-o", str(linked)],
            check=True,
            capture_output=True,
            text=True,
        )
        undefined_result = subprocess.run(
            [self.llvm_nm, "--undefined-only", str(linked)],
            check=True,
            capture_output=True,
            text=True,
        )
        undefined = {line.split()[-1] for line in undefined_result.stdout.splitlines() if line.strip()}
        self.assertEqual(undefined, REMAINING_TARGET_SEAMS)
        self.assertTrue(CLOSED_PROVIDER_NAMES.isdisjoint(undefined))

        defined_result = subprocess.run(
            [self.llvm_nm, "--defined-only", str(linked)],
            check=True,
            capture_output=True,
            text=True,
        )
        defined = {line.split()[-1] for line in defined_result.stdout.splitlines() if line.strip()}
        self.assertTrue(CLOSED_PROVIDER_NAMES <= defined)
        self.assertIn("open_cfw_aeabi_uldivmod", defined)
        self.assertIn("open_cfw_freetype_truetype_set_interpreter", defined)
        self.assertIn("open_cfw_freetype_truetype_get_interpreter", defined)
        for symbol in (
            "open_cfw_freetype_cff_set_hinting_engine",
            "open_cfw_freetype_cff_get_hinting_engine",
            "open_cfw_freetype_cff_set_no_stem_darkening",
            "open_cfw_freetype_cff_get_no_stem_darkening",
            "open_cfw_freetype_cff_set_darkening_parameters",
            "open_cfw_freetype_cff_get_darkening_parameters",
        ):
            self.assertIn(symbol, defined)
        self.assertNotIn("FT_Gzip_Uncompress", defined)

    def test_provider_sources_emit_cortex_m55_arm_objects(self) -> None:
        readobj = _llvm_tool("llvm-readobj")
        if readobj is None:
            self.skipTest("llvm-readobj is required for ELF header qualification")
        for source, definitions in (
            (SCALAR, ("-DOPEN_CFW_TARGET_RUNTIME_EXPORT_NAMES",)),
            (BRIDGE, ()),
            (DIVMOD, ()),
        ):
            with self.subTest(source=source.name):
                output = self.output / f"{source.stem}.o"
                subprocess.run(
                    [self.clang, *TARGET_FLAGS, *definitions, "-c", str(source), "-o", str(output)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                result = subprocess.run(
                    [readobj, "--file-headers", "--arch-specific", str(output)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                self.assertIn("Machine: EM_ARM", result.stdout)
                self.assertIn("Value: cortex-m55", result.stdout)
                self.assertIn("Description: ARM v8.1-M Mainline", result.stdout)
                self.assertIn("TagName: ABI_VFP_args", result.stdout)
                self.assertIn("Description: AAPCS VFP", result.stdout)

    def test_licenses_documented_seams_and_production_exclusion(self) -> None:
        self.assertIn("SPDX-License-Identifier: MIT", SCALAR.read_text())
        self.assertIn("SPDX-License-Identifier: MIT", HEADER.read_text())
        self.assertIn("SPDX-License-Identifier: MIT", FREETYPE_JUMP.read_text())
        self.assertIn("SPDX-License-Identifier: MIT", BRIDGE.read_text())
        documentation = README.read_text()
        self.assertIn("no unresolved symbols", documentation)
        for symbol in (
            "open_cfw_freetype_external_setjmp",
            "open_cfw_freetype_external_longjmp",
        ):
            self.assertIn(symbol, documentation)
        overlay = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
        self.assertNotIn("target_runtime", overlay.read_text())


if __name__ == "__main__":
    unittest.main()
