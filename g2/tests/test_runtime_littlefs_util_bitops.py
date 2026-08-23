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
    / "runtime_littlefs_util_bitops.c"
)
ORACLE_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "runtime_littlefs_util_bitops_upstream_oracle_host.c"
)
UPSTREAM_HEADER = ROOT / "third_party" / "littlefs" / "lfs_util.h"
PROVENANCE = ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
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

SOURCE_SHA256 = (
    "405092c6e8fc65a740f951cb2affaad8"
    "766e2553c7b8d290ff58f435e8830f47"
)
ORACLE_FIXTURE_SHA256 = (
    "e1d533ae545b00b054671070cd2c7902"
    "4b7c9a9e3cb80f4c7583444c887545cd"
)
UPSTREAM_SHA256 = (
    "f5d249326646c818e62af3cefefe8a57"
    "e7b484446a0f48d1050b95e60925088e"
)
PROVENANCE_SHA256 = (
    "44c588de6dec4ed3397fa6f942cfef3dc0fdb707742be73a0c8a4d78fd0ca9d0"
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
    "4a47eff21d5af0af4eb3a8485c2f22d8"
    "921ab3326344dca88c551f781747e205"
)
PREDECESSOR_SHA256 = (
    "b9ef01a036a6ee9727bc0a959a1fc354"
    "4ab889d277b97d947a9aab9b8dd1da66"
)
SUCCESSOR_SHA256 = (
    "4b803c8b48f3088b37ac0137dc2df12d"
    "06fc1d3d2b02a64afe7e5ce21b2fab4c"
)

SHORT_NAMES = ("npw2", "ctz", "popc")
FUNCTIONS = tuple(
    "open_cfw_littlefs_util_" + name for name in SHORT_NAMES
)
STOCK = {
    "npw2": {
        "main": (0x004C_A720, 0x004C_A77A),
        "boot": (0x0041_0428, 0x0041_0482),
        "sha256": (
            "291ab0ccd15efe1085ce5bcdc6551581"
            "ed4eccf67fa84f6560c4500fd68b8b63"
        ),
        "bytes": bytes.fromhex(
            "01000020491eb1f5803f01d3012200e0"
            "0022d2b21201d1401043b1f5807f01d3"
            "012200e00022d2b2d200d14010431029"
            "01d3012200e00022d2b29200d1401043"
            "042901d3012200e00022d2b25200d140"
            "104350ea5100401c7047"
        ),
    },
    "ctz": {
        "main": (0x004C_A77A, 0x004C_A78A),
        "boot": (0x0041_0482, 0x0041_0492),
        "sha256": (
            "4ae07bfa492e5dfad5869ea491ca43f7"
            "20e6fc153315a126e2e686313c3de08c"
        ),
        "bytes": bytes.fromhex(
            "80b541420840401cfff7cdff401e02bd"
        ),
    },
    "popc": {
        "main": (0x004C_A78A, 0x004C_A7B2),
        "boot": (0x0041_0492, 0x0041_04BA),
        "sha256": (
            "2cc25090f38dd5c2121cb4bfc7ddf0b"
            "d71df984312c9b9c52e87feeef5aea872"
        ),
        "bytes": bytes.fromhex(
            "0100490831f0aa31401a30f0cc318008"
            "30f0cc30401810eb101030f0f0305ff0"
            "01314843000e7047"
        ),
    },
}
TOPOLOGY = {
    "npw2": {
        "main": (
            3,
            "38012844589378f3550200486b07880e"
            "de473e5ad35899ef3cf35ca6725206b5",
            "facb27dc7efa9757918b3952902469bec"
            "e6d65f277e931dccd27978e56c8936a",
        ),
        "boot": (
            3,
            "cdb2363fa879cb8c7273771bcfad2072"
            "a11b2171f6aa21a56942d6e30ff54587",
            "b03d4d0b64009006778957e5c191fa49"
            "53daf1472e011037ffa225c73652a703",
        ),
    },
    "ctz": {
        "main": (
            2,
            "be6b83ffb1ee769987dc6d8a66c895ba"
            "ba503001529250ff8bca47e8ce0920d1",
            "58694e5cb022a1ad58966c161ff8ea2d"
            "a2ed7eb65c80994a73be44c8e69217be",
        ),
        "boot": (
            2,
            "eb712fed392b1618739d675addfa5041c"
            "81828ec77490aa5a28c186e7af16d2b",
            "5249923c7b5f4ed7ecc8cc9a0c0019d"
            "2f56453a9ee5a758f6d2edb7130561bb8",
        ),
    },
    "popc": {
        "main": (
            2,
            "48ae20e70e24a9b415df273660b96f9c"
            "194571d71e52dc07696b02c547700e34",
            "69e1ae3dc7a2d3c6c7584f985bdb4f8"
            "e4b4d7d7ea0cfa8c070e85f392e543494",
        ),
        "boot": (
            2,
            "419d1a09391db2dbceebe2cbc55e8abac"
            "f40e287c111284186b06fa087ced7be",
            "eac3e107bb3693f04569336f6c7ccd2b"
            "d111f67e99af9266ef2c143a8b6a44f9",
        ),
    },
}

