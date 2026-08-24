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
    ROOT
    / "components"
    / "shared"
    / "freertos"
    / "runtime_freertos_task_lists_initialize.c"
)
HEADER = SOURCE.with_suffix(".h")
UPSTREAM_TASKS = ROOT / "third_party" / "freertos-kernel" / "tasks.c"
UPSTREAM_LIST = ROOT / "third_party" / "freertos-kernel" / "list.c"
OFFICIAL = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_firmware_ota.bin"
)
OVERLAY_CONFIG = (
    ROOT / "components" / "apollo_main" / "core_overlay" / "overlay.json"
)
MANIFEST = ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
BUILD_DIRECTORY = OVERLAY_CONFIG.parent / "build"
BUILD_REPORT = BUILD_DIRECTORY / "build-report.json"
SOURCE_PATH = SOURCE.relative_to(ROOT).as_posix()

SOURCE_SIZE = 3_529
SOURCE_SHA256 = (
    "58773452256b0f44647040085bbcc7a8"
    "96a1cbd3efd0c5c4b4de3ddfe1a9e857"
)
HEADER_SIZE = 5_886
HEADER_SHA256 = (
    "6fe827f6d2659a784e8b3e22fa096162"
    "dfd4003146c0425222efc92c63baef9e"
)
UPSTREAM_TASKS_SIZE = 223_695
UPSTREAM_TASKS_SHA256 = (
    "14020d617b96dd2814e1211f6e3b645bc"
    "f5e2bd3179c23fe7dd16bc666fe9463"
)
UPSTREAM_LIST_SIZE = 10_338
UPSTREAM_LIST_SHA256 = (
    "db5c169cf3efd68da1c6a923ac84eebc"
    "724d602c940bde0b9b5f01f05028fde4"
)
PACKAGE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd"
    "3e7027730c26a9094eca47268a27863"
)
APPLICATION_SHA256 = (
    "19044a72bdfeb04c6b1b104d87da7b98"
    "e13cc18928528d84d999b6bcc0ba9701"
)

APPLICATION_BASE = 0x0043_8000
PACKAGE_PREAMBLE_SIZE = 32
START = 0x0045_568C
END = 0x0045_56E0
STOCK_BYTES = (
    "38b5002408e0dff82807142101fb04f1084400f0edfc641c382cf4d3"
    "dff89849200000f0e5fcdff89459280000f0e0fc3a4800f0ddfcdff8"
    "880900f0d9fcdff8700900f0d5fcdff87c090460dff87809056031bd"
)
STOCK_SHA256 = (
    "db9aad99c9dfd14cb9f2eb453dd86af0"
    "5b11ed049eacf8771f25a82382894723"
)
CALLER = 0x0045_4A20
CALLER_ENCODING = "00f034fe"
LIST_INITIALISE_ENTRY = 0x0045_607C
OUTGOING_CALLS = [
    (0x0045_569E, "00f0edfc"),
    (0x0045_56AE, "00f0e5fc"),
    (0x0045_56B8, "00f0e0fc"),
    (0x0045_56BE, "00f0ddfc"),
    (0x0045_56C6, "00f0d9fc"),
    (0x0045_56CE, "00f0d5fc"),
]
FIXED_LITERAL_WORDS = {
    0x0045_5DBC: 0x2006_A49C,
    0x0045_6044: 0x2007_3CFC,
    0x0045_6048: 0x2007_3D10,
    0x0045_57A8: 0x2007_3D24,
    0x0045_604C: 0x2007_3D38,
    0x0045_603C: 0x2007_3D4C,
    0x0045_6050: 0x2007_4A24,
    0x0045_6054: 0x2007_4A28,
}

FUNCTION = "open_cfw_freertos_task_lists_initialize"
DEPENDENCY = "open_cfw_freertos_list_initialise"
FUNCTION_SECTION = ".text." + FUNCTION
OVERLAY_RUNTIME_BASE = 0x0079_4324
TARGET_TEXT_BYTES = (
    "b0b54af29c450024c2f206056019fff7feff1434b4f58c6ff8d143f6fc"
    "44c2f207042046fff7feff04f114052846fff7feff04f12800fff7feff"
    "04f13c00fff7feff04f15000fff7feff44f62420c2f2070004604560b0bd"
)
TARGET_TEXT_SHA256 = (
    "6710533445c9aac3904152a43147d0e9"
    "ba9bec7eff8e7c5c6b72007c4c301fdb"
)
TARGET_TEXT_RELOCATION_OFFSETS = [14, 36, 46, 54, 62, 70]

PROFILE_PINS = {
    "apple-clang": {
        "version_prefix": "Apple clang version 21.0.0",
        "placement": 124_356,
        "relocated_sha256": (
            "22d2909d84e02d0216a71168fdac379a"
            "576317c22dd5de6f527fb595c4668b52"
        ),
        "overlay": (
            167_426,
            "800245ad7f4ba1044f01888fc0141f9f3304bc531773847ba9c0c29e62245491",
        ),
        "component": (
            3_690_822,
            "9ed3e77e10dd911ae34e9ba17f691f6988c592723b52a9676b8d414554a21459",
        ),
        "component_accounting": {
            "generated_patch_site_bytes": 121_634,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_401_548,
            "replaced_stock_function_bytes": 121_812,
            "source_owned_bytes": 165_622,
            "source_owned_in_place_bytes": 182,
        },
        "package": (
            4_469_316,
            "d4c7f82a3e0cfbfc4476f8ca72c1bfd6a3aba5b13d32c6b924686cbc4d78c10d",
        ),
        "replacement_prefix": "5df32cb9",
        "replacement_sha256": (
            "fbd0478701f559ab96a24b759970640f"
            "fd17f30f20b36f7cb61e0e4173bf98dd"
        ),
    },
    "linux-clang": {
        "version_prefix": "Homebrew clang version 22.1.8",
        "placement": 126_176,
        "relocated_sha256": (
            "dd4a36cadf6346d513ec039724a2a5830"
            "9f443d31aad4e50858c5a64d95c04f6"
        ),
        "overlay": (
            145_208,
            "fac5b48b6ae2eac985a0a65ddb8d1595dd10e2abcbdd0c6a3bb562f72e43a826",
        ),
        "component": (
            3_668_604,
            "378c868e151060a59ab91b0de1a722e8678b8e1da8eede248c5702ccf8902798",
        ),
        "component_accounting": {
            "generated_patch_site_bytes": 86_286,
            "generated_wrapper_bytes": 32,
            "opaque_base_bytes": 3_436_896,
            "replaced_stock_function_bytes": 86_468,
            "source_owned_bytes": 126_644,
            "source_owned_in_place_bytes": 182,
        },
        "package": (
            4_447_098,
            "deb4cdb9d869abcb3aee5e122661ee45b541680cf277df5d1a7c6eed67bb7b6e",
        ),
        "replacement_prefix": "5df3babc",
        "replacement_sha256": (
            "52fb57ebe49286360f1258cb2855a3b95"
            "abee1ed0a247e0cd3a3d6f6fc7d5e33"
        ),
    },
}

