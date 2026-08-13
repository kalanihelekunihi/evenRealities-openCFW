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
SOURCE = COMPONENT_ROOT / "runtime_style_default_value.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_style_default_value_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x0048297C
STOCK_END = 0x00482A5A
GLOBAL_BASE = 0x0078F278
STOCK_GLOBALS = (
    0x00FFFFFF,
    0x00000100,
    0x000000FF,
    0x000000FF,
    0x0000000F,
    0x00755610,
    0x1FFFFFFF,
    0x00000100,
    0x00000000,
)

COLOR_PROPERTIES = {0x1C}
THREE_BYTE_ZERO_PROPERTIES = {
    0x23,
    0x31,
    0x39,
    0x3D,
    0x45,
    0x4C,
    0x52,
    0x58,
    0x78,
}
GLOBAL_CASES = {
    0x05: 6,
    0x07: 6,
    0x22: 3,
    0x24: 2,
    0x25: 2,
    0x29: 2,
    0x32: 2,
    0x34: 4,
    0x3A: 2,
    0x3E: 2,
    0x44: 2,
    0x4D: 2,
    0x53: 2,
    0x59: 2,
    0x5A: 5,
    0x62: 2,
    0x63: 2,
    0x6E: 1,
    0x6F: 1,
    0x76: 7,
}


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStyleDefaultValueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_default_value.dylib"
            if sys.platform == "darwin"
            else "runtime_style_default_value.so"
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
        cls.execute = cls.loaded.open_cfw_test_runtime_style_default_execute
        cls.execute.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.execute.restype = ctypes.c_uint32
        cls.reset = cls.loaded.open_cfw_test_runtime_style_default_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.values = (ctypes.c_uint32 * 9).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_default_values",
        )
        cls.load_addresses = (ctypes.c_uint32 * 16).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_default_load_addresses",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def install_values(self, values: tuple[int, ...] = STOCK_GLOBALS) -> None:
        for index, value in enumerate(values):
            self.values[index] = value
        self.reset()

    def expected(
        self,
        property_value: int,
        incoming_r1: int,
        values: tuple[int, ...] = STOCK_GLOBALS,
    ) -> tuple[int, list[int]]:
        normalized = property_value & 0xFF
        reads = [GLOBAL_BASE]
        if normalized in COLOR_PROPERTIES:
            return (
                (incoming_r1 & 0xFF000000) | (values[0] & 0x00FFFFFF),
                reads,
            )
        if normalized in THREE_BYTE_ZERO_PROPERTIES:
            return incoming_r1 & 0xFF000000, reads
        index = GLOBAL_CASES.get(normalized, 8)
        reads.append(GLOBAL_BASE + index * 4)
        return values[index], reads

    def assert_execution(
        self,
        property_value: int,
        incoming_r1: int,
        values: tuple[int, ...] = STOCK_GLOBALS,
    ) -> None:
        expected, reads = self.expected(property_value, incoming_r1, values)
        observed = self.execute(property_value, incoming_r1)
        self.assertEqual(observed, expected)
        count = self.uint(
            "open_cfw_test_runtime_style_default_load_count"
        ).value
        self.assertEqual(count, len(reads))
        self.assertEqual(list(self.load_addresses[:count]), reads)

    def test_all_256_properties_match_the_complete_dispatch_table(
        self,
    ) -> None:
        for property_value in range(256):
            self.install_values()
            incoming_r1 = (property_value * 0x01010101) ^ 0xA50000A5
            with self.subTest(property=f"{property_value:#04x}"):
                self.assert_execution(property_value, incoming_r1)

    def test_three_byte_results_preserve_incoming_r1_high_byte(self) -> None:
        for property_value in sorted(
            COLOR_PROPERTIES | THREE_BYTE_ZERO_PROPERTIES
        ):
            for high_byte in (0x00, 0x01, 0x7F, 0x80, 0xA5, 0xFF):
                self.install_values()
                incoming_r1 = high_byte << 24 | 0x0055AA33
                with self.subTest(
                    property=f"{property_value:#04x}",
                    high_byte=high_byte,
                ):
                    self.assert_execution(property_value, incoming_r1)

    def test_full_word_global_cases_ignore_incoming_r1(self) -> None:
        for property_value in sorted(GLOBAL_CASES):
            for incoming_r1 in (0, 0xA5FFFFFF, 0xFFFFFFFF):
                self.install_values()
                with self.subTest(
                    property=f"{property_value:#04x}",
                    incoming_r1=f"{incoming_r1:#010x}",
                ):
                    self.assert_execution(property_value, incoming_r1)

    def test_low_byte_normalization_and_runtime_global_loads(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            values = tuple(generator.getrandbits(32) for _ in range(9))
            normalized = generator.randrange(256)
            property_value = normalized | (generator.getrandbits(24) << 8)
            incoming_r1 = generator.getrandbits(32)
            self.install_values(values)
            with self.subTest(index=index, normalized=normalized):
                self.assert_execution(
                    property_value,
                    incoming_r1,
                    values,
                )

    def test_reviewed_arm_toolchain_preserves_the_r1_carrier_abi(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = Path(directory) / "runtime_style_default_value.o"
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                "--target=thumbv7em-none-eabi",
                "-mthumb",
                "-O2",
                "-ffreestanding",
                "-fno-jump-tables",
                "-fomit-frame-pointer",
                "-fno-builtin",
                "-mno-unaligned-access",
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fropi",
                "-Wall",
                "-Wextra",
                "-Werror",
                "-c",
                str(SOURCE),
                "-o",
                str(object_path),
            ]
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )

            sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
            import apollo_overlay

            data, sections = apollo_overlay.parse_elf32(object_path)
            text_section = apollo_overlay.section_named(sections, ".text")
            start = int(text_section["offset"])
            end = start + int(text_section["size"])
            text = data[start:end]

        self.assertEqual(len(text), 184)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "b8603f32e818ebc2a9d425056b02124b"
            "691da814bc0013508cba701389491f44",
        )
        self.assertIn(bytes.fromhex("090e61f31f60"), text)
        self.assertIn(bytes.fromhex("01f07f40"), text)
        self.assertNotIn(".rel.text", {section["name"] for section in sections})

    def test_stock_span_globals_and_adjacent_boundaries_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        preceding = span(0x00482950, STOCK_START)
        self.assertEqual(len(preceding), 44)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "fabbb1b5b1efc42178859412578c1d81"
            "4e2d03d28032144c156e8125460b70f2",
        )

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 222)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "ff9eb32171697c70cbd592801924eb4e"
            "e1b7279a0378f9d0c04c6941e7beff96",
        )

        following = span(STOCK_END, 0x00482A6A)
        self.assertEqual(
            following.hex(),
            "007a002801d1012000e00020c0b27047",
        )
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "8953caaab007ed0e44911ad65dcabba57"
            "0a3c5d9e791de3136b088b696deef55",
        )

        literal_words = tuple(
            struct.unpack_from(
                "<I",
                application,
                address - APPLICATION_BASE,
            )[0]
            for address in range(0x00482AD8, 0x00482AFC, 4)
        )
        self.assertEqual(
            literal_words,
            tuple(GLOBAL_BASE + index * 4 for index in range(9)),
        )

        global_bytes = span(GLOBAL_BASE, GLOBAL_BASE + 36)
        self.assertEqual(
            struct.unpack("<9I", global_bytes),
            STOCK_GLOBALS,
        )
        self.assertEqual(
            hashlib.sha256(global_bytes).hexdigest(),
            "658f7c6fd2f751ea36c784d58bc7ef9"
            "e68f67bb29097e450bf648078399de916",
        )

    def test_wide_caller_dependency_and_interior_topology_is_complete(
        self,
    ) -> None:
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

        self.assertEqual(callers, [(0x0044BE44, "36f09afd")])
        self.assertEqual(
            hashlib.sha256(
                struct.pack("<I", callers[0][0])
                + bytes.fromhex(callers[0][1])
            ).hexdigest(),
            "904669d5081221173aea0b09aab2291e"
            "72d84ffcd1dcc19fd156a4f41d58e293",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00482986, 0x0043BB00, "b9f7bbf8"),
                (0x00482A18, 0x00439BE4, "b7f7e4f8"),
                (0x00482A26, 0x00439BE4, "b7f7ddf8"),
            ],
        )

    def test_narrow_topology_and_unaligned_pointer_false_positives(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
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
                narrow_entry.append((address, halfword))
            for target in candidates:
                if (
                    STOCK_START < target < STOCK_END
                    and not STOCK_START <= address < STOCK_END
                ):
                    narrow_interior.append((address, target, halfword))

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target, value))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            stored,
            [
                (0x004984FF, 0x004829D0, 0x004829D1),
                (0x005FA08B, 0x00482A46, 0x00482A47),
                (0x0064A523, 0x004829FE, 0x004829FF),
            ],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_style_default_value(",
            "incoming_r1 & 0xFF000000U",
            "low_value & 0x00FFFFFFU",
            "unsigned int normalized = (unsigned char)property;",
            "OPEN_CFW_RUNTIME_STYLE_DEFAULT_LOAD(",
            "OPEN_CFW_RUNTIME_STYLE_DEFAULT_ZERO_ADDRESS",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_style_default_value.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
