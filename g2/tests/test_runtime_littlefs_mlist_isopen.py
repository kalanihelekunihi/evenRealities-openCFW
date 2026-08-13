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
SOURCE = (
    ROOT
    / "components"
    / "apollo_main"
    / "core_overlay"
    / "runtime_littlefs_mlist_isopen.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_mlist_isopen_upstream_oracle_host.c"
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

SOURCE_SHA256 = (
    "7d0bc398c8ecd85fd00b34cc6dcc2b9f"
    "c75c754e1aed0bfbca01dd58ae9d6e0c"
)
ORACLE_FIXTURE_SHA256 = (
    "7be9d94ee8340a909c43b39a6a9dac8d"
    "e46fa6e79ae0d4e10a2481186f6b3777"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"
UPSTREAM_LFS_C_SHA256 = (
    "81a209e8551754d13b24fc0a2b6707fb"
    "3b2475e14feba00bf0df722b98a31398"
)
UPSTREAM_LFS_H_SHA256 = (
    "ee44e99d6b19119b3e577b969b80c9d"
    "5e6f96410c9593794afddf6d4b314c486"
)
UPSTREAM_LFS_C_GIT_BLOB = "7520f2ea7eb1d3d29ab29422ca3d6d0a3057397a"

MAIN_BASE = 0x0043_8000
MAIN_START = 0x004C_B082
MAIN_END = 0x004C_B0A0
MAIN_CALLERS = (
    0x004C_FAA4,
    0x004C_FADC,
    0x004C_FB14,
    0x004C_FB50,
    0x004C_FB8C,
    0x004C_FBC2,
    0x004C_FBF4,
    0x004C_FC3A,
    0x004C_FC74,
)
MAIN_CALLER_ADDRESS_SHA256 = (
    "6667cd1cff87ce0dac079356dc0cbfe9"
    "26fe0e516d131c6f85068d86c055a5ae"
)
MAIN_CALL_BYTES_SHA256 = (
    "bc5aa3b9e9fb126aac9dd24f6df9edf"
    "804895a1660d6ceb7b292f7dac7308141"
)

BOOT_BASE = 0x0041_0000
BOOT_START = 0x0041_0D8A
BOOT_END = 0x0041_0DA8
BOOT_CALLERS = (
    0x0041_5156,
    0x0041_518C,
    0x0041_51D0,
    0x0041_520C,
    0x0041_5242,
    0x0041_5296,
)
BOOT_CALLER_ADDRESS_SHA256 = (
    "677b277604f32390c87b7d237eaeffa3"
    "ac880176ed1ebe3d6c3621fbe1f31665"
)
BOOT_CALL_BYTES_SHA256 = (
    "a0cc47e7cb3c760e603d8bf3d408a773"
    "fece074cf068b4c0761140e513d49cb4"
)

MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
MAIN_PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
BOOT_SHA256 = (
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5"
)
STOCK_BYTES = bytes.fromhex(
    "01b46a4600e012681068002804d01068"
    "8842f8d1012000e0002001b07047"
)
STOCK_SHA256 = (
    "e4963bfc9db9aa487d15261ebce9dd5b"
    "1429c708f6fe78ff47968718821c0c4e"
)
PREDECESSOR_SHA256 = (
    "72120195dbe72dcf39bfef99e55ca80c"
    "733e98fb12a24672ef73ea0b7f08c1ec"
)
SUCCESSOR_SHA256 = (
    "9b2b64da825e2bdf5c391a09e73c8740"
    "2cf0e136b35563e296f96ad97725f1f6"
)

MAIN_FLAGS = [
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
BOOT_FLAGS = [
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
TARGETS = {
    "main": {
        "flags": MAIN_FLAGS,
        "size": 44,
        "sha256": (
            "6161db6d0867e47749654ae90b560ae4"
            "99a03f8c7708b98b2f1f916e6ef450f1"
        ),
        "bytes": bytes.fromhex(
            "80b1884210d0006860b188420cd00068"
            "40b1884208d0006820b1884204d00068"
            "0028eed10020704701207047"
        ),
    },
    "boot": {
        "flags": BOOT_FLAGS,
        "size": 18,
        "sha256": (
            "9b7caac591f8aea5d0eff0dc2b5ff7f"
            "f15ba85ab156ba5f95d47b1e4181db489"
        ),
        "bytes": bytes.fromhex(
            "28b1884204bf012070470068f8e700207047"
        ),
    },
}


class MlistNode(ctypes.Structure):
    pass


MlistNodePointer = ctypes.POINTER(MlistNode)
MlistNode._fields_ = [
    ("next", MlistNodePointer),
    ("id", ctypes.c_uint16),
    ("type", ctypes.c_uint8),
]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def span(image: bytes, base: int, start: int, end: int) -> bytes:
    return image[start - base:end - base]


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


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


def decode_thumb_bl_target(instruction: bytes, address: int) -> int | None:
    first, second = struct.unpack("<HH", instruction)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0xD000:
        return None

    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    displacement = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | ((first & 0x03FF) << 12)
        | ((second & 0x07FF) << 1)
    )
    if displacement & (1 << 24):
        displacement -= 1 << 25
    return (address + 4 + displacement) & 0xFFFF_FFFF


class RuntimeLittlefsMlistIsopenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-littlefs-mlist-isopen-"
        )
        temporary = Path(cls.temporary.name)

        cls.candidate = compile_host_library(
            SOURCE,
            temporary / library_name("runtime_littlefs_mlist_isopen"),
        )
        cls.oracle = compile_host_library(
            ORACLE_FIXTURE,
            temporary
            / library_name("runtime_littlefs_mlist_isopen_oracle"),
        )
        cls.candidate_call = getattr(
            cls.candidate,
            "open_cfw_littlefs_mlist_isopen",
        )
        cls.oracle_call = getattr(
            cls.oracle,
            "open_cfw_oracle_littlefs_mlist_isopen_call",
        )
        for function in (cls.candidate_call, cls.oracle_call):
            function.argtypes = [MlistNodePointer, MlistNodePointer]
            function.restype = ctypes.c_uint32

        cls.oracle_next_offset = getattr(
            cls.oracle,
            "open_cfw_oracle_littlefs_mlist_isopen_next_offset",
        )
        cls.oracle_next_offset.argtypes = []
        cls.oracle_next_offset.restype = ctypes.c_size_t

        cls.target_records = {}
        for profile, target in TARGETS.items():
            target_object = temporary / f"mlist_isopen_{profile}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *target["flags"],
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_records[profile] = cls.parse_target_object(
                target_object
            )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def parse_target_object(cls, path: Path) -> dict[str, object]:
        data, sections = cls.apollo_overlay.parse_elf32(path)
        text = cls.apollo_overlay.section_named(sections, ".text")
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        symbols = cls.apollo_overlay.parse_elf32_symbols(data, sections)
        named_symbols = {
            str(symbol["name"]): symbol
            for symbol in symbols
            if symbol["name"]
        }

        symbol_table = cls.apollo_overlay.section_named(sections, ".symtab")
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
            name = cls.apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))

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

        undefined = sorted(
            str(symbol["name"])
            for symbol in symbols
            if symbol["name"] and int(symbol["section_index"]) == 0
        )
        return {
            "text": text_bytes,
            "symbol": named_symbols["open_cfw_littlefs_mlist_isopen"],
            "relocations": relocations,
            "undefined": undefined,
        }

    @staticmethod
    def linked_nodes(length: int = 5) -> tuple[object, list[MlistNodePointer]]:
        nodes = (MlistNode * length)()
        pointers = [ctypes.pointer(nodes[index]) for index in range(length)]
        for index, node in enumerate(nodes):
            node.next = (
                pointers[index + 1]
                if index + 1 < length
                else MlistNodePointer()
            )
            node.id = 0x120 + index
            node.type = 0x30 + index
        return nodes, pointers

    def test_upstream_oracle_and_recovered_host_layout_match(self) -> None:
        self.assertEqual(MlistNode.next.offset, 0)
        self.assertEqual(self.oracle_next_offset(), 0)

    def test_membership_semantics_match_pristine_upstream(self) -> None:
        nodes, pointers = self.linked_nodes()
        absent = MlistNode(MlistNodePointer(), nodes[2].id, nodes[2].type)
        cases = (
            ("null-head-null-node", MlistNodePointer(), None, 0),
            ("null-head-present-node", MlistNodePointer(), pointers[0], 0),
            ("head", pointers[0], pointers[0], 1),
            ("middle", pointers[0], pointers[2], 1),
            ("tail", pointers[0], pointers[4], 1),
            ("prefix-excluded", pointers[2], pointers[1], 0),
            ("equal-fields-distinct-node", pointers[0], ctypes.pointer(absent), 0),
            ("null-node", pointers[0], None, 0),
        )
        before = ctypes.string_at(ctypes.addressof(nodes), ctypes.sizeof(nodes))
        for label, head, node, expected in cases:
            with self.subTest(case=label):
                candidate = self.candidate_call(head, node)
                oracle = self.oracle_call(head, node)
                self.assertEqual(candidate, expected)
                self.assertEqual(candidate, oracle)
                self.assertIn(candidate, (0, 1))
        after = ctypes.string_at(ctypes.addressof(nodes), ctypes.sizeof(nodes))
        self.assertEqual(after, before)

    def test_source_and_pristine_snapshot_are_authenticated(self) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 1801)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_mlist_isopen()",
            "littlefs v2.10.1 lfs.c",
            UPSTREAM_COMMIT,
            UPSTREAM_TREE,
            "Apollo-main [0x004CB082, 0x004CB0A0)",
            "[0x00410D8A, 0x00410DA8)",
            "sizeof(open_cfw_littlefs_mlist_isopen_bool) == 4U",
            "next\n    ) == 0U",
            "Using C _Bool here makes",
            "while (head)",
            "if (head == node)",
            "head = head->next;",
            "return 1U;",
            "return 0U;",
        ):
            self.assertIn(fragment, source)
        for forbidden in ("#include", "extern "):
            self.assertNotIn(forbidden, source)

        self.assertEqual(
            sha256(ORACLE_FIXTURE.read_bytes()),
            ORACLE_FIXTURE_SHA256,
        )
        oracle_source = ORACLE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("../../third_party/littlefs/lfs.c", oracle_source)
        self.assertIn("lfs_mlist_isopen(head, node)", oracle_source)

        self.assertEqual(
            sha256(LITTLEFS_SOURCE.read_bytes()),
            UPSTREAM_LFS_C_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_HEADER.read_bytes()),
            UPSTREAM_LFS_H_SHA256,
        )
        upstream = LITTLEFS_SOURCE.read_text(encoding="utf-8")
        self.assertIn(
            "static bool lfs_mlist_isopen(struct lfs_mlist *head,",
            upstream,
        )
        self.assertIn(
            "for (struct lfs_mlist **p = &head; *p; p = &(*p)->next)",
            upstream,
        )

        provenance = json.loads(
            LITTLEFS_PROVENANCE.read_text(encoding="utf-8")
        )
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertEqual(provenance["upstream"]["selected_tag"], "v2.10.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        self.assertTrue(
            provenance["recovered_g2_configuration"]["build_options"][
                "assertions"
            ]
        )
        files = {item["path"]: item for item in provenance["files"]}
        self.assertEqual(files["lfs.c"]["sha256"], UPSTREAM_LFS_C_SHA256)
        self.assertEqual(
            files["lfs.c"]["git_blob_sha1"],
            UPSTREAM_LFS_C_GIT_BLOB,
        )

    def test_both_production_profiles_match_reviewed_codegen(self) -> None:
        for profile, expected in TARGETS.items():
            with self.subTest(profile=profile):
                record = self.target_records[profile]
                body = record["text"]
                symbol = record["symbol"]
                self.assertEqual(body, expected["bytes"])
                self.assertEqual(len(body), expected["size"])
                self.assertEqual(sha256(body), expected["sha256"])
                self.assertEqual(int(symbol["size"]), expected["size"])
                self.assertEqual(int(symbol["value"]), 1)
                self.assertNotEqual(int(symbol["section_index"]), 0)
                self.assertEqual(record["relocations"], [])
                self.assertEqual(record["undefined"], [])

    def test_dual_image_stock_span_neighbors_and_callers_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.main_package), 3_523_396)
        self.assertEqual(sha256(self.main_package), MAIN_PACKAGE_SHA256)
        self.assertEqual(len(self.main), 3_523_364)
        self.assertEqual(sha256(self.main), MAIN_PAYLOAD_SHA256)
        self.assertEqual(len(self.boot), 148_599)
        self.assertEqual(sha256(self.boot), BOOT_SHA256)

        profiles = (
            (
                self.main,
                MAIN_BASE,
                MAIN_START,
                MAIN_END,
                MAIN_CALLERS,
                MAIN_CALLER_ADDRESS_SHA256,
                MAIN_CALL_BYTES_SHA256,
            ),
            (
                self.boot,
                BOOT_BASE,
                BOOT_START,
                BOOT_END,
                BOOT_CALLERS,
                BOOT_CALLER_ADDRESS_SHA256,
                BOOT_CALL_BYTES_SHA256,
            ),
        )
        for (
            image,
            base,
            start,
            end,
            callers,
            caller_address_hash,
            call_bytes_hash,
        ) in profiles:
            with self.subTest(start=hex(start)):
                stock = span(image, base, start, end)
                self.assertEqual(stock, STOCK_BYTES)
                self.assertEqual(len(stock), 30)
                self.assertEqual(sha256(stock), STOCK_SHA256)
                self.assertEqual(
                    sha256(span(image, base, start - 32, start)),
                    PREDECESSOR_SHA256,
                )
                self.assertEqual(
                    sha256(span(image, base, end, end + 32)),
                    SUCCESSOR_SHA256,
                )

                address_bytes = b"".join(
                    struct.pack("<I", address) for address in callers
                )
                call_bytes = b"".join(
                    span(image, base, address, address + 4)
                    for address in callers
                )
                self.assertEqual(sha256(address_bytes), caller_address_hash)
                self.assertEqual(sha256(call_bytes), call_bytes_hash)
                for address in callers:
                    instruction = span(
                        image,
                        base,
                        address,
                        address + 4,
                    )
                    self.assertEqual(
                        decode_thumb_bl_target(instruction, address),
                        start,
                    )

                discovered = []
                for offset in range(0, len(image) - 3, 2):
                    address = base + offset
                    if decode_thumb_bl_target(
                        image[offset:offset + 4],
                        address,
                    ) == start:
                        discovered.append(address)
                self.assertEqual(tuple(discovered), callers)

                for address in range(start, end, 2):
                    self.assertEqual(
                        image.find(struct.pack("<I", address)),
                        -1,
                    )
                    self.assertEqual(
                        image.find(struct.pack("<I", address | 1)),
                        -1,
                    )


if __name__ == "__main__":
    unittest.main()
