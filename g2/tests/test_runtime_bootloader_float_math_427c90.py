import ctypes
import hashlib
import math
from pathlib import Path
import random
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_float_math_427c90.c"
VENEERS = ROOT / "components/bootloader/core_overlay/runtime_float_math_veneers_427c90.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_float_math_427c90_host.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FUNCTIONS = (
    ("open_cfw_bootloader_floorf_427c90", 0x00427C90, 16,
     "open_cfw_bootloader_floor_bits_427ca0", 0x00427CA0),
    ("open_cfw_bootloader_floor_bits_427ca0", 0x00427CA0, 44, None, None),
    ("open_cfw_bootloader_fmodf_427ccc", 0x00427CCC, 16,
     "open_cfw_bootloader_fmod_bits_427cdc", 0x00427CDC),
    ("open_cfw_bootloader_fmod_bits_427cdc", 0x00427CDC, 168, None, None),
    ("open_cfw_bootloader_roundf_427d98", 0x00427D98, 16,
     "open_cfw_bootloader_round_bits_427da8", 0x00427DA8),
    ("open_cfw_bootloader_round_bits_427da8", 0x00427DA8, 40, None, None),
    ("open_cfw_bootloader_ceilf_427dd0", 0x00427DD0, 16,
     "open_cfw_bootloader_ceil_bits_427de0", 0x00427DE0),
    ("open_cfw_bootloader_ceil_bits_427de0", 0x00427DE0, 44, None, None),
    ("open_cfw_bootloader_float_range_classify_427e0c", 0x00427E0C, 72,
     None, None),
)
FULL_ENDS = {
    0x00427C90: 0x00427CA0,
    0x00427CA0: 0x00427CCC,
    0x00427CCC: 0x00427CDC,
    0x00427CDC: 0x00427D98,
    0x00427D98: 0x00427DA8,
    0x00427DA8: 0x00427DD0,
    0x00427DD0: 0x00427DE0,
    0x00427DE0: 0x00427E0C,
    0x00427E0C: 0x00427E84,
}
FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = {
    "apple-clang": Path("/usr/bin/clang"),
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}


def bits_to_float(bits):
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def float_to_bits(value):
    return struct.unpack("<I", struct.pack("<f", value))[0]


def f32(value):
    return bits_to_float(float_to_bits(value))


def ordered_oracle(bits, operation):
    exponent = (bits >> 23) & 0xFF
    if exponent == 0xFF or (bits << 1) & 0xFFFFFFFF == 0:
        return bits
    value = bits_to_float(bits)
    if operation == "floor":
        integer = math.floor(value)
    elif operation == "ceil":
        integer = math.ceil(value)
    else:
        integer = math.floor(abs(value) + 0.5)
        if value < 0.0:
            integer = -integer
    if integer == 0:
        return bits & 0x80000000
    return float_to_bits(float(integer))


def fmod_oracle(x_bits, y_bits):
    x_exponent = (x_bits >> 23) & 0xFF
    y_exponent = (y_bits >> 23) & 0xFF
    if ((y_bits << 1) & 0xFFFFFFFF) == 0 or y_exponent == 0xFF or x_exponent == 0xFF:
        return 0x7FFFFFFF
    return float_to_bits(f32(math.fmod(bits_to_float(x_bits), bits_to_float(y_bits))))


def classifier_oracle(bits):
    value = bits_to_float(bits)
    if value < -20.0 and not value < 50.0:
        return 0
    if not value < -20.0 and value < 0.0:
        return 1
    if not value < 0.0 and value < 1000.0:
        return 2
    if not value < 50.0 and value < bits_to_float(0x4FFEE92D):
        return 3
    return 4


