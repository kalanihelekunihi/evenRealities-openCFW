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
SOURCE = COMPONENT_ROOT / "runtime_style_prop_lookup_flags.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_style_prop_lookup_flags_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482A6A
STOCK_END = 0x00482AB2
BUILTIN_TABLE_START = 0x006D439C
BUILTIN_COUNT = 138
LV_STYLE_PROP_ANY = 0xFF
LV_STYLE_PROP_FLAG_ALL = 0x3F


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStylePropLookupFlagsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.stock_builtin = cls.span(
            BUILTIN_TABLE_START,
            BUILTIN_TABLE_START + BUILTIN_COUNT,
        )
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_prop_lookup_flags.dylib"
            if sys.platform == "darwin"
            else "runtime_style_prop_lookup_flags.so"
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
        cls.lookup = cls.loaded.open_cfw_runtime_style_prop_lookup_flags
        cls.lookup.argtypes = [ctypes.c_uint32]
        cls.lookup.restype = ctypes.c_ubyte
        cls.reset = cls.loaded.open_cfw_test_runtime_style_prop_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.builtin = (
            cls.loaded.open_cfw_test_runtime_style_prop_builtin_flag
        )
        cls.builtin.argtypes = [ctypes.c_uint32]
        cls.builtin.restype = ctypes.c_ubyte
        cls.custom_storage = (ctypes.c_ubyte * 256).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_prop_custom_storage",
        )
        cls.size_reads = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_prop_size_reads",
        )
        cls.pointer_reads = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_prop_pointer_reads",
        )
        cls.pointer_resolutions = ctypes.c_uint32.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_prop_pointer_resolutions",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def assert_global_untouched(self) -> None:
        self.assertEqual(self.size_reads.value, 0)
        self.assertEqual(self.pointer_reads.value, 0)
        self.assertEqual(self.pointer_resolutions.value, 0)

    def test_all_builtin_properties_match_the_exact_stock_table(self) -> None:
        self.reset(37, 117)
        self.assertEqual(len(self.stock_builtin), BUILTIN_COUNT)
        for property_id, expected in enumerate(self.stock_builtin):
            with self.subTest(property_id=property_id):
                self.assertEqual(self.builtin(property_id), expected)
                self.assertEqual(
                    self.lookup(0xA5B60000 | property_id),
                    expected,
                )
        self.assert_global_untouched()

    def test_invalid_and_any_properties_have_exact_special_results(self) -> None:
        self.reset(0, 0)
        self.assertEqual(self.lookup(0), 0)
        self.assertEqual(self.lookup(0x12340000), 0)
        self.assertEqual(self.lookup(LV_STYLE_PROP_ANY), LV_STYLE_PROP_FLAG_ALL)
        self.assertEqual(self.lookup(0xCAFE00FF), LV_STYLE_PROP_FLAG_ALL)
        self.assert_global_untouched()

    def test_custom_properties_use_byte_normalized_index_and_size(self) -> None:
        pointer = 23
        size = 117
        self.reset(pointer, size)
        for custom_index in range(size):
            self.custom_storage[pointer + custom_index] = (
                custom_index * 37 + 11
            ) & 0xFF

        cases = (138, 139, 180, 253, 254)
        for property_id in cases:
            custom_index = property_id - BUILTIN_COUNT
            with self.subTest(property_id=property_id):
                before_sizes = self.size_reads.value
                before_pointers = self.pointer_reads.value
                before_resolutions = self.pointer_resolutions.value
                self.assertEqual(
                    self.lookup(0x5A7C0000 | property_id),
                    self.custom_storage[pointer + custom_index],
                )
                self.assertEqual(self.size_reads.value, before_sizes + 1)
                self.assertEqual(
                    self.pointer_reads.value,
                    before_pointers + 2,
                )
                self.assertEqual(
                    self.pointer_resolutions.value,
                    before_resolutions + 1,
                )

    def test_null_and_out_of_range_custom_tables_return_zero_safely(self) -> None:
        self.reset(0, 117)
        self.assertEqual(self.lookup(138), 0)
        self.assertEqual(self.pointer_reads.value, 1)
        self.assertEqual(self.size_reads.value, 0)
        self.assertEqual(self.pointer_resolutions.value, 0)

        self.reset(29, 2)
        self.custom_storage[29] = 0x31
        self.custom_storage[30] = 0x22
        self.custom_storage[31] = 0x3F
        self.assertEqual(self.lookup(138), 0x31)
        self.assertEqual(self.lookup(139), 0x22)
        before_pointers = self.pointer_reads.value
        before_sizes = self.size_reads.value
        before_resolutions = self.pointer_resolutions.value
        self.assertEqual(self.lookup(140), 0)
        self.assertEqual(self.pointer_reads.value, before_pointers + 1)
        self.assertEqual(self.size_reads.value, before_sizes + 1)
        self.assertEqual(
            self.pointer_resolutions.value,
            before_resolutions,
        )

    def test_stock_body_caller_and_adjacent_boundaries_are_pinned(self) -> None:
        stock = self.span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 72)
        self.assertEqual(
            stock.hex(),
            "0100c9b2ff2901d13f201ce00100c9b2002901d1002016e0"
            "0100c9b28a2903da1c49c0b2085c0ee07630084a116b0029"
            "08d00100c9b2936a994203d2116bc0b2085c00e000207047",
        )
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "07168721fd141e88723ce6fdeba3a706"
            "85a7205513862d3e87cac10457108958",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(0x00482A5A, STOCK_START)
            ).hexdigest(),
            "8953caaab007ed0e44911ad65dcabba5"
            "70a3c5d9e791de3136b088b696deef55",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(STOCK_END, 0x00482B00)
            ).hexdigest(),
            "4189f9073fb8b1348be4112fb54b869"
            "ce0be29aed96084b5817d906e65421207",
        )
        caller = self.span(0x0044B844, 0x0044B85C)
        self.assertEqual(
            caller.hex(),
            "10b50c00c0b237f00ef9204201d0012000e00020c0b210bd",
        )
        self.assertEqual(
            hashlib.sha256(caller).hexdigest(),
            "dbb856686589a3316d1696072ea1b641"
            "abbdaacb02f06f554f02d4646e2085e5",
        )

    def test_literal_pool_global_fields_and_builtin_table_are_exact(
        self,
    ) -> None:
        literal_pool = self.span(STOCK_END, 0x00482B00)
        self.assertEqual(len(literal_pool), 78)
        self.assertEqual(literal_pool[:2], b"\x00\x00")
        self.assertEqual(
            struct.unpack_from("<I", literal_pool, 6)[0],
            0x2006F548,
        )
        self.assertEqual(
            struct.unpack_from("<I", literal_pool, 74)[0],
            BUILTIN_TABLE_START,
        )
        self.assertEqual(
            hashlib.sha256(self.stock_builtin).hexdigest(),
            "cd298adbcb31fff3ec4d1e90648c34b2"
            "d4c84536f5c6f9eb0b615b7dd9f970c5",
        )
        self.assertEqual(
            self.span(BUILTIN_TABLE_START - 16, BUILTIN_TABLE_START).hex(),
            "203230323620646f706f206c65000000",
        )
        self.assertEqual(
            self.span(
                BUILTIN_TABLE_START + BUILTIN_COUNT,
                BUILTIN_TABLE_START + BUILTIN_COUNT + 16,
            ).hex(),
            "00005b6e617669676174696f6e2e7569",
        )

        expected_literals = [
            (0x0048287A, 0x00482AC4, 0x0074B0CC),
            (0x0048287E, 0x00482AC8, 0x0078114C),
            (0x00482884, 0x00482AB4, 0x006E8938),
            (0x00482896, 0x00482ACC, 0x0076DE58),
            (0x0048289A, 0x00482AD0, 0x0076DE3C),
            (0x0048289E, 0x00482AC8, 0x0078114C),
            (0x004828A4, 0x00482AB4, 0x006E8938),
            (0x0048296A, 0x00482AD4, 0x00450635),
            (0x0048298A, 0x00482AD8, 0x0078F278),
            (0x00482A0C, 0x00482ADC, 0x0078F27C),
            (0x00482A2E, 0x00482AE0, 0x0078F280),
            (0x00482A34, 0x00482AE4, 0x0078F284),
            (0x00482A3A, 0x00482AE8, 0x0078F288),
            (0x00482A40, 0x00482AEC, 0x0078F28C),
            (0x00482A46, 0x00482AF0, 0x0078F290),
            (0x00482A4C, 0x00482AF4, 0x0078F294),
            (0x00482A52, 0x00482AF8, 0x0078F298),
            (0x00482A8A, 0x00482AFC, BUILTIN_TABLE_START),
            (0x00482A94, 0x00482AB8, 0x2006F548),
        ]
        observed_literals = []
        for offset in range(0, len(self.application) - 1, 2):
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            if halfword & 0xF800 != 0x4800:
                continue
            address = APPLICATION_BASE + offset
            literal = (
                ((address + 4) & ~3)
                + ((halfword & 0xFF) << 2)
            )
            if STOCK_END <= literal < 0x00482B00:
                value = struct.unpack_from(
                    "<I",
                    self.application,
                    literal - APPLICATION_BASE,
                )[0]
                observed_literals.append((address, literal, value))
        self.assertEqual(observed_literals, expected_literals)

    def test_complete_branch_and_stored_pointer_topology_is_pinned(
        self,
    ) -> None:
        sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
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

        self.assertEqual(callers, [(0x0044B84A, "37f00ef9")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(dependencies, [])

        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
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
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            target = value & ~1
            if value & 1 and STOCK_START <= target < STOCK_END:
                stored.append((APPLICATION_BASE + offset, target))

        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(stored, [])

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_style_prop_lookup_flags(",
            "OPEN_CFW_RUNTIME_STYLE_PROP_BUILTIN_COUNT = 138U",
            "OPEN_CFW_RUNTIME_STYLE_PROP_ANY = 0xffU",
            "OPEN_CFW_RUNTIME_STYLE_PROP_ALL_FLAGS = 0x3fU",
            "0x2006F570U",
            "0x2006F578U",
            "open_cfw_runtime_style_prop_builtin_flags[normalized]",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_style_prop_lookup_flags.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
