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
    ROOT
    / "components"
    / "shared"
    / "freertos"
    / "runtime_freertos_task_check_free_stack_space.c"
)
HEADER = SOURCE.with_suffix(".h")
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
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

SOURCE_SIZE = 2_269
SOURCE_SHA256 = (
    "ba8cd2018984f4e6a131698d86a0eb4a"
    "bd0d07dd1e81e75979211f00bf3904de"
)
HEADER_SIZE = 1_267
HEADER_SHA256 = (
    "f87ee206a0ab1f62b2b93478e5ca6cf"
    "461dc96bfb047af98766b5849a4434d2a"
)
UPSTREAM_SIZE = 223_695
UPSTREAM_SHA256 = (
    "14020d617b96dd2814e1211f6e3b645bc"
    "f5e2bd3179c23fe7dd16bc666fe9463"
)
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
START = 0x0045_5820
END = 0x0045_5836
STOCK_BYTES = "0100002001e0491c401c0a78a52afad0800880b27047"
STOCK_SHA256 = (
    "4719035f92eec4dbde4be499b966bb24"
    "eead59d609a3b0f362724e7efe616048"
)
CALLER_START = 0x0045_5728
CALLER_END = 0x0045_57A8
CALLER_SHA256 = (
    "53d97f8c2e506f69df7908f9b3d2c644"
    "fd4f21b456f5961311f1ce34d975f626"
)
CALLER = 0x0045_579A
CALLER_ENCODING = "00f041f8"
CALLER_ADDRESS_SHA256 = (
    "500b947255a4da26c3ce4d43573e25036"
    "0f3068a7ab9c330fa2b88389dc14b97"
)
CALLER_RECORD_SHA256 = (
    "3573325d452b97c91ecc9e6ddb2a6188"
    "e7fc9c9fe0c37b25dc2344f6d18be4b8"
)
RAW_ENTRY_FALSE_POSITIVE = (0x0045_6353, 0x0045_5820)
FUNCTION = "open_cfw_freertos_task_check_free_stack_space"
FUNCTION_SECTION = ".text." + FUNCTION
TARGET_FUNCTION_BYTES = (
    "0178a5291ebf002080b27047022100bf421812f8013ca52b0bd1435ca52b0bd1"
    "5378a52b07d192780431a52af0d0023902e0013900e00131880880b27047"
)
TARGET_FUNCTION_SHA256 = (
    "ff66515dc9532c1f35f76e48b2f800e6"
    "6630027d52910645200832c0c32f0802"
)
PRODUCTION_PINS = {
    "apple-clang": {
        "size": 62,
        "sha256": TARGET_FUNCTION_SHA256,
        "alignment": 4,
            "offset": 118_412,
        "unrelocated_sha256": TARGET_FUNCTION_SHA256,
    },
    "linux-clang": {
        "size": 62,
        "sha256": TARGET_FUNCTION_SHA256,
        "alignment": 4,
        "offset": 120_272,
        "unrelocated_sha256": TARGET_FUNCTION_SHA256,
    },
}
PRODUCTION_ORDER = [
    "open_cfw_freertos_task_remove_from_event_list",
    "open_cfw_freertos_queue_give_from_isr",
    FUNCTION,
]

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

PRISTINE_ORACLE_SOURCE = r"""
typedef unsigned char uint8_t;
typedef unsigned short configSTACK_DEPTH_TYPE;
typedef unsigned int uint32_t;
typedef unsigned int StackType_t;

#define tskSTACK_FILL_BYTE (0xa5U)
#define portSTACK_GROWTH (-1)

__attribute__((used, noinline))
configSTACK_DEPTH_TYPE open_cfw_test_pristine_task_check_free_stack_space(
    const uint8_t * pucStackByte )
{
    uint32_t ulCount = 0U;

    while( *pucStackByte == ( uint8_t ) tskSTACK_FILL_BYTE )
    {
        pucStackByte -= portSTACK_GROWTH;
        ulCount++;
    }

    ulCount /= ( uint32_t ) sizeof( StackType_t );

    return ( configSTACK_DEPTH_TYPE ) ulCount;
}
"""


def sha256(data: bytes) -> str:
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
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
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
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


