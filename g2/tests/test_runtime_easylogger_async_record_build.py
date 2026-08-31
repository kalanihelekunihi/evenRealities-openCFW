from __future__ import annotations

import os

import ctypes
import hashlib
import json
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STOCK_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_easylogger_async_record_build_stock.c"
)
SINGLE_OWNER_SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_easylogger_async_record_build_single_owner.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_easylogger_async_record_build_host.c"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BASE = 0x00438000
START = 0x00448D4E
END = 0x00448DD2
STOCK_SHA256 = (
    "9d95b63bc62e11910e39344ddea652137"
    "98d75caa4b91d5ce9cf033d09509e17"
)
CALLER = 0x0044AA88
RECORD_TOKEN = 0xA1100001
ENQUEUE_LIMIT = 10000
ERROR_MESSAGE = b"error!!!!!!elog_async_ext_output: enqueue_log failed\n"
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


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class AsyncRecord(ctypes.Structure):
    _fields_ = [
        ("next", ctypes.c_uint32),
        ("state", ctypes.c_uint32),
        ("length", ctypes.c_uint16),
        ("metadata", ctypes.c_uint16),
        ("level", ctypes.c_uint8),
        ("payload", ctypes.c_uint8 * 256),
        ("padding", ctypes.c_uint8 * 3),
    ]


class RuntimeEasyLoggerAsyncRecordBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.variants = {}

        for name, define in (
            ("stock", None),
            ("single_owner", "OPEN_CFW_TEST_EASYLOGGER_ASYNC_SINGLE_OWNER"),
        ):
            library = temporary / (
                f"{name}.dylib"
                if sys.platform == "darwin"
                else f"{name}.so"
            )
            command = [
                os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
            ]
            if define is not None:
                command.append(f"-D{define}=1")
            command.append(str(FIXTURE))
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", "-o", str(library)])
            else:
                command.extend(
                    ["-shared", "-fPIC", "-o", str(library)]
                )
            subprocess.run(
                command,
                check=True,
                capture_output=True,
                text=True,
            )
            loaded = ctypes.CDLL(str(library))
            loaded.open_cfw_test_easylogger_async_record_build_reset.argtypes = [
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
            ]
            loaded.open_cfw_test_easylogger_async_record_build_reset.restype = (
                None
            )
            loaded.open_cfw_test_easylogger_async_record_build.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_uint32,
                ctypes.c_uint32,
            ]
            loaded.open_cfw_test_easylogger_async_record_build.restype = (
                ctypes.c_uint32
            )
            cls.variants[name] = loaded

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.target_objects = {}
        for name, source in (
            ("stock", STOCK_SOURCE),
            ("single_owner", SINGLE_OWNER_SOURCE),
        ):
            target_object = temporary / f"{name}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *TARGET_FLAGS,
                    "-c",
                    str(source),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            data, sections = apollo_overlay.parse_elf32(target_object)
            text = apollo_overlay.section_named(sections, ".text")
            rodata = apollo_overlay.section_named(sections, ".rodata")
            symbol_table = apollo_overlay.section_named(
                sections,
                ".symtab",
            )
            string_table = sections[int(symbol_table["link"])]
            strings = data[
                int(string_table["offset"]):
                int(string_table["offset"]) + int(string_table["size"])
            ]
            parsed_symbols = []
            for index in range(int(symbol_table["size"]) // 16):
                fields = struct.unpack_from(
                    "<IIIBBH",
                    data,
                    int(symbol_table["offset"]) + index * 16,
                )
                symbol_name = apollo_overlay.elf_string(
                    strings,
                    fields[0],
                    "symbol",
                )
                parsed_symbols.append((symbol_name, fields))
            relocations = []
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
                        relocations.append(
                            (
                                offset,
                                information & 0xFF,
                                parsed_symbols[information >> 8][0],
                            )
                        )
            cls.target_objects[name] = {
                "text": data[
                    int(text["offset"]):
                    int(text["offset"]) + int(text["size"])
                ],
                "rodata": data[
                    int(rodata["offset"]):
                    int(rodata["offset"]) + int(rodata["size"])
                ],
                "symbols": {
                    symbol_name: fields
                    for symbol_name, fields in parsed_symbols
                    if symbol_name
                },
                "undefined": sorted(
                    symbol_name
                    for symbol_name, fields in parsed_symbols
                    if symbol_name and fields[5] == 0
                ),
                "relocations": relocations,
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def u32(loaded: ctypes.CDLL, name: str) -> int:
        return ctypes.c_uint32.in_dll(loaded, name).value

    @staticmethod
    def record(loaded: ctypes.CDLL) -> AsyncRecord:
        return AsyncRecord.in_dll(
            loaded,
            "open_cfw_test_easylogger_async_record",
        )

    @classmethod
    def events(cls, loaded: ctypes.CDLL) -> list[int]:
        count = cls.u32(
            loaded,
            "open_cfw_test_easylogger_async_event_count",
        )
        values = (ctypes.c_uint32 * 8).in_dll(
            loaded,
            "open_cfw_test_easylogger_async_events",
        )
        return list(values[:count])

    @staticmethod
    def reset(
        loaded: ctypes.CDLL,
        *,
        ready: int = 1,
        default_metadata: int = 1,
        allocate: int = 1,
        success_attempt: int = 1,
        free_head: int = 0,
    ) -> None:
        loaded.open_cfw_test_easylogger_async_record_build_reset(
            ready,
            default_metadata,
            allocate,
            success_attempt,
            free_head,
        )

    @staticmethod
    def build(
        loaded: ctypes.CDLL,
        message: ctypes.Array[ctypes.c_char],
        length: int,
        metadata: int,
        level: int,
    ) -> int:
        return loaded.open_cfw_test_easylogger_async_record_build(
            ctypes.addressof(message),
            length,
            metadata,
            level,
        )

    def test_record_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(AsyncRecord), 0x110)
        self.assertEqual(AsyncRecord.next.offset, 0x00)
        self.assertEqual(AsyncRecord.state.offset, 0x04)
        self.assertEqual(AsyncRecord.length.offset, 0x08)
        self.assertEqual(AsyncRecord.metadata.offset, 0x0A)
        self.assertEqual(AsyncRecord.level.offset, 0x0C)
        self.assertEqual(AsyncRecord.payload.offset, 0x0D)
        self.assertEqual(AsyncRecord.padding.offset, 0x10D)

    def test_silent_rejections_do_not_allocate_or_diagnose(self) -> None:
        message = ctypes.create_string_buffer(b"x")
        for name, loaded in self.variants.items():
            cases = (
                (0, ctypes.addressof(message), 1),
                (1, 0, 1),
                (1, ctypes.addressof(message), 0),
            )
            for ready, pointer, length in cases:
                with self.subTest(
                    variant=name,
                    ready=ready,
                    pointer=pointer,
                    length=length,
                ):
                    self.reset(loaded, ready=ready)
                    result = (
                        loaded.open_cfw_test_easylogger_async_record_build(
                            pointer,
                            length,
                            1,
                            2,
                        )
                    )
                    self.assertEqual(result, 0)
                    self.assertEqual(
                        self.u32(
                            loaded,
                            "open_cfw_test_easylogger_async_allocate_calls",
                        ),
                        0,
                    )
                    self.assertEqual(
                        self.u32(
                            loaded,
                            "open_cfw_test_easylogger_async_diagnostic_calls",
                        ),
                        0,
                    )

    def test_allocation_failure_is_silent(self) -> None:
        message = ctypes.create_string_buffer(b"allocation")
        for name, loaded in self.variants.items():
            with self.subTest(variant=name):
                self.reset(loaded, allocate=0)
                self.assertEqual(self.build(loaded, message, 10, 1, 2), 0)
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_allocate_calls",
                    ),
                    1,
                )
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_enqueue_calls",
                    ),
                    0,
                )
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_recycle_calls",
                    ),
                    0,
                )

    def test_success_builds_exact_record_and_returns_zero(self) -> None:
        message_bytes = bytes(range(1, 33))
        message = ctypes.create_string_buffer(message_bytes)
        for name, loaded in self.variants.items():
            with self.subTest(variant=name):
                self.reset(loaded)
                result = self.build(
                    loaded,
                    message,
                    len(message_bytes),
                    0x1234567A,
                    0x89ABCDEF,
                )
                record = self.record(loaded)
                self.assertEqual(result, 0)
                self.assertEqual(record.state, 2)
                self.assertEqual(record.length, len(message_bytes))
                self.assertEqual(record.metadata, 0x7A)
                self.assertEqual(record.level, 0xEF)
                self.assertEqual(
                    bytes(record.payload[:len(message_bytes)]),
                    message_bytes,
                )
                self.assertEqual(record.payload[len(message_bytes)], 0)
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_recycle_calls",
                    ),
                    0,
                )
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_diagnostic_calls",
                    ),
                    0,
                )
                self.assertEqual(self.events(loaded), [1, 2])

    def test_zero_metadata_uses_truncated_default(self) -> None:
        message = ctypes.create_string_buffer(b"metadata")
        for name, loaded in self.variants.items():
            with self.subTest(variant=name):
                self.reset(loaded, default_metadata=0x1A5)
                self.build(loaded, message, 8, 0xFFFFFF00, 3)
                self.assertEqual(self.record(loaded).metadata, 0xA5)

    def test_length_clamp_and_terminator_are_exact(self) -> None:
        message_bytes = bytes(index & 0xFF for index in range(320))
        message = ctypes.create_string_buffer(message_bytes)
        for name, loaded in self.variants.items():
            for requested, expected in (
                (1, 1),
                (254, 254),
                (255, 255),
                (256, 255),
                (320, 255),
            ):
                with self.subTest(
                    variant=name,
                    requested=requested,
                ):
                    self.reset(loaded)
                    self.build(loaded, message, requested, 1, 2)
                    record = self.record(loaded)
                    self.assertEqual(record.length, expected)
                    self.assertEqual(
                        bytes(record.payload[:expected]),
                        message_bytes[:expected],
                    )
                    self.assertEqual(record.payload[expected], 0)

    def test_success_on_ten_thousandth_attempt_does_not_recycle(
        self,
    ) -> None:
        message = ctypes.create_string_buffer(b"last-attempt")
        for name, loaded in self.variants.items():
            with self.subTest(variant=name):
                self.reset(loaded, success_attempt=ENQUEUE_LIMIT)
                self.build(loaded, message, 12, 1, 2)
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_enqueue_attempts",
                    ),
                    ENQUEUE_LIMIT,
                )
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_recycle_calls",
                    ),
                    0,
                )
                self.assertEqual(self.record(loaded).state, 2)

    def test_retry_exhaustion_reproduces_stock_double_recycle(
        self,
    ) -> None:
        loaded = self.variants["stock"]
        message = ctypes.create_string_buffer(b"retry-limit")
        self.reset(loaded, success_attempt=0)

        self.assertEqual(self.build(loaded, message, 11, 1, 2), 0)

        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_enqueue_attempts",
            ),
            ENQUEUE_LIMIT,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_enqueue_retry_limit_count",
            ),
            1,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_enqueue_drop_count",
            ),
            1,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_recycle_calls",
            ),
            2,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_free_head",
            ),
            RECORD_TOKEN,
        )
        self.assertEqual(self.record(loaded).next, RECORD_TOKEN)
        self.assertEqual(self.record(loaded).state, 0)
        self.assertEqual(self.events(loaded), [1, 2, 3, 3, 4])

    def test_retry_exhaustion_corrected_policy_has_one_owner(
        self,
    ) -> None:
        loaded = self.variants["single_owner"]
        message = ctypes.create_string_buffer(b"retry-limit")
        self.reset(loaded, success_attempt=0)

        self.assertEqual(self.build(loaded, message, 11, 1, 2), 0)

        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_enqueue_attempts",
            ),
            ENQUEUE_LIMIT,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_recycle_calls",
            ),
            1,
        )
        self.assertEqual(
            self.u32(
                loaded,
                "open_cfw_test_easylogger_async_free_head",
            ),
            RECORD_TOKEN,
        )
        self.assertEqual(self.record(loaded).next, 0)
        self.assertEqual(self.record(loaded).state, 0)
        self.assertEqual(self.events(loaded), [1, 2, 3, 4])

    def test_both_failure_policies_emit_exact_diagnostic_once(self) -> None:
        message = ctypes.create_string_buffer(b"diagnostic")
        for name, loaded in self.variants.items():
            with self.subTest(variant=name):
                self.reset(loaded, success_attempt=0)
                self.build(loaded, message, 10, 1, 2)
                self.assertEqual(
                    self.u32(
                        loaded,
                        "open_cfw_test_easylogger_async_diagnostic_calls",
                    ),
                    1,
                )
                observed = (ctypes.c_char * 96).in_dll(
                    loaded,
                    "open_cfw_test_easylogger_async_diagnostic_message",
                )
                self.assertEqual(
                    bytes(observed).split(b"\0", 1)[0],
                    ERROR_MESSAGE,
                )

    @staticmethod
    def decode_wide_branch(
        application: bytes,
        address: int,
        *,
        link: bool,
    ) -> int | None:
        first, second = struct.unpack_from(
            "<HH",
            application,
            address - BASE,
        )
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

    def test_stock_span_hash_abi_and_dependencies_are_exact(self) -> None:
        body = self.application[START - BASE:END - BASE]
        self.assertEqual(len(body), 132)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            self.application[START - BASE - 4:START - BASE],
            bytes.fromhex("bde8f081"),
        )
        self.assertEqual(
            self.application[END - BASE:END - BASE + 4],
            bytes.fromhex("70b57b48"),
        )
        expected_calls = {
            0x00448D84: 0x00448A0C,
            0x00448D9C: 0x00439BE4,
            0x00448DB4: 0x00448AF0,
            0x00448DBE: 0x00448A8E,
            0x00448DC4: 0x004733EE,
        }
        self.assertEqual(
            {
                site: self.decode_wide_branch(
                    self.application,
                    site,
                    link=True,
                )
                for site in expected_calls
            },
            expected_calls,
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x00448FC4 - BASE,
            )[0],
            0x20074FC0,
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x00448FC8 - BASE,
            )[0],
            0x20004546,
        )
        self.assertEqual(
            struct.unpack_from(
                "<I",
                self.application,
                0x00448FD0 - BASE,
            )[0],
            0x0071E990,
        )
        enqueue = self.application[
            0x00448AF0 - BASE:0x00448B96 - BASE
        ]
        self.assertEqual(
            hashlib.sha256(enqueue).hexdigest(),
            "d38c8f35778486058d045b6b7ad9f9b6"
            "a6d8c5242f3c36828f72ea4270bc4c8e",
        )
        self.assertEqual(
            self.application[
                0x00448B30 - BASE:0x00448B34 - BASE
            ],
            bytes.fromhex("42f21170"),
        )
        self.assertEqual(
            self.decode_wide_branch(
                self.application,
                0x00448B6C,
                link=True,
            ),
            0x00448A8E,
        )

    def test_stock_caller_interior_and_pointer_topology_is_exact(
        self,
    ) -> None:
        callers = []
        jumps = []
        interiors = []
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
                    interiors.append((address, target, link))
        self.assertEqual(callers, [CALLER])
        self.assertEqual(jumps, [])
        self.assertEqual(interiors, [])

        narrow_entry = []
        narrow_interiors = []
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
            if target == START and not START <= address < END:
                narrow_entry.append((address, halfword))
            if (
                target is not None
                and START < target < END
                and not START <= address < END
            ):
                narrow_interiors.append((address, target, halfword))
        self.assertEqual(narrow_entry, [])
        self.assertEqual(narrow_interiors, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            if START <= (value & ~1) < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])
        self.assertEqual(
            hashlib.sha256(b"0044AA88").hexdigest(),
            "2670d4a2ca18ae826c3a359f9826321f"
            "58b9101850ab0ccb681f185f810ee769",
        )

    @_APPLE_ONLY
    def test_target_candidates_have_explicit_seams_only(self) -> None:
        self.assertEqual(
            hashlib.sha256(STOCK_SOURCE.read_bytes()).hexdigest(),
            "97a1ce16ff7b36c50d8565acf3b1b0e"
            "f1ef208f61df9c4b0eec2443f7af93819",
        )
        self.assertEqual(
            hashlib.sha256(SINGLE_OWNER_SOURCE.read_bytes()).hexdigest(),
            "ec6f80eb078ad78773da241397a0039af"
            "f6123bf15d05b1c33ac99c85f0861d3",
        )
        expected_common = {
            "open_cfw_retained_easylogger_async_default_metadata",
            "open_cfw_retained_easylogger_async_diagnostic",
            "open_cfw_retained_easylogger_async_ready",
            "open_cfw_retained_easylogger_async_record_allocate",
            "open_cfw_retained_easylogger_async_record_enqueue",
        }
        self.assertEqual(
            set(self.target_objects["single_owner"]["undefined"]),
            expected_common,
        )
        self.assertEqual(
            set(self.target_objects["stock"]["undefined"]),
            expected_common
            | {"open_cfw_retained_easylogger_async_record_recycle"},
        )
        stock_relocation_symbols = {
            symbol
            for _, _, symbol in self.target_objects["stock"][
                "relocations"
            ]
        }
        corrected_relocation_symbols = {
            symbol
            for _, _, symbol in self.target_objects["single_owner"][
                "relocations"
            ]
        }
        self.assertIn(
            "open_cfw_retained_easylogger_async_record_recycle",
            stock_relocation_symbols,
        )
        self.assertNotIn(
            "open_cfw_retained_easylogger_async_record_recycle",
            corrected_relocation_symbols,
        )
        expected_targets = {
            "stock": {
                "size": 228,
                "sha256": (
                    "dce01b3325dc6e08acc71c5497238460f"
                    "679058d75d5b1e99d0df9e5fb5cb00a"
                ),
                "relocations": [
                    (
                        6,
                        47,
                        "open_cfw_retained_easylogger_async_ready",
                    ),
                    (
                        10,
                        48,
                        "open_cfw_retained_easylogger_async_ready",
                    ),
                    (
                        38,
                        47,
                        "open_cfw_retained_easylogger_async_default_metadata",
                    ),
                    (
                        42,
                        48,
                        "open_cfw_retained_easylogger_async_default_metadata",
                    ),
                    (
                        56,
                        10,
                        "open_cfw_retained_easylogger_async_record_allocate",
                    ),
                    (
                        190,
                        10,
                        "open_cfw_retained_easylogger_async_record_enqueue",
                    ),
                    (
                        204,
                        10,
                        "open_cfw_retained_easylogger_async_record_recycle",
                    ),
                    (
                        208,
                        49,
                        "open_cfw_g2_easylogger_async_enqueue_error",
                    ),
                    (
                        212,
                        50,
                        "open_cfw_g2_easylogger_async_enqueue_error",
                    ),
                    (
                        218,
                        10,
                        "open_cfw_retained_easylogger_async_diagnostic",
                    ),
                ],
            },
            "single_owner": {
                "size": 216,
                "sha256": (
                    "498d64ad69021489f1a166af5903ac3c"
                    "dd2edf97dc5f83e16d608b55711a303d"
                ),
                "relocations": [
                    (
                        6,
                        47,
                        "open_cfw_retained_easylogger_async_ready",
                    ),
                    (
                        10,
                        48,
                        "open_cfw_retained_easylogger_async_ready",
                    ),
                    (
                        38,
                        47,
                        "open_cfw_retained_easylogger_async_default_metadata",
                    ),
                    (
                        42,
                        48,
                        "open_cfw_retained_easylogger_async_default_metadata",
                    ),
                    (
                        56,
                        10,
                        "open_cfw_retained_easylogger_async_record_allocate",
                    ),
                    (
                        184,
                        10,
                        "open_cfw_retained_easylogger_async_record_enqueue",
                    ),
                    (
                        196,
                        49,
                        "open_cfw_g2_easylogger_async_enqueue_error",
                    ),
                    (
                        200,
                        50,
                        "open_cfw_g2_easylogger_async_enqueue_error",
                    ),
                    (
                        206,
                        10,
                        "open_cfw_retained_easylogger_async_diagnostic",
                    ),
                ],
            },
        }
        for name, expected in expected_targets.items():
            target = self.target_objects[name]
            with self.subTest(target=name):
                self.assertEqual(len(target["text"]), expected["size"])
                self.assertEqual(
                    hashlib.sha256(target["text"]).hexdigest(),
                    expected["sha256"],
                )
                self.assertEqual(
                    target["relocations"],
                    expected["relocations"],
                )
                self.assertEqual(
                    target["rodata"],
                    ERROR_MESSAGE + b"\0",
                )
                self.assertEqual(
                    hashlib.sha256(target["rodata"]).hexdigest(),
                    "2a8285b704dd7e2cc111a09f750d509f"
                    "79794fca0aba7ec1513414df4fd9bad3",
                )
        expected_functions = {
            "stock": "open_cfw_g2_easylogger_async_record_build_stock",
            "single_owner": (
                "open_cfw_g2_easylogger_async_record_build_single_owner"
            ),
        }
        for name, function_name in expected_functions.items():
            fields = self.target_objects[name]["symbols"][function_name]
            self.assertEqual(fields[2], len(self.target_objects[name]["text"]))
            self.assertEqual(fields[3] & 0x0F, 2)
        for source in (STOCK_SOURCE, SINGLE_OWNER_SOURCE):
            text = source.read_text(encoding="utf-8")
            self.assertIn("not upstream EasyLogger code", text)
            self.assertNotIn("elog_async_output(", text)
            for absolute in (
                "0x00448A0C",
                "0x00448A8E",
                "0x00448AF0",
                "0x004733EE",
                "0x20004546",
                "0x20074FC0",
            ):
                self.assertNotIn(absolute, text)

    def test_production_overlay_selects_single_owner_contract(self) -> None:
        config = json.loads(
            (
                ROOT
                / "components"
                / "apollo_main"
                / "core_overlay"
                / "overlay.json"
            ).read_text(encoding="utf-8")
        )
        builder = next(
            leaf
            for leaf in config["relocated_leaves"]
            if leaf["function"]
            == "open_cfw_g2_easylogger_async_record_build_single_owner"
        )
        self.assertEqual(
            builder["source"]["path"],
            "components/apollo_main/core_overlay/"
            "runtime_easylogger_async_record_build_single_owner.c",
        )
        self.assertNotIn(
            "open_cfw_g2_easylogger_async_record_build_stock",
            config["functions"],
        )
        patch = next(
            site
            for site in config["patch_sites"]
            if site["name"] == "replace_easylogger_async_record_build"
        )
        self.assertEqual(patch["runtime_address"], START)
        self.assertEqual(patch["expected_size"], END - START)
        self.assertEqual(
            patch["target_function"],
            "open_cfw_g2_easylogger_async_record_build_single_owner",
        )
        submit = next(
            leaf
            for leaf in config["relocated_leaves"]
            if leaf["function"] == "open_cfw_g2_easylogger_async_submit"
        )
        for relocations in (
            builder["relocations"],
            builder["toolchain_profiles"]["linux-clang"]["relocations"],
        ):
            self.assertEqual(len(relocations), 9)
            self.assertNotIn(
                "open_cfw_retained_easylogger_async_record_recycle",
                {item["symbol"] for item in relocations},
            )
        for relocations in (
            submit["relocations"],
            submit["toolchain_profiles"]["linux-clang"]["relocations"],
        ):
            builder_call = next(
                item
                for item in relocations
                if item["offset"] == 6
            )
            self.assertEqual(
                builder_call["target_function"],
                "open_cfw_g2_easylogger_async_record_build_single_owner",
            )

    def test_production_manifest_describes_corrected_ownership(self) -> None:
        manifest = json.loads(
            (
                ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
            ).read_text(encoding="utf-8")
        )
        component = manifest["component_overrides"]["apollo_main"]
        text_region = next(
            region
            for region in component["regions"]
            if region["name"]
            == "apollo_easylogger_async_record_builder_source_text"
        )
        self.assertEqual(text_region["file_offset"], 3642008)
        self.assertEqual(text_region["size"], 216)
        self.assertEqual(text_region["target_address"], 0x007B1278)
        self.assertIn("single owner", text_region["function"])
        self.assertNotIn("double-recycle", text_region["function"])


if __name__ == "__main__":
    unittest.main()
