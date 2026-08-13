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
SOURCE = COMPONENT_ROOT / "runtime_byte_map_lookup.c"
FIXTURE = (
    OPENCFW_ROOT / "tests" / "fixtures" / "runtime_byte_map_lookup_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482716
STOCK_END = 0x0048277E
TABLE_OFFSET = 16


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeByteMap(ctypes.Structure):
    _fields_ = [
        ("table", ctypes.c_uint32),
        ("reserved_04", ctypes.c_uint32),
        ("count_or_sentinel", ctypes.c_uint8),
        ("reserved_09", ctypes.c_uint8),
        ("reserved_0a", ctypes.c_uint8),
        ("reserved_0b", ctypes.c_uint8),
    ]


class RuntimeByteMapLookupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_byte_map_lookup.dylib"
            if sys.platform == "darwin"
            else "runtime_byte_map_lookup.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_byte_map_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_byte_map_execute
        cls.execute.argtypes = [ctypes.c_uint32]
        cls.execute.restype = ctypes.c_uint32
        cls.storage = (ctypes.c_ubyte * 4096).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_byte_map_storage",
        )
        cls.map = RuntimeByteMap.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_byte_map",
        )
        cls.output = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_byte_map_output",
        )
        cls.pointer_calls = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_byte_map_pointer_calls",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def reset_storage(self) -> None:
        for index in range(len(self.storage)):
            self.storage[index] = 0xA5

    def install_compact(
        self,
        entries: list[tuple[int, int]],
        *,
        output: int = 0xDEADBEEF,
    ) -> None:
        self.reset_storage()
        self.reset(TABLE_OFFSET, len(entries), output)
        for index, (key, value) in enumerate(entries):
            struct.pack_into("<I", self.storage, TABLE_OFFSET + index * 4, value)
            self.storage[TABLE_OFFSET + len(entries) * 4 + index] = key

    def install_sentinel(
        self,
        entries: list[tuple[int, int]],
        *,
        output: int = 0xDEADBEEF,
    ) -> None:
        self.reset_storage()
        self.reset(TABLE_OFFSET, 0xFF, output)
        for index, (key, value) in enumerate(entries):
            struct.pack_into(
                "<B3xI",
                self.storage,
                TABLE_OFFSET + index * 8,
                key,
                value,
            )
        struct.pack_into(
            "<B3xI",
            self.storage,
            TABLE_OFFSET + len(entries) * 8,
            0,
            0xA5A5A5A5,
        )

    def assert_descriptor_unchanged(self, mode: int) -> None:
        self.assertEqual(self.map.table, TABLE_OFFSET)
        self.assertEqual(self.map.reserved_04, 0x04040404)
        self.assertEqual(self.map.count_or_sentinel, mode)
        self.assertEqual(self.map.reserved_09, 0x09)
        self.assertEqual(self.map.reserved_0a, 0x0A)
        self.assertEqual(self.map.reserved_0b, 0x0B)

    def test_zero_count_misses_without_resolving_the_table_pointer(self) -> None:
        self.reset(0xFFFFFFFF, 0, 0x12345678)
        self.assertEqual(self.execute(0x41), 0)
        self.assertEqual(self.output.value, 0x12345678)
        self.assertEqual(self.pointer_calls.value, 0)
        self.assertEqual(self.map.table, 0xFFFFFFFF)

    def test_compact_layout_returns_first_match_and_normalizes_key(self) -> None:
        entries = [
            (0x10, 0x11111111),
            (0x80, 0x22222222),
            (0x10, 0x33333333),
            (0xFF, 0x44444444),
        ]
        self.install_compact(entries)
        self.assertEqual(self.execute(0xCAFE0110), 1)
        self.assertEqual(self.output.value, 0x11111111)
        self.assertEqual(self.pointer_calls.value, 1)
        self.assert_descriptor_unchanged(len(entries))

    def test_compact_layout_supports_zero_and_maximum_count(self) -> None:
        entries = [
            (index & 0xFF, (index * 0x01020304) & 0xFFFFFFFF)
            for index in range(254)
        ]
        entries[0] = (0, 0x01010101)
        entries[-1] = (0xFE, 0xFEFEFEFE)
        self.install_compact(entries)
        self.assertEqual(self.execute(0), 1)
        self.assertEqual(self.output.value, 0x01010101)
        self.install_compact(entries)
        self.assertEqual(self.execute(0xFFFFFFFE), 1)
        self.assertEqual(self.output.value, 0xFEFEFEFE)
        self.assert_descriptor_unchanged(254)

    def test_compact_miss_leaves_output_untouched(self) -> None:
        self.install_compact(
            [(1, 0x11111111), (2, 0x22222222), (3, 0x33333333)],
            output=0x89ABCDEF,
        )
        self.assertEqual(self.execute(4), 0)
        self.assertEqual(self.output.value, 0x89ABCDEF)
        self.assertEqual(self.pointer_calls.value, 1)
        self.assert_descriptor_unchanged(3)

    def test_sentinel_layout_stops_at_zero_and_returns_first_match(self) -> None:
        self.install_sentinel(
            [
                (0x44, 0x11112222),
                (0xE0, 0x33334444),
                (0x44, 0x55556666),
            ],
        )
        self.assertEqual(self.execute(0x1234E0), 1)
        self.assertEqual(self.output.value, 0x33334444)
        self.assertEqual(self.pointer_calls.value, 1)
        self.assert_descriptor_unchanged(0xFF)

        self.install_sentinel([(1, 0x11111111)], output=0x76543210)
        struct.pack_into(
            "<B3xI",
            self.storage,
            TABLE_OFFSET + 16,
            2,
            0x22222222,
        )
        self.assertEqual(self.execute(2), 0)
        self.assertEqual(self.output.value, 0x76543210)

    def test_sentinel_key_zero_is_the_terminator_not_a_match(self) -> None:
        self.install_sentinel([(0x7F, 0xCAFEBABE)], output=0x10203040)
        self.assertEqual(self.execute(0), 0)
        self.assertEqual(self.output.value, 0x10203040)
        self.assertEqual(self.pointer_calls.value, 1)

    def test_deterministic_tables_match_independent_oracle(self) -> None:
        generator = random.Random(STOCK_START)
        for index in range(256):
            sentinel = bool(generator.getrandbits(1))
            length = generator.randrange(0, 24)
            if sentinel:
                keys = [generator.randrange(1, 256) for _ in range(length)]
            else:
                keys = [generator.randrange(0, 256) for _ in range(length)]
            values = [generator.getrandbits(32) for _ in range(length)]
            entries = list(zip(keys, values))
            requested = generator.randrange(0, 256)
            full_key = requested | (generator.getrandbits(24) << 8)
            initial = generator.getrandbits(32)

            if sentinel:
                self.install_sentinel(entries, output=initial)
            else:
                self.install_compact(entries, output=initial)
            expected = next(
                (value for key, value in entries if key == requested),
                None,
            )
            observed = self.execute(full_key)

            with self.subTest(index=index, sentinel=sentinel, length=length):
                self.assertEqual(observed, 0 if expected is None else 1)
                self.assertEqual(
                    self.output.value,
                    initial if expected is None else expected,
                )
                self.assert_descriptor_unchanged(
                    0xFF if sentinel else length
                )

    def test_stock_span_caller_dependency_and_adjacent_boundaries(self) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 104)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "094798629ce86c61f6c7e0aee2be6867"
            "6cb8e7629dba07c4d0a2959a63dabcce",
        )
        preceding = span(0x00482708, STOCK_START)
        self.assertEqual(
            preceding.hex(),
            "007aff2801d1012000e000207047",
        )
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "5f4d8578d1c93ca71614bc46df4d8532"
            "23c3b8e389efde4fef5231c6cde6f999",
        )
        following = span(STOCK_END, 0x0048278C)
        self.assertEqual(
            following.hex(),
            "c0b28008c0b21f2800d31f207047",
        )
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "859ac3abf53bb7eae92a12e11c26682b"
            "6bd049ee5b4b0dfb8adb541e8f201910",
        )

        wrapper = span(0x00482946, 0x00482950)
        self.assertEqual(
            wrapper.hex(),
            "80b5c9b2fff7e4fe02bd",
        )
        self.assertEqual(
            hashlib.sha256(wrapper).hexdigest(),
            "152db6bc74bffc0424ceeb1dc3eeaffa"
            "bef107ac09a125bfbfc4c0093ccfb7af",
        )

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
                    dependencies.append((address, target, encoded.hex()))

        self.assertEqual(callers, [(0x0048294A, "fff7e4fe")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [(0x00482720, 0x00482708, "fff7f2ff")],
        )

    def test_narrow_and_stored_pointer_topology_is_pinned(self) -> None:
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
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(application) - 3):
            value = struct.unpack_from("<I", application, offset)[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))
        self.assertEqual(stored, [(0x004AAAE5, 0x00482720)])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "struct open_cfw_runtime_byte_map",
            "open_cfw_runtime_byte_map_lookup(",
            "map->count_or_sentinel == 0xffU",
            "table[index * 8U] != 0U",
            "map->count_or_sentinel * 4U",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn("runtime_byte_map_lookup.c", FIXTURE.read_text())


if __name__ == "__main__":
    unittest.main()
