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
SOURCE = COMPONENT_ROOT / "runtime_style_set_property.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_style_set_property_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x00482868
STOCK_END = 0x00482946
OLD_TABLE = 64
NEW_TABLE = 8192
STORAGE_SIZE = 32768


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


def _decode_narrow_branch(address: int, halfword: int) -> int | None:
    if halfword & 0xF800 == 0xE000:
        return address + 4 + (_sign_extend(halfword & 0x7FF, 11) << 1)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0xF) < 0xE
    ):
        return address + 4 + (_sign_extend(halfword & 0xFF, 8) << 1)
    return None


class RuntimeStyleSetDescriptor(ctypes.Structure):
    _fields_ = [
        ("table", ctypes.c_uint32),
        ("property_groups", ctypes.c_uint32),
        ("count_or_static", ctypes.c_ubyte),
        ("reserved_09", ctypes.c_ubyte),
        ("reserved_0a", ctypes.c_ubyte),
        ("reserved_0b", ctypes.c_ubyte),
    ]


class RuntimeStyleSetPropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_set_property.dylib"
            if sys.platform == "darwin"
            else "runtime_style_set_property.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_style_set_reset
        cls.reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.set_groups = cls.loaded.open_cfw_test_runtime_style_set_set_groups
        cls.set_groups.argtypes = [ctypes.c_uint32]
        cls.set_groups.restype = None
        cls.set_entry = cls.loaded.open_cfw_test_runtime_style_set_set_entry
        cls.set_entry.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_entry.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_style_set_execute
        cls.execute.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.execute.restype = None
        cls.style = RuntimeStyleSetDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_set_descriptor",
        )
        cls.storage = (ctypes.c_ubyte * STORAGE_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_set_storage",
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def uint(self, name: str) -> ctypes.c_uint32:
        return ctypes.c_uint32.in_dll(self.loaded, name)

    def install(
        self,
        values: list[int],
        properties: list[int],
        *,
        table: int = OLD_TABLE,
        reallocate_result: int = OLD_TABLE,
        groups: int = 0xA55A3CC3,
    ) -> None:
        self.assertEqual(len(values), len(properties))
        self.reset(len(values), table, reallocate_result)
        self.set_groups(groups)
        for index, (value, property_value) in enumerate(
            zip(values, properties)
        ):
            self.set_entry(index, value, property_value)

    def descriptor_bytes(self) -> bytes:
        return bytes(ctypes.string_at(ctypes.byref(self.style), 12))

    def table_values(self) -> list[int]:
        count = self.style.count_or_static
        table = self.style.table
        raw = bytes(self.storage[table:table + count * 4])
        return list(struct.unpack(f"<{count}I", raw)) if count else []

    def table_properties(self) -> list[int]:
        count = self.style.count_or_static
        start = self.style.table + count * 4
        return list(self.storage[start:start + count])

    def test_existing_property_updates_last_duplicate_without_growth(
        self,
    ) -> None:
        values = [0x11111111, 0x22222222, 0x33333333, 0x44444444]
        properties = [0x21, 0x42, 0x21, 0x63]
        self.install(values, properties)
        self.execute(0xA5B60021, 0xDEADBEEF)
        self.assertEqual(
            self.table_values(),
            [0x11111111, 0x22222222, 0xDEADBEEF, 0x44444444],
        )
        self.assertEqual(self.table_properties(), properties)
        self.assertEqual(self.style.property_groups, 0xA55A3CC3)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_set_reallocate_calls"
            ).value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_bucket_calls").value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_pointer_calls").value,
            1,
        )

    def test_in_place_growth_shifts_packed_keys_and_updates_bitmap(
        self,
    ) -> None:
        values = [0x10203040, 0x55667788, 0x90ABCDEF]
        properties = [0x11, 0x22, 0x33]
        self.install(values, properties, groups=0x00000004)
        self.execute(0xF00D0041, 0x13579BDF)
        self.assertEqual(
            self.table_values(),
            values + [0x13579BDF],
        )
        self.assertEqual(self.table_properties(), properties + [0x41])
        self.assertEqual(self.style.table, OLD_TABLE)
        self.assertEqual(self.style.count_or_static, 4)
        self.assertEqual(
            self.style.property_groups,
            0x00000004 | (1 << (0x41 >> 2)),
        )
        self.assertEqual(
            [
                self.uint(
                    "open_cfw_test_runtime_style_set_reallocate_allocation"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_reallocate_size"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_reallocate_table_before"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_reallocate_count_before"
                ).value,
            ],
            [OLD_TABLE, 20, OLD_TABLE, 3],
        )
        self.assertEqual(
            [
                self.uint(
                    "open_cfw_test_runtime_style_set_static_order"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_reallocate_order"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_bucket_order"
                ).value,
            ],
            [1, 2, 3],
        )
        self.assertEqual(
            [
                self.uint(
                    "open_cfw_test_runtime_style_set_bucket_property"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_bucket_table"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_bucket_count"
                ).value,
            ],
            [0x41, OLD_TABLE, 4],
        )

    def test_moved_reallocation_and_empty_allocation_are_exact(self) -> None:
        cases = [
            (
                [0x01020304, 0xA0B0C0D0],
                [0x18, 0x29],
                OLD_TABLE,
                0x3A,
                0xCAFEBABE,
            ),
            ([], [], 0, 0x7F, 0x01234567),
        ]
        for values, properties, table, added, value in cases:
            self.install(
                values,
                properties,
                table=table,
                reallocate_result=NEW_TABLE,
                groups=0,
            )
            self.execute(added, value)
            with self.subTest(count=len(values)):
                self.assertEqual(self.style.table, NEW_TABLE)
                self.assertEqual(self.style.count_or_static, len(values) + 1)
                self.assertEqual(self.table_values(), values + [value])
                self.assertEqual(
                    self.table_properties(),
                    properties + [added],
                )
                self.assertEqual(
                    self.style.property_groups,
                    1 << min(added >> 2, 31),
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_set_reallocate_size"
                    ).value,
                    (len(values) + 1) * 5,
                )

    def test_reallocation_failure_is_transactional_and_silent(self) -> None:
        self.install(
            [0x01020304, 0x55667788, 0xA0B0C0D0],
            [0x10, 0x20, 0x30],
            reallocate_result=0,
        )
        before_descriptor = self.descriptor_bytes()
        before_storage = bytes(self.storage)
        self.execute(0x44, 0xDEADC0DE)
        self.assertEqual(self.descriptor_bytes(), before_descriptor)
        self.assertEqual(bytes(self.storage), before_storage)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_set_reallocate_size"
            ).value,
            20,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_bucket_calls").value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_log_calls").value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_fatal_calls").value,
            0,
        )

    def test_static_and_invalid_diagnostics_match_stock(self) -> None:
        self.reset(0xFF, OLD_TABLE, NEW_TABLE)
        before = self.descriptor_bytes()
        self.execute(0x42, 0x12345678)
        self.assertEqual(self.descriptor_bytes(), before)
        self.assertEqual(
            [
                self.uint("open_cfw_test_runtime_style_set_log_level").value,
                self.uint("open_cfw_test_runtime_style_set_log_file").value,
                self.uint("open_cfw_test_runtime_style_set_log_line").value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_function"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_message"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_expression"
                ).value,
            ],
            [3, 0x006E8938, 0x14C, 0x0078114C, 0x0074B0CC, 0],
        )
        self.assertEqual(
            [
                self.uint(
                    "open_cfw_test_runtime_style_set_static_order"
                ).value,
                self.uint("open_cfw_test_runtime_style_set_log_order").value,
            ],
            [1, 2],
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_set_reallocate_calls"
            ).value,
            0,
        )

        self.install([0x11111111], [0x21])
        before_descriptor = self.descriptor_bytes()
        before_storage = bytes(self.storage)
        self.execute(0xABCDEF00, 0x87654321)
        self.assertEqual(self.descriptor_bytes(), before_descriptor)
        self.assertEqual(bytes(self.storage), before_storage)
        self.assertEqual(
            [
                self.uint("open_cfw_test_runtime_style_set_log_level").value,
                self.uint("open_cfw_test_runtime_style_set_log_file").value,
                self.uint("open_cfw_test_runtime_style_set_log_line").value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_function"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_message"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_set_log_expression"
                ).value,
            ],
            [
                3,
                0x006E8938,
                0x150,
                0x0078114C,
                0x0076DE3C,
                0x0076DE58,
            ],
        )
        self.assertEqual(
            [
                self.uint(
                    "open_cfw_test_runtime_style_set_static_order"
                ).value,
                self.uint("open_cfw_test_runtime_style_set_log_order").value,
                self.uint(
                    "open_cfw_test_runtime_style_set_fatal_order"
                ).value,
            ],
            [1, 2, 3],
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_set_fatal_calls").value,
            1,
        )

    def test_randomized_append_oracle_and_count_254_boundary(self) -> None:
        generator = random.Random(STOCK_START)
        for case in range(128):
            count = generator.randrange(0, 96)
            properties = generator.sample(range(1, 256), count + 1)
            existing = properties[:-1]
            added = properties[-1]
            values = [generator.getrandbits(32) for _ in range(count)]
            new_value = generator.getrandbits(32)
            groups = generator.getrandbits(32)
            allocation_result = (
                OLD_TABLE if case & 1 else NEW_TABLE
            )
            table = OLD_TABLE if count else 0
            self.install(
                values,
                existing,
                table=table,
                reallocate_result=allocation_result,
                groups=groups,
            )
            self.execute(
                added | (generator.getrandbits(24) << 8),
                new_value,
            )
            with self.subTest(case=case, count=count):
                self.assertEqual(self.table_values(), values + [new_value])
                self.assertEqual(
                    self.table_properties(),
                    existing + [added],
                )
                self.assertEqual(
                    self.style.property_groups,
                    groups | (1 << min(added >> 2, 31)),
                )

        values = [0x10000000 + index for index in range(254)]
        properties = list(range(1, 255))
        self.install(values, properties, groups=0)
        self.execute(0xFF, 0xFEEDFACE)
        self.assertEqual(self.style.count_or_static, 0xFF)
        self.assertEqual(self.table_values(), values + [0xFEEDFACE])
        self.assertEqual(self.table_properties(), properties + [0xFF])
        self.assertEqual(self.style.property_groups, 0x80000000)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_set_reallocate_size"
            ).value,
            1275,
        )

    def test_stock_body_literals_and_adjacent_boundaries_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        previous = span(0x004827B0, STOCK_START)
        self.assertEqual(len(previous), 184)
        self.assertEqual(
            hashlib.sha256(previous).hexdigest(),
            "7301b5de7a8104a456296a6d2b4a74e6"
            "f978ed913109aeae4d02b54865d46360",
        )
        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 222)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "1071391c48262cafb1f72a5bba29b3ba"
            "e4eeb52a15908faf9dee60435c214a84",
        )
        following = span(STOCK_END, 0x00482950)
        self.assertEqual(following.hex(), "80b5c9b2fff7e4fe02bd")
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "152db6bc74bffc0424ceeb1dc3eeaffa"
            "bef107ac09a125bfbfc4c0093ccfb7af",
        )

        literal_words = {
            0x00482AB4: 0x006E8938,
            0x00482AC4: 0x0074B0CC,
            0x00482AC8: 0x0078114C,
            0x00482ACC: 0x0076DE58,
            0x00482AD0: 0x0076DE3C,
        }
        for address, expected in literal_words.items():
            observed = struct.unpack_from(
                "<I",
                application,
                address - APPLICATION_BASE,
            )[0]
            self.assertEqual(observed, expected)
        expected_strings = {
            0x006E8938:
                b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party"
                b"\\lvgl_v9.3\\LVGL\\src\\misc\\lv_style.c",
            0x0074B0CC: b"Cannot set property of constant style",
            0x0078114C: b"lv_style_set_prop",
            0x0076DE58: b"prop != LV_STYLE_PROP_INV",
            0x0076DE3C: b"Asserted at expression: %s",
        }
        for address, expected in expected_strings.items():
            offset = address - APPLICATION_BASE
            self.assertEqual(
                application[offset:offset + len(expected) + 1],
                expected + b"\0",
            )

    def test_all_callers_dependencies_and_entry_topology_are_complete(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]
        sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        dependencies = []
        narrow_interior = []
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

            target = _decode_narrow_branch(
                address,
                int.from_bytes(encoded[:2], "little"),
            )
            if (
                target is not None
                and STOCK_START < target < STOCK_END
                and not STOCK_START <= address < STOCK_END
            ):
                narrow_interior.append((address, target))

        self.assertEqual(len(callers), 50)
        self.assertEqual(
            callers[:4],
            [
                (0x0044BE96, "36f0e7fc"),
                (0x0044C02C, "36f01cfc"),
                (0x0044CC66, "35f0fffd"),
                (0x0044CCC8, "35f0cefd"),
            ],
        )
        self.assertEqual(
            [address for address, _ in callers[4:]],
            [
                0x004D4820, 0x004D482C, 0x004D4838, 0x004D4844,
                0x004D4850, 0x004D485C, 0x004D4868, 0x004D4874,
                0x004D4880, 0x004D488C, 0x004D4898, 0x004D48A4,
                0x004D48BE, 0x004D48CC, 0x004D48E6, 0x004D48F2,
                0x004D490C, 0x004D491A, 0x004D4926, 0x004D4934,
                0x004D4942, 0x004D494E, 0x004D4968, 0x004D4976,
                0x004D4982, 0x004D498E, 0x004D499A, 0x004D49A6,
                0x004D49C0, 0x004D49CE, 0x004D49DA, 0x004D49F4,
                0x004D4A00, 0x004D4A0E, 0x004D4A28, 0x004D4A42,
                0x004D4A4E, 0x004D4A5A, 0x004D4A68, 0x004D4A74,
                0x004D4A82, 0x004D4A9C, 0x004D4AAA, 0x004D4AB6,
                0x004D4AC2, 0x004D4ACE,
            ],
        )
        packed_addresses = b"".join(
            struct.pack("<I", address) for address, _ in callers
        )
        self.assertEqual(
            hashlib.sha256(packed_addresses).hexdigest(),
            "7348bf68f8a1c756264fab6723e467569"
            "3e86a469c4575bea308351ce9f37951",
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(narrow_interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x00482872, 0x00482708, "fff749ff"),
                (0x00482888, 0x0044D25C, "caf7e8fc"),
                (0x004828A8, 0x0044D25C, "caf7d8fc"),
                (0x004828EE, 0x0044F76A, "ccf73cff"),
                (0x00482934, 0x0048277E, "fff723ff"),
            ],
        )

        stored_entry = struct.pack("<I", STOCK_START | 1)
        self.assertEqual(application.find(stored_entry), -1)
        stored_interior = []
        for target in range(STOCK_START + 2, STOCK_END, 2):
            needle = struct.pack("<I", target | 1)
            position = application.find(needle)
            while position >= 0:
                stored_interior.append(
                    (APPLICATION_BASE + position, target)
                )
                position = application.find(needle, position + 1)
        self.assertEqual(
            stored_interior,
            [
                (0x00584703, 0x004828B4),
                (0x00539D21, 0x004828E6),
                (0x0058BB6F, 0x00482910),
            ],
        )
        self.assertTrue(all(address & 1 for address, _ in stored_interior))

    def test_reallocation_dependency_and_failure_diagnostic_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        wrapper = span(0x0044F76A, 0x0044F7A4)
        self.assertEqual(len(wrapper), 58)
        self.assertEqual(
            hashlib.sha256(wrapper).hexdigest(),
            "b33ee2678d15bdb0176f5ca3b8e27351"
            "25b440ce17f361c108d0b64c6d32d29e",
        )
        backend = span(0x0048432A, 0x00484338)
        self.assertEqual(len(backend), 14)
        self.assertEqual(
            hashlib.sha256(backend).hexdigest(),
            "45fe398ca48d9f2b769d5ee758ec48e0"
            "dfcbe8923167bd3c3f3a187d0cbf2cc5",
        )
        wrapper_literals = {
            0x0044F7A4: 0x2006F5AC,
            0x0044F7A8: 0x0076DC28,
            0x0044F7AC: 0x0078B3CC,
            0x0044F7B0: 0x006E883C,
        }
        for address, expected in wrapper_literals.items():
            self.assertEqual(
                struct.unpack_from(
                    "<I",
                    application,
                    address - APPLICATION_BASE,
                )[0],
                expected,
            )
        message = b"couldn't reallocate memory\0"
        offset = 0x0076DC28 - APPLICATION_BASE
        self.assertEqual(
            application[offset:offset + len(message)],
            message,
        )

    def test_source_and_fixture_stay_bounded(self) -> None:
        source = SOURCE.read_text()
        fixture = FIXTURE.read_text()
        self.assertIn("open_cfw_runtime_style_set_property", source)
        self.assertIn("0x0044F76BU", source)
        self.assertIn("0xFFFFFFFFU", source)
        self.assertNotIn("malloc(", source)
        self.assertNotIn("free(", source)
        self.assertIn(
            '#include "../../components/apollo_main/core_overlay/'
            'runtime_style_set_property.c"',
            fixture,
        )


if __name__ == "__main__":
    unittest.main()
