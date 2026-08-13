from __future__ import annotations

import copy
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
    ROOT
    / "components"
    / "shared"
    / "freertos"
    / "runtime_freertos_timeout_state.c"
)
HEADER = SOURCE.with_suffix(".h")
HOST_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_freertos_timeout_state_host.c"
)
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "freertos-kernel" / "verify_snapshot.py"
)
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)

SOURCE_SIZE = 2253
SOURCE_SHA256 = (
    "2d37be0e7fa2410afbe717475a80d2fb4"
    "74ebf715fd030702870ffd47277c1f2"
)
HEADER_SIZE = 2660
HEADER_SHA256 = (
    "120b28c4e56db6d62183f35ff8891eba3"
    "719fb54cdbb3cebe5b5813e6402df61"
)
HOST_FIXTURE_SIZE = 3858
HOST_FIXTURE_SHA256 = (
    "e8c8ad88ea48f733074696a457b288453"
    "8ef17d6ffb2d75d45211cdee1e288ae"
)

BASE = 0x00438000
START = 0x00455556
END = 0x00455566
STOCK_BYTES = "dff8a015096801609349096841607047"
STOCK_SHA256 = (
    "6ff12b123d1647953300d002a439daf4"
    "df52f96e369eebbb0b183a1a4fb3e862"
)
OVERFLOW_LITERAL = 0x00455AF8
OVERFLOW_WORD = 0x20074A48
TICK_LITERAL = 0x004557AC
TICK_WORD = 0x20074A34
CALLERS = [
    (0x00441886, "13f066fe"),
    (0x00441B90, "13f0e1fc"),
    (0x00441CBC, "13f04bfc"),
    (0x004555D0, "fff7c1ff"),
]

UNORDERED_EVENT_START = 0x0045547C
UNORDERED_EVENT_END = START
UNORDERED_EVENT_SHA256 = (
    "aa14475cf28218296c4fd829c02080fc"
    "017a5fe137f476de47e747f1e920e33b"
)
UNORDERED_EVENT_CALLERS = [(0x0047EE02, "d6f73bfb")]
UNORDERED_EVENT_CALLEES = [
    (0x00455486, 0x005FA0A4),
    (0x004554A0, 0x005FA0A4),
    (0x004554D0, 0x00455876),
]

TIMEOUT_CHECK_START = END
TIMEOUT_CHECK_END = 0x004555E6
TIMEOUT_CHECK_SHA256 = (
    "83a983995a285b3257a1213bdbe3fa05"
    "42bae0c9296a88fd8b22c1388abdf72c"
)
TIMEOUT_CHECK_CALLERS = [
    (0x004418C0, "13f051fe"),
    (0x00441BCA, "13f0ccfc"),
    (0x00441CF6, "13f036fc"),
]
TIMEOUT_CHECK_CALLEES = [
    (0x00455570, 0x005FA0A4),
    (0x00455582, 0x005FA0A4),
    (0x00455590, 0x004420D0),
    (0x004555D0, START),
    (0x004555DE, 0x004420E8),
]

FUNCTION = "open_cfw_freertos_task_internal_set_timeout_state"
TARGET_BYTES = "44f63421c2f207014a690260096841607047"
TARGET_SHA256 = (
    "8319202babe42ee571774682793c4c4c"
    "1a54c3a72826a92ba5c60273ba451c6a"
)
APPLE_OFFSET = 115_424
LINUX_OFFSET = 117_256
APPLE_RUNTIME_ADDRESS = 0x007B_0604
LINUX_RUNTIME_ADDRESS = 0x007B_0D2C
APPLE_REPLACEMENT = "5bf355b8" + "00bf" * 6
APPLE_REPLACEMENT_SHA256 = (
    "10fe042bd5164de04b51a0d421fdbb7c"
    "67d9ec2e9d4279bc727501d8418f6de2"
)
LINUX_REPLACEMENT = "5bf3e9bb" + "00bf" * 6
LINUX_REPLACEMENT_SHA256 = (
    "27ffb31c844aae9aad52cfe3c974c8b2"
    "eddf47d5d666b52eb48e0bdeb85f8b6e"
)
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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]