class BootloaderFloatMath427c90Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "float_math.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(FIXTURE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        cls.lib = ctypes.CDLL(str(library))
        for name in (
            "open_cfw_bootloader_floor_bits_427ca0",
            "open_cfw_bootloader_round_bits_427da8",
            "open_cfw_bootloader_ceil_bits_427de0",
        ):
            fn = getattr(cls.lib, name)
            fn.argtypes = [ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
        cls.lib.open_cfw_bootloader_fmod_bits_427cdc.argtypes = [
            ctypes.c_uint32, ctypes.c_uint32,
        ]
        cls.lib.open_cfw_bootloader_fmod_bits_427cdc.restype = ctypes.c_uint32
        cls.lib.open_cfw_float_math_host_classify_bits.argtypes = [ctypes.c_uint32]
        cls.lib.open_cfw_float_math_host_classify_bits.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_freestanding_source_policy(self):
        texts = [path.read_text(encoding="utf-8") for path in (SOURCE, VENEERS)]
        for text in texts:
            self.assertIn("SPDX-License-Identifier: MIT", text)
            self.assertNotIn("#include", text)
            self.assertNotIn("double", text)
            self.assertNotIn("math.h", text)
        combined = "\n".join(texts)
        for name, _address, _size, _target, _target_address in FUNCTIONS:
            self.assertIn(name, combined)

    def test_rounding_boundaries_and_random_binary32(self):
        vectors = {
            0x00000000, 0x80000000, 0x00000001, 0x80000001,
            0x3EFFFFFF, 0x3F000000, 0x3F000001, 0xBF000000,
            0xBF000001, 0x3F7FFFFF, 0xBF7FFFFF, 0x3FC00000,
            0xBFC00000, 0x4AFFFFFF, 0xCAFFFFFF, 0x4B000000,
            0xCB000000, 0x7F800000, 0xFF800000, 0x7FC12345,
            0xFFC12345,
        }
        rng = random.Random(0x427C90)
        vectors.update(rng.getrandbits(32) for _ in range(30_000))
        functions = (
            (self.lib.open_cfw_bootloader_floor_bits_427ca0, "floor"),
            (self.lib.open_cfw_bootloader_round_bits_427da8, "round"),
            (self.lib.open_cfw_bootloader_ceil_bits_427de0, "ceil"),
        )
        for function, operation in functions:
            for bits in vectors:
                self.assertEqual(function(bits), ordered_oracle(bits, operation),
                                 (operation, hex(bits)))

    def test_fmod_boundaries_and_random_binary32(self):
        vectors = (
            (0x00000000, 0x3F800000), (0x80000000, 0x3F800000),
            (0x3F800000, 0x00000000), (0x3F800000, 0x80000000),
            (0x3F800000, 0x3F800000), (0xBF800000, 0x3F800000),
            (0x40400000, 0x40000000), (0xC0400000, 0x40000000),
            (0x00000001, 0x00000002), (0x007FFFFF, 0x00000101),
            (0x7F7FFFFF, 0x00800000), (0x7F800000, 0x3F800000),
            (0x7FC12345, 0x3F800000), (0x3F800000, 0x7F800000),
            (0x3F800000, 0x7FC12345),
        )
        rng = random.Random(0x427CDC)
        samples = list(vectors)
        samples.extend((rng.getrandbits(32), rng.getrandbits(32))
                       for _ in range(75_000))
        function = self.lib.open_cfw_bootloader_fmod_bits_427cdc
        for x_bits, y_bits in samples:
            self.assertEqual(function(x_bits, y_bits),
                             fmod_oracle(x_bits, y_bits),
                             (hex(x_bits), hex(y_bits)))

    def test_classifier_boundaries_and_random_binary32(self):
        threshold = 0x4FFEE92D
        vectors = {
            0, 0x80000000, 0xC1A00000, 0xC1A00001, 0xC19FFFFF,
            0x4479FFFF, 0x447A0000, threshold - 1, threshold,
            0x7F800000, 0xFF800000, 0x7FC00001, 0xFFC00001,
        }
        rng = random.Random(0x427E0C)
        vectors.update(rng.getrandbits(32) for _ in range(30_000))
        function = self.lib.open_cfw_float_math_host_classify_bits
        for bits in vectors:
            self.assertEqual(function(bits), classifier_oracle(bits), hex(bits))

    def test_dual_toolchain_sections_fit_authenticated_windows(self):
        stock = BOOT.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                self.assertTrue(compiler.exists(), profile)
                outputs = {}
                for label, source in (("cores", SOURCE), ("veneers", VENEERS)):
                    output = Path(temporary) / f"{profile}-{label}.o"
                    subprocess.run(
                        [str(compiler), *FLAGS, "-c", str(source), "-o", str(output)],
                        check=True, capture_output=True, text=True,
                    )
                    outputs[label] = output
                for name, address, expected_size, target, target_address in FUNCTIONS:
                    relocations = [] if target is None else [{
                        "offset": 6,
                        "type": "R_ARM_THM_CALL",
                        "symbol": target,
                        "symbol_type": "STT_NOTYPE",
                        "target_address": target_address,
                    }]
                    output = outputs["veneers" if target is not None else "cores"]
                    body, report = apollo_overlay.extract_in_place_function_section(
                        output, name, runtime_address=address,
                        relocation_configs=relocations,
                        strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(len(body), expected_size, (profile, name))
                    self.assertLessEqual(address + len(body), FULL_ENDS[address])
                    self.assertEqual(report["relocation_count"], len(relocations))
                    if address not in (0x00427CDC, 0x00427E0C):
                        expected = stock[address - BOOT_BASE:
                                         address - BOOT_BASE + len(body)]
                        self.assertEqual(body, expected, (profile, name))


if __name__ == "__main__":
    unittest.main()
