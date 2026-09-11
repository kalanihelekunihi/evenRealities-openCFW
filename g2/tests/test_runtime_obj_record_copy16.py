from __future__ import annotations

import ctypes
import hashlib
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_obj_record_copy16.c"
)
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000
START, END = 0x43EE94, 0x43EEA6


class RuntimeObjRecordCopy16Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory()
        library = Path(cls.temp.name) / (
            "a.dylib" if sys.platform == "darwin" else "a.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(SOURCE),
        ]
        command += (
            ["-dynamiclib", "-o", str(library)]
            if sys.platform == "darwin"
            else ["-shared", "-fPIC", "-o", str(library)]
        )
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.copy = cls.loaded.open_cfw_runtime_obj_copy_record16
        cls.copy.argtypes = [
            ctypes.POINTER(ctypes.c_uint32 * 4),
            ctypes.POINTER(ctypes.c_uint32 * 4),
        ]
        cls.copy.restype = None

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_copies_all_four_words(self) -> None:
        Record = ctypes.c_uint32 * 4
        source = Record(0x11111111, 0x22222222, 0x33333333, 0x44444444)
        destination = Record(0, 0, 0, 0)
        self.copy(ctypes.byref(destination), ctypes.byref(source))
        self.assertEqual(list(destination), list(source))

    def test_does_not_read_past_the_fourth_word(self) -> None:
        # A source with a poisoned fifth word must not leak into an
        # oversized destination buffer.
        class Guarded(ctypes.Structure):
            _fields_ = [
                ("record", ctypes.c_uint32 * 4),
                ("guard", ctypes.c_uint32),
            ]

        source = Guarded(
            record=(0xAAAAAAAA, 0xBBBBBBBB, 0xCCCCCCCC, 0xDDDDDDDD),
            guard=0xDEADBEEF,
        )
        destination = Guarded(
            record=(0, 0, 0, 0),
            guard=0x5A5A5A5A,
        )
        self.copy(
            ctypes.byref(destination.record), ctypes.byref(source.record)
        )
        self.assertEqual(list(destination.record), list(source.record))
        self.assertEqual(destination.guard, 0x5A5A5A5A)

    def test_stock_body_hash_is_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        body = application[START - BASE:END - BASE]
        self.assertEqual(len(body), 18)
        self.assertEqual(
            hashlib.sha256(body).hexdigest(),
            "f73e45d66d1de715a1cb3942d89782eb1b96f870340fc063782c50e"
            "e367fc9a6",
        )


if __name__ == "__main__":
    unittest.main()
