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
    / "runtime_littlefs_disk_version.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_disk_version_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_disk_version_upstream_oracle_host.c"
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
MAIN_START = 0x004CB0C4
MAIN_END = 0x004CB0CA
MAIN_LITERAL = 0x004CB964
MAIN_CALLERS = (
    (0x004CB0CC, "fff7faff"),
    (0x004CB0D8, "fff7f4ff"),
    (0x004CEE94, "fcf716f9"),
    (0x004CF68A, "fbf71bfd"),
)
BOOT_BASE = 0x00410000
BOOT_START = 0x00410DCC
BOOT_END = 0x00410DD2
BOOT_LITERAL = 0x0041166C
BOOT_CALLERS = (
    (0x00410DD4, "fff7faff"),
    (0x00410DE0, "fff7f4ff"),
    (0x00414578, "fcf728fc"),
    (0x00414D5A, "fcf737f8"),
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
    "1ff8f5ac86a29e52674a91191c4ed763fe635aed200e701063e8224aa15c3870"
)
STOCK_BYTES = "dff89c087047"
LITERAL_SHA256 = (
    "7b11c1133330cd161071bf23a0c9b6ce5320a8f3a0f83620035a72be46df4104"
)
LITERAL_BYTES = "01000200"
TARGET_SHA256 = (
    "72eba3f48315967708b8128a1c2c9b4273ac363d25ec821bb9a03ea58ed9ce24"
)
TARGET_BYTES = "0048704701000200"
SOURCE_SHA256 = (
    "736a87363e5e009cb29f338c3245c22c02df375e275207f3c6e107b456c26d00"
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


class RuntimeLittlefsDiskVersionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            FIXTURE,
            temporary / cls.library_name("runtime_littlefs_disk_version"),
        )
        cls.oracle = cls.compile_host_library(
            UPSTREAM_FIXTURE,
            temporary / cls.library_name(
                "runtime_littlefs_disk_version_oracle"
            ),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_disk_version_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_disk_version_",
        )

        cls.target_object = temporary / "runtime_littlefs_disk_version.o"
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
        api["call"] = getattr(library, prefix + "call")
        api["call"].argtypes = []
        api["call"].restype = ctypes.c_uint32
        api["u32_size"] = getattr(library, prefix + "u32_size")
        api["u32_size"].argtypes = []
        api["u32_size"].restype = ctypes.c_size_t
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(data: bytes, base: int, start: int, end: int) -> bytes:
        return data[start - base:end - base]

    def test_constant_and_scalar_width_match_pristine_upstream(self) -> None:
        self.assertEqual(self.candidate_api["u32_size"](), 4)
        self.assertEqual(
            self.candidate_api["u32_size"](),
            self.oracle_api["u32_size"](),
        )
        for _ in range(64):
            self.assertEqual(self.candidate_api["call"](), 0x00020001)
            self.assertEqual(
                self.candidate_api["call"](),
                self.oracle_api["call"](),
            )

    def test_target_object_is_a_closed_source_generated_leaf(self) -> None:
        function = self.symbols["open_cfw_littlefs_disk_version"]
        self.assertEqual((function[1], function[2]), (1, 8))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        self.assertEqual(self.target_text.hex(), TARGET_BYTES)
        self.assertEqual(
            hashlib.sha256(self.target_text).hexdigest(),
            TARGET_SHA256,
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
            {"open_cfw_littlefs_disk_version"},
        )
        load, return_, literal = struct.unpack("<HHI", self.target_text)
        self.assertEqual(load, 0x4800)
        self.assertEqual(return_, 0x4770)
        self.assertEqual(literal, 0x00020001)

    def test_source_and_pristine_oracle_are_authenticated(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            SOURCE_SHA256,
        )
        for token in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_fs_disk_version()",
            "littlefs v2.10.1",
            "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "Apollo-main [0x004CB0C4, 0x004CB0CA)",
            "[0x00410DCC, 0x00410DD2)",
            "OPEN_CFW_LFS_DISK_VERSION 0x00020001U",
            "(void)lfs;",
            "return OPEN_CFW_LFS_DISK_VERSION;",
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
        self.assertIn("lfs_fs_disk_version(NULL)", oracle_source)
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

    def test_official_images_and_non_multiversion_abi_are_exact(self) -> None:
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
            self.assertEqual(len(config), 84)
            self.assertEqual(struct.unpack_from("<I", config, 0x20)[0], 3008)
            self.assertEqual(struct.unpack_from("<8I", config, 0x34), (0,) * 8)

    def test_stock_bodies_literals_and_neighbors_are_dual_image_exact(
        self,
    ) -> None:
        cases = (
            (
                self.main,
                MAIN_BASE,
                MAIN_START,
                MAIN_LITERAL,
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_LITERAL,
            ),
        )
        for image, base, start, literal in cases:
            stock = self.span(image, base, start, start + 6)
            self.assertEqual(stock.hex(), STOCK_BYTES)
            self.assertEqual(
                hashlib.sha256(stock).hexdigest(),
                STOCK_SHA256,
            )
            constant = self.span(image, base, literal, literal + 4)
            self.assertEqual(constant.hex(), LITERAL_BYTES)
            self.assertEqual(
                hashlib.sha256(constant).hexdigest(),
                LITERAL_SHA256,
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start - 8, start)
                ).hexdigest(),
                "e3ed290e4e62fc9cce34b0530080dbc0"
                "8efbca65f80ca1b7d182e18bb20c24b9",
            )
            self.assertEqual(
                hashlib.sha256(
                    self.span(image, base, start + 6, start + 18)
                ).hexdigest(),
                "c9ab0025e9e77a75e9240efbd5b15da2"
                "2807bdaa9f9deaf2cb425d4850f3bf08",
            )

        self.assertEqual(
            self.span(
                self.main,
                MAIN_BASE,
                MAIN_START - 8,
                MAIN_START + 18,
            ),
            self.span(
                self.boot,
                BOOT_BASE,
                BOOT_START - 8,
                BOOT_START + 18,
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
                "ae0e36961355004428510eea6826a916"
                "179f361d3bf07704794f30b35a415282",
                "dc5088b616be119cacfa263c84d67dd1"
                "da2777ab79f7c2d4b0cdc87b30780145",
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLERS,
                "9215d01804e2d711a345ab86fb61165f"
                "b893208336866f3bd8687586a3c8167b",
                "91c49e14baa9ef7c6fe7570f766c745d"
                "8831ee0e1a70262bb09382809edd2f6d",
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

    def test_stock_literal_has_one_instruction_reference_per_image(
        self,
    ) -> None:
        for image, base, start, literal in (
            (self.main, MAIN_BASE, MAIN_START, MAIN_LITERAL),
            (self.boot, BOOT_BASE, BOOT_START, BOOT_LITERAL),
        ):
            self.assertEqual(
                self.literal_references(image, base, literal),
                [(start, STOCK_BYTES[:8], "wide")],
            )
            stored_addresses = []
            for offset in range(0, len(image) - 3):
                value = struct.unpack_from("<I", image, offset)[0]
                if value in (literal, literal | 1):
                    stored_addresses.append((base + offset, value))
            self.assertEqual(stored_addresses, [])

    @staticmethod
    def literal_references(
        image: bytes,
        base: int,
        literal: int,
    ) -> list[tuple[int, str, str]]:
        references = []
        for offset in range(0, len(image) - 3, 2):
            address = base + offset
            first, second = struct.unpack_from("<HH", image, offset)
            if (
                first & 0xFF7F == 0xF85F
                and (second >> 12) & 0x0F != 0x0F
            ):
                target = (address + 4) & ~3
                immediate = second & 0x0FFF
                target = (
                    target + immediate
                    if first & 0x0080
                    else target - immediate
                )
                if target == literal:
                    references.append(
                        (address, image[offset:offset + 4].hex(), "wide")
                    )
            if first & 0xF800 == 0x4800:
                target = (
                    ((address + 4) & ~3) + (first & 0x00FF) * 4
                )
                if target == literal:
                    references.append(
                        (address, image[offset:offset + 2].hex(), "narrow")
                    )
        return references

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
                RuntimeLittlefsDiskVersionTests.narrow_branch_targets(
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
