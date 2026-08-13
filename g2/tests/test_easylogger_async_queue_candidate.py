from __future__ import annotations

import ctypes
import hashlib
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
    / "runtime_easylogger_async_queue_candidate.c"
)
HEADER = SOURCE.with_suffix(".h")
FIXTURE = (
    ROOT / "tests" / "fixtures"
    / "runtime_easylogger_async_queue_candidate_host.c"
)
AUDIT = (
    ROOT / "docs" / "research"
    / "easylogger-async-queue-source-candidate-audit.md"
)
OFFICIAL = (
    ROOT / "blobs" / "official" / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY = ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
MAKEFILE = ROOT / "Makefile"

BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
TOKEN_0 = 0x202D_3FC8
TOKEN_1 = TOKEN_0 + 0x110
TOKEN_2 = TOKEN_1 + 0x110
TOKEN_3 = TOKEN_2 + 0x110
TOKEN_254 = TOKEN_0 + 254 * 0x110
TOKEN_255 = TOKEN_0 + 255 * 0x110
NEVER = 0xFFFF_FFFF

STOCK_RANGES = {
    "pool_initialize": (
        0x0044_895E,
        0x0044_89E8,
        "68db4f01f775e26ee30f1fd42f6f87f"
        "6846796a1577fd6d4908ac1ce9414a9da",
        (0x0044_8C84,),
        "c28398907c2837030307a3d551058517"
        "79dba978e94825b5e827c60de0ac351d",
    ),
    "queue_reset": (
        0x0044_89E8,
        0x0044_8A0C,
        "97ece75427abf834ff648cc4c51214a1"
        "a8f08f92614cb956e821c2f2d4fac6a5",
        (0x0044_8C88,),
        "ac85eb28a9ce105208163da561f07b40"
        "799b118a1267c11a9189abbc46e99383",
    ),
    "allocate": (
        0x0044_8A0C,
        0x0044_8A8E,
        "8fe9888ed7114728cbfd66f1190f62ddd"
        "09baa798cfa6ab03f0216ced8c148fa",
        (0x0044_8D02, 0x0044_8D84),
        "3da233fa29c40fd4c264b558f9dee542"
        "83b36349054d65a7c7d373aaf56e909c",
    ),
    "recycle": (
        0x0044_8A8E,
        0x0044_8AF0,
        "a694515d5f6c3389699ab4beceb8f675"
        "dfb604cf214ddf949ad429ed03e1502e",
        (0x0044_8B6C, 0x0044_8D38, 0x0044_8DBE, 0x0044_8E06),
        "e63c6bd159c05e8714f207aab3147544"
        "aa9209a3850ee6b93dfb9f28b078608d",
    ),
    "enqueue": (
        0x0044_8AF0,
        0x0044_8B96,
        "d38c8f35778486058d045b6b7ad9f9b6"
        "a6d8c5242f3c36828f72ea4270bc4c8e",
        (0x0044_8D2E, 0x0044_8DB4),
        "698fba2e8df984ccc5b94b1f2e92dd1"
        "aabf083f76e1fbc3a0909b2b746d9f2df",
    ),
    "dequeue": (
        0x0044_8B96,
        0x0044_8C74,
        "2ffb54da31890c2f13a19dd824b32416"
        "834fdc1de9ba30aefaa728157f80d89d",
        (0x0044_8E1C,),
        "27b52d08b84f7bc14729ae2a0a15b96"
        "0f62904c770eff47a21bee2f3ba241530",
    ),
    "initialize": (
        0x0044_8C74,
        0x0044_8CAA,
        "cf885aafebce26a3b9c0333b549c2d4"
        "aac5418706060d45c4b9ca5dd72f3832d",
        (0x005B_FA30,),
        "0d1553b2fcfc3a684d8b94610e3d47d"
        "4bb79b31c37b090e95c13569ebd6c110e",
    ),
}

ATOMIC_RANGES = {
    (0x0044_88EC, 0x0044_88F4): (
        "e5f5e62dc71878f964110f3a656adbc0"
        "3cd55c51f0aaa0542b6ead80f99430e8"
    ),
    (0x0044_88F4, 0x0044_88FC): (
        "e0af382433dcd2fe57b105589adcbeb5"
        "b7862f9c9cbc16ce06cf1c73f6e61c2e"
    ),
    (0x0044_88FC, 0x0044_8930): (
        "432307baa22caece864fb4e876f4ad602"
        "0f286a27e1cfebabd8df3bf71311de2"
    ),
    (0x0044_8930, 0x0044_8938): (
        "31549b25a562ad9bb17f62fd20e4ed47"
        "4cab10acda78d9a78f40374150dfd96b"
    ),
    (0x0044_8938, 0x0044_8940): (
        "36801dc170e6d188ad67099920b868739"
        "5943ac4206649d4c4d9dba048f598f4"
    ),
    (0x0044_8940, 0x0044_895E): (
        "e2ef1add5fc30b2ca5348d2cb29e5d8"
        "866e5c8b7fd4318ee27d4bc0fe37cc20b"
    ),
}

ATOMIC_CALLERS = {
    0x0044_88EC: (
        0x0044_8932, 0x0044_8988, 0x0044_89B4, 0x0044_89CC,
        0x0044_8A7E, 0x0044_8A9C, 0x0044_8B02,
    ),
    0x0044_88F4: (0x0044_893A,),
    0x0044_88FC: (0x0044_894A,),
    0x0044_8930: (
        0x0044_899E, 0x0044_89C0, 0x0044_89D8, 0x0044_89E2,
        0x0044_89F2, 0x0044_89FE, 0x0044_8A06, 0x0044_8A86,
        0x0044_8AB0, 0x0044_8B0A,
    ),
    0x0044_8938: (
        0x0044_8A16, 0x0044_8A24, 0x0044_8AA6, 0x0044_8B20,
        0x0044_8B28, 0x0044_8B3A, 0x0044_8BA2, 0x0044_8BAC,
        0x0044_8BB4, 0x0044_8BC6,
    ),
    0x0044_8940: (
        0x0044_8A38, 0x0044_8AC4, 0x0044_8B16, 0x0044_8B50,
        0x0044_8B8E, 0x0044_8BF6, 0x0044_8C06,
    ),
}

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

UNDEFINED = [
    "open_cfw_retained_easylogger_async_default_metadata",
    "open_cfw_retained_easylogger_async_free_head",
    "open_cfw_retained_easylogger_async_queue_head",
    "open_cfw_retained_easylogger_async_queue_statistics",
    "open_cfw_retained_easylogger_async_queue_tail",
    "open_cfw_retained_easylogger_async_ready",
    "open_cfw_retained_easylogger_async_record_pool",
    "open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive",
    "open_cfw_retained_easylogger_atomic_load_primitive",
    "open_cfw_retained_easylogger_atomic_store_primitive",
]

ADAPTER_FUNCTIONS = (
    "open_cfw_easylogger_atomic_store_adapter",
    "open_cfw_easylogger_atomic_load_adapter",
    "open_cfw_easylogger_atomic_compare_exchange_adapter",
)
QUEUE_FUNCTIONS = (
    "open_cfw_easylogger_async_queue_record_allocate",
    "open_cfw_easylogger_async_queue_record_recycle",
    "open_cfw_easylogger_async_queue_record_enqueue",
    "open_cfw_easylogger_async_queue_pool_initialize",
    "open_cfw_easylogger_async_queue_reset",
    "open_cfw_easylogger_async_queue_initialize",
    "open_cfw_easylogger_async_queue_record_dequeue",
)
FUNCTIONS = ADAPTER_FUNCTIONS + QUEUE_FUNCTIONS

LOCAL_PINS = {
    SOURCE: (
        15_829,
        "a5235faec1db1790a925c4e072973413"
        "6f8f23eed18076463bb7dda4f14d9a4b",
    ),
    HEADER: (
        9_666,
        "e4eed08bf55e7e589d5562cc664a4f7d"
        "536ab335d274d23b8d9e9f371f21e2d3",
    ),
    FIXTURE: (
        22_603,
        "1813704e7bd023a0efad882a66686db3"
        "f0448c54b33d3bcbabff8b94e4fcb77c",
    ),
    AUDIT: (
        20_022,
        "c2440ae7f71103e4d25417a4f76ccb3e"
        "8c28f89a79be5c700b3d0efcdea00c26",
    ),
}

COMMON_RELOCATIONS = {
    ADAPTER_FUNCTIONS[0]: [
        (0, 30, "open_cfw_retained_easylogger_atomic_store_primitive"),
    ],
    ADAPTER_FUNCTIONS[1]: [
        (0, 30, "open_cfw_retained_easylogger_atomic_load_primitive"),
    ],
    ADAPTER_FUNCTIONS[2]: [
        (
            12,
            10,
            "open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive",
        ),
    ],
    QUEUE_FUNCTIONS[0]: [
        (4, 47, "open_cfw_retained_easylogger_async_free_head"),
        (10, 48, "open_cfw_retained_easylogger_async_free_head"),
        (18, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (28, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (44, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (56, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (60, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (86, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
        (94, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (100, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (104, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (110, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (114, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
    ],
    QUEUE_FUNCTIONS[2]: [
        (20, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
        (28, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (32, 47, "open_cfw_retained_easylogger_async_queue_tail"),
        (36, 48, "open_cfw_retained_easylogger_async_queue_tail"),
        (42, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (48, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (76, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (82, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (88, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (102, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (124, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (132, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (136, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (158, 47, "open_cfw_retained_easylogger_async_queue_tail"),
        (162, 48, "open_cfw_retained_easylogger_async_queue_tail"),
        (172, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (182, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (186, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (204, 10, "open_cfw_easylogger_async_queue_record_recycle"),
    ],
    QUEUE_FUNCTIONS[3]: [
        (4, 47, "open_cfw_retained_easylogger_async_record_pool"),
        (8, 48, "open_cfw_retained_easylogger_async_record_pool"),
        (318, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
        (328, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (354, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
        (368, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (382, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
        (396, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (400, 47, "open_cfw_retained_easylogger_async_free_head"),
        (404, 48, "open_cfw_retained_easylogger_async_free_head"),
        (414, 30, "open_cfw_easylogger_atomic_store_adapter"),
    ],
    QUEUE_FUNCTIONS[4]: [
        (2, 47, "open_cfw_retained_easylogger_async_record_pool"),
        (6, 48, "open_cfw_retained_easylogger_async_record_pool"),
        (22, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (26, 47, "open_cfw_retained_easylogger_async_queue_head"),
        (30, 48, "open_cfw_retained_easylogger_async_queue_head"),
        (36, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (40, 47, "open_cfw_retained_easylogger_async_queue_tail"),
        (44, 48, "open_cfw_retained_easylogger_async_queue_tail"),
        (54, 30, "open_cfw_easylogger_atomic_store_adapter"),
    ],
    QUEUE_FUNCTIONS[5]: [
        (2, 47, "open_cfw_retained_easylogger_async_ready"),
        (6, 48, "open_cfw_retained_easylogger_async_ready"),
        (18, 10, "open_cfw_easylogger_async_queue_pool_initialize"),
        (22, 47, "open_cfw_retained_easylogger_async_record_pool"),
        (26, 48, "open_cfw_retained_easylogger_async_record_pool"),
        (44, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (48, 47, "open_cfw_retained_easylogger_async_queue_head"),
        (52, 48, "open_cfw_retained_easylogger_async_queue_head"),
        (58, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (62, 47, "open_cfw_retained_easylogger_async_queue_tail"),
        (66, 48, "open_cfw_retained_easylogger_async_queue_tail"),
        (72, 10, "open_cfw_easylogger_atomic_store_adapter"),
        (76, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (80, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (212, 47, "open_cfw_retained_easylogger_async_default_metadata"),
        (216, 48, "open_cfw_retained_easylogger_async_default_metadata"),
    ],
    QUEUE_FUNCTIONS[6]: [
        (6, 47, "open_cfw_retained_easylogger_async_queue_head"),
        (10, 48, "open_cfw_retained_easylogger_async_queue_head"),
        (16, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (20, 47, "open_cfw_retained_easylogger_async_queue_tail"),
        (24, 48, "open_cfw_retained_easylogger_async_queue_tail"),
        (32, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (40, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (62, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (70, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (78, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (92, 10, "open_cfw_easylogger_atomic_load_adapter"),
        (114, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (132, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
        (140, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (144, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        (182, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
        (186, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
    ],
}

TARGET_PINS = {
    "apple-clang": {
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": (
            7092,
            "9a7e470a573493c46be3399bef5bb02b3"
            "45c8990a0a875269de923d643788fed",
        ),
        "functions": {
            ADAPTER_FUNCTIONS[0]: (
                4,
                "90a54a1f68a806a1795bd044856908235"
                "426b3c0f67be605fb94d3d5344a747f",
            ),
            ADAPTER_FUNCTIONS[1]: (
                4,
                "90a54a1f68a806a1795bd044856908235"
                "426b3c0f67be605fb94d3d5344a747f",
            ),
            ADAPTER_FUNCTIONS[2]: (
                28,
                "d87c46ceb9ec5d930445c480ca011d65"
                "a326bc48ac14cafe377a438fcc690fa0",
            ),
            QUEUE_FUNCTIONS[0]: (
                138,
                "22dcf80f2f61e2e23780ec9398843aa2"
                "987e3b6606b69735fc7ffd6043c22974",
            ),
            QUEUE_FUNCTIONS[1]: (
                136,
                "dd3c08bd50a4990a80232e21843b9c2e"
                "d79d7a7fe63e4a041188d89c3e1dca50",
            ),
            QUEUE_FUNCTIONS[2]: (
                220,
                "9ead4766d3f2c035442afa4a19fcd8a2"
                "7c0a673a747f8bed807c5f00f7087701",
            ),
            QUEUE_FUNCTIONS[3]: (
                418,
                "a4ba43045a9c57dbac5ee4aa3b5f80e"
                "91dc3f51cfe21df5b0bb9ebefb5744fb9",
            ),
            QUEUE_FUNCTIONS[4]: (
                58,
                "a8fb1df6a0003486b811a142e0277c5f"
                "4eac6b1d04943cbd7184ee90aaf1097b",
            ),
            QUEUE_FUNCTIONS[5]: (
                230,
                "bc9ccc392fe2ccda2e0afc43a9d960ba"
                "c330a3ca7252be6cf48bd274ab9134fe",
            ),
            QUEUE_FUNCTIONS[6]: (
                284,
                "382af6a463906124ff0c6de89b241640"
                "5a97d6d3879ae7f196894638511f9f8f",
            ),
        },
        "recycle_relocations": [
            (18, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
            (22, 47, "open_cfw_retained_easylogger_async_free_head"),
            (26, 48, "open_cfw_retained_easylogger_async_free_head"),
            (32, 10, "open_cfw_easylogger_atomic_load_adapter"),
            (42, 10, "open_cfw_easylogger_atomic_store_adapter"),
            (54, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
            (62, 10, "open_cfw_easylogger_atomic_load_adapter"),
            (72, 10, "open_cfw_easylogger_atomic_store_adapter"),
            (84, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
            (88, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
            (100, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
            (104, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        ],
    },
    "linux-clang": {
        "version": "Homebrew clang version 22.1.8",
        "object": (
            7044,
            "b6c9cd26bc81e4aa978d293d0069d4e6"
            "ddd0b07a6cabbbc3f8afb652c239cdb6",
        ),
        "functions": {
            ADAPTER_FUNCTIONS[0]: (
                4,
                "90a54a1f68a806a1795bd044856908235"
                "426b3c0f67be605fb94d3d5344a747f",
            ),
            ADAPTER_FUNCTIONS[1]: (
                4,
                "90a54a1f68a806a1795bd044856908235"
                "426b3c0f67be605fb94d3d5344a747f",
            ),
            ADAPTER_FUNCTIONS[2]: (
                28,
                "d87c46ceb9ec5d930445c480ca011d65"
                "a326bc48ac14cafe377a438fcc690fa0",
            ),
            QUEUE_FUNCTIONS[0]: (
                138,
                "22dcf80f2f61e2e23780ec9398843aa2"
                "987e3b6606b69735fc7ffd6043c22974",
            ),
            QUEUE_FUNCTIONS[1]: (
                122,
                "e7853b2cff962c465c6de5ca0f66f965"
                "04b680d4dc503599576276113f7e40ef",
            ),
            QUEUE_FUNCTIONS[2]: (
                220,
                "9ead4766d3f2c035442afa4a19fcd8a2"
                "7c0a673a747f8bed807c5f00f7087701",
            ),
            QUEUE_FUNCTIONS[3]: (
                418,
                "a4ba43045a9c57dbac5ee4aa3b5f80e"
                "91dc3f51cfe21df5b0bb9ebefb5744fb9",
            ),
            QUEUE_FUNCTIONS[4]: (
                58,
                "a8fb1df6a0003486b811a142e0277c5f"
                "4eac6b1d04943cbd7184ee90aaf1097b",
            ),
            QUEUE_FUNCTIONS[5]: (
                230,
                "bc9ccc392fe2ccda2e0afc43a9d960ba"
                "c330a3ca7252be6cf48bd274ab9134fe",
            ),
            QUEUE_FUNCTIONS[6]: (
                284,
                "e3cb0022d346dd7d800081223501fd65"
                "2da2940b6bac5819878762c3bca70fcc",
            ),
        },
        "recycle_relocations": [
            (18, 10, "open_cfw_retained_easylogger_atomic_store_primitive"),
            (22, 47, "open_cfw_retained_easylogger_async_free_head"),
            (26, 48, "open_cfw_retained_easylogger_async_free_head"),
            (34, 10, "open_cfw_easylogger_atomic_load_adapter"),
            (44, 10, "open_cfw_easylogger_atomic_store_adapter"),
            (60, 10, "open_cfw_easylogger_atomic_compare_exchange_adapter"),
            (72, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
            (76, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
            (100, 47, "open_cfw_retained_easylogger_async_queue_statistics"),
            (104, 48, "open_cfw_retained_easylogger_async_queue_statistics"),
        ],
    },
}


class AsyncRecord(ctypes.Structure):
    _fields_ = [
        ("next", ctypes.c_uint32),
        ("state", ctypes.c_uint32),
        ("length", ctypes.c_uint16),
        ("metadata", ctypes.c_uint16),
        ("level", ctypes.c_uint8),
        ("payload", ctypes.c_uint8 * 256),
        ("padding", ctypes.c_uint8 * 3),
    ]


class AsyncStatistics(ctypes.Structure):
    _fields_ = [
        ("drained_record_count", ctypes.c_uint32),
        ("failed_operation_count", ctypes.c_uint32),
        ("reserved_08", ctypes.c_uint32),
        ("allocate_retry_total", ctypes.c_uint32),
        ("allocate_attempt_maximum", ctypes.c_uint32),
        ("recycle_retry_total", ctypes.c_uint32),
        ("recycle_attempt_maximum", ctypes.c_uint32),
        ("enqueue_retry_total", ctypes.c_uint32),
        ("enqueue_attempt_maximum", ctypes.c_uint32),
        ("dequeue_retry_total", ctypes.c_uint32),
        ("dequeue_attempt_maximum", ctypes.c_uint32),
        ("retry_limit_count", ctypes.c_uint32),
    ]


class EasyLoggerAsyncQueueCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = OFFICIAL.read_bytes()[PACKAGE_PREAMBLE:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")

        library = temporary / (
            "async_queue.dylib" if sys.platform == "darwin"
            else "async_queue.so"
        )
        host_command = [
            clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            str(FIXTURE),
        ]
        if sys.platform == "darwin":
            host_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            host_command.extend(["-shared", "-fPIC", "-o", str(library)])
        subprocess.run(host_command, check=True, capture_output=True, text=True)
        cls.loaded = ctypes.CDLL(str(library))
        cls.loaded.open_cfw_test_easylogger_async_queue_reset.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_set_record.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_schedule.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_dequeue_schedule.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_allocate.restype = (
            ctypes.c_uint32
        )
        cls.loaded.open_cfw_test_easylogger_async_queue_recycle.argtypes = [
            ctypes.c_uint32
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_enqueue.argtypes = [
            ctypes.c_uint32
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_enqueue.restype = (
            ctypes.c_uint32
        )
        cls.loaded.open_cfw_test_easylogger_async_queue_initialize.restype = (
            ctypes.c_uint32
        )
        cls.loaded.open_cfw_test_easylogger_async_queue_dequeue.restype = (
            ctypes.c_uint32
        )
        cls.loaded.open_cfw_test_easylogger_async_queue_build_level_less.argtypes = [
            ctypes.c_char_p,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_test_easylogger_async_queue_build_level_less.restype = (
            ctypes.c_uint32
        )
        cls.loaded.open_cfw_test_easylogger_async_queue_probe_bad_address.argtypes = [
            ctypes.c_uint32
        ]
        cls.loaded.open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive.argtypes = [
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
            ctypes.c_uint32,
        ]
        cls.loaded.open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive.restype = (
            ctypes.c_uint32
        )

        cls.target_object = temporary / "async_queue.o"
        subprocess.run(
            [clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(cls.target_object)],
            check=True,
            capture_output=True,
            text=True,
        )
        cls.compiler_version = subprocess.run(
            [clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        cls.target = cls.parse_target_object(cls.target_object)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @staticmethod
    def parse_target_object(path: Path) -> dict[str, object]:
        sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        data, sections = apollo_overlay.parse_elf32(path)
        symbol_table = apollo_overlay.section_named(sections, ".symtab")
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
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            symbols.append((name, fields))

        function_data = {}
        relocation_data = {}
        for function in FUNCTIONS:
            section = apollo_overlay.section_named(
                sections,
                ".text." + function,
            )
            body = data[
                int(section["offset"]):
                int(section["offset"]) + int(section["size"])
            ]
            function_data[function] = (
                len(body),
                int(section["alignment"]),
                hashlib.sha256(body).hexdigest(),
            )
            relocations = []
            for relocation_section in sections:
                if (
                    int(relocation_section["type"]) == 9
                    and int(relocation_section["info"]) == int(section["index"])
                ):
                    for index in range(int(relocation_section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II",
                            data,
                            int(relocation_section["offset"]) + index * 8,
                        )
                        relocations.append(
                            (
                                offset,
                                information & 0xFF,
                                symbols[information >> 8][0],
                            )
                        )
            relocation_data[function] = relocations
        return {
            "object": (len(data), hashlib.sha256(data).hexdigest()),
            "functions": function_data,
            "relocations": relocation_data,
            "undefined": sorted(
                name for name, fields in symbols if name and fields[5] == 0
            ),
        }

    @staticmethod
    def u32(name: str) -> int:
        return ctypes.c_uint32.in_dll(
            EasyLoggerAsyncQueueCandidateTests.loaded,
            name,
        ).value

    @staticmethod
    def u8(name: str) -> int:
        return ctypes.c_uint8.in_dll(
            EasyLoggerAsyncQueueCandidateTests.loaded,
            name,
        ).value

    @classmethod
    def records(cls) -> ctypes.Array[AsyncRecord]:
        return (AsyncRecord * 256).in_dll(
            cls.loaded,
            "open_cfw_test_easylogger_async_queue_pool",
        )

    @classmethod
    def stats(cls) -> AsyncStatistics:
        return AsyncStatistics.in_dll(
            cls.loaded,
            "open_cfw_retained_easylogger_async_queue_statistics",
        )

    @classmethod
    def reset(cls, free_head: int = 0, tail: int = TOKEN_0) -> None:
        cls.loaded.open_cfw_test_easylogger_async_queue_reset(free_head, tail)

    @classmethod
    def record(cls, token: int, next_token: int = 0, state: int = 0) -> None:
        cls.loaded.open_cfw_test_easylogger_async_queue_set_record(
            token,
            next_token,
            state,
        )

    @classmethod
    def schedule(
        cls,
        *,
        free_failures: int = 0,
        link_failures: int = 0,
        tail_failures: int = 0,
        tail_mutate_on_load: int = 0,
        tail_mutate_value: int = 0,
        tail_snapshot_conflicts: int = 0,
    ) -> None:
        cls.loaded.open_cfw_test_easylogger_async_queue_schedule(
            free_failures,
            link_failures,
            tail_failures,
            tail_mutate_on_load,
            tail_mutate_value,
            tail_snapshot_conflicts,
        )

    @classmethod
    def dequeue_schedule(
        cls,
        *,
        head_failures: int = 0,
        head_snapshot_conflicts: int = 0,
    ) -> None:
        cls.loaded.open_cfw_test_easylogger_async_queue_dequeue_schedule(
            head_failures,
            head_snapshot_conflicts,
        )

    def assert_valid_addresses(self) -> None:
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_bad_address_count"),
            0,
        )

    def test_record_and_statistics_abis_are_exact(self) -> None:
        self.assertEqual(ctypes.sizeof(AsyncRecord), 0x110)
        self.assertEqual(
            [
                AsyncRecord.next.offset,
                AsyncRecord.state.offset,
                AsyncRecord.length.offset,
                AsyncRecord.metadata.offset,
                AsyncRecord.level.offset,
                AsyncRecord.payload.offset,
                AsyncRecord.padding.offset,
            ],
            [0x00, 0x04, 0x08, 0x0A, 0x0C, 0x0D, 0x10D],
        )
        self.assertEqual(ctypes.sizeof(AsyncStatistics), 0x30)
        self.assertEqual(
            [
                AsyncStatistics.drained_record_count.offset,
                AsyncStatistics.failed_operation_count.offset,
                AsyncStatistics.allocate_retry_total.offset,
                AsyncStatistics.allocate_attempt_maximum.offset,
                AsyncStatistics.recycle_retry_total.offset,
                AsyncStatistics.recycle_attempt_maximum.offset,
                AsyncStatistics.enqueue_retry_total.offset,
                AsyncStatistics.enqueue_attempt_maximum.offset,
                AsyncStatistics.dequeue_retry_total.offset,
                AsyncStatistics.dequeue_attempt_maximum.offset,
                AsyncStatistics.retry_limit_count.offset,
            ],
            [0x00, 0x04, 0x0C, 0x10, 0x14, 0x18, 0x1C, 0x20, 0x24, 0x28, 0x2C],
        )
        header = HEADER.read_text()
        for field in (
            "drained_record_count",
            "failed_operation_count",
            "allocate_retry_total",
            "allocate_attempt_maximum",
            "recycle_retry_total",
            "recycle_attempt_maximum",
            "enqueue_retry_total",
            "enqueue_attempt_maximum",
            "dequeue_retry_total",
            "dequeue_attempt_maximum",
            "retry_limit_count",
        ):
            self.assertIn(
                "volatile open_cfw_easylogger_async_queue_u32 " + field,
                header,
            )

    def test_pool_reset_and_one_shot_initialization_match_stock_layout(self) -> None:
        records = self.records()
        ctypes.memset(
            ctypes.addressof(records),
            0xA5,
            ctypes.sizeof(records),
        )
        self.loaded.open_cfw_test_easylogger_async_queue_pool_initialize()
        self.assertEqual(
            self.u32("open_cfw_retained_easylogger_async_free_head"),
            TOKEN_0,
        )
        for index in range(254):
            self.assertEqual(records[index].state, 0)
            self.assertEqual(records[index].next, TOKEN_0 + (index + 1) * 0x110)
            self.assertEqual(records[index].length, 0)
            self.assertEqual(records[index].metadata, 0)
            self.assertEqual(records[index].level, 0)
            self.assertEqual(bytes(records[index].payload), bytes(256))
        for index in (254, 255):
            self.assertEqual((records[index].state, records[index].next), (0, 0))
            self.assertEqual(records[index].length, 0xA5A5)
            self.assertEqual(records[index].metadata, 0xA5A5)
            self.assertEqual(records[index].level, 0xA5)

        records[255].next = TOKEN_2
        records[255].state = 0x77
        self.loaded.open_cfw_test_easylogger_async_queue_dummy_reset()
        self.assertEqual(records[255].next, 0)
        self.assertEqual(records[255].state, 0x77)
        self.assertEqual(
            self.u32("open_cfw_retained_easylogger_async_queue_head"),
            TOKEN_255,
        )
        self.assertEqual(
            self.u32("open_cfw_retained_easylogger_async_queue_tail"),
            TOKEN_255,
        )

        self.reset()
        ready = ctypes.c_uint8.in_dll(
            self.loaded,
            "open_cfw_retained_easylogger_async_ready",
        )
        metadata = ctypes.c_uint8.in_dll(
            self.loaded,
            "open_cfw_retained_easylogger_async_default_metadata",
        )
        ready.value = 0
        metadata.value = 0xA5
        self.stats().retry_limit_count = 0x11223344
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_initialize(),
            0,
        )
        self.assertEqual((ready.value, metadata.value), (1, 1))
        self.assertEqual(bytes(self.stats()), bytes(0x30))
        self.assertEqual(
            (
                self.u32("open_cfw_retained_easylogger_async_free_head"),
                self.u32("open_cfw_retained_easylogger_async_queue_head"),
                self.u32("open_cfw_retained_easylogger_async_queue_tail"),
            ),
            (TOKEN_0, TOKEN_255, TOKEN_255),
        )
        metadata.value = 0x6A
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_initialize(),
            0,
        )
        self.assertEqual(metadata.value, 0x6A)
        self.assert_valid_addresses()

    def test_dequeue_rotates_dummy_and_preserves_stock_level_omission(self) -> None:
        payload = b"dequeue payload"
        self.reset(0, TOKEN_0)
        records = self.records()
        records[0].next = TOKEN_1
        records[0].level = 0xA5
        records[1].next = 0
        records[1].length = len(payload)
        records[1].metadata = 0x6A
        records[1].level = 0x03
        records[1].payload[:len(payload) + 1] = payload + b"\0"
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_dequeue(),
            TOKEN_0,
        )
        self.assertEqual(
            (
                self.u32("open_cfw_retained_easylogger_async_queue_head"),
                self.u32("open_cfw_retained_easylogger_async_queue_tail"),
            ),
            (TOKEN_1, TOKEN_1),
        )
        self.assertEqual((records[0].length, records[0].metadata), (len(payload), 0x6A))
        self.assertEqual(records[0].level, 0xA5)
        self.assertEqual(bytes(records[0].payload[:len(payload) + 1]), payload + b"\0")
        self.assertEqual(
            (self.stats().dequeue_retry_total, self.stats().dequeue_attempt_maximum),
            (1, 2),
        )
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_dequeue(), 0)
        self.assert_valid_addresses()

    def test_dequeue_contention_and_retry_exhaustion_are_bounded(self) -> None:
        self.reset(0, TOKEN_1)
        self.record(TOKEN_0, TOKEN_1, 2)
        self.record(TOKEN_1, 0, 2)
        ctypes.c_uint32.in_dll(
            self.loaded,
            "open_cfw_retained_easylogger_async_queue_head",
        ).value = TOKEN_0
        self.dequeue_schedule(head_failures=3)
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_dequeue(),
            TOKEN_0,
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_head_cas_calls"),
            4,
        )
        self.assertEqual(
            (self.stats().dequeue_retry_total, self.stats().dequeue_attempt_maximum),
            (3, 4),
        )

        self.reset(0, TOKEN_1)
        self.record(TOKEN_0, TOKEN_1, 2)
        self.record(TOKEN_2, TOKEN_1, 2)
        self.record(TOKEN_1, 0, 2)
        ctypes.c_uint32.in_dll(
            self.loaded,
            "open_cfw_retained_easylogger_async_queue_head",
        ).value = TOKEN_0
        self.dequeue_schedule(head_snapshot_conflicts=NEVER)
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_dequeue(),
            0,
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_head_load_calls"),
            20001,
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_head_cas_calls"),
            0,
        )
        self.assertEqual(self.stats().retry_limit_count, 1)
        self.assert_valid_addresses()

    def test_allocate_pops_treiber_head_and_empty_is_counted(self) -> None:
        self.reset(TOKEN_1)
        self.record(TOKEN_1, TOKEN_2)
        self.record(TOKEN_2, 0)
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_allocate(),
            TOKEN_1,
        )
        records = self.records()
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_2)
        self.assertEqual((records[1].state, records[1].next), (1, 0))
        self.assertEqual(
            (self.stats().allocate_retry_total, self.stats().allocate_attempt_maximum),
            (0, 1),
        )
        self.assertEqual(
            (self.u32("open_cfw_test_easylogger_async_queue_state_store_calls"),
             self.u32("open_cfw_test_easylogger_async_queue_next_store_calls")),
            (1, 1),
        )
        self.assert_valid_addresses()

        self.reset(0)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_allocate(), 0)
        self.assertEqual(self.stats().failed_operation_count, 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 0)

    def test_allocate_contention_and_exact_retry_threshold(self) -> None:
        self.reset(TOKEN_1)
        self.record(TOKEN_1, TOKEN_2)
        self.schedule(free_failures=3)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_allocate(), TOKEN_1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 4)
        self.assertEqual(
            (self.stats().allocate_retry_total, self.stats().allocate_attempt_maximum),
            (3, 4),
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"),
            3,
        )

        self.reset(TOKEN_1)
        self.record(TOKEN_1, TOKEN_2)
        self.schedule(free_failures=999)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_allocate(), TOKEN_1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1000)
        self.assertEqual(
            (self.stats().allocate_retry_total, self.stats().allocate_attempt_maximum),
            (999, 1000),
        )

        self.reset(TOKEN_1)
        self.record(TOKEN_1, TOKEN_2)
        self.schedule(free_failures=NEVER)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_allocate(), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1000)
        self.assertEqual(
            (self.stats().retry_limit_count, self.stats().failed_operation_count),
            (1, 1),
        )

    def test_recycle_pushes_head_and_accumulates_retry_statistics(self) -> None:
        self.reset(TOKEN_2)
        self.schedule(free_failures=2)
        self.loaded.open_cfw_test_easylogger_async_queue_recycle(TOKEN_1)
        records = self.records()
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_1)
        self.assertEqual((records[1].state, records[1].next), (0, TOKEN_2))
        self.assertEqual(
            (self.stats().recycle_retry_total, self.stats().recycle_attempt_maximum),
            (2, 3),
        )
        before = self.u32("open_cfw_test_easylogger_async_queue_primitive_store_calls")
        self.loaded.open_cfw_test_easylogger_async_queue_recycle(0)
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_primitive_store_calls"),
            before,
        )

        self.reset(TOKEN_2)
        self.schedule(free_failures=999)
        self.loaded.open_cfw_test_easylogger_async_queue_recycle(TOKEN_1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1000)
        self.assertEqual(
            (self.stats().recycle_retry_total, self.stats().recycle_attempt_maximum),
            (999, 1000),
        )
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_1)
        self.assert_valid_addresses()

    def test_recycler_retry_exhaustion_leaks_observed_record(self) -> None:
        self.reset(TOKEN_2)
        self.record(TOKEN_1, 0xA5A5A5A5, 1)
        self.schedule(free_failures=NEVER)
        self.loaded.open_cfw_test_easylogger_async_queue_recycle(TOKEN_1)
        records = self.records()
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1000)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_2)
        self.assertEqual((records[1].state, records[1].next), (0, TOKEN_2))
        self.assertEqual(self.stats().retry_limit_count, 1)
        self.assertEqual(self.stats().recycle_attempt_maximum, 0)

    def test_enqueue_success_transfers_ownership_and_advances_tail(self) -> None:
        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_1, 0xA5A5A5A5, 1)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        records = self.records()
        self.assertEqual((records[1].state, records[1].next), (2, 0))
        self.assertEqual(records[0].next, TOKEN_1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_queue_tail"), TOKEN_1)
        self.assertEqual(
            (self.stats().enqueue_retry_total, self.stats().enqueue_attempt_maximum),
            (0, 1),
        )
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 0)

    def test_enqueue_helps_lagging_tail_before_linking(self) -> None:
        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, TOKEN_2, 2)
        self.record(TOKEN_2, 0, 2)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        records = self.records()
        self.assertEqual(records[0].next, TOKEN_2)
        self.assertEqual(records[2].next, TOKEN_1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_queue_tail"), TOKEN_1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_tail_cas_calls"), 2)
        self.assertEqual(
            (self.stats().enqueue_retry_total, self.stats().enqueue_attempt_maximum),
            (1, 2),
        )
        self.assert_valid_addresses()

    def test_enqueue_tail_help_and_final_tail_cas_contention_are_real(self) -> None:
        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, TOKEN_2, 2)
        self.record(TOKEN_2, 0, 2)
        self.schedule(tail_failures=2)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_tail_cas_calls"), 4)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"), 2)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_queue_tail"), TOKEN_1)
        self.assertEqual(self.stats().enqueue_attempt_maximum, 4)

        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.schedule(tail_failures=1)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        self.assertEqual(self.records()[0].next, TOKEN_1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_queue_tail"), TOKEN_0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_tail_cas_calls"), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"), 1)
        self.assert_valid_addresses()

    def test_enqueue_reloads_when_tail_snapshot_changes(self) -> None:
        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_2, 0, 2)
        self.schedule(tail_mutate_on_load=2, tail_mutate_value=TOKEN_2)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        self.assertEqual(self.records()[2].next, TOKEN_1)
        self.assertEqual(self.stats().enqueue_retry_total, 1)
        self.assertEqual(self.stats().enqueue_attempt_maximum, 2)
        self.assert_valid_addresses()

    def test_enqueue_link_contention_updates_cumulative_and_maximum(self) -> None:
        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.schedule(link_failures=4)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_link_cas_calls"), 5)
        self.assertEqual(
            (self.stats().enqueue_retry_total, self.stats().enqueue_attempt_maximum),
            (4, 5),
        )
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"), 4)

        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.schedule(link_failures=9999)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_link_cas_calls"), 10000)
        self.assertEqual(
            (self.stats().enqueue_retry_total, self.stats().enqueue_attempt_maximum),
            (9999, 10000),
        )
        self.assert_valid_addresses()

    def test_enqueue_retry_limit_consumes_and_recycles_once(self) -> None:
        self.reset(TOKEN_3, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_3, 0, 0)
        self.schedule(link_failures=NEVER)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 0)
        records = self.records()
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_link_cas_calls"), 10000)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_1)
        self.assertEqual((records[1].state, records[1].next), (0, TOKEN_3))
        self.assertEqual(
            (self.stats().retry_limit_count, self.stats().failed_operation_count),
            (1, 1),
        )
        self.assertEqual(self.stats().enqueue_attempt_maximum, 0)
        self.assert_valid_addresses()

    def test_tail_snapshot_exhaustion_consumes_and_recycles(self) -> None:
        self.reset(TOKEN_3, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_2, 0, 2)
        self.record(TOKEN_3, 0, 0)
        self.schedule(tail_snapshot_conflicts=NEVER)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_link_cas_calls"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_tail_cas_calls"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_tail_load_calls"), 20001)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"), 10000)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_1)
        self.assertEqual((self.records()[1].state, self.records()[1].next), (0, TOKEN_3))
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1)
        self.assertEqual(
            (self.stats().retry_limit_count, self.stats().failed_operation_count),
            (1, 1),
        )
        self.assert_valid_addresses()

    def test_nested_enqueue_and_recycler_exhaustion_preserves_consumed_ownership(self) -> None:
        self.reset(TOKEN_3, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_3, 0, 0)
        self.schedule(link_failures=NEVER, free_failures=NEVER)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(TOKEN_1), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_link_cas_calls"), 10000)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 1000)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_3)
        self.assertEqual((self.records()[1].state, self.records()[1].next), (0, TOKEN_3))
        self.assertEqual(
            (self.stats().retry_limit_count, self.stats().failed_operation_count),
            (2, 1),
        )
        self.assertEqual(
            (
                self.stats().enqueue_retry_total,
                self.stats().enqueue_attempt_maximum,
                self.stats().recycle_retry_total,
                self.stats().recycle_attempt_maximum,
            ),
            (0, 0, 0, 0),
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_competing_mutation_count"),
            11000,
        )
        self.assert_valid_addresses()

    def test_null_enqueue_does_not_take_ownership_or_touch_state(self) -> None:
        self.reset(TOKEN_3, TOKEN_0)
        self.assertEqual(self.loaded.open_cfw_test_easylogger_async_queue_enqueue(0), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_primitive_load_calls"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_primitive_store_calls"), 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_primitive_cas_calls"), 0)

    def test_retry_totals_accumulate_while_maxima_remain_high_water_marks(self) -> None:
        self.reset(TOKEN_1)
        self.record(TOKEN_1, TOKEN_2)
        self.record(TOKEN_2, TOKEN_3)
        self.record(TOKEN_3, 0)
        for failures, expected in ((2, TOKEN_1), (4, TOKEN_2), (1, TOKEN_3)):
            self.schedule(free_failures=failures)
            self.assertEqual(
                self.loaded.open_cfw_test_easylogger_async_queue_allocate(),
                expected,
            )
        self.assertEqual(
            (self.stats().allocate_retry_total, self.stats().allocate_attempt_maximum),
            (7, 5),
        )

    def test_inner_compare_exchange_is_strong_and_updates_expected(self) -> None:
        object_word = ctypes.c_uint32(7)
        expected = ctypes.c_uint32(6)
        primitive = self.loaded.open_cfw_retained_easylogger_atomic_compare_exchange_strong_primitive
        self.assertEqual(primitive(ctypes.byref(object_word), ctypes.byref(expected), 9), 0)
        self.assertEqual((object_word.value, expected.value), (7, 7))
        self.assertEqual(primitive(ctypes.byref(object_word), ctypes.byref(expected), 9), 1)
        self.assertEqual((object_word.value, expected.value), (9, 7))

    def test_corrected_builder_runs_against_real_queue_candidate(self) -> None:
        payload = b"combined builder and queue"
        self.reset(TOKEN_1, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_1, 0, 0)
        self.records()[1].level = 0xA5
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_build_level_less(
                payload,
                len(payload),
                0x6A,
            ),
            0,
        )
        records = self.records()
        self.assertEqual(
            (
                records[1].state,
                records[1].length,
                records[1].metadata,
                records[1].level,
            ),
            (2, len(payload), 0x6A, 0xA5),
        )
        self.assertEqual(bytes(records[1].payload[:len(payload) + 1]), payload + b"\0")
        self.assertEqual(records[0].next, TOKEN_1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_queue_tail"), TOKEN_1)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_diagnostic_calls"), 0)
        self.assert_valid_addresses()

        self.reset(TOKEN_1, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        self.record(TOKEN_1, 0, 0)
        self.schedule(link_failures=NEVER)
        self.assertEqual(
            self.loaded.open_cfw_test_easylogger_async_queue_build_level_less(
                payload,
                len(payload),
                0x6A,
            ),
            0,
        )
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_diagnostic_calls"), 1)
        self.assertEqual(self.u32("open_cfw_retained_easylogger_async_free_head"), TOKEN_1)
        self.assertEqual(self.records()[1].state, 0)
        self.assertEqual(self.u32("open_cfw_test_easylogger_async_queue_free_cas_calls"), 2)
        self.assert_valid_addresses()

    def test_host_token_adapter_counts_bad_addresses_without_hiding_them(self) -> None:
        self.reset()
        self.loaded.open_cfw_test_easylogger_async_queue_probe_bad_address(TOKEN_0 + 1)
        self.loaded.open_cfw_test_easylogger_async_queue_probe_bad_address(
            TOKEN_0 + 256 * 0x110
        )
        self.assertEqual(
            self.u32("open_cfw_test_easylogger_async_queue_bad_address_count"),
            2,
        )

        self.reset(0, TOKEN_0)
        self.record(TOKEN_0, 0, 2)
        for failures, token in ((2, TOKEN_1), (4, TOKEN_2), (1, TOKEN_3)):
            self.schedule(link_failures=failures)
            self.assertEqual(
                self.loaded.open_cfw_test_easylogger_async_queue_enqueue(token),
                1,
            )
        self.assertEqual(
            (self.stats().enqueue_retry_total, self.stats().enqueue_attempt_maximum),
            (7, 5),
        )

    @staticmethod
    def decode_wide_branch(application: bytes, address: int, *, link: bool) -> int | None:
        first, second = struct.unpack_from("<HH", application, address - BASE)
        if first & 0xF800 != 0xF000:
            return None
        if second & 0xD000 != (0xD000 if link else 0x9000):
            return None
        sign = (first >> 10) & 1
        immediate_10 = first & 0x03FF
        j1 = (second >> 13) & 1
        j2 = (second >> 11) & 1
        immediate_11 = second & 0x07FF
        i1 = (~(j1 ^ sign)) & 1
        i2 = (~(j2 ^ sign)) & 1
        immediate = (
            sign << 24
            | i1 << 23
            | i2 << 22
            | immediate_10 << 12
            | immediate_11 << 1
        )
        if sign:
            immediate -= 1 << 25
        return address + 4 + immediate

    @staticmethod
    def decode_wide_conditional_branch(application: bytes, address: int) -> int | None:
        first, second = struct.unpack_from("<HH", application, address - BASE)
        if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
            return None
        condition = (first >> 6) & 0x0F
        if condition >= 0x0E:
            return None
        sign = (first >> 10) & 1
        immediate = (
            sign << 20
            | ((second >> 11) & 1) << 19
            | ((second >> 13) & 1) << 18
            | (first & 0x003F) << 12
            | (second & 0x07FF) << 1
        )
        if sign:
            immediate -= 1 << 21
        return address + 4 + immediate

    def test_official_spans_atomic_wrappers_and_global_seams_are_exact(self) -> None:
        for start, end, digest, _, _ in STOCK_RANGES.values():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(len(body), end - start)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        for (start, end), digest in ATOMIC_RANGES.items():
            body = self.application[start - BASE:end - BASE]
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)
        self.assertEqual(
            {
                address: struct.unpack_from("<I", self.application, address - BASE)[0]
                for address in (0x0044_8FB0, 0x0044_8FBC, 0x0044_8FC0)
            },
            {
                0x0044_8FB0: 0x2007_4574,
                0x0044_8FBC: 0x2007_342C,
                0x0044_8FC0: 0x2007_413C,
            },
        )
        self.assertEqual(
            self.decode_wide_branch(self.application, 0x0044_8B6C, link=True),
            0x0044_8A8E,
        )
        self.assertEqual(
            self.decode_wide_conditional_branch(self.application, 0x0043_8616),
            0x0043_8768,
        )
        callers = {target: [] for target in ATOMIC_CALLERS}
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            target = self.decode_wide_branch(self.application, address, link=True)
            if target in callers:
                callers[target].append(address)
        self.assertEqual(
            {target: tuple(sites) for target, sites in callers.items()},
            ATOMIC_CALLERS,
        )
        # The stock cluster deliberately bypasses the typed store adapter for
        # state, but uses it for next; the three adapter-to-primitive calls are
        # also exact and exhaustive.
        self.assertEqual(
            tuple(site for site in callers[0x0044_88EC] if site in range(0x0044_8A0C, 0x0044_8B96)),
            (0x0044_8A7E, 0x0044_8A9C, 0x0044_8B02),
        )
        self.assertEqual(callers[0x0044_88F4], [0x0044_893A])
        self.assertEqual(callers[0x0044_88FC], [0x0044_894A])

    def test_complete_caller_interior_and_stored_pointer_topology_is_exact(self) -> None:
        callers = {name: [] for name in STOCK_RANGES}
        entry_jumps = {name: [] for name in STOCK_RANGES}
        interiors = {name: [] for name in STOCK_RANGES}
        wide_conditional_entries = {name: [] for name in STOCK_RANGES}
        wide_conditional_interiors = {name: [] for name in STOCK_RANGES}
        for offset in range(0, len(self.application) - 3, 2):
            address = BASE + offset
            for link in (True, False):
                target = self.decode_wide_branch(self.application, address, link=link)
                if target is None:
                    continue
                for name, (start, end, _, _, _) in STOCK_RANGES.items():
                    if target == start:
                        (callers if link else entry_jumps)[name].append(address)
                    if start < target < end and not start <= address < end:
                        interiors[name].append((address, target, link))
            conditional_target = self.decode_wide_conditional_branch(
                self.application,
                address,
            )
            if conditional_target is not None:
                for name, (start, end, _, _, _) in STOCK_RANGES.items():
                    if conditional_target == start and not start <= address < end:
                        wide_conditional_entries[name].append(address)
                    if (
                        start < conditional_target < end
                        and not start <= address < end
                    ):
                        wide_conditional_interiors[name].append(
                            (address, conditional_target)
                        )

        narrow_entries = {name: [] for name in STOCK_RANGES}
        narrow_interiors = {name: [] for name in STOCK_RANGES}
        for offset in range(0, len(self.application) - 1, 2):
            address = BASE + offset
            halfword = struct.unpack_from("<H", self.application, offset)[0]
            target = None
            if halfword & 0xF800 == 0xE000:
                immediate = halfword & 0x07FF
                if immediate & 0x0400:
                    immediate -= 0x0800
                target = address + 4 + (immediate << 1)
            elif halfword & 0xF000 == 0xD000 and halfword & 0x0F00 != 0x0F00:
                immediate = halfword & 0x00FF
                if immediate & 0x0080:
                    immediate -= 0x0100
                target = address + 4 + (immediate << 1)
            elif halfword & 0xF500 == 0xB100:
                immediate = (((halfword >> 9) & 1) << 6) | (((halfword >> 3) & 0x1F) << 1)
                target = address + 4 + immediate
            if target is None:
                continue
            for name, (start, end, _, _, _) in STOCK_RANGES.items():
                if target == start and not start <= address < end:
                    narrow_entries[name].append((address, halfword))
                if start < target < end and not start <= address < end:
                    narrow_interiors[name].append((address, target, halfword))

        stored = {name: [] for name in STOCK_RANGES}
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            for name, (start, end, _, _, _) in STOCK_RANGES.items():
                if start <= (value & ~1) < end:
                    stored[name].append((BASE + offset, value))

        for name, (_, _, _, expected_callers, caller_digest) in STOCK_RANGES.items():
            self.assertEqual(tuple(callers[name]), expected_callers)
            encoded = ",".join(f"{address:08X}" for address in callers[name])
            self.assertEqual(hashlib.sha256(encoded.encode()).hexdigest(), caller_digest)
            self.assertEqual(entry_jumps[name], [])
            self.assertEqual(interiors[name], [])
            self.assertEqual(wide_conditional_entries[name], [])
            self.assertEqual(wide_conditional_interiors[name], [])
            self.assertEqual(narrow_entries[name], [])
            # 0x004488D4 is a non-instruction halfword in the preceding
            # literal/data island that decodes syntactically as a narrow
            # branch into pool initialization when every halfword is scanned.
            expected_narrow_interiors = (
                [(0x0044_88D4, 0x0044_8970, 0xDE4C)]
                if name == "pool_initialize"
                else []
            )
            self.assertEqual(narrow_interiors[name], expected_narrow_interiors)
            self.assertEqual(stored[name], [])

    def test_target_object_relocations_and_undefined_symbols_are_profile_pinned(self) -> None:
        profile = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE", "apple-clang")
        self.assertIn(profile, TARGET_PINS)
        expected = TARGET_PINS[profile]
        self.assertEqual(self.compiler_version, expected["version"])
        self.assertEqual(self.target["object"], expected["object"])
        self.assertEqual(self.target["undefined"], UNDEFINED)
        for function, (size, digest) in expected["functions"].items():
            self.assertEqual(self.target["functions"][function], (size, 4, digest))
        for function in ADAPTER_FUNCTIONS:
            self.assertEqual(
                self.target["relocations"][function],
                COMMON_RELOCATIONS[function],
            )
        self.assertEqual(self.target["relocations"][QUEUE_FUNCTIONS[0]], COMMON_RELOCATIONS[QUEUE_FUNCTIONS[0]])
        self.assertEqual(self.target["relocations"][QUEUE_FUNCTIONS[1]], expected["recycle_relocations"])
        self.assertEqual(self.target["relocations"][QUEUE_FUNCTIONS[2]], COMMON_RELOCATIONS[QUEUE_FUNCTIONS[2]])
        for function in QUEUE_FUNCTIONS[3:]:
            self.assertEqual(
                self.target["relocations"][function],
                COMMON_RELOCATIONS[function],
            )

    def test_candidate_is_not_registered_as_production_input(self) -> None:
        forbidden = (
            SOURCE.name,
            HEADER.name,
            *FUNCTIONS,
        )
        for path in (OVERLAY, MANIFEST, MAKEFILE):
            text = path.read_text()
            for token in forbidden:
                self.assertNotIn(token, text, f"{token} unexpectedly registered in {path}")

    def test_candidate_artifacts_are_fail_closed(self) -> None:
        for artifact, (size, digest) in LOCAL_PINS.items():
            body = artifact.read_bytes()
            self.assertEqual(len(body), size)
            self.assertEqual(hashlib.sha256(body).hexdigest(), digest)

    def test_fail_closed_mutations_change_authentication_or_fail_compile(self) -> None:
        start, end, digest, _, _ = STOCK_RANGES["enqueue"]
        body = bytearray(self.application[start - BASE:end - BASE])
        body[len(body) // 2] ^= 0x01
        self.assertNotEqual(hashlib.sha256(body).hexdigest(), digest)

        for (atomic_start, atomic_end), atomic_digest in ATOMIC_RANGES.items():
            atomic_body = bytearray(
                self.application[atomic_start - BASE:atomic_end - BASE]
            )
            atomic_body[len(atomic_body) // 2] ^= 0x01
            self.assertNotEqual(
                hashlib.sha256(atomic_body).hexdigest(),
                atomic_digest,
            )

        with tempfile.TemporaryDirectory() as directory:
            mutated_header = Path(directory) / HEADER.name
            mutated_source = Path(directory) / SOURCE.name
            mutated_header.write_text(
                HEADER.read_text().replace(
                    "open_cfw_easylogger_async_queue_u8 payload[256]",
                    "open_cfw_easylogger_async_queue_u8 payload[255]",
                )
            )
            mutated_source.write_text(SOURCE.read_text())
            result = subprocess.run(
                [
                    os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
                    *TARGET_FLAGS,
                    "-I",
                    directory,
                    "-c",
                    str(mutated_source),
                    "-o",
                    str(Path(directory) / "mutated.o"),
                ],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("G2 EasyLogger async", result.stderr)
            self.assertIn("offset changed", result.stderr)


if __name__ == "__main__":
    unittest.main()
