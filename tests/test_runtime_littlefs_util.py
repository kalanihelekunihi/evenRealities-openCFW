from __future__ import annotations

import os

import ctypes
import hashlib
import importlib.util
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
    / "runtime_littlefs_util.c"
)
UPSTREAM_HEADER = ROOT / "third_party" / "littlefs" / "lfs_util.h"
PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "littlefs_util_cluster_upstream_oracle_host.c"
)
MAIN_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
BOOT_COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
BOOT_CONFIG = BOOT_COMPONENT / "overlay.json"
BOOT_BUILDER = BOOT_COMPONENT / "build_component.py"
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

SOURCE_RELATIVE_PATH = (
    "components/apollo_main/core_overlay/runtime_littlefs_util.c"
)
SOURCE_SHA256 = (
    "2730d0f39e02d7b6e07396894b796b26"
    "d9f73332deff23a685b5a06da0f7fb22"
)
UPSTREAM_SHA256 = (
    "f5d249326646c818e62af3cefefe8a57"
    "e7b484446a0f48d1050b95e60925088e"
)
PROVENANCE_SHA256 = (
    "df230e25c30626c0a0fed937406bf0a7"
    "19129e9b6c977aea563239b2b611fbbe"
)
UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"
UPSTREAM_GIT_BLOB = "0aec48855359df6e39d2f5bb3c45ca22b4a28811"

MAIN_BASE = 0x0043_8000
BOOT_BASE = 0x0041_0000
MAIN_PACKAGE_PREAMBLE = 32
MAIN_PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
MAIN_PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
BOOT_SHA256 = (
    "f89a4c4657537cec6bfc572bdb831886"
    "6309b90a5d180c4307680d39824167b5"
)
CLUSTER_BYTES = bytes.fromhex(
    "814200d308007047"
    "884200d308007047"
    "b0fbf1f001fb00f108007047"
    "80b50818401efff7f5ff02bd"
)
CLUSTER_SHA256 = (
    "5e0f6115942ef7d4162e5f499b57a59e"
    "c22fc46d1c39adf68d9f2990099224cf"
)

