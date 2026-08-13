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
SOURCE = COMPONENT_ROOT / "runtime_ascii_fold.c"
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00481830
STOCK_END = 0x00481836
NEXT_FUNCTION_END = 0x004824EE
CALLER_START = 0x00482518
CALLER_END = 0x0048262C


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeAsciiFoldTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_ascii_fold.dylib"
            if sys.platform == "darwin"
            else "runtime_ascii_fold.so"
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
        cls.fold = cls.loaded.open_cfw_ascii_fold_lower
        cls.fold.argtypes = [ctypes.c_uint]
        cls.fold.restype = ctypes.c_uint

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_matches_unconditional_32_bit_or_semantics(self) -> None:
        self.assertEqual(ctypes.sizeof(ctypes.c_uint), 4)
        values = list(range(0x100))
        values.extend(
            (
                0x00000100,
                0x12345600,
                0x1234561F,
                0x12345620,
                0x1234565A,
                0x7FFFFFFF,
                0x80000000,
                0xFFFFFFDF,
                0xFFFFFFFF,
            )
        )
        for value in values:
            with self.subTest(value=f"0x{value:08X}"):
                self.assertEqual(
                    self.fold(value),
                    (value | 0x20) & 0xFFFFFFFF,
                )

    def test_stock_span_and_adjacent_boundaries_are_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        alignment = span(0x0048182E, STOCK_START)
        self.assertEqual(alignment, b"\0\0")
        self.assertEqual(
            hashlib.sha256(alignment).hexdigest(),
            "96a296d224f285c67bee93c30f8a3091"
            "57f0daa35dc5b87e410b78630a09cfc7",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(stock.hex(), "40f020007047")
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "ba0e75482a025061a99348c4060bc9de"
            "61f721b82599d840f94f2ac532612778",
        )

        following = span(STOCK_END, NEXT_FUNCTION_END)
        self.assertEqual(len(following), 3256)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "0ace800002b34fa464fd3a816691e77df"
            "43a7919b2747ef608d0b89213786fb0",
        )

        retained_suffix = span(STOCK_END, 0x00490616)
        self.assertEqual(len(retained_suffix), 60896)
        self.assertEqual(
            hashlib.sha256(retained_suffix).hexdigest(),
            "ec45974e2c0244b46cf22a14dcdfa0bf"
            "735046aeed67d625dd2a7fbba3f56bae",
        )

    def test_sole_executable_caller_context_is_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        caller = application[
            CALLER_START - APPLICATION_BASE:
            CALLER_END - APPLICATION_BASE
        ]
        self.assertEqual(len(caller), 276)
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "be063cc5e8c7478419a02b8f09e24e93"
            "209ee2ec042cdcf325729564f91d4897",
        )
        prefix = application[
            0x00482520 - APPLICATION_BASE:
            0x00482538 - APPLICATION_BASE
        ]
        self.assertEqual(
            prefix.hex(),
            "3c6950466f2808bf082505d0fff780f9782814bf0a251025",
        )
        self.assertEqual(
            hashlib.sha256(prefix).hexdigest(),
            "20f42ad18acfe6e55d7373f2210eb141"
            "870352e09bbc03072b09a2afa4212a74",
        )

    def test_stock_branch_and_pointer_topology_is_pinned(self) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
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
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append((address, target))

        self.assertEqual(callers, [(0x0048252C, "fff780f9")])
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
            "unsigned int open_cfw_ascii_fold_lower(unsigned int value)",
            "return value | 0x20U;",
        ):
            self.assertIn(token, source)
        for token in ("if (", "switch (", "while (", "for ("):
            self.assertNotIn(token, source)
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "84c357e2b2ee87cf1b1d220ef397d8913"
            "08f6dc62629c138e16ae225726a0eea",
        )


if __name__ == "__main__":
    unittest.main()
