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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_cq_term_423f54.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_cq_term_host.c"

TERM = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_size_t, ctypes.c_uint32)


class Context(ctypes.Structure):
    _fields_ = (("reserved", ctypes.c_uint32), ("module", ctypes.c_uint32))


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("cmdq_term", TERM))


class BootloaderMspiCqTermTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-cq-term-")
        output = Path(cls.tmp.name) / (
            "cq-term.dylib" if sys.platform == "darwin" else "cq-term.so"
        )
        command = [os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
                   "-Wall", "-Wextra", "-Werror", str(FIXTURE)]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        command += ["-o", str(output)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.term = ctypes.CDLL(str(output)).open_cfw_bootloader_mspi_cq_term_423f54
        cls.term.argtypes = [ctypes.POINTER(Context), ctypes.POINTER(ctypes.c_size_t),
                             ctypes.POINTER(Ports)]
        cls.term.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    def test_authenticated_body_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(hashlib.sha256(blob[0x13F54:0x13F8E]).hexdigest(),
                         "07a7e8e54305fbecb7f891cd4e843881b73a33186ba1750b147e0647d0041807")
        self.assertEqual(hashlib.sha256(blob[0x13F8E:0x13FB8]).hexdigest(),
                         "36bba0314140bd5189f7b851ed9dee3fb9260e2a3019b9294520cd5eb9802de4")

    def test_null_handle_is_success_without_provider_call(self) -> None:
        calls: list[tuple[int, int]] = []

        @TERM
        def provider(_context, handle, force):
            calls.append((handle, force))

        ports = Ports(None, provider)
        handles = (ctypes.c_size_t * 4)(0, 0, 0, 0)
        context = Context(0, 2)
        self.assertEqual(self.term(ctypes.byref(context), handles, ctypes.byref(ports)), 0)
        self.assertEqual(calls, [])

    def test_nonnull_handle_is_force_terminated_and_cleared(self) -> None:
        calls: list[tuple[int, int]] = []

        @TERM
        def provider(_context, handle, force):
            calls.append((handle, force))

        ports = Ports(None, provider)
        handles = (ctypes.c_size_t * 4)(0x10, 0x20, 0x30, 0x40)
        context = Context(0, 3)
        self.assertEqual(self.term(ctypes.byref(context), handles, ctypes.byref(ports)), 0)
        self.assertEqual(calls, [(0x40, 1)])
        self.assertEqual(list(handles), [0x10, 0x20, 0x30, 0])

    def test_wrapper_preserves_lack_of_module_prevalidation(self) -> None:
        calls: list[tuple[int, int]] = []

        @TERM
        def provider(_context, handle, force):
            calls.append((handle, force))

        ports = Ports(None, provider)
        handles = (ctypes.c_size_t * 5)(0, 0, 0, 0, 0x99)
        context = Context(0, 4)
        self.assertEqual(self.term(ctypes.byref(context), handles, ctypes.byref(ports)), 0)
        self.assertEqual(calls, [(0x99, 1)])
        self.assertEqual(handles[4], 0)

    def test_source_cross_compiles_under_both_reviewed_profiles(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if compiler.is_file():
                subprocess.run(
                    [str(compiler), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                     "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                     "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                     "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                     "-fno-ident", "-c", str(SOURCE), "-o",
                     str(Path(self.tmp.name) / (compiler.parent.name + "-term.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
