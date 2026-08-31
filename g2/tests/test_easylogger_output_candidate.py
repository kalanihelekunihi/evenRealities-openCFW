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
    ROOT / "components" / "shared" / "easylogger"
    / "runtime_easylogger_output_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_output_candidate_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_output_upstream_oracle_host.c"
)
UPSTREAM_SOURCE = ROOT / "third_party" / "easylogger" / "src" / "elog.c"
UPSTREAM_HEADER = ROOT / "third_party" / "easylogger" / "inc" / "elog.h"
UPSTREAM_CONFIG = (
    ROOT / "third_party" / "easylogger" / "inc" / "elog_cfg.h"
)
UPSTREAM_VERIFIER = (
    ROOT / "third_party" / "easylogger" / "verify_snapshot.py"
)
AUDIT = (
    ROOT / "docs" / "research"
    / "easylogger-output-source-candidate-audit.md"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
MAKEFILE = ROOT / "Makefile"

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
START = 0x0043_D574
END = 0x0043_D976
STOCK_SIZE = 1_026
STOCK_SHA256 = (
    "d7c5fd89997fc677ecce543af7c33cd0"
    "8614b832a47602f1fd895bb7ab45f90c"
)
FOLLOWING_BYTES = "00001b5b0000"
CALLER_COUNT = 6_239
CALLER_FIRST = 0x0043_C426
CALLER_LAST = 0x005F_9E7C
CALLER_SHA256 = (
    "2d4e701757c3ec84ae6c6b53b263872"
    "8c3da6d6121eb95579f3b4e13843be2a2"
)

UPSTREAM_PINS = {
    UPSTREAM_SOURCE: (
        28_740,
        "d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1",
    ),
    UPSTREAM_HEADER: (
        10_428,
        "2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48",
    ),
    UPSTREAM_CONFIG: (
        3_995,
        "bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073",
    ),
}

# Production-source integrity pins make silent source/oracle/audit drift fail
# closed.  The historical candidate filename remains stable for audit links.
LOCAL_PINS = {
    SOURCE: (
        13_637,
        "be6e0f1f6cc5617eeb0aed75f4e7e9e437fad20f8ea9c0cab0e4242529321ff3",
    ),
    HEADER: (
        10_036,
        "0c9d95327fafab1b9f9574bde390b3a8cc760835d6dbad4fff99b6aad053e195",
    ),
    CANDIDATE_FIXTURE: (
        19_249,
        "2fc0b1060712c54c1291d0ac5c8281374cfa9363b882bcbeb2aa5fd4dae0db81",
    ),
    UPSTREAM_FIXTURE: (
        11_015,
        "e3f4983c3b301c8189b713d41e64bab433a842d9032b826ed8af08f2bf9f4c7d",
    ),
    AUDIT: (
        14_243,
        "cb8f37460c27f2df15cca70d32f8f52c6ef09ab6985ead47b134856864108382",
    ),
}

FUNCTION = "open_cfw_easylogger_output"
FUNCTION_SECTION = ".text." + FUNCTION
RODATA_SECTION = ".rodata.str1.1"
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
TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0",
        "text_size": 1_614,
        "text_alignment": 4,
        "text_sha256": (
            "479d6304345334af023d5a1ee464a88b"
            "76e05b6d93596c3addc186df516a25dc"
        ),
        "rodata_size": 164,
        "rodata_alignment": 1,
        "rodata_sha256": (
            "22de23c10c0cef980a625e949124f33e9"
            "e7b65815986f889c6c2fb3b1e4ed6ca"
        ),
        "closure_size": 1_778,
        "closure_sha256": (
            "3296e96fdbd2e5b138b9375e67b6d3c"
            "bde109d06b62a5e9d0492b317f4deb28b"
        ),
        "relocation_sha256": (
            "fcc72ad8c65860433a6c57097fe08542"
            "a9ee5d042f54ff9c372e76f016fbe98a"
        ),
        "outgoing_sha256": (
            "e71c6b182672f1396d6897055afc5ad5"
            "107faba5a13ae5b9561f8d702f906d3c"
        ),
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "text_size": 1_618,
        "text_alignment": 4,
        "text_sha256": (
            "315168b42e7f58b9bc9b14a47511866f"
            "8fffa930f8eb8499631cab34d9ade958"
        ),
        "rodata_size": 164,
        "rodata_alignment": 1,
        "rodata_sha256": (
            "22de23c10c0cef980a625e949124f33e9"
            "e7b65815986f889c6c2fb3b1e4ed6ca"
        ),
        "closure_size": 1_782,
        "closure_sha256": (
            "21bb86cbf5bb77891a8063eb5111f6c2"
            "02b55e4bc1416ee57974cf6a351aa918"
        ),
        "relocation_sha256": (
            "c2bfd1d4a98235667cc72c12386a3c69"
            "6bb3f71cf82016e801ccb36bb6e2ea4e"
        ),
        "outgoing_sha256": (
            "b116bc27c2abe769da9bc4e7e448c5c4"
            "b2f9a9c22f2f6ed0449fef6757072103"
        ),
    },
}
UNDEFINED_SYMBOLS = [
    "open_cfw_easylogger_get_filter_tag_level",
    "open_cfw_easylogger_get_fmt_enabled",
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
    "open_cfw_easylogger_helpers_get_logger",
    "open_cfw_easylogger_output_lock",
    "open_cfw_easylogger_output_unlock",
    "open_cfw_easylogger_strcpy",
    "open_cfw_g2_easylogger_async_submit",
]
OUTGOING_SYMBOLS = set(UNDEFINED_SYMBOLS) | {FUNCTION}
RODATA_HEX = (
    "6c6576656c203c3d20454c4f475f4c564c5f564552424f534500656c6f675f6f"
    "757470757400656c6f6700282573292068617320617373657274206661696c6564"
    "2061742025733a256c642e001b5b0020005b005d200028003a00256c64002900"
    "1b5b306d000a0033353b32326d0033313b32326d0033333b32326d0033363b32"
    "326d0033323b32326d0033343b32326d00412f00452f00572f00492f00442f00"
    "562f00"
)
FIRST_SEMANTIC_PREFIX = "2de9f04f8fb01546eff3058212b1"

