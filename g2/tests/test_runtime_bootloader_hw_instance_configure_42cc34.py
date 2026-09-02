import ctypes
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_instance_configure_42cc34.c"
BOOT = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
BASE = 0x410000
A = 0x42CC34
Z = 0x42CDB0
FN = "open_cfw_bootloader_hw_instance_configure_42cc34"
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
RELOCATIONS = [{
    "offset": 0x07C, "type": "R_ARM_THM_CALL",
    "symbol": "open_cfw_bootloader_hw_clock_encode_42c26a",
    "symbol_type": "STT_NOTYPE", "target_address": 0x42C26A,
}]


class Model(ctypes.Structure):
    _fields_ = [
        ("header", ctypes.c_uint32), ("instance", ctypes.c_uint32),
        ("mode", ctypes.c_uint8), ("control_118", ctypes.c_uint32),
        ("control_280", ctypes.c_uint32), ("control_2c0", ctypes.c_uint32),
        ("rate_divisor", ctypes.c_uint32), ("timeout", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32), ("count", ctypes.c_uint32),
        ("window", ctypes.c_uint32), ("buffer_safe", ctypes.c_uint8),
        ("slots", ctypes.c_uint8 * 4),
    ]


class HardwareInstanceConfigureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        library = Path(cls.tmp.name) / "instance.so"
        compiler = shutil.which("cc") or shutil.which("clang")
        subprocess.run(
            [compiler, "-std=c11", "-O2", "-fPIC", "-shared", str(SOURCE),
             "-o", str(library)], check=True, capture_output=True, text=True,
        )
        dll = ctypes.CDLL(str(library))
        cls.configure = dll.open_cfw_bootloader_hw_instance_configure_42cc34_portable
        cls.configure.argtypes = [ctypes.POINTER(Model)] + [ctypes.c_uint32] * 6
        cls.configure.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    @staticmethod
    def model():
        state = Model(); state.header = 0x01123456
        state.instance = 3; state.slots[:] = (1, 2, 3, 4)
        return state

    def test_validation_and_active_guards(self):
        self.assertEqual(self.configure(None, 0, 1, 0, 0, 0, 0), 2)
        state = self.model(); state.header ^= 1
        self.assertEqual(self.configure(ctypes.byref(state), 0, 1, 0, 0, 0, 0), 2)
        state = self.model(); state.instance = 8
        self.assertEqual(self.configure(ctypes.byref(state), 0, 1, 0, 0, 0, 0), 6)
        state = self.model(); state.header |= 0x02000000
        self.assertEqual(self.configure(ctypes.byref(state), 0, 1, 0, 0, 0, 0), 7)

    def test_dynamic_mode_programs_rate_flags_and_buffer_window(self):
        state = self.model()
        self.assertEqual(self.configure(ctypes.byref(state), 0, 400000, 3,
                                        0x120, 0x20010000, 248), 0)
        self.assertEqual((state.mode, state.control_280, state.control_118),
                         (0, 3, 0x121))
        self.assertEqual((state.rate_divisor, state.timeout), (2, 1000))
        self.assertEqual((state.buffer_safe, state.window), (1, 10))
        self.assertEqual(list(state.slots), [0, 0, 0, 0])

    def test_dynamic_mode_rejects_invalid_flags_and_rate(self):
        for rate, flags in ((0, 0), (48000001, 0), (100000, 4)):
            state = self.model()
            self.assertEqual(self.configure(ctypes.byref(state), 0, rate, flags,
                                            0, 0, 0), 6)

    def test_fixed_mode_maps_supported_rates(self):
        expected = {
            100000: (0x773B2301, 0x0003F070, 10),
            400000: (0x1D0E2301, 0x0003F270, 2),
            1000000: (0x0B052301, 0x00023040, 1),
        }
        for rate, values in expected.items():
            state = self.model()
            self.assertEqual(self.configure(ctypes.byref(state), 1, rate, 0,
                                            0, 0, 0), 0)
            self.assertEqual((state.control_118, state.control_2c0,
                              state.rate_divisor), values)
        state = self.model()
        self.assertEqual(self.configure(ctypes.byref(state), 1, 200000, 0,
                                        0, 0, 0), 6)

    def test_unsupported_mode_and_window_clamp(self):
        state = self.model()
        self.assertEqual(self.configure(ctypes.byref(state), 2, 100000, 0,
                                        0, 0, 0), 5)
        state = self.model()
        self.assertEqual(self.configure(ctypes.byref(state), 1, 100000, 0,
                                        0, 0x1000, 100000), 0)
        self.assertEqual(state.window, 256)

    def test_dual_toolchain_exact(self):
        stock = BOOT.read_bytes()[A - BASE:Z - BASE]
        self.assertEqual(hashlib.sha256(stock).hexdigest(),
                         "d881da0882c4dcc9f1385402b877bcb3d8c379de014c78707c8db99f5b03aa93")
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
                self.assertEqual(report["relocation_count"], 1)

    def test_reviewable_source(self):
        text = SOURCE.read_text()
        self.assertIn("SPDX-License-Identifier: MIT", text)
        for token in (".byte", ".short", ".word", ".inst"):
            self.assertNotIn(token, text)


if __name__ == "__main__":
    unittest.main()
