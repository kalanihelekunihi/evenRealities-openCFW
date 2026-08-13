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
SOURCE = COMPONENT_ROOT / "runtime_style_remove_property.c"
FIXTURE = (
    OPENCFW_ROOT
    / "tests"
    / "fixtures"
    / "runtime_style_remove_property_host.c"
)
OFFICIAL = (
    OPENCFW_ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
APPLICATION_BASE = 0x00438000
STOCK_START = 0x004827B0
STOCK_END = 0x00482868
OLD_TABLE = 64
NEW_TABLE = 8192
STORAGE_SIZE = 32768
SNAPSHOT_SIZE = 1270


def _sign_extend(value: int, bits: int) -> int:
    sign = 1 << (bits - 1)
    return value - (1 << bits) if value & sign else value


class RuntimeStyleRemoveDescriptor(ctypes.Structure):
    _fields_ = [
        ("table", ctypes.c_uint32),
        ("property_groups", ctypes.c_uint32),
        ("count_or_static", ctypes.c_ubyte),
        ("reserved_09", ctypes.c_ubyte),
        ("reserved_0a", ctypes.c_ubyte),
        ("reserved_0b", ctypes.c_ubyte),
    ]


class RuntimeStyleRemovePropertyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        library = Path(cls.temporary.name) / (
            "runtime_style_remove_property.dylib"
            if sys.platform == "darwin"
            else "runtime_style_remove_property.so"
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
        cls.reset = cls.loaded.open_cfw_test_runtime_style_remove_reset
        cls.reset.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.set_entry = (
            cls.loaded.open_cfw_test_runtime_style_remove_set_entry
        )
        cls.set_entry.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.set_entry.restype = None
        cls.execute = cls.loaded.open_cfw_test_runtime_style_remove_execute
        cls.execute.argtypes = [ctypes.c_uint32]
        cls.execute.restype = ctypes.c_uint32
        cls.style = RuntimeStyleRemoveDescriptor.in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_remove_descriptor",
        )
        cls.storage = (ctypes.c_ubyte * STORAGE_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_remove_storage",
        )
        cls.snapshot = (ctypes.c_ubyte * SNAPSHOT_SIZE).in_dll(
            cls.loaded,
            "open_cfw_test_runtime_style_remove_free_snapshot",
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
        allocation_result: int = NEW_TABLE,
    ) -> None:
        self.assertEqual(len(values), len(properties))
        self.reset(len(values), allocation_result)
        for index, (value, property_value) in enumerate(
            zip(values, properties)
        ):
            self.set_entry(index, value, property_value)

    def descriptor_bytes(self) -> bytes:
        return bytes(ctypes.string_at(ctypes.byref(self.style), 12))

    def new_values(self, count: int) -> list[int]:
        raw = bytes(self.storage[NEW_TABLE:NEW_TABLE + count * 4])
        return list(struct.unpack(f"<{count}I", raw)) if count else []

    def new_properties(self, count: int) -> list[int]:
        start = NEW_TABLE + count * 4
        return list(self.storage[start:start + count])

    def test_static_style_logs_exact_stock_diagnostic_and_does_not_mutate(
        self,
    ) -> None:
        self.reset(0xFF, NEW_TABLE)
        before = self.descriptor_bytes()
        self.assertEqual(self.execute(0x42), 0)
        self.assertEqual(self.descriptor_bytes(), before)
        self.assertEqual(
            [
                self.uint("open_cfw_test_runtime_style_remove_log_level").value,
                self.uint("open_cfw_test_runtime_style_remove_log_file").value,
                self.uint("open_cfw_test_runtime_style_remove_log_line").value,
                self.uint(
                    "open_cfw_test_runtime_style_remove_log_function"
                ).value,
                self.uint(
                    "open_cfw_test_runtime_style_remove_log_message"
                ).value,
            ],
            [3, 0x006E8938, 0x117, 0x0077943C, 0x0075663C],
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_static_calls").value,
            1,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_static_order").value,
            1,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_log_order").value,
            2,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_remove_allocate_calls"
            ).value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_free_calls").value,
            0,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_pointer_calls").value,
            0,
        )

    def test_empty_and_missing_properties_do_not_allocate_or_mutate(
        self,
    ) -> None:
        cases = [
            ([], [], 0x31),
            ([0x11111111, 0x22222222], [0x10, 0x20], 0x30),
        ]
        for values, properties, removed in cases:
            self.install(values, properties)
            before_descriptor = self.descriptor_bytes()
            before_storage = bytes(self.storage)
            self.assertEqual(self.execute(removed), 0)
            with self.subTest(properties=properties):
                self.assertEqual(self.descriptor_bytes(), before_descriptor)
                self.assertEqual(bytes(self.storage), before_storage)
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_calls"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_free_calls"
                    ).value,
                    0,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_pointer_calls"
                    ).value,
                    0 if not values else 1,
                )

    def test_first_middle_and_last_removals_preserve_packed_order(self) -> None:
        values = [0x10203040, 0x55667788, 0x90ABCDEF, 0x13579BDF]
        properties = [0x11, 0x22, 0x33, 0x44]
        for removed_index in range(len(values)):
            self.install(values, properties)
            removed = properties[removed_index]
            self.assertEqual(self.execute(removed), 1)
            expected_values = (
                values[:removed_index] + values[removed_index + 1:]
            )
            expected_properties = (
                properties[:removed_index]
                + properties[removed_index + 1:]
            )
            with self.subTest(removed_index=removed_index):
                self.assertEqual(self.style.table, NEW_TABLE)
                self.assertEqual(self.style.count_or_static, 3)
                self.assertEqual(self.style.property_groups, 0xA55A3CC3)
                self.assertEqual(
                    (
                        self.style.reserved_09,
                        self.style.reserved_0a,
                        self.style.reserved_0b,
                    ),
                    (0x19, 0x2A, 0x3B),
                )
                self.assertEqual(self.new_values(3), expected_values)
                self.assertEqual(
                    self.new_properties(3),
                    expected_properties,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_size"
                    ).value,
                    15,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_static_order"
                    ).value,
                    1,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_order"
                    ).value,
                    2,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_table_before"
                    ).value,
                    OLD_TABLE,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_count_before"
                    ).value,
                    4,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_free_order"
                    ).value,
                    3,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_free_allocation"
                    ).value,
                    OLD_TABLE,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_free_table"
                    ).value,
                    NEW_TABLE,
                )
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_free_count"
                    ).value,
                    3,
                )
                expected_packed = (
                    struct.pack("<3I", *expected_values)
                    + bytes(expected_properties)
                )
                self.assertEqual(
                    bytes(self.snapshot[:len(expected_packed)]),
                    expected_packed,
                )

    def test_allocation_failure_is_transactional(self) -> None:
        values = [0x01020304, 0xA0B0C0D0, 0x55667788]
        properties = [0x10, 0x20, 0x30]
        self.install(values, properties, allocation_result=0)
        before_descriptor = self.descriptor_bytes()
        before_storage = bytes(self.storage)
        self.assertEqual(self.execute(0x20), 0)
        self.assertEqual(self.descriptor_bytes(), before_descriptor)
        self.assertEqual(bytes(self.storage), before_storage)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_remove_allocate_size"
            ).value,
            10,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_remove_allocate_table_before"
            ).value,
            OLD_TABLE,
        )
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_remove_allocate_count_before"
            ).value,
            3,
        )
        self.assertEqual(
            self.uint("open_cfw_test_runtime_style_remove_free_calls").value,
            0,
        )

    def test_duplicate_matches_reproduce_stock_single_decrement_quirk(
        self,
    ) -> None:
        values = [0x11111111, 0x22222222, 0x33333333, 0x44444444]
        properties = [0x31, 0x55, 0x31, 0x66]
        self.install(values, properties)
        self.assertEqual(self.execute(0x31), 1)
        self.assertEqual(self.style.count_or_static, 3)
        self.assertEqual(self.new_values(3)[:2], [values[1], values[3]])
        self.assertEqual(self.new_properties(3)[:2], [0x55, 0x66])
        self.assertEqual(
            bytes(self.storage[NEW_TABLE + 8:NEW_TABLE + 12]),
            bytes([0xCC]) * 4,
        )
        self.assertEqual(self.storage[NEW_TABLE + 14], 0xCC)

    def test_one_entry_zero_size_allocation_success_and_failure(self) -> None:
        for allocation_result, expected_result in ((NEW_TABLE, 1), (0, 0)):
            self.install([0xAABBCCDD], [0x7E], allocation_result)
            before = self.descriptor_bytes()
            self.assertEqual(self.execute(0xFFFFFF7E), expected_result)
            with self.subTest(allocation_result=allocation_result):
                self.assertEqual(
                    self.uint(
                        "open_cfw_test_runtime_style_remove_allocate_size"
                    ).value,
                    0,
                )
                if allocation_result:
                    self.assertEqual(self.style.table, NEW_TABLE)
                    self.assertEqual(self.style.count_or_static, 0)
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_style_remove_free_calls"
                        ).value,
                        1,
                    )
                else:
                    self.assertEqual(self.descriptor_bytes(), before)
                    self.assertEqual(
                        self.uint(
                            "open_cfw_test_runtime_style_remove_free_calls"
                        ).value,
                        0,
                    )

    def test_low_byte_normalization_and_randomized_oracle(self) -> None:
        generator = random.Random(STOCK_START)
        for case in range(192):
            count = generator.randrange(1, 64)
            properties = generator.sample(range(256), count)
            values = [generator.getrandbits(32) for _ in range(count)]
            removed_index = generator.randrange(count)
            normalized = properties[removed_index]
            full_property = normalized | (generator.getrandbits(24) << 8)
            self.install(values, properties)
            self.assertEqual(self.execute(full_property), 1)
            expected_values = (
                values[:removed_index] + values[removed_index + 1:]
            )
            expected_properties = (
                properties[:removed_index]
                + properties[removed_index + 1:]
            )
            with self.subTest(case=case, count=count):
                self.assertEqual(
                    self.new_values(count - 1),
                    expected_values,
                )
                self.assertEqual(
                    self.new_properties(count - 1),
                    expected_properties,
                )

    def test_maximum_mutable_count_uses_exact_packed_allocation_size(
        self,
    ) -> None:
        values = [
            (0x10203040 + index * 0x01010101) & 0xFFFFFFFF
            for index in range(254)
        ]
        properties = list(range(254))
        removed_index = 127
        self.install(values, properties)
        self.assertEqual(self.execute(properties[removed_index]), 1)
        self.assertEqual(self.style.count_or_static, 253)
        self.assertEqual(
            self.uint(
                "open_cfw_test_runtime_style_remove_allocate_size"
            ).value,
            1265,
        )
        self.assertEqual(
            self.new_values(253),
            values[:removed_index] + values[removed_index + 1:],
        )
        self.assertEqual(
            self.new_properties(253),
            properties[:removed_index] + properties[removed_index + 1:],
        )

    def test_reviewed_arm_toolchain_emits_one_predicate_relocation(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as directory:
            object_path = (
                Path(directory) / "runtime_style_remove_property.o"
            )
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

            sys.path.insert(0, str(OPENCFW_ROOT / "tools")); sys.path.insert(0, str(OPENCFW_ROOT / "tools"))
            import apollo_overlay

            data, sections = apollo_overlay.parse_elf32(object_path)
            text_section = apollo_overlay.section_named(sections, ".text")
            text_start = int(text_section["offset"])
            text_end = text_start + int(text_section["size"])
            text = data[text_start:text_end]
            relocation = apollo_overlay.section_named(
                sections,
                ".rel.text",
            )
            relocation_offset, relocation_info = struct.unpack_from(
                "<II",
                data,
                int(relocation["offset"]),
            )
            symbols = apollo_overlay.section_named(sections, ".symtab")
            symbol_index = relocation_info >> 8
            symbol_offset = (
                int(symbols["offset"])
                + symbol_index * int(symbols["entry_size"])
            )
            name_offset = struct.unpack_from(
                "<I",
                data,
                symbol_offset,
            )[0]
            strings = sections[int(symbols["link"])]
            string_data = data[
                int(strings["offset"]):
                int(strings["offset"]) + int(strings["size"])
            ]
            name_end = string_data.index(b"\0", name_offset)
            symbol_name = string_data[name_offset:name_end].decode()

        self.assertEqual(len(text), 190)
        self.assertEqual(
            hashlib.sha256(text).hexdigest(),
            "561788c8575cc43d7b710082d4f7ffad"
            "4ba2a5c6b28a028822bf712e38750f0c",
        )
        self.assertEqual(int(relocation["size"]), 8)
        self.assertEqual(relocation_offset, 0x0A)
        self.assertEqual(relocation_info & 0xFF, 10)
        self.assertEqual(
            symbol_name,
            "open_cfw_runtime_lookup_is_static",
        )

    def test_stock_bytes_dependencies_callers_and_boundaries_are_pinned(
        self,
    ) -> None:
        application = OFFICIAL.read_bytes()[32:]

        def span(start: int, end: int) -> bytes:
            return application[
                start - APPLICATION_BASE:end - APPLICATION_BASE
            ]

        preceding = span(0x0048278C, STOCK_START)
        self.assertEqual(len(preceding), 36)
        self.assertEqual(
            hashlib.sha256(preceding).hexdigest(),
            "f40bef043b38def6bcd085eba5b57ea2b"
            "07fc97e601327a25cd136150a8eb41b",
        )
        stock = span(STOCK_START, STOCK_END)
        self.assertEqual(len(stock), 184)
        self.assertEqual(
            hashlib.sha256(stock).hexdigest(),
            "7301b5de7a8104a456296a6d2b4a74e6"
            "f978ed913109aeae4d02b54865d46360",
        )
        following = span(STOCK_END, 0x00482946)
        self.assertEqual(len(following), 222)
        self.assertEqual(
            hashlib.sha256(following).hexdigest(),
            "1071391c48262cafb1f72a5bba29b3ba"
            "e4eeb52a15908faf9dee60435c214a84",
        )
        literals = {
            0x00482AB4: 0x006E8938,
            0x00482ABC: 0x0075663C,
            0x00482AC0: 0x0077943C,
        }
        for address, expected in literals.items():
            self.assertEqual(
                struct.unpack("<I", span(address, address + 4))[0],
                expected,
            )
        self.assertEqual(
            span(0x006E8938, 0x006E898B),
            (
                b"D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\"
                b"lvgl_v9.3\\LVGL\\src\\misc\\lv_style.c\0"
            ),
        )
        self.assertEqual(
            span(0x0075663C, 0x00756660),
            b"Cannot remove prop from const style\0",
        )
        self.assertEqual(
            span(0x0077943C, 0x00779451),
            b"lv_style_remove_prop\0",
        )
        allocator = span(0x0044F718, 0x0044F730)
        self.assertEqual(
            allocator.hex(),
            "80b5002801d1214805e034f0fcfd002801d10020ffe702bd",
        )
        self.assertEqual(
            hashlib.sha256(allocator).hexdigest(),
            "6f9d2c280a65a9ad8f6bd6c6d648bfe"
            "e419ffa3643ec7674109f263f67484472",
        )
        self.assertEqual(
            struct.unpack("<I", span(0x0044F7A4, 0x0044F7A8))[0],
            0x2006F5AC,
        )
        free_wrapper = span(0x0044F758, 0x0044F76A)
        self.assertEqual(
            hashlib.sha256(free_wrapper).hexdigest(),
            "f4c5f66b61c9e19b839c553e4f8173b"
            "0073543ac72c0ab57c199ff51c07f67d4",
        )
        result_consumer = span(0x0044BF76, 0x0044BF84)
        self.assertEqual(
            result_consumer.hex(),
            "36f01bfc07003800c0b201280cd1",
        )
        self.assertEqual(
            hashlib.sha256(result_consumer).hexdigest(),
            "b0b24f045b157ce8b0adcc289c2a276e"
            "88b2eb921e1b9f8c9b14b7bcce143043",
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
                    dependencies.append(
                        (address, target, encoded.hex())
                    )

        self.assertEqual(
            callers,
            [
                (0x0044BF76, "36f01bfc"),
                (0x0044CA64, "35f0a4fe"),
                (0x0044CD7A, "35f019fd"),
            ],
        )
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            dependencies,
            [
                (0x004827B8, 0x00482708, "fff7a6ff"),
                (0x004827D4, 0x0044D25C, "caf742fd"),
                (0x0048280E, 0x008847AA, "01f0ccf7"),
                (0x00482810, 0x0044F718, "ccf782ff"),
                (0x0048285C, 0x0044F758, "ccf77cff"),
            ],
        )

    def test_no_alternate_entry_and_pointer_false_positives_are_pinned(
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
                (0x0048A99D, 0x004827D0, 0x004827D1),
                (0x004BA61F, 0x004827FE, 0x004827FF),
            ],
        )

    def test_source_and_fixture_are_bounded(self) -> None:
        source = SOURCE.read_text()
        for token in (
            "open_cfw_runtime_style_remove_property(",
            "new_count * 5U",
            "style->table = new_table;",
            "style->count_or_static = (unsigned char)new_count;",
            "old_properties[source_index] != normalized_property",
            "OPEN_CFW_RUNTIME_STYLE_REMOVE_FREE(old_table);",
            "0x0044F719U",
            "0x0044F759U",
            "0x0044D25DU",
        ):
            self.assertIn(token, source)
        self.assertNotIn("#include <", source)
        self.assertIn(
            "runtime_style_remove_property.c",
            FIXTURE.read_text(),
        )


if __name__ == "__main__":
    unittest.main()
