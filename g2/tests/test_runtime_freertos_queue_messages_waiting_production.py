from __future__ import annotations

import ctypes
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TASK_SOURCE = (
    ROOT / "components/shared/freertos"
    / "runtime_freertos_queue_messages_waiting.c"
)
ISR_SOURCE = (
    ROOT / "components/shared/freertos"
    / "runtime_freertos_queue_messages_waiting_from_isr.c"
)
HEADER = TASK_SOURCE.with_suffix(".h")
SOURCES = {
    "messages_waiting": TASK_SOURCE,
    "messages_waiting_from_isr": ISR_SOURCE,
}
SOURCE_PATHS = {
    key: path.relative_to(ROOT).as_posix()
    for key, path in SOURCES.items()
}
HEADER_PATH = HEADER.relative_to(ROOT).as_posix()
UPSTREAM_ROOT = ROOT / "third_party/freertos-kernel"
UPSTREAM = UPSTREAM_ROOT / "queue.c"
PROVENANCE = UPSTREAM_ROOT / "PROVENANCE.json"
VERIFIER = UPSTREAM_ROOT / "verify_snapshot.py"
OFFICIAL = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE = 32
PACKAGE_SIZE = 3_523_396
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SIZE = 3_523_364
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)
OVERLAY_RUNTIME_ADDRESS = 0x0079_4324

UPSTREAM_COMMIT = "def7d2df2b0506d3d249334974f51e427c17a41c"
UPSTREAM_TREE = "7496dfa815c3cea2f45a090c6e92d113f494b930"
UPSTREAM_QUEUE_BLOB = "5c872e0302839d96aab90919788fdc2b0be1c09e"
UPSTREAM_SIZE = 125_614
UPSTREAM_SHA256 = (
    "5cdf4fa35fe059446effff5bf20deaf83"
    "ddffb08921bc198fda106b1d17dd894"
)
UPSTREAM_FUNCTIONS = {
    "messages_waiting": {
        "marker": b"UBaseType_t uxQueueMessagesWaiting( const QueueHandle_t xQueue )",
        "size": 286,
        "sha256": (
            "c1bd9900ed75941a9ea7f0b822c3555e"
            "c9b16e7f813bd7ddc28c6466e0c1b898"
        ),
    },
    "messages_waiting_from_isr": {
        "marker": (
            b"UBaseType_t uxQueueMessagesWaitingFromISR( "
            b"const QueueHandle_t xQueue )"
        ),
        "size": 243,
        "sha256": (
            "601fcf52884f23a83aec6a516e2f6b1d"
            "f7dabd03ac75f7719e568b025f3b1c79"
        ),
    },
}

FUNCTIONS = {
    "messages_waiting": {
        "symbol": "open_cfw_freertos_queue_messages_waiting",
        "start": 0x0044_1E66,
        "end": 0x0044_1E8A,
        "stock": bytes.fromhex(
            "10b50400002c06d1b8f119f900205ff0ff310860fee7"
            "00f028f9a46b00f031f9200010bd"
        ),
        "stock_sha256": (
            "4c0cf73877126df740ed1609ef221c63c"
            "694ccf47722984a938758e88db42c94"
        ),
        "callers": [
            (0x0044_9A2C, "f8f71bfa"),
            (0x0044_9BE6, "f8f73ef9"),
            (0x0044_9E5E, "f8f702f8"),
        ],
        "caller_address_sha256": (
            "47610a67315bf7a91b9e9a25d57738f"
            "300c6bea9a67b5d5b58413410e67e968f"
        ),
        "caller_encoding_sha256": (
            "53cc949463fe456c1981a74a08ec6e7a"
            "24dcbd8d430a6e4d9b426e250e45c4e7"
        ),
        "outgoing": [
            (0x0044_1E6E, "b8f119f9", 0x005F_A0A4),
            (0x0044_1E7C, "00f028f9", 0x0044_20D0),
            (0x0044_1E82, "00f031f9", 0x0044_20E8),
        ],
        "patch_name": "replace_freertos_queue_messages_waiting",
    },
    "messages_waiting_from_isr": {
        "symbol": "open_cfw_freertos_queue_messages_waiting_from_isr",
        "start": 0x0044_1E8A,
        "end": 0x0044_1EA2,
        "stock": bytes.fromhex(
            "80b5002806d1b8f108f900205ff0ff310860fee7806b02bd"
        ),
        "stock_sha256": (
            "669d2bc894a3f8dd00002713748a6c6a"
            "67409355d12893e0a854e06fa45d5dba"
        ),
        "callers": [
            (0x0044_9A24, "f8f731fa"),
            (0x0044_9BDE, "f8f754f9"),
            (0x0044_9E1C, "f8f735f8"),
        ],
        "caller_address_sha256": (
            "81d0972b79cf47d89e7839d7faac9bd1"
            "e5d3e9e28c764637237ebf4805ee2ff2"
        ),
        "caller_encoding_sha256": (
            "1a0af63638aadeddc54a2196edfacbefe"
            "9074197663187dcfb5014171488cb78"
        ),
        "outgoing": [
            (0x0044_1E90, "b8f108f9", 0x005F_A0A4),
        ],
        "patch_name": "replace_freertos_queue_messages_waiting_from_isr",
    },
}

PREDECESSOR = (
    0x0044_1DA6,
    0x0044_1E66,
    192,
    "cd084580c8e0eededc50eef8fa544290e2c09df64d3ec1e1bf1bbe13bdeb25c4",
)
SUCCESSOR = (
    0x0044_1EA2,
    0x0044_1EC4,
    34,
    "ab55f9fa6eb823935056d4b4030cc10df52bc8b33318abea201e61348a026bc4",
)
INGRESS_PAIRS = (
    (0x0044_9A24, 0x0044_9A2C),
    (0x0044_9BDE, 0x0044_9BE6),
    (0x0044_9E1C, 0x0044_9E5E),
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
    "-fno-ident",
]
EXIDX = bytes.fromhex("0000000001000000")
EXIDX_SHA256 = (
    "01acecb507abfe1a354aa8064f4af5d3"
    "f1acd019e37db3c11c97523b71c76e9d"
)