FUNCTIONS = (
    "open_cfw_littlefs_util_max",
    "open_cfw_littlefs_util_min",
    "open_cfw_littlefs_util_aligndown",
    "open_cfw_littlefs_util_alignup",
)
SHORT_NAMES = ("max", "min", "aligndown", "alignup")
STOCK = {
    "max": {
        "main": (0x004C_A6F8, 0x004C_A700),
        "boot": (0x0041_0400, 0x0041_0408),
        "sha256": (
            "3caa49d8a68e47b2cd91fcb01cae26b"
            "6262c904e8b96d8b3ba35f7fb33d07464"
        ),
    },
    "min": {
        "main": (0x004C_A700, 0x004C_A708),
        "boot": (0x0041_0408, 0x0041_0410),
        "sha256": (
            "7ec81166f84c44a60f4ecf93ad37d93f"
            "52ec00c77bb5db5a7dda659b1319c8a3"
        ),
    },
    "aligndown": {
        "main": (0x004C_A708, 0x004C_A714),
        "boot": (0x0041_0410, 0x0041_041C),
        "sha256": (
            "d0d7407bcf93abaef33623047467d1230"
            "d2176ce9b4a4e93bfcd8adde884f349"
        ),
    },
    "alignup": {
        "main": (0x004C_A714, 0x004C_A720),
        "boot": (0x0041_041C, 0x0041_0428),
        "sha256": (
            "18874b0eb5cf5c7bd6f20b2b29f78715"
            "7294b9e9be16d14ab0d9064d44a97c37"
        ),
    },
}
TOPOLOGY = {
    "max": {
        "main": (
            4,
            "fece20308dc407f9471f6d36dfbdbc428"
            "aa11c36c2823f5092d2732e775418e8",
            "68172fa84c89c7fbbd5a9e08f189f35a"
            "4be945974525084959622cf881e462a9",
        ),
        "boot": (
            4,
            "db4b59cfd0ea98dea6de8e0a949da3b"
            "85005c8d4ccf8ee56c482aaab8e40f47d",
            "5dc0f81da4685dbfc6ab840aa1ab56b7"
            "a7ba46374241f4da0b4f55e2edcc72a5",
        ),
    },
    "min": {
        "main": (
            31,
            "4e9fac593edd2cadf944644ec1765ab713"
            "b67cd5fe231d7f192f93b995bd4e4f",
            "e4917521d25965b50e5cdfe96fe104160"
            "8e982a74c83dc0690106b219827605c",
        ),
        "boot": (
            31,
            "23f4e3fc136f9b700f199c96ea41b9f9"
            "fbf6367639ee252741cc429bb7c07cda",
            "374b6e58126272c30f80399882fbc6936"
            "679b18f37c1c7b1e7b948828a323ca2",
        ),
    },
    "aligndown": {
        "main": (
            5,
            "f9adfb18cf7cf54a61ff58d1742d9b7f"
            "2d35b49b49c6c9e68012901990ae1300",
            "baa14112e260232011181911b0b0007a27"
            "decab41d76ed26ca8ef9116baba430",
        ),
        "boot": (
            5,
            "e4bb189342524b004da5d76f0367be7c"
            "baa25bbb7f7156d173910e7cb712fa25",
            "baa14112e260232011181911b0b0007a27"
            "decab41d76ed26ca8ef9116baba430",
        ),
    },
    "alignup": {
        "main": (
            6,
            "27ff14b7bd0f16a971476b04e6fa0b68"
            "6a7112eb4d1cd3d79ab1c1ed19b8cbbc",
            "7b50bb0e437bca66c10228b7a3838d93"
            "091233bd4a6e486e058fdd533124aeac",
        ),
        "boot": (
            6,
            "cd6b5e56cecea062ed551ff9653ddbb8f"
            "eac40514f7620b5e424e441f5da6bb9",
            "693c7a6c42892fc0b2991be36ca9a1d8"
            "78608518a9db3061e26b3ce15a3fb331",
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
TARGET_BODIES = {
    "main": {
        "max": (
            8,
            "49828a023d7febe0a7005f10d64021e7"
            "ffebe5354dfb50fdfbef19490a76dac0",
        ),
        "min": (
            8,
            "761921b20c0aec1b2d8aacbcffd07ba9b"
            "af30f1c57c0a89311028adc55e8c126",
        ),
        "aligndown": (
            8,
            "965ce09e34fe2ef897bc091faf02f8211"
            "bf344c025d769cf440c747fb5f555ee",
        ),
        "alignup": (
            8,
            "977169907db28276dc49c7f55020c30a"
            "f81d04b8fe43d98393cea03b49fccdd1",
        ),
    },
    "boot": {
        "max": (
            8,
            "00cbab254132bf12554d58b011edf1b5e"
            "3b1e36ff5d55a671d2ab04e5b8428a5",
        ),
        "min": (
            8,
            "36bb5e2d905d59628b5170a2cfecbf56"
            "f3200abb3207bfa30b50eaf3b4b44ab4",
        ),
        "aligndown": (
            8,
            "965ce09e34fe2ef897bc091faf02f8211"
            "bf344c025d769cf440c747fb5f555ee",
        ),
        "alignup": (
            8,
            "977169907db28276dc49c7f55020c30a"
            "f81d04b8fe43d98393cea03b49fccdd1",
        ),
    },
}

EXPECTED_FUNCTION_OFFSETS = {
    "main": dict(zip(FUNCTIONS, (109024, 109032, 109040, 109048))),
    "boot": dict(zip(FUNCTIONS, (58, 66, 74, 82))),
}
EXPECTED_AGGREGATE = {
    "main": {
        "overlay_size": 121_706,
        "overlay_sha256": (
            "9e5004af49fb14a22e7e7ed7357e4c10"
            "f87dc8da3a7fb4d7b97fcffcde804c43"
        ),
        "component_size": 3_645_102,
        "component_sha256": (
            "8722e5565bf54dade66fb751155c11eb"
            "d128d7a12853e3e4b8671c3c97807827"
        ),
        "text_size": 109_592,
        "rodata_size": 3_996,
        "isolated_text_size": 140,
        "isolated_padding_size": 4,
        "resolved_relocation_count": 906,
    },
    "boot": {
        "overlay_size": 622,
        "overlay_sha256": (
            "fc02cf66854adace4d213e08764e435e2"
            "7c8c2bc7cc4f7caac6ff286f3adf813"
        ),
        "component_size": 149_222,
        "component_sha256": (
            "b4a5b0f2028842a2d6fde9424fff05fa"
            "c2db3bf0e26e7f01d16a990e67ed9052"
        ),
        "text_size": 204,
        "rodata_size": 0,
        "isolated_text_size": 78,
        "isolated_padding_size": 0,
        "resolved_relocation_count": 2,
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


def load_boot_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_littlefs_util_boot_builder",
        BOOT_BUILDER,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bootloader core-overlay builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeLittlefsUtilTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.main_config = json.loads(MAIN_CONFIG.read_text(encoding="utf-8"))
        cls.boot_config = json.loads(BOOT_CONFIG.read_text(encoding="utf-8"))
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[MAIN_PACKAGE_PREAMBLE:]
        cls.boot = BOOT_IMAGE.read_bytes()

        build_root = ROOT / "build"
        build_root.mkdir(exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-littlefs-util-",
            dir=build_root,
        )
        temporary = Path(cls.temporary.name)

        cls.candidate = compile_host_library(
            SOURCE,
            temporary / library_name("runtime_littlefs_util"),
        )
        cls.oracle = compile_host_library(
            ORACLE_FIXTURE,
            temporary / library_name("runtime_littlefs_util_oracle"),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_littlefs_util_",
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_util_",
        )

        cls.target_objects = {}
        cls.target_records = {}
        for profile, flags in (("main", MAIN_FLAGS), ("boot", BOOT_FLAGS)):
            target = temporary / f"runtime_littlefs_util_{profile}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *flags,
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_objects[profile] = target
            cls.target_records[profile] = cls.parse_target_object(target)

        cls.production_ready = cls.production_config_is_ready()
        cls.production_reports = {}
        cls.production_overlays = {}
        if cls.production_ready:
            main_report = apollo_overlay.build(
                root=ROOT,
                config_path=MAIN_CONFIG,
                output_dir=temporary / "main-component",
                clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            )
            boot_report = load_boot_builder().build(
                root=ROOT,
                config_path=BOOT_CONFIG,
                output_dir=temporary / "boot-component",
                clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
            )
            cls.production_reports = {
                "main": main_report,
                "boot": boot_report,
            }
            cls.production_overlays = {
                "main": (ROOT / main_report["overlay"]["artifact"]).read_bytes(),
                "boot": (
                    temporary
                    / "boot-component"
                    / "bootloader_core_overlay.bin"
                ).read_bytes(),
            }

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def bind_api(
        library: ctypes.CDLL,
        prefix: str,
    ) -> dict[str, object]:
        api: dict[str, object] = {}
        for name in SHORT_NAMES:
            function = getattr(library, prefix + name)
            function.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            function.restype = ctypes.c_uint32
            api[name] = function
        return api

    @classmethod
    def parse_target_object(cls, path: Path) -> dict[str, object]:
        data, sections = cls.apollo_overlay.parse_elf32(path)
        symbols = cls.apollo_overlay.parse_elf32_symbols(data, sections)
        text = cls.apollo_overlay.section_named(sections, ".text")
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        function_symbols = {
            str(symbol["name"]): symbol
            for symbol in symbols
            if str(symbol["name"]) in FUNCTIONS
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
            "text_alignment": int(text["alignment"]),
            "symbols": function_symbols,
            "relocations": relocations,
            "undefined": undefined,
        }

    @classmethod
    def production_config_is_ready(cls) -> bool:
        expected = set(FUNCTIONS)
        main_functions = set(cls.main_config.get("functions", []))
        boot_functions = set(cls.boot_config.get("functions", {}))
        if not expected <= main_functions or not expected <= boot_functions:
            return False
        for config in (cls.main_config, cls.boot_config):
            sources = config.get("sources", [])
            if (
                not sources
                or not any(
                    source.get("path") == SOURCE_RELATIVE_PATH
                    for source in sources
                )
            ):
                return False
            targets = {
                site.get("target_function")
                for site in config.get("patch_sites", [])
            }
            if not expected <= targets:
                return False
        return True

    def require_production(self) -> None:
        if not self.production_ready:
            self.skipTest(
                "dual-image production overlay registration is not wired yet"
            )

    def test_source_upstream_and_snapshot_provenance_are_pinned(self) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 1753)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "lfs_max(), lfs_min()",
            "lfs_aligndown(), and lfs_alignup()",
            "littlefs v2.10.1 lfs_util.h",
            UPSTREAM_COMMIT,
            "Apollo-main [0x004CA6F8, 0x004CA720)",
            "[0x00410400, 0x00410428)",
            "sizeof(open_cfw_littlefs_util_u32) == 4U",
            "return (a > b) ? a : b;",
            "return (a < b) ? a : b;",
            "return a - (a % alignment);",
            "a + alignment - 1U",
        ):
            self.assertIn(fragment, source)
        for opaque_seam in (
            "#include",
            "extern ",
            "__UINTPTR_TYPE__",
            "typedef void (*",
        ):
            self.assertNotIn(opaque_seam, source)

        self.assertEqual(len(UPSTREAM_HEADER.read_bytes()), 7954)
        self.assertEqual(sha256(UPSTREAM_HEADER.read_bytes()), UPSTREAM_SHA256)
        upstream = UPSTREAM_HEADER.read_text(encoding="utf-8")
        for expression in (
            "return (a > b) ? a : b;",
            "return (a < b) ? a : b;",
            "return a - (a % alignment);",
            "return lfs_aligndown(a + alignment-1, alignment);",
        ):
            self.assertIn(expression, upstream)

        self.assertEqual(len(PROVENANCE.read_bytes()), 5912)
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
        files = {
            record["path"]: record
            for record in provenance["files"]
        }
        self.assertEqual(
            files["lfs_util.h"],
            {
                "path": "lfs_util.h",
                "size": 7954,
                "sha256": UPSTREAM_SHA256,
                "git_blob_sha1": UPSTREAM_GIT_BLOB,
            },
        )

    def test_scalar_and_nonzero_alignment_semantics_match_upstream(
        self,
    ) -> None:
        self.assertEqual(ctypes.sizeof(ctypes.c_uint32), 4)
        values = (
            0,
            1,
            2,
            3,
            7,
            15,
            16,
            17,
            0x7FFF_FFFF,
            0x8000_0000,
            0xFFFF_FFFE,
            0xFFFF_FFFF,
        )
        alignments = (
            1,
            2,
            3,
            7,
            16,
            255,
            256,
            0x7FFF_FFFF,
            0x8000_0000,
            0xFFFF_FFFF,
        )
        for a in values:
            for b in values:
                with self.subTest(operation="selectors", a=a, b=b):
                    self.assertEqual(
                        self.candidate_api["max"](a, b),
                        max(a, b),
                    )
                    self.assertEqual(
                        self.candidate_api["min"](a, b),
                        min(a, b),
                    )
                    self.assertEqual(
                        self.candidate_api["max"](a, b),
                        self.oracle_api["max"](a, b),
                    )
                    self.assertEqual(
                        self.candidate_api["min"](a, b),
                        self.oracle_api["min"](a, b),
                    )
            for alignment in alignments:
                with self.subTest(
                    operation="alignment",
                    a=a,
                    alignment=alignment,
                ):
                    down = a - (a % alignment)
                    wrapped = (a + alignment - 1) & 0xFFFF_FFFF
                    up = wrapped - (wrapped % alignment)
                    self.assertEqual(
                        self.candidate_api["aligndown"](a, alignment),
                        down,
                    )
                    self.assertEqual(
                        self.candidate_api["alignup"](a, alignment),
                        up,
                    )
                    self.assertEqual(
                        self.candidate_api["aligndown"](a, alignment),
                        self.oracle_api["aligndown"](a, alignment),
                    )
                    self.assertEqual(
                        self.candidate_api["alignup"](a, alignment),
                        self.oracle_api["alignup"](a, alignment),
                    )

        generator = random.Random(0x4C_A6_F8)
        for _ in range(4096):
            a = generator.getrandbits(32)
            b = generator.getrandbits(32)
            alignment = generator.getrandbits(32) or 1
            self.assertEqual(
                self.candidate_api["max"](a, b),
                self.oracle_api["max"](a, b),
            )
            self.assertEqual(
                self.candidate_api["min"](a, b),
                self.oracle_api["min"](a, b),
            )
            self.assertEqual(
                self.candidate_api["aligndown"](a, alignment),
                self.oracle_api["aligndown"](a, alignment),
            )
            self.assertEqual(
                self.candidate_api["alignup"](a, alignment),
                self.oracle_api["alignup"](a, alignment),
            )

    def test_target_profiles_emit_four_closed_eight_byte_functions(
        self,
    ) -> None:
        for profile in ("main", "boot"):
            with self.subTest(profile=profile):
                record = self.target_records[profile]
                self.assertEqual(len(record["text"]), 32)
                self.assertEqual(record["undefined"], [])
                self.assertEqual(set(record["symbols"]), set(FUNCTIONS))
                for index, (name, short_name) in enumerate(
                    zip(FUNCTIONS, SHORT_NAMES)
                ):
                    symbol = record["symbols"][name]
                    self.assertEqual(
                        (
                            int(symbol["value"]),
                            int(symbol["size"]),
                            int(symbol["binding"]),
                            int(symbol["type"]),
                        ),
                        (index * 8 + 1, 8, 1, 2),
                    )
                    body = record["text"][index * 8:(index + 1) * 8]
                    expected_size, expected_hash = (
                        TARGET_BODIES[profile][short_name]
                    )
                    self.assertEqual(len(body), expected_size)
                    self.assertEqual(sha256(body), expected_hash)
                self.assertEqual(
                    record["relocations"],
                    [(28, 30, "open_cfw_littlefs_util_aligndown")],
                )

    def test_official_dual_image_spans_are_identical_and_exact(self) -> None:
        self.assertEqual(len(self.main_package), 3_523_396)
        self.assertEqual(sha256(self.main_package), MAIN_PACKAGE_SHA256)
        self.assertEqual(len(self.main), 3_523_364)
        self.assertEqual(sha256(self.main), MAIN_PAYLOAD_SHA256)
        self.assertEqual(len(self.boot), 148_599)
        self.assertEqual(sha256(self.boot), BOOT_SHA256)

        main_cluster = span(
            self.main,
            MAIN_BASE,
            STOCK["max"]["main"][0],
            STOCK["alignup"]["main"][1],
        )
        boot_cluster = span(
            self.boot,
            BOOT_BASE,
            STOCK["max"]["boot"][0],
            STOCK["alignup"]["boot"][1],
        )
        self.assertEqual(main_cluster, CLUSTER_BYTES)
        self.assertEqual(boot_cluster, CLUSTER_BYTES)
        self.assertEqual(sha256(main_cluster), CLUSTER_SHA256)
        self.assertEqual(sha256(boot_cluster), CLUSTER_SHA256)

        for name in SHORT_NAMES:
            for image_name, image, base in (
                ("main", self.main, MAIN_BASE),
                ("boot", self.boot, BOOT_BASE),
            ):
                with self.subTest(function=name, image=image_name):
                    start, end = STOCK[name][image_name]
                    body = span(image, base, start, end)
                    self.assertEqual(len(body), end - start)
                    self.assertEqual(sha256(body), STOCK[name]["sha256"])

    def test_complete_dual_image_entry_and_interior_topology_is_exact(
        self,
    ) -> None:
        for image_name, image, base in (
            ("main", self.main, MAIN_BASE),
            ("boot", self.boot, BOOT_BASE),
        ):
            for name in SHORT_NAMES:
                with self.subTest(function=name, image=image_name):
                    start, end = STOCK[name][image_name]
                    observed = self.scan_topology(image, base, start, end)
                    count, address_hash, encoding_hash = (
                        TOPOLOGY[name][image_name]
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

    @classmethod
    def scan_topology(
        cls,
        image: bytes,
        base: int,
        start: int,
        end: int,
    ) -> dict[str, list[object]]:
        callers: list[tuple[int, bytes]] = []
        wide_jumps: list[tuple[int, bytes]] = []
        narrow_entries: list[tuple[int, int, int]] = []
        interior: list[tuple[int, int, bool, bytes]] = []

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

        stored: list[tuple[int, int]] = []
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

    def test_production_configs_register_one_shared_primary_source(
        self,
    ) -> None:
        self.require_production()
        expected_source = {
            "path": SOURCE_RELATIVE_PATH,
            "sha256": SOURCE_SHA256,
            "license": "BSD-3-Clause",
            "upstream_commit": UPSTREAM_COMMIT,
            "evidence": (
                "docs/research/littlefs-next-closed-leaves-audit.md"
            ),
        }
        for profile, config in (
            ("main", self.main_config),
            ("boot", self.boot_config),
        ):
            with self.subTest(profile=profile):
                configured_source = next(
                    source
                    for source in config["sources"]
                    if source["path"] == SOURCE_RELATIVE_PATH
                )
                for key, value in expected_source.items():
                    self.assertEqual(configured_source[key], value)
                self.assertIn("lfs_util.h", configured_source["upstream"])
                self.assertIn(
                    "bounded freestanding port",
                    configured_source["origin"],
                )

                self.assertTrue(set(FUNCTIONS) <= set(config["functions"]))
                self.assertFalse(
                    set(FUNCTIONS)
                    & {
                        leaf["function"]
                        for leaf in config.get("isolated_leaves", [])
                    }
                )

                sites = {
                    site["target_function"]: site
                    for site in config["patch_sites"]
                    if site["target_function"] in FUNCTIONS
                }
                self.assertEqual(set(sites), set(FUNCTIONS))
                for function, short_name in zip(FUNCTIONS, SHORT_NAMES):
                    start, end = STOCK[short_name][profile]
                    self.assertEqual(
                        sites[function],
                        {
                            "name": f"replace_littlefs_util_{short_name}",
                            "runtime_address": start,
                            "expected_size": end - start,
                            "expected_sha256": STOCK[short_name]["sha256"],
                            "branch": "b_w",
                            "target_function": function,
                        },
                    )

                expected = config["expected"]
                aggregate = EXPECTED_AGGREGATE[profile]
                self.assertEqual(
                    expected["overlay_size"],
                    aggregate["overlay_size"],
                )
                self.assertEqual(
                    expected["component_size"],
                    aggregate["component_size"],
                )
                self.assertEqual(
                    expected["overlay_sha256"],
                    aggregate["overlay_sha256"],
                )
                self.assertEqual(
                    expected["component_sha256"],
                    aggregate["component_sha256"],
                )

    @_APPLE_ONLY
    def test_production_reports_pin_primary_offsets_and_link_closure(
        self,
    ) -> None:
        self.require_production()
        for profile in ("main", "boot"):
            with self.subTest(profile=profile):
                report = self.production_reports[profile]
                overlay = self.production_overlays[profile]
                config = (
                    self.main_config
                    if profile == "main"
                    else self.boot_config
                )
                aggregate = EXPECTED_AGGREGATE[profile]
                self.assertEqual(
                    report["overlay"]["size"],
                    aggregate["overlay_size"],
                )
                self.assertEqual(
                    report["component"]["size"],
                    aggregate["component_size"],
                )
                self.assertEqual(
                    report["overlay"]["sha256"],
                    aggregate["overlay_sha256"],
                )
                self.assertEqual(
                    report["component"]["sha256"],
                    aggregate["component_sha256"],
                )
                link = report["overlay"]["link"]
                for key in (
                    "text_size",
                    "rodata_size",
                    "isolated_text_size",
                    "isolated_padding_size",
                    "resolved_relocation_count",
                ):
                    self.assertEqual(link[key], aggregate[key])

                source_record = next(
                    source
                    for source in report["sources"]
                    if source["path"] == SOURCE_RELATIVE_PATH
                )
                self.assertEqual(source_record["path"], SOURCE_RELATIVE_PATH)
                self.assertEqual(source_record["size"], 1753)
                self.assertEqual(source_record["sha256"], SOURCE_SHA256)

                functions = report["overlay"]["functions"]
                for function, short_name in zip(FUNCTIONS, SHORT_NAMES):
                    expected_offset = (
                        EXPECTED_FUNCTION_OFFSETS[profile][function]
                    )
                    self.assertEqual(
                        functions[function],
                        {"offset": expected_offset, "size": 8},
                    )
                    body = overlay[expected_offset:expected_offset + 8]
                    if short_name != "alignup":
                        self.assertEqual(
                            sha256(body),
                            TARGET_BODIES[profile][short_name][1],
                        )

                alignup_offset = EXPECTED_FUNCTION_OFFSETS[profile][
                    "open_cfw_littlefs_util_alignup"
                ]
                aligndown_offset = EXPECTED_FUNCTION_OFFSETS[profile][
                    "open_cfw_littlefs_util_aligndown"
                ]
                alignup = overlay[alignup_offset:alignup_offset + 8]
                self.assertEqual(alignup[:4], bytes.fromhex("08440138"))
                overlay_address = int(
                    report["overlay"]["overlay_runtime_address"]
                )
                branch_site = overlay_address + alignup_offset + 4
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        branch_site,
                        alignup[4:],
                        link=False,
                    ),
                    overlay_address + aligndown_offset,
                )

    @_APPLE_ONLY
    def test_production_reports_pin_all_eight_stock_redirects(self) -> None:
        self.require_production()
        for profile in ("main", "boot"):
            report = self.production_reports[profile]
            config = (
                self.main_config if profile == "main" else self.boot_config
            )
            sites = {
                site["target_function"]: site
                for site in report["overlay"]["patched_sites"]
                if site["target_function"] in FUNCTIONS
            }
            self.assertEqual(set(sites), set(FUNCTIONS))
            for function, short_name in zip(FUNCTIONS, SHORT_NAMES):
                with self.subTest(profile=profile, function=short_name):
                    site = sites[function]
                    start, end = STOCK[short_name][profile]
                    expected_target = (
                        int(report["overlay"]["overlay_runtime_address"])
                        + EXPECTED_FUNCTION_OFFSETS[profile][function]
                    )
                    self.assertEqual(site["branch"], "b_w")
                    self.assertEqual(site["runtime_address"], start)
                    self.assertEqual(site["expected_size"], end - start)
                    self.assertEqual(
                        site["expected_sha256"],
                        STOCK[short_name]["sha256"],
                    )
                    self.assertEqual(site["target_function"], function)
                    self.assertEqual(site["target_address"], expected_target)
                    replacement = bytes.fromhex(site["replacement_hex"])
                    self.assertEqual(len(replacement), end - start)
                    self.assertEqual(
                        self.apollo_overlay.decode_thumb_branch(
                            start,
                            replacement[:4],
                            link=False,
                        ),
                        expected_target,
                    )
                    self.assertEqual(
                        replacement[4:],
                        b"\x00\xbf" * ((end - start - 4) // 2),
                    )


if __name__ == "__main__":
    unittest.main()
