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
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
CANDIDATE_SOURCE = (
    ROOT / "research" / "candidates" / "littlefs_util_cluster.c"
)
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures" / "littlefs_util_cluster_candidate_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT
    / "tests"
    / "fixtures"
    / "littlefs_util_cluster_upstream_oracle_host.c"
)
LITTLEFS_HEADER = ROOT / "third_party" / "littlefs" / "lfs_util.h"
LITTLEFS_SOURCE = ROOT / "third_party" / "littlefs" / "lfs.c"
LITTLEFS_PROVENANCE = (
    ROOT / "third_party" / "littlefs" / "PROVENANCE.json"
)
LITTLEFS_VERIFIER = (
    ROOT / "third_party" / "littlefs" / "verify_snapshot.py"
)
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

UPSTREAM_COMMIT = "0494ce7169f06a734a7bd7585f49a9fa91fa7318"
UPSTREAM_TREE = "06dd0162169d3cb550cd24a3e34d0e4d02983ad3"
UPSTREAM_HEADER_SHA256 = (
    "f5d249326646c818e62af3cefefe8a57e7b484446a0f48d1050b95e60925088e"
)
UPSTREAM_SOURCE_SHA256 = (
    "81a209e8551754d13b24fc0a2b6707fb3b2475e14feba00bf0df722b98a31398"
)
UPSTREAM_PROVENANCE_SHA256 = (
    "b2f219401b588f5b2b60ba74d8b27a279fa9d30d85724a63e9ab48aca40b46f6"
)
REWIND_SOURCE_PATH = (
    "components/apollo_main/core_overlay/"
    "runtime_littlefs_file_rewind_private.c"
)
REWIND_HEADER_PATH = REWIND_SOURCE_PATH.removesuffix(".c") + ".h"
REWIND_SOURCE_PIN = (
    1_239,
    "e6afb5b67671b3219971b19c20290c601568752d814064147f5ccd4118f5acc8",
)
REWIND_HEADER_PIN = (
    1_743,
    "7430dcd1ad1ea3973d619f2d67d8d8b11a688018d48a3bc26a40e407d1fedb56",
)
REWIND_UPSTREAM_DEFINITION_PIN = (
    118_157,
    192,
    "74638292061613417c2ce7c6bbed200d2bee046c35a7a835fb4d9bb183ab755a",
)
REWIND_STOCK_PIN = (
    "[0x004CE460,0x004CE472)",
    18,
    "be02691b2e7339d7dd1d54b31712c3e8563e5a86f4406a469888640fad9435cd",
    ["0x004CE3BC"],
)
REWIND_PROFILE_PINS = {
    "apple-clang": (
        16,
        124_480,
        "0x007B2964",
        "1c2e2b1fded0de515345b90fe34de51a9c0f08a02a5ad983c1120481c51c5783",
        "46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b",
    ),
    "linux-clang": (
        16,
        126_300,
        "0x007B3080",
        "9731cbf3ff15be31186591ed148d009ae8985cb18bdfca3ba365aeb0897e3fd1",
        "46e8bab056ad39ced45edb5da2612f6470674ab5a428df7f08822f6c2d9e184b",
    ),
}
CANDIDATE_SOURCE_SHA256 = (
    "7abaa8ef1246cc604436dc7db9d1dee1228d20dcf5df4ae9d1ff19ee7f32508e"
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
MAIN_BASE = 0x00438000
BOOT_BASE = 0x00410000
UTILITY_CLUSTER_MAIN = (0x004CA6F8, 0x004CA80A)
UTILITY_CLUSTER_BOOT = (0x00410400, 0x00410512)
UTILITY_CLUSTER_SHA256 = (
    "e45940528fb1cc4eed248f52fa91760b2fec4e2e6829a2acde4da43995fc72e5"
)

STOCK_FUNCTIONS = {
    "max": {
        "size": 8,
        "sha256": (
            "3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464"
        ),
        "main": (0x004CA6F8, 0x004CA700),
        "boot": (0x00410400, 0x00410408),
    },
    "min": {
        "size": 8,
        "sha256": (
            "7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3"
        ),
        "main": (0x004CA700, 0x004CA708),
        "boot": (0x00410408, 0x00410410),
    },
    "aligndown": {
        "size": 12,
        "sha256": (
            "d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349"
        ),
        "main": (0x004CA708, 0x004CA714),
        "boot": (0x00410410, 0x0041041C),
    },
    "alignup": {
        "size": 12,
        "sha256": (
            "18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37"
        ),
        "main": (0x004CA714, 0x004CA720),
        "boot": (0x0041041C, 0x00410428),
    },
    "npw2": {
        "size": 90,
        "sha256": (
            "291ab0ccd15efe1085ce5bcdc6551581ed4eccf67fa84f6560c4500fd68b8b63"
        ),
        "main": (0x004CA720, 0x004CA77A),
        "boot": (0x00410428, 0x00410482),
    },
    "ctz": {
        "size": 16,
        "sha256": (
            "4ae07bfa492e5dfad5869ea491ca43f720e6fc153315a126e2e686313c3de08c"
        ),
        "main": (0x004CA77A, 0x004CA78A),
        "boot": (0x00410482, 0x00410492),
    },
    "popc": {
        "size": 40,
        "sha256": (
            "2cc25090f38dd5c2121cb4bfc7ddf0bd71df984312c9b9c52e87feeef5aea872"
        ),
        "main": (0x004CA78A, 0x004CA7B2),
        "boot": (0x00410492, 0x004104BA),
    },
    "fromle32": {
        "size": 34,
        "sha256": (
            "0666243f83f942c21b4428e4027b6f7815771c2f8a51dcddc550ffa9710add76"
        ),
        "main": (0x004CA7B6, 0x004CA7D8),
        "boot": (0x004104BE, 0x004104E0),
    },
    "tole32": {
        "size": 8,
        "sha256": (
            "b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66"
        ),
        "main": (0x004CA7D8, 0x004CA7E0),
        "boot": (0x004104E0, 0x004104E8),
    },
    "frombe32": {
        "size": 34,
        "sha256": (
            "a0fc2d34d780abf4de23efe08746eefee5cb84cae2728950c4123464e0f952c9"
        ),
        "main": (0x004CA7E0, 0x004CA802),
        "boot": (0x004104E8, 0x0041050A),
    },
    "tobe32": {
        "size": 8,
        "sha256": (
            "b217ac730c7d1b392e0f57a67477d6db88a751a8d3afb3a50ff5bebe0e273f66"
        ),
        "main": (0x004CA802, 0x004CA80A),
        "boot": (0x0041050A, 0x00410512),
    },
    "disk_version_major": {
        "size": 12,
        "sha256": (
            "c9ab0025e9e77a75e9240efbd5b15da22807bdaa9f9deaf2cb425d4850f3bf08"
        ),
        "main": (0x004CB0CA, 0x004CB0D6),
        "boot": (0x00410DD2, 0x00410DDE),
    },
    "disk_version_minor": {
        "size": 10,
        "sha256": (
            "c03343d554dbdd887485eff548d1f2852a1e2f1fe86e662759d478f1d28c7253"
        ),
        "main": (0x004CB0D6, 0x004CB0E0),
        "boot": (0x00410DDE, 0x00410DE8),
    },
}

FUNCTION_SYMBOLS = {
    "max": "open_cfw_littlefs_util_max",
    "min": "open_cfw_littlefs_util_min",
    "aligndown": "open_cfw_littlefs_util_aligndown",
    "alignup": "open_cfw_littlefs_util_alignup",
    "npw2": "open_cfw_littlefs_util_npw2",
    "ctz": "open_cfw_littlefs_util_ctz",
    "popc": "open_cfw_littlefs_util_popc",
    "fromle32": "open_cfw_littlefs_util_fromle32",
    "tole32": "open_cfw_littlefs_util_tole32",
    "frombe32": "open_cfw_littlefs_util_frombe32",
    "tobe32": "open_cfw_littlefs_util_tobe32",
    "disk_version_major": "open_cfw_littlefs_disk_version_major",
    "disk_version_minor": "open_cfw_littlefs_disk_version_minor",
}

MAIN_TARGET = {
    "max": (8, "49828a023d7febe0a7005f10d64021e7ffebe5354dfb50fdfbef19490a76dac0"),
    "min": (8, "761921b20c0aec1b2d8aacbcffd07ba9baf30f1c57c0a89311028adc55e8c126"),
    "aligndown": (8, "965ce09e34fe2ef897bc091faf02f8211bf344c025d769cf440c747fb5f555ee"),
    "alignup": (8, "977169907db28276dc49c7f55020c30af81d04b8fe43d98393cea03b49fccdd1"),
    "npw2": (72, "ef17f9ce9257384acd6010c107338f9d45b2c43b60ef635e970ba54416d3496a"),
    "ctz": (16, "743d892e08268653cd97dcfd35b494def81aff4745bd7467ef6de217189bee1a"),
    "popc": (42, "7b7c7ddb5d9680c5dc736cd13fe67090824cbceece86d99c4f14690abeb230ff"),
    "fromle32": (2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "tole32": (2, "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"),
    "frombe32": (4, "7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11"),
    "tobe32": (4, "90a54a1f68a806a1795bd044856908235426b3c0f67be605fb94d3d5344a747f"),
    "disk_version_major": (10, "ebb72edfdb508cbf5b617452eb60cbceb58bfdfc879dcece076544efa75c092f"),
    "disk_version_minor": (10, "da349b05b3a26d6a22ba3f707c4c21e1591915aeb8451e21f7509905926a4b9d"),
}
BOOT_TARGET = {
    **MAIN_TARGET,
    "max": (8, "00cbab254132bf12554d58b011edf1b5e3b1e36ff5d55a671d2ab04e5b8428a5"),
    "min": (8, "36bb5e2d905d59628b5170a2cfecbf56f3200abb3207bfa30b50eaf3b4b44ab4"),
    "npw2": (56, "1048afe6eb2c306231e410f0a864ab5bfab3c9b0567e1fba6ec61f8bae53094a"),
    "popc": (42, "e537e00ef37eced668a9d421f28e84d54a2b6ea09ea1cfda00f96ec1d65891f7"),
}

COMMON_TARGET_FLAGS = [
    "-mthumb",
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
TARGET_PROFILES = {
    "main": [
        "--target=thumbv7em-none-eabi",
        "-O2",
        *COMMON_TARGET_FLAGS,
    ],
    "boot": [
        "--target=arm-none-eabi",
        "-mcpu=cortex-m55",
        "-Oz",
        *COMMON_TARGET_FLAGS,
    ],
}

EXPECTED_RELOCATIONS = {
    (
        "open_cfw_littlefs_util_alignup",
        30,
        "open_cfw_littlefs_util_aligndown",
    ),
    (
        "open_cfw_littlefs_util_ctz",
        10,
        "open_cfw_littlefs_util_npw2",
    ),
    (
        "open_cfw_littlefs_util_tobe32",
        30,
        "open_cfw_littlefs_util_frombe32",
    ),
    (
        "open_cfw_littlefs_disk_version_major",
        10,
        "open_cfw_littlefs_disk_version",
    ),
    (
        "open_cfw_littlefs_disk_version_minor",
        10,
        "open_cfw_littlefs_disk_version",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class LittlefsUtilClusterCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.main_package = MAIN_PACKAGE.read_bytes()
        cls.main = cls.main_package[32:]
        cls.boot = BOOT_IMAGE.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)

        cls.candidate = cls.compile_host_library(
            CANDIDATE_FIXTURE,
            temporary / cls.library_name("littlefs_util_candidate"),
        )
        cls.oracle = cls.compile_host_library(
            UPSTREAM_FIXTURE,
            temporary / cls.library_name("littlefs_util_oracle"),
        )
        cls.candidate_api = cls.bind_api(
            cls.candidate,
            "open_cfw_test_littlefs_util_",
            has_setter=True,
        )
        cls.oracle_api = cls.bind_api(
            cls.oracle,
            "open_cfw_oracle_littlefs_util_",
            has_setter=False,
        )

        cls.target_objects: dict[str, Path] = {}
        for profile, flags in TARGET_PROFILES.items():
            output = temporary / f"littlefs_util_{profile}.o"
            subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *flags,
                    "-c",
                    str(CANDIDATE_SOURCE),
                    "-o",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_objects[profile] = output

        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay

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
        *,
        has_setter: bool,
    ) -> dict[str, Any]:
        api: dict[str, Any] = {}
        for name in ("max", "min", "aligndown", "alignup"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        for name in (
            "npw2",
            "ctz",
            "popc",
            "fromle32",
            "tole32",
            "frombe32",
            "tobe32",
        ):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = [ctypes.c_uint32]
            api[name].restype = ctypes.c_uint32
        for name in ("disk_version_major", "disk_version_minor"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_uint16
        for name in ("uint8_size", "uint16_size", "uint32_size"):
            api[name] = getattr(library, prefix + name)
            api[name].argtypes = []
            api[name].restype = ctypes.c_size_t
        if has_setter:
            api["set_disk_version"] = getattr(
                library,
                prefix + "set_disk_version",
            )
            api["set_disk_version"].argtypes = [ctypes.c_uint32]
            api["set_disk_version"].restype = None
        return api

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def span(data: bytes, base: int, bounds: tuple[int, int]) -> bytes:
        start, end = bounds
        return data[start - base:end - base]

    @staticmethod
    def fallback_npw2(value: int) -> int:
        value = (value - 1) & 0xFFFFFFFF
        result = 0
        for threshold, shift in (
            (0xFFFF, 16),
            (0xFF, 8),
            (0xF, 4),
            (0x3, 2),
        ):
            selected_shift = shift if value > threshold else 0
            value >>= selected_shift
            result |= selected_shift
        return (result | (value >> 1)) + 1

    @classmethod
    def fallback_ctz(cls, value: int) -> int:
        low_bit_plus_one = ((value & -value) + 1) & 0xFFFFFFFF
        return (cls.fallback_npw2(low_bit_plus_one) - 1) & 0xFFFFFFFF

    @staticmethod
    def byteswap32(value: int) -> int:
        return int.from_bytes(
            value.to_bytes(4, byteorder="little"),
            byteorder="big",
        )

    def parse_target(
        self,
        path: Path,
    ) -> tuple[dict[str, bytes], set[tuple[str, int, str]], set[str]]:
        data, sections = self.apollo_overlay.parse_elf32(path)
        text = self.apollo_overlay.section_named(sections, ".text")
        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]

        parsed_symbols: list[tuple[str, tuple[int, ...]]] = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = self.apollo_overlay.elf_string(
                strings,
                fields[0],
                "symbol",
            )
            parsed_symbols.append((name, fields))

        selected = {
            name: fields
            for name, fields in parsed_symbols
            if name in FUNCTION_SYMBOLS.values()
        }
        function_bytes = {}
        function_ranges = []
        for name, fields in selected.items():
            self.assertEqual(fields[5], text["index"])
            start = fields[1] & ~1
            end = start + fields[2]
            function_ranges.append((start, end, name))
            function_bytes[name] = data[
                int(text["offset"]) + start:
                int(text["offset"]) + end
            ]

        relocations = set()
        for section in sections:
            if (
                int(section["type"]) != 9
                or int(section["info"]) != int(text["index"])
            ):
                continue
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    data,
                    int(section["offset"]) + index * 8,
                )
                owner = next(
                    name
                    for start, end, name in function_ranges
                    if start <= offset < end
                )
                target = parsed_symbols[information >> 8][0]
                relocations.add((owner, information & 0xFF, target))

        undefined = {
            name
            for name, fields in parsed_symbols
            if name and fields[5] == 0 and name != "$t.0"
        }
        return function_bytes, relocations, undefined

    def test_authenticated_upstream_snapshot_and_candidate_pin(self) -> None:
        subprocess.run(
            [sys.executable, str(LITTLEFS_VERIFIER)],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        provenance = json.loads(LITTLEFS_PROVENANCE.read_text("utf-8"))
        self.assertEqual(provenance["schema_version"], 1)
        self.assertEqual(provenance["component"], "littlefs")
        self.assertEqual(provenance["license"], "BSD-3-Clause")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(
            provenance["upstream"]["selected_tree"],
            UPSTREAM_TREE,
        )
        self.assertEqual(
            provenance["selection"]["classification"],
            "source-equivalent release baseline",
        )
        self.assertFalse(
            provenance["selection"]["exact_historical_checkout_proven"]
        )
        integration = provenance["production_integration"]
        self.assertIn("source-equivalent", integration["qualification"])
        self.assertIn("not proof", integration["qualification"])
        self.assertIn(
            REWIND_SOURCE_PATH,
            integration["allowed_production_source_paths"],
        )
        self.assertIn(
            REWIND_HEADER_PATH,
            integration["allowed_production_source_paths"],
        )
        self.assertIn(
            "open_cfw_littlefs_file_rewind_private",
            integration["allowed_production_symbols"],
        )
        rewind = integration["rewind_leaf"]
        self.assertEqual(
            (
                rewind["upstream_definition_offset"],
                rewind["upstream_definition_size"],
                rewind["upstream_definition_sha256"],
            ),
            REWIND_UPSTREAM_DEFINITION_PIN,
        )
        self.assertEqual(
            (rewind["local_source_size"], rewind["local_source_sha256"]),
            REWIND_SOURCE_PIN,
        )
        self.assertEqual(
            (rewind["local_header_size"], rewind["local_header_sha256"]),
            REWIND_HEADER_PIN,
        )
        self.assertEqual(
            (
                rewind["stock_span"],
                rewind["stock_size"],
                rewind["stock_sha256"],
                rewind["stock_seek_seams"],
            ),
            REWIND_STOCK_PIN,
        )
        self.assertEqual(
            {
                name: (
                    profile["leaf_size"],
                    profile["overlay_offset"],
                    profile["runtime_address"],
                    profile["relocated_sha256"],
                    profile["unrelocated_sha256"],
                )
                for name, profile in rewind["production_profiles"].items()
            },
            REWIND_PROFILE_PINS,
        )
        self.assertEqual(
            rewind["sole_relocation"],
            {
                "offset": 6,
                "type": "R_ARM_THM_CALL",
                "symbol": "open_cfw_littlefs_file_seek_private",
                "symbol_type": "STT_NOTYPE",
                "target_address": "0x004CE3BC",
            },
        )
        self.assertEqual(
            sha256(LITTLEFS_HEADER.read_bytes()),
            UPSTREAM_HEADER_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_SOURCE.read_bytes()),
            UPSTREAM_SOURCE_SHA256,
        )
        self.assertEqual(
            sha256(LITTLEFS_PROVENANCE.read_bytes()),
            UPSTREAM_PROVENANCE_SHA256,
        )
        self.assertEqual(
            sha256(CANDIDATE_SOURCE.read_bytes()),
            CANDIDATE_SOURCE_SHA256,
        )

        candidate = CANDIDATE_SOURCE.read_text("ascii")
        self.assertIn(
            "#define OPEN_CFW_LITTLEFS_UTIL_LFS_NO_INTRINSICS 1",
            candidate,
        )
        self.assertNotIn("__builtin_clz", candidate)
        self.assertNotIn("__builtin_ctz", candidate)
        self.assertNotIn("__builtin_popcount", candidate)

    def test_complete_images_and_dual_image_stock_spans_are_pinned(
        self,
    ) -> None:
        self.assertEqual(sha256(self.main_package), MAIN_PACKAGE_SHA256)
        self.assertEqual(sha256(self.main), MAIN_PAYLOAD_SHA256)
        self.assertEqual(sha256(self.boot), BOOT_SHA256)

        main_cluster = self.span(
            self.main,
            MAIN_BASE,
            UTILITY_CLUSTER_MAIN,
        )
        boot_cluster = self.span(
            self.boot,
            BOOT_BASE,
            UTILITY_CLUSTER_BOOT,
        )
        self.assertEqual(main_cluster, boot_cluster)
        self.assertEqual(len(main_cluster), 274)
        self.assertEqual(sha256(main_cluster), UTILITY_CLUSTER_SHA256)

        for name, expected in STOCK_FUNCTIONS.items():
            with self.subTest(function=name):
                main = self.span(self.main, MAIN_BASE, expected["main"])
                boot = self.span(self.boot, BOOT_BASE, expected["boot"])
                self.assertEqual(main, boot)
                self.assertEqual(len(main), expected["size"])
                self.assertEqual(sha256(main), expected["sha256"])

    def test_candidate_abi_widths_match_pristine_upstream(self) -> None:
        expected = {
            "uint8_size": 1,
            "uint16_size": 2,
            "uint32_size": 4,
        }
        for name, size in expected.items():
            with self.subTest(type=name):
                self.assertEqual(self.candidate_api[name](), size)
                self.assertEqual(
                    self.candidate_api[name](),
                    self.oracle_api[name](),
                )

    def test_max_min_and_alignment_match_upstream(self) -> None:
        values = (
            0,
            1,
            2,
            3,
            15,
            16,
            255,
            256,
            4095,
            4096,
            0x7FFFFFFF,
            0x80000000,
            0xFFFFFFFE,
            0xFFFFFFFF,
        )
        for a in values:
            for b in values:
                with self.subTest(operation="max", a=a, b=b):
                    expected = max(a, b)
                    self.assertEqual(self.candidate_api["max"](a, b), expected)
                    self.assertEqual(self.oracle_api["max"](a, b), expected)
                with self.subTest(operation="min", a=a, b=b):
                    expected = min(a, b)
                    self.assertEqual(self.candidate_api["min"](a, b), expected)
                    self.assertEqual(self.oracle_api["min"](a, b), expected)

        alignments = (
            1,
            2,
            3,
            4,
            7,
            8,
            16,
            255,
            256,
            4096,
            0x80000000,
            0xFFFFFFFF,
        )
        for value in values:
            for alignment in alignments:
                with self.subTest(
                    operation="aligndown",
                    value=value,
                    alignment=alignment,
                ):
                    expected = value - (value % alignment)
                    self.assertEqual(
                        self.candidate_api["aligndown"](value, alignment),
                        expected,
                    )
                    self.assertEqual(
                        self.oracle_api["aligndown"](value, alignment),
                        expected,
                    )
                with self.subTest(
                    operation="alignup",
                    value=value,
                    alignment=alignment,
                ):
                    wrapped = (value + alignment - 1) & 0xFFFFFFFF
                    expected = wrapped - (wrapped % alignment)
                    self.assertEqual(
                        self.candidate_api["alignup"](value, alignment),
                        expected,
                    )
                    self.assertEqual(
                        self.oracle_api["alignup"](value, alignment),
                        expected,
                    )

    def test_fallback_bit_and_endian_helpers_match_upstream(self) -> None:
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
            0x7FFFFFFF,
            0x80000000,
            0xFFFFFFFE,
            0xFFFFFFFF,
            0x01020304,
            0xA5A5A5A5,
        ]
        generator = random.Random(0x4C465355)
        values.extend(generator.getrandbits(32) for _ in range(10_000))

        for value in values:
            expected = {
                "npw2": self.fallback_npw2(value),
                "ctz": self.fallback_ctz(value),
                "popc": bin(value).count("1"),
                "fromle32": value,
                "tole32": value,
                "frombe32": self.byteswap32(value),
                "tobe32": self.byteswap32(value),
            }
            for name, result in expected.items():
                with self.subTest(function=name, value=value):
                    self.assertEqual(self.candidate_api[name](value), result)
                    self.assertEqual(self.oracle_api[name](value), result)

    def test_disk_version_pair_closes_over_source_provider(self) -> None:
        self.assertEqual(
            self.oracle_api["disk_version_major"](),
            0x0002,
        )
        self.assertEqual(
            self.oracle_api["disk_version_minor"](),
            0x0001,
        )
        for version in (
            0,
            1,
            0x00020001,
            0x0102A0B0,
            0xFFFF0000,
            0xFFFFFFFF,
        ):
            with self.subTest(version=version):
                self.candidate_api["set_disk_version"](version)
                self.assertEqual(
                    self.candidate_api["disk_version_major"](),
                    version >> 16,
                )
                self.assertEqual(
                    self.candidate_api["disk_version_minor"](),
                    version & 0xFFFF,
                )

    def test_target_profiles_have_pinned_closed_function_bodies(self) -> None:
        for profile, expected in (
            ("main", MAIN_TARGET),
            ("boot", BOOT_TARGET),
        ):
            with self.subTest(profile=profile):
                function_bytes, relocations, undefined = self.parse_target(
                    self.target_objects[profile]
                )
                self.assertEqual(
                    set(function_bytes),
                    set(FUNCTION_SYMBOLS.values()),
                )
                for name, (size, digest) in expected.items():
                    symbol = FUNCTION_SYMBOLS[name]
                    body = function_bytes[symbol]
                    self.assertEqual(len(body), size)
                    self.assertEqual(sha256(body), digest)
                self.assertEqual(relocations, EXPECTED_RELOCATIONS)
                self.assertEqual(
                    undefined,
                    {"open_cfw_littlefs_disk_version"},
                )


if __name__ == "__main__":
    unittest.main()