# RECORD-PIN GATE: these values are intentionally absent until the final
# source/header and compile-twice objects have been reviewed.  Leaving any
# entry as None makes the production suite fail rather than accepting moving
# source or toolchain output.
LOCAL_PINS: dict[Path, tuple[int, str] | None] = {
    TASK_SOURCE: (
        2118,
        "a5ddb8530031a4510abb894b082c229725f66b3e5f4e1ff72c34137362854a04",
    ),
    ISR_SOURCE: (
        2067,
        "a73ed32264681fadabbe10dce300388bd0f9fa8821334eba2a8b65b0ff327d34",
    ),
    HEADER: (
        7042,
        "393d1cdd116fd8f71fabebda73a05eb8a520dc5c0e2916ca4197df9a1e4aab0c",
    ),
}
OBJECT_PINS: dict[str, dict[str, object]] = {
    "apple-clang": {
        "compiler": "/usr/bin/clang",
        "version": "Apple clang version 21.0.0 (clang-2100.3.30.1)",
        "object": {
            "messages_waiting": (
                852,
                "24c8d8a8311ad6a094b0e92e048b0324320002d9d850441887b05ececbcc0453",
            ),
            "messages_waiting_from_isr": (
                856,
                "a69c13094a7f4afcc65f48e660ccd09293a5409b6ec94f278eab9635c31139a7",
            ),
        },
        "text": {
            "messages_waiting": (
                50,
                "b0b558b142f2d105c0f244050446a847a46b05f1180080472046b0bd4af2a500c0f25f0080474ff0ff300021016000bffee7",
                "fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04",
            ),
            "messages_waiting_from_isr": (
                34,
                "00281cbf806b704780b54af2a500c0f25f0080474ff0ff3000210160bde88040fee7",
                "38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c",
            ),
        },
    },
    "linux-clang": {
        "compiler": "/home/linuxbrew/.linuxbrew/bin/clang",
        "version": "Homebrew clang version 22.1.8",
        "object": {
            "messages_waiting": (
                852,
                "24c8d8a8311ad6a094b0e92e048b0324320002d9d850441887b05ececbcc0453",
            ),
            "messages_waiting_from_isr": (
                856,
                "a69c13094a7f4afcc65f48e660ccd09293a5409b6ec94f278eab9635c31139a7",
            ),
        },
        "text": {
            "messages_waiting": (
                50,
                "b0b558b142f2d105c0f244050446a847a46b05f1180080472046b0bd4af2a500c0f25f0080474ff0ff300021016000bffee7",
                "fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04",
            ),
            "messages_waiting_from_isr": (
                34,
                "00281cbf806b704780b54af2a500c0f25f0080474ff0ff3000210160bde88040fee7",
                "38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c",
            ),
        },
    },
}

# RECORD-PIN GATE: fill only from isolated deterministic production builds.
# Patch bytes depend on the placed runtime addresses and aggregate pins depend
# on all concurrently approved leaves, so none are inferred here.
PROFILE_PINS: dict[str, dict[str, object]] = {
    "apple-clang": {
        "placements": {
            "messages_waiting": 124212,
            "messages_waiting_from_isr": 124264,
        },
        "relocated_sha256": {
            "messages_waiting": "fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04",
            "messages_waiting_from_isr": "38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c",
        },
        "patch": {
            "messages_waiting": (
                "70f3f7bc00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
                "8b1f7a72f4e021331a04cd81707ea2cfa85712c8cf637ff3f7365c62ab5c54d2",
            ),
            "messages_waiting_from_isr": (
                "70f3ffbc00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
                "bd3b32c736e57005c1cbe65a2725fb66ed5389227686ff7961793f699364e68c",
            ),
        },
        "overlay": (165412, "91449e27a73806e1537548657bed4486d77b275e4ee8a58b2bb1ef527c252ada"),
        "component": (3688808, "9b2424332183f3415b0e2a745e22c7f1b9b0721fcfeaed074272de67d760068c"),
        "package": (4467302, "88e7242268d2a5472e4c96e740dff637214940b5aa88f043bac29500eeb63d3f"),
    },
    "linux-clang": {
        "placements": {
            "messages_waiting": 126032,
            "messages_waiting_from_isr": 126084,
        },
        "relocated_sha256": {
            "messages_waiting": "fd95750405881458902725fe3e29d72367bcfe3a723a05588c74337b55202f04",
            "messages_waiting_from_isr": "38774f1d59f2cd201929d20c3370e12e167d24866477e5a661220bca25db834c",
        },
        "patch": {
            "messages_waiting": (
                "71f385b800bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
                "0dd88ba663317edbf9a515397f3369d4221f25889551189ff70a5b8bb68067d6",
            ),
            "messages_waiting_from_isr": (
                "71f38db800bf00bf00bf00bf00bf00bf00bf00bf00bf00bf",
                "2ef6ffe002ec6b197643da1304921bbc422dc9beb124b23343f16bf187e303a1",
            ),
        },
        "overlay": (145180, "afbcb57a8414e65a18c6c95396a0f32fe454cb2087e6a03d51717196a4854b57"),
        "component": (3668576, "292f55478951dc8d41a8bc5e4cc01f80ae88f9c44350d8fec89958c939a4fac5"),
        "package": (4447070, "be5c62a97b9d31f4df257615c28ce81d79ab186feadb68262f96ac5bc35a1c25"),
    },
}

# RECORD-PIN GATE: (region_count, {address_status: (count, total_size)}).
MANIFEST_PIN: tuple[int, dict[str, tuple[int, int]]] | None = (
    1745,
    {
        "container_only": (1, 32),
    "generated_alignment": (182, 366),
    "generated_source_entry_replacement": (842, 118_700),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (265, 3_404_306),
    "source_compiled": (437, 164_764),
    },
)


def sha256(value: bytes | Path) -> str:
    if isinstance(value, Path):
        value = value.read_bytes()
    return hashlib.sha256(value).hexdigest()