EVENT_OVERFLOW_READ = 1
EVENT_OVERFLOW_STORE = 2
EVENT_TICK_READ = 3
EVENT_TICK_STORE = 4

_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang")
    == "apple-clang",
    "production byte-exact build uses the reviewed Apple-clang profile",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


class RuntimeFreeRTOSTimeoutStateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=temporary_parent)
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / library_name("runtime_freertos_timeout_state")
        host_command = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(HOST_FIXTURE),
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
        cls.reset = cls.loaded.open_cfw_test_timeout_reset
        cls.reset.argtypes = [ctypes.c_int32, ctypes.c_uint32]
        cls.reset.restype = None
        cls.invoke = cls.loaded.open_cfw_test_timeout_invoke
        cls.invoke.argtypes = [
            ctypes.POINTER(ctypes.c_int32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        cls.invoke.restype = None
        cls.event_count = cls.loaded.open_cfw_test_timeout_event_count
        cls.event_count.argtypes = []
        cls.event_count.restype = ctypes.c_uint32
        cls.event_kind = cls.loaded.open_cfw_test_timeout_event_kind
        cls.event_kind.argtypes = [ctypes.c_uint32]
        cls.event_kind.restype = ctypes.c_uint32
        cls.event_value = cls.loaded.open_cfw_test_timeout_event_value
        cls.event_value.argtypes = [ctypes.c_uint32]
        cls.event_value.restype = ctypes.c_uint32

        cls.target_object = temporary / "runtime_freertos_timeout_state.o"
        subprocess.run(
            [
                clang,
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

        cls.apollo_overlay = apollo_overlay
        cls.config = json.loads(
            OVERLAY_CONFIG.read_text(encoding="utf-8")
        )
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]

        cls.production = None
        if (
            os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang"
        ) == "apple-clang":
            build_config = copy.deepcopy(cls.config)
            build_config["expected"] = {}
            unpinned_config = temporary / "overlay-unpinned-final.json"
            unpinned_config.write_text(
                json.dumps(build_config, indent=2) + "\n",
                encoding="utf-8",
            )
            cls.production = apollo_overlay.build(
                root=ROOT,
                config_path=unpinned_config,
                output_dir=temporary / "production",
                clang=clang,
                toolchain_profile="apple-clang",
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[start - BASE:end - BASE]

    def test_authenticated_upstream_and_local_source_are_pinned(self) -> None:
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, 223_695)
        self.assertEqual(
            sha256(UPSTREAM_TASKS),
            "14020d617b96dd2814e1211f6e3b645b"
            "cf5e2bd3179c23fe7dd16bc666fe9463",
        )
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verifier.stdout)

        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        self.assertIn(
            """void vTaskInternalSetTimeOutState( TimeOut_t * const pxTimeOut )
{
    /* For internal use only as it does not use a critical section. */
    pxTimeOut->xOverflowCount = xNumOfOverflows;
    pxTimeOut->xTimeOnEntering = xTickCount;
}""",
            upstream,
        )
        self.assertIn(
            "PRIVILEGED_DATA static volatile BaseType_t "
            "xNumOfOverflows = ( BaseType_t ) 0;",
            upstream,
        )
        self.assertIn(
            "PRIVILEGED_DATA static volatile TickType_t xTickCount",
            upstream,
        )

        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(sha256(SOURCE), SOURCE_SHA256)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(HEADER), HEADER_SHA256)
        self.assertEqual(HOST_FIXTURE.stat().st_size, HOST_FIXTURE_SIZE)
        self.assertEqual(sha256(HOST_FIXTURE), HOST_FIXTURE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "vTaskInternalSetTimeOutState()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455556, 0x00455566)",
            "OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_READ()",
            "OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_STORE(timeout, "
            "overflow_count)",
            "OPEN_CFW_FREERTOS_TIMEOUT_TICK_READ()",
            "OPEN_CFW_FREERTOS_TIMEOUT_TICK_STORE(timeout, tick_count)",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_TIMEOUT_TICK_COUNT_ADDRESS = "
            "0x20074A34U",
            "OPEN_CFW_FREERTOS_TIMEOUT_OVERFLOW_COUNT_ADDRESS = "
            "0x20074A48U",
            "sizeof(struct open_cfw_freertos_timeout_state) == 8U",
            "_Alignof(struct open_cfw_freertos_timeout_state) == 4U",
            "volatile open_cfw_freertos_timeout_base_type",
            "volatile open_cfw_freertos_timeout_tick_type",
        ):
            self.assertIn(token, header)

    def test_official_body_literals_and_timeout_layout_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            "36c5b0e499a68ac2493a497bdab9740fd"
            "3e7027730c26a9094eca47268a27863",
        )
        body = self.span(START, END)
        self.assertEqual(len(body), 16)
        self.assertEqual(body.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(body).hexdigest(), STOCK_SHA256)

        first, second = struct.unpack_from("<HH", body)
        self.assertEqual(first, 0xF8DF)
        self.assertEqual(second >> 12, 1)
        self.assertEqual(second & 0x0FFF, 0x5A0)
        self.assertEqual(
            ((START + 4) & ~3) + (second & 0x0FFF),
            OVERFLOW_LITERAL,
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(OVERFLOW_LITERAL, OVERFLOW_LITERAL + 4),
            )[0],
            OVERFLOW_WORD,
        )

        tick_instruction = struct.unpack_from("<H", body, 8)[0]
        self.assertEqual(tick_instruction & 0xF800, 0x4800)
        tick_immediate = tick_instruction & 0x00FF
        self.assertEqual(
            ((START + 8 + 4) & ~3) + tick_immediate * 4,
            TICK_LITERAL,
        )
        self.assertEqual(
            struct.unpack(
                "<I",
                self.span(TICK_LITERAL, TICK_LITERAL + 4),
            )[0],
            TICK_WORD,
        )
        self.assertEqual(body[4:].hex(), "096801609349096841607047")

        class TimeOut(ctypes.Structure):
            _fields_ = [
                ("overflow_count", ctypes.c_int32),
                ("time_on_entering", ctypes.c_uint32),
            ]

        self.assertEqual(ctypes.sizeof(TimeOut), 8)
        self.assertEqual(ctypes.alignment(TimeOut), 4)
        self.assertEqual(TimeOut.overflow_count.offset, 0)
        self.assertEqual(TimeOut.time_on_entering.offset, 4)

    def test_neighboring_released_identities_and_topology_are_exact(
        self,
    ) -> None:
        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        unordered_source = upstream.index(
            "void vTaskRemoveFromUnorderedEventList("
        )
        public_timeout_source = upstream.index(
            "void vTaskSetTimeOutState("
        )
        internal_timeout_source = upstream.index(
            "void vTaskInternalSetTimeOutState("
        )
        timeout_check_source = upstream.index(
            "BaseType_t xTaskCheckForTimeOut("
        )
        self.assertLess(unordered_source, public_timeout_source)
        self.assertLess(public_timeout_source, internal_timeout_source)
        self.assertLess(internal_timeout_source, timeout_check_source)
        self.assertIn(
            "prvResetNextTaskUnblockTime();",
            upstream[unordered_source:public_timeout_source],
        )
        self.assertIn(
            "vTaskInternalSetTimeOutState( pxTimeOut );",
            upstream[timeout_check_source:],
        )

        identities = {
            "vTaskRemoveFromUnorderedEventList": (
                UNORDERED_EVENT_START,
                UNORDERED_EVENT_END,
                218,
                UNORDERED_EVENT_SHA256,
            ),
            "xTaskCheckForTimeOut": (
                TIMEOUT_CHECK_START,
                TIMEOUT_CHECK_END,
                128,
                TIMEOUT_CHECK_SHA256,
            ),
        }
        for name, (start, end, size, digest) in identities.items():
            with self.subTest(function=name):
                body = self.span(start, end)
                self.assertEqual(len(body), size)
                self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

        self.assertEqual(UNORDERED_EVENT_END, START)
        self.assertEqual(END, TIMEOUT_CHECK_START)

        incoming = {name: [] for name in identities}
        outgoing = {name: [] for name in identities}
        wide_entries = {name: [] for name in identities}
        exterior_interior = {name: [] for name in identities}
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                for name, (start, end, _, _) in identities.items():
                    if target == start and not start <= address < end:
                        record = (address, encoded.hex())
                        if link:
                            incoming[name].append(record)
                        else:
                            wide_entries[name].append(record)
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        exterior_interior[name].append(
                            (address, target, link, encoded.hex())
                        )
                    if link and start <= address < end:
                        outgoing[name].append((address, target))

        self.assertEqual(
            incoming["vTaskRemoveFromUnorderedEventList"],
            UNORDERED_EVENT_CALLERS,
        )
        self.assertEqual(
            outgoing["vTaskRemoveFromUnorderedEventList"],
            UNORDERED_EVENT_CALLEES,
        )
        self.assertEqual(
            incoming["xTaskCheckForTimeOut"],
            TIMEOUT_CHECK_CALLERS,
        )
        self.assertEqual(
            outgoing["xTaskCheckForTimeOut"],
            TIMEOUT_CHECK_CALLEES,
        )
        self.assertEqual(
            wide_entries,
            {name: [] for name in identities},
        )
        self.assertEqual(
            exterior_interior,
            {name: [] for name in identities},
        )

        # The authenticated source places the public critical-section wrapper
        # here, but the two identified stock neighbors directly abut the
        # source-owned internal leaf.  The public wrapper was dead-stripped.
        self.assertEqual(
            (UNORDERED_EVENT_END, START, END, TIMEOUT_CHECK_START),
            (START, START, END, END),
        )

    def test_host_records_overflow_read_store_before_tick_read_store(
        self,
    ) -> None:
        cases = [
            (-123_456_789, 0x89ABCDEF),
            (-0x80000000, 0xFFFFFFFF),
            (0x7FFFFFFF, 0),
        ]
        for overflow_value, tick_value in cases:
            with self.subTest(
                overflow=overflow_value,
                tick=tick_value,
            ):
                output_overflow = ctypes.c_int32(0x11223344)
                output_tick = ctypes.c_uint32(0x55667788)
                self.reset(overflow_value, tick_value)
                self.invoke(
                    ctypes.byref(output_overflow),
                    ctypes.byref(output_tick),
                )

                self.assertEqual(output_overflow.value, overflow_value)
                self.assertEqual(output_tick.value, tick_value)
                self.assertEqual(self.event_count(), 4)
                self.assertEqual(
                    [self.event_kind(index) for index in range(4)],
                    [
                        EVENT_OVERFLOW_READ,
                        EVENT_OVERFLOW_STORE,
                        EVENT_TICK_READ,
                        EVENT_TICK_STORE,
                    ],
                )
                self.assertEqual(
                    [self.event_value(index) for index in range(4)],
                    [
                        overflow_value & 0xFFFFFFFF,
                        overflow_value & 0xFFFFFFFF,
                        tick_value,
                        tick_value,
                    ],
                )

    def test_target_object_is_one_relocation_free_18_byte_leaf(self) -> None:
        data, sections = self.apollo_overlay.parse_elf32(
            self.target_object
        )
        symbol_table = self.apollo_overlay.section_named(
            sections,
            ".symtab",
        )
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            symbols.append(
                (
                    self.apollo_overlay.elf_string(
                        strings,
                        fields[0],
                        "symbol",
                    ),
                    fields,
                )
            )
        function = next(
            fields for name, fields in symbols if name == FUNCTION
        )
        function_section = sections[int(function[5])]
        self.assertEqual(
            function_section["name"],
            f".text.{FUNCTION}",
        )
        self.assertEqual(int(function_section["flags"]), 0x6)
        self.assertEqual(int(function_section["alignment"]), 4)
        self.assertEqual((int(function[1]), int(function[2])), (1, 18))
        self.assertEqual(function[3] & 0x0F, 2)
        leaf = data[
            int(function_section["offset"]):
            int(function_section["offset"]) + int(function_section["size"])
        ]
        self.assertEqual(leaf.hex(), TARGET_BYTES)
        self.assertEqual(hashlib.sha256(leaf).hexdigest(), TARGET_SHA256)
        self.assertEqual(
            {
                name
                for name, fields in symbols
                if name and fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {FUNCTION},
        )
        self.assertEqual(
            {
                name
                for name, fields in symbols
                if name and fields[5] == 0
            },
            set(),
        )
        self.assertEqual(
            [
                section["name"]
                for section in sections
                if (
                    int(section["type"]) == 9
                    and int(section["info"]) == int(function_section["index"])
                    and int(section["size"]) != 0
                )
            ],
            [],
        )
        for prefix in (".data", ".bss", ".rodata"):
            self.assertFalse(
                any(
                    section["name"].startswith(prefix)
                    and int(section["size"]) != 0
                    for section in sections
                )
            )

    def test_official_topology_has_four_callers_and_no_bypass(self) -> None:
        calls = []
        jumps = []
        exterior_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, calls), (False, jumps)):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target == START:
                    observed.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    exterior_interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(calls, CALLERS)
        self.assertEqual(jumps, [])
        self.assertEqual(exterior_interior, [])
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in calls
                )
            ).hexdigest(),
            "00c5a45e0818672f879e7c38ad544eb3"
            "21184a295f3adb0fee7eb708a3483feb",
        )

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow.append((address, target, halfword))
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            normalized = value & ~1 if value & 1 else value
            if START <= normalized < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        caller_spans = {
            (0x004417EE, 0x00441952): (
                356,
                "d8a463345ca0e7754eb0808ebf3a725a3"
                "ca66541b6e85220b6d5459166aac11d",
            ),
            (0x00441B0A, 0x00441C44): (
                314,
                "f96de373691fb5d916ccbe25e0bc1d34"
                "74b918c16968b540b601fe6e36575560",
            ),
            (0x00441C44, 0x00441DA6): (
                354,
                "4d112cee107085a6606d4704c6f9edb4"
                "83264086cc9f954991ac76818c08b34c",
            ),
            (0x00455566, 0x004555E6): (
                128,
                "83a983995a285b3257a1213bdbe3fa05"
                "42bae0c9296a88fd8b22c1388abdf72c",
            ),
        }
        for (start, end), (size, digest) in caller_spans.items():
            caller = self.span(start, end)
            self.assertEqual(len(caller), size)
            self.assertEqual(hashlib.sha256(caller).hexdigest(), digest)

    def test_dual_profile_configuration_and_redirect_are_exact(self) -> None:
        leaf = next(
            leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] == FUNCTION
        )
        self.assertNotIn("profiles", leaf)
        self.assertEqual(
            {
                key: leaf["source"][key]
                for key in (
                    "path",
                    "size",
                    "sha256",
                    "license",
                    "upstream_commit",
                    "evidence",
                )
            },
            {
                "path": (
                    "components/shared/freertos/"
                    "runtime_freertos_timeout_state.c"
                ),
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "upstream_commit": (
                    "def7d2df2b0506d3d249334974f51e427c17a41c"
                ),
                "evidence": (
                    "docs/research/"
                    "freertos-timeout-state-source-boundary-audit.md"
                ),
            },
        )
        expected = {
            "size": 18,
            "sha256": TARGET_SHA256,
            "alignment": 4,
            "offset": APPLE_OFFSET,
            "unrelocated_sha256": TARGET_SHA256,
        }
        self.assertEqual(leaf["expected"], expected)
        self.assertEqual(leaf["relocations"], [])
        self.assertEqual(
            leaf["toolchain_profiles"]["linux-clang"],
            {
                "reviewed_version_prefix": (
                    "Homebrew clang version 22.1.8"
                ),
                "expected": {**expected, "offset": LINUX_OFFSET},
                "relocations": [],
            },
        )
        expected_functions = {
            "open_cfw_freertos_task_suspend_all",
            FUNCTION,
        }
        self.assertEqual(
            [
                item["function"]
                for item in self.config["relocated_leaves"]
                if item["function"] in expected_functions
            ],
            [
                "open_cfw_freertos_task_suspend_all",
                FUNCTION,
            ],
        )

        patch = next(
            patch
            for patch in self.config["patch_sites"]
            if patch["target_function"] == FUNCTION
        )
        self.assertEqual(
            patch,
            {
                "name": (
                    "replace_freertos_task_internal_set_timeout_state"
                ),
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            },
        )
        for target, replacement_hex, replacement_sha256 in (
            (
                APPLE_RUNTIME_ADDRESS,
                APPLE_REPLACEMENT,
                APPLE_REPLACEMENT_SHA256,
            ),
            (
                LINUX_RUNTIME_ADDRESS,
                LINUX_REPLACEMENT,
                LINUX_REPLACEMENT_SHA256,
            ),
        ):
            replacement = (
                self.apollo_overlay.encode_thumb_branch(
                    START,
                    target,
                    link=False,
                )
                + b"\x00\xbf" * 6
            )
            self.assertEqual(replacement.hex(), replacement_hex)
            self.assertEqual(
                hashlib.sha256(replacement).hexdigest(),
                replacement_sha256,
            )

    @_APPLE_ONLY
    def test_production_placement_redirect_aggregate_and_manifest_are_exact(
        self,
    ) -> None:
        self.assertIsNotNone(self.production)
        report_leaf = next(
            leaf
            for leaf in self.production["relocated_leaves"]
            if leaf["extraction"]["function"] == FUNCTION
        )
        self.assertEqual(
            report_leaf["placement"],
            {
                "alignment": 4,
                "offset": APPLE_OFFSET,
                "padding_before": 0,
                "runtime_address": APPLE_RUNTIME_ADDRESS,
                "runtime_address_hex": "0x007B0604",
                "size": 18,
            },
        )
        self.assertEqual(report_leaf["extraction"]["sha256"], TARGET_SHA256)
        self.assertEqual(report_leaf["extraction"]["relocation_count"], 0)

        overlay = (
            ROOT / self.production["overlay"]["artifact"]
        ).read_bytes()
        self.assertEqual(
            overlay[APPLE_OFFSET:APPLE_OFFSET + 18].hex(),
            TARGET_BYTES,
        )
        patch = next(
            patch
            for patch in self.production["overlay"]["patched_sites"]
            if patch["target_function"] == FUNCTION
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(patch["payload_offset"], 120_182)
        self.assertEqual(patch["target_address"], APPLE_RUNTIME_ADDRESS)
        self.assertEqual(replacement.hex(), APPLE_REPLACEMENT)
        self.assertEqual(
            hashlib.sha256(replacement).hexdigest(),
            APPLE_REPLACEMENT_SHA256,
        )
        self.assertEqual(
            (
                self.production["overlay"]["size"],
                self.production["overlay"]["sha256"],
                len(self.production["overlay"]["functions"]),
                len(self.production["overlay"]["patched_sites"]),
            ),
            (
                121_706,
                (
                    "9e5004af49fb14a22e7e7ed7357e4c10"
            "f87dc8da3a7fb4d7b97fcffcde804c43"
                ),
                615,
                578,
            ),
        )
        component = self.production["component"]
        self.assertEqual(
            {
                key: component[key]
                for key in (
                    "size",
                    "sha256",
                    "generated_patch_site_bytes",
                    "replaced_stock_function_bytes",
                    "source_owned_bytes",
                    "source_owned_in_place_bytes",
                    "opaque_base_bytes",
                )
            },
            {
                "size": 3_645_102,
                "sha256": (
                    "8722e5565bf54dade66fb751155c11eb"
            "d128d7a12853e3e4b8671c3c97807827"
                ),
                "generated_patch_site_bytes": 84_654,
                "replaced_stock_function_bytes": 84_836,
                "source_owned_bytes": 121_900,
                "source_owned_in_place_bytes": 182,
                "opaque_base_bytes": 3_438_528,
            },
        )

        manifest = json.loads(
            CORE_SOURCE_MANIFEST.read_text(encoding="utf-8")
        )
        self.assertEqual(
            manifest["package"],
            {
                "output_name": (
                    "g2-openCFW-s200_v2.2.6.10-core-source."
                    "evenota.bin"
                ),
                "expected_size": 4_423_556,
                "expected_sha256": (
                    "f2688fb35061283c05e9eb165d4f3eeb"
            "2cb2c4abd18cd28d074e58cb9da021db"
                ),
                "profiles": {
                    "linux-clang": {
                        "expected_size": 4_425_408,
                        "expected_sha256": (
                            "5598cb1f2a3b9a8b6101f61afcc5e24"
            "de54b01c3d5aa45396bf161344b3618bb"
                        ),
                    },
                },
            },
        )
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        selected_names = {
            "opaque_between_freertos_pc_task_get_name_and_task_increment_tick",
            "freertos_task_increment_tick_source_replacement",
            (
                "opaque_between_freertos_task_increment_tick_and_"
                "task_remove_from_event_list"
            ),
            "freertos_task_remove_from_event_list_source_replacement",
            "opaque_between_freertos_task_event_removal_functions",
            (
                "freertos_task_remove_from_unordered_event_list_"
                "source_replacement"
            ),
            "freertos_task_internal_set_timeout_state_source_replacement",
            "freertos_task_check_for_timeout_source_replacement",
            "apollo_freertos_task_internal_set_timeout_state_source_leaf",
        }
        selected = {
            region["name"]: (
                region["file_offset"],
                region["size"],
                region["target_address"],
                region["address_status"],
            )
            for region in regions
            if region["name"] in selected_names
        }
        self.assertEqual(
            selected,
            {
                (
                    "opaque_between_freertos_pc_task_get_name_and_task_"
                    "increment_tick"
                ): (118_616, 276, 0x0045_4F38, "official_blob"),
                "freertos_task_increment_tick_source_replacement": (
                    118_892,
                    338,
                    0x0045_504C,
                    "generated_source_entry_replacement",
                ),
                "opaque_between_freertos_task_increment_tick_and_"
                "task_remove_from_event_list": (
                    119_230,
                    466,
                    0x0045_519E,
                    "official_blob",
                ),
                "freertos_task_remove_from_event_list_source_replacement": (
                    119_696,
                    246,
                    0x0045_5370,
                    "generated_source_entry_replacement",
                ),
                "opaque_between_freertos_task_event_removal_functions": (
                    119_942,
                    22,
                    0x0045_5466,
                    "official_blob",
                ),
                (
                    "freertos_task_remove_from_unordered_event_list_"
                    "source_replacement"
                ): (
                    119_964,
                    218,
                    0x0045_547C,
                    "generated_source_entry_replacement",
                ),
                (
                    "freertos_task_internal_set_timeout_state_"
                    "source_replacement"
                ): (
                    120_182,
                    16,
                    START,
                    "generated_source_entry_replacement",
                ),
                "freertos_task_check_for_timeout_source_replacement": (
                    120_198,
                    128,
                    END,
                    "generated_source_entry_replacement",
                ),
                (
                    "apollo_freertos_task_internal_set_timeout_state_"
                    "source_leaf"
                ): (
                    3_638_820,
                    18,
                    APPLE_RUNTIME_ADDRESS,
                    "source_compiled",
                ),
            },
        )

    @staticmethod
    def narrow_branch_targets(
        address: int,
        halfword: int,
    ) -> list[int]:
        if halfword & 0xF800 == 0xE000:
            immediate = halfword & 0x07FF
            if immediate & 0x0400:
                immediate -= 0x0800
            return [address + 4 + immediate * 2]
        if (
            halfword & 0xF000 == 0xD000
            and ((halfword >> 8) & 0x0F) < 0x0E
        ):
            immediate = halfword & 0x00FF
            if immediate & 0x0080:
                immediate -= 0x0100
            return [address + 4 + immediate * 2]
        if halfword & 0xF500 == 0xB100:
            immediate = (
                ((halfword >> 9) & 1) << 6
                | ((halfword >> 3) & 0x1F) << 1
            )
            return [address + 4 + immediate]
        return []


if __name__ == "__main__":
    unittest.main()
