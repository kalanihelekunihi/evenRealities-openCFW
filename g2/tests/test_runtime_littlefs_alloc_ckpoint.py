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
    / "runtime_littlefs_alloc_ckpoint.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_alloc_ckpoint_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_alloc_ckpoint_upstream_oracle_host.c"
)
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs.h"
LITTLEFS_UTIL_SOURCE = ROOT / "third_party" / "littlefs" / "lfs_util.c"
LITTLEFS_PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
MAIN_PACKAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
BOOT_IMAGE = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)

MAIN_BASE = 0x00438000
MAIN_START = 0x004CB0E0
MAIN_END = 0x004CB0E6
MAIN_CALLERS = (
    (0x004CB0F0, "fff7f6ff"),
    (0x004CD400, "fdf76efe"),
    (0x004CDE38, "fdf752f9"),
    (0x004CE1F4, "fcf774ff"),
    (0x004CE256, "fcf743ff"),
    (0x004CEE80, "fcf72ef9"),
)
BOOT_BASE = 0x00410000
BOOT_START = 0x00410DE8
BOOT_END = 0x00410DEE
BOOT_CALLERS = (
    (0x00410DF8, "fff7f6ff"),
    (0x00413004, "fdf7f0fe"),
    (0x00413988, "fdf72efa"),
    (0x00413D44, "fdf750f8"),
    (0x00413DA6, "fdf71ff8"),
    (0x00414564, "fcf740fc"),
)

MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
MAIN_PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
)
BOOT_SHA256 = (
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
)
STOCK_SHA256 = (
    "74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c"
)
STOCK_BYTES = "c16e01667047"
SOURCE_SHA256 = (
    "16acfce3da9211512631113cb717abd012a0d551ceed36c57b4af300c21e7395"
)

