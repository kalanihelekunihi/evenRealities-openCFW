from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "components" / "shared" / "freertos"
    / "runtime_freertos_task_check_for_timeout.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_freertos_task_check_for_timeout_candidate_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"

SOURCE_SIZE = 3_506
SOURCE_SHA256 = "d0d84996ae7ab897cf53655962e86574577b98bf367df52c9ae8ac076a8dc89e"
HEADER_SIZE = 5_152
HEADER_SHA256 = "a4704e71126df108833878ee3ddcf51a744f4b02cae9519a4d03fe308f0abcbc"
HOST_FIXTURE_SIZE = 9_295
HOST_FIXTURE_SHA256 = "00612017a9632e9c5fe1427c0b6a57d090371072ff54c31fc377605fb95d303a"
UPSTREAM_SIZE = 223_695
UPSTREAM_SHA256 = (
    "14020d617b96dd2814e1211f6e3b645b"
    "cf5e2bd3179c23fe7dd16bc666fe9463"
)

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
START = 0x0045_5566
END = 0x0045_55E6
STOCK_BYTES = (
    "38b505000c00002d06d1a4f198fd00205ff0ff310860fee7002c06d1a4f18ffd"
    "00205ff0ff310860fee7ecf79efd854800686968411a226812f1010f01d10025"
    "1ae0dff84c2512682b689a4206d06a68904203d30125002020600de020688142"
    "07d22068411a21602800fff7c1ff002502e0002020600125ecf783fd280032bd"
)
STOCK_SHA256 = (
    "83a983995a285b3257a1213bdbe3fa05"
    "42bae0c9296a88fd8b22c1388abdf72c"
)
CALLERS = [
    (0x0044_18C0, "13f051fe"),
    (0x0044_1BCA, "13f0ccfc"),
    (0x0044_1CF6, "13f036fc"),
]
CALLER_ADDRESS_SHA256 = (
    "0c3f5a6499ff9a73584f0a759a51260c"
    "0b12462b4835fa683874bb7bcc909b20"
)
CALLER_RECORD_SHA256 = (
    "41fb83aa91102630a8a0c5d7b88ac1c"
    "d640f50870712a3edec21326571a9954e"
)
CALLER_SPANS = [
    (0x0044_17EE, 0x0044_1952, 356,
     "d8a463345ca0e7754eb0808ebf3a725a3ca66541b6e85220b6d5459166aac11d"),
    (0x0044_1B0A, 0x0044_1C44, 314,
     "f96de373691fb5d916ccbe25e0bc1d3474b918c16968b540b601fe6e36575560"),
    (0x0044_1C44, 0x0044_1DA6, 354,
     "4d112cee107085a6606d4704c6f9edb483264086cc9f954991ac76818c08b34c"),
]
OUTGOING = [
    (0x0045_5570, 0x005F_A0A4),
    (0x0045_5582, 0x005F_A0A4),
    (0x0045_5590, 0x0044_20D0),
    (0x0045_55D0, 0x0045_5556),
    (0x0045_55DE, 0x0044_20E8),
]
INTERNAL_NARROW = [
    (0x0045_556E, 0x0045_557E),
    (0x0045_557C, 0x0045_557C),
    (0x0045_5580, 0x0045_5590),
    (0x0045_558E, 0x0045_558E),
    (0x0045_55A2, 0x0045_55A8),
    (0x0045_55A6, 0x0045_55DE),
    (0x0045_55B2, 0x0045_55C2),
    (0x0045_55B8, 0x0045_55C2),
    (0x0045_55C0, 0x0045_55DE),
    (0x0045_55C6, 0x0045_55D8),
    (0x0045_55D6, 0x0045_55DE),
]
TICK_LITERAL = 0x0045_57AC
TICK_ADDRESS = 0x2007_4A34
OVERFLOW_LITERAL = 0x0045_5AF8
OVERFLOW_ADDRESS = 0x2007_4A48