class FreeRTOSTaskCheckFreeStackSpaceCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE_SIZE:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        oracle = temporary / "pristine_oracle.c"
        oracle.write_text(PRISTINE_ORACLE_SOURCE, encoding="utf-8")
        library = temporary / library_name("freertos_stack_space_candidate")
        host_command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(SOURCE),
            str(oracle),
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
        cls.candidate = getattr(cls.loaded, FUNCTION)
        cls.candidate.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.candidate.restype = ctypes.c_uint16
        cls.oracle = (
            cls.loaded
            .open_cfw_test_pristine_task_check_free_stack_space
        )
        cls.oracle.argtypes = [ctypes.POINTER(ctypes.c_uint8)]
        cls.oracle.restype = ctypes.c_uint16

        cls.target_object = temporary / "candidate.o"
        subprocess.run(
            [
                cls.clang,
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

        cls.elf_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_object
        )
        symbol_table = apollo_overlay.section_named(
            cls.sections,
            ".symtab",
        )
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
            name: fields
            for name, fields in cls.parsed_symbols
            if name
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
                        str(section["name"]),
                        str(target["name"]),
                        offset,
                        information & 0xFF,
                        cls.parsed_symbols[information >> 8][0],
                    )
                )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def invoke_pair(self, fill_bytes: int) -> tuple[int, int]:
        guard = 16
        sentinel = 0x5A
        size = guard + fill_bytes + 1 + guard
        buffer = (ctypes.c_uint8 * size)()
        for index in range(size):
            buffer[index] = (index * 29 + 0x31) & 0xFF
        for index in range(fill_bytes):
            buffer[guard + index] = 0xA5
        buffer[guard + fill_bytes] = sentinel
        before = bytes(buffer)
        pointer = ctypes.cast(
            ctypes.byref(buffer, guard),
            ctypes.POINTER(ctypes.c_uint8),
        )
        candidate = int(self.candidate(pointer))
        oracle = int(self.oracle(pointer))
        self.assertEqual(bytes(buffer), before)
        self.assertEqual(buffer[guard + fill_bytes], sentinel)
        self.assertEqual(bytes(buffer[:guard]), before[:guard])
        self.assertEqual(
            bytes(buffer[guard + fill_bytes + 1:]),
            before[guard + fill_bytes + 1:],
        )
        return candidate, oracle

    def test_authenticated_source_attribution_and_configuration_guards(
        self,
    ) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER.read_bytes()), HEADER_SHA256)
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, UPSTREAM_SIZE)
        self.assertEqual(
            sha256(UPSTREAM_TASKS.read_bytes()),
            UPSTREAM_SHA256,
        )

        upstream = UPSTREAM_TASKS.read_text(encoding="utf-8")
        for token in (
            "static configSTACK_DEPTH_TYPE prvTaskCheckFreeStackSpace(",
            "while( *pucStackByte == ( uint8_t ) tskSTACK_FILL_BYTE )",
            "pucStackByte -= portSTACK_GROWTH;",
            "ulCount /= ( uint32_t ) sizeof( StackType_t );",
            "return ( configSTACK_DEPTH_TYPE ) ulCount;",
        ):
            self.assertIn(token, upstream)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "prvTaskCheckFreeStackSpace()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x00455820, 0x00455836)",
            "__UINT32_TYPE__ count = 0U;",
            "stack_byte -= OPEN_CFW_FREERTOS_STACK_GROWTH;",
            "count /= (__UINT32_TYPE__)"
            "sizeof(open_cfw_freertos_stack_type);",
            "return (open_cfw_freertos_stack_depth_type)count;",
            "candidate",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_STACK_FILL_BYTE = 0xA5U",
            "OPEN_CFW_FREERTOS_STACK_GROWTH = -1",
            "sizeof(open_cfw_freertos_stack_type) == 4U",
            "sizeof(open_cfw_freertos_stack_depth_type) == 2U",
        ):
            self.assertIn(token, header)

        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            [
                function
                for function in config["functions"]
                if function in PRODUCTION_ORDER
            ],
            PRODUCTION_ORDER,
        )
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
        }
        leaf = leaves[FUNCTION]
        self.assertEqual(leaf["source"]["path"], SOURCE.relative_to(ROOT).as_posix())
        self.assertEqual(leaf["source"]["size"], SOURCE_SIZE)
        self.assertEqual(leaf["source"]["sha256"], SOURCE_SHA256)
        self.assertEqual(leaf["expected"], PRODUCTION_PINS["apple-clang"])
        linux = leaf["toolchain_profiles"]["linux-clang"]
        self.assertEqual(
            linux["reviewed_version_prefix"],
            "Homebrew clang version 22.1.8",
        )
        self.assertEqual(linux["expected"], PRODUCTION_PINS["linux-clang"])
        self.assertEqual(linux["relocations"], [])
        self.assertEqual(leaf["relocations"], [])

        patch = next(
            item
            for item in config["patch_sites"]
            if item["name"]
            == "replace_freertos_task_check_free_stack_space"
        )
        self.assertEqual(patch["runtime_address"], START)
        self.assertEqual(patch["expected_hex"], STOCK_BYTES)
        self.assertEqual(patch["branch"], "b_w")
        self.assertEqual(patch["target_function"], FUNCTION)

    def test_pristine_oracle_equivalence_and_guard_preservation(self) -> None:
        for fill_bytes in (
            0,
            1,
            2,
            3,
            4,
            5,
            7,
            8,
            15,
            16,
            17,
            255,
            4_097,
            100_003,
        ):
            with self.subTest(fill_bytes=fill_bytes):
                candidate, oracle = self.invoke_pair(fill_bytes)
                expected = (fill_bytes // 4) & 0xFFFF
                self.assertEqual(candidate, oracle)
                self.assertEqual(candidate, expected)

    def test_sixteen_bit_result_truncation_matches_upstream(self) -> None:
        for words in (65_535, 65_536, 65_537):
            fill_bytes = words * 4
            with self.subTest(words=words):
                candidate, oracle = self.invoke_pair(fill_bytes)
                self.assertEqual(candidate, oracle)
                self.assertEqual(candidate, words & 0xFFFF)

    def test_official_span_hash_caller_and_internal_topology(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        self.assertEqual(
            sha256(self.span(CALLER_START, CALLER_END)),
            CALLER_SHA256,
        )
        encoding = self.span(CALLER, CALLER + 4)
        self.assertEqual(encoding.hex(), CALLER_ENCODING)
        self.assertEqual(
            sha256(struct.pack("<I", CALLER)),
            CALLER_ADDRESS_SHA256,
        )
        self.assertEqual(
            sha256(struct.pack("<I", CALLER) + encoding),
            CALLER_RECORD_SHA256,
        )

        internal = []
        for offset in range(0, len(stock), 2):
            address = START + offset
            halfword = struct.unpack_from("<H", stock, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END:
                    internal.append((address, target))
        self.assertEqual(
            internal,
            [(0x0045_5824, 0x0045_582A), (0x0045_582E, 0x0045_5826)],
        )

    def test_whole_image_entry_interior_and_stored_pointer_closure(
        self,
    ) -> None:
        direct_bl = []
        direct_bw = []
        external_interior = []
        external_narrow = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from(
                "<HH",
                self.application,
                offset,
            )
            for link, kind in ((True, "BL"), (False, "B.W")):
                target = thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target is None or not START <= target < END:
                    continue
                record = (address, target, self.application[offset:offset + 4])
                if target == START:
                    (direct_bl if link else direct_bw).append(record)
                else:
                    external_interior.append((kind, *record))

        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    external_narrow.append((address, target, halfword))

        self.assertEqual(
            direct_bl,
            [(CALLER, START, bytes.fromhex(CALLER_ENCODING))],
        )
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(external_narrow, [])

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = self.application.find(needle, position)
                    if position < 0:
                        break
                    stored.append(
                        (
                            APPLICATION_BASE + position,
                            value,
                            canonical,
                            position % 4,
                        )
                    )
                    position += 1
        self.assertEqual(
            stored,
            [(*RAW_ENTRY_FALSE_POSITIVE, START, 3)],
        )
        false_address, false_value = RAW_ENTRY_FALSE_POSITIVE
        self.assertNotEqual(false_address % 4, 0)
        self.assertEqual(false_value & 1, 0)
        self.assertEqual(
            self.span(0x0045_6352, 0x0045_6356).hex(),
            "07205845",
        )

    def test_isolated_thumb_object_has_one_closed_function_section(
        self,
    ) -> None:
        function_section = next(
            section
            for section in self.sections
            if section["name"] == FUNCTION_SECTION
        )
        executable = [
            section
            for section in self.sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(
            [section["name"] for section in executable],
            [FUNCTION_SECTION],
        )
        function_bytes = self.elf_data[
            int(function_section["offset"]):
            int(function_section["offset"]) + int(function_section["size"])
        ]
        self.assertEqual(int(function_section["type"]), 1)
        self.assertEqual(int(function_section["flags"]), 0x6)
        self.assertEqual(int(function_section["alignment"]), 4)
        self.assertEqual(len(function_bytes), 62)
        self.assertEqual(function_bytes.hex(), TARGET_FUNCTION_BYTES)
        self.assertEqual(sha256(function_bytes), TARGET_FUNCTION_SHA256)

        fields = self.symbols[FUNCTION]
        self.assertEqual(fields[1] & 1, 1)
        self.assertEqual(fields[2], int(function_section["size"]))
        self.assertEqual(fields[3] >> 4, 1)
        self.assertEqual(fields[3] & 0xF, 2)
        self.assertEqual(fields[5], int(function_section["index"]))

        undefined = [
            name
            for name, fields in self.parsed_symbols
            if name and fields[5] == 0
        ]
        self.assertEqual(undefined, [])
        writable_allocated = [
            section["name"]
            for section in self.sections
            if (
                int(section["size"]) > 0
                and int(section["flags"]) & 0x2
                and int(section["flags"]) & 0x1
            )
        ]
        self.assertEqual(writable_allocated, [])

        self.assertEqual(len(self.relocations), 1)
        relocation = self.relocations[0]
        self.assertTrue(relocation[0].startswith(".rel.ARM.exidx."))
        self.assertTrue(relocation[1].startswith(".ARM.exidx."))
        self.assertEqual(relocation[2], 0)
        self.assertEqual(relocation[3], 42)
        self.assertEqual(relocation[4], "")
        self.assertFalse(
            any(target == FUNCTION_SECTION for _, target, *_ in self.relocations)
        )


if __name__ == "__main__":
    unittest.main()
