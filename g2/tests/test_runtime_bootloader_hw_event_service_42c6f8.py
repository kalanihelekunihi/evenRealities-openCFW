import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_event_service_42c6f8.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42C6F8
Z = 0x42C980
FN = "open_cfw_bootloader_hw_event_service_42c6f8"
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
    (0x09E, "open_cfw_bootloader_hw_error_classify_42c076", 0x42C076),
    (0x0D8, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x42C0B2),
    (0x0F4, "open_cfw_bootloader_hw_descriptor_publish_42c45a", 0x42C45A),
    (0x13E, "open_cfw_bootloader_cmdq_get_status_427a56", 0x427A56),
    (0x1D6, "open_cfw_bootloader_hw_error_classify_42c076", 0x42C076),
    (0x232, "open_cfw_bootloader_hw_event_apply_42c0b2", 0x42C0B2),
    (0x23A, "open_cfw_bootloader_cmdq_error_resume_427b38", 0x427B38),
    (0x246, "open_cfw_bootloader_cmdq_adapter_enable_42c420", 0x42C420),
    (0x252, "open_cfw_bootloader_cmdq_adapter_disable_42c44e", 0x42C44E),
)
RELOCATIONS = [
    {"offset": offset, "type": "R_ARM_THM_CALL", "symbol": symbol,
     "symbol_type": "STT_NOTYPE", "target_address": target}
    for offset, symbol, target in SPECS
]


class Model(ctypes.Structure):
    _fields_ = [
        ("header", ctypes.c_uint32), ("event_bits", ctypes.c_uint32),
        ("producer", ctypes.c_uint32), ("pending", ctypes.c_uint32),
        ("ring_size", ctypes.c_uint32),
        ("callback_present", ctypes.c_uint32),
        ("callback_count", ctypes.c_uint32),
        ("descriptor_publish_count", ctypes.c_uint32),
        ("applied_event_bits", ctypes.c_uint32),
        ("register_200", ctypes.c_uint32),
        ("register_208", ctypes.c_uint32),
        ("register_218", ctypes.c_uint32),
        ("register_224", ctypes.c_uint32),
        ("register_238", ctypes.c_uint32),
        ("active_service", ctypes.c_uint8),
    ]


class HardwareEventServiceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "event.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.service = dll.open_cfw_bootloader_hw_event_service_42c6f8_portable
        cls.service.argtypes = [ctypes.POINTER(Model), ctypes.c_uint32,
                                ctypes.c_uint32, ctypes.c_uint32]
        cls.service.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def model(active=1, pending=2):
        state = Model()
        state.header = 0x01123456
        state.active_service = active
        state.pending = pending
        state.ring_size = 4
        state.register_200 = 0xFFFFFFFF
        state.register_208 = 7
        state.register_218 = 0xFFFFFFFF
        state.register_224 = 9
        return state

    def test_validation(self):
        self.assertEqual(self.service(None, 0, 0, 0), 2)
        state = self.model(); state.header ^= 1
        self.assertEqual(self.service(ctypes.byref(state), 0, 0, 0), 2)

    def test_active_path_accumulates_without_gate(self):
        state = self.model()
        self.assertEqual(self.service(ctypes.byref(state), 0x20, 0, 0), 0)
        self.assertEqual(state.event_bits, 0x20)
        self.assertEqual((state.producer, state.pending), (0, 2))

    def test_active_path_retires_callback_and_publishes_next(self):
        state = self.model(); state.callback_present = 1
        self.assertEqual(self.service(ctypes.byref(state), 0x801, 1, 0), 0)
        self.assertEqual((state.producer, state.pending), (1, 1))
        self.assertEqual((state.callback_count, state.callback_present), (1, 0))
        self.assertEqual(state.descriptor_publish_count, 1)
        self.assertEqual(state.event_bits, 0)

    def test_active_path_terminal_cleanup(self):
        state = self.model(pending=1)
        self.assertEqual(self.service(ctypes.byref(state), 0x801, 1, 0), 0)
        self.assertEqual(state.active_service, 0)
        self.assertEqual(state.register_200, 0xFFFFFBFE)
        self.assertEqual(state.register_238, 0x00800000)

    def test_event_apply_and_inactive_cmdq_status(self):
        state = self.model(); state.event_bits = 0x4000
        self.assertEqual(self.service(ctypes.byref(state), 0x801, 1, 0), 0)
        self.assertEqual(state.applied_event_bits, 0x4800)
        self.assertEqual(state.register_218 & 1, 0)
        inactive = self.model(active=0)
        self.assertEqual(self.service(ctypes.byref(inactive), 0, 0, 6), 6)

    def test_dual_toolchain_exact(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         "7272867858e1c23f8ad5e5938ef7f5e02d59289de7c3c76eb6c7ea69fcec5958")
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
                self.assertEqual(report["relocation_count"], 9)

    def test_reviewable_source(self):
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
