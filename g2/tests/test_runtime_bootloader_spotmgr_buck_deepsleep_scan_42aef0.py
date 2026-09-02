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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_buck_deepsleep_scan_42aef0.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
MAIN = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BOOT_BASE = 0x00410000
MAIN_BASE = 0x00437FE0
ADDRESS = 0x0042AEF0
SIZE = 288
FUNCTION = "open_cfw_bootloader_spotmgr_buck_deepsleep_scan_42aef0"
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
RELOCATIONS = ({
    "offset": 0x30,
    "type": "R_ARM_THM_CALL",
    "symbol": "open_cfw_bootloader_stimer_is_running_41f3f0",
    "symbol_type": "STT_NOTYPE",
    "target_address": 0x0041F3F0,
},)


class State(ctypes.Structure):
    _fields_ = [
        ("dev_power_status", ctypes.c_uint32),
        ("audss_power_status", ctypes.c_uint32),
        ("reserved_08", ctypes.c_uint8 * 8),
        ("temperature_range", ctypes.c_uint8),
        ("syspll_enabled", ctypes.c_uint8),
        ("stimer_running", ctypes.c_uint8),
        ("stimer_clock", ctypes.c_uint8),
        ("timer_ctrl", ctypes.c_uint32 * 16),
        ("timer_global_enable", ctypes.c_uint32),
        ("deep_sleep_blocked", ctypes.c_uint8),
    ]


def expected_blocked(state: State) -> int:
    if (
        state.temperature_range == 3
        or (state.dev_power_status & 0x3FFFFFFF) != 0
        or (state.audss_power_status & 0x4C4) != 0
        or state.syspll_enabled != 0
    ):
        return 1
    if state.stimer_running != 0 and 1 <= state.stimer_clock < 3:
        return 1
    for index, control in enumerate(state.timer_ctrl):
        clock = (control >> 8) & 0x1FF
        if (
            control & 1
            and state.timer_global_enable & (1 << index)
            and (clock < 6 or 19 <= clock < 25 or 0x100 <= clock < 0x1E0)
        ):
            return 1
    return 0


class BootloaderSpotmgrBuckDeepsleepScan42aef0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_scan.so"
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

    def test_portable_scan_covers_all_predicate_families(self):
        rng = random.Random(0x42AEF0)
        for _ in range(100_000):
            state = State()
            state.dev_power_status = rng.getrandbits(32)
            state.audss_power_status = rng.getrandbits(32)
            state.temperature_range = rng.randrange(8)
            state.syspll_enabled = rng.randrange(2)
            state.stimer_running = rng.randrange(2)
            state.stimer_clock = rng.randrange(16)
            for index in range(16):
                state.timer_ctrl[index] = rng.getrandbits(32)
            state.timer_global_enable = rng.getrandbits(32)
            state.deep_sleep_blocked = rng.randrange(256)
            expected = expected_blocked(state)
            self.function(ctypes.byref(state))
            self.assertEqual(state.deep_sleep_blocked, expected)

    def test_dual_toolchain_body_and_main_analogue_are_exact(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "7a54959ea8247c505df0f3139ce607b4d1fabb5d0015054b89bd44b5d79cc31b",
        )
        main = MAIN.read_bytes()[0x005A0C20 - MAIN_BASE:0x005A0D40 - MAIN_BASE]
        self.assertEqual(sum(left == right for left, right in zip(stock, main)), 284)
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
                    relocation_configs=list(RELOCATIONS),
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(linked, stock, profile)
                self.assertEqual(
                    report["unrelocated_sha256"],
                    "040d93b977d325156b2ac09b6f01d68023fb2faf2bcf18e083a469afbb46e490",
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