FUNCTION = "open_cfw_freertos_task_check_for_timeout"
FUNCTION_SECTION = ".text." + FUNCTION
TARGETS = {
    "apple-clang": {
        "size": 136,
        "alignment": 4,
        "sha256": (
            "33f0782fa8af468bccf78b558cc010a9"
            "f7a89f30c7c76abced9a799feb6a93f5"
        ),
        "hex": (
            "f0b581b018b30c4659b342f2d10544f63426c0f244050746c2f20706a8473268"
            "2168481c11d038467b6877690668b74201d09a421fd2d21a91421cd9891a2160"
            "45f25751c0f245018847002416e04af2a500c0f25f0080474ff0ff3000210160"
            "fee74af2a500c0f25f0080474ff0ff3000210160fee700202060012405f118008"
            "047204601b0f0bd"
        ),
    },
    "linux-clang": {
        "size": 136,
        "alignment": 4,
        "sha256": (
            "486515dfdbdb1e175321445df167dca2"
            "7357f270421b2d00492268e8da7c815c"
        ),
        "hex": (
            "f0b581b018b30c4659b342f2d10544f63426c0f244050746c2f20706a8473268"
            "2168481c11d03846d7e900737669be4201d09a421fd2d21a91421cd9891a2160"
            "45f25751c0f245018847002416e04af2a500c0f25f0080474ff0ff3000210160"
            "fee74af2a500c0f25f0080474ff0ff3000210160fee700202060012405f118008"
            "047204601b0f0bd"
        ),
    },
}

PRODUCTION_PINS = {
    "apple-clang": {
        "size": 136,
        "sha256": TARGETS["apple-clang"]["sha256"],
        "alignment": 4,
        "offset": 118_476,
        "unrelocated_sha256": TARGETS["apple-clang"]["sha256"],
    },
    "linux-clang": {
        "size": 136,
        "sha256": TARGETS["linux-clang"]["sha256"],
        "alignment": 4,
        "offset": 120_336,
        "unrelocated_sha256": TARGETS["linux-clang"]["sha256"],
    },
}

PRODUCTION_APPLE_AGGREGATE = {
    "overlay_size": 380_444,
    "overlay_sha256": (
        "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622"
    ),
    "component_size": 3_956_672,
    "component_sha256": (
        "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6"
    ),
}

PRODUCTION_LINUX_AGGREGATE = {
    "overlay_size": 172_828,
    "overlay_sha256": (
        "13a12b7fc7ec3af866d4ebe9229105ce"
        "923d6842ec6e8c4b0e01564582ed8ab1"
    ),
    "component_size": 3_956_672,
    "component_sha256": (
        "dbfc7bbf1462166b04fb962e9e639ba2"
        "296c84a6e0b4f6f22d7ae5e321efc0e6"
    ),
}

TARGET_FLAGS = [
    "--target=thumbv7em-none-eabi", "-mthumb", "-O2", "-ffreestanding",
    "-fno-jump-tables", "-fomit-frame-pointer", "-fno-builtin",
    "-mno-unaligned-access", "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables", "-fropi", "-ffunction-sections",
    "-fdata-sections", "-Wall", "-Wextra", "-Werror",
]

EVENT_ASSERT = 1
EVENT_ENTER = 2
EVENT_TICK_LOAD = 3
EVENT_OVERFLOW_LOAD = 4
EVENT_INTERNAL_SET = 5
EVENT_EXIT = 6


def sha256(data: bytes | Path) -> str:
    if isinstance(data, Path):
        data = data.read_bytes()
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22) |
        (imm10 << 12) | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5) |
            ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


class FreeRTOSTaskCheckForTimeoutCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        if version.startswith("Apple clang version 21.0.0"):
            cls.profile = "apple-clang"
        elif version.startswith("Homebrew clang version 22.1.8"):
            cls.profile = "linux-clang"
        else:
            raise AssertionError(f"unreviewed target compiler: {version!r}")

        library = temporary / library_name("freertos_check_timeout_candidate")
        host_command = [
            cls.clang, "-O2", "-Wall", "-Wextra", "-Werror",
            str(HOST_FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_check_timeout_reset
        cls.reset.argtypes = [ctypes.c_int32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.candidate = cls.loaded.open_cfw_test_check_timeout_candidate
        cls.oracle = cls.loaded.open_cfw_test_check_timeout_oracle
        for function in (cls.candidate, cls.oracle):
            function.argtypes = [
                ctypes.POINTER(ctypes.c_int32),
                ctypes.POINTER(ctypes.c_uint32),
                ctypes.POINTER(ctypes.c_uint32),
            ]
            function.restype = ctypes.c_int32
        cls.event_count = cls.loaded.open_cfw_test_check_timeout_event_count
        cls.event_count.argtypes = [ctypes.c_uint32]
        cls.event_count.restype = ctypes.c_uint32
        cls.event_kind = cls.loaded.open_cfw_test_check_timeout_event_kind
        cls.event_kind.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.event_kind.restype = ctypes.c_uint32
        cls.event_value = cls.loaded.open_cfw_test_check_timeout_event_value
        cls.event_value.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        cls.event_value.restype = ctypes.c_uint32

        cls.target_objects = [temporary / "candidate-1.o", temporary / "candidate-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [cls.clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                check=True,
                capture_output=True,
                text=True,
            )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.elf_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_objects[0]
        )
        symbol_table = apollo_overlay.section_named(cls.sections, ".symtab")
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.elf_data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.elf_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields for name, fields in cls.parsed_symbols if name
        }
        cls.relocations = []
        for section in cls.sections:
            if int(section["type"]) != 9:
                continue
            target = cls.sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    cls.elf_data,
                    int(section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    (
                        str(section["name"]), str(target["name"]), offset,
                        information & 0xFF,
                        cls.parsed_symbols[information >> 8][0],
                    )
                )

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def invoke_pair(
        self,
        *,
        current_overflow: int,
        current_tick: int,
        saved_overflow: int,
        entered_tick: int,
        ticks_to_wait: int,
    ) -> tuple[tuple[int, int, int, int], list[tuple[int, int]]]:
        self.reset(current_overflow, current_tick)
        results = []
        logs = []
        for channel, function in enumerate((self.candidate, self.oracle)):
            overflow = ctypes.c_int32(saved_overflow)
            entered = ctypes.c_uint32(entered_tick)
            wait = ctypes.c_uint32(ticks_to_wait)
            result = int(function(
                ctypes.byref(overflow),
                ctypes.byref(entered),
                ctypes.byref(wait),
            ))
            results.append((result, overflow.value, entered.value, wait.value))
            logs.append([
                (int(self.event_kind(channel, index)),
                 int(self.event_value(channel, index)))
                for index in range(int(self.event_count(channel)))
            ])
        self.assertEqual(results[0], results[1])
        self.assertEqual(logs[0], logs[1])
        return results[0], logs[0]

    def test_authenticated_upstream_local_source_and_configuration_are_pinned(
        self,
    ) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, UPSTREAM_SIZE)
        self.assertEqual(sha256(UPSTREAM_TASKS), UPSTREAM_SHA256)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(HOST_FIXTURE.stat().st_size, HOST_FIXTURE_SIZE)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)

        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        for token in (
            "BaseType_t xTaskCheckForTimeOut( TimeOut_t * const pxTimeOut,",
            "configASSERT( pxTimeOut );",
            "configASSERT( pxTicksToWait );",
            "const TickType_t xConstTickCount = xTickCount;",
            "if( *pxTicksToWait == portMAX_DELAY )",
            "xNumOfOverflows != pxTimeOut->xOverflowCount",
            "vTaskInternalSetTimeOutState( pxTimeOut );",
            "taskEXIT_CRITICAL();",
        ):
            self.assertIn(token, upstream)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "xTaskCheckForTimeOut()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455566, 0x004555E6)",
            "INCLUDE_vTaskSuspend=1",
            "INCLUDE_xTaskAbortDelay=0",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET(timeout);",
            "registered by the Apollo-main production overlay",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ASSERT_MASK_ADDRESS = 0x005FA0A4U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_ENTER_CRITICAL_ADDRESS = 0x004420D0U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_INTERNAL_SET_ADDRESS = 0x00455556U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_EXIT_CRITICAL_ADDRESS = 0x004420E8U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_TICK_COUNT_ADDRESS = 0x20074A34U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_OVERFLOW_COUNT_ADDRESS = 0x20074A48U",
            "OPEN_CFW_FREERTOS_CHECK_TIMEOUT_MAX_DELAY __UINT32_MAX__",
            "sizeof(struct open_cfw_freertos_check_timeout_state) == 8U",
        ):
            self.assertIn(token, header)

    def test_pristine_oracle_equivalence_covers_every_timeout_path(self) -> None:
        cases = [
            # Indefinite wait: INCLUDE_vTaskSuspend=1 bypasses overflow logic.
            (2, 0x200, 1, 0x100, 0xFFFF_FFFF, (0, 1, 0x100, 0xFFFF_FFFF)),
            # Overflow count changed and current tick passed entered tick.
            (2, 0x200, 1, 0x100, 0x1000, (1, 1, 0x100, 0)),
            # Same overflow, partial wait: remaining delay and snapshot update.
            (-4, 0x140, -4, 0x100, 0x80, (0, -4, 0x140, 0x40)),
            # Elapsed time exactly equals and exceeds the remaining wait.
            (7, 0x180, 7, 0x100, 0x80, (1, 7, 0x100, 0)),
            (7, 0x181, 7, 0x100, 0x80, (1, 7, 0x100, 0)),
            # One tick wrap, not a full extra overflow cycle.
            (11, 0x20, 10, 0xFFFF_FFF0, 0x80, (0, 11, 0x20, 0x50)),
            # Unsigned subtraction and signed overflow-count extremes.
            (-0x8000_0000, 0, 0x7FFF_FFFF, 0, 1,
             (1, 0x7FFF_FFFF, 0, 0)),
        ]
        for (
            current_overflow,
            current_tick,
            saved_overflow,
            entered_tick,
            ticks_to_wait,
            expected,
        ) in cases:
            with self.subTest(
                current_overflow=current_overflow,
                current_tick=current_tick,
                saved_overflow=saved_overflow,
                entered_tick=entered_tick,
                ticks_to_wait=ticks_to_wait,
            ):
                result, events = self.invoke_pair(
                    current_overflow=current_overflow,
                    current_tick=current_tick,
                    saved_overflow=saved_overflow,
                    entered_tick=entered_tick,
                    ticks_to_wait=ticks_to_wait,
                )
                self.assertEqual(result, expected)
                self.assertEqual(
                    [kind for kind, _ in events[:4]],
                    [EVENT_ASSERT, EVENT_ASSERT, EVENT_ENTER, EVENT_TICK_LOAD],
                )
                self.assertEqual(events[-1][0], EVENT_EXIT)

        indefinite = self.invoke_pair(
            current_overflow=99,
            current_tick=0x1234,
            saved_overflow=-99,
            entered_tick=0xFFFF_F000,
            ticks_to_wait=0xFFFF_FFFF,
        )[1]
        self.assertNotIn(EVENT_OVERFLOW_LOAD, [kind for kind, _ in indefinite])
        self.assertNotIn(EVENT_INTERNAL_SET, [kind for kind, _ in indefinite])

    def test_official_body_literals_configuration_and_call_topology_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 128)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(sha256(stock), STOCK_SHA256)

        # Both configASSERT expansions call the interrupt-mask provider and
        # fault through address -1; no abort-delay/TCB load precedes max delay.
        self.assertEqual(stock[6:24].hex(), "002d06d1a4f198fd00205ff0ff310860fee7")
        self.assertEqual(stock[24:42].hex(), "002c06d1a4f18ffd00205ff0ff310860fee7")
        self.assertEqual(stock[54:62].hex(), "226812f1010f01d1")

        tick_instruction = struct.unpack_from("<H", stock, 46)[0]
        self.assertEqual(tick_instruction & 0xF800, 0x4800)
        self.assertEqual(
            ((START + 46 + 4) & ~3) + (tick_instruction & 0xFF) * 4,
            TICK_LITERAL,
        )
        self.assertEqual(
            struct.unpack("<I", self.span(TICK_LITERAL, TICK_LITERAL + 4))[0],
            TICK_ADDRESS,
        )
        first, second = struct.unpack_from("<HH", stock, 66)
        self.assertEqual((first & 0xFFF0, second & 0xF000), (0xF8D0, 0x2000))
        self.assertEqual(
            ((START + 66 + 4) & ~3) + (second & 0x0FFF),
            OVERFLOW_LITERAL,
        )
        self.assertEqual(
            struct.unpack(
                "<I", self.span(OVERFLOW_LITERAL, OVERFLOW_LITERAL + 4)
            )[0],
            OVERFLOW_ADDRESS,
        )

        outgoing = []
        internal = []
        for offset in range(0, len(stock), 2):
            address = START + offset
            if offset + 4 <= len(stock):
                first, second = struct.unpack_from("<HH", stock, offset)
                target = thumb_wide_branch_target(
                    address, first, second, link=True
                )
                if target is not None:
                    outgoing.append((address, target))
            halfword = struct.unpack_from("<H", stock, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END:
                    internal.append((address, target))
        self.assertEqual(outgoing, OUTGOING)
        self.assertEqual(internal, INTERNAL_NARROW)

    def test_callers_and_whole_image_entry_interior_pointer_closure(self) -> None:
        direct_bl = []
        direct_bw = []
        external_interior = []
        external_narrow = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            encoding = self.application[offset:offset + 4]
            for link in (True, False):
                target = thumb_wide_branch_target(
                    address, first, second, link=link
                )
                if target is None or not START <= target < END:
                    continue
                if target == START:
                    (direct_bl if link else direct_bw).append(
                        (address, encoding.hex())
                    )
                elif not START <= address < END:
                    external_interior.append(
                        (address, target, link, encoding.hex())
                    )
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END and not START <= address < END:
                    external_narrow.append((address, target, halfword))

        self.assertEqual(direct_bl, CALLERS)
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(external_narrow, [])
        self.assertEqual(
            sha256(b"".join(struct.pack("<I", address) for address, _ in CALLERS)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(b"".join(
                struct.pack("<I", address) + bytes.fromhex(encoding)
                for address, encoding in CALLERS
            )),
            CALLER_RECORD_SHA256,
        )
        for start, end, size, digest in CALLER_SPANS:
            body = self.span(start, end)
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = self.application.find(needle, position)
                    if position < 0:
                        break
                    stored.append((BASE + position, value, canonical, position % 4))
                    position += 1
        self.assertEqual(stored, [])

    def test_isolated_target_object_is_closed_and_profile_pinned(self) -> None:
        for profile, pins in TARGETS.items():
            with self.subTest(recorded_profile=profile):
                recorded = bytes.fromhex(pins["hex"])
                self.assertEqual(len(recorded), pins["size"])
                self.assertEqual(sha256(recorded), pins["sha256"])
        target = TARGETS[self.profile]
        parsed = [
            self.apollo_overlay.parse_elf32(path) for path in self.target_objects
        ]
        function_bytes = []
        for data, sections in parsed:
            section = next(
                item for item in sections if item["name"] == FUNCTION_SECTION
            )
            body = data[
                int(section["offset"]):
                int(section["offset"]) + int(section["size"])
            ]
            function_bytes.append(body)
            self.assertEqual(int(section["type"]), 1)
            self.assertEqual(int(section["flags"]), 0x6)
            self.assertEqual(int(section["alignment"]), target["alignment"])
            self.assertEqual(len(body), target["size"])
            self.assertEqual(body.hex(), target["hex"])
            self.assertEqual(sha256(body), target["sha256"])
            executable = [
                item["name"] for item in sections
                if int(item["size"]) > 0 and int(item["flags"]) & 0x4
            ]
            self.assertEqual(executable, [FUNCTION_SECTION])
            writable_allocated = [
                item["name"] for item in sections
                if int(item["size"]) > 0
                and int(item["flags"]) & 0x2
                and int(item["flags"]) & 0x1
            ]
            self.assertEqual(writable_allocated, [])
        self.assertEqual(function_bytes[0], function_bytes[1])

        fields = self.symbols[FUNCTION]
        function_section = next(
            item for item in self.sections if item["name"] == FUNCTION_SECTION
        )
        self.assertEqual(fields[1] & 1, 1)
        self.assertEqual(fields[2], TARGETS[self.profile]["size"])
        self.assertEqual(fields[3] >> 4, 1)
        self.assertEqual(fields[3] & 0xF, 2)
        self.assertEqual(fields[5], int(function_section["index"]))
        undefined = [
            name for name, symbol in self.parsed_symbols
            if name and symbol[5] == 0
        ]
        self.assertEqual(undefined, [])
        self.assertEqual(len(self.relocations), 1)
        relocation = self.relocations[0]
        self.assertTrue(relocation[0].startswith(".rel.ARM.exidx."))
        self.assertTrue(relocation[1].startswith(".ARM.exidx."))
        self.assertEqual(relocation[2:], (0, 42, ""))
        self.assertFalse(
            any(target_name == FUNCTION_SECTION
                for _, target_name, *_ in self.relocations)
        )

    def test_production_overlay_registration_and_redirect_are_exact(self) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        self.assertEqual(config["expected"], PRODUCTION_APPLE_AGGREGATE)
        self.assertEqual(
            config["toolchain_profiles"]["linux-clang"]["expected"],
            PRODUCTION_LINUX_AGGREGATE,
        )

        leaves = [
            item for item in config["relocated_leaves"]
            if item.get("function") == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        leaf = leaves[0]
        self.assertEqual(
            leaf["source"]["path"],
            SOURCE.relative_to(ROOT).as_posix(),
        )
        self.assertEqual(leaf["source"]["size"], SOURCE_SIZE)
        self.assertEqual(leaf["source"]["sha256"], SOURCE_SHA256)
        self.assertEqual(leaf["source"]["license"], "MIT")
        self.assertEqual(
            leaf["source"]["upstream_commit"],
            "def7d2df2b0506d3d249334974f51e427c17a41c",
        )
        self.assertEqual(leaf["expected"], PRODUCTION_PINS["apple-clang"])
        self.assertEqual(leaf["relocations"], [])
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(linux["expected"], PRODUCTION_PINS["linux-clang"])
        self.assertEqual(linux["relocations"], [])

        # The timeout closure owns one profile-pinned, non-overlapping span.
        # Its position is ordered against every other relocated leaf by offset,
        # without assuming that it remains the final function as new source
        # replacements are appended to the overlay.
        function_index = config["functions"].index(FUNCTION)
        for profile in ("apple-clang", "linux-clang"):
            expected = PRODUCTION_PINS[profile]
            start = expected["offset"]
            end = start + expected["size"]
            for other in config["relocated_leaves"]:
                if other is leaf:
                    continue
                other_profile = other.get("toolchain_profiles", {}).get(
                    profile,
                    {},
                )
                other_expected = other_profile.get(
                    "expected",
                    other["expected"],
                )
                other_start = other_expected["offset"]
                other_end = other_start + other_expected["size"]
                self.assertTrue(
                    other_end <= start or end <= other_start,
                    msg=(
                        f"{profile} timeout closure overlaps "
                        f"{other['function']}"
                    ),
                )
                self.assertNotEqual(
                    config["functions"].index(other["function"]),
                    function_index,
                )

        patches = [
            item for item in config["patch_sites"]
            if item.get("runtime_address") == START
        ]
        self.assertEqual(len(patches), 1)
        patch = patches[0]
        self.assertEqual(patch["name"], "replace_freertos_task_check_for_timeout")
        self.assertEqual(patch["expected_hex"], STOCK_BYTES)
        self.assertEqual(len(bytes.fromhex(patch["expected_hex"])), END - START)
        self.assertEqual(sha256(bytes.fromhex(patch["expected_hex"])), STOCK_SHA256)
        self.assertEqual(patch["branch"], "b_w")
        self.assertEqual(patch["target_function"], FUNCTION)

        overlay_runtime = BASE + len(self.application)
        for profile in ("apple-clang", "linux-clang"):
            target = overlay_runtime + PRODUCTION_PINS[profile]["offset"]
            branch = self.apollo_overlay.encode_thumb_b_w(START, target)
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    START,
                    branch,
                    link=False,
                ),
                target,
            )


if __name__ == "__main__":
    unittest.main()
