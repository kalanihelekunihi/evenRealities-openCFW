from __future__ import annotations

import os

import ctypes
import hashlib
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_strchr.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00481818
STOCK_END = 0x0048182E


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStrchrTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_strchr.dylib"
            if sys.platform == "darwin"
            else "runtime_strchr.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(SOURCE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.search = cls.loaded.open_cfw_strchr
        cls.search.argtypes = [ctypes.c_void_p, ctypes.c_int]
        cls.search.restype = ctypes.c_void_p

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_searches_each_alignment_and_returns_first_match(self) -> None:
        for offset in range(4):
            for payload in (
                b"",
                b"a",
                b"abca",
                bytes(range(1, 32)),
                b"\xff\x80\x7f\x80",
            ):
                with self.subTest(offset=offset, payload=payload):
                    storage = (
                        ctypes.c_ubyte * (offset + len(payload) + 2)
                    )()
                    for index, value in enumerate(payload):
                        storage[offset + index] = value
                    storage[offset + len(payload)] = 0
                    storage[offset + len(payload) + 1] = 0xA5
                    base = ctypes.addressof(storage) + offset

                    for needle in set(payload):
                        expected = payload.index(needle)
                        self.assertEqual(
                            self.search(base, needle),
                            base + expected,
                        )

                    self.assertEqual(
                        self.search(base, 0),
                        base + len(payload),
                    )
                    self.assertEqual(storage[-1], 0xA5)

    def test_absent_search_and_low_byte_argument_semantics(self) -> None:
        payload = b"alpha"
        storage = ctypes.create_string_buffer(payload)
        base = ctypes.addressof(storage)

        self.assertIsNone(self.search(base, ord("z")))
        self.assertEqual(self.search(base, 0x161), base)
        self.assertEqual(self.search(base, -159), base)
        self.assertIsNone(self.search(base, 0x17A))

    def test_stock_span_and_adjacent_boundaries_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(
            stock.hex(),
            "c9b202788a421ab11cbf10f8012ff9e718bf00207047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "bddb972fdfdf0440df6ae70b677dafdf"
            "1ee07436771ddacbed65e2d2fb7b23f7",
        )

        prefix = span(0x0048173A, STOCK_START)
        self.assertEqual(len(prefix), 222)
        self.assertEqual(
            hashlib.sha256(prefix).hexdigest(),
            "b92f5bfd636f7099de2f9a6ec60bc02f"
            "d6c3a718c9e193281a523effdc6f77f2",
        )

        alignment = span(STOCK_END, 0x00481830)
        self.assertEqual(alignment, b"\0\0")
        self.assertEqual(
            hashlib.sha256(alignment).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )

        following = span(0x00481830, 0x00481836)
        self.assertEqual(following.hex(), "40f020007047")
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "ba0e75482a025061a99348c4060bc9de"
            "61f721b82599d840f94f2ac532612778",
        )

    def test_stock_branch_and_pointer_topology_is_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == STOCK_START:
                    observed.append(address)
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target))

        # Ghidra resolves the first six sites as executable callers. The last
        # branch-shaped word is in data and has no containing function.
        self.assertEqual(
            callers,
            [
                0x0044B652,
                0x0048197E,
                0x004CE4AC,
                0x004D1718,
                0x004D175E,
                0x004D2196,
                0x005A506E,
            ],
        )
        self.assertEqual(
            application[
                0x005A506E - APPLICATION_BASE:
                0x005A5072 - APPLICATION_BASE
            ],
            bytes.fromhex("dcf6d3fb"),
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from("<H", application, offset)[0]
            candidates = []
            if halfword & 0xF800 == 0xE000:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0x7FF) << 1, 12)
                )
            condition = (halfword >> 8) & 0xF
            if halfword & 0xF000 == 0xD000 and condition < 0xE:
                candidates.append(
                    address
                    + 4
                    + _sign_extend((halfword & 0xFF) << 1, 9)
                )
            if halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                candidates.append(address + 4 + immediate)
            if STOCK_START in candidates:
                narrow_entry.append(address)
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [])

    def test_source_is_bounded_and_review_pinned(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "char *open_cfw_strchr(const char *text, int character)",
            "const unsigned char needle = (unsigned char)character;",
            "while (*cursor != needle)",
            "if (*cursor == '\\0')",
        ):
            self.assertIn(token, source)
        self.assertNotIn("text == ", source)
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "b4257a957df2c91f485b4735ef52393f"
            "0768f4f7185e45e16038a1029297cba1",
        )


if __name__ == "__main__":
    unittest.main()