COMMON_FLAGS = [
    "-mthumb",
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
TARGET_PROFILES = {
    "main": {
        "flags": ["--target=thumbv7em-none-eabi", "-O2", *COMMON_FLAGS],
        "functions": {
            "npw2": (
                72,
                "ef17f9ce9257384acd6010c107338f9d4"
                "5b2c43b60ef635e970ba54416d3496a",
            ),
            "ctz": (
                16,
                "743d892e08268653cd97dcfd35b494def"
                "81aff4745bd7467ef6de217189bee1a",
            ),
            "popc": (
                42,
                "7b7c7ddb5d9680c5dc736cd13fe67090"
                "824cbceece86d99c4f14690abeb230ff",
            ),
        },
    },
    "boot": {
        "flags": [
            "--target=arm-none-eabi",
            "-mcpu=cortex-m55",
            "-Oz",
            *COMMON_FLAGS,
        ],
        "functions": {
            "npw2": (
                56,
                "1048afe6eb2c306231e410f0a864ab5b"
                "fab3c9b0567e1fba6ec61f8bae53094a",
            ),
            "ctz": (
                16,
                "743d892e08268653cd97dcfd35b494def"
                "81aff4745bd7467ef6de217189bee1a",
            ),
            "popc": (
                42,
                "e537e00ef37eced668a9d421f28e84d5"
                "4a2b6ea09ea1cfda00f96ec1d65891f7",
            ),
        },
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


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class RuntimeLittlefsUtilBitopsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-littlefs-util-bitops-"
        )
        temporary = Path(cls.temporary.name)
        cls.candidate = compile_host_library(
            SOURCE,
            temporary / library_name("littlefs_util_bitops"),
        )
        cls.oracle = compile_host_library(
            ORACLE_FIXTURE,
            temporary / library_name("littlefs_util_bitops_oracle"),
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
        for profile, expected in TARGET_PROFILES.items():
            target_object = temporary / f"littlefs_util_bitops_{profile}.o"
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

        bodies = {}
        relocations = []
        for function_name in FUNCTIONS:
            symbol = named_symbols[function_name]
            section = sections[int(symbol["section_index"])]
            if section["name"] != ".text." + function_name:
                raise AssertionError(
                    f"{function_name} did not receive a dedicated section"
                )
            start = int(section["offset"]) + (int(symbol["value"]) & ~1)
            bodies[function_name] = data[
                start:start + int(symbol["size"])
            ]
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) != 9
                    or int(relocation_section["info"])
                    != int(section["index"])
                ):
                    continue
                for index in range(
                    int(relocation_section["size"]) // 8
                ):
                    offset, information = struct.unpack_from(
                        "<II",
                        data,
                        int(relocation_section["offset"]) + index * 8,
                    )
                    relocations.append(
                        (
                            function_name,
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
        allocated_data = sorted(
            str(section["name"])
            for section in sections
            if (
                int(section["flags"]) & 2
                and int(section["size"]) != 0
                and not str(section["name"]).startswith(".text.")
                and not str(section["name"]).startswith(".ARM.exidx.text.")
            )
        )
        return {
            "bodies": bodies,
            "relocations": relocations,
            "undefined": undefined,
            "allocated_data": allocated_data,
            "symbols": named_symbols,
        }

    def test_upstream_snapshot_source_and_license_are_authenticated(
        self,
    ) -> None:
        self.assertEqual(len(SOURCE.read_bytes()), 2795)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        source = SOURCE.read_text(encoding="utf-8")
        for fragment in (
            "The little filesystem",
            "SPDX-License-Identifier: BSD-3-Clause",
            "LFS_NO_INTRINSICS branches",
            "lfs_npw2(), lfs_ctz(), and lfs_popc()",
            UPSTREAM_COMMIT,
            UPSTREAM_TREE,
            "Apollo-main [0x004CA720, 0x004CA7B2)",
            "[0x00410428, 0x004104BA)",
            "#define OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS 1",
            "open_cfw_littlefs_util_npw2",
            "open_cfw_littlefs_util_ctz",
            "open_cfw_littlefs_util_popc",
            "(a & (0U - a)) + 1U",
            "0x55555555U",
            "0x33333333U",
            "0x0f0f0f0fU",
            "0x01010101U",
        ):
            self.assertIn(fragment, source)
        for forbidden in (
            "#include",
            "extern ",
            "__builtin_clz",
            "__builtin_ctz",
            "__builtin_popcount",
            "uint64_t",
        ):
            self.assertNotIn(forbidden, source)

        self.assertEqual(
            sha256(ORACLE_FIXTURE.read_bytes()),
            ORACLE_FIXTURE_SHA256,
        )
        fixture = ORACLE_FIXTURE.read_text(encoding="utf-8")
        self.assertIn("#define LFS_NO_INTRINSICS", fixture)
        self.assertIn("../../third_party/littlefs/lfs_util.h", fixture)
        for name in SHORT_NAMES:
            self.assertIn(f"lfs_{name}(a)", fixture)

        self.assertEqual(len(UPSTREAM_HEADER.read_bytes()), 7954)
        self.assertEqual(sha256(UPSTREAM_HEADER.read_bytes()), UPSTREAM_SHA256)
        upstream = UPSTREAM_HEADER.read_text(encoding="utf-8")
        for fragment in (
            "static inline uint32_t lfs_npw2(uint32_t a)",
            "static inline uint32_t lfs_ctz(uint32_t a)",
            "static inline uint32_t lfs_popc(uint32_t a)",
            "return lfs_npw2((a & -a) + 1) - 1;",
            "a = a - ((a >> 1) & 0x55555555);",
            "#if !defined(LFS_NO_INTRINSICS)",
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

    def test_fallback_semantics_and_zero_edges_match_pristine_upstream(
        self,
    ) -> None:
        values = [
            0,
            1,
            2,
            3,
            4,
            7,
            8,
            15,
            16,
            31,
            32,
            0x7FFF_FFFF,
            0x8000_0000,
            0xFFFF_FFFE,
            0xFFFF_FFFF,
            0x0102_0304,
            0xA5A5_A5A5,
        ]
        generator = random.Random(0x4C_A720)
        values.extend(generator.getrandbits(32) for _ in range(8192))

        self.assertEqual(self.candidate_api["npw2"](0), 32)
        self.assertEqual(self.candidate_api["npw2"](1), 1)
        self.assertEqual(self.candidate_api["ctz"](0), 0)
        self.assertEqual(self.candidate_api["ctz"](1), 0)
        self.assertEqual(self.candidate_api["popc"](0), 0)
        for value in values:
            for name in SHORT_NAMES:
                with self.subTest(function=name, value=value):
                    self.assertEqual(
                        self.candidate_api[name](value),
                        self.oracle_api[name](value),
                    )

    def test_target_profiles_pin_closed_mini_linked_cluster(
        self,
    ) -> None:
        for profile, expected in TARGET_PROFILES.items():
            with self.subTest(profile=profile):
                record = self.target_records[profile]
                self.assertEqual(record["undefined"], [])
                self.assertEqual(record["allocated_data"], [])
                self.assertEqual(
                    record["relocations"],
                    [
                        (
                            "open_cfw_littlefs_util_ctz",
                            8,
                            10,
                            "open_cfw_littlefs_util_npw2",
                        )
                    ],
                )
                self.assertEqual(
                    set(record["bodies"]),
                    set(FUNCTIONS),
                )
                for name, (size, digest) in expected["functions"].items():
                    function_name = "open_cfw_littlefs_util_" + name
                    body = record["bodies"][function_name]
                    self.assertEqual(len(body), size)
                    self.assertEqual(sha256(body), digest)
                    self.assertNotIn(bytes.fromhex("dff8"), body)

                defined_functions = {
                    str(symbol["name"])
                    for symbol in record["symbols"].values()
                    if (
                        int(symbol["type"]) == 2
                        and int(symbol["section_index"]) != 0
                    )
                }
                self.assertEqual(defined_functions, set(FUNCTIONS))

    @_APPLE_ONLY
    def test_production_configs_link_and_place_the_closed_trio(self) -> None:
        expected = {
            "main": {
                "overlay": (
                    165_412,
                    "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada",
                ),
                "component": (
                    3_688_808,
                    "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c",
                ),
                "functions": {
                    "npw2": (
                        109_056,
                        72,
                        "ef17f9ce9257384acd6010c107338f9d4"
                        "5b2c43b60ef635e970ba54416d3496a",
                    ),
                    "ctz": (
                        109_128,
                        16,
                        "b4282c027702526c28364bd68157a143"
                        "a064aa0e277ee1f245890bd6beb56c9c",
                    ),
                    "popc": (
                        109_144,
                        42,
                        "7b7c7ddb5d9680c5dc736cd13fe67090"
                        "824cbceece86d99c4f14690abeb230ff",
                    ),
                },
            },
            "boot": {
                "overlay": (
                    662,
                    "7cb3c17a03dda3b8576d8288ffa61df1332d89f1f24d6c5877bf0143e233902b",
                ),
                "component": (
                    149_262,
                    "695688b7cc4d9583e9e5c854db44980acab9a58d367bc7e02fa5e51eb00e3267",
                ),
                "functions": {
                    "npw2": (
                        90,
                        56,
                        "1048afe6eb2c306231e410f0a864ab5b"
                        "fab3c9b0567e1fba6ec61f8bae53094a",
                    ),
                    "ctz": (
                        146,
                        16,
                        "a5616df42c6d3705e9906d0cdce4d6d"
                        "5b59d0f02b647c59efeb6594c64004ab1",
                    ),
                    "popc": (
                        162,
                        42,
                        "e537e00ef37eced668a9d421f28e84d5"
                        "4a2b6ea09ea1cfda00f96ec1d65891f7",
                    ),
                },
            },
        }
        configs = {
            "main": json.loads(MAIN_CONFIG.read_text(encoding="utf-8")),
            "boot": json.loads(BOOT_CONFIG.read_text(encoding="utf-8")),
        }
        for profile, config in configs.items():
            sources = {
                source["path"]: source for source in config["sources"]
            }
            source = sources[SOURCE.relative_to(ROOT).as_posix()]
            self.assertEqual(source["sha256"], SOURCE_SHA256)
            self.assertEqual(source["license"], "BSD-3-Clause")
            self.assertEqual(source["upstream_commit"], UPSTREAM_COMMIT)
            isolated = {
                leaf["function"] for leaf in config["isolated_leaves"]
            }
            self.assertTrue(set(FUNCTIONS).isdisjoint(isolated))
            configured = config["functions"]
            self.assertTrue(set(FUNCTIONS).issubset(set(configured)))

            patches = {
                patch["target_function"]: patch
                for patch in config["patch_sites"]
            }
            for name in SHORT_NAMES:
                function_name = "open_cfw_littlefs_util_" + name
                start, end = STOCK[name][profile]
                patch = patches[function_name]
                self.assertEqual(patch["runtime_address"], start)
                self.assertEqual(patch["expected_size"], end - start)
                self.assertEqual(
                    patch["expected_sha256"],
                    STOCK[name]["sha256"],
                )
                self.assertEqual(patch["branch"], "b_w")

        production_builds = tempfile.TemporaryDirectory(
            prefix="test-runtime-littlefs-util-bitops-production-",
            dir=ROOT / "build",
        )
        self.addCleanup(production_builds.cleanup)
        output_root = Path(production_builds.name)
        main_report = self.apollo_overlay.build(
            root=ROOT,
            config_path=MAIN_CONFIG,
            output_dir=output_root / "main",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        spec = importlib.util.spec_from_file_location(
            "runtime_littlefs_util_bitops_boot_builder",
            BOOT_BUILDER,
        )
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        boot_builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(boot_builder)
        boot_report = boot_builder.build(
            root=ROOT,
            config_path=BOOT_CONFIG,
            output_dir=output_root / "boot",
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )

        for profile, report in (
            ("main", main_report),
            ("boot", boot_report),
        ):
            for artifact in ("overlay", "component"):
                size, digest = expected[profile][artifact]
                self.assertEqual(report[artifact]["size"], size)
                self.assertEqual(report[artifact]["sha256"], digest)

            overlay_path = output_root / profile / report["overlay"]["artifact"]
            if not overlay_path.exists():
                overlay_path = (
                    output_root / profile / Path(
                        report["overlay"]["artifact"]
                    ).name
                )
            overlay = overlay_path.read_bytes()
            functions = report["overlay"]["functions"]
            for name, (
                offset,
                size,
                digest,
            ) in expected[profile]["functions"].items():
                function_name = "open_cfw_littlefs_util_" + name
                function = functions[function_name]
                self.assertEqual(function, {"offset": offset, "size": size})
                body = overlay[offset:offset + size]
                self.assertEqual(sha256(body), digest)

            ctz_offset = expected[profile]["functions"]["ctz"][0]
            ctz_address = (
                report["overlay"]["overlay_runtime_address"] + ctz_offset
            )
            npw2_address = (
                report["overlay"]["overlay_runtime_address"]
                + expected[profile]["functions"]["npw2"][0]
            )
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    ctz_address + 8,
                    overlay[ctz_offset + 8:ctz_offset + 12],
                    link=True,
                ),
                npw2_address,
            )

    def test_official_dual_image_spans_and_neighbors_are_exact(
        self,
    ) -> None:
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
            cluster_start = STOCK["npw2"][profile][0]
            cluster_end = STOCK["popc"][profile][1]
            cluster = span(image, base, cluster_start, cluster_end)
            clusters[profile] = cluster
            self.assertEqual(len(cluster), 146)
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
                SUCCESSOR_SHA256,
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

            ctz_call = span(
                image,
                base,
                STOCK["ctz"][profile][0] + 8,
                STOCK["ctz"][profile][0] + 12,
            )
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    STOCK["ctz"][profile][0] + 8,
                    ctz_call,
                    link=True,
                ),
                STOCK["npw2"][profile][0],
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