MANIFEST_COVERAGE = {
    "container_only": (1, 32),
    "generated_alignment": (190, 382),
    "generated_source_entry_replacement": (858, 119_962),
    "generated_source_exact_load_image": (1, 6),
    "generated_source_exact_replacement": (7, 134),
    "official_blob": (268, 3_403_044),
    "source_compiled": (455, 166_412),
}

MAX_PRIORITIES = 56
LIST_SIZE = 0x14
READY_LISTS_ADDRESS = 0x2006_A49C
SPECIAL_LIST_ADDRESSES = [
    0x2007_3CFC,
    0x2007_3D10,
    0x2007_3D24,
    0x2007_3D38,
    0x2007_3D4C,
]
DELAYED_POINTER_VALUES = [0x2007_3CFC, 0x2007_3D10]

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

HOST_BINDINGS = r"""
#ifndef OPEN_CFW_TEST_TASK_LIST_BINDINGS_H
#define OPEN_CFW_TEST_TASK_LIST_BINDINGS_H

extern unsigned char open_cfw_test_candidate_ready_guarded[];
extern unsigned char open_cfw_test_candidate_delayed_1_guarded[];
extern unsigned char open_cfw_test_candidate_delayed_2_guarded[];
extern unsigned char open_cfw_test_candidate_pending_guarded[];
extern unsigned char open_cfw_test_candidate_termination_guarded[];
extern unsigned char open_cfw_test_candidate_suspended_guarded[];
extern unsigned char open_cfw_test_candidate_delayed_pointer_guarded[];
extern unsigned char open_cfw_test_candidate_overflow_pointer_guarded[];

#define OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_ready_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1 \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_delayed_1_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2 \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_delayed_2_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_pending_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_termination_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST \
    ((struct open_cfw_freertos_task_lists_list *)(void *) \
        (open_cfw_test_candidate_suspended_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER \
    (*(volatile open_cfw_freertos_task_lists_target_pointer *)(void *) \
        (open_cfw_test_candidate_delayed_pointer_guarded + 16U))
#define OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER \
    (*(volatile open_cfw_freertos_task_lists_target_pointer *)(void *) \
        (open_cfw_test_candidate_overflow_pointer_guarded + 16U))

#endif
"""

