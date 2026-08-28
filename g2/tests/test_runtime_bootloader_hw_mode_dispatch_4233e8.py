from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_mode_dispatch_4233e8.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_mode_dispatch_host.c"

class Instance(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x11C)]

class Request(ctypes.Structure):
    _fields_ = [("bytes", ctypes.c_uint8 * 0x38)]

class BootloaderHardwareModeDispatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hwmd.dylib" if sys.platform == "darwin" else "hwmd.so")
        subprocess.run([os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)], check=True, capture_output=True)
        cls.lib = ctypes.CDLL(str(output))
        cls.dispatch = cls.lib.open_cfw_bootloader_hw_mode_dispatch_4233e8
        cls.dispatch.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(Request)]
        cls.dispatch.restype = ctypes.c_uint32
        cls.mode_two = cls.lib.open_cfw_bootloader_hw_mode_two_start_4234d8
        cls.mode_three = cls.lib.open_cfw_bootloader_hw_mode_three_start_4234fa
        for function in (cls.mode_two, cls.mode_three):
            function.argtypes = [ctypes.POINTER(Instance), ctypes.POINTER(Request)]
            function.restype = ctypes.c_uint32
        names = ("mode_zero_result", "mode_one_result", "primary_latch_result", "secondary_latch_result", "mode_zero_count", "mode_one_count", "primary_latch_count", "secondary_latch_count", "primary_progress_count", "secondary_progress_count", "clear_status_count")
        for name in names:
            setattr(cls, name, ctypes.c_uint32.in_dll(cls.lib, "open_cfw_hwmd_host_" + name))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def setUp(self) -> None:
        for name in ("mode_zero_result", "mode_one_result", "primary_latch_result", "secondary_latch_result", "mode_zero_count", "mode_one_count", "primary_latch_count", "secondary_latch_count", "primary_progress_count", "secondary_progress_count", "clear_status_count"):
            getattr(self, name).value = 0
        self.instance = Instance(); self.request = Request()
        for index, byte in enumerate((0x06, 0x9E, 0xEA, 0x01)):
            self.instance.bytes[index] = byte

    def test_authenticated_bodies_literal_pool_and_boundaries(self) -> None:
        blob = OFFICIAL.read_bytes()
        pins = ((0x133E8, 0x13430, "55aca3e5c488f1f76de2b7d38129b7dbae64a1a97c9de9b466aef93788f7721d"), (0x134D8, 0x134FA, "67cc585ebb380f6e1f1c49d0855a82d0fe92f8d1f54bd3ddb466d0ad903a9eb5"), (0x134FA, 0x13524, "5b3f8d6b0e2f9010d42bfc9ef5fe5e9ba65e5791c7d0f2081e042eccfece1412"))
        for start, end, digest in pins:
            self.assertEqual(hashlib.sha256(blob[start:end]).hexdigest(), digest)
        self.assertEqual(int.from_bytes(blob[0x13830:0x13834], "little"), 0x01EA9E06)

    def test_dispatch_validates_type_and_routes_all_modes(self) -> None:
        self.assertEqual(self.dispatch(None, ctypes.byref(self.request)), 2)
        self.instance.bytes[0] = 7; self.assertEqual(self.dispatch(ctypes.byref(self.instance), ctypes.byref(self.request)), 2)
        self.instance.bytes[0] = 6
        self.mode_zero_result.value = 9; self.request.bytes[0x34] = 0; self.assertEqual(self.dispatch(ctypes.byref(self.instance), ctypes.byref(self.request)), 9)
        self.mode_one_result.value = 8; self.request.bytes[0x34] = 1; self.assertEqual(self.dispatch(ctypes.byref(self.instance), ctypes.byref(self.request)), 8)
        self.request.bytes[0x34] = 4; self.assertEqual(self.dispatch(ctypes.byref(self.instance), ctypes.byref(self.request)), 1)
        self.assertEqual((self.mode_zero_count.value, self.mode_one_count.value), (1, 1))

    def test_mode_two_clears_status_latches_and_starts_only_on_success(self) -> None:
        self.request.bytes[8] = 1
        self.assertEqual(self.mode_two(ctypes.byref(self.instance), ctypes.byref(self.request)), 0)
        self.assertEqual((self.clear_status_count.value, self.primary_latch_count.value, self.primary_progress_count.value), (1, 1, 1))
        self.primary_latch_result.value = 5
        self.assertEqual(self.mode_two(ctypes.byref(self.instance), ctypes.byref(self.request)), 5)
        self.assertEqual(self.primary_progress_count.value, 1)

    def test_mode_three_has_independent_latch_and_progress_path(self) -> None:
        self.request.bytes[8] = 1
        self.secondary_latch_result.value = 7
        self.assertEqual(self.mode_three(ctypes.byref(self.instance), ctypes.byref(self.request)), 7)
        self.assertEqual((self.clear_status_count.value, self.secondary_latch_count.value, self.secondary_progress_count.value), (1, 1, 0))
        self.secondary_latch_result.value = 0
        self.assertEqual(self.mode_three(ctypes.byref(self.instance), ctypes.byref(self.request)), 0)
        self.assertEqual(self.secondary_progress_count.value, 1)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run([compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwmd.o"))], check=True, capture_output=True)

if __name__ == "__main__":
    unittest.main()
