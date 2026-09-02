import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_context_enable_42c538.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42C538
Z = 0x42C63A
FN = "open_cfw_bootloader_hw_context_enable_42c538"
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
RELOCATIONS = [
    {"offset": 0x38, "type": "R_ARM_THM_CALL",
     "symbol": "open_cfw_bootloader_hw_status_route_42c034",
     "symbol_type": "STT_NOTYPE", "target_address": 0x42C034},
    {"offset": 0x98, "type": "R_ARM_THM_CALL",
     "symbol": "open_cfw_bootloader_cmdq_adapter_init_42c3e2",
     "symbol_type": "STT_NOTYPE", "target_address": 0x42C3E2},
    {"offset": 0xC6, "type": "R_ARM_THM_CALL",
     "symbol": "open_cfw_bootloader_retained_status_check_41d246",
     "symbol_type": "STT_NOTYPE", "target_address": 0x41D246},
]


class Model(ctypes.Structure):
    _fields_ = [
        ("header", ctypes.c_uint32), ("instance", ctypes.c_uint32),
        ("mode", ctypes.c_uint8), ("cmdq_present", ctypes.c_uint32),
        ("reset_words", ctypes.c_uint32 * 7),
        ("reset_byte", ctypes.c_uint8), ("ready_byte", ctypes.c_uint8),
        ("register_238", ctypes.c_uint32),
        ("register_210", ctypes.c_uint32),
        ("register_11c", ctypes.c_uint32),
    ]


class HardwareContextEnableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "enable.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.enable = dll.open_cfw_bootloader_hw_context_enable_42c538_portable
        cls.enable.argtypes = [ctypes.POINTER(Model), ctypes.c_uint32,
                               ctypes.c_uint32, ctypes.c_uint32]
        cls.enable.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def model(cmdq=1):
        value = Model()
        value.header = 0x01123456
        value.instance = 2
        value.mode = 1
        value.cmdq_present = cmdq
        value.reset_words[:] = [9] * 7
        value.reset_byte = 9
        value.ready_byte = 0
        value.register_11c = 0xFFFFFFFF
        return value

    def test_validation_and_idempotent_active_path(self):
        self.assertEqual(self.enable(None, 1, 0, 0), 2)
        bad = self.model(); bad.header = 0x01123457
        self.assertEqual(self.enable(ctypes.byref(bad), 1, 0, 0), 2)
        active = self.model(); active.header |= 0x02000000
        self.assertEqual(self.enable(ctypes.byref(active), 0, 7, 8), 0)

    def test_status_route_rejection(self):
        model = self.model()
        self.assertEqual(self.enable(ctypes.byref(model), 0, 0, 0), 9)
        self.assertEqual(list(model.reset_words), [9] * 7)

    def test_cmdq_initialization_failure_is_returned(self):
        model = self.model()
        self.assertEqual(self.enable(ctypes.byref(model), 1, 4, 0), 4)
        self.assertEqual(list(model.reset_words), [0] * 7)
        self.assertEqual((model.reset_byte, model.ready_byte), (0, 1))
        self.assertEqual((model.register_238, model.register_210),
                         (0x00800040, 2))
        self.assertEqual(model.header, 0x01123456)

    def test_wait_success_sets_active_flag(self):
        model = self.model(cmdq=0)
        self.assertEqual(self.enable(ctypes.byref(model), 1, 7, 0), 0)
        self.assertEqual(model.header, 0x03123456)
        self.assertEqual(list(model.reset_words), [9] * 7)

    def test_wait_failure_rolls_back_control_bits(self):
        model = self.model()
        self.assertEqual(self.enable(ctypes.byref(model), 1, 0, 3), 3)
        self.assertEqual(model.header, 0x01123456)
        self.assertEqual(model.register_11c, 0xFFFFFFEE)

    def test_dual_toolchain_exact(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         "0183cf1cab1b0089fb0b49f71137bf868309198abd9319ca1e35f794ba430f2a")
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
                self.assertEqual(report["relocation_count"], 3)

    def test_reviewable_source(self):
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