HOST_ORACLE = r"""
#include "runtime_freertos_task_lists_initialize.h"

typedef __SIZE_TYPE__ open_cfw_test_size;

enum {
    OPEN_CFW_TEST_GUARD_WORDS = 4U,
    OPEN_CFW_TEST_CALL_COUNT =
        OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES +
        OPEN_CFW_FREERTOS_TASK_LISTS_SPECIAL_LIST_COUNT
};

struct open_cfw_test_guarded_ready {
    open_cfw_freertos_task_lists_target_pointer before[4];
    struct open_cfw_freertos_task_lists_list value[56];
    open_cfw_freertos_task_lists_target_pointer after[4];
};

struct open_cfw_test_guarded_list {
    open_cfw_freertos_task_lists_target_pointer before[4];
    struct open_cfw_freertos_task_lists_list value;
    open_cfw_freertos_task_lists_target_pointer after[4];
};

struct open_cfw_test_guarded_pointer {
    open_cfw_freertos_task_lists_target_pointer before[4];
    volatile open_cfw_freertos_task_lists_target_pointer value;
    open_cfw_freertos_task_lists_target_pointer after[4];
};

struct open_cfw_test_guarded_ready open_cfw_test_candidate_ready_guarded;
struct open_cfw_test_guarded_list open_cfw_test_candidate_delayed_1_guarded;
struct open_cfw_test_guarded_list open_cfw_test_candidate_delayed_2_guarded;
struct open_cfw_test_guarded_list open_cfw_test_candidate_pending_guarded;
struct open_cfw_test_guarded_list open_cfw_test_candidate_termination_guarded;
struct open_cfw_test_guarded_list open_cfw_test_candidate_suspended_guarded;
struct open_cfw_test_guarded_pointer
    open_cfw_test_candidate_delayed_pointer_guarded;
struct open_cfw_test_guarded_pointer
    open_cfw_test_candidate_overflow_pointer_guarded;

static struct open_cfw_test_guarded_ready open_cfw_test_oracle_ready;
static struct open_cfw_test_guarded_list open_cfw_test_oracle_delayed_1;
static struct open_cfw_test_guarded_list open_cfw_test_oracle_delayed_2;
static struct open_cfw_test_guarded_list open_cfw_test_oracle_pending;
static struct open_cfw_test_guarded_list open_cfw_test_oracle_termination;
static struct open_cfw_test_guarded_list open_cfw_test_oracle_suspended;
static struct open_cfw_test_guarded_pointer
    open_cfw_test_oracle_delayed_pointer;
static struct open_cfw_test_guarded_pointer
    open_cfw_test_oracle_overflow_pointer;

static open_cfw_freertos_task_lists_target_pointer
    open_cfw_test_call_targets[OPEN_CFW_TEST_CALL_COUNT];
static open_cfw_freertos_task_lists_ubase_type open_cfw_test_call_count;
static open_cfw_freertos_task_lists_ubase_type open_cfw_test_mapping_failed;

static void open_cfw_test_fill(
    void *memory,
    open_cfw_test_size size,
    open_cfw_freertos_task_lists_target_pointer seed
)
{
    unsigned char *bytes = (unsigned char *)memory;
    open_cfw_test_size index;

    for (index = 0U; index < size; index++) {
        bytes[index] = (unsigned char)(seed + 37U * index + index / 3U);
    }
}

static int open_cfw_test_equal(
    const void *left,
    const void *right,
    open_cfw_test_size size
)
{
    const unsigned char *left_bytes = (const unsigned char *)left;
    const unsigned char *right_bytes = (const unsigned char *)right;
    open_cfw_test_size index;

    for (index = 0U; index < size; index++) {
        if (left_bytes[index] != right_bytes[index]) {
            return 0;
        }
    }
    return 1;
}

static open_cfw_freertos_task_lists_target_pointer
open_cfw_test_map_ready(
    struct open_cfw_freertos_task_lists_list *list,
    struct open_cfw_test_guarded_ready *ready
)
{
    open_cfw_freertos_task_lists_uintptr address =
        (open_cfw_freertos_task_lists_uintptr)(void *)list;
    open_cfw_freertos_task_lists_uintptr base =
        (open_cfw_freertos_task_lists_uintptr)(void *)&ready->value[0];
    open_cfw_freertos_task_lists_uintptr end =
        (open_cfw_freertos_task_lists_uintptr)(void *)&ready->value[56];

    if (
        address >= base &&
        address < end &&
        ((address - base) %
         sizeof(struct open_cfw_freertos_task_lists_list)) == 0U
    ) {
        return (open_cfw_freertos_task_lists_target_pointer)(
            OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS_ADDRESS +
            (address - base)
        );
    }
    return 0U;
}

static open_cfw_freertos_task_lists_target_pointer
open_cfw_test_map_candidate(
    struct open_cfw_freertos_task_lists_list *list
)
{
    open_cfw_freertos_task_lists_target_pointer target =
        open_cfw_test_map_ready(
            list,
            &open_cfw_test_candidate_ready_guarded
        );

    if (target != 0U) {
        return target;
    }
    if (list == &open_cfw_test_candidate_delayed_1_guarded.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS;
    }
    if (list == &open_cfw_test_candidate_delayed_2_guarded.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS;
    }
    if (list == &open_cfw_test_candidate_pending_guarded.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST_ADDRESS;
    }
    if (list == &open_cfw_test_candidate_termination_guarded.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST_ADDRESS;
    }
    if (list == &open_cfw_test_candidate_suspended_guarded.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST_ADDRESS;
    }
    open_cfw_test_mapping_failed = 1U;
    return 0U;
}

static open_cfw_freertos_task_lists_target_pointer
open_cfw_test_map_oracle(
    struct open_cfw_freertos_task_lists_list *list
)
{
    open_cfw_freertos_task_lists_target_pointer target =
        open_cfw_test_map_ready(list, &open_cfw_test_oracle_ready);

    if (target != 0U) {
        return target;
    }
    if (list == &open_cfw_test_oracle_delayed_1.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS;
    }
    if (list == &open_cfw_test_oracle_delayed_2.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS;
    }
    if (list == &open_cfw_test_oracle_pending.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_PENDING_READY_LIST_ADDRESS;
    }
    if (list == &open_cfw_test_oracle_termination.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_TERMINATION_LIST_ADDRESS;
    }
    if (list == &open_cfw_test_oracle_suspended.value) {
        return OPEN_CFW_FREERTOS_TASK_LISTS_SUSPENDED_LIST_ADDRESS;
    }
    open_cfw_test_mapping_failed = 1U;
    return 0U;
}

static void open_cfw_test_list_initialise_at(
    struct open_cfw_freertos_task_lists_list *list,
    open_cfw_freertos_task_lists_target_pointer target
)
{
    open_cfw_freertos_task_lists_target_pointer end = target + 0x08U;

    list->index = end;
    list->end_item_value = __UINT32_MAX__;
    list->end_next = end;
    list->end_previous = end;
    list->item_count = 0U;
}

void open_cfw_freertos_list_initialise(
    struct open_cfw_freertos_list_initialise_list *provider_list
)
{
    struct open_cfw_freertos_task_lists_list *list =
        (struct open_cfw_freertos_task_lists_list *)(void *)provider_list;
    open_cfw_freertos_task_lists_target_pointer target =
        open_cfw_test_map_candidate(list);

    if (open_cfw_test_call_count < OPEN_CFW_TEST_CALL_COUNT) {
        open_cfw_test_call_targets[open_cfw_test_call_count] = target;
    } else {
        open_cfw_test_mapping_failed = 1U;
    }
    open_cfw_test_call_count++;
    open_cfw_test_list_initialise_at(list, target);
}

static void open_cfw_test_oracle_vListInitialise(
    struct open_cfw_freertos_task_lists_list *list
)
{
    open_cfw_test_list_initialise_at(list, open_cfw_test_map_oracle(list));
}

static void open_cfw_test_pristine_task_lists_initialize(void)
{
    open_cfw_freertos_task_lists_ubase_type uxPriority;

    for (
        uxPriority = (open_cfw_freertos_task_lists_ubase_type)0U;
        uxPriority < (open_cfw_freertos_task_lists_ubase_type)
            OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES;
        uxPriority++
    ) {
        open_cfw_test_oracle_vListInitialise(
            &open_cfw_test_oracle_ready.value[uxPriority]
        );
    }

    open_cfw_test_oracle_vListInitialise(
        &open_cfw_test_oracle_delayed_1.value
    );
    open_cfw_test_oracle_vListInitialise(
        &open_cfw_test_oracle_delayed_2.value
    );
    open_cfw_test_oracle_vListInitialise(
        &open_cfw_test_oracle_pending.value
    );
    open_cfw_test_oracle_vListInitialise(
        &open_cfw_test_oracle_termination.value
    );
    open_cfw_test_oracle_vListInitialise(
        &open_cfw_test_oracle_suspended.value
    );

    open_cfw_test_oracle_delayed_pointer.value =
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_1_ADDRESS;
    open_cfw_test_oracle_overflow_pointer.value =
        OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_LIST_2_ADDRESS;
}

void open_cfw_test_task_lists_reset(
    open_cfw_freertos_task_lists_target_pointer seed
)
{
#define OPEN_CFW_TEST_RESET_PAIR(candidate, oracle, salt) \
    do { \
        open_cfw_test_fill(&(candidate), sizeof(candidate), seed + (salt)); \
        open_cfw_test_fill(&(oracle), sizeof(oracle), seed + (salt)); \
    } while (0)

    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_ready_guarded,
        open_cfw_test_oracle_ready,
        1U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_delayed_1_guarded,
        open_cfw_test_oracle_delayed_1,
        2U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_delayed_2_guarded,
        open_cfw_test_oracle_delayed_2,
        3U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_pending_guarded,
        open_cfw_test_oracle_pending,
        4U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_termination_guarded,
        open_cfw_test_oracle_termination,
        5U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_suspended_guarded,
        open_cfw_test_oracle_suspended,
        6U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_delayed_pointer_guarded,
        open_cfw_test_oracle_delayed_pointer,
        7U
    );
    OPEN_CFW_TEST_RESET_PAIR(
        open_cfw_test_candidate_overflow_pointer_guarded,
        open_cfw_test_oracle_overflow_pointer,
        8U
    );
#undef OPEN_CFW_TEST_RESET_PAIR

    open_cfw_test_call_count = 0U;
    open_cfw_test_mapping_failed = 0U;
    open_cfw_test_fill(
        open_cfw_test_call_targets,
        sizeof(open_cfw_test_call_targets),
        seed + 9U
    );
}

void open_cfw_test_task_lists_run_candidate(void)
{
    open_cfw_freertos_task_lists_initialize();
}

void open_cfw_test_task_lists_run_oracle(void)
{
    open_cfw_test_pristine_task_lists_initialize();
}

int open_cfw_test_task_lists_equivalent(void)
{
#define OPEN_CFW_TEST_COMPARE(candidate, oracle) \
    open_cfw_test_equal(&(candidate), &(oracle), sizeof(candidate))

    return open_cfw_test_mapping_failed == 0U &&
        open_cfw_test_call_count == OPEN_CFW_TEST_CALL_COUNT &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_ready_guarded,
            open_cfw_test_oracle_ready
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_delayed_1_guarded,
            open_cfw_test_oracle_delayed_1
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_delayed_2_guarded,
            open_cfw_test_oracle_delayed_2
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_pending_guarded,
            open_cfw_test_oracle_pending
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_termination_guarded,
            open_cfw_test_oracle_termination
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_suspended_guarded,
            open_cfw_test_oracle_suspended
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_delayed_pointer_guarded,
            open_cfw_test_oracle_delayed_pointer
        ) &&
        OPEN_CFW_TEST_COMPARE(
            open_cfw_test_candidate_overflow_pointer_guarded,
            open_cfw_test_oracle_overflow_pointer
        );
#undef OPEN_CFW_TEST_COMPARE
}

open_cfw_freertos_task_lists_ubase_type
open_cfw_test_task_lists_call_count(void)
{
    return open_cfw_test_call_count;
}

open_cfw_freertos_task_lists_target_pointer
open_cfw_test_task_lists_call_target(
    open_cfw_freertos_task_lists_ubase_type index
)
{
    if (index >= OPEN_CFW_TEST_CALL_COUNT) {
        return 0U;
    }
    return open_cfw_test_call_targets[index];
}

static struct open_cfw_freertos_task_lists_list *
open_cfw_test_candidate_list(
    open_cfw_freertos_task_lists_ubase_type group,
    open_cfw_freertos_task_lists_ubase_type index
)
{
    if (
        group == 0U &&
        index < OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES
    ) {
        return &open_cfw_test_candidate_ready_guarded.value[index];
    }
    if (group == 1U) {
        return &open_cfw_test_candidate_delayed_1_guarded.value;
    }
    if (group == 2U) {
        return &open_cfw_test_candidate_delayed_2_guarded.value;
    }
    if (group == 3U) {
        return &open_cfw_test_candidate_pending_guarded.value;
    }
    if (group == 4U) {
        return &open_cfw_test_candidate_termination_guarded.value;
    }
    if (group == 5U) {
        return &open_cfw_test_candidate_suspended_guarded.value;
    }
    return (struct open_cfw_freertos_task_lists_list *)0;
}

open_cfw_freertos_task_lists_target_pointer
open_cfw_test_task_lists_list_word(
    open_cfw_freertos_task_lists_ubase_type group,
    open_cfw_freertos_task_lists_ubase_type index,
    open_cfw_freertos_task_lists_ubase_type word
)
{
    struct open_cfw_freertos_task_lists_list *list =
        open_cfw_test_candidate_list(group, index);
    const open_cfw_freertos_task_lists_target_pointer *words =
        (const open_cfw_freertos_task_lists_target_pointer *)(const void *)list;

    if (list == (struct open_cfw_freertos_task_lists_list *)0 || word >= 5U) {
        return 0U;
    }
    return words[word];
}

open_cfw_freertos_task_lists_target_pointer
open_cfw_test_task_lists_delayed_pointer(
    open_cfw_freertos_task_lists_ubase_type overflow
)
{
    return overflow == 0U
        ? open_cfw_test_candidate_delayed_pointer_guarded.value
        : open_cfw_test_candidate_overflow_pointer_guarded.value;
}
"""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def library_name(stem: str) -> str:
    return stem + (".dylib" if sys.platform == "darwin" else ".so")


