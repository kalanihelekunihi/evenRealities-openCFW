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
    / "runtime_littlefs_file_tell_private.c"
)
FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_file_tell_private_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_file_tell_private_upstream_oracle_host.c"
)
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs.h"
LITTLEFS_UTIL_SOURCE = ROOT / "third_party" / "littlefs" / "lfs_util.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)

BASE = 0x00438000
START = 0x004CE45C
END = 0x004CE460
PUBLIC_START = 0x004CFBE8
PUBLIC_END = 0x004CFC16
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701"
)
STOCK_SHA256 = (
    "efdc6e5a708e49cc1158aec6dfbde6a0115558c29a0f8c6a6ba9c4075df0fb5f"
)
STOCK_BYTES = "486b7047"

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


class LittlefsMdir32(ctypes.Structure):
    _fields_ = [
        ("pair", ctypes.c_uint32 * 2),
        ("revision", ctypes.c_uint32),
        ("offset", ctypes.c_uint32),
        ("etag", ctypes.c_uint32),
        ("count", ctypes.c_uint16),
        ("erased", ctypes.c_bool),
        ("split", ctypes.c_bool),
        ("tail", ctypes.c_uint32 * 2),
    ]


class LittlefsCtz32(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
    ]


class LittlefsFile32(ctypes.Structure):
    _fields_ = [
        ("next", ctypes.c_uint32),
        ("identifier", ctypes.c_uint16),
        ("type", ctypes.c_uint8),
        ("directory", LittlefsMdir32),
        ("ctz", LittlefsCtz32),
        ("flags", ctypes.c_uint32),
        ("position", ctypes.c_uint32),
        ("block", ctypes.c_uint32),
        ("offset", ctypes.c_uint32),
        ("cache", LittlefsCache32),
        ("configuration", ctypes.c_uint32),
    ]


class RuntimeLittlefsFileTellPrivateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[32:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        candidate_library = temporary / (
            "runtime_littlefs_file_tell_private.dylib"
            if sys.platform == "darwin"
            else "runtime_littlefs_file_tell_private.so"
        )
        candidate_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            candidate_command.extend(
                ["-dynamiclib", "-o", str(candidate_library)]
            )
        else:
            candidate_command.extend(
                ["-shared", "-fPIC", "-o", str(candidate_library)]
            )
        subprocess.run(
            candidate_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.candidate = ctypes.CDLL(str(candidate_library))

        oracle_library = temporary / (
            "runtime_littlefs_file_tell_private_oracle.dylib"
            if sys.platform == "darwin"
            else "runtime_littlefs_file_tell_private_oracle.so"
        )
        oracle_command = [
            os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(UPSTREAM_FIXTURE),
        ]
        if sys.platform == "darwin":
            oracle_command.extend(
                ["-dynamiclib", "-o", str(oracle_library)]
            )
        else:
            oracle_command.extend(
                ["-shared", "-fPIC", "-o", str(oracle_library)]
            )
        subprocess.run(
            oracle_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.oracle = ctypes.CDLL(str(oracle_library))

        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_file_tell_private_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_file_tell_private_",
        )

        cls.target_object = temporary / (
            "runtime_littlefs_file_tell_private.o"
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
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api: dict[str, object] = {}
        api["reset"] = getattr(library, prefix + "reset")
        api["reset"].argtypes = [ctypes.c_uint8, ctypes.c_uint32]
        api["reset"].restype = None
        api["call"] = getattr(library, prefix + "call")
        api["call"].argtypes = [ctypes.c_size_t]
        api["call"].restype = ctypes.c_int32
        api["checksum"] = getattr(library, prefix + "checksum")
        api["checksum"].argtypes = []
        api["checksum"].restype = ctypes.c_uint32
        api["position"] = getattr(library, prefix + "position")
        api["position"].argtypes = []
        api["position"].restype = ctypes.c_uint32
        api["file_size"] = getattr(library, prefix + "file_size")
        api["file_size"].argtypes = []
        api["file_size"].restype = ctypes.c_size_t
        api["position_offset"] = getattr(
            library,
            prefix + "position_offset",
        )
        api["position_offset"].argtypes = []
        api["position_offset"].restype = ctypes.c_size_t
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[start - BASE:end - BASE]

    def reset_both(self, pattern: int, position: int) -> None:
        self.candidate_api["reset"](pattern, position)
        self.oracle_api["reset"](pattern, position)

    def test_recovered_littlefs_file_abi_is_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(LittlefsCache32), 0x10)
        self.assertEqual(ctypes.sizeof(LittlefsMdir32), 0x20)
        self.assertEqual(ctypes.sizeof(LittlefsCtz32), 0x08)
        self.assertEqual(ctypes.sizeof(LittlefsFile32), 0x54)
        self.assertEqual(LittlefsFile32.position.offset, 0x34)

        self.assertEqual(
            self.candidate_api["file_size"](),
            self.oracle_api["file_size"](),
        )
        self.assertEqual(
            self.candidate_api["position_offset"](),
            self.oracle_api["position_offset"](),
        )

    def test_all_position_classes_match_pristine_upstream(self) -> None:
        for pattern in (0x00, 0x5A, 0xFF):
            for position in (
                0x00000000,
                0x00000001,
                0x7FFFFFFF,
                0x80000000,
                0xFFFFFFFF,
            ):
                with self.subTest(pattern=pattern, position=position):
                    self.reset_both(pattern, position)
                    candidate_before = self.candidate_api["checksum"]()
                    oracle_before = self.oracle_api["checksum"]()
                    self.assertEqual(candidate_before, oracle_before)

                    for lfs_address in (0, 1, 0x12345678):
                        self.assertEqual(
                            self.candidate_api["call"](lfs_address),
                            self.oracle_api["call"](lfs_address),
                        )
                        self.assertEqual(
                            self.candidate_api["call"](lfs_address),
                            ctypes.c_int32(position).value,
                        )

                    self.assertEqual(
                        self.candidate_api["checksum"](),
                        candidate_before,
                    )
                    self.assertEqual(
                        self.oracle_api["checksum"](),
                        oracle_before,
                    )
                    self.assertEqual(
                        self.candidate_api["position"](),
                        position,
                    )
                    self.assertEqual(
                        self.oracle_api["position"](),
                        position,
                    )

    def test_target_object_is_exact_stock_leaf_without_dependencies(
        self,
    ) -> None:
        function = self.symbols[
            "open_cfw_littlefs_file_tell_private"
        ]
        self.assertEqual((function[1], function[2]), (1, 4))
        self.assertEqual(function[3] & 0x0F, 2)
        self.assertNotEqual(function[5], 0)
        self.assertEqual(self.target_text.hex(), STOCK_BYTES)
        self.assertEqual(len(self.target_text), END - START)
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
            {"open_cfw_littlefs_file_tell_private"},
        )

    def test_source_is_pinned_upstream_and_has_no_opaque_seam(self) -> None:
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(
            hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
            "cfe48c2eb4ae9f7b8cc5f18c8ce140e8"
            "d309dd4953cc642da212d58448a53a51",
        )
        for token in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_file_tell_()",
            "littlefs v2.10.1",
            "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "[0x004CE45C, 0x004CE460)",
            "sizeof(struct open_cfw_littlefs_file_tell_private_file)"
            " == 0x54U",
            "position\n    ) == 0x34U",
            "return file->position;",
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
            "../../third_party/littlefs/lfs.c",
            oracle_source,
        )
        self.assertIn(
            "../../third_party/littlefs/lfs_util.c",
            oracle_source,
        )
        self.assertIn("return lfs_file_tell_(", oracle_source)
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

    def test_official_package_and_stock_boundaries_are_exact(self) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(
            hashlib.sha256(self.package).hexdigest(),
            PACKAGE_SHA256,
        )
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(
            hashlib.sha256(self.application).hexdigest(),
            PAYLOAD_SHA256,
        )

        stock = self.span(START, END)
        self.assertEqual(len(stock), 4)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(hashlib.sha256(stock).hexdigest(), STOCK_SHA256)
        self.assertEqual(
            hashlib.sha256(
                self.span(0x004CE3BC, START)
            ).hexdigest(),
            "368a3e58188f71ad37233eaca687cd39"
            "39a9f06406702a176f9731f22bcaf61f",
        )
        self.assertEqual(
            hashlib.sha256(
                self.span(END, 0x004CE472)
            ).hexdigest(),
            "be02691b2e7339d7dd1d54b31712c3e8"
            "563e5a86f4406a469888640fad9435cd",
        )

    def test_stock_caller_interior_and_stored_topology_is_exact(
        self,
    ) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        callers = []
        jumps = []
        interior = []
        public_callers = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            encoded = self.application[offset:offset + 4]
            for link, observed in ((True, callers), (False, jumps)):
                try:
                    target = apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except apollo_overlay.BuildError:
                    continue
                if target == START:
                    observed.append((address, encoded.hex()))
                if link and target == PUBLIC_START:
                    public_callers.append((address, encoded.hex()))
                if (
                    START < target < END
                    and not START <= address < END
                ):
                    interior.append(
                        (address, target, link, encoded.hex())
                    )
        self.assertEqual(callers, [(0x004CFC10, "fef724fc")])
        self.assertEqual(jumps, [])
        self.assertEqual(interior, [])
        self.assertEqual(
            public_callers,
            [
                (0x0047489A, "5bf0a5f9"),
                (0x004C906A, "06f0bdfd"),
            ],
        )
        self.assertEqual(
            hashlib.sha256(
                struct.pack("<I", callers[0][0])
            ).hexdigest(),
            "ec5bf1b540555e7fb3a4630a6b4edb1"
            "c00c08d3c3c2f9ee2fce252de4c16f7f8",
        )
        self.assertEqual(
            hashlib.sha256(
                b"".join(
                    struct.pack("<I", address)
                    for address, _ in public_callers
                )
            ).hexdigest(),
            "1ecea10b4064a3a5afa47fec5f195e0f"
            "f6fd258e7c04478f71efcdda01af8281",
        )

        narrow_interior = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in self.narrow_branch_targets(
                address,
                halfword,
            ):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    narrow_interior.append((address, target, halfword))
        self.assertEqual(narrow_interior, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from(
                "<I",
                self.application,
                offset,
            )[0]
            canonical = value & ~1
            if canonical in (START, START + 2):
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        public_wrapper = self.span(PUBLIC_START, PUBLIC_END)
        self.assertEqual(len(public_wrapper), 46)
        self.assertEqual(
            hashlib.sha256(public_wrapper).hexdigest(),
            "94d0448e342cf969f6a4553a19ef9d63"
            "8a75e0d41cdf8d842e7f8b4900cb3675",
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
