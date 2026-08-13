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
    / "runtime_easylogger_control.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_easylogger_control_host.c"
UPSTREAM_FIXTURE = (
    ROOT / "tests" / "fixtures" / "runtime_easylogger_upstream_oracle_host.c"
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
    "set_output_enabled": (0x0043D260, 0x0043D2CE),
    "set_text_color_enabled": (0x0043D2CE, 0x0043D33C),
    "set_format": (0x0043D33C, 0x0043D3A6),
    "set_filter_level": (0x0043D3A6, 0x0043D406),
    "set_filter_tag": (0x0043D406, 0x0043D416),
    "output_lock": (0x0043D416, 0x0043D438),
    "output_unlock": (0x0043D438, 0x0043D45A),
    "output_lock_enabled": (0x0043DA24, 0x0043DA60),
}
STOCK_HASHES = {
    "set_output_enabled": (
        "34e10d7a43f9f578deadcb826f515aff9af06d607d5e79355901c74b1ce0adea"
    ),
    "set_text_color_enabled": (
        "30d6f6b942386065bbd82a097450efe06d7d50a26a71b8b12690c0a2beb3f48c"
    ),
    "set_format": (
        "819c008ba3c645a4d711ccec7eaca6cd6b573db2f27b188ae279c23f7464ea89"
    ),
    "set_filter_level": (
        "dc6524c43cb10777aa81332adc7b0e02b9f152afa4250077799308a1b951d06a"
    ),
    "set_filter_tag": (
        "9885baca1970ff465b03c64473ca6737d6e801c604eee63aac14eef5d0494218"
    ),
    "output_lock": (
        "4d87d1bcc02e66513c6774076ff4ba4c1024c5592013439d7e8dfdf53bb483b0"
    ),
    "output_unlock": (
        "86bff518c98f24bd440f5ebe4150c5d66c0e0090e844c3af3c446ab53e4799ea"
    ),
    "output_lock_enabled": (
        "7e1cf06caefa3b03995700b9fb4ff7c42ae51d056a36bac00dd47960147a5864"
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

OFFSET_FILTER_LEVEL = 0x00
OFFSET_FILTER_TAG = 0x01
OFFSET_FORMATS = 0xD8
OFFSET_OUTPUT_ENABLED = 0xF1
OFFSET_LOCK_ENABLED = 0xF2
OFFSET_LOCKED_BEFORE_ENABLE = 0xF3
OFFSET_LOCKED_BEFORE_DISABLE = 0xF4
OFFSET_TEXT_COLOR_ENABLED = 0xF5


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


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


class RuntimeEasyLoggerControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        library = temporary / (
            "runtime_easylogger_control.dylib"
            if sys.platform == "darwin"
            else "runtime_easylogger_control.so"
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
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        oracle_library = temporary / (
            "runtime_easylogger_upstream_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_easylogger_upstream_oracle.so"
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

        cls.reset = cls.loaded.open_cfw_test_easylogger_reset
        cls.reset.argtypes = []
        cls.reset.restype = None
        cls.read_u8 = cls.loaded.open_cfw_test_easylogger_read_u8
        cls.read_u8.argtypes = [ctypes.c_uint32]
        cls.read_u8.restype = ctypes.c_uint32
        cls.write_u8 = cls.loaded.open_cfw_test_easylogger_write_u8
        cls.write_u8.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.write_u8.restype = None
        cls.read_u32 = cls.loaded.open_cfw_test_easylogger_read_u32
        cls.read_u32.argtypes = [ctypes.c_uint32]
        cls.read_u32.restype = ctypes.c_uint32
        cls.assert_count = (
            cls.loaded.open_cfw_test_easylogger_get_assert_count
        )
        cls.assert_count.argtypes = []
        cls.assert_count.restype = ctypes.c_uint32
        cls.assert_line = cls.loaded.open_cfw_test_easylogger_get_assert_line
        cls.assert_line.argtypes = []
        cls.assert_line.restype = ctypes.c_uint32
        cls.assert_expression = (
            cls.loaded.open_cfw_test_easylogger_get_assert_expression
        )
        cls.assert_expression.argtypes = []
        cls.assert_expression.restype = ctypes.c_char_p
        cls.assert_function = (
            cls.loaded.open_cfw_test_easylogger_get_assert_function
        )
        cls.assert_function.argtypes = []
        cls.assert_function.restype = ctypes.c_char_p
        cls.lock_count = (
            cls.loaded.open_cfw_test_easylogger_get_port_lock_count
        )
        cls.lock_count.argtypes = []
        cls.lock_count.restype = ctypes.c_uint32
        cls.unlock_count = (
            cls.loaded.open_cfw_test_easylogger_get_port_unlock_count
        )
        cls.unlock_count.argtypes = []
        cls.unlock_count.restype = ctypes.c_uint32

        cls.set_output = (
            cls.loaded.open_cfw_easylogger_set_output_enabled
        )
        cls.set_output.argtypes = [ctypes.c_uint8]
        cls.set_output.restype = None
        cls.set_text_color = (
            cls.loaded.open_cfw_easylogger_set_text_color_enabled
        )
        cls.set_text_color.argtypes = [ctypes.c_uint8]
        cls.set_text_color.restype = None
        cls.set_format = cls.loaded.open_cfw_easylogger_set_format
        cls.set_format.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        cls.set_format.restype = None
        cls.set_filter_level = (
            cls.loaded.open_cfw_easylogger_set_filter_level
        )
        cls.set_filter_level.argtypes = [ctypes.c_uint8]
        cls.set_filter_level.restype = None
        cls.set_filter_tag = cls.loaded.open_cfw_easylogger_set_filter_tag
        cls.set_filter_tag.argtypes = [ctypes.c_char_p]
        cls.set_filter_tag.restype = None
        cls.output_lock = cls.loaded.open_cfw_easylogger_output_lock
        cls.output_lock.argtypes = []
        cls.output_lock.restype = None
        cls.output_unlock = cls.loaded.open_cfw_easylogger_output_unlock
        cls.output_unlock.argtypes = []
        cls.output_unlock.restype = None
        cls.lock_enabled = (
            cls.loaded.open_cfw_easylogger_output_lock_enabled
        )
        cls.lock_enabled.argtypes = [ctypes.c_uint8]
        cls.lock_enabled.restype = None

        cls.oracle_reset = cls.oracle.open_cfw_oracle_reset
        cls.oracle_reset.argtypes = []
        cls.oracle_reset.restype = None
        cls.oracle_read_u8 = cls.oracle.open_cfw_oracle_read_u8
        cls.oracle_read_u8.argtypes = [ctypes.c_uint32]
        cls.oracle_read_u8.restype = ctypes.c_uint32
        cls.oracle_read_u32 = cls.oracle.open_cfw_oracle_read_u32
        cls.oracle_read_u32.argtypes = [ctypes.c_uint32]
        cls.oracle_read_u32.restype = ctypes.c_uint32
        cls.oracle_filter_level = (
            cls.oracle.open_cfw_oracle_get_filter_level
        )
        cls.oracle_filter_level.argtypes = []
        cls.oracle_filter_level.restype = ctypes.c_uint32
        cls.oracle_filter_tag_byte = (
            cls.oracle.open_cfw_oracle_get_filter_tag_byte
        )
        cls.oracle_filter_tag_byte.argtypes = [ctypes.c_uint32]
        cls.oracle_filter_tag_byte.restype = ctypes.c_uint32
        cls.oracle_format = cls.oracle.open_cfw_oracle_get_format
        cls.oracle_format.argtypes = [ctypes.c_uint32]
        cls.oracle_format.restype = ctypes.c_uint32
        cls.oracle_output_enabled = (
            cls.oracle.open_cfw_oracle_get_output_enabled
        )
        cls.oracle_output_enabled.argtypes = []
        cls.oracle_output_enabled.restype = ctypes.c_uint32
        cls.oracle_lock_enabled_state = (
            cls.oracle.open_cfw_oracle_get_lock_enabled
        )
        cls.oracle_lock_enabled_state.argtypes = []
        cls.oracle_lock_enabled_state.restype = ctypes.c_uint32
        cls.oracle_locked_before_enable = (
            cls.oracle.open_cfw_oracle_get_locked_before_enable
        )
        cls.oracle_locked_before_enable.argtypes = []
        cls.oracle_locked_before_enable.restype = ctypes.c_uint32
        cls.oracle_locked_before_disable = (
            cls.oracle.open_cfw_oracle_get_locked_before_disable
        )
        cls.oracle_locked_before_disable.argtypes = []
        cls.oracle_locked_before_disable.restype = ctypes.c_uint32
        cls.oracle_text_color_enabled = (
            cls.oracle.open_cfw_oracle_get_text_color_enabled
        )
        cls.oracle_text_color_enabled.argtypes = []
        cls.oracle_text_color_enabled.restype = ctypes.c_uint32
        cls.oracle_write_u8 = cls.oracle.open_cfw_oracle_write_u8
        cls.oracle_write_u8.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.oracle_write_u8.restype = None
        cls.oracle_assert_count = (
            cls.oracle.open_cfw_oracle_get_assert_count
        )
        cls.oracle_assert_count.argtypes = []
        cls.oracle_assert_count.restype = ctypes.c_uint32
        cls.oracle_lock_count = cls.oracle.open_cfw_oracle_get_lock_count
        cls.oracle_lock_count.argtypes = []
        cls.oracle_lock_count.restype = ctypes.c_uint32
        cls.oracle_unlock_count = (
            cls.oracle.open_cfw_oracle_get_unlock_count
        )
        cls.oracle_unlock_count.argtypes = []
        cls.oracle_unlock_count.restype = ctypes.c_uint32
        cls.oracle_set_output = cls.oracle.elog_set_output_enabled
        cls.oracle_set_output.argtypes = [ctypes.c_uint8]
        cls.oracle_set_output.restype = None
        cls.oracle_set_text_color = (
            cls.oracle.elog_set_text_color_enabled
        )
        cls.oracle_set_text_color.argtypes = [ctypes.c_uint8]
        cls.oracle_set_text_color.restype = None
        cls.oracle_set_format = cls.oracle.elog_set_fmt
        cls.oracle_set_format.argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        cls.oracle_set_format.restype = None
        cls.oracle_set_filter_level = cls.oracle.elog_set_filter_lvl
        cls.oracle_set_filter_level.argtypes = [ctypes.c_uint8]
        cls.oracle_set_filter_level.restype = None
        cls.oracle_set_filter_tag = cls.oracle.elog_set_filter_tag
        cls.oracle_set_filter_tag.argtypes = [ctypes.c_char_p]
        cls.oracle_set_filter_tag.restype = None
        cls.oracle_output_lock = cls.oracle.elog_output_lock
        cls.oracle_output_lock.argtypes = []
        cls.oracle_output_lock.restype = None
        cls.oracle_output_unlock = cls.oracle.elog_output_unlock
        cls.oracle_output_unlock.argtypes = []
        cls.oracle_output_unlock.restype = None
        cls.oracle_lock_enabled = cls.oracle.elog_output_lock_enabled
        cls.oracle_lock_enabled.argtypes = [ctypes.c_uint8]
        cls.oracle_lock_enabled.restype = None

        cls.target_object = temporary / "runtime_easylogger_control.o"
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

        (
            cls.target_overlay,
            cls.target_functions,
            cls.target_link_report,
        ) = apollo_overlay.extract_linked_overlay(cls.target_object)
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

    def test_recovered_object_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(EasyLoggerTagLevel32), 0x21)
        self.assertEqual(ctypes.sizeof(EasyLoggerFilter32), 0xD6)
        self.assertEqual(ctypes.sizeof(EasyLogger32), 0xF8)
        self.assertEqual(EasyLogger32.enabled_format_set.offset, 0xD8)
        self.assertEqual(EasyLogger32.init_ok.offset, 0xF0)
        self.assertEqual(EasyLogger32.output_enabled.offset, 0xF1)
        self.assertEqual(EasyLogger32.output_lock_enabled.offset, 0xF2)
        self.assertEqual(
            EasyLogger32.output_is_locked_before_enable.offset,
            0xF3,
        )
        self.assertEqual(
            EasyLogger32.output_is_locked_before_disable.offset,
            0xF4,
        )
        self.assertEqual(EasyLogger32.text_color_enabled.offset, 0xF5)

    def test_stock_boundaries_and_hashes_are_exact(self) -> None:
        for name, (start, end) in FUNCTIONS.items():
            body = self.span(start, end)
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_HASHES[name])

    def test_control_setters_update_recovered_fields(self) -> None:
        self.set_output(1)
        self.set_text_color(1)
        self.set_format(4, 0x87)
        self.set_filter_level(3)
        self.assertEqual(self.read_u8(OFFSET_OUTPUT_ENABLED), 1)
        self.assertEqual(self.read_u8(OFFSET_TEXT_COLOR_ENABLED), 1)
        self.assertEqual(self.read_u32(OFFSET_FORMATS + 4 * 4), 0x87)
        self.assertEqual(self.read_u8(OFFSET_FILTER_LEVEL), 3)
        self.assertEqual(self.assert_count(), 0)

    def test_control_sequence_matches_pristine_upstream_oracle(self) -> None:
        self.set_output(1)
        self.oracle_set_output(1)
        self.set_text_color(1)
        self.oracle_set_text_color(1)
        for level, format_set in enumerate(
            (0xFF, 0x87, 0x87, 0x87, 0x87, 0x87)
        ):
            self.set_format(level, format_set)
            self.oracle_set_format(level, format_set)
        self.set_filter_level(3)
        self.oracle_set_filter_level(3)
        self.set_filter_tag(b"apollo-main")
        self.oracle_set_filter_tag(b"apollo-main")

        self.assertEqual(
            self.read_u8(OFFSET_OUTPUT_ENABLED),
            self.oracle_output_enabled(),
        )
        self.assertEqual(
            self.read_u8(OFFSET_TEXT_COLOR_ENABLED),
            self.oracle_text_color_enabled(),
        )
        self.assertEqual(
            self.read_u8(OFFSET_FILTER_LEVEL),
            self.oracle_filter_level(),
        )
        self.assertEqual(
            [self.read_u32(OFFSET_FORMATS + level * 4) for level in range(6)],
            [self.oracle_format(level) for level in range(6)],
        )
        self.assertEqual(
            [self.read_u8(OFFSET_FILTER_TAG + index) for index in range(31)],
            [self.oracle_filter_tag_byte(index) for index in range(31)],
        )

    def test_lock_state_machine_matches_pristine_upstream_oracle(self) -> None:
        operations = (
            (self.output_lock, self.oracle_output_lock),
            (self.output_unlock, self.oracle_output_unlock),
            (lambda: self.lock_enabled(1), lambda: self.oracle_lock_enabled(1)),
            (self.output_lock, self.oracle_output_lock),
            (self.output_unlock, self.oracle_output_unlock),
            (lambda: self.lock_enabled(0), lambda: self.oracle_lock_enabled(0)),
            (self.output_lock, self.oracle_output_lock),
            (lambda: self.lock_enabled(1), lambda: self.oracle_lock_enabled(1)),
        )
        for candidate, oracle in operations:
            candidate()
            oracle()
            self.assertEqual(
                self.read_u8(OFFSET_LOCK_ENABLED),
                self.oracle_lock_enabled_state(),
            )
            self.assertEqual(
                self.read_u8(OFFSET_LOCKED_BEFORE_ENABLE),
                self.oracle_locked_before_enable(),
            )
            self.assertEqual(
                self.read_u8(OFFSET_LOCKED_BEFORE_DISABLE),
                self.oracle_locked_before_disable(),
            )
            self.assertEqual(self.lock_count(), self.oracle_lock_count())
            self.assertEqual(self.unlock_count(), self.oracle_unlock_count())

    def test_recovered_default_format_masks_are_accepted(self) -> None:
        self.set_format(0, 0xFF)
        for level in range(1, 6):
            self.set_format(level, 0x87)
        self.assertEqual(self.read_u32(OFFSET_FORMATS), 0xFF)
        self.assertEqual(
            [self.read_u32(OFFSET_FORMATS + level * 4) for level in range(1, 6)],
            [0x87] * 5,
        )

    def test_assert_hook_arguments_and_continue_behavior_match_upstream(self) -> None:
        cases = [
            (
                lambda: self.set_output(2),
                OFFSET_OUTPUT_ENABLED,
                2,
                b"(enabled == false) || (enabled == true)",
                b"elog_set_output_enabled",
                278,
            ),
            (
                lambda: self.set_text_color(2),
                OFFSET_TEXT_COLOR_ENABLED,
                2,
                b"(enabled == false) || (enabled == true)",
                b"elog_set_text_color_enabled",
                290,
            ),
            (
                lambda: self.set_format(6, 0xA5A5A5A5),
                OFFSET_FORMATS + 6 * 4,
                0xA5A5A5A5,
                b"level <= ELOG_LVL_VERBOSE",
                b"elog_set_fmt",
                321,
            ),
            (
                lambda: self.set_filter_level(6),
                OFFSET_FILTER_LEVEL,
                6,
                b"level <= ELOG_LVL_VERBOSE",
                b"elog_set_filter_lvl",
                347,
            ),
        ]
        for invoke, offset, value, expression, function, line in cases:
            with self.subTest(function=function):
                self.reset()
                invoke()
                self.assertEqual(self.assert_count(), 1)
                self.assertEqual(self.assert_expression(), expression)
                self.assertEqual(self.assert_function(), function)
                self.assertEqual(self.assert_line(), line)
                if value <= 0xFF:
                    self.assertEqual(self.read_u8(offset), value)
                else:
                    self.assertEqual(self.read_u32(offset), value)

    def test_filter_tag_preserves_upstream_bounded_copy_semantics(self) -> None:
        self.write_u8(OFFSET_FILTER_TAG + 30, ord("!"))
        self.set_filter_tag(b"abcdefghijklmnopqrstuvwxyz0123456789")
        copied = bytes(
            self.read_u8(OFFSET_FILTER_TAG + index)
            for index in range(31)
        )
        self.assertEqual(copied[:30], b"abcdefghijklmnopqrstuvwxyz0123")
        self.assertEqual(copied[30], ord("!"))

    def test_output_lock_and_unlock_preserve_state_machine(self) -> None:
        self.output_lock()
        self.assertEqual(self.read_u8(OFFSET_LOCKED_BEFORE_ENABLE), 1)
        self.assertEqual((self.lock_count(), self.unlock_count()), (0, 0))
        self.output_unlock()
        self.assertEqual(self.read_u8(OFFSET_LOCKED_BEFORE_ENABLE), 0)

        self.write_u8(OFFSET_LOCK_ENABLED, 1)
        self.output_lock()
        self.assertEqual(self.read_u8(OFFSET_LOCKED_BEFORE_DISABLE), 1)
        self.assertEqual((self.lock_count(), self.unlock_count()), (1, 0))
        self.output_unlock()
        self.assertEqual(self.read_u8(OFFSET_LOCKED_BEFORE_DISABLE), 0)
        self.assertEqual((self.lock_count(), self.unlock_count()), (1, 1))

    def test_lock_enable_reconciles_deferred_transition_once(self) -> None:
        self.write_u8(OFFSET_LOCKED_BEFORE_ENABLE, 1)
        self.lock_enabled(1)
        self.assertEqual(self.read_u8(OFFSET_LOCK_ENABLED), 1)
        self.assertEqual((self.lock_count(), self.unlock_count()), (1, 0))

        self.reset()
        self.write_u8(OFFSET_LOCKED_BEFORE_DISABLE, 1)
        self.lock_enabled(1)
        self.assertEqual((self.lock_count(), self.unlock_count()), (0, 1))

        self.reset()
        self.write_u8(OFFSET_LOCKED_BEFORE_ENABLE, 1)
        self.lock_enabled(0)
        self.assertEqual(self.read_u8(OFFSET_LOCK_ENABLED), 0)
        self.assertEqual((self.lock_count(), self.unlock_count()), (0, 0))

    @_APPLE_ONLY
    def test_target_object_has_only_candidate_functions_and_no_undefined_seams(
        self,
    ) -> None:
        expected = {
            "open_cfw_easylogger_set_output_enabled": {
                "offset": 0,
                "size": 152,
            },
            "open_cfw_easylogger_set_text_color_enabled": {
                "offset": 152,
                "size": 152,
            },
            "open_cfw_easylogger_set_format": {
                "offset": 304,
                "size": 160,
            },
            "open_cfw_easylogger_set_filter_level": {
                "offset": 464,
                "size": 152,
            },
            "open_cfw_easylogger_set_filter_tag": {
                "offset": 616,
                "size": 22,
            },
            "open_cfw_easylogger_output_lock": {
                "offset": 640,
                "size": 36,
            },
            "open_cfw_easylogger_output_unlock": {
                "offset": 676,
                "size": 36,
            },
            "open_cfw_easylogger_output_lock_enabled": {
                "offset": 712,
                "size": 50,
            },
        }
        observed = {
            name
            for name, fields in self.symbols.items()
            if fields[3] & 0x0F == 2
        }
        self.assertEqual(observed, set(expected))
        self.assertEqual(self.target_functions, expected)
        self.assertEqual(len(self.target_overlay), 952)
        self.assertEqual(
            hashlib.sha256(self.target_overlay).hexdigest(),
            "46fec4899d5c2652466284cdc037743d069a09673b8fe4bcce8e4b4abcbf0fb9",
        )
        self.assertEqual(self.target_link_report["text_size"], 762)
        self.assertEqual(self.target_link_report["rodata_size"], 190)
        self.assertEqual(
            self.target_link_report["resolved_relocation_count"],
            48,
        )
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )
        self.assertTrue(
            all(self.symbols[name][1] & 1 for name in expected)
        )
        self.assertEqual(len(self.target_text_relocations), 48)
        self.assertEqual(
            {relocation_type for _, relocation_type, _ in self.target_text_relocations},
            {49, 50},
        )
        self.assertTrue(
            all(
                symbol.startswith(".L.str")
                for _, _, symbol in self.target_text_relocations
            )
        )

    def test_source_pins_upstream_and_stock_seams(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "4b310d835604b409dec3d404b7fcd48d28839a9b2807aef339549a7563d39bbe",
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
            "0x0044B5A1U",
            "0x0044AA99U",
            "0x0044AAA1U",
        ):
            self.assertIn(literal, source)


if __name__ == "__main__":
    unittest.main()
