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


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_easylogger_filter.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_easylogger_filter_host.c"
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_easylogger_filter_upstream_oracle_host.c"
)
UPSTREAM_INCLUDE = ROOT / "third_party" / "easylogger" / "inc"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
FUNCTIONS = {
    "filter_tag_levels_reset": (0x0043D45A, 0x0043D4B0),
    "get_filter_tag_level": (0x0043D4B0, 0x0043D574),
}
STOCK_HASHES = {
    "filter_tag_levels_reset": (
        "7f77794d5e81ef5fe375f98e37f63520f20f4538f7187ca90036769087582c36"
    ),
    "get_filter_tag_level": (
        "53770f37005d894be731529ef8bdcaa2588f2f7917239b3feb18bb59cf5a9c17"
    ),
}
TARGET_FLAGS = [
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
]

OFFSET_TAG_LEVELS = 0x31
TAG_LEVEL_SIZE = 0x21
OFFSET_TAG_LEVEL = 0x00
OFFSET_TAG = 0x01
OFFSET_TAG_USE = 0x20
OFFSET_INIT_OK = 0xF0


class EasyLoggerTagLevel32(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("tag", ctypes.c_char * 31),
        ("tag_use_flag", ctypes.c_uint8),
    ]


class EasyLoggerFilter32(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("tag", ctypes.c_char * 31),
        ("keyword", ctypes.c_char * 17),
        ("tag_level", EasyLoggerTagLevel32 * 5),
    ]


class EasyLogger32(ctypes.Structure):
    _fields_ = [
        ("filter", EasyLoggerFilter32),
        ("enabled_format_set", ctypes.c_uint32 * 6),
        ("init_ok", ctypes.c_uint8),
        ("output_enabled", ctypes.c_uint8),
        ("output_lock_enabled", ctypes.c_uint8),
        ("output_is_locked_before_enable", ctypes.c_uint8),
        ("output_is_locked_before_disable", ctypes.c_uint8),
        ("text_color_enabled", ctypes.c_uint8),
    ]


class RuntimeEasyLoggerFilterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_easylogger_filter.dylib"
            if sys.platform == "darwin"
            else "runtime_easylogger_filter.so"
        )
        host_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))

        oracle_library = temporary / (
            "runtime_easylogger_filter_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_easylogger_filter_oracle.so"
        )
        oracle_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(UPSTREAM_INCLUDE),
            str(UPSTREAM_FIXTURE),
        ]
        if sys.platform == "darwin":
            oracle_command.extend(["-dynamiclib", "-o", str(oracle_library)])
        else:
            oracle_command.extend(
                ["-shared", "-fPIC", "-o", str(oracle_library)]
            )
        subprocess.run(
            oracle_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.oracle = ctypes.CDLL(str(oracle_library))

        cls.reset = cls.loaded.open_cfw_test_easylogger_filter_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.read_u8 = cls.loaded.open_cfw_test_easylogger_filter_read_u8
        cls.read_u8.argtypes = [ctypes.c_uint32]
        cls.read_u8.restype = ctypes.c_uint32
        cls.write_u8 = cls.loaded.open_cfw_test_easylogger_filter_write_u8
        cls.write_u8.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.write_u8.restype = None
        cls.reset_levels = (
            cls.loaded.open_cfw_easylogger_filter_tag_levels_reset
        )
        cls.reset_levels.argtypes = []
        cls.reset_levels.restype = None
        cls.get_level = (
            cls.loaded.open_cfw_easylogger_get_filter_tag_level
        )
        cls.get_level.argtypes = [ctypes.c_char_p]
        cls.get_level.restype = ctypes.c_uint8
        cls.assert_count = (
            cls.loaded.open_cfw_test_easylogger_filter_get_assert_count
        )
        cls.assert_count.argtypes = []
        cls.assert_count.restype = ctypes.c_uint32
        cls.assert_line = (
            cls.loaded.open_cfw_test_easylogger_filter_get_assert_line
        )
        cls.assert_line.argtypes = []
        cls.assert_line.restype = ctypes.c_uint32
        cls.assert_expression = (
            cls.loaded.open_cfw_test_easylogger_filter_get_assert_expression
        )
        cls.assert_expression.argtypes = []
        cls.assert_expression.restype = ctypes.c_char_p
        cls.assert_function = (
            cls.loaded.open_cfw_test_easylogger_filter_get_assert_function
        )
        cls.assert_function.argtypes = []
        cls.assert_function.restype = ctypes.c_char_p
        cls.lock_count = (
            cls.loaded.open_cfw_test_easylogger_filter_get_lock_count
        )
        cls.lock_count.argtypes = []
        cls.lock_count.restype = ctypes.c_uint32
        cls.unlock_count = (
            cls.loaded.open_cfw_test_easylogger_filter_get_unlock_count
        )
        cls.unlock_count.argtypes = []
        cls.unlock_count.restype = ctypes.c_uint32
        cls.event = cls.loaded.open_cfw_test_easylogger_filter_get_event
        cls.event.argtypes = [ctypes.c_uint32]
        cls.event.restype = ctypes.c_uint32

        cls.oracle_reset = (
            cls.oracle.open_cfw_oracle_easylogger_filter_reset
        )
        cls.oracle_reset.argtypes = []
        cls.oracle_reset.restype = None
        cls.oracle_defaults = (
            cls.oracle.open_cfw_oracle_easylogger_filter_defaults
        )
        cls.oracle_defaults.argtypes = []
        cls.oracle_defaults.restype = None
        cls.oracle_read_u8 = (
            cls.oracle.open_cfw_oracle_easylogger_filter_read_u8
        )
        cls.oracle_read_u8.argtypes = [ctypes.c_uint32]
        cls.oracle_read_u8.restype = ctypes.c_uint32
        cls.oracle_write_u8 = (
            cls.oracle.open_cfw_oracle_easylogger_filter_write_u8
        )
        cls.oracle_write_u8.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.oracle_write_u8.restype = None
        cls.oracle_set_init = (
            cls.oracle.open_cfw_oracle_easylogger_filter_set_init
        )
        cls.oracle_set_init.argtypes = [ctypes.c_uint32]
        cls.oracle_set_init.restype = None
        cls.oracle_get_level = cls.oracle.elog_get_filter_tag_lvl
        cls.oracle_get_level.argtypes = [ctypes.c_char_p]
        cls.oracle_get_level.restype = ctypes.c_uint8
        cls.oracle_lock_count = (
            cls.oracle.open_cfw_oracle_easylogger_filter_get_lock_count
        )
        cls.oracle_lock_count.argtypes = []
        cls.oracle_lock_count.restype = ctypes.c_uint32
        cls.oracle_unlock_count = (
            cls.oracle.open_cfw_oracle_easylogger_filter_get_unlock_count
        )
        cls.oracle_unlock_count.argtypes = []
        cls.oracle_unlock_count.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_easylogger_filter.o"
        subprocess.run(
            [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                *TARGET_FLAGS,
                "-c",
                str(SOURCE),
                "-o",
                str(cls.target_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.target_text_relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.target_text_relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def setUp(self) -> None:
        self.reset()
        self.oracle_reset()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    @staticmethod
    def slot_offset(slot: int, field: int = 0) -> int:
        return OFFSET_TAG_LEVELS + slot * TAG_LEVEL_SIZE + field

    def write_both(self, offset: int, value: int) -> None:
        self.write_u8(offset, value)
        self.oracle_write_u8(offset, value)

    def set_init_both(self, value: int) -> None:
        self.write_u8(OFFSET_INIT_OK, value)
        self.oracle_set_init(value)

    def write_slot(
        self,
        slot: int,
        tag: bytes,
        level: int,
        used: int = 1,
    ) -> None:
        self.write_both(self.slot_offset(slot, OFFSET_TAG_LEVEL), level)
        for index in range(31):
            value = tag[index] if index < len(tag) else 0
            self.write_both(self.slot_offset(slot, OFFSET_TAG + index), value)
        self.write_both(self.slot_offset(slot, OFFSET_TAG_USE), used)

    def test_recovered_object_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(EasyLoggerTagLevel32), 0x21)
        self.assertEqual(ctypes.sizeof(EasyLoggerFilter32), 0xD6)
        self.assertEqual(ctypes.sizeof(EasyLogger32), 0xF8)
        self.assertEqual(EasyLoggerFilter32.tag_level.offset, 0x31)
        self.assertEqual(EasyLogger32.init_ok.offset, 0xF0)

    def test_stock_boundaries_and_hashes_are_exact(self) -> None:
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_HASHES[name])

    def test_reset_matches_pristine_upstream_byte_for_byte(self) -> None:
        for slot in range(5):
            self.write_slot(
                slot,
                bytes((slot + index + 1) & 0xFF for index in range(31)),
                slot + 1,
                1,
            )
        self.reset_levels()
        self.oracle_defaults()
        for offset in range(OFFSET_TAG_LEVELS, 0xD6):
            self.assertEqual(self.read_u8(offset), self.oracle_read_u8(offset))
        for slot in range(5):
            self.assertEqual(
                self.read_u8(self.slot_offset(slot, OFFSET_TAG_LEVEL)),
                0,
            )
            self.assertEqual(
                self.read_u8(self.slot_offset(slot, OFFSET_TAG_USE)),
                0,
            )
            self.assertEqual(
                [
                    self.read_u8(self.slot_offset(slot, OFFSET_TAG + index))
                    for index in range(31)
                ],
                [0] * 31,
            )

    def test_getter_matches_upstream_for_match_miss_and_disabled_slot(
        self,
    ) -> None:
        self.set_init_both(1)
        self.write_slot(0, b"ignored", 1, 0)
        self.write_slot(1, b"apollo-main", 3, 1)
        self.write_slot(2, b"display", 4, 1)
        for tag in (b"ignored", b"apollo-main", b"display", b"missing"):
            with self.subTest(tag=tag):
                self.assertEqual(
                    self.get_level(tag),
                    self.oracle_get_level(tag),
                )
        self.assertEqual(self.get_level(b"ignored"), 5)
        self.assertEqual(self.get_level(b"apollo-main"), 3)
        self.assertEqual(self.get_level(b"display"), 4)
        self.assertEqual(self.get_level(b"missing"), 5)

    def test_getter_preserves_first_match_and_30_byte_bound(self) -> None:
        prefix = b"abcdefghijklmnopqrstuvwxyz0123"
        self.assertEqual(len(prefix), 30)
        self.set_init_both(1)
        self.write_slot(0, prefix + b"A", 2)
        self.write_slot(1, prefix + b"B", 4)
        query = prefix + b"different-after-the-bound"
        self.assertEqual(self.get_level(query), self.oracle_get_level(query))
        self.assertEqual(self.get_level(query), 2)

    def test_uninitialized_getter_returns_all_without_locking(self) -> None:
        self.write_slot(0, b"apollo-main", 2)
        self.assertEqual(self.get_level(b"apollo-main"), 5)
        self.assertEqual(self.oracle_get_level(b"apollo-main"), 5)
        self.assertEqual((self.lock_count(), self.unlock_count()), (0, 0))
        self.assertEqual(
            (self.oracle_lock_count(), self.oracle_unlock_count()),
            (0, 0),
        )

    def test_initialized_getter_locks_and_unlocks_exactly_once(self) -> None:
        self.set_init_both(1)
        self.write_slot(4, b"transport", 1)
        self.assertEqual(self.get_level(b"transport"), 1)
        self.assertEqual((self.lock_count(), self.unlock_count()), (1, 1))
        self.assertEqual([self.event(0), self.event(1)], [1, 2])

    def test_null_tag_assertion_uses_recovered_g2_metadata(self) -> None:
        self.assertEqual(self.get_level(None), 5)
        self.assertEqual(self.assert_count(), 1)
        self.assertEqual(self.assert_expression(), b"tag != ((void *)0)")
        self.assertEqual(self.assert_function(), b"elog_get_filter_tag_lvl")
        self.assertEqual(self.assert_line(), 481)
        self.assertEqual((self.lock_count(), self.unlock_count()), (0, 0))

    def test_stock_branch_and_pointer_topology_is_exact(self) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        expected_callers = {
            "filter_tag_levels_reset": [0x0043D18A],
            "get_filter_tag_level": [0x0043D600],
        }
        for name, (start, end) in FUNCTIONS.items():
            callers = []
            jumps = []
            interior = []
            for offset in range(0, len(self.application) - 3, 2):
                address = BASE + offset
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
                    if target == start:
                        observed.append(address)
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        interior.append((address, target, link))
            self.assertEqual(callers, expected_callers[name])
            self.assertEqual(jumps, [])
            self.assertEqual(interior, [])

            stored = []
            for offset in range(0, len(self.application) - 3):
                value = struct.unpack_from(
                    "<I",
                    self.application,
                    offset,
                )[0]
                target = value & ~1
                if value & 1 and start <= target < end:
                    stored.append((BASE + offset, target))
            self.assertEqual(stored, [])

    def test_target_object_is_bounded_to_source_and_lock_dependencies(
        self,
    ) -> None:
        expected_functions = {
            "open_cfw_easylogger_filter_tag_levels_reset": (1, 90),
            "open_cfw_easylogger_get_filter_tag_level": (161, 284),
            "open_cfw_easylogger_filter_zero_tag": (93, 66),
            "open_cfw_easylogger_filter_tags_equal": (445, 258),
        }
        observed_functions = {
            name: (fields[1], fields[2])
            for name, fields in self.symbols.items()
            if fields[3] & 0x0F == 2 and fields[5] != 0
        }
        self.assertEqual(observed_functions, expected_functions)
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [
                "open_cfw_easylogger_output_lock",
                "open_cfw_easylogger_output_unlock",
            ],
        )
        self.assertEqual(len(self.target_text_relocations), 14)
        self.assertEqual(
            [
                (relocation_type, symbol)
                for _, relocation_type, symbol in self.target_text_relocations
                if relocation_type == 10
            ],
            [
                (10, "open_cfw_easylogger_output_lock"),
                (10, "open_cfw_easylogger_output_unlock"),
            ],
        )
        self.assertEqual(
            {
                relocation_type
                for _, relocation_type, _ in self.target_text_relocations
            },
            {10, 49, 50},
        )

    def test_source_pins_upstream_and_only_recovered_fixed_seams(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "ee87cf6742b4df9cc190e205c46326ad2269cf9f9f2c6ee0e97cb518e7916624",
        )
        self.assertIn(
            "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            source,
        )
        for literal in (
            "0x20070BE8U",
            "0x2007456CU",
            "0x0043D575U",
            "0x0044B0AFU",
            "0x006E3098U",
        ):
            self.assertIn(literal, source)
        for replaced_library_seam in ("0x0043C0E4U", "0x0044B611U"):
            self.assertNotIn(replaced_library_seam, source)


if __name__ == "__main__":
    unittest.main()
