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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_power_transition_trims_42b06c.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
ADDRESS = 0x0042B06C
SIZE = 552
FUNCTION = "open_cfw_bootloader_spotmgr_power_transition_trims_42b06c"
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
RELOCATIONS = tuple({
    "offset": offset,
    "type": "R_ARM_THM_CALL",
    "symbol": "open_cfw_bootloader_delay_cycles_41d1c0",
    "symbol_type": "STT_NOTYPE",
    "target_address": 0x0041D1C0,
} for offset in (0x76, 0x90))


class State(ctypes.Structure):
    _fields_ = [(name, ctypes.c_uint32) for name in (
        "core_trim", "flash_trim", "transition_control", "profile_54",
        "profile_58", "profile_5c", "profile_60", "state7_core",
        "state7_flash", "simobuck_core", "simobuck_flash", "mode_trim",
        "delay_calls",
    )]


def field(value, shift):
    return (value >> shift) & 0x1F


def insert(value, code, shift):
    return (value & ~(0x1F << shift)) | ((code & 0x1F) << shift)


def expected_codes(power_state, transition, state):
    if power_state == 0:
        core, flash = field(state.profile_5c, 0), field(state.profile_5c, 10)
    elif power_state == 1:
        core, flash = field(state.profile_5c, 5), field(state.profile_5c, 15)
    elif power_state == 2:
        core, flash = field(state.profile_54, 0), field(state.profile_58, 0)
    elif power_state == 3:
        core, flash = field(state.profile_54, 10), field(state.profile_58, 10)
    elif power_state == 4:
        core, flash = field(state.profile_54, 5), field(state.profile_58, 5)
    elif power_state == 6:
        core, flash = field(state.profile_60, 0), field(state.profile_60, 10)
    elif power_state == 7:
        core, flash = field(state.state7_core, 11), field(state.state7_flash, 17)
    else:
        core, flash = field(state.profile_54, 15), field(state.profile_58, 15)
    if transition == 8:
        core = field(state.profile_5c, 20)
    elif transition == 12:
        core = field(state.profile_54, 20)
    elif transition == 14:
        core = min(core + 6, 31)
    elif transition == 15:
        core = min(core + 12, 31)
    return core, flash


class BootloaderSpotmgrPowerTransitionTrims42b06cTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_power_transition.so"
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

    def test_profile_selection_bias_restore_and_transition_routes(self):
        rng = random.Random(0x42B06C)
        for power_state in range(10):
            for transition in range(21):
                for _ in range(50):
                    values = [rng.getrandbits(32) for _ in range(13)]
                    state = State(*values)
                    core_code, flash_code = expected_codes(
                        power_state, transition, state
                    )
                    original_core = state.core_trim
                    original_flash = state.flash_trim
                    original_control = state.transition_control
                    original_core_reg = state.simobuck_core
                    original_flash_reg = state.simobuck_flash
                    original_mode = state.mode_trim
                    original_delays = state.delay_calls
                    self.function(power_state, transition, ctypes.byref(state))
                    self.assertEqual(state.core_trim, original_core)
                    self.assertEqual(state.flash_trim, original_flash)
                    self.assertEqual(state.transition_control,
                                     original_control & ~0x30000000)
                    self.assertEqual(state.simobuck_core,
                                     insert(original_core_reg, core_code, 25))
                    self.assertEqual(state.simobuck_flash,
                                     insert(original_flash_reg, flash_code, 8))
                    mode = 4 if transition in (1, 5, 17) else 6
                    self.assertEqual(state.mode_trim,
                                     insert(original_mode, mode, 25))
                    self.assertEqual(state.delay_calls,
                                     (original_delays + 2) & 0xFFFFFFFF)

    def test_dual_toolchain_body_matches_stock_and_main_analogue(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "44271365df4592f33c91286690e4e75e328a8dd11127aa934bec2c571292c377",
        )
        main = MAIN.read_bytes()[0x005A0D9C - MAIN_BASE:0x005A0FC4 - MAIN_BASE]
        self.assertEqual(sum(a == b for a, b in zip(stock, main)), 540)
        with tempfile.TemporaryDirectory() as temporary:
            for profile, compiler in PROFILES.items():
                output = Path(temporary) / f"{profile}.o"
                subprocess.run(
                    [str(compiler), *FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True, capture_output=True, text=True,
                )
                linked, report = apollo_overlay.extract_in_place_function_section(
                    output, FUNCTION, runtime_address=ADDRESS,
                    relocation_configs=list(RELOCATIONS),
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(
                    report["unrelocated_sha256"],
                    "35646af379886e8764cde56a2bf9bc6fb22e94f53ea178c5c60dd1727d190127",
                    profile,
                )

    def test_source_is_reviewable_bsd_c_without_raw_encodings(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        for token in (".byte", ".word", ".inst"):
            self.assertNotIn(token, body)


if __name__ == "__main__":
    unittest.main()
