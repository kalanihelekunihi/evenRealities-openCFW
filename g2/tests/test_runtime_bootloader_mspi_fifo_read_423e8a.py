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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_mspi_fifo_read_423e8a.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_mspi_fifo_read_host.c"

READ = ctypes.CFUNCTYPE(ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32)
STATUS = ctypes.CFUNCTYPE(
    ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint8,
)


class Ports(ctypes.Structure):
    _fields_ = (("context", ctypes.c_void_p), ("read_word", READ),
                ("status_check", STATUS))


class BootloaderMspiFifoReadTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp = tempfile.TemporaryDirectory(prefix="open-cfw-mspi-fifo-read-")
        output = Path(cls.tmp.name) / (
            "mspi-read.dylib" if sys.platform == "darwin" else "mspi-read.so"
        )
        command = [
            os.environ.get("CC", "/usr/bin/clang"), "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror", str(FIXTURE),
        ]
        command += ["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]
        command += ["-o", str(output)]
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.read = ctypes.CDLL(str(output)).open_cfw_bootloader_mspi_fifo_read_423e8a
        cls.read.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint8), ctypes.c_uint32,
            ctypes.c_uint32, ctypes.POINTER(Ports),
        ]
        cls.read.restype = ctypes.c_uint32

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmp.cleanup()

    @staticmethod
    def ports(words: list[int], statuses: list[int], calls: list[tuple]) -> Ports:
        @READ
        def read_word(_context, address):
            calls.append(("read", address))
            return words.pop(0)

        @STATUS
        def status(_context, timeout, address, mask, value, is_equal):
            calls.append(("status", timeout, address, mask, value, is_equal))
            return statuses.pop(0)

        value = Ports(None, read_word, status)
        value._callbacks = (read_word, status)
        return value

    def test_authenticated_body_and_successor(self) -> None:
        blob = OFFICIAL.read_bytes()
        self.assertEqual(
            hashlib.sha256(blob[0x13E8A:0x13F28]).hexdigest(),
            "9bb93dd67b7844ce1e9d75d6a165667cc38f27b45ad937ea7815c357d8ce4a7b",
        )
        self.assertEqual(
            hashlib.sha256(blob[0x13F28:0x13F44]).hexdigest(),
            "08d063cb0dff6fed321206c0f5865143a12d828a4af0686098a27d02d2ad05d2",
        )

    def test_invalid_module_and_zero_length_have_no_side_effects(self) -> None:
        for module, count, expected in ((4, 4, 5), (0, 0, 0)):
            calls: list[tuple] = []
            ports = self.ports([], [], calls)
            output = (ctypes.c_uint8 * 4)(*[0xCC] * 4)
            self.assertEqual(self.read(module, output, count, 9, ctypes.byref(ports)), expected)
            self.assertEqual(calls, [])
            self.assertEqual(bytes(output), b"\xCC" * 4)

    def test_words_and_remainder_are_read_little_endian(self) -> None:
        calls: list[tuple] = []
        ports = self.ports([0x44332211, 0x88776655], [0, 0], calls)
        output = (ctypes.c_uint8 * 8)(*[0xCC] * 8)
        self.assertEqual(self.read(3, output, 6, 77, ctypes.byref(ports)), 0)
        self.assertEqual(bytes(output), b"\x11\x22\x33\x44\x55\x66\xCC\xCC")
        self.assertEqual(calls, [
            ("status", 77, 0x4006301C, 0x3F, 0, 0),
            ("read", 0x40063014),
            ("status", 77, 0x4006301C, 0x3F, 0, 0),
            ("read", 0x40063014),
        ])

    def test_word_poll_failure_returns_before_fifo_access(self) -> None:
        calls: list[tuple] = []
        ports = self.ports([], [9], calls)
        output = (ctypes.c_uint8 * 4)(*[0xCC] * 4)
        self.assertEqual(self.read(1, output, 4, 8, ctypes.byref(ports)), 9)
        self.assertEqual(calls, [("status", 8, 0x4006101C, 0x3F, 0, 0)])
        self.assertEqual(bytes(output), b"\xCC" * 4)

    def test_remainder_poll_failure_preserves_tail(self) -> None:
        calls: list[tuple] = []
        ports = self.ports([0x04030201], [0, 7], calls)
        output = (ctypes.c_uint8 * 8)(*[0xCC] * 8)
        self.assertEqual(self.read(2, output, 5, 6, ctypes.byref(ports)), 7)
        self.assertEqual(bytes(output), b"\x01\x02\x03\x04" + b"\xCC" * 4)

    def test_source_cross_compiles_under_both_reviewed_profiles(self) -> None:
        for compiler in (Path("/usr/bin/clang"), Path("/opt/homebrew/opt/llvm@22/bin/clang")):
            if compiler.is_file():
                subprocess.run(
                    [str(compiler), "-target", "arm-none-eabi", "-mcpu=cortex-m55",
                     "-mthumb", "-Oz", "-ffreestanding", "-fno-builtin",
                     "-ffunction-sections", "-fdata-sections", "-fno-unwind-tables",
                     "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                     "-fno-ident", "-c", str(SOURCE), "-o",
                     str(Path(self.tmp.name) / (compiler.parent.name + "-read.o"))],
                    check=True, capture_output=True,
                )


if __name__ == "__main__":
    unittest.main()
