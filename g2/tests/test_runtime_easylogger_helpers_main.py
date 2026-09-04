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
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
UPSTREAM_CORE = ROOT / "third_party" / "easylogger" / "src" / "elog.c"
UPSTREAM_UTILS = (
    ROOT / "third_party" / "easylogger" / "src" / "elog_utils.c"
)
UPSTREAM_HEADER = ROOT / "third_party" / "easylogger" / "inc" / "elog.h"
UPSTREAM_CONFIG = (
    ROOT / "third_party" / "easylogger" / "inc" / "elog_cfg.h"
)
UPSTREAM_VERIFIER = ROOT / "third_party" / "easylogger" / "verify_snapshot.py"
SOURCE = (
    ROOT
    / "components"
    / "shared"
    / "easylogger"
    / "runtime_easylogger_helpers.c"
)
SOURCE_HEADER = SOURCE.with_suffix(".h")
PRODUCTION_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)

APPLICATION_BASE = 0x0043_8000
WRAPPER_SIZE = 3_523_396
WRAPPER_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
PAYLOAD_SIZE = 3_523_364
PAYLOAD_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

FUNCTIONS = {
    "get_fmt_enabled": {
        "start": 0x0043_D97C,
        "end": 0x0043_D9E6,
        "sha256": (
            "d0a18c1e6bc1a42e8a91b37c891aaf34"
            "25b98f6bc56741211512d871056b136d"
        ),
        "predecessor": "f08f00001b5b0000",
        "predecessor_sha256": (
            "7dee118caa57733779c32f385e4af373b"
            "b0222f927835758564429bec74b96de"
        ),
        "successor": "0000200000005b00",
        "successor_sha256": (
            "cbc80b7beecf3830309f85ff345e84131"
            "4f70876178b098870c20b30768c9f58"
        ),
    },
    "get_fmt_used_and_enabled_u32": {
        "start": 0x0043_D9F0,
        "end": 0x0043_DA0A,
        "sha256": (
            "95bba933ae9e65022ef0ff0daa7632467"
            "8aa539c2ba79435b80181ce34a23db7"
        ),
        "predecessor": "200000005b000000",
        "predecessor_sha256": (
            "0b93fbe533e81445248199e0ff59c6c82"
            "722d26ccf83384225168252f1790393"
        ),
        "successor": "80b5002a06d0c0b2",
        "successor_sha256": (
            "20c5fb578148fa722bd45382ebc8332252"
            "1f01946a65ad20cf2e3773f4afa735"
        ),
    },
    "get_fmt_used_and_enabled_ptr": {
        "start": 0x0043_DA0A,
        "end": 0x0043_DA24,
        "sha256": (
            "3af2631ad7a44be557a9454da2df68862"
            "b6458bf2359f58d41c3d6d2ff86c8a2"
        ),
        "predecessor": "00e00020c0b202bd",
        "predecessor_sha256": (
            "198c8d06fec9c3b72e6dfe95d3a7c172"
            "76c837154b45dd42d804384aa9d0d86b"
        ),
        "successor": "80b5124981f8f200",
        "successor_sha256": (
            "3b8e577b95351a9eb82128e1b79647cd"
            "b62eb9becc65a9a301818d81ed068ce1"
        ),
    },
    "elog_strcpy": {
        "start": 0x0044_B668,
        "end": 0x0044_B70A,
        "sha256": (
            "aac245096c55f678eec81bf04dfe27ef6"
            "3fffbe1c225e8ab73fe99f6c97f1997"
        ),
        "predecessor": "002befd170bd0000",
        "predecessor_sha256": (
            "c1e957ba8c55b09b772dd7a1af8f5ed3"
            "6125b34b41944a1415d52e99317eaf7c"
        ),
        "successor": "0000647374007372",
        "successor_sha256": (
            "23aab33d03e86cc598a1904c7011dab0e"
            "10734e6f0a71b6d604d7999fbaeac6c"
        ),
    },
}
STOCK_CLOSURE_SIZE = 320
STOCK_CLOSURE_SHA256 = (
    "26e192374322d5c4dceafbeda6e57ae5"
    "6ebc24609f2251c0bcf1708087a76306"
)