TARGET_FLAGS = [
    "--target=arm-none-eabi",
    "-mcpu=cortex-m55",
    "-mthumb",
    "-Oz",
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


class LittlefsCache32(ctypes.Structure):
    _fields_ = [
        ("block", ctypes.c_uint32),
        ("offset", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32),
    ]


class LittlefsGstate32(ctypes.Structure):
    _fields_ = [
        ("tag", ctypes.c_uint32),
        ("pair", ctypes.c_uint32 * 2),
    ]


class LittlefsLookahead32(ctypes.Structure):
    _fields_ = [
        ("start", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("next", ctypes.c_uint32),
        ("checkpoint", ctypes.c_uint32),
        ("buffer", ctypes.c_uint32),
    ]


class Littlefs32(ctypes.Structure):
    _fields_ = [
        ("read_cache", LittlefsCache32),
        ("program_cache", LittlefsCache32),
        ("root", ctypes.c_uint32 * 2),
        ("open_list", ctypes.c_uint32),
        ("seed", ctypes.c_uint32),
        ("global_state", LittlefsGstate32),
        ("disk_state", LittlefsGstate32),
        ("delta_state", LittlefsGstate32),
        ("lookahead", LittlefsLookahead32),
        ("configuration", ctypes.c_uint32),
        ("block_count", ctypes.c_uint32),
        ("name_max", ctypes.c_uint32),
        ("file_max", ctypes.c_uint32),
        ("attribute_max", ctypes.c_uint32),
        ("inline_max", ctypes.c_uint32),
    ]


class RuntimeLittlefsAllocCkpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            FIXTURE,
            temporary / cls.library_name(
                "runtime_littlefs_alloc_ckpoint"
            ),
        )
        cls.oracle = cls.compile_host_library(
            UPSTREAM_FIXTURE,
            temporary / cls.library_name(
                "runtime_littlefs_alloc_ckpoint_oracle"
            ),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_alloc_ckpoint_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_alloc_ckpoint_",
        )

        cls.target_object = temporary / "runtime_littlefs_alloc_ckpoint.o"
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
            int(text["offset"]):int(text["offset"]) + int(text["size"])
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
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.text_relocations = []
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
                    cls.text_relocations.append(
                        (
                            offset,
                            information & 0xFF,
                            cls.parsed_symbols[information >> 8][0],
                        )
                    )

    @staticmethod
    def library_name(stem: str) -> str:
        return stem + (".dylib" if sys.platform == "darwin" else ".so")

    @staticmethod
    def compile_host_library(source: Path, output: Path) -> ctypes.CDLL:
        command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(source),
        ]
        if sys.platform == "darwin":
            command.extend(["-dynamiclib", "-o", str(output)])
        else:
            command.extend(["-shared", "-fPIC", "-o", str(output)])
        subprocess.run(command, check=True, capture_output=True, text=True)
        return ctypes.CDLL(str(output))

    @staticmethod
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api: dict[str, object] = {}
        api["reset"] = getattr(library, prefix + "reset")
        api["reset"].argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        api["reset"].restype = None
        api["call"] = getattr(library, prefix + "call")
        api["call"].argtypes = []
        api["call"].restype = None
        for name in (
            "checksum",
            "outside_checksum",
            "checkpoint",
            "block_count",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_uint32
        for name in (
            "lfs_size",
            "lookahead_offset",
            "checkpoint_offset",
            "block_count_offset",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_size_t
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(data: bytes, base: int, start: int, end: int) -> bytes:
        return data[start - base:end - base]

    def reset_both(self, pattern: int, block_count: int) -> None:
        self.candidate_api["reset"](pattern, block_count)
        self.oracle_api["reset"](pattern, block_count)

    def test_recovered_target_lfs_layout_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(LittlefsCache32), 0x10)
        self.assertEqual(ctypes.sizeof(LittlefsGstate32), 0x0C)
        self.assertEqual(ctypes.sizeof(LittlefsLookahead32), 0x14)
        self.assertEqual(ctypes.sizeof(Littlefs32), 0x80)

        expected_offsets = {
            "read_cache": 0x00,
            "program_cache": 0x10,
            "root": 0x20,
            "open_list": 0x28,
            "seed": 0x2C,
            "global_state": 0x30,
            "disk_state": 0x3C,
            "delta_state": 0x48,
            "lookahead": 0x54,
            "configuration": 0x68,
            "block_count": 0x6C,
            "name_max": 0x70,
            "file_max": 0x74,
            "attribute_max": 0x78,
            "inline_max": 0x7C,
        }
        for name, expected in expected_offsets.items():
            self.assertEqual(getattr(Littlefs32, name).offset, expected)
        self.assertEqual(LittlefsLookahead32.start.offset, 0x00)
        self.assertEqual(LittlefsLookahead32.size.offset, 0x04)
        self.assertEqual(LittlefsLookahead32.next.offset, 0x08)
        self.assertEqual(LittlefsLookahead32.checkpoint.offset, 0x0C)
        self.assertEqual(LittlefsLookahead32.buffer.offset, 0x10)
        self.assertEqual(
            Littlefs32.lookahead.offset +
            LittlefsLookahead32.checkpoint.offset,
            0x60,
        )

        for name in (
            "lfs_size",
            "lookahead_offset",
            "checkpoint_offset",
            "block_count_offset",
        ):
            self.assertEqual(
                self.candidate_api[name](),
                self.oracle_api[name](),
            )

    def test_all_value_classes_match_pristine_upstream(self) -> None:
        for pattern in (0x00, 0x5A, 0xFF):
            for block_count in (
                0x00000000,
                0x00000001,
                0x00000BC0,
                0x7FFFFFFF,
                0x80000000,
                0xFFFFFFFF,
            ):
                with self.subTest(
                    pattern=pattern,
                    block_count=block_count,
                ):
                    self.reset_both(pattern, block_count)
                    self.assertEqual(
                        self.candidate_api["checksum"](),
                        self.oracle_api["checksum"](),
                    )
                    candidate_outside = self.candidate_api[
                        "outside_checksum"
                    ]()
                    oracle_outside = self.oracle_api[
                        "outside_checksum"
                    ]()
                    self.assertEqual(candidate_outside, oracle_outside)

                    self.candidate_api["call"]()
                    self.oracle_api["call"]()

                    self.assertEqual(
                        self.candidate_api["checkpoint"](),
                        block_count,
                    )
                    self.assertEqual(
                        self.oracle_api["checkpoint"](),
                        block_count,
                    )
                    self.assertEqual(
                        self.candidate_api["block_count"](),
                        block_count,
                    )
                    self.assertEqual(
                        self.oracle_api["block_count"](),
                        block_count,
                    )
                    self.assertEqual(
                        self.candidate_api["checksum"](),
                        self.oracle_api["checksum"](),
                    )
                    self.assertEqual(
                        self.candidate_api["outside_checksum"](),
                        candidate_outside,
                    )
                    self.assertEqual(
                        self.oracle_api["outside_checksum"](),
                        oracle_outside,
                    )

                    self.candidate_api["call"]()
                    self.oracle_api["call"]()
                    self.assertEqual(
                        self.candidate_api["checksum"](),
                        self.oracle_api["checksum"](),
                    )

    def test_target_object_is_exact_stock_leaf_without_dependencies(
        self,
    ) -> None:
        function = self.symbols["open_cfw_littlefs_alloc_ckpoint"]
        self.assertEqual((function[1], function[2]), (1, 6))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        self.assertEqual(self.target_text.hex(), STOCK_BYTES)
        self.assertEqual(len(self.target_text), MAIN_END - MAIN_START)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            STOCK_SHA256,
        )
        self.assertEqual(self.text_relocations, [])
        self.assertEqual(
            sorted(
                name
                for name, fields in self.symbols.items()
                if fields[5] == 0
            ),
            [],
        )
        self.assertEqual(
            {
                name
                for name, fields in self.symbols.items()
                if fields[3] & 0x0F == 2 and fields[5] != 0
            },
            {"open_cfw_littlefs_alloc_ckpoint"},
        )

    def test_target_opcodes_encode_the_two_authenticated_offsets(
        self,
    ) -> None:
        load, store, return_ = struct.unpack("<HHH", self.target_text)
        self.assertEqual(load & 0xF800, 0x6800)
        self.assertEqual(store & 0xF800, 0x6000)
        self.assertEqual((load >> 6 & 0x1F) * 4, 0x6C)
        self.assertEqual((store >> 6 & 0x1F) * 4, 0x60)
        self.assertEqual((load >> 3 & 0x07, load & 0x07), (0, 1))
        self.assertEqual((store >> 3 & 0x07, store & 0x07), (0, 1))
        self.assertEqual(return_, 0x4770)

    def test_source_and_pristine_oracle_are_authenticated(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            SOURCE_SHA256,
        )
        for token in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_alloc_ckpoint()",
            "littlefs v2.10.1",
            "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "Apollo-main [0x004CB0E0, 0x004CB0E6)",
            "[0x00410DE8, 0x00410DEE)",
            "sizeof(struct open_cfw_littlefs_alloc_ckpoint_lfs)"
            " == 0x80U",
            "checkpoint\n        ) == 0x60U",
            "block_count\n    ) == 0x6CU",
            "lfs->lookahead.checkpoint = lfs->block_count;",
        ):
            self.assertIn(token, source)
        for opaque_seam in (
            "#include",
            "extern ",
            "__UINTPTR_TYPE__",
            "typedef void (*",
        ):
            self.assertNotIn(opaque_seam, source)

        oracle_source = UPSTREAM_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("../../third_party/littlefs/lfs.c", oracle_source)
        self.assertIn(
            "../../third_party/littlefs/lfs_util.c",
            oracle_source,
        )
        self.assertIn("lfs_alloc_ckpoint(", oracle_source)
        self.assertEqual(
            hashlib.sha256(LITTLEFS_SOURCE.read_bytes()).hexdigest(),
            "81a209e8551754d13b24fc0a2b6707fb"
            "3b2475e14feba00bf0df722b98a31398",
        )
        self.assertEqual(
            hashlib.sha256(LITTLEFS_HEADER.read_bytes()).hexdigest(),
            "ee44e99d6b19119b3e577b969b80c9d"
            "5e6f96410c9593794afddf6d4b314c486",
        )
        self.assertEqual(
            hashlib.sha256(LITTLEFS_UTIL_SOURCE.read_bytes()).hexdigest(),
            "f2fbde533670560434bd9f5a547174cc"
            "7c5a4670a02c47b4bd85180dced8b2ec",
        )
        provenance = LITTLEFS_PROVENANCE.read_text(encoding="utf-8")
        self.assertIn('"selected_tag": "v2.10.1"', provenance)
        self.assertIn(
            '"selected_commit": '
            '"0494ce7169f06a734a7bd7585f49a9fa91fa7318"',
            provenance,
        )

    def test_official_images_and_configuration_are_exact(self) -> None:
        self.assertEqual(len(self.main_package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.main_package).hexdigest(),
            MAIN_PACKAGE_SHA256,
        )
        self.assertEqual(len(self.main), 3_523_364)
        self.assertEqual(
            hashlib.sha256(self.main).hexdigest(),
            MAIN_PAYLOAD_SHA256,
        )
        self.assertEqual(len(self.boot), 148_599)
        self.assertEqual(
            hashlib.sha256(self.boot).hexdigest(),
            BOOT_SHA256,
        )

        configurations = (
            (
                self.main,
                MAIN_BASE,
                0x006E83A4,
                (
                    0x004763B9,
                    0x004763F1,
                    0x00476429,
                    0x004764DD,
                ),
                "f38bd899e180d29ee60609a2452d25c2"
                "d2d6c6fef4eb455064e23a6ca7c6e813",
            ),
            (
                self.boot,
                BOOT_BASE,
                0x00431070,
                (
                    0x004212D9,
                    0x00421311,
                    0x00421349,
                    0x004213D5,
                ),
                "724c351d2136e3c2f10b59ad84d547da"
                "4632739ea1f20eb839e9af2cfbd5b6e8",
            ),
        )
        for image, base, address, callbacks, expected_hash in configurations:
            config = self.span(image, base, address, address + 84)
            self.assertEqual(
                hashlib.sha256(config).hexdigest(),
                expected_hash,
            )
            words = struct.unpack("<21I", config)
            self.assertEqual(words[0], 0)
            self.assertEqual(words[1:5], callbacks)
            self.assertEqual(
                words[5:13],
                (16, 256, 4096, 3008, 500, 4096, 256, 0),
            )
            self.assertEqual(words[13:21], (0,) * 8)

    def test_dual_image_stock_neighbors_and_allocator_layout_match(
        self,
    ) -> None:
        for image, base, start in (
            (self.main, MAIN_BASE, MAIN_START),
            (self.boot, BOOT_BASE, BOOT_START),
        ):
            stock = self.span(image, base, start, start + 6)
            self.assertEqual(stock.hex(), STOCK_BYTES)
            self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start - 8, start)
                ).hexdigest(),
                "4a6d9e118e5aa8e7142d434ea2b710ef"
                "aa2cb2b34c03d88d68b35c9e4d92216b",
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start + 6, start + 22)
                ).hexdigest(),
                "55b7d516bb75d425ebbc077729c8c03a"
                "ef31b93897d422450084cfed8a771f66",
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start + 22, start + 78)
                ).hexdigest(),
                "58285c138461a673be0bed2c5376f8d7"
                "39e40e2aea753ad05d5061bfbc9265cf",
            )

        self.assertEqual(
            self.span(
                self.main,
                MAIN_BASE,
                MAIN_START - 8,
                MAIN_START + 78,
            ),
            self.span(
                self.boot,
                BOOT_BASE,
                BOOT_START - 8,
                BOOT_START + 78,
            ),
        )

    def test_dual_image_caller_and_reference_topology_is_exact(self) -> None:
        cases = (
            (
                self.main,
                MAIN_BASE,
                MAIN_START,
                MAIN_END,
                MAIN_CALLERS,
                "828e65cef40bf49a49b33ea1862e6c0d"
                "ad727e58dba5704905674e88a6a4ffd8",
                "35e674b64e228e851c69f3c0e5b0a8e"
                "2ace176c2f59f34a9717e8fe435ece924",
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLERS,
                "0b8d579b980802287ea289ed468130308"
                "d20ad59838a3e31e596fd993ba48fa4",
                "db2e6169825dcaec817f284ed47d08a0"
                "2e9bda9ae163fd26c4053561579eaca9",
            ),
        )
        for (
            image,
            base,
            start,
            end,
            callers,
            address_hash,
            call_hash,
        ) in cases:
            with self.subTest(start=f"{start:#010x}"):
                topology = self.scan_topology(image, base, start, end)
                self.assertEqual(
                    topology,
                    {
                        "callers": list(callers),
                        "wide_jumps": [],
                        "narrow": [],
                        "stored": [],
                        "interior": [],
                    },
                )
                addresses = b"".join(
                    struct.pack("<I", address)
                    for address, _ in callers
                )
                calls = b"".join(
                    self.span(image, base, address, address + 4)
                    for address, _ in callers
                )
                self.assertEqual(
                    hashlib.sha256(addresses).hexdigest(),
                    address_hash,
                )
                self.assertEqual(
                    hashlib.sha256(calls).hexdigest(),
                    call_hash,
                )

    @staticmethod
    def scan_topology(
        image: bytes,
        base: int,
        start: int,
        end: int,
    ) -> dict[str, list[object]]:
        import apollo_overlay

        callers: list[object] = []
        wide_jumps: list[object] = []
        narrow: list[object] = []
        stored: list[object] = []
        interior: list[object] = []

        for offset in range(0, len(image) - 3, 2):
            address = base + offset
            encoded = image[offset:offset + 4]
            for link, observed in (
                (True, callers),
                (False, wide_jumps),
            ):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == start:
                    observed.append((address, encoded.hex()))
                if (
                    start < target < end
                    and not start <= address < end
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )

        for offset in range(0, len(image) - 1, 2):
            address = base + offset
            halfword = struct.unpack_from("<H", image, offset)[0]
            for target in (
                RuntimeLittlefsAllocCkpointTests.narrow_branch_targets(
                    address,
                    halfword,
                )
            ):
                if (
                    start <= target < end
                    and not start <= address < end
                ):
                    narrow.append((address, target, halfword))

        target_words = {
            address | thumb
            for address in range(start, end, 2)
            for thumb in (0, 1)
        }
        for offset in range(0, len(image) - 3):
            value = struct.unpack_from("<I", image, offset)[0]
            if value in target_words:
                stored.append((base + offset, value))

        return {
            "callers": callers,
            "wide_jumps": wide_jumps,
            "narrow": narrow,
            "stored": stored,
            "interior": interior,
        }

    @staticmethod
    def narrow_branch_targets(address: int, halfword: int) -> list[int]:
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
