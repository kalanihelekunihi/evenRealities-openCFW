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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_factory_trims_429da4.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x00429DA4
SIZE = 82
FUNCTION = "open_cfw_bootloader_spotmgr_load_factory_trims_429da4"
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


class State(ctypes.Structure):
    _fields_ = [
        ("ldoreg1", ctypes.c_uint32),
        ("vrefgen2", ctypes.c_uint32),
        ("trim_index", ctypes.c_uint32),
        ("trim_words", ctypes.c_uint32 * 17),
        ("ready", ctypes.c_uint8),
    ]


class BootloaderSpotmgrFactoryTrims429da4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "factory_trims.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.function = getattr(ctypes.CDLL(str(library)), FUNCTION)
        cls.function.argtypes = [ctypes.POINTER(State)]
        cls.function.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_source_is_reviewable_c_with_exact_indexed_contract(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("trim_words[state->trim_index + 1U]", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)

    def test_portable_semantics_over_random_trim_tables(self):
        rng = random.Random(0x429DA4)
        for _ in range(50_000):
            state = State()
            state.ldoreg1 = rng.getrandbits(32)
            state.vrefgen2 = rng.getrandbits(32)
            state.trim_index = rng.randrange(16)
            for index in range(17):
                state.trim_words[index] = rng.getrandbits(32)
            state.ready = rng.randrange(256)
            before_ldo = state.ldoreg1
            before_vref = state.vrefgen2
            record = state.trim_words[state.trim_index + 1]
            self.function(ctypes.byref(state))
            expected_ldo = (before_ldo & ~(0xF << 10)) | (
                ((record >> 17) & 0xF) << 10)
            expected_ldo = (expected_ldo & ~0x3FF) | ((record >> 7) & 0x3FF)
            self.assertEqual(state.ldoreg1, expected_ldo)
            self.assertEqual(
                state.vrefgen2,
                (before_vref & ~0x7F) | ((record >> 21) & 0x7F),
            )
            self.assertEqual(state.ready, 0)

    def test_dual_toolchain_body_is_exact_and_relocation_free(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "a69ea6c52f959eba65684feebd9651d2068cdd0d91caf8eb45d74e52969c61a4",
        )
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                self.assertTrue(compiler.exists(), profile)
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=ADDRESS,
                    relocation_configs=[], strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 0)


if __name__ == "__main__":
    unittest.main()