def extract_c_function(source: bytes, marker: bytes) -> bytes:
    start = source.index(marker)
    opening = source.index(b"{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index:index + 1] == b"{":
            depth += 1
        elif source[index:index + 1] == b"}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise AssertionError(f"unterminated function at {marker!r}")


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


def wide_conditional_target(
    address: int,
    first: int,
    second: int,
) -> int | None:
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x8000:
        return None
    if ((first >> 6) & 0x0F) >= 0x0E:
        return None
    sign = (first >> 10) & 1
    immediate = (
        (sign << 20)
        | (((second >> 11) & 1) << 19)
        | (((second >> 13) & 1) << 18)
        | ((first & 0x003F) << 12)
        | ((second & 0x07FF) << 1)
    )
    if sign:
        immediate -= 1 << 21
    return address + 4 + immediate


def required_pin(value: object, label: str) -> object:
    if value is None:
        raise AssertionError(
            f"unrecorded production pin {label}; fill it only from the "
            "reviewed isolated build"
        )
    return value


def host_source() -> str:
    return r'''
#include <setjmp.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

enum {
    OPEN_CFW_HOST_EVENT_ASSERT = 1,
    OPEN_CFW_HOST_EVENT_ENTER = 2,
    OPEN_CFW_HOST_EVENT_EXIT = 3
};

static jmp_buf open_cfw_host_trap;
static uint32_t open_cfw_host_events[8];
static uint32_t open_cfw_host_event_count;
static uint32_t open_cfw_host_enter_calls;
static uint32_t open_cfw_host_exit_calls;
static uint32_t open_cfw_host_depth;
static uint32_t open_cfw_host_max_depth;
static uint32_t open_cfw_host_mutate_enter;
static uint32_t open_cfw_host_enter_value;
static uint32_t open_cfw_host_mutate_exit;
static uint32_t open_cfw_host_exit_value;

static void open_cfw_host_record(uint32_t event) {
    if (open_cfw_host_event_count < 8U) {
        open_cfw_host_events[open_cfw_host_event_count] = event;
    }
    open_cfw_host_event_count++;
}

static void open_cfw_host_assert(int condition);
static void open_cfw_host_enter(void);
static void open_cfw_host_exit(void);

#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT(condition) \
    open_cfw_host_assert((condition))
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL() \
    open_cfw_host_enter()
#define OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL() \
    open_cfw_host_exit()
#include "components/shared/freertos/runtime_freertos_queue_messages_waiting.c"
#include "components/shared/freertos/runtime_freertos_queue_messages_waiting_from_isr.c"

static struct open_cfw_freertos_queue_messages_control open_cfw_host_queue;

struct open_cfw_host_result {
    uint32_t value;
    uint32_t trapped;
    uint32_t event_count;
    uint32_t events[8];
    uint32_t enter_calls;
    uint32_t exit_calls;
    uint32_t depth;
    uint32_t max_depth;
    uint32_t final_messages;
    uint32_t checksum;
};

static void open_cfw_host_assert(int condition) {
    open_cfw_host_record(OPEN_CFW_HOST_EVENT_ASSERT);
    if (!condition) {
        longjmp(open_cfw_host_trap, 1);
    }
}

static void open_cfw_host_enter(void) {
    open_cfw_host_record(OPEN_CFW_HOST_EVENT_ENTER);
    open_cfw_host_enter_calls++;
    open_cfw_host_depth++;
    if (open_cfw_host_depth > open_cfw_host_max_depth) {
        open_cfw_host_max_depth = open_cfw_host_depth;
    }
    if (open_cfw_host_mutate_enter) {
        open_cfw_host_queue.messages_waiting = open_cfw_host_enter_value;
    }
}

static void open_cfw_host_exit(void) {
    if (open_cfw_host_mutate_exit) {
        open_cfw_host_queue.messages_waiting = open_cfw_host_exit_value;
    }
    open_cfw_host_exit_calls++;
    if (open_cfw_host_depth > 0U) {
        open_cfw_host_depth--;
    }
    open_cfw_host_record(OPEN_CFW_HOST_EVENT_EXIT);
}

static uint32_t open_cfw_host_checksum(void) {
    const unsigned char *bytes = (const unsigned char *)&open_cfw_host_queue;
    uint32_t value = 2166136261U;
    size_t index;
    for (index = 0; index < sizeof(open_cfw_host_queue); index++) {
        value ^= bytes[index];
        value *= 16777619U;
    }
    return value;
}

static uint32_t open_cfw_host_oracle(
    int from_isr,
    const struct open_cfw_freertos_queue_messages_control *queue
) {
    uint32_t result;
    open_cfw_host_assert(queue != 0);
    if (from_isr) {
        result = queue->messages_waiting;
    } else {
        open_cfw_host_enter();
        result = queue->messages_waiting;
        open_cfw_host_exit();
    }
    return result;
}

void open_cfw_host_run(
    int use_candidate,
    int from_isr,
    int null_queue,
    uint32_t initial,
    uint32_t mutate_enter,
    uint32_t enter_value,
    uint32_t mutate_exit,
    uint32_t exit_value,
    struct open_cfw_host_result *result
) {
    const struct open_cfw_freertos_queue_messages_control *queue;
    uint32_t trapped = 0U;

    memset(&open_cfw_host_queue, 0xA5, sizeof(open_cfw_host_queue));
    open_cfw_host_queue.messages_waiting = initial;
    memset(open_cfw_host_events, 0, sizeof(open_cfw_host_events));
    open_cfw_host_event_count = 0U;
    open_cfw_host_enter_calls = 0U;
    open_cfw_host_exit_calls = 0U;
    open_cfw_host_depth = 0U;
    open_cfw_host_max_depth = 0U;
    open_cfw_host_mutate_enter = mutate_enter;
    open_cfw_host_enter_value = enter_value;
    open_cfw_host_mutate_exit = mutate_exit;
    open_cfw_host_exit_value = exit_value;
    queue = null_queue ? 0 : &open_cfw_host_queue;
    memset(result, 0, sizeof(*result));

    if (setjmp(open_cfw_host_trap) == 0) {
        if (use_candidate) {
            result->value = from_isr
                ? open_cfw_freertos_queue_messages_waiting_from_isr(queue)
                : open_cfw_freertos_queue_messages_waiting(queue);
        } else {
            result->value = open_cfw_host_oracle(from_isr, queue);
        }
    } else {
        trapped = 1U;
    }

    result->trapped = trapped;
    result->event_count = open_cfw_host_event_count;
    memcpy(result->events, open_cfw_host_events, sizeof(result->events));
    result->enter_calls = open_cfw_host_enter_calls;
    result->exit_calls = open_cfw_host_exit_calls;
    result->depth = open_cfw_host_depth;
    result->max_depth = open_cfw_host_max_depth;
    result->final_messages = open_cfw_host_queue.messages_waiting;
    result->checksum = open_cfw_host_checksum();
}

size_t open_cfw_host_queue_size(void) {
    return sizeof(open_cfw_host_queue);
}

size_t open_cfw_host_messages_offset(void) {
    return offsetof(
        struct open_cfw_freertos_queue_messages_control,
        messages_waiting
    );
}
'''


class QueueList32(ctypes.Structure):
    _fields_ = [
        ("item_count", ctypes.c_uint32),
        ("remainder", ctypes.c_uint8 * 16),
    ]


class QueueValue32(ctypes.Union):
    _fields_ = [("words", ctypes.c_uint32 * 2)]


class QueueControl32(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_uint32),
        ("write_to", ctypes.c_uint32),
        ("value", QueueValue32),
        ("tasks_waiting_to_send", QueueList32),
        ("tasks_waiting_to_receive", QueueList32),
        ("messages_waiting", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("item_size", ctypes.c_uint32),
        ("receive_lock", ctypes.c_int8),
        ("transmit_lock", ctypes.c_int8),
        ("statically_allocated", ctypes.c_uint8),
        ("allocation_padding", ctypes.c_uint8),
        ("queue_number", ctypes.c_uint32),
        ("queue_type", ctypes.c_uint8),
        ("trace_padding", ctypes.c_uint8 * 3),
    ]


class QueueValueNative(ctypes.Union):
    _fields_ = [("pointers", ctypes.c_void_p * 2)]


class QueueControlNative(ctypes.Structure):
    _fields_ = [
        ("head", ctypes.c_void_p),
        ("write_to", ctypes.c_void_p),
        ("value", QueueValueNative),
        ("tasks_waiting_to_send", QueueList32),
        ("tasks_waiting_to_receive", QueueList32),
        ("messages_waiting", ctypes.c_uint32),
        ("length", ctypes.c_uint32),
        ("item_size", ctypes.c_uint32),
        ("receive_lock", ctypes.c_int8),
        ("transmit_lock", ctypes.c_int8),
        ("statically_allocated", ctypes.c_uint8),
        ("allocation_padding", ctypes.c_uint8),
        ("queue_number", ctypes.c_uint32),
        ("queue_type", ctypes.c_uint8),
        ("trace_padding", ctypes.c_uint8 * 3),
    ]


class HostResult(ctypes.Structure):
    _fields_ = [
        ("value", ctypes.c_uint32),
        ("trapped", ctypes.c_uint32),
        ("event_count", ctypes.c_uint32),
        ("events", ctypes.c_uint32 * 8),
        ("enter_calls", ctypes.c_uint32),
        ("exit_calls", ctypes.c_uint32),
        ("depth", ctypes.c_uint32),
        ("max_depth", ctypes.c_uint32),
        ("final_messages", ctypes.c_uint32),
        ("checksum", ctypes.c_uint32),
    ]

    def tuple(self) -> tuple[object, ...]:
        return (
            self.value,
            self.trapped,
            self.event_count,
            tuple(self.events),
            self.enter_calls,
            self.exit_calls,
            self.depth,
            self.max_depth,
            self.final_messages,
            self.checksum,
        )


class RuntimeFreeRTOSQueueMessagesWaitingProductionTests(unittest.TestCase):
    maxDiff = None

    @classmethod
    def setUpClass(cls) -> None:
        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.apollo_overlay = apollo_overlay
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE:]

        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        matches = [
            name for name, pins in OBJECT_PINS.items()
            if (cls.clang, version) == (pins["compiler"], pins["version"])
        ]
        if len(matches) != 1:
            raise AssertionError(f"unreviewed compiler: {(cls.clang, version)!r}")
        cls.profile = matches[0]

        temporary_parent = ROOT / "build"
        temporary_parent.mkdir(parents=True, exist_ok=True)
        cls.temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-queue-messages-production-",
            dir=temporary_parent,
        )
        temporary = Path(cls.temporary.name)

        cls.objects = {
            key: [
                temporary / f"{key}-a.o",
                temporary / f"{key}-b.o",
            ]
            for key in FUNCTIONS
        }
        for key, outputs in cls.objects.items():
            for output in outputs:
                subprocess.run(
                    [
                        cls.clang,
                        *TARGET_FLAGS,
                        "-c",
                        SOURCE_PATHS[key],
                        "-o",
                        str(output),
                    ],
                    cwd=ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )

        host = temporary / "queue-messages-host.c"
        host.write_text(host_source(), encoding="utf-8")
        library = temporary / (
            "queue-messages-host.dylib"
            if sys.platform == "darwin"
            else "queue-messages-host.so"
        )
        command = [
            cls.clang,
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-I",
            str(ROOT),
            str(host),
        ]
        if sys.platform == "darwin":
            command.extend(("-dynamiclib", "-o", str(library)))
        else:
            command.extend(("-shared", "-fPIC", "-o", str(library)))
        subprocess.run(command, check=True, capture_output=True, text=True)
        cls.host = ctypes.CDLL(str(library))
        cls.host_run = cls.host.open_cfw_host_run
        cls.host_run.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.POINTER(HostResult),
        ]
        cls.host_run.restype = None
        cls.host_queue_size = cls.host.open_cfw_host_queue_size
        cls.host_queue_size.argtypes = []
        cls.host_queue_size.restype = ctypes.c_size_t
        cls.host_messages_offset = cls.host.open_cfw_host_messages_offset
        cls.host_messages_offset.argtypes = []
        cls.host_messages_offset.restype = ctypes.c_size_t

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def span(self, start: int, end: int) -> bytes:
        return self.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def run_host(
        self,
        use_candidate: int,
        from_isr: int,
        null_queue: int,
        initial: int,
        mutate_enter: int,
        enter_value: int,
        mutate_exit: int,
        exit_value: int,
    ) -> HostResult:
        result = HostResult()
        self.host_run(
            use_candidate,
            from_isr,
            null_queue,
            initial,
            mutate_enter,
            enter_value,
            mutate_exit,
            exit_value,
            ctypes.byref(result),
        )
        return result

    def parse_object(
        self,
        path: Path,
    ) -> tuple[bytes, list[dict[str, object]], list[dict[str, object]]]:
        data, sections = self.apollo_overlay.parse_elf32(path)
        symbols = self.apollo_overlay.parse_elf32_symbols(data, sections)
        return data, sections, symbols

    def test_record_pins_are_complete_and_local_source_is_exact(self) -> None:
        for path, pin in LOCAL_PINS.items():
            with self.subTest(path=path.relative_to(ROOT)):
                size, digest = required_pin(
                    pin,
                    f"LOCAL_PINS[{path.relative_to(ROOT)}]",
                )
                self.assertEqual(path.stat().st_size, size)
                self.assertEqual(sha256(path), digest)

        profile = OBJECT_PINS[self.profile]
        for key, paths in self.objects.items():
            object_size, object_hash = required_pin(
                profile["object"][key],
                f"OBJECT_PINS[{self.profile}].object[{key}]",
            )
            for path in paths:
                self.assertEqual(path.stat().st_size, object_size)
                self.assertEqual(sha256(path), object_hash)
            self.assertEqual(paths[0].read_bytes(), paths[1].read_bytes())

    def test_authenticated_upstream_bodies_license_and_configuration_are_exact(
        self,
    ) -> None:
        upstream = UPSTREAM.read_bytes()
        self.assertEqual(len(upstream), UPSTREAM_SIZE)
        self.assertEqual(sha256(upstream), UPSTREAM_SHA256)
        for key, contract in UPSTREAM_FUNCTIONS.items():
            with self.subTest(function=key):
                body = extract_c_function(upstream, contract["marker"])
                self.assertEqual(len(body), contract["size"])
                self.assertEqual(sha256(body), contract["sha256"])

        provenance = json.loads(PROVENANCE.read_text(encoding="utf-8"))
        self.assertEqual(provenance["license"], "MIT")
        self.assertEqual(provenance["upstream"]["selected_tag"], "V10.5.1")
        self.assertEqual(
            provenance["upstream"]["selected_commit"],
            UPSTREAM_COMMIT,
        )
        self.assertEqual(provenance["upstream"]["selected_tree"], UPSTREAM_TREE)
        self.assertEqual(
            provenance["files"]["queue.c"],
            {
                "size": UPSTREAM_SIZE,
                "sha256": UPSTREAM_SHA256,
                "git_blob_sha1": UPSTREAM_QUEUE_BLOB,
            },
        )
        verification = subprocess.run(
            [sys.executable, str(VERIFIER)],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("FreeRTOS-Kernel V10.5.1", verification.stdout)
        self.assertIn("Git blobs", verification.stdout)

        sources = {
            key: path.read_text(encoding="utf-8")
            for key, path in SOURCES.items()
        }
        source = "\n".join(sources.values())
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "Copyright (C) 2021 Amazon.com, Inc. or its affiliates.",
            "SPDX-License-Identifier: MIT",
            "Permission is hereby granted, free of charge",
            UPSTREAM_COMMIT,
            "uxQueueMessagesWaiting()",
            "uxQueueMessagesWaitingFromISR()",
            "[0x00441E66, 0x00441E8A)",
            "[0x00441E8A, 0x00441EA2)",
            "result = queue->messages_waiting;",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT_MASK_ADDRESS = 0x005FA0A4U",
            "OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ENTER_CRITICAL_ADDRESS = 0x004420D0U",
            "OPEN_CFW_FREERTOS_QUEUE_MESSAGES_EXIT_CRITICAL_ADDRESS = 0x004420E8U",
            "OPEN_CFW_FREERTOS_QUEUE_MESSAGES_QUEUE_SIZE = 0x50U",
            "messages_waiting\n    ) == 0x38U",
            "OPEN_CFW_FREERTOS_QUEUE_MESSAGES_ASSERT(queue != 0)",
        ):
            self.assertIn(token, header + source)
        self.assertIn(f'#include "{HEADER.name}"', source)
        self.assertNotIn("research/candidates", source + header)
        self.assertIn(
            "open_cfw_freertos_queue_messages_waiting(",
            sources["messages_waiting"],
        )
        self.assertNotIn(
            "open_cfw_freertos_queue_messages_waiting_from_isr(",
            sources["messages_waiting"],
        )
        self.assertIn(
            "open_cfw_freertos_queue_messages_waiting_from_isr(",
            sources["messages_waiting_from_isr"],
        )
        self.assertNotIn(
            "open_cfw_freertos_queue_messages_waiting(\n",
            sources["messages_waiting_from_isr"],
        )

    def test_recovered_queue_abi_is_exact_in_host_and_source(self) -> None:
        self.assertEqual(ctypes.sizeof(QueueList32), 0x14)
        self.assertEqual(ctypes.sizeof(QueueControl32), 0x50)
        self.assertEqual(QueueControl32.tasks_waiting_to_send.offset, 0x10)
        self.assertEqual(QueueControl32.tasks_waiting_to_receive.offset, 0x24)
        self.assertEqual(QueueControl32.messages_waiting.offset, 0x38)
        self.assertEqual(QueueControl32.length.offset, 0x3C)
        self.assertEqual(QueueControl32.item_size.offset, 0x40)
        self.assertEqual(QueueControl32.receive_lock.offset, 0x44)
        self.assertEqual(QueueControl32.transmit_lock.offset, 0x45)
        self.assertEqual(QueueControl32.statically_allocated.offset, 0x46)
        self.assertEqual(QueueControl32.queue_number.offset, 0x48)
        self.assertEqual(QueueControl32.queue_type.offset, 0x4C)
        self.assertEqual(self.host_queue_size(), ctypes.sizeof(QueueControlNative))
        self.assertEqual(
            self.host_messages_offset(),
            QueueControlNative.messages_waiting.offset,
        )

    def test_candidate_matches_independent_oracle_and_critical_order(self) -> None:
        cases = [
            (0, 0, 0, 0),
            (1, 0, 0, 0),
            (0x7FFF_FFFF, 0, 0, 0),
            (0x8000_0000, 0, 0, 0),
            (0xFFFF_FFFF, 0, 0, 0),
            (0x1234_5678, 1, 0x8765_4321, 0),
            (0x1234_5678, 0, 0, 1),
            (0x1234_5678, 1, 0x8765_4321, 1),
        ]
        state = 0xC001_D00D
        for _ in range(128):
            state = (1664525 * state + 1013904223) & 0xFFFF_FFFF
            cases.append((state, state & 1, state ^ 0xA5A5_A5A5, (state >> 1) & 1))

        for from_isr in (0, 1):
            for initial, mutate_enter, enter_value, mutate_exit in cases:
                exit_value = initial ^ 0x5A5A_5A5A
                with self.subTest(
                    from_isr=from_isr,
                    initial=initial,
                    mutate_enter=mutate_enter,
                    mutate_exit=mutate_exit,
                ):
                    actual = self.run_host(
                        1,
                        from_isr,
                        0,
                        initial,
                        mutate_enter,
                        enter_value,
                        mutate_exit,
                        exit_value,
                    )
                    expected = self.run_host(
                        0,
                        from_isr,
                        0,
                        initial,
                        mutate_enter,
                        enter_value,
                        mutate_exit,
                        exit_value,
                    )
                    self.assertEqual(actual.tuple(), expected.tuple())
                    if from_isr:
                        self.assertEqual(actual.value, initial)
                        self.assertEqual(actual.event_count, 1)
                        self.assertEqual(tuple(actual.events[:1]), (1,))
                        self.assertEqual((actual.enter_calls, actual.exit_calls), (0, 0))
                        self.assertEqual(actual.final_messages, initial)
                    else:
                        sampled = enter_value if mutate_enter else initial
                        final = exit_value if mutate_exit else sampled
                        self.assertEqual(actual.value, sampled)
                        self.assertEqual(actual.event_count, 3)
                        self.assertEqual(tuple(actual.events[:3]), (1, 2, 3))
                        self.assertEqual((actual.enter_calls, actual.exit_calls), (1, 1))
                        self.assertEqual((actual.depth, actual.max_depth), (0, 1))
                        self.assertEqual(actual.final_messages, final)

    def test_null_queue_asserts_before_load_or_critical_entry(self) -> None:
        for from_isr in (0, 1):
            actual = self.run_host(1, from_isr, 1, 0x1234, 1, 0x5678, 1, 0x9ABC)
            expected = self.run_host(0, from_isr, 1, 0x1234, 1, 0x5678, 1, 0x9ABC)
            with self.subTest(from_isr=from_isr):
                self.assertEqual(actual.tuple(), expected.tuple())
                self.assertEqual(actual.trapped, 1)
                self.assertEqual(actual.event_count, 1)
                self.assertEqual(tuple(actual.events[:1]), (1,))
                self.assertEqual((actual.enter_calls, actual.exit_calls), (0, 0))
                self.assertEqual(actual.final_messages, 0x1234)

    def test_target_object_sections_symbols_and_zero_relocations_are_exact(self) -> None:
        object_pin = OBJECT_PINS[self.profile]
        for key, contract in FUNCTIONS.items():
            for object_path in self.objects[key]:
                data, sections, symbols = self.parse_object(object_path)
                sections_by_name = {
                    str(section["name"]): section for section in sections
                }
                symbols_by_name = {
                    str(symbol["name"]): symbol
                    for symbol in symbols
                    if symbol["name"]
                }
                undefined = sorted(
                    str(symbol["name"])
                    for symbol in symbols
                    if symbol["name"] and int(symbol["section_index"]) == 0
                )
                self.assertEqual(undefined, [])

                symbol_name = contract["symbol"]
                section_name = ".text." + symbol_name
                executable_sections = [
                    str(section["name"])
                    for section in sections
                    if int(section["size"])
                    and int(section["flags"]) & 2
                    and int(section["flags"]) & 4
                ]
                self.assertEqual(executable_sections, [section_name])
                section = sections_by_name[section_name]
                text = data[
                    int(section["offset"]):
                    int(section["offset"]) + int(section["size"])
                ]
                text_size, text_hex, text_hash = required_pin(
                    object_pin["text"][key],
                    f"OBJECT_PINS[{self.profile}].text[{key}]",
                )
                self.assertEqual((len(text), text.hex(), sha256(text)), (
                    text_size,
                    text_hex,
                    text_hash,
                ))
                self.assertEqual(int(section["alignment"]), 4)
                self.assertEqual(int(section["flags"]) & 7, 6)

                symbol = symbols_by_name[symbol_name]
                self.assertEqual(int(symbol["binding"]), 1)
                self.assertEqual(int(symbol["type"]), 2)
                self.assertEqual(int(symbol["size"]), len(text))
                self.assertEqual(int(symbol["value"]) & ~1, 0)
                self.assertEqual(int(symbol["value"]) & 1, 1)

                relocations: list[tuple[int, int, str]] = []
                exidx_relocations: list[tuple[int, int, str]] = []
                for relocation_section in sections:
                    if int(relocation_section["type"]) != 9:
                        continue
                    target = sections[int(relocation_section["info"])]
                    if target["name"] not in (section_name, ".ARM.exidx" + section_name):
                        continue
                    symbol_table = sections[int(relocation_section["link"])]
                    string_table = sections[int(symbol_table["link"])]
                    strings = data[
                        int(string_table["offset"]):
                        int(string_table["offset"]) + int(string_table["size"])
                    ]
                    parsed_symbols: list[str] = []
                    for index in range(int(symbol_table["size"]) // 16):
                        name_offset = struct.unpack_from(
                            "<I",
                            data,
                            int(symbol_table["offset"]) + 16 * index,
                        )[0]
                        parsed_symbols.append(
                            self.apollo_overlay.elf_string(strings, name_offset, "symbol")
                        )
                    for index in range(int(relocation_section["size"]) // 8):
                        offset, information = struct.unpack_from(
                            "<II",
                            data,
                            int(relocation_section["offset"]) + 8 * index,
                        )
                        record = (
                            offset,
                            information & 0xFF,
                            parsed_symbols[information >> 8],
                        )
                        if target["name"] == section_name:
                            relocations.append(record)
                        else:
                            exidx_relocations.append(record)
                self.assertEqual(relocations, [])
                self.assertEqual(exidx_relocations, [(0, 42, "")])
                exidx = sections_by_name[".ARM.exidx" + section_name]
                exidx_bytes = data[
                    int(exidx["offset"]):
                    int(exidx["offset"]) + int(exidx["size"])
                ]
                self.assertEqual(exidx_bytes, EXIDX)
                self.assertEqual(sha256(exidx_bytes), EXIDX_SHA256)

                sibling_symbols = {
                    item["symbol"] for sibling_key, item in FUNCTIONS.items()
                    if sibling_key != key
                }
                self.assertTrue(sibling_symbols.isdisjoint(symbols_by_name))
                for candidate_section in sections:
                    name = str(candidate_section["name"])
                    if name.startswith((".data", ".rodata")):
                        self.assertEqual(int(candidate_section["size"]), 0, name)

    def test_official_spans_neighbors_callers_ingress_and_references_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), PACKAGE_SIZE)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(len(self.application), APPLICATION_SIZE)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)

        for key, contract in FUNCTIONS.items():
            body = self.span(contract["start"], contract["end"])
            with self.subTest(function=key):
                self.assertEqual(body, contract["stock"])
                self.assertEqual(sha256(body), contract["stock_sha256"])

        for start, end, size, digest in (PREDECESSOR, SUCCESSOR):
            body = self.span(start, end)
            self.assertEqual(len(body), size)
            self.assertEqual(sha256(body), digest)

        callers = {key: [] for key in FUNCTIONS}
        jumps = {key: [] for key in FUNCTIONS}
        interiors = {key: [] for key in FUNCTIONS}
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
                for key, contract in FUNCTIONS.items():
                    if target == contract["start"]:
                        (callers if link else jumps)[key].append(
                            (address, encoded.hex())
                        )
                    if (
                        contract["start"] < target < contract["end"]
                        and not contract["start"] <= address < contract["end"]
                    ):
                        interiors[key].append((address, target, link, encoded.hex()))

        for key, contract in FUNCTIONS.items():
            self.assertEqual(callers[key], contract["callers"])
            self.assertEqual(jumps[key], [])
            self.assertEqual(interiors[key], [])
            self.assertEqual(
                sha256(b"".join(struct.pack("<I", item[0]) for item in callers[key])),
                contract["caller_address_sha256"],
            )
            self.assertEqual(
                sha256(b"".join(bytes.fromhex(item[1]) for item in callers[key])),
                contract["caller_encoding_sha256"],
            )

        self.assertEqual(
            tuple(
                (
                    FUNCTIONS["messages_waiting_from_isr"]["callers"][index][0],
                    FUNCTIONS["messages_waiting"]["callers"][index][0],
                )
                for index in range(3)
            ),
            INGRESS_PAIRS,
        )

        conditional_or_narrow: list[tuple[int, int, str]] = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from("<HH", self.application, offset)
            conditional = wide_conditional_target(address, first, second)
            targets = (
                *((conditional,) if conditional is not None else ()),
                *narrow_branch_targets(address, first),
            )
            for target in targets:
                for key, contract in FUNCTIONS.items():
                    if (
                        contract["start"] <= target < contract["end"]
                        and not contract["start"] <= address < contract["end"]
                    ):
                        conditional_or_narrow.append((address, target, key))
        self.assertEqual(conditional_or_narrow, [])

        stored: list[tuple[int, int, str]] = []
        for offset in range(0, len(self.application) - 3):
            value = struct.unpack_from("<I", self.application, offset)[0]
            canonical = value & ~1
            for key, contract in FUNCTIONS.items():
                if contract["start"] <= canonical < contract["end"]:
                    stored.append((APPLICATION_BASE + offset, value, key))
        self.assertEqual(stored, [])

        for key, contract in FUNCTIONS.items():
            outgoing: list[tuple[int, str, int]] = []
            for address in range(contract["start"], contract["end"] - 3, 2):
                encoded = self.span(address, address + 4)
                try:
                    target = self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    )
                except self.apollo_overlay.BuildError:
                    continue
                if not contract["start"] <= target < contract["end"]:
                    outgoing.append((address, encoded.hex(), target))
            self.assertEqual(outgoing, contract["outgoing"])

    def test_overlay_registration_relocations_patch_shape_and_aggregate_pins(
        self,
    ) -> None:
        config = json.loads(OVERLAY.read_text(encoding="utf-8"))
        leaves = {
            item["function"]: item
            for item in config["relocated_leaves"]
            if item["function"] in {
                contract["symbol"] for contract in FUNCTIONS.values()
            }
        }
        self.assertEqual(
            set(leaves),
            {contract["symbol"] for contract in FUNCTIONS.values()},
        )
        for key, contract in FUNCTIONS.items():
            symbol = contract["symbol"]
            self.assertEqual(config["functions"].count(symbol), 1)
            leaf = leaves[symbol]
            self.assertTrue(leaf["strict_relocation_contract"])
            source_path = SOURCES[key]
            self.assertEqual(leaf["source"]["path"], SOURCE_PATHS[key])
            source_size, source_hash = required_pin(
                LOCAL_PINS[source_path],
                f"LOCAL_PINS[{source_path.relative_to(ROOT)}]",
            )
            self.assertEqual(
                (leaf["source"]["size"], leaf["source"]["sha256"]),
                (source_size, source_hash),
            )
            self.assertEqual(leaf["source"]["license"], "MIT")
            self.assertEqual(leaf["source"]["upstream_commit"], UPSTREAM_COMMIT)
            self.assertEqual(leaf["toolchain"]["target"], "thumbv7em-none-eabi")
            self.assertEqual(leaf["toolchain"]["flags"], TARGET_FLAGS[1:])
            self.assertEqual(leaf["relocations"], [])

            for profile in PROFILE_PINS:
                expected = (
                    leaf["expected"]
                    if profile == "apple-clang"
                    else leaf["toolchain_profiles"][profile]["expected"]
                )
                text_size, _text_hex, text_hash = required_pin(
                    OBJECT_PINS[profile]["text"][key],
                    f"OBJECT_PINS[{profile}].text[{key}]",
                )
                placement = required_pin(
                    PROFILE_PINS[profile]["placements"][key],
                    f"PROFILE_PINS[{profile}].placements[{key}]",
                )
                relocated_hash = required_pin(
                    PROFILE_PINS[profile]["relocated_sha256"][key],
                    f"PROFILE_PINS[{profile}].relocated_sha256[{key}]",
                )
                self.assertEqual(expected["size"], text_size)
                self.assertEqual(expected["unrelocated_sha256"], text_hash)
                self.assertEqual(expected["sha256"], relocated_hash)
                self.assertEqual(expected["offset"], placement)
                self.assertEqual(text_hash, relocated_hash)

            patch = next(
                item for item in config["patch_sites"]
                if item["name"] == contract["patch_name"]
            )
            self.assertEqual(
                patch,
                {
                    "name": contract["patch_name"],
                    "runtime_address": contract["start"],
                    "expected_size": contract["end"] - contract["start"],
                    "expected_sha256": contract["stock_sha256"],
                    "branch": "b_w",
                    "target_function": symbol,
                },
            )

        registration_text = OVERLAY.read_text(encoding="utf-8") + MANIFEST.read_text(
            encoding="utf-8"
        )
        self.assertNotIn("runtime_freertos_queue_messages_waiting_candidate", registration_text)
        self.assertNotIn("open_cfw_freertos_queue_messages_waiting_candidate", registration_text)
        self.assertNotIn('"target_function": "uxQueueMessagesWaiting"', registration_text)
        self.assertNotIn('"target_function": "uxQueueMessagesWaitingFromISR"', registration_text)

        pins = PROFILE_PINS[self.profile]
        output = Path(self.temporary.name) / "registered-overlay"
        report = self.apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY,
            output_dir=output,
            clang=self.clang,
            toolchain_profile=self.profile,
        )
        overlay_pin = required_pin(pins["overlay"], f"PROFILE_PINS[{self.profile}].overlay")
        component_pin = required_pin(
            pins["component"],
            f"PROFILE_PINS[{self.profile}].component",
        )
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            overlay_pin,
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            component_pin,
        )

        by_function = {
            item["extraction"]["function"]: item
            for item in report["relocated_leaves"]
        }
        patch_reports = {
            item["name"]: item for item in report["overlay"]["patched_sites"]
        }
        component = (output / "ota_s200_firmware_ota.bin").read_bytes()
        for key, contract in FUNCTIONS.items():
            symbol = contract["symbol"]
            leaf_report = by_function[symbol]
            placement = required_pin(
                pins["placements"][key],
                f"PROFILE_PINS[{self.profile}].placements[{key}]",
            )
            overlay_runtime = report["overlay"]["overlay_runtime_address"]
            self.assertEqual(overlay_runtime, OVERLAY_RUNTIME_ADDRESS)
            runtime = overlay_runtime + placement
            self.assertEqual(leaf_report["placement"]["offset"], placement)
            self.assertEqual(leaf_report["placement"]["runtime_address"], runtime)
            self.assertEqual(leaf_report["extraction"]["relocation_count"], 0)
            self.assertEqual(leaf_report["extraction"]["relocations"], [])

            patch_report = patch_reports[contract["patch_name"]]
            replacement = bytes.fromhex(patch_report["replacement_hex"])
            patch_hex, patch_hash = required_pin(
                pins["patch"][key],
                f"PROFILE_PINS[{self.profile}].patch[{key}]",
            )
            self.assertEqual((replacement.hex(), sha256(replacement)), (
                patch_hex,
                patch_hash,
            ))
            self.assertEqual(len(replacement), contract["end"] - contract["start"])
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    contract["start"],
                    replacement[:4],
                    link=False,
                ),
                runtime,
            )
            self.assertEqual(replacement[4:], b"\x00\xbf" * ((len(replacement) - 4) // 2))

            package_offset = PACKAGE_PREAMBLE + contract["start"] - APPLICATION_BASE
            self.assertEqual(
                component[package_offset:package_offset + len(replacement)],
                replacement,
            )

        pair_start = min(int(item["start"]) for item in FUNCTIONS.values())
        pair_end = max(int(item["end"]) for item in FUNCTIONS.values())
        intervals = []
        for site in config["patch_sites"]:
            site_size = site.get("expected_size")
            if site_size is None:
                site_size = len(bytes.fromhex(site["expected_hex"]))
            intervals.append((
                int(site["runtime_address"]),
                int(site["runtime_address"]) + int(site_size),
                str(site["name"]),
            ))
        overlapping = [
            item for item in intervals
            if item[0] < pair_end and pair_start < item[1]
        ]
        self.assertEqual(
            overlapping,
            [
                (
                    int(contract["start"]),
                    int(contract["end"]),
                    str(contract["patch_name"]),
                )
                for contract in FUNCTIONS.values()
            ],
        )
        for address in (*range(pair_start - 8, pair_start), *range(pair_end, pair_end + 8)):
            if any(start <= address < end for start, end, _name in intervals):
                continue
            package_offset = PACKAGE_PREAMBLE + address - APPLICATION_BASE
            self.assertEqual(
                component[package_offset],
                self.package[package_offset],
                hex(address),
            )

    def test_manifest_registration_tiling_ownership_and_opaque_exclusion(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        region_count, accounting_pin = required_pin(MANIFEST_PIN, "MANIFEST_PIN")
        self.assertEqual(len(regions), region_count)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(left["file_offset"] + left["size"], right["file_offset"])
        provider = main["provider"]
        self.assertEqual(regions[-1]["file_offset"] + regions[-1]["size"], provider["size"])

        accounting: dict[str, tuple[int, int]] = {}
        for status in {item["address_status"] for item in regions}:
            selected = [item for item in regions if item["address_status"] == status]
            accounting[status] = (len(selected), sum(item["size"] for item in selected))
        self.assertEqual(accounting, accounting_pin)

        package = manifest["package"]
        for profile, pins in PROFILE_PINS.items():
            selected_provider = (
                provider
                if profile == "apple-clang"
                else provider["profiles"][profile]
            )
            selected_package = (
                package
                if profile == "apple-clang"
                else package["profiles"][profile]
            )
            provider_pin = required_pin(
                pins["component"],
                f"PROFILE_PINS[{profile}].component",
            )
            package_pin = required_pin(
                pins["package"],
                f"PROFILE_PINS[{profile}].package",
            )
            self.assertEqual(
                (selected_provider["size"], selected_provider["sha256"]),
                provider_pin,
            )
            self.assertEqual(
                (
                    selected_package["expected_size"],
                    selected_package["expected_sha256"],
                ),
                package_pin,
            )

        apple_pins = PROFILE_PINS["apple-clang"]

        for key, contract in FUNCTIONS.items():
            replacement = [
                item for item in regions
                if item["address_status"] == "generated_source_entry_replacement"
                and item.get("target_address") == contract["start"]
                and item["size"] == contract["end"] - contract["start"]
            ]
            self.assertEqual(len(replacement), 1, (key, replacement))
            self.assertIn("source_replacement", replacement[0]["name"])

            for region in regions:
                if region["address_status"] != "official_blob":
                    continue
                region_start = region.get("target_address")
                if not isinstance(region_start, int):
                    continue
                region_end = region_start + region["size"]
                self.assertFalse(
                    region_start < contract["end"] and contract["start"] < region_end,
                    (key, region),
                )

            placement = required_pin(
                apple_pins["placements"][key],
                f"PROFILE_PINS[apple-clang].placements[{key}]",
            )
            runtime = OVERLAY_RUNTIME_ADDRESS + placement
            text_size, _text_hex, _text_hash = required_pin(
                OBJECT_PINS["apple-clang"]["text"][key],
                f"OBJECT_PINS[apple-clang].text[{key}]",
            )
            source_regions = [
                item for item in regions
                if item["address_status"] == "source_compiled"
                and item.get("target_address") == runtime
                and item["size"] == text_size
            ]
            self.assertEqual(len(source_regions), 1, (key, source_regions))


if __name__ == "__main__":
    unittest.main()