EVENT_IPSR = 1
EVENT_STATE = 2
EVENT_TAG_LEVEL = 3
EVENT_LOCK = 4
EVENT_BUFFER = 5
EVENT_APPEND = 6
EVENT_MESSAGE_FORMAT = 11
EVENT_SINK = 12
EVENT_UNLOCK = 13
EVENT_ASSERT = 14

FMT_LEVEL = 0x01
FMT_TAG = 0x02
FMT_TIME = 0x04
FMT_PROCESS = 0x08
FMT_THREAD = 0x10
FMT_DIRECTORY = 0x20
FMT_FUNCTION = 0x40
FMT_LINE = 0x80


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    return ()


class HostHarness:
    def __init__(self, library: Path) -> None:
        self.loaded = ctypes.CDLL(str(library))
        self.reset = self.loaded.open_cfw_test_easylogger_output_reset
        self.reset.argtypes = [ctypes.c_uint32]
        self.set_output = (
            self.loaded.open_cfw_test_easylogger_output_set_output_enabled
        )
        self.set_output.argtypes = [ctypes.c_uint32]
        self.set_global = (
            self.loaded.open_cfw_test_easylogger_output_set_global_level
        )
        self.set_global.argtypes = [ctypes.c_uint32]
        self.set_color = self.loaded.open_cfw_test_easylogger_output_set_color
        self.set_color.argtypes = [ctypes.c_uint32]
        self.set_mask = self.loaded.open_cfw_test_easylogger_output_set_mask
        self.set_mask.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        self.set_filter = self.loaded.open_cfw_test_easylogger_output_set_filter
        self.set_filter.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
        self.set_tag_level = (
            self.loaded.open_cfw_test_easylogger_output_set_tag_level
        )
        self.set_tag_level.argtypes = [
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.set_port = (
            self.loaded.open_cfw_test_easylogger_output_set_port_text
        )
        self.set_port.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]
        self.force = (
            self.loaded.open_cfw_test_easylogger_output_force_formatter
        )
        self.force.argtypes = [
            ctypes.c_uint32,
            ctypes.c_int32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.emit_text = (
            self.loaded.open_cfw_test_easylogger_output_emit_text
        )
        self.emit_text.argtypes = [
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_char_p,
        ]
        self.emit_integer = (
            self.loaded.open_cfw_test_easylogger_output_emit_integer
        )
        self.emit_integer.argtypes = [
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_long,
            ctypes.c_char_p,
            ctypes.c_int32,
        ]
        self.sink_data = (
            self.loaded.open_cfw_test_easylogger_output_sink_data
        )
        self.sink_data.restype = ctypes.c_void_p
        self.sink_length = (
            self.loaded.open_cfw_test_easylogger_output_sink_length
        )
        self.sink_length.restype = ctypes.c_uint32
        self.sink_level = (
            self.loaded.open_cfw_test_easylogger_output_sink_level
        )
        self.sink_level.restype = ctypes.c_uint32
        self.sink_calls = (
            self.loaded.open_cfw_test_easylogger_output_sink_calls
        )
        self.sink_calls.restype = ctypes.c_uint32
        self.event_count = (
            self.loaded.open_cfw_test_easylogger_output_event_count
        )
        self.event_count.restype = ctypes.c_uint32
        self.event = self.loaded.open_cfw_test_easylogger_output_event
        self.event.argtypes = [ctypes.c_uint32]
        self.event.restype = ctypes.c_uint32
        self.lock_depth = (
            self.loaded.open_cfw_test_easylogger_output_lock_depth_value
        )
        self.lock_depth.restype = ctypes.c_uint32

    def result(self) -> tuple[bytes, int, int, list[int]]:
        length = int(self.sink_length())
        data = ctypes.string_at(self.sink_data(), length)
        events = [
            int(self.event(index))
            for index in range(int(self.event_count()))
        ]
        return data, length, int(self.sink_level()), events


class EasyLoggerOutputCandidateTests(unittest.TestCase):
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

        libraries = {}
        for name, fixture in (
            ("candidate", CANDIDATE_FIXTURE),
            ("upstream", UPSTREAM_FIXTURE),
        ):
            library = temporary / library_name("easylogger-output-" + name)
            command = [
                cls.clang,
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
            ]
            if name == "upstream":
                command.extend([
                    "-I",
                    str(ROOT / "third_party" / "easylogger" / "inc"),
                ])
            command.append(str(fixture))
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", "-o", str(library)])
            else:
                command.extend(["-shared", "-fPIC", "-o", str(library)])
            subprocess.run(command, check=True, capture_output=True, text=True)
            libraries[name] = library
        cls.candidate = HostHarness(libraries["candidate"])
        cls.upstream = HostHarness(libraries["upstream"])

        cls.target_objects = [temporary / "candidate-1.o", temporary / "candidate-2.o"]
        for output in cls.target_objects:
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(output),
                ],
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
        cls.symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.elf_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.symbols.append((name, fields))
        cls.relocations = []
        text = apollo_overlay.section_named(cls.sections, FUNCTION_SECTION)
        for section in cls.sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(text["index"])
            ):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II",
                        cls.elf_data,
                        int(section["offset"]) + index * 8,
                    )
                    cls.relocations.append((
                        offset,
                        information & 0xFF,
                        cls.symbols[information >> 8][0],
                    ))

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def compare_pair(
        self,
        configure,
        emit,
    ) -> tuple[bytes, int, int, list[int]]:
        results = []
        for harness in (self.candidate, self.upstream):
            harness.reset(0)
            configure(harness)
            emit(harness)
            self.assertEqual(int(harness.lock_depth()), 0)
            results.append(harness.result())
        self.assertEqual(results[0][:3], results[1][:3])
        return results[0]

    def test_authenticated_upstream_and_local_candidate_are_pinned(self) -> None:
        for path, (size, digest) in UPSTREAM_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("EasyLogger 2.2.99 source-equivalent", verifier.stdout)
        self.assertIn("file hashes: OK", verifier.stdout)
        for path, (size, digest) in LOCAL_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "Production bounded Apollo-main adaptation",
            "OPEN_CFW_EASYLOGGER_OUTPUT_READ_IPSR()",
            "open_cfw_easylogger_get_filter_tag_level(tag)",
            "open_cfw_g2_easylogger_async_submit(log_buffer, log_length, level)",
            "OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF",
            "OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE - log_length",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_EASYLOGGER_OUTPUT_LEVEL_COUNT = 6",
            "OPEN_CFW_EASYLOGGER_OUTPUT_LINE_BUFFER_SIZE = 1024",
            "OPEN_CFW_EASYLOGGER_OUTPUT_TAG_MAX = 30",
            "OPEN_CFW_EASYLOGGER_OUTPUT_KEYWORD_MAX = 16",
            "OPEN_CFW_EASYLOGGER_OUTPUT_TAG_LEVEL_COUNT = 5",
            "OPEN_CFW_EASYLOGGER_OUTPUT_ASSERT_LINE = 572",
            "OPEN_CFW_EASYLOGGER_OUTPUT_VSNPRINTF_ADDRESS = 0x0044B76CU",
        ):
            self.assertIn(token, header)
        self.assertEqual(header.count("| 1U)"), 6)

    def test_official_span_and_complete_caller_topology_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        body = self.application[START - BASE:END - BASE]
        self.assertEqual(len(body), STOCK_SIZE)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(
            self.application[END - BASE:END - BASE + 6].hex(),
            FOLLOWING_BYTES,
        )

        callers = []
        entry_wide_branches = []
        external_wide_interiors = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link in (True, False):
                target = wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target == START:
                    (callers if link else entry_wide_branches).append(address)
                if (
                    target is not None
                    and START < target < END
                    and not START <= address < END
                ):
                    external_wide_interiors.append((address, target, link))
        self.assertEqual(len(callers), CALLER_COUNT)
        self.assertEqual((callers[0], callers[-1]), (CALLER_FIRST, CALLER_LAST))
        self.assertEqual(
            sha256(",".join(f"{site:08X}" for site in callers).encode()),
            CALLER_SHA256,
        )
        self.assertEqual(entry_wide_branches, [])
        self.assertEqual(external_wide_interiors, [])

        external_narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    external_narrow.append((address, target))
        self.assertEqual(external_narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1 and START <= target < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

    def test_target_text_rodata_closure_and_relocations_are_exact(self) -> None:
        data2, sections2 = self.apollo_overlay.parse_elf32(
            self.target_objects[1]
        )
        self.assertEqual(self.elf_data, data2)
        self.assertEqual(self.sections, sections2)

        text = self.apollo_overlay.section_named(
            self.sections,
            FUNCTION_SECTION,
        )
        rodata = self.apollo_overlay.section_named(
            self.sections,
            RODATA_SECTION,
        )
        text_bytes = self.elf_data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        rodata_bytes = self.elf_data[
            int(rodata["offset"]):
            int(rodata["offset"]) + int(rodata["size"])
        ]
        pin = TARGET_PINS[self.profile]
        self.assertEqual(int(text["size"]), pin["text_size"])
        self.assertEqual(int(text["alignment"]), pin["text_alignment"])
        self.assertEqual(sha256(text_bytes), pin["text_sha256"])
        self.assertEqual(int(rodata["size"]), pin["rodata_size"])
        self.assertEqual(int(rodata["alignment"]), pin["rodata_alignment"])
        self.assertEqual(sha256(rodata_bytes), pin["rodata_sha256"])
        self.assertEqual(rodata_bytes.hex(), RODATA_HEX)
        self.assertEqual(len(text_bytes + rodata_bytes), pin["closure_size"])
        self.assertEqual(
            sha256(text_bytes + rodata_bytes),
            pin["closure_sha256"],
        )
        self.assertTrue(text_bytes.hex().startswith(FIRST_SEMANTIC_PREFIX))

        relocation_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in self.relocations
        ).encode()
        outgoing = [
            relocation
            for relocation in self.relocations
            if relocation[2].startswith("open_cfw_")
        ]
        outgoing_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in outgoing
        ).encode()
        self.assertEqual(len(self.relocations), 109)
        self.assertEqual(sha256(relocation_record), pin["relocation_sha256"])
        self.assertEqual(len(outgoing), 45)
        self.assertEqual(sha256(outgoing_record), pin["outgoing_sha256"])
        for _, kind, symbol in self.relocations:
            if kind == 10:
                self.assertIn(symbol, OUTGOING_SYMBOLS)
            else:
                self.assertIn(kind, (49, 50))
                self.assertTrue(symbol.startswith(".L.str"))
        undefined = sorted(
            name
            for name, fields in self.symbols
            if name and fields[5] == 0
        )
        self.assertEqual(undefined, UNDEFINED_SYMBOLS)
        functions = [
            name
            for name, fields in self.symbols
            if name and fields[5] != 0 and fields[3] & 0x0F == 2
        ]
        self.assertEqual(functions, [FUNCTION])
        writable_allocated = [
            section["name"]
            for section in self.sections
            if int(section["size"]) != 0
            and int(section["flags"]) & 0x02
            and int(section["flags"]) & 0x01
        ]
        self.assertEqual(writable_allocated, [])

    def test_audited_candidate_is_the_exact_production_closure(self) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
        production_text = "\n".join((
            json.dumps(overlay, sort_keys=True),
            json.dumps(manifest, sort_keys=True),
            MAKEFILE.read_text(encoding="utf-8"),
        ))
        functions = overlay.get("functions", [])
        output_index = functions.index(FUNCTION)
        self.assertEqual(functions[output_index - 2:output_index + 1], [
            "open_cfw_g2_easylogger_async_record_build_single_owner",
            "open_cfw_g2_easylogger_async_submit",
            FUNCTION,
        ])
        self.assertIn(SOURCE.name, production_text)
        leaves = {
            leaf["function"]: leaf
            for leaf in overlay["relocated_leaves"]
            if leaf["function"] in {
                "open_cfw_g2_easylogger_async_record_build_single_owner",
                "open_cfw_g2_easylogger_async_submit",
                FUNCTION,
            }
        }
        self.assertTrue(leaves[FUNCTION]["strict_relocation_contract"])
        self.assertEqual(leaves[FUNCTION]["expected"]["offset"], 118_916)
        self.assertEqual(
            leaves[FUNCTION]["expected"]["closure_size"],
            1_778,
        )
        self.assertEqual(len(leaves[FUNCTION]["relocations"]), 109)
        sites = {
            site["runtime_address"]: site
            for site in overlay["patch_sites"]
            if site["runtime_address"] == START
        }
        self.assertEqual(sites[START]["target_function"], FUNCTION)
        self.assertEqual(sites[START]["expected_size"], STOCK_SIZE)
        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        replacement = next(
            region for region in regions
            if region.get("target_address") == START
        )
        self.assertEqual(
            replacement["address_status"],
            "generated_source_entry_replacement",
        )
        appended = next(
            region for region in regions
            if region.get("name") == "apollo_easylogger_output_source_text"
        )
        self.assertEqual(appended["size"], 1_614)
        self.assertEqual(appended["address_status"], "source_compiled")

    def test_nonzero_ipsr_returns_before_every_observable_access(self) -> None:
        invalid = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_emit_invalid_interrupt
        )
        invalid.argtypes = []
        invalid.restype = None
        assert_calls = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_assert_calls
        )
        assert_calls.restype = ctypes.c_uint32

        for ipsr in (1, 15, 511):
            with self.subTest(ipsr=ipsr):
                self.candidate.reset(ipsr)
                invalid()
                self.assertEqual(self.candidate.result()[3], [EVENT_IPSR])
                self.assertEqual(int(self.candidate.sink_calls()), 0)
                self.assertEqual(int(assert_calls()), 0)
                self.assertEqual(int(self.candidate.lock_depth()), 0)

    def test_upstream_differential_covers_levels_colors_masks_and_tags(self) -> None:
        colors = [b"35;22m", b"31;22m", b"33;22m", b"36;22m", b"32;22m", b"34;22m"]
        levels = [b"A/", b"E/", b"W/", b"I/", b"D/", b"V/"]
        for level in range(6):
            with self.subTest(level=level):
                data, length, sink_level, _ = self.compare_pair(
                    lambda harness: None,
                    lambda harness, level=level: harness.emit_text(
                        level, b"tag", b"file.c", b"func", 42, b"message"
                    ),
                )
                self.assertEqual(length, len(data))
                self.assertEqual(sink_level, level)
                self.assertTrue(data.startswith(b"\x1b[" + colors[level] + levels[level]))
                self.assertTrue(data.endswith(b"message\x1b[0m\n"))

        for tag_length in (0, 15, 16, 30, 31):
            tag = b"T" * tag_length
            with self.subTest(tag_length=tag_length):
                data, _, _, _ = self.compare_pair(
                    lambda harness: (
                        harness.set_color(0),
                        harness.set_mask(3, FMT_LEVEL | FMT_TAG),
                    ),
                    lambda harness, tag=tag: harness.emit_text(
                        3, tag, None, None, 0, b"body"
                    ),
                )
                padding = b" " * max(15 - tag_length, 0)
                self.assertEqual(data, b"I/" + tag + padding + b" body\n")

        port_masks = [
            sum(
                bit
                for selected, bit in zip(
                    selection,
                    (FMT_TIME, FMT_PROCESS, FMT_THREAD),
                )
                if selected
            )
            for selection in (
                (False, False, True),
                (False, True, False),
                (False, True, True),
                (True, False, False),
                (True, False, True),
                (True, True, False),
                (True, True, True),
            )
        ]
        matrix = [
            0,
            FMT_LEVEL,
            FMT_TAG,
            *port_masks,
            FMT_DIRECTORY,
            FMT_FUNCTION,
            FMT_LINE,
            0xFF,
        ]
        for mask in matrix:
            with self.subTest(mask=mask):
                self.compare_pair(
                    lambda harness, mask=mask: (
                        harness.set_color(0),
                        harness.set_mask(4, mask),
                        harness.set_port(b"T", b"P", b"R"),
                    ),
                    lambda harness: harness.emit_integer(
                        4, b"mask", b"dir/file.c", b"work", 9999,
                        b" value=%d", 73,
                    ),
                )

        for line in (-1000, -999, -1, 0, 1, 999, 9999, 10000):
            with self.subTest(line=line):
                self.compare_pair(
                    lambda harness: (
                        harness.set_color(0),
                        harness.set_mask(2, FMT_LINE),
                    ),
                    lambda harness, line=line: harness.emit_text(
                        2, b"line", None, None, line, b" body"
                    ),
                )

    def test_upstream_differential_covers_all_filter_gates(self) -> None:
        cases = [
            (
                "output-disabled",
                lambda h: h.set_output(0),
                b"allow",
                0,
            ),
            (
                "global-level",
                lambda h: h.set_global(2),
                b"allow",
                0,
            ),
            (
                "tag-level",
                lambda h: h.set_tag_level(0, b"allow", 2, 1),
                b"allow",
                0,
            ),
            (
                "tag-substring-miss",
                lambda h: h.set_filter(b"needle", b""),
                b"allow",
                0,
            ),
            (
                "tag-substring-hit",
                lambda h: h.set_filter(b"low", b""),
                b"allow-low-tag",
                1,
            ),
        ]
        for name, configure, tag, expected_calls in cases:
            with self.subTest(name=name):
                self.compare_pair(
                    configure,
                    lambda harness, tag=tag: harness.emit_text(
                        3, tag, None, None, 0, b"message"
                    ),
                )
                self.assertEqual(int(self.candidate.sink_calls()), expected_calls)
                self.assertEqual(int(self.upstream.sink_calls()), expected_calls)

        self.candidate.reset(0)
        self.candidate.set_global(2)
        self.candidate.emit_text(3, b"tag", None, None, 0, b"message")
        events = self.candidate.result()[3]
        self.assertEqual(events, [EVENT_IPSR, EVENT_STATE])

    def test_formatter_boundaries_keyword_order_and_locking_match_upstream(self) -> None:
        for color in (0, 1):
            for result, write in ((0, 0), (1023, 1023), (1024, 1024), (1025, 1024), (-1, 32)):
                with self.subTest(color=color, result=result, write=write):
                    data, length, _, _ = self.compare_pair(
                        lambda h, color=color, result=result, write=write: (
                            h.set_color(color),
                            h.set_mask(1, 0),
                            h.force(1, result, write, ord("X")),
                        ),
                        lambda h: h.emit_text(
                            1, b"tag", None, None, 0, b"ignored"
                        ),
                    )
                    if result == 0:
                        self.assertEqual(length, 13 if color else 1)
                    elif color:
                        self.assertEqual(length, 1024)
                        self.assertTrue(data.endswith(b"\x1b[0m\n"))
                    else:
                        self.assertEqual(length, 1020)
                        self.assertTrue(data.endswith(b"\n"))

        data, _, _, events = self.compare_pair(
            lambda h: (
                h.set_color(1),
                h.set_mask(3, 0),
                h.set_filter(b"", b"needle"),
            ),
            lambda h: h.emit_text(3, b"tag", None, None, 0, b"needle"),
        )
        self.assertEqual(data, b"\x1b[36;22mneedle\x1b[0m\n")
        self.assertLess(events.index(EVENT_LOCK), events.index(EVENT_BUFFER))
        self.assertLess(events.index(EVENT_BUFFER), events.index(EVENT_APPEND))
        self.assertLess(events.index(EVENT_MESSAGE_FORMAT), events.index(EVENT_SINK))
        self.assertEqual(events[-1], EVENT_UNLOCK)

        for keyword in (b"absent", b"\x1b[0m", b"\n"):
            with self.subTest(keyword=keyword):
                self.compare_pair(
                    lambda h, keyword=keyword: (
                        h.set_color(1),
                        h.set_mask(3, 0),
                        h.set_filter(b"", keyword),
                    ),
                    lambda h: h.emit_text(
                        3, b"tag", None, None, 0, b"message"
                    ),
                )
                self.assertEqual(int(self.candidate.sink_calls()), 0)
                candidate_events = self.candidate.result()[3]
                self.assertNotIn(EVENT_SINK, candidate_events)
                self.assertEqual(candidate_events[-1], EVENT_UNLOCK)

    def test_returning_assert_hook_identity_precedes_state_access(self) -> None:
        assert_calls = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_assert_calls
        )
        assert_calls.restype = ctypes.c_uint32
        assert_line = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_assert_line
        )
        assert_line.restype = ctypes.c_uint32
        assert_expression = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_assert_expression_value
        )
        assert_expression.restype = ctypes.c_char_p
        assert_function = (
            self.candidate.loaded
            .open_cfw_test_easylogger_output_assert_function_value
        )
        assert_function.restype = ctypes.c_char_p

        self.candidate.reset(0)
        self.candidate.set_output(0)
        self.candidate.emit_text(6, b"tag", None, None, 0, b"message")
        self.assertEqual(int(assert_calls()), 1)
        self.assertEqual(int(assert_line()), 572)
        self.assertEqual(assert_expression(), b"level <= ELOG_LVL_VERBOSE")
        self.assertEqual(assert_function(), b"elog_output")
        self.assertEqual(
            self.candidate.result()[3],
            [EVENT_IPSR, EVENT_ASSERT, EVENT_STATE],
        )
        self.assertEqual(int(self.candidate.sink_calls()), 0)


if __name__ == "__main__":
    unittest.main()