def thumb_wide_branch_target(
    address: int,
    first: int,
    second: int,
    *,
    link: bool,
) -> int | None:
    expected_second = 0xD000 if link else 0x9000
    if first & 0xF800 != 0xF000 or second & 0xD000 != expected_second:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFF_FFFF


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


class RuntimeFreeRTOSTaskListsInitializeProductionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = OFFICIAL.read_bytes()
        cls.application = cls.package[PACKAGE_PREAMBLE_SIZE:]
        cls.temporary = tempfile.TemporaryDirectory()
        temporary = Path(cls.temporary.name)
        cls.clang = os.environ.get("OPENCFW_CLANG", "/usr/bin/clang")
        cls.clang_version = subprocess.run(
            [cls.clang, "--version"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.splitlines()[0]
        profiles = [
            profile
            for profile, pins in PROFILE_PINS.items()
            if cls.clang_version.startswith(str(pins["version_prefix"]))
        ]
        if len(profiles) != 1:
            raise AssertionError(
                f"unreviewed compiler: {(cls.clang, cls.clang_version)!r}"
            )
        cls.profile = profiles[0]
        cls.profile_pins = PROFILE_PINS[cls.profile]

        bindings = temporary / "host_bindings.h"
        bindings.write_text(HOST_BINDINGS, encoding="utf-8")
        oracle = temporary / "host_oracle.c"
        oracle.write_text(HOST_ORACLE, encoding="utf-8")
        candidate_object = temporary / "candidate_host.o"
        oracle_object = temporary / "oracle_host.o"
        host_flags = ["-O2", "-fPIC", "-Wall", "-Wextra", "-Werror"]
        include_directory = str(SOURCE.parent)
        subprocess.run(
            [
                cls.clang,
                *host_flags,
                "-I",
                include_directory,
                "-include",
                str(bindings),
                "-c",
                str(SOURCE),
                "-o",
                str(candidate_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        subprocess.run(
            [
                cls.clang,
                *host_flags,
                "-I",
                include_directory,
                "-c",
                str(oracle),
                "-o",
                str(oracle_object),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        library = temporary / library_name("freertos_task_lists_candidate")
        link_command = [cls.clang, str(candidate_object), str(oracle_object)]
        if sys.platform == "darwin":
            link_command.extend(["-dynamiclib", "-o", str(library)])
        else:
            link_command.extend(["-shared", "-o", str(library)])
        subprocess.run(
            link_command,
            check=True,
            capture_output=True,
            text=True,
        )
        cls.loaded = ctypes.CDLL(str(library))
        cls.reset = cls.loaded.open_cfw_test_task_lists_reset
        cls.reset.argtypes = [ctypes.c_uint32]
        cls.reset.restype = None
        cls.run_candidate = cls.loaded.open_cfw_test_task_lists_run_candidate
        cls.run_candidate.argtypes = []
        cls.run_candidate.restype = None
        cls.run_oracle = cls.loaded.open_cfw_test_task_lists_run_oracle
        cls.run_oracle.argtypes = []
        cls.run_oracle.restype = None
        cls.equivalent = cls.loaded.open_cfw_test_task_lists_equivalent
        cls.equivalent.argtypes = []
        cls.equivalent.restype = ctypes.c_int
        cls.call_count = cls.loaded.open_cfw_test_task_lists_call_count
        cls.call_count.argtypes = []
        cls.call_count.restype = ctypes.c_uint32
        cls.call_target = cls.loaded.open_cfw_test_task_lists_call_target
        cls.call_target.argtypes = [ctypes.c_uint32]
        cls.call_target.restype = ctypes.c_uint32
        cls.list_word = cls.loaded.open_cfw_test_task_lists_list_word
        cls.list_word.argtypes = [
            ctypes.c_uint32,
            ctypes.c_uint32,
            ctypes.c_uint32,
        ]
        cls.list_word.restype = ctypes.c_uint32
        cls.delayed_pointer = (
            cls.loaded.open_cfw_test_task_lists_delayed_pointer
        )
        cls.delayed_pointer.argtypes = [ctypes.c_uint32]
        cls.delayed_pointer.restype = ctypes.c_uint32

        cls.target_objects = []
        for index in range(2):
            target_object = temporary / f"candidate_target_{index}.o"
            subprocess.run(
                [
                    cls.clang,
                    *TARGET_FLAGS,
                    "-c",
                    str(SOURCE),
                    "-o",
                    str(target_object),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            cls.target_objects.append(target_object)

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay

        cls.elf_data, cls.sections = apollo_overlay.parse_elf32(
            cls.target_objects[0]
        )
        cls.apollo_overlay = apollo_overlay
        symbol_table = apollo_overlay.section_named(cls.sections, ".symtab")
        string_table = cls.sections[int(symbol_table["link"])]
        strings = cls.elf_data[
            int(string_table["offset"]):
            int(string_table["offset"]) + int(string_table["size"])
        ]
        cls.parsed_symbols = []
        for index in range(int(symbol_table["size"]) // 16):
            fields = struct.unpack_from(
                "<IIIBBH",
                cls.elf_data,
                int(symbol_table["offset"]) + index * 16,
            )
            name = apollo_overlay.elf_string(strings, fields[0], "symbol")
            cls.parsed_symbols.append((name, fields))
        cls.symbols = {
            name: fields
            for name, fields in cls.parsed_symbols
            if name
        }
        cls.relocations = []
        for section in cls.sections:
            if int(section["type"]) != 9:
                continue
            target = cls.sections[int(section["info"])]
            for index in range(int(section["size"]) // 8):
                offset, information = struct.unpack_from(
                    "<II",
                    cls.elf_data,
                    int(section["offset"]) + index * 8,
                )
                cls.relocations.append(
                    (
                        str(section["name"]),
                        str(target["name"]),
                        offset,
                        information & 0xFF,
                        cls.parsed_symbols[information >> 8][0],
                    )
                )

        (ROOT / "build").mkdir(parents=True, exist_ok=True)
        cls.production_temporary = tempfile.TemporaryDirectory(
            prefix="open-cfw-task-lists-production-",
            dir=ROOT / "build",
        )
        cls.production_output = Path(cls.production_temporary.name)
        cls.production_report = apollo_overlay.build(
            root=ROOT,
            config_path=OVERLAY_CONFIG,
            output_dir=cls.production_output,
            clang=cls.clang,
            toolchain_profile=cls.profile,
        )
        cls.recorded_report = json.loads(
            BUILD_REPORT.read_text(encoding="utf-8")
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.production_temporary.cleanup()
        cls.temporary.cleanup()

    @classmethod
    def span(cls, start: int, end: int) -> bytes:
        return cls.application[
            start - APPLICATION_BASE:end - APPLICATION_BASE
        ]

    def test_authenticated_source_and_configuration_are_pinned(
        self,
    ) -> None:
        self.assertEqual(SOURCE.stat().st_size, SOURCE_SIZE)
        self.assertEqual(HEADER.stat().st_size, HEADER_SIZE)
        self.assertEqual(sha256(SOURCE.read_bytes()), SOURCE_SHA256)
        self.assertEqual(sha256(HEADER.read_bytes()), HEADER_SHA256)
        self.assertEqual(UPSTREAM_TASKS.stat().st_size, UPSTREAM_TASKS_SIZE)
        self.assertEqual(
            sha256(UPSTREAM_TASKS.read_bytes()),
            UPSTREAM_TASKS_SHA256,
        )
        self.assertEqual(UPSTREAM_LIST.stat().st_size, UPSTREAM_LIST_SIZE)
        self.assertEqual(
            sha256(UPSTREAM_LIST.read_bytes()),
            UPSTREAM_LIST_SHA256,
        )

        tasks = UPSTREAM_TASKS.read_text(encoding="utf-8")
        for token in (
            "static void prvInitialiseTaskLists( void )",
            "uxPriority < ( UBaseType_t ) configMAX_PRIORITIES",
            "vListInitialise( &( pxReadyTasksLists[ uxPriority ] ) );",
            "vListInitialise( &xDelayedTaskList1 );",
            "vListInitialise( &xDelayedTaskList2 );",
            "vListInitialise( &xPendingReadyList );",
            "vListInitialise( &xTasksWaitingTermination );",
            "vListInitialise( &xSuspendedTaskList );",
            "pxDelayedTaskList = &xDelayedTaskList1;",
            "pxOverflowDelayedTaskList = &xDelayedTaskList2;",
        ):
            self.assertIn(token, tasks)
        upstream_list = UPSTREAM_LIST.read_text(encoding="utf-8")
        for token in (
            "void vListInitialise( List_t * const pxList )",
            "pxList->xListEnd.xItemValue = portMAX_DELAY;",
            "pxList->uxNumberOfItems = ( UBaseType_t ) 0U;",
        ):
            self.assertIn(token, upstream_list)

        source = SOURCE.read_text(encoding="utf-8")
        header = HEADER.read_text(encoding="utf-8")
        for token in (
            "FreeRTOS Kernel V10.5.1",
            "SPDX-License-Identifier: MIT",
            "prvInitialiseTaskLists()",
            "def7d2df2b0506d3d249334974f51e427c17a41c",
            "[0x0045568C, 0x004556E0)",
            "OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES",
            "OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER",
            "OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER",
        ):
            self.assertIn(token, source)
        for token in (
            "OPEN_CFW_FREERTOS_TASK_LISTS_MAX_PRIORITIES = 56U",
            "OPEN_CFW_FREERTOS_TASK_LISTS_SPECIAL_LIST_COUNT = 5U",
            "sizeof(struct open_cfw_freertos_task_lists_list) == 0x14U",
            "OPEN_CFW_FREERTOS_TASK_LISTS_READY_LISTS_ADDRESS = 0x2006A49CU",
            "OPEN_CFW_FREERTOS_TASK_LISTS_DELAYED_POINTER_ADDRESS = 0x20074A24U",
            "OPEN_CFW_FREERTOS_TASK_LISTS_OVERFLOW_POINTER_ADDRESS = 0x20074A28U",
        ):
            self.assertIn(token, header)

    def test_production_registration_profile_pins_and_relocations_are_exact(
        self,
    ) -> None:
        config = json.loads(OVERLAY_CONFIG.read_text(encoding="utf-8"))
        leaves = [
            item
            for item in config["relocated_leaves"]
            if item["function"] == FUNCTION
        ]
        self.assertEqual(len(leaves), 1)
        self.assertEqual(config["functions"].count(FUNCTION), 1)
        self.assertEqual(config["functions"].index(FUNCTION), 644)
        leaf = leaves[0]
        self.assertTrue(leaf["strict_relocation_contract"])
        self.assertEqual(
            leaf["source"],
            {
                "path": SOURCE_PATH,
                "size": SOURCE_SIZE,
                "sha256": SOURCE_SHA256,
                "license": "MIT",
                "origin": (
                    "bounded adaptation of authenticated FreeRTOS-Kernel "
                    "V10.5.1 prvInitialiseTaskLists with recovered G2 "
                    "scheduler-list RAM bindings and direct source-owned "
                    "vListInitialise closure"
                ),
                "upstream": (
                    "https://github.com/FreeRTOS/FreeRTOS-Kernel/blob/"
                    "def7d2df2b0506d3d249334974f51e427c17a41c/"
                    "tasks.c"
                ),
                "upstream_commit": (
                    "def7d2df2b0506d3d249334974f51e427c17a41c"
                ),
                "evidence": (
                    "docs/research/"
                    "freertos-task-lists-initialize-source-audit.md"
                ),
            },
        )
        self.assertEqual(leaf["toolchain"]["target"], TARGET_FLAGS[0][9:])
        self.assertEqual(leaf["toolchain"]["flags"], TARGET_FLAGS[1:])
        self.assertEqual(
            leaf["toolchain"]["reviewed_version_prefix"],
            PROFILE_PINS["apple-clang"]["version_prefix"],
        )

        relocation_pin = [
            {
                "offset": offset,
                "type": "R_ARM_THM_CALL",
                "symbol": DEPENDENCY,
                "symbol_type": "STT_NOTYPE",
                "target_function": DEPENDENCY,
            }
            for offset in TARGET_TEXT_RELOCATION_OFFSETS
        ]
        for profile, pins in PROFILE_PINS.items():
            profile_leaf = (
                leaf
                if profile == "apple-clang"
                else leaf["toolchain_profiles"][profile]
            )
            self.assertEqual(
                profile_leaf["expected"],
                {
                    "size": 88,
                    "sha256": pins["relocated_sha256"],
                    "alignment": 4,
                    "offset": pins["placement"],
                    "unrelocated_sha256": TARGET_TEXT_SHA256,
                },
            )
            self.assertEqual(profile_leaf["relocations"], relocation_pin)
            if profile != "apple-clang":
                self.assertEqual(
                    profile_leaf["reviewed_version_prefix"],
                    pins["version_prefix"],
                )

            aggregate = (
                config["expected"]
                if profile == "apple-clang"
                else config["toolchain_profiles"][profile]["expected"]
            )
            self.assertEqual(
                (aggregate["overlay_size"], aggregate["overlay_sha256"]),
                pins["overlay"],
            )
            self.assertEqual(
                (
                    aggregate["component_size"],
                    aggregate["component_sha256"],
                ),
                pins["component"],
            )

            replacement = (
                bytes.fromhex(str(pins["replacement_prefix"]))
                + b"\x00\xbf" * 40
            )
            self.assertEqual(len(replacement), END - START)
            self.assertEqual(
                sha256(replacement),
                pins["replacement_sha256"],
            )
            self.assertEqual(
                self.apollo_overlay.decode_thumb_branch(
                    START,
                    replacement[:4],
                    link=False,
                ),
                OVERLAY_RUNTIME_BASE + int(pins["placement"]),
            )

        patches = [
            item
            for item in config["patch_sites"]
            if item.get("target_function") == FUNCTION
        ]
        self.assertEqual(
            patches,
            [{
                "name": "replace_freertos_task_lists_initialize",
                "runtime_address": START,
                "expected_size": END - START,
                "expected_sha256": STOCK_SHA256,
                "branch": "b_w",
                "target_function": FUNCTION,
            }],
        )
        self.assertIn(DEPENDENCY, config["functions"])
        dependency_patches = [
            item
            for item in config["patch_sites"]
            if item.get("target_function") == DEPENDENCY
        ]
        self.assertEqual(len(dependency_patches), 1)
        self.assertEqual(
            (
                dependency_patches[0]["name"],
                dependency_patches[0]["runtime_address"],
            ),
            ("replace_freertos_list_initialise", LIST_INITIALISE_ENTRY),
        )

    def test_active_and_recorded_production_artifacts_and_patch_are_exact(
        self,
    ) -> None:
        report = self.production_report
        pins = self.profile_pins
        self.assertEqual(
            (report["overlay"]["size"], report["overlay"]["sha256"]),
            pins["overlay"],
        )
        self.assertEqual(
            (report["component"]["size"], report["component"]["sha256"]),
            pins["component"],
        )
        for key, value in pins["component_accounting"].items():
            self.assertEqual(report["component"][key], value, key)

        selected = [
            item
            for item in report["relocated_leaves"]
            if item["extraction"]["function"] == FUNCTION
        ]
        self.assertEqual(len(selected), 1)
        selected_leaf = selected[0]
        runtime = OVERLAY_RUNTIME_BASE + int(pins["placement"])
        self.assertEqual(
            selected_leaf["placement"],
            {
                "offset": pins["placement"],
                "runtime_address": runtime,
                "runtime_address_hex": f"0x{runtime:08X}",
                "size": 88,
                "alignment": 4,
                "padding_before": 0,
            },
        )
        extraction = selected_leaf["extraction"]
        self.assertEqual(extraction["sha256"], pins["relocated_sha256"])
        self.assertEqual(
            extraction["unrelocated_sha256"],
            TARGET_TEXT_SHA256,
        )
        self.assertEqual(extraction["relocation_count"], 6)
        dependency_runtime = (
            OVERLAY_RUNTIME_BASE
            + report["overlay"]["functions"][DEPENDENCY]["offset"]
        )
        for relocation, expected_offset in zip(
            extraction["relocations"],
            TARGET_TEXT_RELOCATION_OFFSETS,
        ):
            self.assertEqual(
                {
                    key: relocation[key]
                    for key in (
                        "offset",
                        "type",
                        "type_id",
                        "symbol",
                        "symbol_type",
                        "target_function",
                        "target_address",
                    )
                },
                {
                    "offset": expected_offset,
                    "type": "R_ARM_THM_CALL",
                    "type_id": 10,
                    "symbol": DEPENDENCY,
                    "symbol_type": "STT_NOTYPE",
                    "target_function": DEPENDENCY,
                    "target_address": dependency_runtime,
                },
            )
        self.assertEqual(
            extraction["authenticated_cantunwind_discard_count"],
            1,
        )
        self.assertEqual(extraction["discarded_alloc_section_bytes"], 8)

        patch = next(
            item
            for item in report["overlay"]["patched_sites"]
            if item["name"] == "replace_freertos_task_lists_initialize"
        )
        replacement = bytes.fromhex(patch["replacement_hex"])
        self.assertEqual(
            (replacement[:4].hex(), sha256(replacement)),
            (pins["replacement_prefix"], pins["replacement_sha256"]),
        )
        self.assertEqual(replacement[4:], b"\x00\xbf" * 40)
        self.assertEqual(patch["target_address"], runtime)
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                START,
                replacement[:4],
                link=False,
            ),
            runtime,
        )
        component = (
            self.production_output / "ota_s200_firmware_ota.bin"
        ).read_bytes()
        patch_offset = PACKAGE_PREAMBLE_SIZE + START - APPLICATION_BASE
        self.assertEqual(patch["payload_offset"], patch_offset)
        self.assertEqual(
            component[patch_offset:patch_offset + len(replacement)],
            replacement,
        )
        self.assertEqual(
            component[patch_offset - 8:patch_offset],
            self.package[patch_offset - 8:patch_offset],
        )
        self.assertEqual(
            component[
                patch_offset + len(replacement):
                patch_offset + len(replacement) + 8
            ],
            self.package[
                patch_offset + len(replacement):
                patch_offset + len(replacement) + 8
            ],
        )

        recorded_profile = self.recorded_report["toolchain"]["profile"]
        self.assertIn(recorded_profile, PROFILE_PINS)
        recorded_pins = PROFILE_PINS[recorded_profile]
        self.assertEqual(
            (
                self.recorded_report["overlay"]["size"],
                self.recorded_report["overlay"]["sha256"],
            ),
            recorded_pins["overlay"],
        )
        self.assertEqual(
            (
                self.recorded_report["component"]["size"],
                self.recorded_report["component"]["sha256"],
            ),
            recorded_pins["component"],
        )
        for report_key in ("overlay", "component"):
            artifact = ROOT / self.recorded_report[report_key]["artifact"]
            self.assertEqual(
                (artifact.stat().st_size, sha256(artifact.read_bytes())),
                recorded_pins[report_key],
            )

    def test_manifest_ownership_tiling_and_profile_coverage_are_exact(
        self,
    ) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        main = manifest["component_overrides"]["apollo_main"]
        regions = main["regions"]
        self.assertEqual(len(regions), 1818)
        self.assertEqual(regions[0]["file_offset"], 0)
        for left, right in zip(regions, regions[1:]):
            self.assertEqual(
                left["file_offset"] + left["size"],
                right["file_offset"],
            )
        provider = main["provider"]
        self.assertEqual(
            regions[-1]["file_offset"] + regions[-1]["size"],
            provider["size"],
        )

        coverage: dict[str, tuple[int, int]] = {}
        for status in {region["address_status"] for region in regions}:
            selected = [
                region
                for region in regions
                if region["address_status"] == status
            ]
            coverage[status] = (
                len(selected),
                sum(region["size"] for region in selected),
            )
        self.assertEqual(coverage, MANIFEST_COVERAGE)

        by_name = {region["name"]: region for region in regions}
        replacement = by_name[
            "freertos_task_lists_initialize_source_replacement"
        ]
        self.assertEqual(
            replacement,
            {
                "name": (
                    "freertos_task_lists_initialize_source_replacement"
                ),
                "function": (
                    "Generated entry redirect and NOP fill replacing "
                    "FreeRTOS V10.5.1 prvInitialiseTaskLists"
                ),
                "file_offset": PACKAGE_PREAMBLE_SIZE + START - APPLICATION_BASE,
                "size": END - START,
                "target": "apollo510b_internal_mram",
                "target_address": START,
                "address_status": "generated_source_entry_replacement",
                "output": (
                    "apollo510b/source-entry-freertos-task-lists-"
                    "initialize-0x0045568c.bin"
                ),
            },
        )
        tail = by_name["apollo_freertos_task_lists_initialize_source_leaf"]
        self.assertIs(tail, regions[-493])
        self.assertEqual(
            tail,
            {
                "name": (
                    "apollo_freertos_task_lists_initialize_source_leaf"
                ),
                "function": (
                    "MIT-licensed FreeRTOS V10.5.1 scheduler-list "
                    "initialization source leaf"
                ),
                "file_offset": 3_647_752,
                "size": 88,
                "target": "apollo510b_internal_mram",
                "target_address": (
                    OVERLAY_RUNTIME_BASE
                    + int(PROFILE_PINS["apple-clang"]["placement"])
                ),
                "address_status": "source_compiled",
                "output": (
                    "apollo510b/main-source-freertos-task-lists-"
                    "initialize-0x007b28e8.bin"
                ),
            },
        )
        for region in regions:
            if region["address_status"] != "official_blob":
                continue
            region_start = region.get("target_address")
            if not isinstance(region_start, int):
                continue
            self.assertFalse(
                region_start < END
                and START < region_start + region["size"],
                region,
            )

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
            self.assertEqual(
                (selected_provider["size"], selected_provider["sha256"]),
                pins["component"],
            )
            self.assertEqual(
                (
                    selected_package["expected_size"],
                    selected_package["expected_sha256"],
                ),
                pins["package"],
            )

    def test_host_oracle_all_lists_order_pointers_and_guards(self) -> None:
        expected_targets = [
            READY_LISTS_ADDRESS + LIST_SIZE * index
            for index in range(MAX_PRIORITIES)
        ] + SPECIAL_LIST_ADDRESSES

        for seed in (0, 1, 0x55, 0xA5, 0xFFFF_FFFF):
            with self.subTest(seed=seed):
                self.reset(seed)
                self.run_candidate()
                self.run_oracle()
                self.assertEqual(self.equivalent(), 1)
                self.assertEqual(self.call_count(), len(expected_targets))
                self.assertEqual(
                    [self.call_target(index) for index in range(61)],
                    expected_targets,
                )

                for index in range(MAX_PRIORITIES):
                    target = READY_LISTS_ADDRESS + LIST_SIZE * index
                    words = [
                        self.list_word(0, index, word)
                        for word in range(5)
                    ]
                    self.assertEqual(
                        words,
                        [0, target + 8, 0xFFFF_FFFF, target + 8, target + 8],
                    )
                for group, target in enumerate(
                    SPECIAL_LIST_ADDRESSES,
                    start=1,
                ):
                    self.assertEqual(
                        [self.list_word(group, 0, word) for word in range(5)],
                        [0, target + 8, 0xFFFF_FFFF, target + 8, target + 8],
                    )
                self.assertEqual(
                    [self.delayed_pointer(index) for index in range(2)],
                    DELAYED_POINTER_VALUES,
                )

    def test_official_span_call_graph_literals_and_ingress_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.package), 3_523_396)
        self.assertEqual(sha256(self.package), PACKAGE_SHA256)
        self.assertEqual(len(self.application), 3_523_364)
        self.assertEqual(sha256(self.application), APPLICATION_SHA256)
        stock = self.span(START, END)
        self.assertEqual(len(stock), 84)
        self.assertEqual(stock.hex(), STOCK_BYTES)
        self.assertEqual(sha256(stock), STOCK_SHA256)
        self.assertEqual(self.span(CALLER, CALLER + 4).hex(), CALLER_ENCODING)
        for address, value in FIXED_LITERAL_WORDS.items():
            self.assertEqual(
                struct.unpack("<I", self.span(address, address + 4))[0],
                value,
            )

        direct_bl = []
        direct_bw = []
        outgoing = []
        external_interior = []
        for offset in range(0, len(self.application) - 3, 2):
            address = APPLICATION_BASE + offset
            first, second = struct.unpack_from(
                "<HH",
                self.application,
                offset,
            )
            for link, observed in ((True, direct_bl), (False, direct_bw)):
                target = thumb_wide_branch_target(
                    address,
                    first,
                    second,
                    link=link,
                )
                if target == START:
                    observed.append(
                        (address, self.application[offset:offset + 4].hex())
                    )
                if (
                    target is not None
                    and START < target < END
                    and not START <= address < END
                ):
                    external_interior.append((address, target, link))
                if link and START <= address < END and target is not None:
                    outgoing.append(
                        (address, target, self.application[offset:offset + 4].hex())
                    )
        self.assertEqual(direct_bl, [(CALLER, CALLER_ENCODING)])
        self.assertEqual(direct_bw, [])
        self.assertEqual(external_interior, [])
        self.assertEqual(
            outgoing,
            [
                (address, LIST_INITIALISE_ENTRY, encoding)
                for address, encoding in OUTGOING_CALLS
            ],
        )

        external_narrow = []
        for offset in range(0, len(self.application) - 1, 2):
            address = APPLICATION_BASE + offset
            halfword = struct.unpack_from(
                "<H",
                self.application,
                offset,
            )[0]
            for target in narrow_branch_targets(address, halfword):
                if (
                    START <= target < END
                    and not START <= address < END
                ):
                    external_narrow.append((address, target, halfword))
        self.assertEqual(external_narrow, [])

        stored = []
        for canonical in range(START, END):
            for value in {canonical, canonical | 1}:
                needle = struct.pack("<I", value)
                position = 0
                while True:
                    position = self.application.find(needle, position)
                    if position < 0:
                        break
                    stored.append(
                        (APPLICATION_BASE + position, value, canonical)
                    )
                    position += 1
        self.assertEqual(stored, [])

    def test_target_object_is_reproducible_and_closes_on_owned_provider(
        self,
    ) -> None:
        first_object = self.target_objects[0].read_bytes()
        second_object = self.target_objects[1].read_bytes()
        self.assertEqual(first_object, second_object)

        function_section = next(
            section
            for section in self.sections
            if section["name"] == FUNCTION_SECTION
        )
        executable = [
            section
            for section in self.sections
            if int(section["size"]) > 0 and int(section["flags"]) & 0x4
        ]
        self.assertEqual(
            [section["name"] for section in executable],
            [FUNCTION_SECTION],
        )
        function_bytes = self.elf_data[
            int(function_section["offset"]):
            int(function_section["offset"]) + int(function_section["size"])
        ]
        self.assertEqual(int(function_section["type"]), 1)
        self.assertEqual(int(function_section["flags"]), 0x6)
        self.assertEqual(int(function_section["alignment"]), 4)
        self.assertEqual(len(function_bytes), 88)
        self.assertEqual(function_bytes.hex(), TARGET_TEXT_BYTES)
        self.assertEqual(sha256(function_bytes), TARGET_TEXT_SHA256)

        fields = self.symbols[FUNCTION]
        self.assertEqual(fields[1] & 1, 1)
        self.assertEqual(fields[2], int(function_section["size"]))
        self.assertEqual(fields[3] >> 4, 1)
        self.assertEqual(fields[3] & 0xF, 2)
        self.assertEqual(fields[5], int(function_section["index"]))
        undefined = [
            name
            for name, fields in self.parsed_symbols
            if name and fields[5] == 0
        ]
        self.assertEqual(undefined, [DEPENDENCY])

        text_relocations = [
            relocation
            for relocation in self.relocations
            if relocation[1] == FUNCTION_SECTION
        ]
        self.assertEqual(
            text_relocations,
            [
                (
                    ".rel." + FUNCTION_SECTION[1:],
                    FUNCTION_SECTION,
                    offset,
                    10,
                    DEPENDENCY,
                )
                for offset in TARGET_TEXT_RELOCATION_OFFSETS
            ],
        )
        metadata_relocations = [
            relocation
            for relocation in self.relocations
            if relocation[1].startswith(".ARM.exidx.")
        ]
        self.assertEqual(len(metadata_relocations), 1)
        self.assertEqual(metadata_relocations[0][2:], (0, 42, ""))

        writable_allocated = [
            section["name"]
            for section in self.sections
            if (
                int(section["size"]) > 0
                and int(section["flags"]) & 0x2
                and int(section["flags"]) & 0x1
            )
        ]
        self.assertEqual(writable_allocated, [])
        self.assertFalse(
            any(
                str(section["name"]).startswith((".data", ".bss", ".rodata"))
                and int(section["size"]) > 0
                for section in self.sections
            )
        )


if __name__ == "__main__":
    unittest.main()