CALLERS = {
    "get_fmt_enabled": [
        (0x0043_D688, "00f078f9"),
        (0x0043_D6B2, "00f063f9"),
        (0x0043_D706, "00f039f9"),
        (0x0043_D726, "00f029f9"),
        (0x0043_D746, "00f019f9"),
        (0x0043_D762, "00f00bf9"),
        (0x0043_D782, "00f0fbf8"),
        (0x0043_D79E, "00f0edf8"),
        (0x0043_D9F8, "fff7c0ff"),
        (0x0043_DA12, "fff7b3ff"),
    ],
    "get_fmt_used_and_enabled_u32": [
        (0x0043_D7F2, "00f0fdf8"),
        (0x0043_D852, "00f0cdf8"),
        (0x0043_D870, "00f0bef8"),
    ],
    "get_fmt_used_and_enabled_ptr": [
        (0x0043_D7D2, "00f01af9"),
        (0x0043_D7E2, "00f012f9"),
        (0x0043_D814, "00f0f9f8"),
        (0x0043_D832, "00f0eaf8"),
        (0x0043_D89A, "00f0b6f8"),
        (0x0043_D8B8, "00f0a7f8"),
    ],
    "elog_strcpy": [
        (0x0043_D664, "0ef000f8"),
        (0x0043_D67C, "0df0f4ff"),
        (0x0043_D6A6, "0df0dfff"),
        (0x0043_D6C6, "0df0cfff"),
        (0x0043_D6EC, "0df0bcff"),
        (0x0043_D6FA, "0df0b5ff"),
        (0x0043_D71A, "0df0a5ff"),
        (0x0043_D73A, "0df095ff"),
        (0x0043_D756, "0df087ff"),
        (0x0043_D776, "0df077ff"),
        (0x0043_D792, "0df069ff"),
        (0x0043_D7B2, "0df059ff"),
        (0x0043_D7C0, "0df052ff"),
        (0x0043_D806, "0df02fff"),
        (0x0043_D824, "0df020ff"),
        (0x0043_D842, "0df011ff"),
        (0x0043_D862, "0df001ff"),
        (0x0043_D88C, "0df0ecfe"),
        (0x0043_D8AA, "0df0ddfe"),
        (0x0043_D8C8, "0df0cefe"),
        (0x0043_D8D6, "0df0c7fe"),
        (0x0043_D94C, "0df08cfe"),
        (0x0043_D95A, "0df085fe"),
        (0x0043_DB30, "0df09afd"),
        (0x0043_DBCA, "0df04dfd"),
        (0x0043_DBEA, "0df03dfd"),
        (0x0043_DC10, "0df02afd"),
        (0x0043_DC72, "0df0f9fc"),
    ],
}
CALLER_DIGESTS = {
    "get_fmt_enabled": (
        "dfeaf0c883a7e9e23c2eb09e5f14f934"
        "da56e4a9d3ea5972bccccd3406d9612c"
    ),
    "get_fmt_used_and_enabled_u32": (
        "2dfdd9b59819f72c56f2bc6a7d86889d"
        "2306f364ed9ac385a1ee1ffe5d5ec491"
    ),
    "get_fmt_used_and_enabled_ptr": (
        "a1b68901945b68e29b7994d29c0299af"
        "9f472d4eb4ba08dd747b3af671d5cec2"
    ),
    "elog_strcpy": (
        "de8c90c8d7cce895b040306fb993f9c1c"
        "bc05ddb4e61f6c6bdceb0d852544963"
    ),
}

OUTPUT_ENTRY = 0x0043_D574
ASSERT_WAIT = 0x0044_B0AE
LOGGER_ADDRESS = 0x2007_0BE8
ASSERT_HOOK_ADDRESS = 0x2007_456C
OUTGOING_WIDE_CALLS = {
    "get_fmt_enabled": [
        (0x0043_D9B2, "fff7dffd", OUTPUT_ENTRY),
        (0x0043_D9B6, "0df07afb", ASSERT_WAIT),
    ],
    "get_fmt_used_and_enabled_u32": [
        (0x0043_D9F8, "fff7c0ff", 0x0043_D97C),
    ],
    "get_fmt_used_and_enabled_ptr": [
        (0x0043_DA12, "fff7b3ff", 0x0043_D97C),
    ],
    "elog_strcpy": [
        (0x0044_B69A, "f1f76bff", OUTPUT_ENTRY),
        (0x0044_B69E, "fff706fd", ASSERT_WAIT),
        (0x0044_B6D4, "f1f74eff", OUTPUT_ENTRY),
        (0x0044_B6D8, "fff7e9fc", ASSERT_WAIT),
    ],
}

