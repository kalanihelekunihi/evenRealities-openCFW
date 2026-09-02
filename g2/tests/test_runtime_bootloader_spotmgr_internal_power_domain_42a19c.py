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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_internal_power_domain_42a19c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x0042A19C
SIZE = 22
FUNCTION = "open_cfw_bootloader_spotmgr_internal_power_domain_42a19c"
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
    _fields_ = [("hp_to_deep_sleep", ctypes.c_uint8)]


class BootloaderSpotmgrInternalPowerDomain42a19cTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_domain.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.function = getattr(ctypes.CDLL(str(library)), FUNCTION)
        cls.function.argtypes = [ctypes.c_uint8, ctypes.c_uint8,
                                 ctypes.POINTER(State)]
        cls.function.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_source_is_reviewable_bsd_c_without_raw_opcodes(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("prior_state == 1U", body)
        self.assertIn("requested_state == 2U", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)

    def test_portable_transition_marker_over_randomized_states(self):
        rng = random.Random(0x42A19C)
        for _ in range(100_000):
            requested = rng.randrange(256)
            prior = rng.randrange(256)
            initial = rng.randrange(256)
            state = State(initial)
            self.function(requested, prior, ctypes.byref(state))
            expected = 1 if requested == 2 and prior == 1 else initial
            self.assertEqual(state.hp_to_deep_sleep, expected)

    def test_dual_toolchain_body_is_exact_without_relocations(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        expected_sha = "34664d76a6022980a70a926ac4c1108f43d33974584a9cb854f8faa59a8ebacf"
        self.assertEqual(hashlib.sha256(stock).hexdigest(), expected_sha)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
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
                self.assertEqual(report["unrelocated_sha256"], expected_sha)
                self.assertEqual(report["relocation_count"], 0)


if __name__ == "__main__":
    unittest.main()
