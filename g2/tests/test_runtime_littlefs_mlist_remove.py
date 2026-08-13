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
    / "runtime_littlefs_mlist_remove.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_mlist_remove_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_mlist_remove_upstream_oracle_host.c"
)
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs.h"
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
MAIN_START = 0x004CB0A0
MAIN_END = 0x004CB0BC
MAIN_CALLERS = (
    (0x004CD606, "fdf74bfd"),
    (0x004CDCF8, "fdf7d2f9"),
)
BOOT_BASE = 0x00410000
BOOT_START = 0x00410DA8
BOOT_END = 0x00410DC4
BOOT_CALLERS = (
    (0x0041320A, "fdf7cdfd"),
    (0x00413848, "fdf7aefa"),
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
    "55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd"
)
STOCK_BYTES = (
    "10f1280200e012681068002805d010688842f8d11068006810607047"
)
TARGET_SHA256 = (
    "bb4d51fd66c1638dae0c38615feffb08286027539aede7f65197306491d44e4f"
)
TARGET_BYTES = "28300246006818b18842fad1006810607047"
SOURCE_SHA256 = (
    "be21546c80eaec4d8ad738ea6875bb6760fae7a873105658bd94a2a751b0bd7d"
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


class RuntimeLittlefsMlistRemoveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            FIXTURE,
            temporary / cls.library_name("runtime_littlefs_mlist_remove"),
        )
        cls.oracle = cls.compile_host_library(
            UPSTREAM_FIXTURE,
            temporary / cls.library_name(
                "runtime_littlefs_mlist_remove_oracle"
            ),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_mlist_remove_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_mlist_remove_",
        )

        cls.target_object = temporary / "runtime_littlefs_mlist_remove.o"
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
            name: fields for name, fields in cls.parsed_symbols if name
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
        for name in ("reset", "call"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = None
        for name in ("head_id", "seed", "block_count"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_uint32
        for name in ("next_id", "node_id", "node_type"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        for name in (
            "lfs_size",
            "mlist_offset",
            "next_offset",
            "id_offset",
            "type_offset",
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

    def assert_apis_match(self) -> None:
        for name in ("head_id", "seed", "block_count"):
            self.assertEqual(
                self.candidate_api[name](),
                self.oracle_api[name](),
            )
        for index in range(4):
            for name in ("next_id", "node_id", "node_type"):
                self.assertEqual(
                    self.candidate_api[name](index),
                    self.oracle_api[name](index),
                )

    def test_recovered_layout_matches_pristine_upstream(self) -> None:
        for name in (
            "lfs_size",
            "mlist_offset",
            "next_offset",
            "id_offset",
            "type_offset",
        ):
            self.assertEqual(
                self.candidate_api[name](),
                self.oracle_api[name](),
            )
        self.assertEqual(self.candidate_api["next_offset"](), 0)

    def test_all_valid_removal_positions_match_pristine_upstream(
        self,
    ) -> None:
        cases = (
            (0, 0, 0xFFFFFFFF, (0xFFFFFFFF,) * 4),
            (2, 3, 0x210, (0x211, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)),
            (3, 0, 0x211, (0x211, 0x212, 0xFFFFFFFF, 0xFFFFFFFF)),
            (3, 1, 0x210, (0x212, 0x212, 0xFFFFFFFF, 0xFFFFFFFF)),
            (3, 2, 0x210, (0x211, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)),
        )
        for length, remove, head, next_ids in cases:
            with self.subTest(length=length, remove=remove):
                self.candidate_api["reset"](length)
                self.oracle_api["reset"](length)
                self.assert_apis_match()

                self.candidate_api["call"](remove)
                self.oracle_api["call"](remove)
                self.assert_apis_match()

                self.assertEqual(self.candidate_api["head_id"](), head)
                for index, expected in enumerate(next_ids):
                    self.assertEqual(
                        self.candidate_api["next_id"](index),
                        expected,
                    )
                self.assertEqual(self.candidate_api["seed"](), 0x2468ACE0)
                self.assertEqual(self.candidate_api["block_count"](), 3008)
                for index in range(4):
                    self.assertEqual(
                        self.candidate_api["node_id"](index),
                        0x210 + index,
                    )
                    self.assertEqual(
                        self.candidate_api["node_type"](index),
                        0x30 + index,
                    )

    def test_target_object_is_closed_and_smaller_than_stock(self) -> None:
        function = self.symbols["open_cfw_littlefs_mlist_remove"]
        self.assertEqual((function[1], function[2]), (1, 18))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        self.assertEqual(self.target_text.hex(), TARGET_BYTES)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            TARGET_SHA256,
        )
        self.assertLess(len(self.target_text), MAIN_END - MAIN_START)
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
            {"open_cfw_littlefs_mlist_remove"},
        )

        halfwords = struct.unpack("<9H", self.target_text)
        self.assertEqual(halfwords[0], 0x3028)
        self.assertEqual(halfwords[2], 0x6800)
        self.assertEqual(halfwords[4], 0x4288)
        self.assertEqual(halfwords[6], 0x6800)
        self.assertEqual(halfwords[7], 0x6010)
        self.assertEqual(halfwords[8], 0x4770)

    def test_source_and_pristine_oracle_are_authenticated(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            SOURCE_SHA256,
        )
        for token in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_mlist_remove()",
            "littlefs v2.10.1",
            "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "Apollo-main [0x004CB0A0, 0x004CB0BC)",
            "[0x00410DA8, 0x00410DC4)",
            "open_list\n    ) == 0x28U",
            "next\n    ) == 0U",
            "for (p = &lfs->open_list; *p; p = &(*p)->next)",
            "*p = (*p)->next;",
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
        self.assertIn("lfs_mlist_remove(", oracle_source)
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
                "f38bd899e180d29ee60609a2452d25c2"
                "d2d6c6fef4eb455064e23a6ca7c6e813",
            ),
            (
                self.boot,
                BOOT_BASE,
                0x00431070,
                "724c351d2136e3c2f10b59ad84d547da"
                "4632739ea1f20eb839e9af2cfbd5b6e8",
            ),
        )
        for image, base, address, expected_hash in configurations:
            config = self.span(image, base, address, address + 84)
            self.assertEqual(
                hashlib.sha256(config).hexdigest(),
                expected_hash,
            )
            self.assertEqual(struct.unpack_from("<I", config, 0x20)[0], 3008)

    def test_dual_image_stock_neighbors_and_function_match(self) -> None:
        for image, base, start in (
            (self.main, MAIN_BASE, MAIN_START),
            (self.boot, BOOT_BASE, BOOT_START),
        ):
            stock = self.span(image, base, start, start + 28)
            self.assertEqual(stock.hex(), STOCK_BYTES)
            self.assertEqual(
                hashlib.sha256(stock).hexdigest(),
                STOCK_SHA256,
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start - 30, start)
                ).hexdigest(),
                "e4963bfc9db9aa487d15261ebce9dd5b"
                "1429c708f6fe78ff47968718821c0c4e",
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start + 28, start + 42)
                ).hexdigest(),
                "38a84a73407c7b3c4751e9cd6e006041"
                "0afcc528ed57b86985f1ac8d97418852",
            )

        self.assertEqual(
            self.span(
                self.main,
                MAIN_BASE,
                MAIN_START - 30,
                MAIN_START + 42,
            ),
            self.span(
                self.boot,
                BOOT_BASE,
                BOOT_START - 30,
                BOOT_START + 42,
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
                "6c4bb102d90b0b2fecf42e493f6ce815"
                "fee1e1b8cb34cebefa3aa20561c3c570",
                "aea63c312924b0200829c0ae9d58bd33"
                "2bee9c2c0cc3b7882a86e90623bcff3f",
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLERS,
                "a4062608f53073dab0c6980ec6c9b9d8"
                "bd1448f5aa200a7654b83a5eb45e7103",
                "086fa8e91282e56652937f8dd939aefc"
                "1d4ec81edd03fadb877f41400fbdfdb1",
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
                struct.pack("<I", address) for address, _ in callers
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
                RuntimeLittlefsMlistRemoveTests.narrow_branch_targets(
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
