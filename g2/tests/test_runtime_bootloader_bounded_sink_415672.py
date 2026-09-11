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
SOURCE = ROOT / "components/bootloader/core_overlay/runtime_bounded_sink_415672.c"
FIXTURE = ROOT / "tests/fixtures/bootloader_runtime_bounded_sink_415672_host.c"


class Sink(ctypes.Structure):
    _fields_ = [
        ("cursor", ctypes.c_void_p),
        ("remaining", ctypes.c_uint32),
        ("total", ctypes.c_uint32),
    ]


class BootloaderBoundedSinkTests(unittest.TestCase):
    """Host-side behavioral contract for the retained bounded output sink at
    [0x00415672,0x0041568C), admitted as an in-place Cortex-M55 leaf that
    keeps the same 26-byte stock span but is compiled from
    ``runtime_bounded_sink_415672.c``, not retained stock bytes."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        suffix = "sink.dylib" if sys.platform == "darwin" else "sink.so"
        cls.library = Path(cls.temporary.name) / suffix
        subprocess.run(
            [
                os.environ.get("CC", "/usr/bin/clang"),
                "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                str(FIXTURE),
                *(["-dynamiclib"] if sys.platform == "darwin" else ["-shared", "-fPIC"]),
                "-o", str(cls.library),
            ],
            check=True, capture_output=True,
        )
        cls.lib = ctypes.CDLL(str(cls.library))
        cls.putc = cls.lib.open_cfw_bootloader_bounded_sink_putc_415672
        cls.putc.argtypes = [ctypes.POINTER(Sink), ctypes.c_ubyte]
        cls.putc.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_complete_stock_body(self) -> None:
        blob = OFFICIAL.read_bytes()
        body = blob[0x5672:0x5672 + 26]
        self.assertEqual(len(body), 26)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "e4d1a37e747c2fbecff8857afc606938f61b5d3b20f17a9b4ac78eac26550bfc",
        )

    def test_write_advances_cursor_and_decrements_remaining(self) -> None:
        buf = (ctypes.c_ubyte * 8)()
        sink = Sink(cursor=ctypes.cast(buf, ctypes.c_void_p), remaining=8, total=0)
        for index, char in enumerate(b"opencfw!"):
            self.putc(ctypes.byref(sink), char)
            self.assertEqual(sink.total, index + 1)
            self.assertEqual(sink.remaining, 8 - (index + 1))
        self.assertEqual(bytes(buf), b"opencfw!")
        self.assertEqual(sink.cursor, ctypes.cast(buf, ctypes.c_void_p).value + 8)

    def test_overflow_still_counts_but_stops_writing(self) -> None:
        buf = (ctypes.c_ubyte * 2)()
        sink = Sink(cursor=ctypes.cast(buf, ctypes.c_void_p), remaining=2, total=0)
        for char in b"toolong":
            self.putc(ctypes.byref(sink), char)
        # Every offered character is counted even once the buffer is full.
        self.assertEqual(sink.total, 7)
        # Only the first two bytes were actually written; remaining pins at 0.
        self.assertEqual(sink.remaining, 0)
        self.assertEqual(bytes(buf), b"to")

    def test_zero_remaining_never_dereferences_cursor(self) -> None:
        # A null cursor with zero remaining must not be touched: the sink
        # short-circuits on remaining == 0 before ever reading *cursor.
        sink = Sink(cursor=None, remaining=0, total=5)
        self.putc(ctypes.byref(sink), ord("x"))
        self.assertEqual(sink.total, 6)
        self.assertEqual(sink.remaining, 0)
        self.assertIsNone(sink.cursor)

    def test_source_cross_compiles_for_cortex_m55(self) -> None:
        for compiler in ("/usr/bin/clang", "/opt/homebrew/opt/llvm@22/bin/clang"):
            if not Path(compiler).is_file():
                continue
            output = Path(self.temporary.name) / (Path(compiler).parent.name + "-sink.o")
            subprocess.run(
                [
                    compiler, "--target=arm-none-eabi", "-mcpu=cortex-m55", "-mthumb",
                    "-Oz", "-ffreestanding", "-fno-builtin", "-ffunction-sections",
                    "-fdata-sections", "-fno-unwind-tables",
                    "-fno-asynchronous-unwind-tables", "-Wall", "-Wextra", "-Werror",
                    "-c", str(SOURCE), "-o", str(output),
                ],
                check=True, capture_output=True,
            )
            self.assertTrue(output.is_file())


if __name__ == "__main__":
    unittest.main()
