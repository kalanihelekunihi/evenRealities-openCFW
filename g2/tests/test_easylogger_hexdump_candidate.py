from __future__ import annotations

import ctypes
import hashlib
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SOURCE = (
    ROOT / "components" / "shared" / "easylogger"
    / "runtime_easylogger_hexdump_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
SEAMS_SOURCE = SOURCE.with_name("runtime_easylogger_hexdump_seams.c")
SEAMS_HEADER = SEAMS_SOURCE.with_suffix(".h")
CANDIDATE_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_hexdump_candidate_host.c"
)
UPSTREAM_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_hexdump_upstream_oracle_host.c"
)
SEAMS_FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_hexdump_seams_host.c"
)
UPSTREAM_SOURCE = ROOT / "third_party" / "easylogger" / "src" / "elog.c"
UPSTREAM_HEADER = ROOT / "third_party" / "easylogger" / "inc" / "elog.h"
UPSTREAM_CONFIG = (
    ROOT / "third_party" / "easylogger" / "inc" / "elog_cfg.h"
)
UPSTREAM_VERIFIER = ROOT / "third_party" / "easylogger" / "verify_snapshot.py"
AUDIT = (
    ROOT / "docs" / "research"
    / "easylogger-hexdump-source-candidate-audit.md"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
CORE_SOURCE_MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740f"
    "d3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
START = 0x0043_DACC
END = 0x0043_DC88
STOCK_SIZE = 444
STOCK_SHA256 = (
    "782cb65686dde396075abdd4f7c6a168"
    "bbf64962498d97446ab35e0e1670536c"
)
STOCK_FIRST = "2de9f04f85b004000f00984600201500"
STOCK_LAST = "1bf1010bd0e7fff7dbfb05b0bde8f08f"

DIRECT_CALLS = (
    (0x0043_DAE4, 0x0043_C0E4),
    (0x0043_DB02, 0x0044_B63A),
    (0x0043_DB0C, 0x0043_D416),
    (0x0043_DB30, 0x0044_B668),
    (0x0043_DB3C, 0x0044_AA76),
    (0x0043_DB72, 0x0044_B728),
    (0x0043_DB92, 0x0044_B5A0),
    (0x0043_DBB8, 0x0044_B728),
    (0x0043_DBCA, 0x0044_B668),
    (0x0043_DBEA, 0x0044_B668),
    (0x0043_DC10, 0x0044_B668),
    (0x0043_DC60, 0x0044_B728),
    (0x0043_DC72, 0x0044_B668),
    (0x0043_DC7E, 0x0043_D438),
)
CALLERS = (
    0x0047_22BA, 0x0047_88B2, 0x0047_8DDC, 0x0047_8DEC,
    0x0047_8E3E, 0x0047_8F44, 0x0047_981E, 0x0047_B998,
    0x0047_B9A8, 0x0047_BA50, 0x0047_BA5E, 0x0047_BB0C,
    0x0047_BB1C, 0x0048_EF8C, 0x0049_FDFC, 0x004A_1334,
    0x004A_2428, 0x004B_BEAE, 0x004B_C89C, 0x004B_CCAC,
    0x004B_E2C4, 0x004B_E7E2, 0x004C_4890, 0x0053_23E2,
    0x0053_26B0, 0x0053_86DE, 0x0057_AF7C, 0x0057_C0CA,
    0x0057_C156, 0x0057_C508, 0x0058_8626, 0x0058_885A,
    0x0058_8948, 0x0058_8A36, 0x0058_8B20, 0x0058_8BF6,
    0x0058_8CD2, 0x0059_F5AE, 0x0059_F940, 0x005B_1BBE,
    0x005B_210E,
)
CALLER_SHA256 = (
    "eddd8dc16569623d78608b9f6b476c2"
    "279e51243d822f4732eed39d56a8c1ad3"
)
CALLER_WIDTH_RECORDS = (
    (0x004722BA, 0x004722B4, 16, 0x2110), (0x004788B2, 0x004788AE, 16, 0x2110),
    (0x00478DDC, 0x00478DD6, 16, 0x2110), (0x00478DEC, 0x00478DE6, 16, 0x2110),
    (0x00478E3E, 0x00478E38, 16, 0x2110), (0x00478F44, 0x00478F3E, 16, 0x2110),
    (0x0047981E, 0x0047981A, 16, 0x2110), (0x0047B998, 0x0047B992, 16, 0x2110),
    (0x0047B9A8, 0x0047B9A2, 16, 0x2110), (0x0047BA50, 0x0047BA4A, 16, 0x2110),
    (0x0047BA5E, 0x0047BA58, 16, 0x2110), (0x0047BB0C, 0x0047BB06, 16, 0x2110),
    (0x0047BB1C, 0x0047BB16, 16, 0x2110), (0x0048EF8C, 0x0048EF88, 16, 0x2110),
    (0x0049FDFC, 0x0049FDF6, 16, 0x2110), (0x004A1334, 0x004A132E, 16, 0x2110),
    (0x004A2428, 0x004A2422, 16, 0x2110), (0x004BBEAE, 0x004BBEA8, 16, 0x2110),
    (0x004BC89C, 0x004BC896, 16, 0x2110), (0x004BCCAC, 0x004BCCA6, 16, 0x2110),
    (0x004BE2C4, 0x004BE2C0, 16, 0x2110), (0x004BE7E2, 0x004BE7DE, 8, 0x2108),
    (0x004C4890, 0x004C488A, 16, 0x2110), (0x005323E2, 0x005323DC, 16, 0x2110),
    (0x005326B0, 0x005326AA, 16, 0x2110), (0x005386DE, 0x005386D8, 16, 0x2110),
    (0x0057AF7C, 0x0057AF76, 8, 0x2108), (0x0057C0CA, 0x0057C0C4, 16, 0x2110),
    (0x0057C156, 0x0057C150, 16, 0x2110), (0x0057C508, 0x0057C502, 16, 0x2110),
    (0x00588626, 0x00588620, 16, 0x2110), (0x0058885A, 0x00588854, 16, 0x2110),
    (0x00588948, 0x00588942, 16, 0x2110), (0x00588A36, 0x00588A30, 16, 0x2110),
    (0x00588B20, 0x00588B1C, 16, 0x2110), (0x00588BF6, 0x00588BF2, 16, 0x2110),
    (0x00588CD2, 0x00588CCE, 16, 0x2110), (0x0059F5AE, 0x0059F5A8, 16, 0x2110),
    (0x0059F940, 0x0059F93C, 16, 0x2110), (0x005B1BBE, 0x005B1BB8, 16, 0x2110),
    (0x005B210E, 0x005B210A, 16, 0x2110),
)
CALLER_WIDTH_SHA256 = (
    "05d0d859ae08fa8b0f9b41a20335d62"
    "930e913432acd02e3f0d8e36ee5576908"
)
CURRENT_RETAINED_CALLERS = (
    0x0048EF8C, 0x0049FDFC, 0x004A1334,
    0x004A2428, 0x005386DE, 0x0057AF7C,
)
CURRENT_RETAINED_CALLER_WIDTH_SHA256 = (
    "777f2eb894b61d9ac4a7176ba9845d55"
    "2e4f270dc1c1fc79416720b636438863"
)

UPSTREAM_PINS = {
    UPSTREAM_SOURCE: (
        28_740,
        "d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1",
    ),
    UPSTREAM_HEADER: (
        10_428,
        "2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48",
    ),
    UPSTREAM_CONFIG: (
        3_995,
        "bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073",
    ),
}

# Updated deliberately when a reviewed nonproduction artifact changes. None
# of these pins register the files as production firmware inputs.
LOCAL_PINS = {
    SOURCE: (
        6_570,
        "f96e23938e1973c443c378f83761497c0bc8658538fedf3db1bf091f06d5a942",
    ),
    HEADER: (
        5_188,
        "355cf432ed8e8b7cab866cf9a925a20033fce59db444962bd85c01ad9bdf47cf",
    ),
    SEAMS_SOURCE: (
        8_795,
        "f9fe880e4d1f09b1120dbdd751680fd378818a779abd999d07ba26888fc1259b",
    ),
    SEAMS_HEADER: (
        1_809,
        "c788ff6f9dc2071ae648acb5da6d58f65af6989894fa5797bd93bb7853462599",
    ),
    CANDIDATE_FIXTURE: (
        17_574,
        "8446553aacac21213f01f681bfccd9a0f213e8bd724531ae8df6e06f8ca91d18",
    ),
    UPSTREAM_FIXTURE: (
        14_296,
        "f6614ba626a763f0464490312dc560dbddf5269c2a7b8a054a6a247d646ff27d",
    ),
    SEAMS_FIXTURE: (
        7_327,
        "a31ca118032e952f4b30b75c4a5b8808d84f9efc6bbd10afb9a392b83ac52dbf",
    ),
    AUDIT: (
        20_266,
        "dce76c6e86350dccdbf3111f3ccfdc8e6abf2ce5f1b00313e9f9dff2d005b552",
    ),
}

FUNCTION = "open_cfw_easylogger_hexdump_candidate"
FUNCTION_SECTION = ".text." + FUNCTION
RODATA_SECTION = ".rodata.str1.1"
EXIDX_SECTION = ".ARM.exidx" + FUNCTION_SECTION
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
APPLE_TARGET_PIN = {
    "version": "Apple clang version 21.0.0 (clang-2100.3.27.1)",
    "object_size": 2_384,
    "object_sha256": (
        "1daa36a1c4a3ee011cff337c74bfad06"
        "f7eb3bc36a9b75f2d67881ff9f6bb547"
    ),
    "runtime_address": 0x007C_0858,
    "text_size": 514,
    "text_alignment": 4,
    "text_sha256": (
        "b590d72a5cea9fefcbab0a1b224ca032"
        "db38c853698ced7f2ee210b107a1cb87"
    ),
    "rodata_size": 7,
    "rodata_alignment": 1,
    "rodata_sha256": (
        "9f702654a35832eb92db88b74ff52483"
        "e0afacca06a1e79c14f86041105b762e"
    ),
    "closure_size": 521,
    "closure_sha256": (
        "5e2c10b84757c891bca3dd226a2849bd"
        "1034db09f09d1ad87a7ae33334d142b9"
    ),
    "relocation_sha256": (
        "50981cb8bf7cd917a905e69843e6947b"
        "f193f4cf6e5a5b19b8e9b70a7c7e54ee"
    ),
    "outgoing_sha256": (
        "51877376e43a256b7809c962d98cd9e1"
        "92cd3c953e099100757415a648253f7d"
    ),
    "relocated_text_sha256": (
        "5ac66301964ac295e8d2f8a15466c33e"
        "b5bf8cb48d6e1a7e12c6cad337f3e69a"
    ),
    "relocated_closure_sha256": (
        "c14b607ec21fd8ba87cc62cf666a87d5"
        "9bd589d899047892a4d0fe1caebc441f"
    ),
    "exidx_sha256": (
        "01acecb507abfe1a354aa8064f4af5d3"
        "f1acd019e37db3c11c97523b71c76e9d"
    ),
}
DOCKER = os.environ.get("OPENCFW_DOCKER", "docker")
LINUX_IMAGE = "opencfw-linux-llvm:22.1.8"
LINUX_IMAGE_ID = (
    "sha256:92ccf0cddac1680db0d9912cf681735b"
    "39e729d21e052965e177fa3c97faef26"
)
LINUX_CLANG = "/home/linuxbrew/.linuxbrew/bin/clang"
LINUX_OBJCOPY = "/home/linuxbrew/.linuxbrew/bin/llvm-objcopy"
LINUX_CLANG_VERSION = "Homebrew clang version 22.1.8"
LINUX_TARGET_PIN = {
    "object_size": 2_352,
    "object_sha256": (
        "4b1090c536705d393522b917b6cc1802"
        "a042670f9efb447b6cd43651ed9eb740"
    ),
    "runtime_address": 0x007B_25CC,
    "text_size": 500,
    "text_alignment": 4,
    "text_sha256": (
        "23b05264d4c99fa4e79ee0b5f422def9"
        "156cee4d53d88a96adb84c2db83aa051"
    ),
    "rodata_size": 7,
    "rodata_alignment": 1,
    "rodata_sha256": (
        "9f702654a35832eb92db88b74ff52483"
        "e0afacca06a1e79c14f86041105b762e"
    ),
    "closure_size": 507,
    "closure_sha256": (
        "c0d7f4bc418cfc9a7d7a79f9e994d746"
        "c5817a70aa46855769da3f226857c420"
    ),
    "relocation_sha256": (
        "2c3dcc618a62ccc03ec0cd3d01e974a9"
        "476059bf5395d8dec02f107e122c6201"
    ),
    "outgoing_sha256": (
        "7cfb64b8d88e6839a18275b93ce14cd7"
        "37f101dcd6bc9e02a5c382d5d84c38f2"
    ),
    "relocated_text_sha256": (
        "ac660718be5b3711001a7a82b226f59e"
        "9ba83f26c59e5fc72a4db75465d3eebf"
    ),
    "relocated_closure_sha256": (
        "4471c11778e3ec2457766ce9d093a847"
        "3dc06ce4fd6abbe78b144a9761c4b96f"
    ),
    "exidx_sha256": (
        "01acecb507abfe1a354aa8064f4af5d3"
        "f1acd019e37db3c11c97523b71c76e9d"
    ),
}
RODATA_HEX = (
    "20002020000a00"
)
UNDEFINED_SYMBOLS = [
    "open_cfw_easylogger_helpers_get_logger",
    "open_cfw_easylogger_hexdump_blank_hex_source",
    "open_cfw_easylogger_hexdump_fill_source",
    "open_cfw_easylogger_hexdump_format_character_source",
    "open_cfw_easylogger_hexdump_format_header_source",
    "open_cfw_easylogger_hexdump_format_hex_source",
    "open_cfw_easylogger_hexdump_raw_submit_source",
    "open_cfw_easylogger_output_lock",
    "open_cfw_easylogger_output_unlock",
    "open_cfw_easylogger_strcpy",
]
RODATA_SYMBOLS = (
    (".L.str", 0, 2),
    (".L.str.1", 2, 3),
    (".L.str.2", 5, 2),
)
SOURCE_OWNED_TARGETS = {
    "apple-clang": {
        "open_cfw_easylogger_helpers_get_logger": 0x007B_EDD4,
        "open_cfw_easylogger_output_lock": 0x007A_E6C4,
        "open_cfw_easylogger_output_unlock": 0x007A_E6E8,
        "open_cfw_easylogger_strcpy": 0x007B_EEE0,
        "open_cfw_easylogger_hexdump_fill_source": 0x007B_209C,
        "open_cfw_easylogger_hexdump_format_header_source": 0x007B_20F0,
        "open_cfw_easylogger_hexdump_format_hex_source": 0x007B_22EC,
        "open_cfw_easylogger_hexdump_blank_hex_source": 0x007B_2318,
        "open_cfw_easylogger_hexdump_format_character_source": 0x007B_2310,
        "open_cfw_easylogger_hexdump_raw_submit_source": 0x007B_2438,
    },
    "linux-clang": {
        "open_cfw_easylogger_helpers_get_logger": 0x007B_0A50,
        "open_cfw_easylogger_output_lock": 0x007A_E8EC,
        "open_cfw_easylogger_output_unlock": 0x007A_E910,
        "open_cfw_easylogger_strcpy": 0x007B_0B5C,
        "open_cfw_easylogger_hexdump_fill_source": 0x007B_27C8,
        "open_cfw_easylogger_hexdump_format_header_source": 0x007B_281C,
        "open_cfw_easylogger_hexdump_format_hex_source": 0x007B_2A14,
        "open_cfw_easylogger_hexdump_blank_hex_source": 0x007B_2A40,
        "open_cfw_easylogger_hexdump_format_character_source": 0x007B_2A38,
        "open_cfw_easylogger_hexdump_raw_submit_source": 0x007B_2B58,
    },
}
APPLE_RELOCATION_PINS = (
    (20, 10, "open_cfw_easylogger_hexdump_fill_source"),
    (24, 10, "open_cfw_easylogger_helpers_get_logger"),
    (134, 10, "open_cfw_easylogger_output_lock"),
    (168, 49, ".L.str.1"), (172, 50, ".L.str.1"),
    (186, 10, "open_cfw_easylogger_strcpy"),
    (218, 49, ".L.str.2"), (222, 50, ".L.str.2"),
    (234, 10, "open_cfw_easylogger_strcpy"),
    (244, 10, "open_cfw_easylogger_hexdump_raw_submit_source"),
    (292, 10, "open_cfw_easylogger_hexdump_format_header_source"),
    (350, 10, "open_cfw_easylogger_hexdump_format_hex_source"),
    (358, 10, "open_cfw_easylogger_hexdump_blank_hex_source"),
    (372, 10, "open_cfw_easylogger_strcpy"),
    (386, 49, ".L.str"), (390, 50, ".L.str"),
    (404, 10, "open_cfw_easylogger_strcpy"),
    (412, 49, ".L.str.1"), (416, 50, ".L.str.1"),
    (430, 10, "open_cfw_easylogger_strcpy"),
    (484, 10, "open_cfw_easylogger_hexdump_format_character_source"),
    (496, 10, "open_cfw_easylogger_strcpy"),
    (504, 10, "open_cfw_easylogger_output_unlock"),
)
LINUX_RELOCATION_PINS = (
    (20, 10, "open_cfw_easylogger_hexdump_fill_source"),
    (24, 10, "open_cfw_easylogger_helpers_get_logger"),
    (140, 10, "open_cfw_easylogger_output_lock"),
    (168, 49, ".L.str.1"), (172, 50, ".L.str.1"),
    (186, 10, "open_cfw_easylogger_strcpy"),
    (212, 49, ".L.str.2"), (216, 50, ".L.str.2"),
    (228, 10, "open_cfw_easylogger_strcpy"),
    (238, 10, "open_cfw_easylogger_hexdump_raw_submit_source"),
    (288, 10, "open_cfw_easylogger_hexdump_format_header_source"),
    (342, 10, "open_cfw_easylogger_hexdump_format_hex_source"),
    (350, 10, "open_cfw_easylogger_hexdump_blank_hex_source"),
    (364, 10, "open_cfw_easylogger_strcpy"),
    (378, 49, ".L.str"), (382, 50, ".L.str"),
    (396, 10, "open_cfw_easylogger_strcpy"),
    (404, 49, ".L.str.1"), (408, 50, ".L.str.1"),
    (422, 10, "open_cfw_easylogger_strcpy"),
    (470, 10, "open_cfw_easylogger_hexdump_format_character_source"),
    (482, 10, "open_cfw_easylogger_strcpy"),
    (490, 10, "open_cfw_easylogger_output_unlock"),
)

SEAM_UNDEFINED_SYMBOLS = [
    "open_cfw_retained_easylogger_async_default_metadata",
    "open_cfw_retained_easylogger_async_diagnostic",
    "open_cfw_retained_easylogger_async_ready",
    "open_cfw_retained_easylogger_async_record_allocate",
    "open_cfw_retained_easylogger_async_record_enqueue",
]
SEAM_TARGET_PINS = {
    "apple-clang": {
        "object_size": 5_072,
        "object_sha256": (
            "60f1fd2587e56234f3959cb437648b466"
            "3697c98b34ad57a49bb5e65e10d1307"
        ),
        "relocation_count": 38,
        "relocation_sha256": (
            "6a8995317560819dcee7c1ca8d824fd7"
            "6762d383a70b6f327a31e233f8922ba9"
        ),
        "text": {
            "open_cfw_easylogger_hexdump_fill_source": (
                84, "2edbfc9684d37aa09a6a4562c86ba1bb0cfe52353b2bc367361fc939e401d22f"
            ),
            "open_cfw_easylogger_hexdump_format_header_source": (
                232, "7957f7db68162d1a3ff382233eb4ae34a00977a6722cccc69db9b5e28397f1e0"
            ),
            "open_cfw_easylogger_hexdump_put": (
                22, "e876cbf50a078b0f76d076fffd59db69efbd644171a5c80dd8efb0d43d6b1f51"
            ),
            "open_cfw_easylogger_hexdump_put_hex": (
                234, "774ac4799fffa3745c8a82ed9fb3070875ec9908937b5e0b4530428ff53c0fa6"
            ),
            "open_cfw_easylogger_hexdump_format_hex_source": (
                34, "fee72226cf8028522f2cefa6326dbeaa05c4dc3ce6d6e6a9c7c8eda8d8044e6a"
            ),
            "open_cfw_easylogger_hexdump_format_character_source": (
                8, "d07f579a51895739fb8889eb2fffeba280b4b891e1a031033380fbda2cbfa004"
            ),
            "open_cfw_easylogger_hexdump_blank_hex_source": (
                22, "8f288a9efc5ff1c0da079cf6c5febaf304bcdb4267b9e6881d86b1c6669340fe"
            ),
            "open_cfw_g2_easylogger_async_record_build_level_less": (
                208, "1b33d6136679a37af3e2679b0aeb990346a8afdd48a8eae8465c7e8f0b3326e0"
            ),
            "open_cfw_easylogger_hexdump_raw_submit_source": (
                6, "e1306533deb7c78f8b3431ad297def9b17e14d91a575d167181bd7e0c1a1c546"
            ),
        },
    },
    "linux-clang": {
        "object_size": 5_048,
        "object_sha256": (
            "3448cae3bf4e0398a5560f72a279fc02"
            "5e9b417898196c343eb102a262a6669a"
        ),
        "relocation_count": 38,
        "relocation_sha256": (
            "c9a328e66ba2407ee7a98b1e3ccc8427"
            "5a0c298d3fe4da959404ea56c8707c8c"
        ),
        "text": {
            "open_cfw_easylogger_hexdump_fill_source": (
                84, "b9006beb3861f5cc5f0d53cca57a36ed1b309764626eb4e8e5f5f3b65b69893a"
            ),
            "open_cfw_easylogger_hexdump_format_header_source": (
                232, "7957f7db68162d1a3ff382233eb4ae34a00977a6722cccc69db9b5e28397f1e0"
            ),
            "open_cfw_easylogger_hexdump_put": (
                22, "e876cbf50a078b0f76d076fffd59db69efbd644171a5c80dd8efb0d43d6b1f51"
            ),
            "open_cfw_easylogger_hexdump_put_hex": (
                230, "828cfbaba88f0903e845ea95d60380925a7897379d618c5d862e595f1c07cb0c"
            ),
            "open_cfw_easylogger_hexdump_format_hex_source": (
                34, "fee72226cf8028522f2cefa6326dbeaa05c4dc3ce6d6e6a9c7c8eda8d8044e6a"
            ),
            "open_cfw_easylogger_hexdump_format_character_source": (
                8, "d07f579a51895739fb8889eb2fffeba280b4b891e1a031033380fbda2cbfa004"
            ),
            "open_cfw_easylogger_hexdump_blank_hex_source": (
                22, "8f288a9efc5ff1c0da079cf6c5febaf304bcdb4267b9e6881d86b1c6669340fe"
            ),
            "open_cfw_g2_easylogger_async_record_build_level_less": (
                202, "cd81c6d60ea24742a32f91a6fb2d4415b7f53674ea63318e7787ba8bbbfddd3c"
            ),
            "open_cfw_easylogger_hexdump_raw_submit_source": (
                6, "e1306533deb7c78f8b3431ad297def9b17e14d91a575d167181bd7e0c1a1c546"
            ),
        },
    },
}

SEAM_FUNCTIONS = tuple(SEAM_TARGET_PINS["apple-clang"]["text"])
SEAM_COMMON_RELOCATIONS = {
    "open_cfw_easylogger_hexdump_fill_source": (),
    "open_cfw_easylogger_hexdump_format_header_source": (
        (30, 10, "open_cfw_easylogger_hexdump_put"),
        (42, 10, "open_cfw_easylogger_hexdump_put"),
        (54, 10, "open_cfw_easylogger_hexdump_put"),
        (66, 10, "open_cfw_easylogger_hexdump_put"),
        (78, 10, "open_cfw_easylogger_hexdump_put"),
        (90, 10, "open_cfw_easylogger_hexdump_put"),
        (112, 10, "open_cfw_easylogger_hexdump_put"),
        (134, 10, "open_cfw_easylogger_hexdump_put"),
        (146, 10, "open_cfw_easylogger_hexdump_put"),
        (158, 10, "open_cfw_easylogger_hexdump_put_hex"),
        (170, 10, "open_cfw_easylogger_hexdump_put"),
        (182, 10, "open_cfw_easylogger_hexdump_put_hex"),
        (194, 10, "open_cfw_easylogger_hexdump_put"),
        (206, 10, "open_cfw_easylogger_hexdump_put"),
    ),
    "open_cfw_easylogger_hexdump_put": (),
    "open_cfw_easylogger_hexdump_format_hex_source": (
        (0, 49, "open_cfw_easylogger_hexdump_put_hex.digits"),
        (4, 50, "open_cfw_easylogger_hexdump_put_hex.digits"),
    ),
    "open_cfw_easylogger_hexdump_format_character_source": (),
    "open_cfw_easylogger_hexdump_blank_hex_source": (),
    "open_cfw_easylogger_hexdump_raw_submit_source": (
        (2, 30, "open_cfw_g2_easylogger_async_record_build_level_less"),
    ),
}
SEAM_PROFILE_RELOCATIONS = {
    "apple-clang": {
        "open_cfw_easylogger_hexdump_put_hex": (
            (8, 49, "open_cfw_easylogger_hexdump_put_hex.digits"),
            (12, 50, "open_cfw_easylogger_hexdump_put_hex.digits"),
            (196, 10, "open_cfw_easylogger_hexdump_put"),
        ),
        "open_cfw_g2_easylogger_async_record_build_level_less": (
            (8, 47, "open_cfw_retained_easylogger_async_ready"),
            (12, 48, "open_cfw_retained_easylogger_async_ready"),
            (38, 47, "open_cfw_retained_easylogger_async_default_metadata"),
            (42, 48, "open_cfw_retained_easylogger_async_default_metadata"),
            (56, 10, "open_cfw_retained_easylogger_async_record_allocate"),
            (180, 10, "open_cfw_retained_easylogger_async_record_enqueue"),
            (186, 49, "open_cfw_easylogger_hexdump_enqueue_error"),
            (190, 50, "open_cfw_easylogger_hexdump_enqueue_error"),
            (196, 10, "open_cfw_retained_easylogger_async_diagnostic"),
        ),
    },
    "linux-clang": {
        "open_cfw_easylogger_hexdump_put_hex": (
            (6, 49, "open_cfw_easylogger_hexdump_put_hex.digits"),
            (10, 50, "open_cfw_easylogger_hexdump_put_hex.digits"),
            (194, 10, "open_cfw_easylogger_hexdump_put"),
        ),
        "open_cfw_g2_easylogger_async_record_build_level_less": (
            (8, 47, "open_cfw_retained_easylogger_async_ready"),
            (12, 48, "open_cfw_retained_easylogger_async_ready"),
            (38, 47, "open_cfw_retained_easylogger_async_default_metadata"),
            (42, 48, "open_cfw_retained_easylogger_async_default_metadata"),
            (56, 10, "open_cfw_retained_easylogger_async_record_allocate"),
            (174, 10, "open_cfw_retained_easylogger_async_record_enqueue"),
            (180, 49, "open_cfw_easylogger_hexdump_enqueue_error"),
            (184, 50, "open_cfw_easylogger_hexdump_enqueue_error"),
            (190, 10, "open_cfw_retained_easylogger_async_diagnostic"),
        ),
    },
}
SEAM_RETAINED_TARGETS = {
    "open_cfw_retained_easylogger_async_ready": 0x2007_4FC0,
    "open_cfw_retained_easylogger_async_default_metadata": 0x2000_4546,
    "open_cfw_retained_easylogger_async_record_allocate": 0x0044_8A0C,
    "open_cfw_retained_easylogger_async_record_enqueue": 0x0044_8AF0,
    "open_cfw_retained_easylogger_async_diagnostic": 0x0047_33EE,
}
SEAM_RODATA_PINS = {
    "digits": {
        "section": ".rodata.str1.1",
        "size": 17,
        "alignment": 1,
        "sha256": "15035c2b8a71a2cf05f146d7e149a0d0399298833e1394702fbaf2aaa822c08e",
        "symbol": ("open_cfw_easylogger_hexdump_put_hex.digits", 0, 17, 1, 0, 0),
    },
    "enqueue_error": {
        "section": ".rodata.open_cfw_easylogger_hexdump_enqueue_error",
        "size": 54,
        "alignment": 1,
        "sha256": "2a8285b704dd7e2cc111a09f750d509f79794fca0aba7ec1513414df4fd9bad3",
        "symbol": ("open_cfw_easylogger_hexdump_enqueue_error", 0, 54, 1, 0, 0),
    },
}
SEAM_LAYOUT_PINS = {
    "apple-clang": {
        "production_tail": 0x007B_1E8E,
        "candidate_start": 0x007C_0858,
        "end": 0x007B_243E,
        "growth": 1_456,
        "runtime": {
            "open_cfw_easylogger_hexdump_fill_source": 0x007B_209C,
            "open_cfw_easylogger_hexdump_format_header_source": 0x007B_20F0,
            "open_cfw_easylogger_hexdump_put": 0x007B_21D8,
            "open_cfw_easylogger_hexdump_put_hex": 0x007B_21F0,
            "open_cfw_easylogger_hexdump_format_hex_source": 0x007B_22EC,
            "open_cfw_easylogger_hexdump_format_character_source": 0x007B_2310,
            "open_cfw_easylogger_hexdump_blank_hex_source": 0x007B_2318,
            "open_cfw_g2_easylogger_async_record_build_level_less": 0x007B_2330,
            "open_cfw_easylogger_hexdump_raw_submit_source": 0x007B_2438,
        },
        "rodata_runtime": {"digits": 0x007B_22DA, "enqueue_error": 0x007B_2400},
        "relocated": {
            "open_cfw_easylogger_hexdump_fill_source": (84, "2edbfc9684d37aa09a6a4562c86ba1bb0cfe52353b2bc367361fc939e401d22f"),
            "open_cfw_easylogger_hexdump_format_header_source": (232, "45a8c7846180661b410151f9cbaffee30b79f16d0ca41154f12def5e28815449"),
            "open_cfw_easylogger_hexdump_put": (22, "e876cbf50a078b0f76d076fffd59db69efbd644171a5c80dd8efb0d43d6b1f51"),
            "open_cfw_easylogger_hexdump_put_hex": (251, "be190f65f1ccb7c4c3227ad8d8b2f1d2cb624f0f5b6bd9dfa990889e99d4f8a0"),
            "open_cfw_easylogger_hexdump_format_hex_source": (34, "838d2100c9ad5f6f1cb3395f35e835ecc726ff2004df2a2d3d1e3b8dbc1511ea"),
            "open_cfw_easylogger_hexdump_format_character_source": (8, "d07f579a51895739fb8889eb2fffeba280b4b891e1a031033380fbda2cbfa004"),
            "open_cfw_easylogger_hexdump_blank_hex_source": (22, "8f288a9efc5ff1c0da079cf6c5febaf304bcdb4267b9e6881d86b1c6669340fe"),
            "open_cfw_g2_easylogger_async_record_build_level_less": (262, "5f81838fc52b3cb040e303ff635a60e2e1f470e21d2c0dd17fdf97b8a8f9c8e1"),
            "open_cfw_easylogger_hexdump_raw_submit_source": (6, "ceaa776ec84e3540b8fabd626d0ce6fab7fa3aba68e3fcd2465710a1f0705cb6"),
        },
    },
    "linux-clang": {
        "production_tail": 0x007B_25CA,
        "candidate_start": 0x007B_25CC,
        "end": 0x007B_2B5E,
        "growth": 1_428,
        "runtime": {
            "open_cfw_easylogger_hexdump_fill_source": 0x007B_27C8,
            "open_cfw_easylogger_hexdump_format_header_source": 0x007B_281C,
            "open_cfw_easylogger_hexdump_put": 0x007B_2904,
            "open_cfw_easylogger_hexdump_put_hex": 0x007B_291C,
            "open_cfw_easylogger_hexdump_format_hex_source": 0x007B_2A14,
            "open_cfw_easylogger_hexdump_format_character_source": 0x007B_2A38,
            "open_cfw_easylogger_hexdump_blank_hex_source": 0x007B_2A40,
            "open_cfw_g2_easylogger_async_record_build_level_less": 0x007B_2A58,
            "open_cfw_easylogger_hexdump_raw_submit_source": 0x007B_2B58,
        },
        "rodata_runtime": {"digits": 0x007B_2A02, "enqueue_error": 0x007B_2B22},
        "relocated": {
            "open_cfw_easylogger_hexdump_fill_source": (84, "b9006beb3861f5cc5f0d53cca57a36ed1b309764626eb4e8e5f5f3b65b69893a"),
            "open_cfw_easylogger_hexdump_format_header_source": (232, "45a8c7846180661b410151f9cbaffee30b79f16d0ca41154f12def5e28815449"),
            "open_cfw_easylogger_hexdump_put": (22, "e876cbf50a078b0f76d076fffd59db69efbd644171a5c80dd8efb0d43d6b1f51"),
            "open_cfw_easylogger_hexdump_put_hex": (247, "d1adddb24678f93907f04b39379e2e8e60abd41b3182dccfd268f1c79e884252"),
            "open_cfw_easylogger_hexdump_format_hex_source": (34, "838d2100c9ad5f6f1cb3395f35e835ecc726ff2004df2a2d3d1e3b8dbc1511ea"),
            "open_cfw_easylogger_hexdump_format_character_source": (8, "d07f579a51895739fb8889eb2fffeba280b4b891e1a031033380fbda2cbfa004"),
            "open_cfw_easylogger_hexdump_blank_hex_source": (22, "8f288a9efc5ff1c0da079cf6c5febaf304bcdb4267b9e6881d86b1c6669340fe"),
            "open_cfw_g2_easylogger_async_record_build_level_less": (256, "9782fd47c8147ed31323771afc08e9206e2f7f5af4c5a83c598aec0b28629227"),
            "open_cfw_easylogger_hexdump_raw_submit_source": (6, "d11d808c4b1c4c17e7060f9d2ecbbddc3004e11829ce75359ad5d3a2a2899890"),
        },
    },
}

EVENT_FILL = 1
EVENT_STATE = 2
EVENT_LOCK = 3
EVENT_BUFFER = 4
EVENT_HEADER = 5
EVENT_HEX = 6
EVENT_STRNCPY = 7
EVENT_APPEND = 8
EVENT_CHARACTER = 9
EVENT_SINK = 10
EVENT_UNLOCK = 11


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def compiler_version(path: str | Path) -> str | None:
    try:
        result = subprocess.run(
            [str(path), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return result.stdout.splitlines()[0]


def align_up(value: int, alignment: int) -> int:
    if alignment <= 0 or alignment & (alignment - 1):
        raise ValueError("alignment must be a positive power of two")
    return (value + alignment - 1) & ~(alignment - 1)


def encode_prel31(target: int, place: int) -> int:
    displacement = target - place
    if displacement < -(1 << 30) or displacement >= (1 << 30):
        raise ValueError("R_ARM_PREL31 displacement is out of range")
    return displacement & 0x7FFF_FFFF


def decode_prel31(word: int, place: int) -> int:
    displacement = word & 0x7FFF_FFFF
    if displacement & 0x4000_0000:
        displacement -= 0x8000_0000
    return place + displacement


def sign16(value: int) -> int:
    return value - 0x1_0000 if value & 0x8000 else value


def thumb_movwt_immediate(first: int, second: int) -> int:
    return (
        ((first & 0x000F) << 12)
        | (((first >> 10) & 1) << 11)
        | (((second >> 12) & 7) << 8)
        | (second & 0x00FF)
    )


def thumb_movwt_with_immediate(
    first: int,
    second: int,
    value: int,
) -> tuple[int, int]:
    value &= 0xFFFF
    first = (
        (first & ~((1 << 10) | 0x000F))
        | (((value >> 11) & 1) << 10)
        | ((value >> 12) & 0x000F)
    )
    second = (
        (second & ~((7 << 12) | 0x00FF))
        | (((value >> 8) & 7) << 12)
        | (value & 0x00FF)
    )
    return first, second


def encode_thumb_bl(address: int, target: int) -> bytes:
    displacement = target - (address + 4)
    if displacement & 1 or not -(1 << 24) <= displacement < (1 << 24):
        raise ValueError("Thumb BL target is invalid")
    immediate = displacement & 0x01FF_FFFF
    sign = (immediate >> 24) & 1
    i1 = (immediate >> 23) & 1
    i2 = (immediate >> 22) & 1
    j1 = 1 ^ (i1 ^ sign)
    j2 = 1 ^ (i2 ^ sign)
    first = 0xF000 | (sign << 10) | ((immediate >> 12) & 0x03FF)
    second = 0xD000 | (j1 << 13) | (j2 << 11) | (
        (immediate >> 1) & 0x07FF
    )
    return struct.pack("<HH", first, second)


def encode_thumb_b_w(address: int, target: int) -> bytes:
    displacement = target - (address + 4)
    if displacement & 1 or not -(1 << 24) <= displacement < (1 << 24):
        raise ValueError("Thumb B.W target is invalid")
    immediate = displacement & 0x01FF_FFFF
    sign = (immediate >> 24) & 1
    i1 = (immediate >> 23) & 1
    i2 = (immediate >> 22) & 1
    j1 = 1 ^ (i1 ^ sign)
    j2 = 1 ^ (i2 ^ sign)
    first = 0xF000 | (sign << 10) | ((immediate >> 12) & 0x03FF)
    second = 0x9000 | (j1 << 13) | (j2 << 11) | (
        (immediate >> 1) & 0x07FF
    )
    return struct.pack("<HH", first, second)


def wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


def narrow_branch_targets(address: int, halfword: int) -> tuple[int, ...]:
    if halfword & 0xF800 == 0xE000:
        immediate = halfword & 0x07FF
        if immediate & 0x0400:
            immediate -= 0x0800
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF000 == 0xD000 and ((halfword >> 8) & 0x0F) < 0x0E:
        immediate = halfword & 0x00FF
        if immediate & 0x0080:
            immediate -= 0x0100
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    if halfword & 0xF500 == 0xB100:
        immediate = (((halfword >> 9) & 1) << 5) | ((halfword >> 3) & 0x1F)
        return ((address + 4 + immediate * 2) & 0xFFFF_FFFF,)
    return ()


class HostHarness:
    PREFIX = "open_cfw_test_easylogger_hexdump_"

    def __init__(self, library: Path) -> None:
        self.loaded = ctypes.CDLL(str(library))
        self.reset = getattr(self.loaded, self.PREFIX + "reset")
        self.set_output = getattr(self.loaded, self.PREFIX + "set_output_enabled")
        self.set_level = getattr(self.loaded, self.PREFIX + "set_filter_level")
        self.set_tag = getattr(self.loaded, self.PREFIX + "set_filter_tag")
        self.force_header = getattr(self.loaded, self.PREFIX + "force_header_result")
        self.run_function = getattr(self.loaded, self.PREFIX + "run")
        self.set_output.argtypes = [ctypes.c_uint32]
        self.set_level.argtypes = [ctypes.c_uint32]
        self.set_tag.argtypes = [ctypes.c_char_p]
        self.force_header.argtypes = [ctypes.c_uint32, ctypes.c_int32]
        self.run_function.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        self.run_function.restype = ctypes.c_uint32
        self.getters = {}
        for name in (
            "event_count", "lock_depth", "fill_calls", "fill_count",
            "fill_value", "header_calls", "hex_calls", "character_calls",
            "strncpy_calls", "append_calls", "sink_calls", "last_length",
            "last_buffer_matches", "last_header_offset", "last_header_end",
        ):
            function = getattr(self.loaded, self.PREFIX + name)
            function.restype = ctypes.c_uint32
            self.getters[name] = function
        self.event_at = getattr(self.loaded, self.PREFIX + "event_at")
        self.event_at.argtypes = [ctypes.c_uint32]
        self.event_at.restype = ctypes.c_uint32
        self.line_at = getattr(self.loaded, self.PREFIX + "line_at")
        self.line_at.argtypes = [ctypes.c_uint32]
        self.line_at.restype = ctypes.c_void_p
        self.line_length_at = getattr(self.loaded, self.PREFIX + "line_length_at")
        self.line_length_at.argtypes = [ctypes.c_uint32]
        self.line_length_at.restype = ctypes.c_uint32
        self.last_line_pointer = getattr(self.loaded, self.PREFIX + "last_line")
        self.last_line_pointer.restype = ctypes.c_void_p
        self.last_name_pointer = getattr(
            self.loaded, self.PREFIX + "last_header_name"
        )
        self.last_name_pointer.restype = ctypes.c_char_p

    def get(self, name: str) -> int:
        return int(self.getters[name]())

    def events(self, maximum: int = 512) -> list[int]:
        count = min(self.get("event_count"), maximum)
        return [int(self.event_at(index)) for index in range(count)]

    def line(self, index: int) -> bytes:
        length = int(self.line_length_at(index))
        return ctypes.string_at(self.line_at(index), length)

    def last_line(self) -> bytes:
        return ctypes.string_at(self.last_line_pointer(), self.get("last_length"))

    def run(
        self,
        name: bytes,
        width: int,
        data: bytes,
        *,
        size: int | None = None,
        sink_limit: int = 0,
    ) -> int:
        storage = (ctypes.c_uint8 * max(1, len(data)))()
        if data:
            storage[:len(data)] = data
        actual_size = len(data) if size is None else size
        return int(self.run_function(name, width, storage, actual_size, sink_limit))

    def summary(self) -> tuple[object, ...]:
        calls = self.get("sink_calls")
        captured = tuple(self.line(index) for index in range(min(calls, 16)))
        return (
            calls,
            captured,
            self.last_line() if calls else b"",
            self.get("last_length"),
            self.get("last_header_offset"),
            self.get("last_header_end"),
            self.last_name_pointer() or b"",
            self.get("header_calls"),
            self.get("hex_calls"),
            self.get("character_calls"),
            self.get("strncpy_calls"),
        )


class EasyLoggerHexdumpCandidateTests(unittest.TestCase):
    @classmethod
    def run_linux_tool(
        cls,
        tool: str,
        arguments: list[str],
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                DOCKER,
                "run",
                "--platform",
                "linux/amd64",
                "--rm",
                "--network",
                "none",
                "-v",
                f"{ROOT.parent}:/workspace:ro",
                "-v",
                f"{cls.temporary_path}:/out",
                "-w",
                "/workspace",
                LINUX_IMAGE,
                tool,
                *arguments,
            ],
            check=True,
            capture_output=True,
            text=True,
        )

    @classmethod
    def setUpClass(cls) -> None:
        parent = ROOT / "build"
        parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(dir=parent)
        temporary = Path(cls.temporary.name)
        cls.temporary_path = temporary
        cls.host_clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        libraries = {}
        for name, fixture in (
            ("candidate", CANDIDATE_FIXTURE),
            ("upstream", UPSTREAM_FIXTURE),
            ("seams", SEAMS_FIXTURE),
        ):
            library = temporary / library_name("easylogger-hexdump-" + name)
            command = [
                cls.host_clang,
                "-std=c11",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
            ]
            if name == "upstream":
                command.extend([
                    "-I", str(ROOT / "third_party" / "easylogger" / "inc")
                ])
            command.append(str(fixture))
            if sys.platform == "darwin":
                command.extend(["-dynamiclib", "-o", str(library)])
            else:
                command.extend(["-shared", "-fPIC", "-o", str(library)])
            subprocess.run(command, check=True, capture_output=True, text=True)
            libraries[name] = library
        cls.candidate = HostHarness(libraries["candidate"])
        cls.upstream = HostHarness(libraries["upstream"])
        cls.seams = ctypes.CDLL(str(libraries["seams"]))
        cls.seams.open_cfw_test_easylogger_hexdump_seams_reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_fill.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_fill.restype = ctypes.c_void_p
        cls.seams.open_cfw_test_easylogger_hexdump_format_header.argtypes = [
            ctypes.c_void_p,
            ctypes.c_uint32,
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_format_header.restype = (
            ctypes.c_int
        )
        for formatter in ("format_hex", "format_character"):
            function = getattr(
                cls.seams,
                "open_cfw_test_easylogger_hexdump_" + formatter,
            )
            function.argtypes = [ctypes.c_void_p, ctypes.c_uint32]
        cls.seams.open_cfw_test_easylogger_hexdump_blank_hex.argtypes = [
            ctypes.c_void_p
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_raw_submit.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint32,
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_build_level_less.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.seams.open_cfw_test_easylogger_hexdump_build_level_less.restype = (
            ctypes.c_uint32
        )
        cls.seams.open_cfw_test_easylogger_hexdump_record_payload.restype = (
            ctypes.c_void_p
        )
        cls.seams.open_cfw_test_easylogger_hexdump_diagnostic.restype = (
            ctypes.c_char_p
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.apple_clang = None
        apple_candidates = [
            os.environ.get("OPENCFW_APPLE_CLANG", ""),
            "/usr/bin/clang",
        ]
        for compiler in apple_candidates:
            if compiler and compiler_version(compiler) == APPLE_TARGET_PIN["version"]:
                cls.apple_clang = compiler
                break
        cls.apple_objects = []
        cls.apple_seam_objects = []
        if cls.apple_clang is not None:
            for sequence in (1, 2):
                output = temporary / f"candidate-apple-{sequence}.o"
                subprocess.run(
                    [cls.apple_clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(output)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                cls.apple_objects.append(output)
                seam_output = temporary / f"seams-apple-{sequence}.o"
                subprocess.run(
                    [
                        cls.apple_clang,
                        *TARGET_FLAGS,
                        "-c",
                        str(SEAMS_SOURCE),
                        "-o",
                        str(seam_output),
                    ],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                cls.apple_seam_objects.append(seam_output)

        cls.linux_objects = []
        cls.linux_seam_objects = []
        cls.linux_unavailable_reason = None
        try:
            image_id = subprocess.run(
                [DOCKER, "image", "inspect", LINUX_IMAGE, "--format", "{{.Id}}"],
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        except (FileNotFoundError, subprocess.CalledProcessError) as error:
            cls.linux_unavailable_reason = (
                f"pinned Linux compiler image {LINUX_IMAGE!r} is unavailable: "
                f"{error}"
            )
        else:
            if image_id != LINUX_IMAGE_ID:
                raise AssertionError(
                    f"unreviewed {LINUX_IMAGE} image ID: {image_id!r}"
                )
            linux_version = cls.run_linux_tool(
                LINUX_CLANG,
                ["--version"],
            ).stdout.splitlines()[0]
            if linux_version != LINUX_CLANG_VERSION:
                raise AssertionError(
                    f"unreviewed container compiler: {linux_version!r}"
                )
            source_in_container = (
                Path("openCFW") / SOURCE.relative_to(ROOT)
            ).as_posix()
            for sequence in (1, 2):
                name = f"candidate-linux-{sequence}.o"
                cls.run_linux_tool(
                    LINUX_CLANG,
                    [
                        *TARGET_FLAGS,
                        "-c",
                        source_in_container,
                        "-o",
                        f"/out/{name}",
                    ],
                )
                cls.linux_objects.append(temporary / name)
                seam_name = f"seams-linux-{sequence}.o"
                seam_source_in_container = (
                    Path("openCFW") / SEAMS_SOURCE.relative_to(ROOT)
                ).as_posix()
                cls.run_linux_tool(
                    LINUX_CLANG,
                    [
                        *TARGET_FLAGS,
                        "-c",
                        seam_source_in_container,
                        "-o",
                        f"/out/{seam_name}",
                    ],
                )
                cls.linux_seam_objects.append(temporary / seam_name)

        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def compare_pair(
        self,
        name: bytes,
        width: int,
        data: bytes,
        *,
        size: int | None = None,
        sink_limit: int = 0,
        configure=None,
        expect_lock_depth: int = 0,
    ) -> tuple[object, ...]:
        results = []
        aborted = []
        for harness in (self.candidate, self.upstream):
            harness.reset()
            if configure is not None:
                configure(harness)
            aborted.append(harness.run(
                name, width, data, size=size, sink_limit=sink_limit
            ))
            self.assertEqual(harness.get("lock_depth"), expect_lock_depth)
            results.append(harness.summary())
        self.assertEqual(aborted[0], aborted[1])
        self.assertEqual(results[0], results[1])
        return results[0]

    def parse_object(self, path: Path):
        data, sections = self.apollo_overlay.parse_elf32(path)
        symbol_table = self.apollo_overlay.section_named(sections, ".symtab")
        string_table = sections[int(symbol_table["link"])]
        strings = data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH", data, int(symbol_table["offset"]) + index * 16
            )
            name = self.apollo_overlay.elf_string(strings, fields[0], "symbol")
            symbols.append((name, fields))
        text = self.apollo_overlay.section_named(sections, FUNCTION_SECTION)
        relocations = []
        for section in sections:
            if int(section["type"]) == 9 and int(section["info"]) == int(text["index"]):
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    relocations.append((
                        offset,
                        information & 0xFF,
                        symbols[information >> 8][0],
                    ))
        return data, sections, symbols, relocations

    def strict_profile_inputs(
        self,
        profile: str,
    ) -> tuple[dict[str, object], list[dict[str, object]]]:
        pin = APPLE_TARGET_PIN if profile == "apple-clang" else LINUX_TARGET_PIN
        relocation_pins = (
            APPLE_RELOCATION_PINS
            if profile == "apple-clang"
            else LINUX_RELOCATION_PINS
        )
        closure: dict[str, object] = {
            "text_section": FUNCTION_SECTION,
            "rodata": {
                "section": RODATA_SECTION,
                "size": pin["rodata_size"],
                "sha256": pin["rodata_sha256"],
                "alignment": pin["rodata_alignment"],
                "symbols": [
                    {"name": name, "offset": offset, "size": size}
                    for name, offset, size in RODATA_SYMBOLS
                ],
            },
        }
        type_names = {
            10: "R_ARM_THM_CALL",
            49: "R_ARM_THM_MOVW_PREL_NC",
            50: "R_ARM_THM_MOVT_PREL",
        }
        targets = SOURCE_OWNED_TARGETS[profile]
        relocation_configs: list[dict[str, object]] = []
        for offset, kind, symbol in relocation_pins:
            item: dict[str, object] = {
                "offset": offset,
                "type": type_names[kind],
                "symbol": symbol,
            }
            if kind == 10:
                item.update({
                    "target_address": targets[symbol],
                    "symbol_type": "STT_NOTYPE",
                })
            relocation_configs.append(item)
        return closure, relocation_configs

    @staticmethod
    def seam_relocations_for(
        profile: str,
        function: str,
    ) -> tuple[tuple[int, int, str], ...]:
        if function in SEAM_PROFILE_RELOCATIONS[profile]:
            return SEAM_PROFILE_RELOCATIONS[profile][function]
        return SEAM_COMMON_RELOCATIONS[function]

    def relocate_seam_leaf(
        self,
        profile: str,
        function: str,
        text_bytes: bytes,
        owned_rodata: bytes = b"",
    ) -> bytes:
        layout = SEAM_LAYOUT_PINS[profile]
        runtime = int(layout["runtime"][function])
        targets = dict(SEAM_RETAINED_TARGETS)
        targets.update(layout["runtime"])
        targets.update({
            "open_cfw_easylogger_hexdump_put_hex.digits":
                layout["rodata_runtime"]["digits"],
            "open_cfw_easylogger_hexdump_enqueue_error":
                layout["rodata_runtime"]["enqueue_error"],
        })
        blob = bytearray(text_bytes)
        relocations = self.seam_relocations_for(profile, function)
        index = 0
        while index < len(relocations):
            offset, kind, symbol = relocations[index]
            target = int(targets[symbol])
            if kind in (10, 30):
                encoder = encode_thumb_bl if kind == 10 else encode_thumb_b_w
                blob[offset:offset + 4] = encoder(runtime + offset, target)
                index += 1
                continue
            self.assertIn(kind, (47, 49))
            self.assertLess(index + 1, len(relocations))
            high_offset, high_kind, high_symbol = relocations[index + 1]
            self.assertEqual((high_kind, high_symbol), (kind + 1, symbol))
            low_first, low_second = struct.unpack_from("<HH", blob, offset)
            high_first, high_second = struct.unpack_from(
                "<HH", blob, high_offset
            )
            low_addend = thumb_movwt_immediate(low_first, low_second)
            high_addend = thumb_movwt_immediate(high_first, high_second)
            if kind == 49:
                low_result = (
                    target + sign16(low_addend) - (runtime + offset)
                ) & 0xFFFF_FFFF
                high_result = (
                    target + sign16(high_addend) - (runtime + high_offset)
                ) & 0xFFFF_FFFF
            else:
                low_result = (target + low_addend) & 0xFFFF_FFFF
                high_result = (target + high_addend) & 0xFFFF_FFFF
            self.assertEqual(low_result >> 16, high_result >> 16)
            low_first, low_second = thumb_movwt_with_immediate(
                low_first, low_second, low_result
            )
            high_first, high_second = thumb_movwt_with_immediate(
                high_first, high_second, high_result >> 16
            )
            struct.pack_into(
                "<HH", blob, offset, low_first, low_second
            )
            struct.pack_into(
                "<HH", blob, high_offset, high_first, high_second
            )
            index += 2
        return bytes(blob) + owned_rodata

    def independent_mini_link(
        self,
        profile: str,
        unrelocated_text: bytes,
        rodata: bytes,
    ) -> bytes:
        pin = APPLE_TARGET_PIN if profile == "apple-clang" else LINUX_TARGET_PIN
        relocations = (
            APPLE_RELOCATION_PINS
            if profile == "apple-clang"
            else LINUX_RELOCATION_PINS
        )
        runtime = int(pin["runtime_address"])
        symbol_offsets = {name: offset for name, offset, _ in RODATA_SYMBOLS}
        targets = SOURCE_OWNED_TARGETS[profile]
        blob = bytearray(unrelocated_text + rodata)
        index = 0
        while index < len(relocations):
            offset, kind, symbol = relocations[index]
            if kind == 10:
                blob[offset:offset + 4] = encode_thumb_bl(
                    runtime + offset,
                    targets[symbol],
                )
                index += 1
                continue
            self.assertEqual(kind, 49)
            self.assertLess(index + 1, len(relocations))
            high_offset, high_kind, high_symbol = relocations[index + 1]
            self.assertEqual((high_kind, high_symbol), (50, symbol))
            low_first, low_second = struct.unpack_from("<HH", blob, offset)
            high_first, high_second = struct.unpack_from(
                "<HH", blob, high_offset
            )
            low_addend = sign16(
                thumb_movwt_immediate(low_first, low_second)
            )
            high_addend = sign16(
                thumb_movwt_immediate(high_first, high_second)
            )
            target = runtime + len(unrelocated_text) + symbol_offsets[symbol]
            low_result = (target + low_addend - (runtime + offset)) & 0xFFFF_FFFF
            high_result = (
                target + high_addend - (runtime + high_offset)
            ) & 0xFFFF_FFFF
            self.assertEqual(low_result >> 16, high_result >> 16)
            low_first, low_second = thumb_movwt_with_immediate(
                low_first, low_second, low_result
            )
            high_first, high_second = thumb_movwt_with_immediate(
                high_first, high_second, high_result >> 16
            )
            struct.pack_into("<HH", blob, offset, low_first, low_second)
            struct.pack_into(
                "<HH", blob, high_offset, high_first, high_second
            )
            index += 2
        return bytes(blob)

    def assert_source_seams_only(
        self,
        profile: str,
        text_bytes: bytes,
    ) -> None:
        self.assertIn(profile, SOURCE_OWNED_TARGETS)
        self.assertGreater(len(text_bytes), 0)
        candidate_text = SOURCE.read_text(encoding="utf-8") + \
            HEADER.read_text(encoding="utf-8")
        for fixed_code_seam in (
            "0x0043C0E4", "0x0044AA76", "0x0044B728", "0x0044B5A0"
        ):
            self.assertNotIn(fixed_code_seam, candidate_text)

    def test_authenticated_sources_and_candidate_artifacts_are_pinned(self) -> None:
        for path, (size, digest) in UPSTREAM_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)
        verifier = subprocess.run(
            [sys.executable, str(UPSTREAM_VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("EasyLogger 2.2.99 source-equivalent", verifier.stdout)
        self.assertIn("file hashes: OK", verifier.stdout)
        for path, (size, digest) in LOCAL_PINS.items():
            self.assertEqual(path.stat().st_size, size)
            self.assertEqual(sha256(path), digest)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "NONPRODUCTION",
            "OPEN_CFW_EASYLOGGER_HEXDUMP_FILL(",
            "open_cfw_easylogger_output_lock();",
            "OPEN_CFW_EASYLOGGER_HEXDUMP_RAW_SINK(",
            "open_cfw_easylogger_output_unlock();",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_EASYLOGGER_HEXDUMP_LOGGER_ADDRESS = 0x20070BE8U",
            "OPEN_CFW_EASYLOGGER_HEXDUMP_BUFFER_ADDRESS = 0x2006BD30U",
            "open_cfw_easylogger_hexdump_fill_source",
            "open_cfw_easylogger_hexdump_raw_submit_source",
            "open_cfw_easylogger_hexdump_format_header_source",
            "open_cfw_easylogger_hexdump_blank_hex_source",
        ):
            self.assertIn(token, header)
        combined = source + header + SEAMS_SOURCE.read_text(encoding="utf-8")
        self.assertNotIn("open_cfw_g2_easylogger_async_submit", combined)
        for fixed_code_seam in (
            "0x0043C0E4", "0x0044AA76", "0x0044B728", "0x0044B5A0"
        ):
            self.assertNotIn(fixed_code_seam, combined)

    def test_stock_span_seams_literals_and_complete_boundary_are_exact(self) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        body = self.application[START - BASE:END - BASE]
        self.assertEqual(len(body), STOCK_SIZE)
        self.assertEqual(sha256(body), STOCK_SHA256)
        self.assertEqual(body[:16].hex(), STOCK_FIRST)
        self.assertEqual(body[-16:].hex(), STOCK_LAST)

        direct_calls = []
        for offset in range(START - BASE, END - BASE - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            target = wide_branch_target(address, first, second, link=True)
            if target is not None:
                direct_calls.append((address, target))
        self.assertEqual(tuple(direct_calls), DIRECT_CALLS)

        def read_u32(address: int) -> int:
            return struct.unpack_from("<I", self.application, address - BASE)[0]

        def read_c_string(address: int) -> bytes:
            start = address - BASE
            end = self.application.index(0, start)
            return self.application[start:end]

        self.assertEqual(read_c_string(0x0043_DC88), b"\n")
        self.assertEqual(read_u32(0x0043_DC8C), 0x2006_BD30)
        self.assertEqual(read_c_string(0x0043_DC90), b"   ")
        self.assertEqual(read_c_string(0x0043_DC98), b" ")
        self.assertEqual(read_c_string(0x0043_DC9C), b"  ")
        self.assertEqual(read_c_string(0x0043_DCA0), b"%c")
        self.assertEqual(read_u32(0x0043_DCB4), 0x2007_0BE8)
        self.assertEqual(read_u32(0x0043_DCB8), 0x0077_70FC)
        self.assertEqual(read_c_string(0x0077_70FC), b"D/HEX %s: %04X-%04X: ")
        self.assertEqual(read_u32(0x0043_DCBC), 0x0078_D504)
        self.assertEqual(read_c_string(0x0078_D504), b"%02X ")

        callers = []
        entry_wide_branches = []
        external_wide_interiors = []
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            for link in (True, False):
                target = wide_branch_target(address, first, second, link=link)
                if target == START:
                    (callers if link else entry_wide_branches).append(address)
                if (
                    target is not None
                    and START < target < END
                    and not START <= address < END
                ):
                    external_wide_interiors.append((address, target, link))
        self.assertEqual(tuple(callers), CALLERS)
        self.assertEqual(
            sha256(",".join(f"{site:08X}" for site in callers).encode()),
            CALLER_SHA256,
        )
        width_records = []
        for caller in callers:
            matches = []
            for distance in range(2, 12, 2):
                site = caller - distance
                instruction = struct.unpack_from(
                    "<H", self.application, site - BASE
                )[0]
                if instruction in (0x2108, 0x2110):
                    matches.append((caller, site, instruction & 0xFF, instruction))
            self.assertEqual(len(matches), 1)
            width_records.extend(matches)
        self.assertEqual(tuple(width_records), CALLER_WIDTH_RECORDS)
        self.assertEqual(
            sha256(",".join(
                f"{caller:08X}:{site:08X}:{width:02X}:{instruction:04X}"
                for caller, site, width, instruction in width_records
            ).encode()),
            CALLER_WIDTH_SHA256,
        )
        self.assertEqual(
            {width: sum(row[2] == width for row in width_records)
             for width in (8, 16)},
            {8: 2, 16: 39},
        )
        self.assertNotIn(0, [row[2] for row in width_records])
        self.assertEqual(entry_wide_branches, [])
        self.assertEqual(external_wide_interiors, [])

        external_narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            for target in narrow_branch_targets(address, halfword):
                if START <= target < END and not START <= address < END:
                    external_narrow.append((address, target))
        self.assertEqual(external_narrow, [])

        stored = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            target = value & ~1
            if value & 1 and START <= target < END:
                stored.append((BASE + offset, value))
        self.assertEqual(stored, [])

        # Thirty-five official callers are now inside source-replaced production
        # spans.  The other six stock call instructions remain byte-owned and
        # their widths remain 5x16 plus 1x8.  Current generated overlay source
        # has no hexdump call, so there is no generated zero-width caller.
        overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        replaced = set()
        for patch in overlay["patch_sites"]:
            start = int(patch["runtime_address"])
            size = int(patch.get(
                "expected_size",
                len(bytes.fromhex(patch.get("expected_hex", ""))),
            ))
            replaced.update(
                caller for caller in callers if start <= caller < start + size
            )
        retained_records = [
            record for record in width_records if record[0] not in replaced
        ]
        self.assertEqual(
            tuple(record[0] for record in retained_records),
            CURRENT_RETAINED_CALLERS,
        )
        self.assertEqual((len(replaced), len(retained_records)), (35, 6))
        self.assertEqual(
            (sum(record[2] == 16 for record in retained_records),
             sum(record[2] == 8 for record in retained_records)),
            (5, 1),
        )
        self.assertEqual(
            sha256(",".join(
                f"{caller:08X}:{site:08X}:{width:02X}:{instruction:04X}"
                for caller, site, width, instruction in retained_records
            ).encode()),
            CURRENT_RETAINED_CALLER_WIDTH_SHA256,
        )
        configured_sources = {
            (entry["path"] if group == "sources" else entry["source"]["path"])
            for group in ("sources", "isolated_leaves", "relocated_leaves")
            for entry in overlay[group]
        }
        generated_references = []
        for relative in sorted(configured_sources):
            text = (ROOT / relative).read_text(encoding="utf-8")
            if FUNCTION in text or "0x0043DACC" in text:
                generated_references.append(relative)
        self.assertEqual(generated_references, [])

    def assert_exidx_record(
        self,
        data: bytes | bytearray,
        sections,
        symbols,
        text,
        exidx_name: str | None = None,
    ):
        if exidx_name is None:
            exidx_name = EXIDX_SECTION
        matches = [
            section for section in sections
            if section["name"] == exidx_name
        ]
        self.assertEqual(len(matches), 1)
        exidx = matches[0]
        self.assertEqual(int(exidx["size"]), 8)
        self.assertEqual(int(exidx["alignment"]), 4)
        self.assertTrue(int(exidx["flags"]) & 0x02)
        exidx_bytes = bytes(data[
            int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
        ])
        self.assertEqual(exidx_bytes, bytes.fromhex("0000000001000000"))
        relocations = []
        for section in sections:
            if (
                int(section["type"]) == 9
                and int(section["info"]) == int(exidx["index"])
            ):
                self.assertEqual(int(section["size"]), 8)
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"])
                )
                symbol_fields = symbols[information >> 8][1]
                relocations.append((
                    offset,
                    information & 0xFF,
                    symbol_fields[5],
                ))
        self.assertEqual(relocations, [(0, 42, int(text["index"]))])
        return exidx, exidx_bytes

    def test_apple_target_closure_is_deterministic_and_exact(self) -> None:
        if not self.apple_objects:
            self.skipTest("reviewed Apple clang 21.0.0 is unavailable")
        data, sections, symbols, relocations = self.parse_object(
            self.apple_objects[0]
        )
        data2, sections2, _, _ = self.parse_object(self.apple_objects[1])
        self.assertEqual(data, data2)
        self.assertEqual(sections, sections2)
        self.assertEqual(len(data), APPLE_TARGET_PIN["object_size"])
        self.assertEqual(sha256(data), APPLE_TARGET_PIN["object_sha256"])

        text = self.apollo_overlay.section_named(sections, FUNCTION_SECTION)
        rodata = self.apollo_overlay.section_named(sections, RODATA_SECTION)
        exidx = self.apollo_overlay.section_named(sections, EXIDX_SECTION)
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        rodata_bytes = data[
            int(rodata["offset"]):int(rodata["offset"]) + int(rodata["size"])
        ]
        pin = APPLE_TARGET_PIN
        self.assertEqual(int(text["size"]), pin["text_size"])
        self.assertEqual(int(text["alignment"]), pin["text_alignment"])
        self.assertEqual(sha256(text_bytes), pin["text_sha256"])
        self.assertEqual(int(rodata["size"]), pin["rodata_size"])
        self.assertEqual(int(rodata["alignment"]), pin["rodata_alignment"])
        self.assertEqual(sha256(rodata_bytes), pin["rodata_sha256"])
        self.assertEqual(rodata_bytes.hex(), RODATA_HEX)
        self.assertEqual(len(text_bytes + rodata_bytes), pin["closure_size"])
        self.assertEqual(sha256(text_bytes + rodata_bytes), pin["closure_sha256"])

        relocation_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in relocations
        ).encode()
        outgoing = [item for item in relocations if item[1] == 10]
        outgoing_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in outgoing
        ).encode()
        self.assertEqual(tuple(relocations), APPLE_RELOCATION_PINS)
        self.assertEqual(len(relocations), 23)
        self.assertEqual(sha256(relocation_record), pin["relocation_sha256"])
        self.assertEqual(len(outgoing), 15)
        self.assertEqual(sha256(outgoing_record), pin["outgoing_sha256"])
        for _, kind, symbol in relocations:
            if kind == 10:
                self.assertIn(symbol, UNDEFINED_SYMBOLS)
            else:
                self.assertIn(kind, (49, 50))
                self.assertTrue(symbol.startswith(".L.str"))

        undefined_records = sorted(
            (name, fields[3] & 0x0F, fields[3] >> 4, fields[4])
            for name, fields in symbols if name and fields[5] == 0
        )
        undefined = [item[0] for item in undefined_records]
        self.assertEqual(undefined, UNDEFINED_SYMBOLS)
        self.assertEqual(
            undefined_records,
            [(name, 0, 1, 0) for name in UNDEFINED_SYMBOLS],
        )
        functions = [
            name
            for name, fields in symbols
            if name and fields[5] != 0 and fields[3] & 0x0F == 2
        ]
        self.assertEqual(functions, [FUNCTION])
        writable_allocated = [
            section["name"]
            for section in sections
            if int(section["size"]) != 0
            and int(section["flags"]) & 0x02
            and int(section["flags"]) & 0x01
        ]
        self.assertEqual(writable_allocated, [])
        self.assertEqual(int(exidx["size"]), 8)
        self.assertEqual(int(exidx["alignment"]), 4)
        self.assertTrue(int(exidx["flags"]) & 0x02)
        exidx_bytes = data[
            int(exidx["offset"]):int(exidx["offset"]) + int(exidx["size"])
        ]
        self.assertEqual(exidx_bytes.hex(), "0000000001000000")
        self.assertEqual(sha256(exidx_bytes), pin["exidx_sha256"])
        exidx_relocations = []
        for section in sections:
            if int(section["type"]) == 9 and int(section["info"]) == int(exidx["index"]):
                self.assertEqual(int(section["size"]), 8)
                offset, information = struct.unpack_from(
                    "<II", data, int(section["offset"])
                )
                symbol_fields = symbols[information >> 8][1]
                exidx_relocations.append((
                    offset,
                    information & 0xFF,
                    symbol_fields[5],
                ))
        self.assertEqual(
            exidx_relocations,
            [(0, 42, int(text["index"]))],
        )
        self.assert_source_seams_only("apple-clang", text_bytes)

    def test_exact_linux_container_profile_is_deterministic_and_exact(self) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        self.assertEqual(
            self.linux_objects[0].read_bytes(),
            self.linux_objects[1].read_bytes(),
        )
        self.assertEqual(
            self.linux_objects[0].stat().st_size,
            LINUX_TARGET_PIN["object_size"],
        )
        self.assertEqual(
            sha256(self.linux_objects[0]),
            LINUX_TARGET_PIN["object_sha256"],
        )
        data, sections, symbols, relocations = self.parse_object(
            self.linux_objects[0]
        )
        text = self.apollo_overlay.section_named(sections, FUNCTION_SECTION)
        rodata = self.apollo_overlay.section_named(sections, RODATA_SECTION)
        text_bytes = data[
            int(text["offset"]):int(text["offset"]) + int(text["size"])
        ]
        rodata_bytes = data[
            int(rodata["offset"]):int(rodata["offset"]) + int(rodata["size"])
        ]
        pin = LINUX_TARGET_PIN
        self.assertEqual(int(text["size"]), pin["text_size"])
        self.assertEqual(int(text["alignment"]), pin["text_alignment"])
        self.assertEqual(sha256(text_bytes), pin["text_sha256"])
        self.assertEqual(int(rodata["size"]), pin["rodata_size"])
        self.assertEqual(int(rodata["alignment"]), pin["rodata_alignment"])
        self.assertEqual(sha256(rodata_bytes), pin["rodata_sha256"])
        self.assertEqual(rodata_bytes.hex(), RODATA_HEX)
        self.assertEqual(len(text_bytes + rodata_bytes), pin["closure_size"])
        self.assertEqual(
            sha256(text_bytes + rodata_bytes),
            pin["closure_sha256"],
        )

        relocation_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in relocations
        ).encode()
        outgoing = [item for item in relocations if item[1] == 10]
        outgoing_record = ",".join(
            f"{offset:08X}:{kind}:{symbol}"
            for offset, kind, symbol in outgoing
        ).encode()
        self.assertEqual(tuple(relocations), LINUX_RELOCATION_PINS)
        self.assertEqual(len(relocations), 23)
        self.assertEqual(sha256(relocation_record), pin["relocation_sha256"])
        self.assertEqual(len(outgoing), 15)
        self.assertEqual(sha256(outgoing_record), pin["outgoing_sha256"])
        for _, kind, symbol in relocations:
            if kind == 10:
                self.assertIn(symbol, UNDEFINED_SYMBOLS)
            else:
                self.assertIn(kind, (49, 50))
                self.assertTrue(symbol.startswith(".L.str"))

        undefined_records = sorted(
            (name, fields[3] & 0x0F, fields[3] >> 4, fields[4])
            for name, fields in symbols if name and fields[5] == 0
        )
        undefined = [item[0] for item in undefined_records]
        self.assertEqual(undefined, UNDEFINED_SYMBOLS)
        self.assertEqual(
            undefined_records,
            [(name, 0, 1, 0) for name in UNDEFINED_SYMBOLS],
        )
        functions = [
            name
            for name, fields in symbols
            if name and fields[5] != 0 and fields[3] & 0x0F == 2
        ]
        self.assertEqual(functions, [FUNCTION])
        writable_allocated = [
            section["name"]
            for section in sections
            if int(section["size"]) != 0
            and int(section["flags"]) & 0x02
            and int(section["flags"]) & 0x01
        ]
        self.assertEqual(writable_allocated, [])
        _, exidx_bytes = self.assert_exidx_record(
            data, sections, symbols, text
        )
        self.assertEqual(sha256(exidx_bytes), pin["exidx_sha256"])
        self.assert_source_seams_only("linux-clang", text_bytes)

    def test_source_seam_target_objects_are_deterministic_and_fail_closed(
        self,
    ) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        profiles = [("linux-clang", self.linux_seam_objects)]
        if self.apple_seam_objects:
            profiles.insert(0, ("apple-clang", self.apple_seam_objects))
        for profile, objects in profiles:
            with self.subTest(profile=profile):
                self.assertEqual(objects[0].read_bytes(), objects[1].read_bytes())
                pin = SEAM_TARGET_PINS[profile]
                data, sections = self.apollo_overlay.parse_elf32(objects[0])
                self.assertEqual(len(data), pin["object_size"])
                self.assertEqual(sha256(data), pin["object_sha256"])
                symbol_table = self.apollo_overlay.section_named(
                    sections, ".symtab"
                )
                string_table = sections[int(symbol_table["link"])]
                strings = data[
                    int(string_table["offset"]):
                    int(string_table["offset"]) + int(string_table["size"])
                ]
                symbols = []
                for index in range(int(symbol_table["size"]) // 16):
                    fields = struct.unpack_from(
                        "<IIIBBH",
                        data,
                        int(symbol_table["offset"]) + index * 16,
                    )
                    symbols.append((
                        self.apollo_overlay.elf_string(
                            strings, fields[0], "symbol"
                        ),
                        fields,
                    ))
                self.assertEqual(
                    sorted(
                        name for name, fields in symbols
                        if name and fields[5] == 0
                    ),
                    SEAM_UNDEFINED_SYMBOLS,
                )
                defined_functions = [
                    name for name, fields in symbols
                    if name and fields[5] != 0 and fields[3] & 0x0F == 2
                ]
                self.assertEqual(set(defined_functions), set(SEAM_FUNCTIONS))
                self.assertEqual(len(defined_functions), len(SEAM_FUNCTIONS))
                for function, (size, digest) in pin["text"].items():
                    section = self.apollo_overlay.section_named(
                        sections, ".text." + function
                    )
                    body = data[
                        int(section["offset"]):
                        int(section["offset"]) + int(section["size"])
                    ]
                    self.assertEqual(int(section["size"]), size)
                    self.assertEqual(int(section["alignment"]), 4)
                    self.assertEqual(sha256(body), digest)
                    selected = [
                        fields for name, fields in symbols if name == function
                    ]
                    self.assertEqual(len(selected), 1)
                    fields = selected[0]
                    self.assertEqual(
                        (fields[1], fields[2], fields[3] & 0x0F,
                         fields[3] >> 4, fields[4], fields[5]),
                        (1, size, 2,
                         0 if function in (
                             "open_cfw_easylogger_hexdump_put",
                             "open_cfw_easylogger_hexdump_put_hex",
                         ) else 1,
                         0, int(section["index"])),
                    )

                relocation_records = []
                relocation_by_section = {}
                for section in sections:
                    if int(section["type"]) != 9:
                        continue
                    target = sections[int(section["info"])]["name"]
                    records = []
                    for index in range(int(section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II",
                            data,
                            int(section["offset"]) + index * 8,
                        )
                        record = (
                            target,
                            offset,
                            information & 0xFF,
                            symbols[information >> 8][0],
                        )
                        records.append(record[1:])
                        relocation_records.append(record)
                    relocation_by_section[target] = records
                normalized = "|".join(
                    f"{section}:{offset:08X}:{kind}:{symbol}"
                    for section, offset, kind, symbol in relocation_records
                ).encode()
                self.assertEqual(
                    len(relocation_records), pin["relocation_count"]
                )
                self.assertEqual(
                    sha256(normalized), pin["relocation_sha256"]
                )
                for function in SEAM_FUNCTIONS:
                    self.assertEqual(
                        tuple(relocation_by_section.get(
                            ".text." + function, []
                        )),
                        self.seam_relocations_for(profile, function),
                    )
                self.assertEqual(
                    relocation_by_section[
                        ".text.open_cfw_easylogger_hexdump_raw_submit_source"
                    ],
                    [(2, 30, "open_cfw_g2_easylogger_async_record_build_level_less")],
                )
                builder_symbols = {
                    symbol
                    for _, _, symbol in relocation_by_section[
                        ".text.open_cfw_g2_easylogger_async_record_build_level_less"
                    ]
                }
                self.assertEqual(
                    builder_symbols,
                    set(SEAM_UNDEFINED_SYMBOLS)
                    | {"open_cfw_easylogger_hexdump_enqueue_error"},
                )
                self.assertNotIn(
                    "open_cfw_g2_easylogger_async_record_build_stock",
                    builder_symbols,
                )
                self.assertEqual(
                    sum(
                        1 for section in sections
                        if section["name"].startswith(".ARM.exidx.text.")
                    ),
                    len(pin["text"]),
                )
                for function in SEAM_FUNCTIONS:
                    text_section = self.apollo_overlay.section_named(
                        sections, ".text." + function
                    )
                    self.assert_exidx_record(
                        data,
                        sections,
                        symbols,
                        text_section,
                        ".ARM.exidx.text." + function,
                    )
                for name, rodata_pin in SEAM_RODATA_PINS.items():
                    section = self.apollo_overlay.section_named(
                        sections, rodata_pin["section"]
                    )
                    body = data[
                        int(section["offset"]):
                        int(section["offset"]) + int(section["size"])
                    ]
                    self.assertEqual(int(section["size"]), rodata_pin["size"])
                    self.assertEqual(
                        int(section["alignment"]), rodata_pin["alignment"]
                    )
                    self.assertEqual(sha256(body), rodata_pin["sha256"])
                    symbol_name, value, size, kind, binding, visibility = (
                        rodata_pin["symbol"]
                    )
                    symbol_fields = next(
                        fields for candidate, fields in symbols
                        if candidate == symbol_name
                    )
                    self.assertEqual(
                        (symbol_fields[1], symbol_fields[2],
                         symbol_fields[3] & 0x0F, symbol_fields[3] >> 4,
                         symbol_fields[4], symbol_fields[5]),
                        (value, size, kind, binding, visibility,
                         int(section["index"])),
                    )
                    self.assertEqual(
                        layout_address := SEAM_LAYOUT_PINS[profile][
                            "rodata_runtime"
                        ][name],
                        SEAM_LAYOUT_PINS[profile]["runtime"][
                            "open_cfw_easylogger_hexdump_put_hex"
                            if name == "digits"
                            else "open_cfw_g2_easylogger_async_record_build_level_less"
                        ] + (
                            pin["text"][
                                "open_cfw_easylogger_hexdump_put_hex"
                                if name == "digits"
                                else "open_cfw_g2_easylogger_async_record_build_level_less"
                            ][0]
                        ),
                    )
                    self.assertGreater(layout_address, 0)
                writable_allocated = [
                    section["name"]
                    for section in sections
                    if int(section["size"]) != 0
                    and int(section["flags"]) & 0x02
                    and int(section["flags"]) & 0x01
                ]
                self.assertEqual(writable_allocated, [])

                layout = SEAM_LAYOUT_PINS[profile]
                # These addresses freeze the pre-promotion placement rehearsal
                # and its independent mini-link digests.  Production now owns
                # equivalent dedicated leaves at the current overlay tail, so
                # the candidate gate deliberately no longer equates this
                # historical rehearsal tail with the live overlay size.
                candidate_pin = (
                    APPLE_TARGET_PIN
                    if profile == "apple-clang"
                    else LINUX_TARGET_PIN
                )
                self.assertEqual(
                    align_up(layout["production_tail"], 4),
                    layout["candidate_start"],
                )
                self.assertEqual(
                    candidate_pin["runtime_address"],
                    layout["candidate_start"],
                )
                cursor = (
                    layout["candidate_start"]
                    + candidate_pin["closure_size"]
                )
                intervals = [(
                    layout["candidate_start"],
                    cursor,
                    FUNCTION,
                )]
                for function in SEAM_FUNCTIONS:
                    cursor = align_up(cursor, 4)
                    self.assertEqual(cursor, layout["runtime"][function])
                    text_section = self.apollo_overlay.section_named(
                        sections, ".text." + function
                    )
                    text_body = data[
                        int(text_section["offset"]):
                        int(text_section["offset"]) + int(text_section["size"])
                    ]
                    owned_rodata = b""
                    if function == "open_cfw_easylogger_hexdump_put_hex":
                        rodata = self.apollo_overlay.section_named(
                            sections, SEAM_RODATA_PINS["digits"]["section"]
                        )
                        owned_rodata = data[
                            int(rodata["offset"]):
                            int(rodata["offset"]) + int(rodata["size"])
                        ]
                    elif function == (
                        "open_cfw_g2_easylogger_async_record_build_level_less"
                    ):
                        rodata = self.apollo_overlay.section_named(
                            sections,
                            SEAM_RODATA_PINS["enqueue_error"]["section"],
                        )
                        owned_rodata = data[
                            int(rodata["offset"]):
                            int(rodata["offset"]) + int(rodata["size"])
                        ]
                    relocated = self.relocate_seam_leaf(
                        profile, function, text_body, owned_rodata
                    )
                    expected_size, expected_sha = layout["relocated"][function]
                    self.assertEqual(len(relocated), expected_size)
                    self.assertEqual(sha256(relocated), expected_sha)
                    intervals.append((cursor, cursor + len(relocated), function))
                    cursor += len(relocated)
                self.assertEqual(cursor, layout["end"])
                self.assertEqual(
                    cursor - layout["production_tail"], layout["growth"]
                )
                for left, right in zip(intervals, intervals[1:]):
                    self.assertLessEqual(left[1], right[0])

    def test_source_seam_per_leaf_contract_mutations_fail_closed(self) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        profiles = [("linux-clang", self.linux_seam_objects[0])]
        if self.apple_seam_objects:
            profiles.insert(0, ("apple-clang", self.apple_seam_objects[0]))
        for profile, object_path in profiles:
            data, sections = self.apollo_overlay.parse_elf32(object_path)
            symbol_table = self.apollo_overlay.section_named(
                sections, ".symtab"
            )
            string_table = sections[int(symbol_table["link"])]
            strings = data[
                int(string_table["offset"]):
                int(string_table["offset"]) + int(string_table["size"])
            ]
            symbols = []
            for index in range(int(symbol_table["size"]) // 16):
                fields = struct.unpack_from(
                    "<IIIBBH",
                    data,
                    int(symbol_table["offset"]) + index * 16,
                )
                symbols.append((
                    self.apollo_overlay.elf_string(
                        strings, fields[0], "symbol"
                    ),
                    fields,
                ))
            relocation_by_section = {}
            for section in sections:
                if int(section["type"]) != 9:
                    continue
                target = sections[int(section["info"])]["name"]
                records = []
                for index in range(int(section["size"]) // 8):
                    offset, information = struct.unpack_from(
                        "<II", data, int(section["offset"]) + index * 8
                    )
                    records.append((
                        offset,
                        information & 0xFF,
                        symbols[information >> 8][0],
                    ))
                relocation_by_section[target] = records

            def verify_leaf(
                function: str,
                payload: bytes | bytearray,
                symbol_records,
                relocations,
            ) -> None:
                text = self.apollo_overlay.section_named(
                    sections, ".text." + function
                )
                body = payload[
                    int(text["offset"]):
                    int(text["offset"]) + int(text["size"])
                ]
                expected_size, expected_sha = SEAM_TARGET_PINS[profile][
                    "text"
                ][function]
                self.assertEqual((int(text["size"]), sha256(bytes(body))),
                                 (expected_size, expected_sha))
                selected = [
                    fields for name, fields in symbol_records
                    if name == function
                ]
                self.assertEqual(len(selected), 1)
                self.assertEqual(selected[0][2], expected_size)
                self.assertEqual(
                    tuple(relocations.get(".text." + function, [])),
                    self.seam_relocations_for(profile, function),
                )
                self.assert_exidx_record(
                    payload,
                    sections,
                    symbol_records,
                    text,
                    ".ARM.exidx.text." + function,
                )

            for function in SEAM_FUNCTIONS:
                with self.subTest(profile=profile, function=function):
                    verify_leaf(
                        function, data, symbols, relocation_by_section
                    )
                    text = self.apollo_overlay.section_named(
                        sections, ".text." + function
                    )
                    damaged_text = bytearray(data)
                    damaged_text[int(text["offset"])] ^= 1
                    with self.assertRaises(AssertionError):
                        verify_leaf(
                            function,
                            damaged_text,
                            symbols,
                            relocation_by_section,
                        )

                    damaged_symbols = list(symbols)
                    symbol_index = next(
                        index for index, (name, _) in enumerate(symbols)
                        if name == function
                    )
                    name, fields = damaged_symbols[symbol_index]
                    fields = list(fields)
                    fields[2] += 2
                    damaged_symbols[symbol_index] = (name, tuple(fields))
                    with self.assertRaises(AssertionError):
                        verify_leaf(
                            function,
                            data,
                            damaged_symbols,
                            relocation_by_section,
                        )

                    damaged_relocations = {
                        section: list(records)
                        for section, records in relocation_by_section.items()
                    }
                    target_section = ".text." + function
                    if damaged_relocations.get(target_section):
                        record = list(damaged_relocations[target_section][0])
                        record[1] = 255
                        damaged_relocations[target_section][0] = tuple(record)
                    else:
                        damaged_relocations[target_section] = [
                            (0, 10, "unexpected")
                        ]
                    with self.assertRaises(AssertionError):
                        verify_leaf(
                            function,
                            data,
                            symbols,
                            damaged_relocations,
                        )

                    exidx = self.apollo_overlay.section_named(
                        sections, ".ARM.exidx.text." + function
                    )
                    damaged_exidx = bytearray(data)
                    damaged_exidx[int(exidx["offset"])] ^= 1
                    with self.assertRaises(AssertionError):
                        verify_leaf(
                            function,
                            damaged_exidx,
                            symbols,
                            relocation_by_section,
                        )

                    exidx_relocation = next(
                        section for section in sections
                        if int(section["type"]) == 9
                        and int(section["info"]) == int(exidx["index"])
                    )
                    damaged_prel31 = bytearray(data)
                    information = struct.unpack_from(
                        "<I",
                        damaged_prel31,
                        int(exidx_relocation["offset"]) + 4,
                    )[0]
                    struct.pack_into(
                        "<I",
                        damaged_prel31,
                        int(exidx_relocation["offset"]) + 4,
                        (information & ~0xFF) | 41,
                    )
                    with self.assertRaises(AssertionError):
                        verify_leaf(
                            function,
                            damaged_prel31,
                            symbols,
                            relocation_by_section,
                        )

            for rodata_pin in SEAM_RODATA_PINS.values():
                section = self.apollo_overlay.section_named(
                    sections, rodata_pin["section"]
                )
                start = int(section["offset"])
                damaged = bytearray(data)
                damaged[start] ^= 1
                with self.assertRaises(AssertionError):
                    self.assertEqual(
                        sha256(bytes(damaged[start:start + int(section["size"])])),
                        rodata_pin["sha256"],
                    )

    def test_released_library_and_raw_transport_seams_are_authenticated(
        self,
    ) -> None:
        spans = {
            (0x0043_C0E4, 0x0043_C14A): (
                102,
                "34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a",
            ),
            (0x0044_AA76, 0x0044_AA80): (
                10,
                "a509174409c14871498cd505c5246e02d78cd9cf067100b83aff576842b3e123",
            ),
            (0x0044_8CCC, 0x0044_8D4E): (
                130,
                "91ae986d5deaa816a662a842ecd71217c0deb0dff552ebbe04e382f16e8ebc55",
            ),
            (0x0044_B5A0, 0x0044_B610): (
                112,
                "97b8f3f453cf4f85bd079916e7bbffcc11f7bef676034c2cb10911e2b9e74a1d",
            ),
            (0x0044_B728, 0x0044_B766): (
                62,
                "0b3f0ee4463f8a2560eb9a1ac68060b39fb797c0c44f5a85daa923fe5bcf14fd",
            ),
        }
        for (start, end), (size, digest) in spans.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)
        self.assertEqual(
            self.application[0x0044_AA76 - BASE:0x0044_AA80 - BASE].hex(),
            "80b50022fef727f901bd",
        )
        self.assertEqual(
            wide_branch_target(
                0x0044_AA7A,
                *struct.unpack_from(
                    "<HH", self.application, 0x0044_AA7A - BASE
                ),
                link=True,
            ),
            0x0044_8CCC,
        )
        expected_builder_calls = {
            0x0044_8D02: 0x0044_8A0C,
            0x0044_8D1A: 0x0043_9BE4,
            0x0044_8D2E: 0x0044_8AF0,
            0x0044_8D38: 0x0044_8A8E,
            0x0044_8D40: 0x0047_33EE,
        }
        self.assertEqual(
            {
                site: wide_branch_target(
                    site,
                    *struct.unpack_from(
                        "<HH", self.application, site - BASE
                    ),
                    link=True,
                )
                for site in expected_builder_calls
            },
            expected_builder_calls,
        )
        callers = {0x0044_AA76: [], 0x0044_8CCC: []}
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            target = wide_branch_target(
                address,
                *struct.unpack_from("<HH", self.application, offset),
                link=True,
            )
            if target in callers:
                callers[target].append(address)
        self.assertEqual(callers[0x0044_AA76], [0x0043_DB3C])
        self.assertEqual(callers[0x0044_8CCC], [0x0044_AA7A])
        self.assertEqual(
            wide_branch_target(
                0x0044_B60A,
                *struct.unpack_from(
                    "<HH", self.application, 0x0044_B60A - BASE
                ),
                link=True,
            ),
            0x0043_C0EC,
        )
        self.assertEqual(
            wide_branch_target(
                0x0044_B74E,
                *struct.unpack_from(
                    "<HH", self.application, 0x0044_B74E - BASE
                ),
                link=True,
            ),
            0x0048_1836,
        )

    def test_source_fill_and_bounded_formatters_match_standard_oracles(
        self,
    ) -> None:
        for offset in range(8):
            for count in (0, 1, 2, 3, 4, 7, 8, 15, 31):
                for value in (0, 0x41, 0xFF, 0x1234):
                    storage = (ctypes.c_uint8 * 48)(*([0xA5] * 48))
                    pointer = ctypes.addressof(storage) + offset
                    returned = self.seams.open_cfw_test_easylogger_hexdump_fill(
                        pointer, count, value
                    )
                    self.assertEqual(returned, pointer)
                    self.assertEqual(
                        bytes(storage),
                        b"\xA5" * offset
                        + bytes([value & 0xFF]) * count
                        + b"\xA5" * (48 - offset - count),
                    )

        for name in (b"", b"g2", b"name-with-dash", b"x" * 1020):
            for offset, end in (
                (0, 7),
                (0xFFFF, 0x10006),
                (0, 0xFFFF_FFFF),
            ):
                expected = (
                    b"D/HEX " + name + b": "
                    + f"{offset:04X}-{end:04X}: ".encode()
                )
                for capacity in (0, 1, 2, 8, 64, 1024):
                    storage = (ctypes.c_char * 1100)()
                    result = (
                        self.seams.open_cfw_test_easylogger_hexdump_format_header(
                            storage,
                            capacity,
                            name,
                            offset,
                            end,
                        )
                    )
                    self.assertEqual(result, len(expected))
                    if capacity != 0:
                        copied = expected[:capacity - 1]
                        self.assertEqual(bytes(storage[:len(copied)]), copied)
                        self.assertEqual(storage[len(copied)], b"\0")

        scratch = (ctypes.c_char * 8)()
        for value in range(256):
            self.seams.open_cfw_test_easylogger_hexdump_format_hex(
                scratch, value
            )
            self.assertEqual(
                bytes(scratch[:4]), f"{value:02X} ".encode() + b"\0"
            )
        self.seams.open_cfw_test_easylogger_hexdump_format_character(
            scratch, 0x7E
        )
        self.assertEqual(bytes(scratch[:2]), b"~\0")
        self.seams.open_cfw_test_easylogger_hexdump_blank_hex(scratch)
        self.assertEqual(bytes(scratch), b"   \0\0\0\0\0")

    def test_level_less_raw_source_adapter_enforces_single_owner_policy(
        self,
    ) -> None:
        getter_prefix = "open_cfw_test_easylogger_hexdump_"

        def get(name: str) -> int:
            function = getattr(self.seams, getter_prefix + name)
            function.restype = ctypes.c_uint32
            return int(function())

        # Direct builder tests cover all length cliffs and prove that payload
        # begins at +0x0D while the level byte at +0x0C remains untouched.
        message = bytes((index % 251) + 1 for index in range(300))
        for requested, expected in ((1, 1), (254, 254), (255, 255),
                                    (256, 255), (300, 255)):
            with self.subTest(length=requested):
                self.seams.open_cfw_test_easylogger_hexdump_seams_reset(
                    1, 0x6A, 1, 1
                )
                returned = (
                    self.seams.open_cfw_test_easylogger_hexdump_build_level_less(
                        message, requested, 0
                    )
                )
                self.assertEqual(returned, 0)
                self.assertEqual(get("record_length"), expected)
                self.assertEqual(get("record_metadata"), 0x6A)
                self.assertEqual(get("record_reserved_level"), 0xA5)
                self.assertEqual(get("record_payload_offset"), 0x0D)
                payload = (
                    self.seams.open_cfw_test_easylogger_hexdump_record_payload()
                )
                self.assertEqual(
                    ctypes.string_at(payload, expected), message[:expected]
                )
                self.assertEqual(ctypes.string_at(payload + expected, 1), b"\0")
                self.assertEqual(
                    (get("allocate_calls"), get("enqueue_calls")), (1, 1)
                )
                self.assertEqual(
                    (get("free_list_count"), get("record_owner")), (0, 2)
                )
                self.assertEqual(
                    (get("recycle_calls"), get("double_recycle_calls")),
                    (0, 0),
                )

        # Metadata is truncated to its low byte; only a resulting zero selects
        # the retained default.  The raw wrapper always requests that default.
        for metadata, expected in ((0, 0x6A), (0x34, 0x34),
                                   (0x1234, 0x34), (0x100, 0x6A)):
            with self.subTest(metadata=metadata):
                self.seams.open_cfw_test_easylogger_hexdump_seams_reset(
                    1, 0x6A, 1, 1
                )
                self.assertEqual(
                    self.seams.open_cfw_test_easylogger_hexdump_build_level_less(
                        b"m", 1, metadata
                    ),
                    0,
                )
                self.assertEqual(get("record_metadata"), expected)
        self.seams.open_cfw_test_easylogger_hexdump_seams_reset(1, 0x42, 1, 1)
        self.seams.open_cfw_test_easylogger_hexdump_raw_submit(b"raw", 3)
        self.assertEqual(get("record_metadata"), 0x42)

        # Allocation failure leaves the sole free-list record untouched.
        self.seams.open_cfw_test_easylogger_hexdump_seams_reset(1, 0x42, 0, 1)
        self.assertEqual(
            self.seams.open_cfw_test_easylogger_hexdump_build_level_less(
                b"allocation", 10, 0
            ),
            0,
        )
        self.assertEqual(
            (get("allocate_calls"), get("enqueue_calls"),
             get("free_list_count"), get("record_owner")),
            (1, 0, 1, 0),
        )

        # Enqueue exhaustion consumes and recycles exactly once.  Repeating
        # the operation proves there is never a second free-list insertion.
        self.seams.open_cfw_test_easylogger_hexdump_seams_reset(1, 0x42, 1, 0)
        for attempt in range(2):
            with self.subTest(enqueue_exhaustion_attempt=attempt):
                self.assertEqual(
                    self.seams.open_cfw_test_easylogger_hexdump_build_level_less(
                        b"failure", 7, 0
                    ),
                    0,
                )
                self.assertEqual(get("free_list_count"), 1)
                self.assertEqual(get("record_owner"), 0)
                self.assertEqual(get("recycle_calls"), attempt + 1)
                self.assertEqual(get("double_recycle_calls"), 0)
        self.assertEqual(get("diagnostic_calls"), 2)
        self.assertEqual(
            self.seams.open_cfw_test_easylogger_hexdump_diagnostic(),
            b"error!!!!!!elog_async_ext_output: enqueue_log failed\n",
        )

        # After a successful enqueue ownership belongs to the queue.  A second
        # build cannot allocate the same record and cannot recycle it.
        self.seams.open_cfw_test_easylogger_hexdump_seams_reset(1, 0x42, 1, 1)
        self.seams.open_cfw_test_easylogger_hexdump_raw_submit(b"success", 7)
        self.seams.open_cfw_test_easylogger_hexdump_raw_submit(b"again", 5)
        self.assertEqual(
            (get("allocate_calls"), get("enqueue_calls"),
             get("free_list_count"), get("record_owner")),
            (2, 1, 0, 2),
        )
        self.assertEqual(
            (get("recycle_calls"), get("double_recycle_calls")), (0, 0)
        )

        for ready, message, length, allocate in (
            (0, b"x", 1, 1),
            (1, None, 1, 1),
            (1, b"x", 0, 1),
            (1, b"x", 1, 0),
        ):
            self.seams.open_cfw_test_easylogger_hexdump_seams_reset(
                ready, 0x42, allocate, 1
            )
            self.seams.open_cfw_test_easylogger_hexdump_raw_submit(
                message, length
            )
            self.assertEqual((get("allocate_calls"), get("enqueue_calls")),
                             ((1 if ready and message and length else 0), 0))
            self.assertEqual(get("double_recycle_calls"), 0)

    def test_strict_nonproduction_closures_match_independent_mini_link(
        self,
    ) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        profiles = [("linux-clang", self.linux_objects[0], LINUX_TARGET_PIN)]
        if self.apple_objects:
            profiles.insert(
                0, ("apple-clang", self.apple_objects[0], APPLE_TARGET_PIN)
            )
        for profile, object_path, pin in profiles:
            with self.subTest(profile=profile):
                data, sections, _, parsed_relocations = self.parse_object(
                    object_path
                )
                text = self.apollo_overlay.section_named(
                    sections, FUNCTION_SECTION
                )
                rodata = self.apollo_overlay.section_named(
                    sections, RODATA_SECTION
                )
                text_bytes = data[
                    int(text["offset"]):
                    int(text["offset"]) + int(text["size"])
                ]
                rodata_bytes = data[
                    int(rodata["offset"]):
                    int(rodata["offset"]) + int(rodata["size"])
                ]
                closure, relocation_configs = self.strict_profile_inputs(
                    profile
                )
                blob, report = (
                    self.apollo_overlay.extract_relocated_function_closure(
                        object_path,
                        FUNCTION,
                        runtime_address=int(pin["runtime_address"]),
                        closure_config=closure,
                        relocation_configs=relocation_configs,
                        strict_relocation_contract=True,
                    )
                )
                self.assertEqual(len(blob), pin["closure_size"])
                self.assertEqual(
                    sha256(blob[:int(pin["text_size"])]),
                    pin["relocated_text_sha256"],
                )
                self.assertEqual(
                    sha256(blob), pin["relocated_closure_sha256"]
                )
                self.assertEqual(report["relocation_count"], 23)
                self.assertEqual(report["discarded_alloc_section_count"], 1)
                self.assertEqual(report["discarded_alloc_section_bytes"], 8)
                self.assertEqual(
                    report["authenticated_cantunwind_discard_count"], 1
                )
                self.assertEqual(
                    report["authenticated_cantunwind_discards"],
                    [{
                        "name": EXIDX_SECTION,
                        "size": 8,
                        "policy": (
                            "authenticated selected-function "
                            "CANTUNWIND/R_ARM_PREL31 metadata deliberately "
                            "discarded, not executable closure data"
                        ),
                    }],
                )
                self.assertEqual(
                    blob,
                    self.independent_mini_link(
                        profile, text_bytes, rodata_bytes
                    ),
                )
                runtime = int(pin["runtime_address"])
                for item in relocation_configs:
                    if item["type"] != "R_ARM_THM_CALL":
                        continue
                    offset = int(item["offset"])
                    first, second = struct.unpack_from("<HH", blob, offset)
                    self.assertEqual(
                        wide_branch_target(
                            runtime + offset, first, second, link=True
                        ),
                        item["target_address"],
                    )
                    self.assertEqual(item["symbol_type"], "STT_NOTYPE")
                self.assertEqual(
                    tuple(parsed_relocations),
                    APPLE_RELOCATION_PINS
                    if profile == "apple-clang"
                    else LINUX_RELOCATION_PINS,
                )

                wrong_type = [dict(item) for item in relocation_configs]
                next(
                    item for item in wrong_type
                    if item["type"] == "R_ARM_THM_CALL"
                )["symbol_type"] = "STT_FUNC"
                with self.assertRaisesRegex(
                    self.apollo_overlay.BuildError,
                    "symbol metadata differs",
                ):
                    self.apollo_overlay.extract_relocated_function_closure(
                        object_path,
                        FUNCTION,
                        runtime_address=int(pin["runtime_address"]),
                        closure_config=closure,
                        relocation_configs=wrong_type,
                        strict_relocation_contract=True,
                    )

    def test_documented_unwind_flags_cannot_remove_linux_exidx(self) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        source_in_container = (
            Path("openCFW") / SOURCE.relative_to(ROOT)
        ).as_posix()
        base_flags = [
            flag for flag in TARGET_FLAGS
            if flag not in (
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
            )
        ]
        variants = {
            "default": [],
            "no-exceptions": ["-fno-exceptions"],
            "no-unwind": ["-fno-unwind-tables"],
            "no-async-unwind": ["-fno-asynchronous-unwind-tables"],
            "no-unwind-both": [
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
            ],
            "no-unwind-or-exceptions": [
                "-fno-unwind-tables",
                "-fno-asynchronous-unwind-tables",
                "-fno-exceptions",
            ],
            "frontend-unwind-zero": [
                "-Xclang",
                "-funwind-tables=0",
            ],
        }
        for name, flags in variants.items():
            with self.subTest(name=name):
                output_name = f"candidate-{name}.o"
                self.run_linux_tool(
                    LINUX_CLANG,
                    [
                        *base_flags,
                        *flags,
                        "-c",
                        source_in_container,
                        "-o",
                        f"/out/{output_name}",
                    ],
                )
                output = self.temporary_path / output_name
                self.assertEqual(
                    output.stat().st_size,
                    LINUX_TARGET_PIN["object_size"],
                )
                self.assertEqual(
                    sha256(output),
                    LINUX_TARGET_PIN["object_sha256"],
                )
                data, sections, symbols, _ = self.parse_object(output)
                text = self.apollo_overlay.section_named(
                    sections, FUNCTION_SECTION
                )
                self.assert_exidx_record(data, sections, symbols, text)

        frontend_help = self.run_linux_tool(
            LINUX_CLANG,
            ["-cc1", "--help"],
        ).stdout
        self.assertIn("-funwind-tables=<value>", frontend_help)
        self.assertNotIn("exidx", frontend_help.lower())
        self.assertNotIn("ehabi", frontend_help.lower())

        assembly_name = "candidate-no-unwind.s"
        self.run_linux_tool(
            LINUX_CLANG,
            [
                *TARGET_FLAGS,
                "-fno-exceptions",
                "-S",
                source_in_container,
                "-o",
                f"/out/{assembly_name}",
            ],
        )
        assembly = (self.temporary_path / assembly_name).read_text(
            encoding="utf-8"
        )
        self.assertEqual(assembly.count("\t.fnstart"), 1)
        self.assertEqual(assembly.count("\t.cantunwind"), 1)
        self.assertEqual(assembly.count("\t.fnend"), 1)

    def test_authenticated_exidx_discard_boundary_and_negative_cases(
        self,
    ) -> None:
        if self.linux_unavailable_reason:
            self.skipTest(self.linux_unavailable_reason)
        proposed_entries = []
        expected = (
            (0x20C, 0x214, "f4fdff7f01000000", 0x007B_2099),
            (0x1FC, 0x204, "04feff7f01000000", 0x007B_27C7),
        )
        for profile, expected_row in zip(
            (APPLE_TARGET_PIN, LINUX_TARGET_PIN), expected
        ):
            rodata_offset = profile["text_size"]
            exidx_offset = align_up(
                rodata_offset + profile["rodata_size"],
                4,
            )
            self.assertEqual(exidx_offset, expected_row[0])
            first_word = encode_prel31(0, exidx_offset)
            proposed = struct.pack("<II", first_word, 1)
            self.assertEqual(proposed.hex(), expected_row[2])
            self.assertEqual(decode_prel31(first_word, exidx_offset), 0)
            self.assertEqual(exidx_offset + len(proposed), expected_row[1])
            self.assertEqual(
                int(profile["runtime_address"]) + int(profile["closure_size"]),
                expected_row[3],
            )
            self.assertGreater(exidx_offset + len(proposed), profile["closure_size"])
            proposed_entries.append(proposed)
        self.assertNotEqual(proposed_entries[0], proposed_entries[1])

        self.assertEqual(encode_prel31(0, 1 << 30), 0x4000_0000)
        with self.assertRaises(ValueError):
            encode_prel31(0, (1 << 30) + 1)
        with self.assertRaises(ValueError):
            encode_prel31(1 << 30, 0)
        with self.assertRaises(ValueError):
            align_up(1, 3)

        stripped_name = "candidate-linux-no-exidx.o"
        self.run_linux_tool(
            LINUX_OBJCOPY,
            [
                "--remove-section=" + EXIDX_SECTION,
                "--remove-section=.rel" + EXIDX_SECTION,
                "/out/candidate-linux-1.o",
                f"/out/{stripped_name}",
            ],
        )
        stripped_data, stripped_sections, stripped_symbols, _ = (
            self.parse_object(self.temporary_path / stripped_name)
        )
        stripped_text = self.apollo_overlay.section_named(
            stripped_sections, FUNCTION_SECTION
        )
        with self.assertRaises(AssertionError):
            self.assert_exidx_record(
                stripped_data,
                stripped_sections,
                stripped_symbols,
                stripped_text,
            )

        data, sections, symbols, _ = self.parse_object(self.linux_objects[0])
        text = self.apollo_overlay.section_named(sections, FUNCTION_SECTION)
        exidx = self.apollo_overlay.section_named(sections, EXIDX_SECTION)

        misaligned_sections = [dict(section) for section in sections]
        misaligned_sections[int(exidx["index"])]["alignment"] = 2
        with self.assertRaises(AssertionError):
            self.assert_exidx_record(
                data, misaligned_sections, symbols, text
            )

        wrong_payload = bytearray(data)
        struct.pack_into("<I", wrong_payload, int(exidx["offset"]) + 4, 2)
        with self.assertRaises(AssertionError):
            self.assert_exidx_record(
                wrong_payload, sections, symbols, text
            )

        wrong_relocation = bytearray(data)
        relocation_section = next(
            section for section in sections
            if int(section["type"]) == 9
            and int(section["info"]) == int(exidx["index"])
        )
        information = struct.unpack_from(
            "<I", wrong_relocation, int(relocation_section["offset"]) + 4
        )[0]
        struct.pack_into(
            "<I",
            wrong_relocation,
            int(relocation_section["offset"]) + 4,
            (information & ~0xFF) | 41,
        )
        with self.assertRaises(AssertionError):
            self.assert_exidx_record(
                wrong_relocation, sections, symbols, text
            )

    def test_candidate_is_excluded_and_reviewed_production_sources_own_spans(
        self,
    ) -> None:
        overlay = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        manifest = json.loads(CORE_SOURCE_MANIFEST.read_text(encoding="utf-8"))
        production_text = "\n".join((
            json.dumps(overlay, sort_keys=True),
            json.dumps(manifest, sort_keys=True),
            MAKEFILE.read_text(encoding="utf-8"),
        ))
        self.assertNotIn(FUNCTION, overlay.get("functions", []))
        self.assertNotIn(SOURCE.name, production_text)
        self.assertNotIn(SEAMS_SOURCE.name, production_text)
        expected = {
            "replace_easylogger_hexdump": (
                START,
                END - START,
                "open_cfw_easylogger_hexdump",
            ),
            "replace_easylogger_hexdump_raw_submit": (
                0x0044_AA76,
                10,
                "open_cfw_easylogger_hexdump_raw_submit",
            ),
            "replace_easylogger_async_record_build_level_less": (
                0x0044_8CCC,
                130,
                "open_cfw_g2_easylogger_async_record_build_level_less_single_owner",
            ),
        }
        sites = {site["name"]: site for site in overlay["patch_sites"]}
        for name, (start, size, target) in expected.items():
            site = sites[name]
            self.assertEqual(
                (site["runtime_address"], site["expected_size"],
                 site["branch"], site["target_function"]),
                (start, size, "b_w", target),
            )
            self.assertNotEqual(site["target_function"], FUNCTION)

        regions = manifest["component_overrides"]["apollo_main"]["regions"]
        for start in (START, 0x0044_AA76, 0x0044_8CCC):
            matches = [
                region for region in regions
                if region.get("target_address") == start
            ]
            self.assertEqual(len(matches), 1)
            self.assertEqual(
                matches[0]["address_status"],
                "generated_source_entry_replacement",
            )

    def test_upstream_differential_matrix_and_printability(self) -> None:
        matrix = [
            (b"empty", 8, b"", None),
            (b"one", 1, b"\x00", None),
            (b"partial", 8, bytes([0x00, 0x1F, 0x20, 0x41, 0x7E, 0x7F, 0x80]), None),
            (b"full", 8, bytes(range(8)), None),
            (b"nine", 8, bytes(range(9)), None),
            (b"wide", 16, bytes(range(31)), None),
            (b"truncate-width", 0x108, bytes(range(9)), None),
            (b"truncate-size", 8, b"\x41\x42", 0x1_0002),
        ]
        for name, width, data, size in matrix:
            with self.subTest(name=name):
                self.compare_pair(name, width, data, size=size)

        result = self.compare_pair(
            b"print", 8, bytes([0x1F, 0x20, 0x21, 0x7E, 0x7F, 0x80, 0x00, 0x41])
        )
        self.assertTrue(result[2].endswith(b". !~...A\n"))

    def test_filter_fill_and_lock_order_match_released_body(self) -> None:
        cases = [
            (lambda h: h.set_output(0), b"tag"),
            (lambda h: h.set_level(3), b"tag"),
            (lambda h: h.set_tag(b"needle"), b"tag"),
        ]
        for configure, name in cases:
            self.candidate.reset()
            configure(self.candidate)
            self.assertEqual(self.candidate.run(name, 8, b"\x01"), 0)
            self.assertEqual(self.candidate.get("fill_calls"), 1)
            self.assertEqual(self.candidate.get("fill_count"), 8)
            self.assertEqual(self.candidate.get("fill_value"), 0)
            self.assertEqual(self.candidate.get("sink_calls"), 0)
            self.assertEqual(self.candidate.events(), [EVENT_FILL, EVENT_STATE])

        self.candidate.reset()
        self.candidate.set_tag(b"needle")
        self.assertEqual(self.candidate.run(b"has-needle-tag", 8, b"\x01"), 0)
        events = self.candidate.events()
        self.assertEqual(events[:5], [
            EVENT_FILL, EVENT_STATE, EVENT_LOCK, EVENT_BUFFER, EVENT_HEADER
        ])
        self.assertEqual(events[-2:], [EVENT_SINK, EVENT_UNLOCK])
        self.assertEqual(self.candidate.get("lock_depth"), 0)

        self.candidate.reset()
        self.assertEqual(self.candidate.run(b"zero", 0, b"", size=0), 0)
        self.assertEqual(
            self.candidate.events(),
            [EVENT_FILL, EVENT_STATE, EVENT_LOCK, EVENT_UNLOCK],
        )

    def test_exact_formatter_arguments_copy_counts_and_raw_sink_abi(self) -> None:
        result = self.compare_pair(b"abi", 10, bytes([0x00, 0x20, 0x7E]))
        self.assertEqual(result[0], 1)
        self.assertEqual(result[4:7], (0, 9, b"abi"))
        self.assertEqual(result[7:11], (1, 3, 3, 7))
        self.assertEqual(self.candidate.get("fill_calls"), 1)
        self.assertEqual(self.candidate.get("append_calls"), 16)
        self.assertEqual(self.candidate.get("last_buffer_matches"), 1)
        self.assertEqual(self.candidate.get("last_length"), len(result[2]))
        self.assertEqual(self.upstream.loaded.open_cfw_test_easylogger_hexdump_last_level(), 4)

        header_index = self.candidate.events().index(EVENT_HEADER)
        sink_index = self.candidate.events().index(EVENT_SINK)
        self.assertLess(header_index, sink_index)
        self.assertEqual(self.candidate.events()[sink_index + 1], EVENT_UNLOCK)

    def test_formatter_return_boundaries_match_pristine_upstream(self) -> None:
        for result in (-1, 0, 1024, 1025):
            with self.subTest(result=result):
                pair = self.compare_pair(
                    b"format",
                    1,
                    b"\x41",
                    configure=lambda h, result=result: h.force_header(1, result),
                )
                if result in (-1, 1025):
                    self.assertEqual(pair[3], 1024)
                    self.assertTrue(pair[2].endswith(b"\n"))

    def test_zero_width_nonzero_size_retains_released_repetition(self) -> None:
        result = self.compare_pair(
            b"zero-width",
            0,
            b"\x41",
            sink_limit=3,
            expect_lock_depth=1,
        )
        self.assertEqual(result[0], 3)
        self.assertEqual(result[1], (result[1][0],) * 3)
        self.assertEqual(result[4], 0)
        self.assertEqual(result[5], 0xFFFF_FFFF)
        self.assertEqual(self.candidate.events()[-1], EVENT_SINK)

    def test_uint16_offset_wrap_matches_pristine_upstream(self) -> None:
        data = bytes(index & 0xFF for index in range(0xFFFF))
        result = self.compare_pair(
            b"wrap",
            2,
            data,
            sink_limit=32_769,
            expect_lock_depth=1,
        )
        self.assertEqual(result[0], 32_769)
        self.assertEqual(result[4:6], (0, 1))
        self.assertEqual(result[1][0], result[2])


if __name__ == "__main__":
    unittest.main()
