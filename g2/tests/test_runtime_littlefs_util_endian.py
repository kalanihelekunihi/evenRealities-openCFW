from __future__ import annotations

import os

import ctypes
import hashlib
import json
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
    / "runtime_littlefs_util_endian.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_util_endian_upstream_oracle_host.c"
)
UPSTREAM_HEADER = ROOT / "third_party" / "littlefs" / "lfs_util.h"
PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
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
    "830d49b043181d270ac0aedda432c5e2"
    "32ce8d6ce65e8e537b80b1a706fd6cac"
)
ORACLE_FIXTURE_SHA256 = (
    "9d02060d559479a3ef56b587cf110c87"
    "ee0739033854f2ff9ff0868ef5bec125"
)
UPSTREAM_SHA256 = (
    "f5d249326646c818e62af3cefefe8a57"
    "e7b484446a0f48d1050b95e60925088e"
)
PROVENANCE_SHA256 = (
    "8d8b17dfdd485f83334df11333729e426c9b7d0ef41dade2502cf2870e1d2a94"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"
UPSTREAM_GIT_BLOB = "0aec48855359df6e39d2f5bb3c45ca22b4a28811"

MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
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
CLUSTER_SHA256 = (
    "136bebb2d17a83f29e934ea60c619329"
    "5417861101354ba5b89f7e35d18e1a38"
)
PREDECESSOR_SHA256 = (
    "13167bc14a6281f7a117e97ca303325a"
    "b33d28f7cbacc50d3f9e44320c8c82d3"
)
SUCCESSOR_SHA256 = {
    "main": (
        "080b929ac1a8cb0ad9f88c18db7fe657"
        "39a31eaa4ad5ed6484ffa4f31a08fc2f"
    ),
    "boot": (
        "56436a33873ca28297924f4a8be3aa5a"
        "72a998758f4101044953a2ed8630440b"
    ),
}

SHORT_NAMES = ("fromle32", "tole32", "frombe32", "tobe32")
FUNCTIONS = tuple(
    "open_cfw_littlefs_util_" + name for name in SHORT_NAMES
)
STOCK = {
    "fromle32": {
        "main": (0x004C_A7B6, 0x004C_A7D8),
        "boot": (0x0041_04BE, 0x0041_04E0),
        "sha256": (
            "0666243f83f942c21b4428e4027b6f78"
            "15771c2f8a51dcddc550ffa9710add76"
        ),
        "bytes": bytes.fromhex(
            "01b49df800009df8011050ea01209df8"
            "021050ea01409df8031050ea016001b0"
            "7047"
        ),
    },
    "tole32": {
        "main": (0x004C_A7D8, 0x004C_A7E0),
        "boot": (0x0041_04E0, 0x0041_04E8),
        "sha256": (
            "b217ac730c7d1b392e0f57a67477d6db"
            "88a751a8d3afb3a50ff5bebe0e273f66"
        ),
        "bytes": bytes.fromhex("80b5fff7ecff02bd"),
    },
    "frombe32": {
        "main": (0x004C_A7E0, 0x004C_A802),
        "boot": (0x0041_04E8, 0x0041_050A),
        "sha256": (
            "a0fc2d34d780abf4de23efe08746eefe"
            "e5cb84cae2728950c4123464e0f952c9"
        ),
        "bytes": bytes.fromhex(
            "01b49df800109df80100000450ea0160"
            "9df8021050ea01209df80310084301b0"
            "7047"
        ),
    },
    "tobe32": {
        "main": (0x004C_A802, 0x004C_A80A),
        "boot": (0x0041_050A, 0x0041_0512),
        "sha256": (
            "b217ac730c7d1b392e0f57a67477d6db"
            "88a751a8d3afb3a50ff5bebe0e273f66"
        ),
        "bytes": bytes.fromhex("80b5fff7ecff02bd"),
    },
}
TOPOLOGY = {
    "fromle32": {
        "main": (
            26,
            "e31d5e49b0d3d9add81d5c1b715999d"
            "e65c24f03ecf77f26bc45ca79fe738b2d",
            "bcdf80fe96884b8c1ea2420f735095c7"
            "f6a57fd6ba20ab719015a2574a88493c",
        ),
        "boot": (
            26,
            "264efba92915eabc31125f55e64c97687"
            "4594e100517c37c0a158105dcd635d0",
            "05dd81fda3b837996366dd91d47c8fd6"
            "32d43a2f8054550104904bab92908976",
        ),
    },
    "tole32": {
        "main": (
            19,
            "48db1319f5574c43bb4d05dcdcfd0868"
            "4d212c75cb96e5d36111ebe854861f4f",
            "44e91dd2102b812487ae2481038cb3e3f"
            "96e2094bb7917a336ce8752deffaa75",
        ),
        "boot": (
            19,
            "006824bf38a74c325ecbcd802d36eb495"
            "a8f44d19081d9365cb148c83ada9def",
            "9dbb2c053d8fbcc91c2355be96d1eb32"
            "384da8322ad83c00cd90ea6788deb512",
        ),
    },
    "frombe32": {
        "main": (
            4,
            "22bd22451a943a39a30b54a7309da70c"
            "08cf86ced375d654b5ed83be4ce4d7d9",
            "19531d5ffc21ba2a338dfa396b607ed2f"
            "8a43d4c3de8142d395fd778f5c53dd5",
        ),
        "boot": (
            4,
            "87b688ea884e40a88a40ffd0d1316309"
            "0109f8149abcf140c6c072e4fb013861",
            "19531d5ffc21ba2a338dfa396b607ed2f"
            "8a43d4c3de8142d395fd778f5c53dd5",
        ),
    },
    "tobe32": {
        "main": (
            2,
            "2b184d419a0bf749247a7ba30e596b01"
            "ba778f824ce5fd01c5a7b96828b6cc3c",
            "c4bc23d34a3b86a0bb2c9f3e0bee2f8"
            "714747023d114c0ae55239d586b27febd",
        ),
        "boot": (
            2,
            "c27e310b5184d4c38df655d98707dc68"
            "d1fef93ac0b3e2f5185a3ed308f9784d",
            "21c2a7f67248b726b8f3ab8d5cc50d7"
            "de2b88c85afa60d0998110e2d8f3c00c2",
        ),
    },
}

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
TARGET_FUNCTIONS = {
    "fromle32": (
        2,
        "c7dfbb7d02759eacb64dbc916c1bb6f21"
        "eabaff1c1032ea5c9176abf7fd28df8",
        bytes.fromhex("7047"),
    ),
    "tole32": (
        2,
        "c7dfbb7d02759eacb64dbc916c1bb6f21"
        "eabaff1c1032ea5c9176abf7fd28df8",
        bytes.fromhex("7047"),
    ),
    "frombe32": (
        4,
        "7a8f0cc1ae130c65908d3dbd4e89f7c"
        "7bd898743a4ee62deced9203383df3d11",
        bytes.fromhex("00ba7047"),
    ),
    "tobe32": (
        4,
        "7a8f0cc1ae130c65908d3dbd4e89f7c"
        "7bd898743a4ee62deced9203383df3d11",
        bytes.fromhex("00ba7047"),
    ),
}
TARGET_PROFILES = {
    "main": {
        "flags": MAIN_FLAGS,
        "offsets": (0, 4, 8, 12),
        "text_size": 16,
        "text_sha256": (
            "076ce4443ea6487d517db60329b436ad"
            "63d43734f9b9f8d4466a81b391ede932"
        ),
        "text_bytes": bytes.fromhex(
            "704700bf704700bf00ba704700ba7047"
        ),
    },
    "boot": {
        "flags": BOOT_FLAGS,
        "offsets": (0, 2, 4, 8),
        "text_size": 12,
        "text_sha256": (
            "4a7845c2d836bae45258e40684a938f7"
            "30a88b4319221eef1e6ae1a85fad0bac"
        ),
        "text_bytes": bytes.fromhex("7047704700ba704700ba7047"),
    },
}


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


class RuntimeLittlefsUtilEndianTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-littlefs-util-endian-"
        )
        temporary = Path(cls.temporary.name)

        cls.candidate = compile_host_library(
            SOURCE,
            temporary / library_name("littlefs_util_endian"),
        )
        cls.oracle = compile_host_library(
            ORACLE_FIXTURE,
            temporary / library_name("littlefs_util_endian_oracle"),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_littlefs_util_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_util_",
        )

        cls.target_records = {}
        cls.target_macros = {}
        for profile, expected in TARGET_PROFILES.items():
            target_object = temporary / f"littlefs_util_endian_{profile}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *expected["flags"],
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
            macros = subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *expected["flags"],
                    "-dM",
                    "-E",
                    "-x",
                    "c",
                    "-",
                ],
                input="",
                check=True,
                capture_output=True,
                text=True,
            ).stdout
            cls.target_macros[profile] = {
                parts[1]: parts[2]
                for line in macros.splitlines()
                if len(parts := line.split(maxsplit=2)) == 3
                and parts[0] == "#define"
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api = {}
        for name in SHORT_NAMES:
            function = getattr(library, prefix + name)
            function.argtypes = [ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            api[name] = function
        return api

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
            "symbols": named_symbols,
            "relocations": relocations,
            "undefined": undefined,
        }

    def test_upstream_source_snapshot_and_license_are_authenticated(
        self,
    ) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 2222)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_fromle32(), lfs_tole32()",
            "lfs_frombe32(), and lfs_tobe32()",
            "littlefs v2.10.1 lfs_util.h",
            UPSTREAM_COMMIT,
            UPSTREAM_TREE,
            "Apollo-main [0x004CA7B6, 0x004CA80A)",
            "[0x004104BE, 0x00410512)",
            "sizeof(open_cfw_littlefs_util_endian_u32) == 4U",
            "__BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__",
            "return a;",
            "return __builtin_bswap32(a);",
            "return open_cfw_littlefs_util_fromle32(a);",
            "upstream's inlined lfs_tobe32 -> lfs_frombe32 selection",
        ):
            self.assertIn(fragment, source)
        for forbidden in ("#include", "extern ", "uint64_t", "uint16_t"):
            self.assertNotIn(forbidden, source)

        self.assertEqual(
            sha256(ORACLE_FIXTURE.read_bytes()),
            ORACLE_FIXTURE_SHA256,
        )
        fixture = ORACLE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("../../third_party/littlefs/lfs_util.h", fixture)
        for name in SHORT_NAMES:
            self.assertIn(f"lfs_{name}(a)", fixture)

        self.assertEqual(len(UPSTREAM_HEADER.read_bytes()), 7954)
        self.assertEqual(sha256(UPSTREAM_HEADER.read_bytes()), UPSTREAM_SHA256)
        upstream = UPSTREAM_HEADER.read_text(encoding="utf-8")
        for fragment in (
            "static inline uint32_t lfs_fromle32(uint32_t a)",
            "static inline uint32_t lfs_tole32(uint32_t a)",
            "static inline uint32_t lfs_frombe32(uint32_t a)",
            "static inline uint32_t lfs_tobe32(uint32_t a)",
            "return __builtin_bswap32(a);",
            "return lfs_fromle32(a);",
            "return lfs_frombe32(a);",
        ):
            self.assertIn(fragment, upstream)

        self.assertEqual(sha256(PROVENANCE.read_bytes()), PROVENANCE_SHA256)
        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
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
        self.assertEqual(
            provenance["recovered_g2_configuration"]["target_endianness"],
            "little",
        )
        files = {item["path"]: item for item in provenance["files"]}
        self.assertEqual(
            files["lfs_util.h"],
            {
                "path": "lfs_util.h",
                "size": 7954,
                "sha256": UPSTREAM_SHA256,
                "git_blob_sha1": UPSTREAM_GIT_BLOB,
            },
        )

    def test_uint32_little_endian_semantics_match_pristine_upstream(
        self,
    ) -> None:
        self.assertEqual(ctypes.sizeof(ctypes.c_uint32), 4)
        values = [
            0,
            1,
            0x0000_00FF,
            0x0000_FF00,
            0x0102_0304,
            0x7FFF_FFFF,
            0x8000_0000,
            0xA5C3_1E70,
            0xFFFF_FFFF,
        ]
        generator = random.Random(0x4C_A7B6)
        values.extend(generator.getrandbits(32) for _ in range(4096))

        for value in values:
            swapped = int.from_bytes(
                value.to_bytes(4, "little"),
                "big",
            )
            expected = {
                "fromle32": value,
                "tole32": value,
                "frombe32": swapped,
                "tobe32": swapped,
            }
            for name in SHORT_NAMES:
                candidate = self.candidate_api[name](value)
                oracle = self.oracle_api[name](value)
                self.assertEqual(candidate, expected[name])
                self.assertEqual(candidate, oracle)

            self.assertEqual(
                self.candidate_api["frombe32"](swapped),
                value,
            )
            self.assertEqual(
                self.candidate_api["tobe32"](swapped),
                value,
            )

    def test_target_profiles_prove_little_endian_selection_and_codegen(
        self,
    ) -> None:
        for profile, expected in TARGET_PROFILES.items():
            with self.subTest(profile=profile):
                macros = self.target_macros[profile]
                self.assertEqual(
                    macros["__BYTE_ORDER__"],
                    "__ORDER_LITTLE_ENDIAN__",
                )
                self.assertEqual(macros["__ORDER_LITTLE_ENDIAN__"], "1234")
                self.assertEqual(macros["__SIZEOF_INT__"], "4")

                record = self.target_records[profile]
                text = record["text"]
                self.assertEqual(text, expected["text_bytes"])
                self.assertEqual(len(text), expected["text_size"])
                self.assertEqual(sha256(text), expected["text_sha256"])
                self.assertEqual(record["undefined"], [])
                self.assertEqual(record["relocations"], [])

                for name, offset in zip(
                    SHORT_NAMES,
                    expected["offsets"],
                ):
                    function_name = "open_cfw_littlefs_util_" + name
                    symbol = record["symbols"][function_name]
                    size, digest, body = TARGET_FUNCTIONS[name]
                    self.assertEqual(int(symbol["value"]), offset | 1)
                    self.assertEqual(int(symbol["size"]), size)
                    self.assertNotEqual(int(symbol["section_index"]), 0)
                    extracted = text[offset:offset + size]
                    self.assertEqual(extracted, body)
                    self.assertEqual(sha256(extracted), digest)

                defined_functions = {
                    str(symbol["name"])
                    for symbol in record["symbols"].values()
                    if (
                        int(symbol["type"]) == 2
                        and int(symbol["section_index"]) != 0
                    )
                }
                self.assertEqual(defined_functions, set(FUNCTIONS))

    def test_official_dual_image_spans_and_neighbors_are_exact(self) -> None:
        self.assertEqual(len(self.main_package), 3_523_396)
        self.assertEqual(sha256(self.main_package), MAIN_PACKAGE_SHA256)
        self.assertEqual(len(self.main), 3_523_364)
        self.assertEqual(sha256(self.main), MAIN_PAYLOAD_SHA256)
        self.assertEqual(len(self.boot), 148_599)
        self.assertEqual(sha256(self.boot), BOOT_SHA256)

        clusters = {}
        for profile, image, base in (
            ("main", self.main, MAIN_BASE),
            ("boot", self.boot, BOOT_BASE),
        ):
            cluster_start = STOCK["fromle32"][profile][0]
            cluster_end = STOCK["tobe32"][profile][1]
            cluster = span(
                image,
                base,
                cluster_start,
                cluster_end,
            )
            clusters[profile] = cluster
            self.assertEqual(len(cluster), 84)
            self.assertEqual(sha256(cluster), CLUSTER_SHA256)
            self.assertEqual(
                sha256(
                    span(
                        image,
                        base,
                        cluster_start - 32,
                        cluster_start,
                    )
                ),
                PREDECESSOR_SHA256,
            )
            self.assertEqual(
                sha256(
                    span(
                        image,
                        base,
                        cluster_end,
                        cluster_end + 32,
                    )
                ),
                SUCCESSOR_SHA256[profile],
            )
            for name in SHORT_NAMES:
                start, end = STOCK[name][profile]
                body = span(image, base, start, end)
                self.assertEqual(body, STOCK[name]["bytes"])
                self.assertEqual(len(body), end - start)
                self.assertEqual(sha256(body), STOCK[name]["sha256"])

        self.assertEqual(clusters["main"], clusters["boot"])

    def test_complete_dual_image_call_and_entry_topology_is_exact(
        self,
    ) -> None:
        for profile, image, base in (
            ("main", self.main, MAIN_BASE),
            ("boot", self.boot, BOOT_BASE),
        ):
            for name in SHORT_NAMES:
                with self.subTest(profile=profile, function=name):
                    start, end = STOCK[name][profile]
                    observed = self.scan_topology(image, base, start, end)
                    count, address_hash, encoding_hash = (
                        TOPOLOGY[name][profile]
                    )
                    self.assertEqual(len(observed["callers"]), count)
                    self.assertEqual(
                        sha256(
                            b"".join(
                                struct.pack("<I", address)
                                for address, _encoding
                                in observed["callers"]
                            )
                        ),
                        address_hash,
                    )
                    self.assertEqual(
                        sha256(
                            b"".join(
                                encoding
                                for _address, encoding
                                in observed["callers"]
                            )
                        ),
                        encoding_hash,
                    )
                    self.assertEqual(observed["wide_jumps"], [])
                    self.assertEqual(observed["narrow_entries"], [])
                    self.assertEqual(observed["interior"], [])
                    self.assertEqual(observed["stored"], [])

            tole_call = span(
                image,
                base,
                STOCK["tole32"][profile][0] + 2,
                STOCK["tole32"][profile][0] + 6,
            )
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    STOCK["tole32"][profile][0] + 2,
                    tole_call,
                    link=True,
                ),
                STOCK["fromle32"][profile][0],
            )
            tobe_call = span(
                image,
                base,
                STOCK["tobe32"][profile][0] + 2,
                STOCK["tobe32"][profile][0] + 6,
            )
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    STOCK["tobe32"][profile][0] + 2,
                    tobe_call,
                    link=True,
                ),
                STOCK["frombe32"][profile][0],
            )

    @classmethod
    def scan_topology(
        cls,
        image: bytes,
        base: int,
        start: int,
        end: int,
    ) -> dict[str, list[object]]:
        callers = []
        wide_jumps = []
        narrow_entries = []
        interior = []

        for offset in range(0, len(image) - 3, 2):
            address = base + offset
            encoded = image[offset:offset + 4]
            for link in (True, False):
                try:
                    target = cls.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except cls.apollo_overlay.BuildError:
                    continue
                if target == start:
                    if link:
                        callers.append((address, encoded))
                    else:
                        wide_jumps.append((address, encoded))
                if (
                    start < target < end
                    and not start <= address < end
                ):
                    interior.append((address, target, link, encoded))

        for offset in range(0, len(image) - 1, 2):
            address = base + offset
            halfword = struct.unpack_from("<H", image, offset)[0]
            for target in cls.narrow_branch_targets(address, halfword):
                if (
                    start <= target < end
                    and not start <= address < end
                ):
                    narrow_entries.append((address, target, halfword))

        stored = []
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
            "narrow_entries": narrow_entries,
            "interior": interior,
            "stored": stored,
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
