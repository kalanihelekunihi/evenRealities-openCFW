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
    / "runtime_obj_pointer_predicates.c"
)
OFFICIAL = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
BASE = 0x438000
EQUALS_START, EQUALS_END = 0x43E2BC, 0x43E2D4
CHAIN_START, CHAIN_END = 0x43E2D4, 0x43E2EA


class RuntimeObjPointerPredicatesTests(unittest.TestCase):
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
        cls.equals = cls.loaded.open_cfw_runtime_obj_field_equals_or_null
        cls.equals.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.equals.restype = ctypes.c_int
        cls.contains = cls.loaded.open_cfw_runtime_obj_pointer_chain_contains
        cls.contains.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        cls.contains.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def test_field_equals_or_null_rejects_null(self) -> None:
        self.assertEqual(self.equals(None, 0x1234), 0)

    def test_field_equals_or_null_compares_first_field(self) -> None:
        value = ctypes.c_uint32(0xABCD1234)
        self.assertEqual(
            self.equals(ctypes.byref(value), 0xABCD1234), 1
        )
        self.assertEqual(
            self.equals(ctypes.byref(value), 0xABCD1235), 0
        )

    def test_pointer_chain_contains_walks_past_the_head(self) -> None:
        # chain: head -> a -> b -> NULL. Each node's first field is a
        # pointer-sized "next" slot, matching the stock 32-bit target's
        # plain linked-node layout.
        Node = ctypes.c_void_p
        b = Node(None)
        a = Node(ctypes.addressof(b))
        head = Node(ctypes.addressof(a))

        self.assertEqual(
            self.contains(ctypes.byref(head), ctypes.byref(a)), 1
        )
        self.assertEqual(
            self.contains(ctypes.byref(head), ctypes.byref(b)), 1
        )
        # the head's own address is never matched: the walk starts one
        # link past it.
        self.assertEqual(
            self.contains(ctypes.byref(head), ctypes.byref(head)), 0
        )

    def test_pointer_chain_contains_returns_false_past_null(self) -> None:
        Node = ctypes.c_void_p
        head = Node(None)
        missing = ctypes.c_int(0xDEADBEEF)
        self.assertEqual(
            self.contains(ctypes.byref(head), ctypes.byref(missing)), 0
        )

    def test_stock_body_hashes_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[start - BASE:end - BASE]

        equals_body = span(EQUALS_START, EQUALS_END)
        self.assertEqual(len(equals_body), 24)
        self.assertEqual(
            hashlib.sha256(equals_body).hexdigest(),
            "42f9829aa7d7005341974bd567d2be6335082be309679cd4f28186a"
            "68597ef0f",
        )
        chain_body = span(CHAIN_START, CHAIN_END)
        self.assertEqual(len(chain_body), 22)
        self.assertEqual(
            hashlib.sha256(chain_body).hexdigest(),
            "39b5eb1d1cc0f33c96d35797658eb69b105ecbe151944a95c7eb15a"
            "8ce9e573e",
        )


if __name__ == "__main__":
    unittest.main()
