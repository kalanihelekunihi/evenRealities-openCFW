from __future__ import annotations

import os

import ctypes
import hashlib
import random
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


OPENCFW_ROOT = Path(__file__).resolve().parent.parent
COMPONENT_ROOT = OPENCFW_ROOT / "components" / "apollo_main" / "core_overlay"
SOURCE = COMPONENT_ROOT / "runtime_style_is_empty.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_style_is_empty_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482A5A
STOCK_END = 0x00482A6A


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStyleIsEmptyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_is_empty.dylib"
            if sys.platform == "darwin"
            else "runtime_style_is_empty.so"
        )
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(library)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.predicate = cls.loaded.open_cfw_runtime_style_is_empty
        cls.predicate.argtypes = [ctypes.c_void_p]
        cls.predicate.restype = ctypes.c_int

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_all_count_bytes_match_the_exact_zero_oracle(self) -> None:
        for count in range(256):
            style = (ctypes.c_ubyte * 17)(
                *(((index * 37) + count) & 0xFF for index in range(17))
            )
            style[8] = count
            before = bytes(style)
            with self.subTest(count=count):
                self.assertEqual(self.predicate(style), int(count == 0))
                self.assertEqual(bytes(style), before)

    def test_surrounding_descriptor_bytes_do_not_affect_the_result(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            style = (ctypes.c_ubyte * 64)(
                *(generator.randrange(256) for _ in range(64))
            )
            empty = bool(index & 1)
            style[8] = 0 if empty else generator.randrange(1, 256)
            before = bytes(style)
            with self.subTest(index=index, empty=empty):
                self.assertEqual(self.predicate(style), int(empty))
                self.assertEqual(bytes(style), before)

    def test_stock_boundary_caller_and_adjacent_functions_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x0048297C, STOCK_START)
        self.assertEqual(len(previous), 222)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "ff9eb32171697c70cbd592801924eb4e"
            "e1b7279a0378f9d0c04c6941e7beff96",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 16)
        self.assertEqual(
            stock.hex(),
            "007a002801d1012000e00020c0b27047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "8953caaab007ed0e44911ad65dcabba5"
            "70a3c5d9e791de3136b088b696deef55",
        )

        following = span(STOCK_END, 0x00482AB2)
        self.assertEqual(len(following), 72)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "07168721fd141e88723ce6fdeba3a706"
            "85a7205513862d3e87cac10457108958",
        )

        caller = span(0x0044CD78, 0x0044CD98)
        self.assertEqual(
            caller.hex(),
            "306835f019fde06850f8380035f069fe"
            "002806d0726822f07f4231682000fef7",
        )
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "f8e467fc16a9377a367ef59d4f590e4"
            "9b109b8544e80d02d17f301c06e386649",
        )

    def test_wide_call_and_dependency_topology_is_complete(self) -> None:
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
                    observed.append((address, encoded.hex()))
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    interior.append((address, target, link))
                if link and STOCK_START <= address < STOCK_END:
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(callers, [(0x0044CD84, "35f069fe")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

    def test_narrow_control_flow_and_stored_pointer_topology_is_complete(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        narrow_entry = []
        narrow_interior = []
        internal = []
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
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target, halfword))
                if (
                    STOCK_START <= address < STOCK_END
                    and STOCK_START <= target < STOCK_END
                ):
                    internal.append((address, target, halfword))

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            internal,
            [
                (0x00482A5E, 0x00482A64, 0xD101),
                (0x00482A62, 0x00482A66, 0xE000),
            ],
        )
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "int open_cfw_runtime_style_is_empty(const void *style)",
            "const unsigned char *bytes = (const unsigned char *)style;",
            "return bytes[8] == 0U;",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_style_is_empty.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