SOURCE_SIZE = 4_975
SOURCE_SHA256 = (
    "8f2850f789fba3b08bdc3e1fa8f3a464"
    "6aaef7e4b16862f3be53478071aa22b5"
)
SOURCE_HEADER_SIZE = 6_505
SOURCE_HEADER_SHA256 = (
    "f3a7e9bce0f136a2ff4a76929c317aef"
    "7bbc7c29dfc60d58311d94e58f6e2393"
)
TARGET_FLAGS = [
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
    "-ffunction-sections",
    "-fdata-sections",
    "-Wall",
    "-Wextra",
    "-Werror",
]
TARGET_PROFILE_FLAGS = [
    "-DOPEN_CFW_EASYLOGGER_HELPERS_PROFILE="
    "OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_APOLLO_MAIN",
    "-DOPEN_CFW_EASYLOGGER_HELPERS_BUILD_LEAF=1",
]
TARGETS = {
    "open_cfw_easylogger_strcpy": {
        "macro": "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_STRCPY",
        "size": 130,
        "sha256": (
            "2dc0289602225d43cdcf604a5c47c1d74"
            "a5060900fa8ade2aa5be94c6b6815c8"
        ),
        "bytes": (
            "f0b581b014460d46064649b36cb32178204699b30020b0eb962f20462ed10020"
            "40f2fe3e40f2fd3c231829545f7807b3321872451dd829184f709f78dfb162451"
            "9d88f70df78c7b1b2f57f7f15d8cf701979043011b1b2f57f7fe5d320440de0"
            "2c20fff7feff002cd1d12d20fff7feffcde7581c02e0981c00e0d81c001b01b0"
            "f0bd"
        ),
        "relocations": [
            (0x62, 10, "open_cfw_easylogger_helpers_assert_failed"),
            (0x6C, 10, "open_cfw_easylogger_helpers_assert_failed"),
        ],
    },
    "open_cfw_easylogger_get_fmt_enabled": {
        "macro": "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_ENABLED",
        "size": 38,
        "sha256": (
            "b4441bd7ded864834ac501bad704026003"
            "3eb235f33317cdab586ffec002507f"
        ),
        "bytes": (
            "b0b5044606280d4603d340f2e720fff7fefffff7feff00eb8400"
            "d0f8d800284018bf0120b0bd"
        ),
        "relocations": [
            (0x0E, 10, "open_cfw_easylogger_helpers_assert_failed"),
            (0x12, 10, "open_cfw_easylogger_helpers_get_logger"),
        ],
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
        "macro": (
            "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_U32"
        ),
        "size": 22,
        "sha256": (
            "7837c848df3a0acb43f4d05804610e5a"
            "d79275ea2e0daf86f986835ad3aaecc5"
        ),
        "bytes": (
            "002a04bf0020704780b5fff7feff002818bf012080bd"
        ),
        "relocations": [
            (0x0A, 10, "open_cfw_easylogger_get_fmt_enabled"),
        ],
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
        "macro": (
            "OPEN_CFW_EASYLOGGER_HELPERS_LEAF_GET_FMT_USED_AND_ENABLED_PTR"
        ),
        "size": 22,
        "sha256": (
            "7837c848df3a0acb43f4d05804610e5a"
            "d79275ea2e0daf86f986835ad3aaecc5"
        ),
        "bytes": (
            "002a04bf0020704780b5fff7feff002818bf012080bd"
        ),
        "relocations": [
            (0x0A, 10, "open_cfw_easylogger_get_fmt_enabled"),
        ],
    },
}
TARGET_CLOSURE_SIZE = 212
TARGET_CLOSURE_SHA256 = (
    "682363db5f9393d204f3ca9b8a620fa0"
    "1c399d012381724213bf380336d8aa24"
)
PRODUCTION_OVERLAY_SIZE = 380_444
PRODUCTION_OVERLAY_SHA256 = (
    "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622"
)
PRODUCTION_COMPONENT_SIZE = 3_903_840
PRODUCTION_COMPONENT_SHA256 = (
    "2fe63dbce04257b3961fa80702e62fe4e5ee9859df5908b9245377f272c60752"
)
PRODUCTION_LEAVES = {
    "open_cfw_easylogger_helpers_get_logger": {
        "offset": 114_920,
        "size": 10,
        "padding_before": 2,
        "runtime_address": 0x007B_040C,
        "sha256": (
            "5970df921f43a013c1198a9d9a5fc1c1"
            "67e7d6b104aaefa8135d94630c3aea5b"
        ),
        "unrelocated_sha256": (
            "5970df921f43a013c1198a9d9a5fc1c1"
            "67e7d6b104aaefa8135d94630c3aea5b"
        ),
        "relocations": [],
    },
    "open_cfw_easylogger_helpers_assert_failed": {
        "offset": 114_932,
        "size": 168,
        "padding_before": 2,
        "runtime_address": 0x007B_0418,
        "sha256": (
            "2437cde26a848cd283fbf7d67862f63f"
            "1bdd3262f6db17dc19ffb36ba51fa3bc"
        ),
        "unrelocated_sha256": (
            "2437cde26a848cd283fbf7d67862f63f"
            "1bdd3262f6db17dc19ffb36ba51fa3bc"
        ),
        "relocations": [],
    },
    "open_cfw_easylogger_get_fmt_enabled": {
        "offset": 115_100,
        "size": 38,
        "padding_before": 0,
        "runtime_address": 0x007B_04C0,
        "sha256": (
            "93a04bebddcaabf397058f30793491388"
            "8c49cca4135c5dfd4b1177ebe7a0624"
        ),
        "unrelocated_sha256": TARGETS[
            "open_cfw_easylogger_get_fmt_enabled"
        ]["sha256"],
        "relocations": [
            (
                0x0E,
                0x007B_04CE,
                "open_cfw_easylogger_helpers_assert_failed",
                0x007B_0418,
            ),
            (
                0x12,
                0x007B_04D2,
                "open_cfw_easylogger_helpers_get_logger",
                0x007B_040C,
            ),
        ],
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
        "offset": 115_140,
        "size": 22,
        "padding_before": 2,
        "runtime_address": 0x007B_04E8,
        "sha256": (
            "353077e72b5c3fdb3534472dcb345e48"
            "23670d971233e94f4b3df3afc90e871e"
        ),
        "unrelocated_sha256": TARGETS[
            "open_cfw_easylogger_get_fmt_used_and_enabled_u32"
        ]["sha256"],
        "relocations": [
            (
                0x0A,
                0x007B_04F2,
                "open_cfw_easylogger_get_fmt_enabled",
                0x007B_04C0,
            ),
        ],
    },
    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
        "offset": 115_164,
        "size": 22,
        "padding_before": 2,
        "runtime_address": 0x007B_0500,
        "sha256": (
            "6c5f1c48b7e8fb80e64c9db3e096a92"
            "3894770b482c17a7a9b78af9f4c3ed56f"
        ),
        "unrelocated_sha256": TARGETS[
            "open_cfw_easylogger_get_fmt_used_and_enabled_ptr"
        ]["sha256"],
        "relocations": [
            (
                0x0A,
                0x007B_050A,
                "open_cfw_easylogger_get_fmt_enabled",
                0x007B_04C0,
            ),
        ],
    },
    "open_cfw_easylogger_strcpy": {
        "offset": 115_188,
        "size": 130,
        "padding_before": 2,
        "runtime_address": 0x007B_0518,
        "sha256": (
            "28596bd394c2cec04862dd33abf23595"
            "b937e6b1908f9b77a36e4160d0697ff1"
        ),
        "unrelocated_sha256": TARGETS[
            "open_cfw_easylogger_strcpy"
        ]["sha256"],
        "relocations": [
            (
                0x62,
                0x007B_057A,
                "open_cfw_easylogger_helpers_assert_failed",
                0x007B_0418,
            ),
            (
                0x6C,
                0x007B_0584,
                "open_cfw_easylogger_helpers_assert_failed",
                0x007B_0418,
            ),
        ],
    },
}
PRODUCTION_PATCHES = {
    "replace_easylogger_get_fmt_enabled": (
        "get_fmt_enabled",
        "open_cfw_easylogger_get_fmt_enabled",
        "01f3ea2ea7f0c1f824f7e9db9013fb5d"
        "f0f2ff03db269683c90c8234151aca78",
    ),
    "replace_easylogger_get_fmt_used_and_enabled_u32": (
        "get_fmt_used_and_enabled_u32",
        "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
        "b5ef9a3d023653a576ca0476385bc155"
        "d248a4b9240b3c3e8d4527509aed319c",
    ),
    "replace_easylogger_get_fmt_used_and_enabled_ptr": (
        "get_fmt_used_and_enabled_ptr",
        "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
        "ac3835d213636c886f037848c98ee2d2"
        "fb8b238692fadd2e56b9b55d4a27ec89",
    ),
    "replace_easylogger_strcpy": (
        "elog_strcpy",
        "open_cfw_easylogger_strcpy",
        "cbaae722e5f03b04628f54f7184775d3"
        "f28b5ad72a6530c6da2282a8c1061d01",
    ),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return (address + 4 + immediate * 2,)
    if (
        halfword & 0xF000 == 0xD000
        and ((halfword >> 8) & 0x0F) < 0x0E
    ):
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return (address + 4 + immediate * 2,)
    if halfword & 0xF500 == 0xB100:
        immediate = (
            (((halfword >> 9) & 1) << 5)
            | ((halfword >> 3) & 0x1F)
        )
        return (address + 4 + immediate * 2,)
    return ()


_APPLE_ONLY = unittest.skipUnless(
    (os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang") == "apple-clang",
    "byte-exact / toolchain-specific Apple-clang assertion; Linux byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)


class EasyLoggerTagLevel32(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("tag", ctypes.c_char * 31),
        ("tag_use_flag", ctypes.c_uint8),
    ]


class EasyLoggerFilter32(ctypes.Structure):
    _fields_ = [
        ("level", ctypes.c_uint8),
        ("tag", ctypes.c_char * 31),
        ("keyword", ctypes.c_char * 17),
        ("tag_level", EasyLoggerTagLevel32 * 5),
    ]


class EasyLogger32(ctypes.Structure):
    _fields_ = [
        ("filter", EasyLoggerFilter32),
        ("enabled_format_set", ctypes.c_uint32 * 6),
        ("init_ok", ctypes.c_uint8),
        ("output_enabled", ctypes.c_uint8),
        ("output_lock_enabled", ctypes.c_uint8),
        ("output_is_locked_before_enable", ctypes.c_uint8),
        ("output_is_locked_before_disable", ctypes.c_uint8),
        ("text_color_enabled", ctypes.c_uint8),
    ]


class RuntimeEasyLoggerHelpersMainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.wrapper = OFFICIAL.read_bytes()
        cls.application = cls.wrapper[32:]
        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="test-runtime-easylogger-helpers-main-",
            dir=temporary_parent,
        )
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.target_profiles = {}
        for function, expected in TARGETS.items():
            object_path = Path(cls.temporary.name) / f"{function}.o"
            compile_result = subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *TARGET_FLAGS,
                    *TARGET_PROFILE_FLAGS,
                    f"-D{expected['macro']}=1",
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(object_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if compile_result.returncode:
                raise AssertionError(
                    compile_result.stderr or compile_result.stdout
                )
            elf, sections = apollo_overlay.parse_elf32(object_path)
            symbols = apollo_overlay.parse_elf32_symbols(elf, sections)
            sections_by_name = {
                str(section["name"]): section for section in sections
            }
            text_section = sections_by_name[f".text.{function}"]
            text = elf[
                int(text_section["offset"]):
                int(text_section["offset"]) + int(text_section["size"])
            ]
            relocation_name = f".rel.text.{function}"
            relocations = []
            if relocation_name in sections_by_name:
                relocation_section = sections_by_name[relocation_name]
                for offset in range(
                    int(relocation_section["offset"]),
                    int(relocation_section["offset"])
                    + int(relocation_section["size"]),
                    8,
                ):
                    relocation_offset, information = struct.unpack_from(
                        "<II",
                        elf,
                        offset,
                    )
                    relocations.append(
                        (
                            relocation_offset,
                            information & 0xFF,
                            str(symbols[information >> 8]["name"]),
                        )
                    )
            cls.target_profiles[function] = {
                "compile": compile_result,
                "elf": elf,
                "sections": sections,
                "symbols": symbols,
                "text_section": text_section,
                "text": text,
                "relocations": relocations,
            }
        production_output = (
            Path(cls.temporary.name) / "production-apollo-main"
        )
        production_config = json.loads(
            PRODUCTION_CONFIG.read_text(encoding="utf-8")
        )
        production_config["expected"] = dict(
            production_config["core_stage_expected"]
        )
        for profile in production_config["toolchain_profiles"].values():
            profile["expected"] = dict(profile["core_stage_expected"])
        production_config_path = (
            Path(cls.temporary.name) / "production-core-stage.json"
        )
        production_config_path.write_text(
            json.dumps(production_config, indent=2) + "\n",
            encoding="utf-8",
        )
        cls.production_report = apollo_overlay.build(
            root=ROOT,
            config_path=production_config_path,
            output_dir=production_output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.production_overlay = (
            production_output / "apollo_core_overlay.bin"
        ).read_bytes()
        cls.production_component = (
            production_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def read_u32(self, address: int) -> int:
        return struct.unpack(
            "<I",
            self.span(address, address + 4),
        )[0]

    def read_c_string(self, address: int) -> str:
        tail = self.application[address - APPLICATION_BASE:]
        return tail[:tail.index(0)].decode("ascii")

    def test_official_wrapper_payload_spans_neighbors_and_closure_are_exact(
        self,
    ) -> None:
        self.assertEqual(
            (len(self.wrapper), sha256(self.wrapper)),
            (WRAPPER_SIZE, WRAPPER_SHA256),
        )
        self.assertEqual(
            (len(self.application), sha256(self.application)),
            (PAYLOAD_SIZE, PAYLOAD_SHA256),
        )
        closure = bytearray()
        for name, details in FUNCTIONS.items():
            with self.subTest(function=name):
                start = int(details["start"])
                end = int(details["end"])
                body = self.span(start, end)
                self.assertEqual(len(body), end - start)
                self.assertEqual(sha256(body), details["sha256"])
                predecessor = self.span(start - 8, start)
                successor = self.span(end, end + 8)
                self.assertEqual(predecessor.hex(), details["predecessor"])
                self.assertEqual(
                    sha256(predecessor),
                    details["predecessor_sha256"],
                )
                self.assertEqual(successor.hex(), details["successor"])
                self.assertEqual(
                    sha256(successor),
                    details["successor_sha256"],
                )
                closure.extend(body)
        self.assertEqual(len(closure), STOCK_CLOSURE_SIZE)
        self.assertEqual(sha256(bytes(closure)), STOCK_CLOSURE_SHA256)

    def test_all_wide_callers_and_negative_reference_topology_are_exact(
        self,
    ) -> None:
        entries = {
            int(details["start"]): name
            for name, details in FUNCTIONS.items()
        }
        observed = {name: [] for name in FUNCTIONS}
        wide_jumps = []
        external_interiors = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            encoded = self.application[offset:offset + 4]
            for link in (True, False):
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=link,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target in entries:
                    if link:
                        observed[entries[target]].append(
                            (address, encoded.hex())
                        )
                    else:
                        wide_jumps.append(
                            (address, target, encoded.hex())
                        )
                for name, details in FUNCTIONS.items():
                    start = int(details["start"])
                    end = int(details["end"])
                    if (
                        start < target < end
                        and not start <= address < end
                    ):
                        external_interiors.append(
                            (name, address, target, link, encoded.hex())
                        )
        self.assertEqual(observed, CALLERS)
        self.assertEqual(wide_jumps, [])
        self.assertEqual(external_interiors, [])
        for name, callers in observed.items():
            with self.subTest(caller_digest=name):
                self.assertEqual(len(callers), len(CALLERS[name]))
                self.assertEqual(
                    sha256(
                        b"".join(
                            struct.pack("<I", address)
                            for address, _encoded in callers
                        )
                    ),
                    CALLER_DIGESTS[name],
                )

        narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                for name, details in FUNCTIONS.items():
                    start = int(details["start"])
                    end = int(details["end"])
                    if (
                        start <= target < end
                        and not start <= address < end
                    ):
                        narrow.append(
                            (name, address, target, halfword)
                        )
        self.assertEqual(narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1 if value & 1 else value
            for name, details in FUNCTIONS.items():
                if int(details["start"]) <= canonical < int(details["end"]):
                    stored.append(
                        (name, APPLICATION_BASE + offset, value)
                    )
        self.assertEqual(stored, [])

    def test_stock_outgoing_calls_predicate_closure_and_assertions_are_exact(
        self,
    ) -> None:
        for name, details in FUNCTIONS.items():
            start = int(details["start"])
            end = int(details["end"])
            outgoing = []
            for address in range(start, end - 3, 2):
                encoded = self.span(address, address + 4)
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if target != address:
                    outgoing.append(
                        (address, encoded.hex(), target)
                    )
            self.assertEqual(outgoing, OUTGOING_WIDE_CALLS[name])

        get_fmt = self.span(
            FUNCTIONS["get_fmt_enabled"]["start"],
            FUNCTIONS["get_fmt_enabled"]["end"],
        )
        self.assertEqual(get_fmt[0x1C:0x20].hex(), "40f2e720")
        self.assertEqual(get_fmt[0x40:0x44].hex(), "40f2e722")
        self.assertEqual(self.read_u32(0x0043_DA70), LOGGER_ADDRESS)
        self.assertEqual(self.read_u32(0x0043_DAA0), ASSERT_HOOK_ADDRESS)
        self.assertEqual(self.read_u32(0x0043_DA88), 0x006E_3098)
        self.assertEqual(self.read_u32(0x0043_DAB8), 0x0076_B634)
        self.assertEqual(self.read_u32(0x0043_DCB0), 0x0078_5DC0)
        self.assertEqual(
            self.read_c_string(0x0076_B634),
            "level <= ELOG_LVL_VERBOSE",
        )
        self.assertEqual(
            self.read_c_string(0x0078_5DC0),
            "get_fmt_enabled",
        )
        self.assertEqual(
            self.read_c_string(0x006E_3098).rsplit("\\", 1)[-1],
            "elog.c",
        )

        strcpy = self.span(
            FUNCTIONS["elog_strcpy"]["start"],
            FUNCTIONS["elog_strcpy"]["end"],
        )
        self.assertEqual(
            {
                0x1A: strcpy[0x1A:0x1C].hex(),
                0x3C: strcpy[0x3C:0x3E].hex(),
                0x54: strcpy[0x54:0x56].hex(),
                0x76: strcpy[0x76:0x78].hex(),
            },
            {
                0x1A: "2c20",
                0x3C: "2c22",
                0x54: "2d20",
                0x76: "2d22",
            },
        )
        self.assertEqual(self.read_u32(0x0044_B714), ASSERT_HOOK_ADDRESS)
        self.assertEqual(self.read_u32(0x0044_B718), 0x0078_A9AC)
        self.assertEqual(self.read_u32(0x0044_B720), 0x006D_D234)
        self.assertEqual(self.read_c_string(0x0044_B70C), "dst")
        self.assertEqual(self.read_c_string(0x0044_B710), "src")
        self.assertEqual(self.read_c_string(0x0078_A9AC), "elog_strcpy")
        self.assertEqual(
            self.read_c_string(0x006D_D234).rsplit("\\", 1)[-1],
            "elog_utils.c",
        )

    def test_authenticated_upstream_configuration_and_32_bit_abi_are_exact(
        self,
    ) -> None:
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("EasyLogger", verifier.stdout)
        self.assertEqual(
            sha256(UPSTREAM_CORE.read_bytes()),
            "d4291ab1314a34cf940c8e0d7246e055"
            "70f8d32ae0704b498cf6fbacab76acb1",
        )
        self.assertEqual(
            sha256(UPSTREAM_UTILS.read_bytes()),
            "937eaf98151cb5fa25f102621802637d7"
            "1ccadd56028098e3a45978a0707d9d0",
        )
        self.assertEqual(
            sha256(UPSTREAM_HEADER.read_bytes()),
            "2890b272a01820a6336da544c056e773"
            "5b88330cd91a5092fb83a5538de11f48",
        )
        self.assertEqual(
            sha256(UPSTREAM_CONFIG.read_bytes()),
            "bccd34ca41c36ce8201d78fd2b844b07"
            "1bad25bfbac452d02764617ca4ed3073",
        )
        core = UPSTREAM_CORE.read_text(encoding="utf-8")
        utils = UPSTREAM_UTILS.read_text(encoding="utf-8")
        header = UPSTREAM_HEADER.read_text(encoding="utf-8")
        config = UPSTREAM_CONFIG.read_text(encoding="utf-8")
        for marker in (
            "static bool get_fmt_enabled(uint8_t level, size_t set)",
            "get_fmt_used_and_enabled_u32",
            "get_fmt_used_and_enabled_ptr",
            "level <= ELOG_LVL_VERBOSE",
        ):
            self.assertIn(marker, core)
        for marker in (
            "size_t elog_strcpy(size_t cur_len, char *dst, const char *src)",
            "assert(dst);",
            "assert(src);",
        ):
            self.assertIn(marker, utils)
        self.assertIn(
            "#define ELOG_LINE_BUF_SIZE                       1024",
            config,
        )
        self.assertIn("ELOG_LVL_TOTAL_NUM", header)
        self.assertIn("size_t enabled_fmt_set[ELOG_LVL_TOTAL_NUM]", header)

        self.assertEqual(ctypes.sizeof(ctypes.c_uint32), 4)
        self.assertEqual(ctypes.sizeof(EasyLoggerTagLevel32), 0x21)
        self.assertEqual(EasyLoggerTagLevel32.level.offset, 0x00)
        self.assertEqual(EasyLoggerTagLevel32.tag.offset, 0x01)
        self.assertEqual(EasyLoggerTagLevel32.tag_use_flag.offset, 0x20)
        self.assertEqual(EasyLoggerFilter32.tag_level.offset, 0x31)
        self.assertEqual(ctypes.sizeof(EasyLoggerFilter32), 0xD6)
        self.assertEqual(EasyLogger32.enabled_format_set.offset, 0xD8)
        self.assertEqual(
            ctypes.sizeof(ctypes.c_uint32 * 6),
            24,
        )
        self.assertEqual(ctypes.sizeof(EasyLogger32), 0xF8)

    def test_shared_source_pins_main_profile_and_recovered_parameters(
        self,
    ) -> None:
        self.assertEqual(
            (SOURCE.stat().st_size, sha256(SOURCE.read_bytes())),
            (SOURCE_SIZE, SOURCE_SHA256),
        )
        self.assertEqual(
            (
                SOURCE_HEADER.stat().st_size,
                sha256(SOURCE_HEADER.read_bytes()),
            ),
            (SOURCE_HEADER_SIZE, SOURCE_HEADER_SHA256),
        )
        source = SOURCE.read_text(encoding="utf-8")
        header = SOURCE_HEADER.read_text(encoding="utf-8")
        for marker in (
            "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_SRC_LINE",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE",
            "open_cfw_easylogger_get_fmt_enabled(level, format_set)",
        ):
            self.assertIn(marker, source + header)
        for marker in (
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS "
            "0x20070BE8U",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_HOOK_ADDRESS "
            "0x2007456CU",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_OUTPUT_ADDRESS "
            "0x0043D574U",
            "#define OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_ASSERT_WAIT_ADDRESS "
            "0x0044B0AEU",
            "OPEN_CFW_EASYLOGGER_HELPERS_LEVEL_COUNT = 6",
            "OPEN_CFW_EASYLOGGER_HELPERS_LINE_BUFFER_SIZE = 1024",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_DST_LINE = 44",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_STRCPY_SRC_LINE = 45",
            "OPEN_CFW_EASYLOGGER_HELPERS_ASSERT_GET_FMT_LINE = 743",
            "sizeof(open_cfw_easylogger_helpers_u32) == 4U",
            "level\n    ) == 0x00U",
            "tag\n    ) == 0x01U",
            "tag_use_flag\n    ) == 0x20U",
        ):
            self.assertIn(marker, header)

    def test_main_target_leaf_text_symbols_and_relocations_are_exact(
        self,
    ) -> None:
        closure = bytearray()
        for function, expected in TARGETS.items():
            with self.subTest(function=function):
                profile = self.target_profiles[function]
                self.assertEqual(profile["compile"].stderr, "")
                self.assertEqual(
                    profile["elf"][:6],
                    b"\x7fELF\x01\x01",
                )
                text = profile["text"]
                self.assertEqual(len(text), expected["size"])
                self.assertEqual(text, bytes.fromhex(expected["bytes"]))
                self.assertEqual(sha256(text), expected["sha256"])
                closure.extend(text)
                section = profile["text_section"]
                self.assertEqual(int(section["alignment"]), 4)
                self.assertEqual(int(section["flags"]) & 7, 6)
                symbols_by_name = {
                    str(symbol["name"]): symbol
                    for symbol in profile["symbols"]
                }
                symbol = symbols_by_name[function]
                self.assertEqual(int(symbol["binding"]), 1)
                self.assertEqual(int(symbol["type"]), 2)
                self.assertEqual(int(symbol["size"]), expected["size"])
                self.assertEqual(
                    int(symbol["section_index"]),
                    int(section["index"]),
                )
                self.assertEqual(
                    profile["relocations"],
                    expected["relocations"],
                )
                undefined = sorted(
                    str(symbol["name"])
                    for symbol in profile["symbols"]
                    if (
                        int(symbol["section_index"]) == 0
                        and str(symbol["name"])
                    )
                )
                self.assertEqual(
                    undefined,
                    sorted(
                        {
                            relocation[2]
                            for relocation in expected["relocations"]
                        }
                    ),
                )
                self.assertFalse(
                    any(
                        str(section["name"]).startswith(".rodata")
                        and int(section["size"])
                        for section in profile["sections"]
                    )
                )

        self.assertEqual(len(closure), TARGET_CLOSURE_SIZE)
        self.assertEqual(sha256(bytes(closure)), TARGET_CLOSURE_SHA256)
        for function in (
            "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
            "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
        ):
            self.assertEqual(
                self.target_profiles[function]["relocations"],
                [
                    (
                        0x0A,
                        10,
                        "open_cfw_easylogger_get_fmt_enabled",
                    )
                ],
            )

    @_APPLE_ONLY
    def test_production_leaves_redirects_artifacts_and_accounting_are_exact(
        self,
    ) -> None:
        self.assertEqual(
            (
                len(self.production_overlay),
                sha256(self.production_overlay),
            ),
            (PRODUCTION_OVERLAY_SIZE, PRODUCTION_OVERLAY_SHA256),
        )
        self.assertEqual(
            (
                len(self.production_component),
                sha256(self.production_component),
            ),
            (PRODUCTION_COMPONENT_SIZE, PRODUCTION_COMPONENT_SHA256),
        )
        report = self.production_report
        leaves = {
            leaf["extraction"]["function"]: leaf
            for leaf in report["relocated_leaves"]
            if leaf["extraction"]["function"] in PRODUCTION_LEAVES
        }
        self.assertEqual(set(leaves), set(PRODUCTION_LEAVES))
        for function, expected in PRODUCTION_LEAVES.items():
            with self.subTest(production_leaf=function):
                leaf = leaves[function]
                placement = leaf["placement"]
                self.assertEqual(
                    {
                        key: placement[key]
                        for key in (
                            "offset",
                            "size",
                            "padding_before",
                            "runtime_address",
                        )
                    },
                    {
                        key: expected[key]
                        for key in (
                            "offset",
                            "size",
                            "padding_before",
                            "runtime_address",
                        )
                    },
                )
                extraction = leaf["extraction"]
                self.assertEqual(extraction["sha256"], expected["sha256"])
                self.assertEqual(
                    extraction["unrelocated_sha256"],
                    expected["unrelocated_sha256"],
                )
                observed_relocations = [
                    (
                        item["offset"],
                        item["runtime_address"],
                        item["symbol"],
                        item["target_address"],
                    )
                    for item in extraction["relocations"]
                ]
                self.assertEqual(
                    observed_relocations,
                    expected["relocations"],
                )
                start = int(expected["offset"])
                end = start + int(expected["size"])
                body = self.production_overlay[start:end]
                self.assertEqual(sha256(body), expected["sha256"])
                for relocation in extraction["relocations"]:
                    offset = int(relocation["offset"])
                    self.assertEqual(
                        self.apollo_overlay.decode_thumb_branch(
                            int(expected["runtime_address"]) + offset,
                            body[offset:offset + 4],
                            link=True,
                        ),
                        int(relocation["target_address"]),
                    )

        patches = {
            patch["name"]: patch
            for patch in report["overlay"]["patched_sites"]
            if patch["name"] in PRODUCTION_PATCHES
        }
        self.assertEqual(set(patches), set(PRODUCTION_PATCHES))
        for patch_name, (
            stock_name,
            target_function,
            replacement_sha256,
        ) in PRODUCTION_PATCHES.items():
            with self.subTest(production_patch=patch_name):
                patch = patches[patch_name]
                stock = FUNCTIONS[stock_name]
                replacement = bytes.fromhex(patch["replacement_hex"])
                stock_size = int(stock["end"]) - int(stock["start"])
                self.assertEqual(patch["runtime_address"], stock["start"])
                self.assertEqual(patch["expected_size"], stock_size)
                self.assertEqual(
                    patch["expected_sha256"],
                    stock["sha256"],
                )
                self.assertEqual(patch["target_function"], target_function)
                self.assertEqual(len(replacement), stock_size)
                self.assertEqual(sha256(replacement), replacement_sha256)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        int(stock["start"]),
                        replacement[:4],
                        link=False,
                    ),
                    PRODUCTION_LEAVES[target_function][
                        "runtime_address"
                    ],
                )
                self.assertEqual(
                    replacement[4:],
                    b"\x00\xbf" * ((stock_size - 4) // 2),
                )
                payload_offset = int(patch["payload_offset"])
                self.assertEqual(
                    self.production_component[
                        payload_offset:
                        payload_offset + stock_size
                    ],
                    replacement,
                )

        self.assertEqual(
            {
                key: report["component"][key]
                for key in (
                    "replaced_stock_function_bytes",
                    "generated_patch_site_bytes",
                    "generated_wrapper_bytes",
                    "source_owned_in_place_bytes",
                    "source_owned_bytes",
                    "opaque_base_bytes",
                )
            },
            {
                "replaced_stock_function_bytes": 422_658,
                "generated_patch_site_bytes": 422_476,
                "generated_wrapper_bytes": 32,
                "source_owned_in_place_bytes": 186,
                "source_owned_bytes": 382_878,
                "opaque_base_bytes": 3_098_454,
            },
        )


if __name__ == "__main__":
    unittest.main()
