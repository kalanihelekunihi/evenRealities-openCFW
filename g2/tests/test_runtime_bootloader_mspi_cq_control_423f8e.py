from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin"
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_cq_control_423f8e.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_cq_control_host.c"

CLOCK = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
                         ctypes.c_uint8)
CONTROL = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_size_t)


class Context(ctypes.Structure):
    _fields_ = (("reserved", ctypes.c_uint32), ("module", ctypes.c_uint32),
                ("gap", ctypes.c_uint8 * 0x820), ("handle", ctypes.c_size_t))


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("clock_request", CLOCK),
                ("cmdq_enable", CONTROL), ("cmdq_disable", CONTROL))


class BootloaderMspiCqControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-cq-control-")
        output = Path(cls.tmp.name) / (
            "cq-control.dylib" if sys.platform == "darwin" else "cq-control.so"
        )
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
                   "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        command += ["-o", str(output)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        loaded = ctypes.CDLL(str(output))
        cls.enable = loaded.open_cfw_bootloader_mspi_cq_enable_423f8e
        cls.disable = loaded.open_cfw_bootloader_mspi_cq_disable_423fac
        for function in (cls.enable, cls.disable):
            function.argtypes = [ctypes.POINTER(Context), ctypes.POINTER(Ports)]
            function.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def ports(clock_status: int, enable_status: int, disable_status: int,
              calls: list[tuple]) -> Ports:
        @CLOCK
        def clock(_context, source, user):
            calls.append(("clock", source, user))
            return clock_status

        @CONTROL
        def enable(_context, handle):
            calls.append(("enable", handle))
            return enable_status

        @CONTROL
        def disable(_context, handle):
            calls.append(("disable", handle))
            return disable_status

        value = Ports(None, clock, enable, disable)
        value._callbacks = (clock, enable, disable)
        return value

    def test_authenticated_bodies_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13F8E:0x13FAC]).hexdigest(),
                         "b846c512f60e83e86f69d04322eb6ce0d5936f143ad86475967c6be67545ab65")
        self.assertEqual(hashlib.sha256(blob[0x13FAC:0x13FB8]).hexdigest(),
                         "8c21c4878a3125546a7201b39610d661f69d8da7e1cae81d3eb223fdf919fb0a")
        self.assertEqual(hashlib.sha256(blob[0x13FB8:0x1403E]).hexdigest(),
                         "ff20411c8e4283f16d82cb8373e95004d648e4c03d151ba89bf43ff7d58a2794")

    def test_enable_requests_clock_then_enables_handle(self) -> None:
        calls: list[tuple] = []
        ports = self.ports(0, 9, 0, calls)
        context = Context(); context.module = 3; context.handle = 0x1234
        self.assertEqual(self.enable(ctypes.byref(context), ctypes.byref(ports)), 9)
        self.assertEqual(calls, [("clock", 4, 0x13), ("enable", 0x1234)])

    def test_clock_failure_short_circuits_enable(self) -> None:
        calls: list[tuple] = []
        ports = self.ports(7, 0, 0, calls)
        context = Context(); context.module = 1; context.handle = 0x55
        self.assertEqual(self.enable(ctypes.byref(context), ctypes.byref(ports)), 7)
        self.assertEqual(calls, [("clock", 4, 0x11)])

    def test_disable_delegates_handle_without_clock_request(self) -> None:
        calls: list[tuple] = []
        ports = self.ports(0, 0, 6, calls)
        context = Context(); context.module = 2; context.handle = 0xA5
        self.assertEqual(self.disable(ctypes.byref(context), ctypes.byref(ports)), 6)
        self.assertEqual(calls, [("disable", 0xA5)])

    def test_clock_user_conversion_is_uint8(self) -> None:
        calls: list[tuple] = []
        ports = self.ports(5, 0, 0, calls)
        context = Context(); context.module = 0xFFFFFFFA
        self.assertEqual(self.enable(ctypes.byref(context), ctypes.byref(ports)), 5)
        self.assertEqual(calls, [("clock", 4, 0x0A)])

    def test_source_cross_compiles_under_both_reviewed_profiles(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if compiler.is_file():
                subprocess.run(
                    [str(compiler), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                     "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                     "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                     "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                     "-fno-ident", "-c", str(SOURCE), "-o",
                     str(Path(self.tmp.name) / (compiler.parent.name + "-control.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
