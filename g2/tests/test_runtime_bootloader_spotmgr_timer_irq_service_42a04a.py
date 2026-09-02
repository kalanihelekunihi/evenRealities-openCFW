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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_spotmgr_timer_irq_service_42a04a.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BOOT_BASE = 0x00410000
ADDRESS = 0x0042A04A
SIZE = 46
FUNCTION = "open_cfw_bootloader_spotmgr_timer_irq_service_42a04a"
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
RELOCATIONS = (
    (0x02, "open_cfw_bootloader_critical_save_41b8ec", 0x0041B8EC),
    (0x12, "open_cfw_bootloader_spotmgr_transition_sequence_2b_428378", 0x00428378),
    (0x1E, "open_cfw_bootloader_spotmgr_transition_sequence_7b_428a94", 0x00428A94),
    (0x22, "open_cfw_bootloader_spotmgr_timer_finish_41ccd6", 0x0041CCD6),
)


class State(ctypes.Structure):
    _fields_ = [
        ("ongoing_sequence", ctypes.c_uint8),
        ("saved_primask", ctypes.c_uint32),
        ("current_primask", ctypes.c_uint32),
        ("critical_save_calls", ctypes.c_uint32),
        ("transition_2b_calls", ctypes.c_uint32),
        ("transition_7b_calls", ctypes.c_uint32),
        ("timer_finish_calls", ctypes.c_uint32),
    ]


class BootloaderSpotmgrTimerIrqService42a04aTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / "spotmgr_timer_irq.so"
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

    def test_source_is_reviewable_and_restores_the_exact_interrupt_token(self):
        body = SOURCE.read_text(encoding="utf-8")
        self.assertIn("SPDX-License-Identifier: BSD-3-Clause", body)
        self.assertIn(FUNCTION, body)
        self.assertIn("state->current_primask = token", body)
        self.assertNotIn(".byte", body)
        self.assertNotIn(".word", body)
        self.assertNotIn(".inst", body)

    def test_portable_sequence_dispatch_over_random_states(self):
        rng = random.Random(0x42A04A)
        for _ in range(100_000):
            values = [rng.getrandbits(32) for _ in range(7)]
            state = State(values[0] & 0xFF, *values[1:])
            before = {name: getattr(state, name) for name, _type in State._fields_}
            self.function(ctypes.byref(state))
            self.assertEqual(state.saved_primask, before["current_primask"])
            self.assertEqual(state.current_primask, before["current_primask"])
            self.assertEqual(
                state.critical_save_calls,
                (before["critical_save_calls"] + 1) & 0xFFFFFFFF,
            )
            self.assertEqual(
                state.transition_2b_calls,
                (before["transition_2b_calls"] +
                 (1 if before["ongoing_sequence"] == 2 else 0)) & 0xFFFFFFFF,
            )
            self.assertEqual(
                state.transition_7b_calls,
                (before["transition_7b_calls"] +
                 (1 if before["ongoing_sequence"] == 7 else 0)) & 0xFFFFFFFF,
            )
            self.assertEqual(
                state.timer_finish_calls,
                (before["timer_finish_calls"] + 1) & 0xFFFFFFFF,
            )

    def test_dual_toolchain_body_is_exact_after_four_relocations(self):
        stock = BOOT.read_bytes()[ADDRESS - BOOT_BASE:ADDRESS - BOOT_BASE + SIZE]
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "2ce0019a9c986275a9d5c9ea8d04c05e055c163e2802417c4ee68be2fd2b7fd4",
        )
        relocations = [{
            "offset": offset,
            "type": "R_ARM_THM_CALL",
            "symbol": symbol,
            "symbol_type": "STT_NOTYPE",
            "target_address": target,
        } for offset, symbol, target in RELOCATIONS]
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
                self.assertEqual(report["relocation_count"], 4)


if __name__ == "__main__":
    unittest.main()
