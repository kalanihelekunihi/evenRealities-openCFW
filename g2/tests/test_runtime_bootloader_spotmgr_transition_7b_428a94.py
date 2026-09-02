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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_transition_7b_428a94.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x00428A94
SIZE = 276
FUNCTION = "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94"
DELAY = "open_cfw_bootloader_delay_us_41d1c0"
STATUS_DELAY = "open_cfw_bootloader_delay_us_status_change_41d21c"
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
        ("vrefgen2", ctypes.c_uint32),
        ("ldoreg1", ctypes.c_uint32),
        ("vrefgen4", ctypes.c_uint32),
        ("mcuperfreq", ctypes.c_uint32),
        ("pwrsw0", ctypes.c_uint32),
        ("clkgen_misc", ctypes.c_uint32),
        ("clkgen_clockenstat", ctypes.c_uint32),
        ("new_vddc_trim", ctypes.c_uint32),
        ("new_coreldo_tempco_trim", ctypes.c_uint32),
        ("new_coreldo_active_trim", ctypes.c_uint32),
        ("new_vddf_trim", ctypes.c_uint32),
        ("ongoing_sequence", ctypes.c_uint8),
        ("delay_calls", ctypes.c_uint32),
        ("one_us_delay_calls", ctypes.c_uint32),
        ("last_delay_us", ctypes.c_uint32),
        ("status_change_calls", ctypes.c_uint32),
        ("last_status_delay", ctypes.c_uint32),
        ("last_status_mask", ctypes.c_uint32),
        ("last_status_expected", ctypes.c_uint32),
    ]


class BootloaderSpotmgrTransition7b428a94Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_transition_7b.so"
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
        self.assertIn("transition_sequence_7b", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)
        self.assertIn("index < 20U", body)

    def test_portable_semantics_against_random_register_states(self):
        rng = random.Random(0x428A94)
        names = [name for name, _type in State._fields_]
        for _ in range(50_000):
            values = [rng.getrandbits(32) for _ in names]
            values[names.index("ongoing_sequence")] &= 0xFF
            state = State(*values)
            before = {name: getattr(state, name) for name in names}
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
                state.vrefgen4,
                (before["vrefgen4"] & ~0x7F) |
                (before["new_vddf_trim"] & 0x7F),
            )

            was_hp = (before["mcuperfreq"] & 3) == 2
            ack = (before["mcuperfreq"] >> 2) & 1
            clock_ready = (before["clkgen_clockenstat"] >> 24) & 1
            forced = was_hp and ((before["clkgen_misc"] >> 5) & 1) == 0
            one_us_calls = 0
            expected_perf = before["mcuperfreq"]
            if was_hp:
                expected_perf = (expected_perf & ~3) | 1
                if not ack:
                    one_us_calls += 20
                if forced:
                    one_us_calls += 1
                if clock_ready:
                    expected_perf = (expected_perf & ~3) | 2
                    if not ack:
                        one_us_calls += 20
            self.assertEqual(state.mcuperfreq, expected_perf)
            self.assertEqual(
                state.pwrsw0,
                (before["pwrsw0"] | (1 << 6) | (1 << 3)) & ~(1 << 25),
            )
            self.assertEqual(state.clkgen_misc, before["clkgen_misc"])
            self.assertEqual(
                state.one_us_delay_calls,
                (before["one_us_delay_calls"] + one_us_calls) & 0xFFFFFFFF,
            )
            self.assertEqual(
                state.delay_calls,
                (before["delay_calls"] + 1 + one_us_calls) & 0xFFFFFFFF,
            )
            self.assertEqual(state.last_delay_us, 1 if one_us_calls else 5)
            self.assertEqual(
                state.status_change_calls,
                (before["status_change_calls"] + (1 if forced else 0)) &
                0xFFFFFFFF,
            )
            if forced:
                self.assertEqual(state.last_status_delay, 15)
                self.assertEqual(state.last_status_mask, 1 << 24)
                self.assertEqual(state.last_status_expected, 1 << 24)
            else:
                self.assertEqual(state.last_status_delay, before["last_status_delay"])
                self.assertEqual(state.last_status_mask, before["last_status_mask"])
                self.assertEqual(
                    state.last_status_expected, before["last_status_expected"])
            self.assertEqual(state.ongoing_sequence, 26)

    def test_dual_toolchain_body_is_exact_after_provider_relocations(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "1e0e7ddb0036670d692a97a50f6cc821d2a2358e741b72d502e943d31bb0b351",
        )
        relocations = []
        for offset, symbol, target in (
            (0x2E, DELAY, 0x0041D1C0),
            (0x64, DELAY, 0x0041D1C0),
            (0xB4, DELAY, 0x0041D1C0),
            (0xC6, STATUS_DELAY, 0x0041D21C),
            (0xEA, DELAY, 0x0041D1C0),
        ):
            relocations.append({
                "offset": offset,
                "type": "R_ARM_THM_CALL",
                "symbol": symbol,
                "symbol_type": "STT_NOTYPE",
                "target_address": target,
            })
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
                    relocation_configs=relocations,
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(report["relocation_count"], 5)


if __name__ == "__main__":
    unittest.main()
