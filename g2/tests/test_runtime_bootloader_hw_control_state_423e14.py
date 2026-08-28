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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_hw_control_state_423e14.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_hw_control_state_host.c"


class Context(ctypes.Structure):
    _fields_ = [("prefix", ctypes.c_uint8 * 0x838), ("state", ctypes.c_uint32)]


class BootloaderHwControlStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory()
        output = Path(cls.tmp.name) / ("hwsm.dylib" if sys.platform == "darwin" else "hwsm.so")
        subprocess.run(
            [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", str(FIXTURE), *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]), "-o", str(output)],
            check=True, capture_output=True,
        )
        cls.map = ctypes.CDLL(str(output)).open_cfw_bootloader_hw_control_state_423e14
        cls.map.argtypes = [ctypes.POINTER(Context), ctypes.c_uint32]
        cls.map.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_body_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13E14:0x13E40]).hexdigest(), "7179c8490a752b21bfb18de838e98aa785e90da2cbde22e10356fc75829045c1")
        self.assertEqual(hashlib.sha256(blob[0x13E40:0x13E8A]).hexdigest(), "8ea56d5bbd1d671d999791ea24b747f4083048a9bfe169360470ebf4d36914d1")

    def test_state_one_advances_and_merges_flags(self) -> None:
        context = Context()
        context.state = 1
        self.assertEqual(self.map(ctypes.byref(context), 0x101), 0x41A1)
        self.assertEqual(context.state, 2)

    def test_state_two_overrides_flags_without_mutation(self) -> None:
        context = Context()
        context.state = 2
        self.assertEqual(self.map(ctypes.byref(context), 0xFFFFFFFF), 0x4000)
        self.assertEqual(context.state, 2)

    def test_other_states_merge_default_mask(self) -> None:
        for state in (0, 3, 0xFFFFFFFF):
            context = Context()
            context.state = state
            self.assertEqual(self.map(ctypes.byref(context), 0x21), 0x40A1)
            self.assertEqual(context.state, state)

    def test_source_cross_compiles(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if Path(compiler).exists():
                subprocess.run(
                    [compiler, "-target", "arm-none-eabi", "-mcpu=cortex-m55", "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables", "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror", "-fno-ident", "-c", str(SOURCE), "-o", str(Path(self.tmp.name) / (Path(compiler).parent.name + "-hwsm.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
