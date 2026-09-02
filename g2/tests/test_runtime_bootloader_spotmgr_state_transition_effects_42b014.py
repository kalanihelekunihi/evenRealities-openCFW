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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_state_transition_effects_42b014.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
ADDRESS = 0x0042B014
SIZE = 84
FUNCTION = "open_cfw_bootloader_spotmgr_state_transition_effects_42b014"
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
        ("hp_entry_pending", ctypes.c_uint8),
        ("deep_sleep_entry_pending", ctypes.c_uint8),
        ("power_control", ctypes.c_uint32),
    ]


class BootloaderSpotmgrStateTransitionEffects42b014Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_effects.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        cls.function = getattr(ctypes.CDLL(str(library)), FUNCTION)
        cls.function.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                                 ctypes.POINTER(State)]
        cls.function.restype = None

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_all_low_byte_state_pairs_and_flag_gates(self):
        rng = random.Random(0x42B014)
        clear_mask = 0x10000 | 0x08 | 0x40
        for prior in range(256):
            for next_state in range(256):
                initial_hp = (prior ^ next_state) & 1
                initial_deep = (prior + next_state) & 1
                power = rng.getrandbits(32)
                state = State(initial_hp, initial_deep, power)
                self.function(prior, next_state, ctypes.byref(state))
                expected_deep = initial_deep
                if next_state == 1 and prior == 2 and initial_hp == 0:
                    expected_deep = 1
                expected_hp = initial_hp
                expected_power = power
                if next_state == 1 and prior == 0:
                    expected_hp = 0
                    expected_power &= ~clear_mask
                self.assertEqual(state.hp_entry_pending, expected_hp)
                self.assertEqual(state.deep_sleep_entry_pending, expected_deep)
                self.assertEqual(state.power_control, expected_power)

    def test_dual_toolchain_body_and_main_analogue_are_exact(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        main = MAIN.read_bytes()[0x005A0D44 - MAIN_BASE:0x005A0D98 - MAIN_BASE]
        expected = "b3da01a94a3c08eb7eb0d7d344b6760d929296878e2dfbf9c4770373aedd3d88"
        self.assertEqual(hashlib.sha256(stock).hexdigest(), expected)
        self.assertEqual(stock, main)
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
                self.assertEqual(report["relocation_count"], 0, profile)

    def test_source_is_reviewable_bsd_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        for token in (".byte", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
