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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_transition_428378.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x00428378
SIZE = 106
FUNCTION = "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378"
DELAY = "open_cfw_bootloader_delay_us_41d1c0"
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
    "apple-clang": Path("/usr/bin/clang"),
    "linux-clang": Path("/opt/homebrew/opt/llvm@22/bin/clang"),
}


class State(ctypes.Structure):
    _fields_ = [
        ("vrefgen2", ctypes.c_uint32),
        ("ldoreg1", ctypes.c_uint32),
        ("pwrsw0", ctypes.c_uint32),
        ("vrefgen4", ctypes.c_uint32),
        ("new_vddc_trim", ctypes.c_uint32),
        ("new_coreldo_tempco_trim", ctypes.c_uint32),
        ("new_coreldo_active_trim", ctypes.c_uint32),
        ("new_vddf_trim", ctypes.c_uint32),
        ("ongoing_sequence", ctypes.c_uint8),
        ("delay_calls", ctypes.c_uint32),
        ("last_delay_us", ctypes.c_uint32),
    ]


class BootloaderSpotmgrTransition428378Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_transition.so"
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

    def test_source_is_reviewable_c_with_mnemonic_target_body(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("transition_sequence_2b", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn("__asm__(\"", body)

    def test_portable_semantics_against_random_register_states(self):
        rng = random.Random(0x428378)
        for _ in range(50_000):
            values = [rng.getrandbits(32) for _ in range(11)]
            state = State(*values[:8], values[8] & 0xFF, values[9], values[10])
            before = {name: getattr(state, name) for name, _type in State._fields_}
            self.function(ctypes.byref(state))
            self.assertEqual(
                state.vrefgen2,
                (before["vrefgen2"] & ~0x7F) |
                (before["new_vddc_trim"] & 0x7F),
            )
            expected_ldo = (before["ldoreg1"] & ~(0xF << 10)) | (
                (before["new_coreldo_tempco_trim"] & 0xF) << 10)
            expected_ldo = (expected_ldo & ~0x3FF) | (
                before["new_coreldo_active_trim"] & 0x3FF)
            self.assertEqual(state.ldoreg1, expected_ldo)
            self.assertEqual(
                state.pwrsw0,
                before["pwrsw0"] & ~(1 << 16) & ~(1 << 25),
            )
            self.assertEqual(
                state.vrefgen4,
                (before["vrefgen4"] & ~0x7F) |
                (before["new_vddf_trim"] & 0x7F),
            )
            self.assertEqual(state.ongoing_sequence, 26)
            self.assertEqual(state.delay_calls, (before["delay_calls"] + 1) & 0xFFFFFFFF)
            self.assertEqual(state.last_delay_us, 5)

    def test_dual_toolchain_body_is_exact_after_delay_relocation(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "051e40c208a75b89a9826c46a5fcea7b9933f1de7c90f4acc01777ba1ed16866",
        )
        relocation = [{
            "offset": 54,
            "type": "R_ARM_THM_CALL",
            "symbol": DELAY,
            "symbol_type": "STT_NOTYPE",
            "target_address": 0x0041D1C0,
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
