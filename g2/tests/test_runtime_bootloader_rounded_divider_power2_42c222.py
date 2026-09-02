import ctypes
import hashlib
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_rounded_divider_power2_42c222.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402


FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = {
    "apple-clang": ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}
FUNCTIONS = (
    ("open_cfw_bootloader_rounded_divider_42c222", 0x0042C222, 52,
     "84a7909276921edf87861325fa09f547e536659109a2de4eeb1fd171f7f57411",
     0x0055BF1C),
    ("open_cfw_bootloader_is_power_of_two_42c256", 0x0042C256, 20,
     "c7c013df5ce01fcc66215af1337fed966a975393591a7bc7e17ebcf71bde8213",
     0x0055BF50),
)


class BootloaderRoundedDividerPower2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "divider_helpers.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.rounded = dll.open_cfw_bootloader_rounded_divider_42c222
        cls.rounded.argtypes = [ctypes.c_uint32] * 5
        cls.rounded.restype = ctypes.c_uint32
        cls.power2 = dll.open_cfw_bootloader_is_power_of_two_42c256
        cls.power2.argtypes = [ctypes.c_uint32]
        cls.power2.restype = ctypes.c_uint8

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_rounded_divider_and_power_of_two_semantics(self):
        rng = random.Random(0x42C222)
        tested = 0
        while tested < 100_000:
            numerator = rng.getrandbits(32)
            exponent = rng.randrange(1, 32)
            first = rng.randrange(256)
            second = rng.randrange(256)
            third = rng.randrange(256)
            denominator = (((first * 2 + 1) << (exponent - 1)) & 0xFFFFFFFF)
            denominator = (denominator * (third * second + 1)) & 0xFFFFFFFF
            if denominator == 0:
                continue
            expected = numerator // denominator
            if numerator % denominator > denominator >> 1:
                expected = (expected + 1) & 0xFFFFFFFF
            self.assertEqual(
                self.rounded(numerator, exponent, first, second, third), expected
            )
            tested += 1
        values = [0, 1, 2, 3, 4, 5, 0x40000000, 0x80000000, 0xFFFFFFFF]
        values.extend(rng.getrandbits(32) for _ in range(100_000))
        for value in values:
            self.assertEqual(self.power2(value),
                             int(value != 0 and value & (value - 1) == 0))

    def test_dual_toolchain_bodies_and_main_analogues_are_exact(self):
        boot = BOOT.read_bytes(); main = MAIN.read_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                for function, address, size, digest, main_address in FUNCTIONS:
                    stock = boot[address - BOOT_BASE:address - BOOT_BASE + size]
                    analogue = main[main_address - MAIN_BASE:
                                    main_address - MAIN_BASE + size]
                    self.assertEqual(hashlib.sha256(stock).hexdigest(), digest)
                    self.assertEqual(stock, analogue)
                    linked, report = apollo_overlay.extract_in_place_function_section(
                        output, function, runtime_address=address,
                        relocation_configs=[], strict_relocation_contract=True,
                        allow_discarded_alloc_sections=True,
                    )
                    self.assertEqual(linked, stock, (profile, function))
                    self.assertEqual(report["relocation_count"], 0)

    def test_source_is_reviewable_mit_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        for function, *_rest in FUNCTIONS:
            self.assertIn(function, body)
        for token in (".byte", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
