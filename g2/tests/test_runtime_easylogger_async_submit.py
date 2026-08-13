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
    / "runtime_easylogger_async_submit.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_easylogger_async_submit_host.c"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
START = 0x0044AA80
END = 0x0044AA98
STOCK_SHA256 = (
    "787d13cfe59fad83061379298387393fa"
    "94266c9b31420e7f67e8e07d63f7356"
)
CALLER = 0x0043D968
BUILDER = 0x00448D4E
EVENT_SET = 0x004495E4
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


class RuntimeEasyLoggerAsyncSubmitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        library = temporary / (
            "runtime_easylogger_async_submit.dylib"
            if sys.platform == "darwin"
            else "runtime_easylogger_async_submit.so"
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
            host_command.extend(
                ["-shared", "-fPIC", "-o", str(library)]
            )
        subprocess.run(
            host_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))

        cls.reset = cls.loaded.open_cfw_test_easylogger_async_reset
        cls.reset.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.reset.restype = None
        cls.mutate_handle = (
            cls.loaded.open_cfw_test_easylogger_async_set_build_handle_mutation
        )
        cls.mutate_handle.argtypes = [ctypes.c_void_p]
        cls.mutate_handle.restype = None
        cls.submit = cls.loaded.open_cfw_g2_easylogger_async_submit
        cls.submit.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.submit.restype = None

        cls.target_object = (
            temporary / "runtime_easylogger_async_submit.o"
        )
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

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(cls.target_object)
        text = apollo_overlay.section_named(sections, ".text")
        cls.target_text = data[
            int(text["offset"]):
            int(text["offset"]) + int(text["size"])
        ]
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
            name = apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.target_relocations = []
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
                    cls.target_relocations.append(
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
        self.reset(0x11223344, 0xA5A5A5A5, 0x5A5A5A5A)

    def value(self, name: str) -> int:
        return ctypes.c_uint32.in_dll(self.loaded, name).value

    def pointer_value(self, name: str) -> int:
        return ctypes.c_size_t.in_dll(self.loaded, name).value

    def events(self) -> list[int]:
        count = self.value("open_cfw_test_easylogger_async_event_count")
        values = (ctypes.c_uint32 * 4).in_dll(
            self.loaded,
            "open_cfw_test_easylogger_async_events",
        )
        return list(values[:count])

    def test_forwards_exact_private_builder_abi_then_notifies(self) -> None:
        message = ctypes.create_string_buffer(b"apollo-main")
        pointer = ctypes.addressof(message)

        self.submit(pointer, 0x10203040, 0x123456AB)

        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_calls"),
            1,
        )
        self.assertEqual(
            self.pointer_value(
                "open_cfw_test_easylogger_async_build_buffer"
            ),
            pointer,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_length"),
            0x10203040,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_metadata"),
            0,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_level"),
            0xAB,
        )
        self.assertEqual(
            self.pointer_value("open_cfw_test_easylogger_async_set_handle"),
            0x11223344,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_set_flags"),
            1,
        )
        self.assertEqual(self.events(), [1, 2])

    def test_builder_and_event_results_are_ignored(self) -> None:
        for build_result, set_result in (
            (0, 0),
            (0xFFFFFFFF, 0x80000000),
            (0x12345678, 0x87654321),
        ):
            with self.subTest(
                build_result=build_result,
                set_result=set_result,
            ):
                self.reset(0x10203040, build_result, set_result)
                self.submit(0x50607080, 17, 4)
                self.assertEqual(
                    self.value(
                        "open_cfw_test_easylogger_async_build_calls"
                    ),
                    1,
                )
                self.assertEqual(
                    self.value("open_cfw_test_easylogger_async_set_calls"),
                    1,
                )
                self.assertEqual(self.events(), [1, 2])

    def test_notification_is_unconditional_for_rejected_input(self) -> None:
        self.reset(None, 0, 0xFFFFFFFF)

        self.submit(None, 0, 0xFFFFFFFF)

        self.assertEqual(
            self.pointer_value(
                "open_cfw_test_easylogger_async_build_buffer"
            ),
            0,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_length"),
            0,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_build_level"),
            0xFF,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_set_calls"),
            1,
        )
        self.assertEqual(
            self.pointer_value("open_cfw_test_easylogger_async_set_handle"),
            0,
        )
        self.assertEqual(
            self.value("open_cfw_test_easylogger_async_set_flags"),
            1,
        )

    def test_event_handle_is_loaded_after_builder_returns(self) -> None:
        self.mutate_handle(0x55667788)

        self.submit(0x1234, 1, 2)

        self.assertEqual(
            self.pointer_value("open_cfw_test_easylogger_async_set_handle"),
            0x55667788,
        )
        self.assertEqual(self.events(), [1, 2])

    @staticmethod
    def decode_wide_branch(
        application: bytes,
        address: int,
        *,
        link: bool,
    ) -> int | None:
        offset = address - BASE
        first, second = struct.unpack_from("<HH", application, offset)
        if first & 0xF800 != 0xF000:
            return None
        if second & 0xD000 != (0xD000 if link else 0x9000):
            return None
        sign = (first >> 10) & 1
        immediate_10 = first & 0x03FF
        j1 = (second >> 13) & 1
        j2 = (second >> 11) & 1
        immediate_11 = second & 0x07FF
        i1 = (~(j1 ^ sign)) & 1
        i2 = (~(j2 ^ sign)) & 1
        immediate = (
            sign << 24
            | i1 << 23
            | i2 << 22
            | immediate_10 << 12
            | immediate_11 << 1
        )
        if sign != 0:
            immediate -= 1 << 25
        return address + 4 + immediate

    def test_stock_body_hash_boundary_and_dependencies_are_exact(
        self,
    ) -> None:
        body = self.application[START - BASE:END - BASE]
        self.assertEqual(len(body), 24)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            body.hex(),
            "80b51300dbb20022fef761f901211d480068fef7a7fd01bd",
        )
        self.assertEqual(
            self.decode_wide_branch(
                self.application,
                0x0044AA88,
                link=True,
            ),
            BUILDER,
        )
        self.assertEqual(
            self.decode_wide_branch(
                self.application,
                0x0044AA92,
                link=True,
            ),
            EVENT_SET,
        )
        literal = struct.unpack_from(
            "<I",
            self.application,
            0x0044AB04 - BASE,
        )[0]
        self.assertEqual(literal, 0x20074570)
        self.assertEqual(
            self.application[END - BASE:END - BASE + 2],
            bytes.fromhex("80b5"),
        )
        self.assertEqual(
            self.application[START - BASE - 2:START - BASE],
            bytes.fromhex("01bd"),
        )

    def test_stock_caller_and_wide_interior_topology_are_exact(self) -> None:
        callers = []
        jumps = []
        interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            for link, observed in ((True, callers), (False, jumps)):
                target = self.decode_wide_branch(
                    self.application,
                    address,
                    link=link,
                )
                if target is None:
                    continue
                if target == START:
                    observed.append(address)
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append((address, target, link))
        self.assertEqual(callers, [CALLER])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            hashlib.sha256(b"0043D968").hexdigest(),
            "afc2b1614e0bc5e95e1f2434f0ee0ce"
            "30a0a654400cdb40392af4fa5b8a32899",
        )

    def test_no_narrow_interior_branch_or_stored_pointer_exists(
        self,
    ) -> None:
        narrow_entry = []
        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            target = None
            if halfword & 0xF800 == 0xE000:
                immediate = halfword & 0x07FF
                if immediate & 0x0400:
                    immediate -= 0x0800
                target = address + 4 + (immediate << 1)
            elif (
                halfword & 0xF000 == 0xD000
                and halfword & 0x0F00 != 0x0F00
            ):
                immediate = halfword & 0x00FF
                if immediate & 0x0080:
                    immediate -= 0x0100
                target = address + 4 + (immediate << 1)
            elif halfword & 0xF500 == 0xB100:
                immediate = (
                    ((halfword >> 9) & 1) << 6
                    | ((halfword >> 3) & 0x1F) << 1
                )
                target = address + 4 + immediate
            if target is not None:
                if target == START and not START <= address < END:
                    narrow_entry.append((address, halfword))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    narrow_interior.append((address, target, halfword))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            target = value & ~1
            if START <= target < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

    def test_target_symbol_and_explicit_seam_relocations_are_exact(
        self,
    ) -> None:
        function = self.symbols["open_cfw_g2_easylogger_async_submit"]
        self.assertEqual(len(self.target_text), 30)
        self.assertEqual(
            self.target_text.hex(),
            "80b5d3b20022fff7feff40f20000c0f200000068"
            "0121bde88040fff7febf",
        )
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            "c859de656db6228f8bccaa11288f7e17a"
            "7868eb17ae169598d47a349580f7484",
        )
        self.assertEqual(function[2], len(self.target_text))
        self.assertEqual(function[3] & 0x0F, 2)
        undefined = sorted(
            name
            for name, fields in self.symbols.items()
            if fields[5] == 0
        )
        self.assertEqual(
            undefined,
            [
                "open_cfw_g2_easylogger_async_record_build_single_owner",
                "open_cfw_retained_easylogger_async_event_flags",
                "open_cfw_retained_os_event_flags_set",
            ],
        )
        self.assertEqual(
            self.target_relocations,
            [
                (
                    6,
                    10,
                    "open_cfw_g2_easylogger_async_record_build_single_owner",
                ),
                (
                    10,
                    47,
                    "open_cfw_retained_easylogger_async_event_flags",
                ),
                (
                    14,
                    48,
                    "open_cfw_retained_easylogger_async_event_flags",
                ),
                (
                    26,
                    30,
                    "open_cfw_retained_os_event_flags_set",
                ),
            ],
        )

    def test_source_has_no_hidden_absolute_stock_seam(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in (
            "0x00448D4E",
            "0x004495E4",
            "0x20074570",
        ):
            self.assertNotIn(forbidden, source)
        for seam in (
            "open_cfw_g2_easylogger_async_record_build_single_owner",
            "open_cfw_retained_easylogger_async_event_flags",
            "open_cfw_retained_os_event_flags_set",
        ):
            self.assertIn(seam, source)


if __name__ == "__main__":
    unittest.main()
