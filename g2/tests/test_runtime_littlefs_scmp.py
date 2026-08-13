from __future__ import annotations

import os

import ctypes
import hashlib
import random
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
    / "runtime_littlefs_scmp.c"
)
FIXTURE = ROOT / "tests" / "fixtures" / "runtime_littlefs_scmp_host.c"
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_scmp_upstream_oracle_host.c"
)
LITTLEFS_UTIL_HEADER = ROOT / "third_party" / "littlefs" / "lfs_util.h"
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
MAIN_START = 0x004CA7B2
MAIN_END = 0x004CA7B6
MAIN_CALLER = 0x004CB9CA
BOOT_BASE = 0x00410000
BOOT_START = 0x004104BA
BOOT_END = 0x004104BE
BOOT_CALLER = 0x004116D2

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
    "787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe"
)
STOCK_BYTES = "401a7047"
CALL_BYTES = "fef7f2fe"
CALL_SHA256 = (
    "d77a3cd87c4c95d7dbf4c0ba35c2c96298b6b41a880cdbe425c9867632ce51a8"
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


class RuntimeLittlefsScmpTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            FIXTURE,
            temporary / cls.library_name("runtime_littlefs_scmp"),
        )
        cls.oracle = cls.compile_host_library(
            UPSTREAM_FIXTURE,
            temporary / cls.library_name("runtime_littlefs_scmp_oracle"),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_scmp_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_scmp_",
        )

        cls.target_object = temporary / "runtime_littlefs_scmp.o"
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
        api["call"] = getattr(library, prefix + "call")
        api["call"].argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        api["call"].restype = ctypes.c_int32
        for name in ("uint32_size", "unsigned_size", "int_size"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_size_t
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def signed_distance(a: int, b: int) -> int:
        return ctypes.c_int32((a - b) & 0xFFFFFFFF).value

    @staticmethod
    def span(data: bytes, base: int, start: int, end: int) -> bytes:
        return data[start - base:end - base]

    def test_abi_widths_match_pristine_upstream(self) -> None:
        for name in ("uint32_size", "unsigned_size", "int_size"):
            self.assertEqual(self.candidate_api[name](), 4)
            self.assertEqual(
                self.candidate_api[name](),
                self.oracle_api[name](),
            )

    def test_edge_and_wrap_classes_match_pristine_upstream(self) -> None:
        values = (
            0x00000000,
            0x00000001,
            0x00000002,
            0x0000000F,
            0x7FFFFFFF,
            0x80000000,
            0x80000001,
            0xFFFFFFF0,
            0xFFFFFFFE,
            0xFFFFFFFF,
        )
        for a in values:
            for b in values:
                with self.subTest(a=a, b=b):
                    expected = self.signed_distance(a, b)
                    self.assertEqual(
                        self.candidate_api["call"](a, b),
                        expected,
                    )
                    self.assertEqual(
                        self.oracle_api["call"](a, b),
                        expected,
                    )

    def test_deterministic_full_width_samples_match_upstream(self) -> None:
        generator = random.Random(0x4C_A7_B2)
        for _ in range(4096):
            a = generator.getrandbits(32)
            b = generator.getrandbits(32)
            expected = self.signed_distance(a, b)
            self.assertEqual(self.candidate_api["call"](a, b), expected)
            self.assertEqual(self.oracle_api["call"](a, b), expected)

    def test_return_is_distance_not_three_way_comparison(self) -> None:
        cases = (
            (0x00000010, 0x00000000, 16),
            (0x00000000, 0x00000010, -16),
            (0x00000010, 0xFFFFFFF0, 32),
            (0xFFFFFFF0, 0x00000010, -32),
            (0x80000000, 0x00000000, -0x80000000),
        )
        for a, b, expected in cases:
            with self.subTest(a=a, b=b):
                self.assertEqual(
                    self.candidate_api["call"](a, b),
                    expected,
                )
                self.assertEqual(self.oracle_api["call"](a, b), expected)

    def test_target_object_is_exact_stock_leaf_without_dependencies(
        self,
    ) -> None:
        function = self.symbols["open_cfw_littlefs_scmp"]
        self.assertEqual((function[1], function[2]), (1, 4))
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
            {"open_cfw_littlefs_scmp"},
        )

    def test_source_is_pinned_upstream_and_has_no_opaque_seam(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "c89c32261a206e82e7da871ec4f1da21e"
            "b1fe0f9b329d59d28eaea6bb3546c88",
        )
        for token in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_scmp()",
            "littlefs v2.10.1",
            "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "Apollo-main [0x004CA7B2, 0x004CA7B6)",
            "[0x004104BA, 0x004104BE)",
            "sizeof(open_cfw_littlefs_scmp_u32) == 4U",
            "sizeof(unsigned) == 4U",
            "sizeof(int) == 4U",
            "return (int)(unsigned)(a - b);",
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
        self.assertIn(
            "../../third_party/littlefs/lfs_util.h",
            oracle_source,
        )
        self.assertIn("return lfs_scmp(a, b);", oracle_source)
        self.assertEqual(
            hashlib.sha256(LITTLEFS_UTIL_HEADER.read_bytes()).hexdigest(),
            "f5d249326646c818e62af3cefefe8a57"
            "e7b484446a0f48d1050b95e60925088e",
        )
        provenance = LITTLEFS_PROVENANCE.read_text(encoding="utf-8")
        self.assertIn('"selected_tag": "v2.10.1"', provenance)
        self.assertIn(
            '"selected_commit": '
            '"0494ce7169f06a734a7bd7585f49a9fa91fa7318"',
            provenance,
        )

    def test_official_images_and_stock_boundaries_are_exact(self) -> None:
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

        for image, base, start, end in (
            (self.main, MAIN_BASE, MAIN_START, MAIN_END),
            (self.boot, BOOT_BASE, BOOT_START, BOOT_END),
        ):
            stock = self.span(image, base, start, end)
            self.assertEqual(stock.hex(), STOCK_BYTES)
            self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)

        self.assertEqual(
            hashlib.sha256(
                self.span(
                    self.main,
                    MAIN_BASE,
                    0x004CA78A,
                    MAIN_START,
                )
            ).hexdigest(),
            "2cc25090f38dd5c2121cb4bfc7ddf0bd"
            "71df984312c9b9c52e87feeef5aea872",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(
                    self.boot,
                    BOOT_BASE,
                    0x00410492,
                    BOOT_START,
                )
            ).hexdigest(),
            "2cc25090f38dd5c2121cb4bfc7ddf0bd"
            "71df984312c9b9c52e87feeef5aea872",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(
                    self.main,
                    MAIN_BASE,
                    MAIN_END,
                    0x004CA7D8,
                )
            ).hexdigest(),
            "0666243f83f942c21b4428e4027b6f78"
            "15771c2f8a51dcddc550ffa9710add76",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(
                    self.boot,
                    BOOT_BASE,
                    BOOT_END,
                    0x004104E0,
                )
            ).hexdigest(),
            "0666243f83f942c21b4428e4027b6f78"
            "15771c2f8a51dcddc550ffa9710add76",
        )

    def test_dual_image_caller_and_reference_topology_is_exact(self) -> None:
        for (
            image,
            base,
            start,
            end,
            caller,
            caller_hash,
        ) in (
            (
                self.main,
                MAIN_BASE,
                MAIN_START,
                MAIN_END,
                MAIN_CALLER,
                "ab3abbc52e7e8885f61d1fd5cbd86926"
                "d22efbe07a5a1038e8eec32a0e84952d",
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLER,
                "43167613e139eae1bf7f26330e9a733b8"
                "d7dde264d87a627dc9d10a1b5e0f3a9",
            ),
        ):
            with self.subTest(start=f"{start:#010x}"):
                topology = self.scan_topology(
                    image,
                    base,
                    start,
                    end,
                )
                self.assertEqual(
                    topology,
                    {
                        "callers": [(caller, CALL_BYTES)],
                        "wide_jumps": [],
                        "narrow": [],
                        "stored": [],
                        "interior": [],
                    },
                )
                call = self.span(image, base, caller, caller + 4)
                self.assertEqual(call.hex(), CALL_BYTES)
                self.assertEqual(
                    hashlib.sha256(call).hexdigest(),
                    CALL_SHA256,
                )
                self.assertEqual(
                    hashlib.sha256(
                        struct.pack("<I", caller)
                    ).hexdigest(),
                    caller_hash,
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
            for target in RuntimeLittlefsScmpTests.narrow_branch_targets(
                address,
                halfword,
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
