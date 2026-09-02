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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_factory_trims_ensure_42a036.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x0042A036
SIZE = 20
FUNCTION = "open_cfw_bootloader_spotmgr_ensure_factory_trims_42a036"
LOADER = "open_cfw_bootloader_spotmgr_load_factory_trims_429da4"
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
        ("factory_trims_pending", ctypes.c_uint8),
        ("loader_calls", ctypes.c_uint32),
    ]


class BootloaderSpotmgrFactoryTrimsEnsure42a036Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "factory_trims_ensure.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.function = getattr(ctypes.CDLL(str(library)), FUNCTION)
        cls.function.argtypes = [ctypes.POINTER(State)]
        cls.function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_source_is_reviewable_c_with_guarded_loader_contract(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: MIT", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("factory_trims_pending != 0U", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)

    def test_portable_semantics_over_random_pending_states(self):
        rng = random.Random(0x42A036)
        for _ in range(100_000):
            pending = rng.randrange(256)
            calls = rng.getrandbits(32)
            state = State(pending, calls)
            self.assertEqual(self.function(ctypes.byref(state)), 0)
            self.assertEqual(
                state.loader_calls,
                (calls + (1 if pending != 0 else 0)) & 0xFFFFFFFF,
            )

    def test_dual_toolchain_body_is_exact_after_loader_relocation(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "9c901638e2c0e882e9f92662df44aa585a49a2e160eb4f2a4c7b32b374ae7a06",
        )
        relocation = [{
            "offset": 12,
            "type": "R_ARM_THM_CALL",
            "symbol": LOADER,
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x00429DA4,
        }]
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
                    relocation_configs=relocation,
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 1)


if __name__ == "__main__":
    unittest.main()
