import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_config_transaction_42c988.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42C988
Z = 0x42CC34
FN = "open_cfw_bootloader_hw_config_transaction_42c988"
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

FLAGS = (
    "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz",
    "-ffreestanding", "-fno-builtin", "-ffunction-sections",
    "-fdata-sections", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
    "-fno-ident", "-mllvm", "-enable-machine-outliner=never",
)
PROFILES = (
    ROOT / ".tmp-canonical-toolchains/apple-clang-21-review/bin/clang",
    Path("/opt/homebrew/opt/llvm@22/bin/clang"),
)
SPECS = (
    (0x04A, "open_cfw_bootloader_pwrctrl_periph_enable_41bf84", 0x41BF84),
    (0x11C, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x42C420),
    (0x140, "open_cfw_bootloader_retained_status_check_41d246", 0x41D246),
    (0x152, "open_cfw_bootloader_mode_enable_route_4222f0", 0x4222F0),
    (0x258, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x42C44E),
    (0x290, "open_cfw_bootloader_pwrctrl_periph_disable_41c17a", 0x41C17A),
    (0x29C, "open_cfw_bootloader_mode_disable_route_422364", 0x422364),
)
RELOCATIONS = [
    {"offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
     "symbol_type": "STT_NOTYPE", "target_address": target}
    for offset, symbol, target in SPECS
]


class Model(ctypes.Structure):
    _fields_ = [
        ("header", ctypes.c_uint32), ("pending", ctypes.c_uint32),
        ("status_248", ctypes.c_uint32),
        ("registers", ctypes.c_uint32 * 13),
        ("saved", ctypes.c_uint32 * 13),
        ("saved_valid", ctypes.c_uint8),
    ]


class HardwareConfigTransactionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "config.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.transact = dll.open_cfw_bootloader_hw_config_transaction_42c988_portable
        cls.transact.argtypes = [ctypes.POINTER(Model), ctypes.c_uint32,
                                 ctypes.c_uint32, ctypes.c_uint32]
        cls.transact.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def model():
        state = Model(); state.header = 0x01123456
        state.registers[:] = range(13)
        state.saved[:] = range(100, 113)
        return state

    def test_validation_and_mode_bounds(self):
        self.assertEqual(self.transact(None, 0, 0, 0), 2)
        state = self.model(); state.header ^= 1
        self.assertEqual(self.transact(ctypes.byref(state), 0, 0, 0), 2)
        state = self.model()
        self.assertEqual(self.transact(ctypes.byref(state), 3, 0, 0), 6)

    def test_restore_requires_and_consumes_snapshot(self):
        state = self.model()
        self.assertEqual(self.transact(ctypes.byref(state), 0, 1, 0), 7)
        state.saved_valid = 1
        self.assertEqual(self.transact(ctypes.byref(state), 0, 1, 0), 0)
        expected = list(range(100, 113)); expected[3] &= ~1
        self.assertEqual(list(state.registers), expected)
        self.assertEqual(state.saved_valid, 0)

    def test_route_status_is_propagated(self):
        state = self.model()
        self.assertEqual(self.transact(ctypes.byref(state), 0, 0, 5), 5)
        self.assertEqual(self.transact(ctypes.byref(state), 2, 0, 4), 4)

    def test_active_guard(self):
        state = self.model(); state.header |= 0x02000000
        state.status_248 = 0; state.pending = 0
        self.assertEqual(self.transact(ctypes.byref(state), 1, 1, 0), 3)
        state.status_248 = 4; state.pending = 1
        self.assertEqual(self.transact(ctypes.byref(state), 1, 1, 0), 3)

    def test_save_copies_registers_and_clears_controls(self):
        state = self.model(); state.registers[2] = 0xFFFFFFFF
        self.assertEqual(self.transact(ctypes.byref(state), 2, 1, 0), 0)
        expected = list(range(13)); expected[2] = 0xFFFFFFFF
        self.assertEqual(list(state.saved), expected)
        self.assertEqual(state.saved_valid, 1)
        self.assertEqual(state.registers[2], 0xFFFFFFEE)

    def test_dual_toolchain_exact(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         "1a89b00660cf0c54c66e781ac95f19dd764bb671587c36959ad2cd34fec53ae5")
        with tempfile.TemporaryDirectory() as temp:
            for profile, compiler in enumerate(PROFILES):
                obj = Path(temp) / f"{profile}.o"
                subprocess.run([str(compiler), *FLAGS, "-c", str(SOURCE),
                                "-o", str(obj)], check=True,
                               capture_output=True, text=True)
                body, report = apollo_overlay.extract_in_place_function_section(
                    obj, FN, runtime_address=A, relocation_configs=RELOCATIONS,
                    strict_relocation_contract=True,
                    allow_discarded_alloc_sections=True,
                )
                self.assertEqual(body, stock)
                self.assertEqual(report["relocation_count"], 7)

    def test_reviewable_source(self):
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
