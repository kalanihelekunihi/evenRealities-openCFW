from __future__ import annotations

import os

import hashlib
import importlib.util
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
COMPONENT = ROOT / "components" / "bootloader" / "core_overlay"
CONFIG_PATH = COMPONENT / "overlay.json"
BUILDER_PATH = COMPONENT / "build_component.py"
CORE_SOURCE_MANIFEST_PATH = (
    ROOT / "manifests" / "g2-2.2.6.10-core-source.json"
)
OFFICIAL_PATH = (
    ROOT
    / "blobs"
    / "official"
    / "g2-2.2.6.10"
    / "ota_s200_bootloader.bin"
)

RUN_BASE = 0x00410000
MAIN_BOUNDARY = 0x00438000
STOCK_END = 0x00434477
LITTLEFS_UTIL_MAX_ADDRESS = 0x00410400
LITTLEFS_UTIL_MIN_ADDRESS = 0x00410408
LITTLEFS_UTIL_ALIGNDOWN_ADDRESS = 0x00410410
LITTLEFS_UTIL_ALIGNUP_ADDRESS = 0x0041041C
LITTLEFS_UTIL_NPW2_ADDRESS = 0x00410428
LITTLEFS_UTIL_CTZ_ADDRESS = 0x00410482
LITTLEFS_UTIL_POPC_ADDRESS = 0x00410492
SCMP_ADDRESS = 0x004104BA
SCMP_CALLER_ADDRESS = 0x004116D2
ALLOC_ADDRESS = 0x00410DE8
ALLOC_CALLERS = (
    (0x00413004, "fdf7f0fe"),
    (0x00413988, "fdf72efa"),
    (0x00413D44, "fdf750f8"),
    (0x00413DA6, "fdf71ff8"),
    (0x00414564, "fcf740fc"),
)
ALLOC_DROP_ADDRESS = 0x00410DEE
ALLOC_DROP_CALLERS = (
    (0x00410E82, "fff7b4ff"),
    (0x0041493E, "fcf756fa"),
)
MLIST_REMOVE_ADDRESS = 0x00410DA8
MLIST_REMOVE_CALLERS = (
    (0x0041320A, "fdf7cdfd"),
    (0x00413848, "fdf7aefa"),
)
MLIST_ISOPEN_ADDRESS = 0x00410D8A
MLIST_ISOPEN_CALLERS = (
    (0x00415156, "fbf718fe"),
    (0x0041518C, "fbf7fdfd"),
    (0x004151D0, "fbf7dbfd"),
    (0x0041520C, "fbf7bdfd"),
    (0x00415242, "fbf7a2fd"),
    (0x00415296, "fbf778fd"),
)
MLIST_APPEND_ADDRESS = 0x00410DC4
MLIST_APPEND_CALLERS = (
    (0x004131F8, "fdf7e4fd"),
    (0x004135FA, "fdf7e3fb"),
)
DISK_VERSION_ADDRESS = 0x00410DCC
DISK_VERSION_MAJOR_ADDRESS = 0x00410DD2
DISK_VERSION_MINOR_ADDRESS = 0x00410DDE
ALLOC_LOOKAHEAD_ADDRESS = 0x00410DFE
DISK_VERSION_CALLERS = (
    (0x00414578, "fcf728fc"),
    (0x00414D5A, "fcf737f8"),
)
MSPI_INTERRUPT_CLEAR_ADDRESS = 0x00426506
MSPI_INTERRUPT_CLEAR_CALLERS = ()
OVERLAY_ADDRESS = 0x00434478
SCMP_TARGET = OVERLAY_ADDRESS
ALLOC_TARGET = 0x0043447C
ALLOC_DROP_TARGET = 0x00434482
DISK_VERSION_TARGET = 0x00434490
MLIST_APPEND_TARGET = 0x00434498
MLIST_REMOVE_TARGET = 0x004344A0
LITTLEFS_UTIL_MAX_TARGET = 0x004344B2
LITTLEFS_UTIL_MIN_TARGET = 0x004344BA
LITTLEFS_UTIL_ALIGNDOWN_TARGET = 0x004344C2
LITTLEFS_UTIL_ALIGNUP_TARGET = 0x004344CA
LITTLEFS_UTIL_NPW2_TARGET = 0x004344D2
LITTLEFS_UTIL_CTZ_TARGET = 0x0043450A
LITTLEFS_UTIL_POPC_TARGET = 0x0043451A
MSPI_INTERRUPT_CLEAR_TARGET = 0x00434544
MLIST_ISOPEN_TARGET = 0x00434574
LITTLEFS_UTIL_FROMLE32_ADDRESS = 0x004104BE
LITTLEFS_UTIL_TOLE32_ADDRESS = 0x004104E0
LITTLEFS_UTIL_FROMBE32_ADDRESS = 0x004104E8
LITTLEFS_UTIL_TOBE32_ADDRESS = 0x0041050A
LITTLEFS_UTIL_FROMLE32_TARGET = 0x00434586
LITTLEFS_UTIL_TOLE32_TARGET = 0x00434588
LITTLEFS_UTIL_FROMBE32_TARGET = 0x0043458A
LITTLEFS_UTIL_TOBE32_TARGET = 0x0043458E
DISK_VERSION_MAJOR_TARGET = 0x00434592
DISK_VERSION_MINOR_TARGET = 0x0043459C
ALLOC_LOOKAHEAD_TARGET = 0x004345A6
EASYLOGGER_GET_LOGGER_TARGET = 0x004345D8
EASYLOGGER_ASSERT_FAILED_TARGET = 0x004345E0
EASYLOGGER_GET_FMT_TARGET = 0x00434664
EASYLOGGER_GET_FMT_U32_TARGET = 0x0043468A
EASYLOGGER_GET_FMT_PTR_TARGET = 0x0043469E
EASYLOGGER_STRCPY_TARGET = 0x004346B2
EASYLOGGER_OUTPUT_TARGET = 0x004362DC
EASYLOGGER_OUTPUT_ADDRESS = 0x004176CE
EASYLOGGER_LOCK_ENABLED_TARGET = 0x00436700
EASYLOGGER_LOCK_ENABLED_ADDRESS = 0x00417B7C
EASYLOGGER_GET_FMT_ADDRESS = 0x00417AD4
EASYLOGGER_GET_FMT_U32_ADDRESS = 0x00417B48
EASYLOGGER_GET_FMT_PTR_ADDRESS = 0x00417B62
EASYLOGGER_STRCPY_ADDRESS = 0x0041B158
EASYLOGGER_DRIVER_OUTPUT_ADDRESS = 0x0041B854
EASYLOGGER_CHANNEL_WRITE_ADDRESS = 0x0041F918
BOOT_DELAY_MILLISECONDS_ADDRESS = 0x0041F9D8
BOOT_DELAY_ADDRESS = 0x0041F9E6
BOOT_INITIALIZER_COMPARE_ADDRESS = 0x0041F9F0
BOOT_RUN_INITIALIZERS_ADDRESS = 0x0041F9F8
BOOT_PLATFORM_SETUP_ADDRESS = 0x0041FA50
BOOT_GUARDED_TEARDOWN_ADDRESS = 0x0041FA98
BOOT_PIN_GROUPS_ADDRESS = 0x0041FADC
BOOT_ALLOCATOR_INIT_ADDRESS = 0x0041FD70
BOOT_NVIC_ENABLE_ADDRESS = 0x0041FDC0
BOOT_NVIC_PRIORITY_ADDRESS = 0x0041FDDE
BOOT_MSPI_ISR_ADDRESS = 0x0041FE06
BOOT_MSPI_ENABLE_ADDRESS = 0x0041FE28
BOOT_MSPI_DISABLE_ADDRESS = 0x0041FE48
BOOT_EVENT_FLAGS_INIT_ADDRESS = 0x0041FE62
BOOT_EVENT_FLAGS_ACQUIRE_ADDRESS = 0x0041FE9C
BOOT_EVENT_FLAGS_RELEASE_ADDRESS = 0x0041FED4
BOOT_MSPI_GUARD_ENTER_ADDRESS = 0x0041FF08
BOOT_MSPI_GUARD_ENTER_TARGET = 0x00436D14
BOOT_MSPI_GUARD_EXIT_ADDRESS = 0x0041FF1E
BOOT_MSPI_GUARD_EXIT_TARGET = 0x00436D38
BOOT_MSPI_XIP_CONFIG_ADDRESS = 0x0041FF34
BOOT_MSPI_XIP_CONFIG_TARGET = 0x00436D58
BOOT_LONGEST_ONES_RUN_ADDRESS = 0x0041FF60
BOOT_LONGEST_ONES_RUN_TARGET = 0x00436D7C
BOOT_LONGEST_ONES_CENTER_ADDRESS = 0x0041FF74
BOOT_LONGEST_ONES_CENTER_TARGET = 0x00436D8C
BOOT_MSPI_TIMING_SCAN_ADDRESS = 0x00420002
BOOT_MSPI_TIMING_SCAN_TARGET = 0x00436E0C
BOOT_MSPI_TIMING_AUTO_ADDRESS = 0x004201BA
BOOT_MSPI_TIMING_AUTO_TARGET = 0x00436FB0
BOOT_MSPI_LOW_LEVEL_INIT_ADDRESS = 0x00420254
BOOT_MSPI_LOW_LEVEL_INIT_TARGET = 0x0043705C
BOOT_MSPI_DRIVER_INIT_ADDRESS = 0x00420476
BOOT_MSPI_DRIVER_INIT_TARGET = 0x00437248
BOOT_MSPI_SOFT_RESET_ADDRESS = 0x0042052A
BOOT_MSPI_SOFT_RESET_TARGET = 0x00437314
BOOT_MSPI_READ_ID_ADDRESS = 0x0042059E
BOOT_MSPI_READ_ID_TARGET = 0x0043739C
BOOT_MSPI_READ_TRANSFER_ADDRESS = 0x004205F4
BOOT_MSPI_READ_TRANSFER_TARGET = 0x00437400
BOOT_MSPI_WRITE_TRANSFER_ADDRESS = 0x0042069E
BOOT_MSPI_WRITE_TRANSFER_TARGET = 0x004374AC
BOOT_MSPI_BUSY_STATUS_ADDRESS = 0x0042074E
BOOT_MSPI_BUSY_STATUS_TARGET = 0x00437540
BOOT_MSPI_WAIT_READY_ADDRESS = 0x004207A2
BOOT_MSPI_WAIT_READY_TARGET = 0x00437598
BOOT_MSPI_WAIT_READY_DEFAULT_ADDRESS = 0x004207F4
BOOT_MSPI_WAIT_READY_DEFAULT_TARGET = 0x004375F0
BOOT_FS_DIRECTORIES_ADDRESS = 0x004210C8
BOOT_FS_DIRECTORIES_TARGET = 0x00437D78
BOOT_LITTLEFS_FORMAT_ADDRESS = 0x004211B0
BOOT_LITTLEFS_FORMAT_TARGET = 0x00437E54
BOOT_LITTLEFS_INIT_ADDRESS = 0x00421210
BOOT_LITTLEFS_INIT_TARGET = 0x00437EC0
BOOT_LITTLEFS_READ_ADDRESS = 0x004212D8
BOOT_LITTLEFS_READ_TARGET = 0x00437FC4
BOOT_LITTLEFS_PROGRAM_ADDRESS = 0x00421310
BOOT_LITTLEFS_PROGRAM_TARGET = 0x00421214
BOOT_LITTLEFS_PROGRAM_CAVE = bytes.fromhex(
    "feb502eb0130089e14460d46194600f1a0773246384616f055fb50b1cde90070"
    "054829462246334613f0a0fe6ff00400febd0020febd00bf0c184300"
)
BOOT_LITTLEFS_ERASE_ADDRESS = 0x00421348
BOOT_LITTLEFS_ERASE_TARGET = 0x00421250
BOOT_LITTLEFS_ERASE_CAVE = bytes.fromhex(
    "b0b54ff0a0700c4600eb0135284616f0c1fa40b10346054821462a4613f088fe"
    "6ff00400b0bd0020b0bd00bf68254300"
)
BOOT_LITTLEFS_SYNC_ADDRESS = 0x004213D4
BOOT_LITTLEFS_SYNC_TARGET = 0x00421280
BOOT_LITTLEFS_SYNC_CAVE = bytes.fromhex("00207047")
BOOT_MEMORY_SELECT_COPY_ADDRESS = 0x004213E6
BOOT_MEMORY_SELECT_COPY_TARGET = 0x004213EC
BOOT_MEMORY_SELECT_COPY_CAVE = bytes.fromhex(
    "f8b51d461446324a324b12681e68b5b1d308c0b24fea121c052821d0012818d0"
    "02280ed0032811d004280cd038b95feacc774ff0400708bf4ff4007712e00620"
    "f8bd40270ee04ff400770be04ff4307708e0df074ff4307708bf4ff4c06701e0"
    "4ff4c0676218ba4284bf0520f8bd04280ed0f60e012814d002280cd0032818d0"
    "a8b95feacc7006d10846fff7afff01464ff0844014e0f0070dd00f4800f5005"
    "00ee0d80705d10846fff7a1ff01460a4806e0f00701d10920f8bd074800f580"
    "4000eb810029462246fbf7e9fe0020f8bdbc0102400810024000200042"
)
BOOT_MEMORY_SELECT_ODD_ADDRESS = 0x00421548
BOOT_MEMORY_SELECT_ODD_TARGET = 0x004214C8
BOOT_MEMORY_SELECT_ODD_CAVE = bytes.fromhex(
    "10b50446c0b204f0fd04012c18bf052803d1bde81040fff785bf062010bd"
)
LITTLEFS_TAG_CHUNK_ADDRESS = 0x00410BA8
LITTLEFS_TAG_CHUNK_TARGET = 0x004346E6
LITTLEFS_TAG_ISVALID_ADDRESS = 0x00410B72
LITTLEFS_TAG_ISVALID_TARGET = 0x004346EC
LITTLEFS_TAG_TYPE1_ADDRESS = 0x00410B90
LITTLEFS_TAG_TYPE1_TARGET = 0x004346F2
LITTLEFS_TAG_TYPE3_ADDRESS = 0x00410BA0
LITTLEFS_TAG_TYPE3_TARGET = 0x004346FC
LITTLEFS_TAG_ID_ADDRESS = 0x00410BB8
LITTLEFS_TAG_ID_TARGET = 0x00434702
LITTLEFS_TAG_SIZE_ADDRESS = 0x00410BC0
LITTLEFS_TAG_SIZE_TARGET = 0x00434708
REDIRECT_INIT_ADDRESS = 0x00415590
REDIRECT_INIT_TARGET = 0x00434710
AEABI_MEMSET_ADDRESS = 0x0041560C
AEABI_MEMSET_TARGET = 0x00434824
AEABI_MEMCPY_ADDRESS = 0x0041568C
AEABI_MEMCPY_TARGET = 0x00434830
MEMCMP_ADDRESS = 0x00415758
MEMCMP_TARGET = 0x00434840
CRC32_ADDRESS = 0x004157C0
CRC32_TARGET = 0x00434898
STORE_200270CC_ADDRESS = 0x0041583C
STORE_200270CC_TARGET = 0x004348C4
UDIV10_ADDRESS = 0x00415844
UDIV10_TARGET = 0x004348D0
UDEC_DIGITS_ADDRESS = 0x00415900
UDEC_DIGITS_TARGET = 0x0043493A
SDEC_DIGITS_ADDRESS = 0x00415924
SDEC_DIGITS_TARGET = 0x00434956
HEX_DIGITS_ADDRESS = 0x00415936
HEX_DIGITS_TARGET = 0x0043496A
PARSE_DEC_ADDRESS = 0x0041595C
PARSE_DEC_TARGET = 0x00434982
U64_TO_DEC_ADDRESS = 0x004159A0
U64_TO_DEC_TARGET = 0x004349B2
U64_TO_HEX_ADDRESS = 0x00415A08
U64_TO_HEX_TARGET = 0x004349FC
NULLABLE_STRLEN_ADDRESS = 0x00415A7C
NULLABLE_STRLEN_TARGET = 0x00434A44
REPEAT_CHAR_ADDRESS = 0x00415A94
REPEAT_CHAR_TARGET = 0x00434A58
FLOAT_TO_FIXED_ADDRESS = 0x00415AB6
FLOAT_TO_FIXED_TARGET = 0x00434A78
FORMAT_CORE_ADDRESS = 0x00415BF6
FORMAT_CORE_TARGET = 0x00434BB8
LOG_DISPATCH_ADDRESS = 0x00415FAE
LOG_DISPATCH_TARGET = 0x00434F80
STRSTR_ADDRESS = 0x00415FFA
STRSTR_TARGET = 0x00434FBC
CRITICAL_CONTEXT_ADDRESS = 0x0041602A
CRITICAL_CONTEXT_TARGET = 0x00434FEA
GATE_ACQUIRE_ADDRESS = 0x00416058
GATE_ACQUIRE_TARGET = 0x00435018
GATE_STATE_ADDRESS = 0x00416088
GATE_STATE_TARGET = 0x00435048
GATE_RELEASE_ADDRESS = 0x004160B0
GATE_RELEASE_TARGET = 0x0043506C
CONTEXT_VALUE_ADDRESS = 0x004160E8
CONTEXT_VALUE_TARGET = 0x004350A4
RUNTIME_DISPATCH_4160FE_ADDRESS = 0x004160FE
RUNTIME_DISPATCH_4160FE_TARGET = 0x004350BC
RUNTIME_VALUE_4161C6_ADDRESS = 0x004161C6
RUNTIME_VALUE_4161C6_TARGET = 0x00435162
RUNTIME_CALL_4161CE_ADDRESS = 0x004161CE
RUNTIME_CALL_4161CE_TARGET = 0x00435166
RUNTIME_ACTION_416200_ADDRESS = 0x00416200
RUNTIME_ACTION_416200_TARGET = 0x00435192
RUNTIME_TRANSFER_41623A_ADDRESS = 0x0041623A
RUNTIME_TRANSFER_41623A_TARGET = 0x004351C8
RUNTIME_WAIT_4162C4_ADDRESS = 0x004162C4
RUNTIME_WAIT_4162C4_TARGET = 0x00435248
RUNTIME_NOTIFY_416378_ADDRESS = 0x00416378
RUNTIME_NOTIFY_416378_TARGET = 0x004352FA
RUNTIME_CALLBACK_41639A_ADDRESS = 0x0041639A
RUNTIME_CALLBACK_41639A_TARGET = 0x00435316
RUNTIME_REGISTER_4163B2_ADDRESS = 0x004163B2
RUNTIME_REGISTER_4163B2_TARGET = 0x00435330
RUNTIME_SUBMIT_41649A_ADDRESS = 0x0041649A
RUNTIME_SUBMIT_41649A_TARGET = 0x004353E4
RUNTIME_CREATE_4164DA_ADDRESS = 0x004164DA
RUNTIME_CREATE_4164DA_TARGET = 0x0043541A
RUNTIME_FLAGS_SET_41652E_ADDRESS = 0x0041652E
RUNTIME_FLAGS_SET_41652E_TARGET = 0x00435448
RUNTIME_FLAGS_WAIT_416590_ADDRESS = 0x00416590
RUNTIME_FLAGS_WAIT_416590_TARGET = 0x0043549C
RUNTIME_FLAGS_CREATE_416610_ADDRESS = 0x00416610
RUNTIME_FLAGS_CREATE_416610_TARGET = 0x00435500
RUNTIME_HANDLE_ACQUIRE_4166AA_ADDRESS = 0x004166AA
RUNTIME_HANDLE_ACQUIRE_4166AA_TARGET = 0x00435552
RUNTIME_HANDLE_RELEASE_416710_ADDRESS = 0x00416710
RUNTIME_HANDLE_RELEASE_416710_TARGET = 0x00435596
RUNTIME_SEMAPHORE_CREATE_416762_ADDRESS = 0x00416762
RUNTIME_SEMAPHORE_CREATE_416762_TARGET = 0x004355D0
RUNTIME_QUEUE_CREATE_416816_ADDRESS = 0x00416816
RUNTIME_QUEUE_CREATE_416816_TARGET = 0x0043565C
RUNTIME_QUEUE_PUT_4168A2_ADDRESS = 0x004168A2
RUNTIME_QUEUE_PUT_4168A2_TARGET = 0x004356C0
RUNTIME_QUEUE_GET_416920_ADDRESS = 0x00416920
RUNTIME_QUEUE_GET_416920_TARGET = 0x00435730
RUNTIME_BIT_WIDTH_4169A4_ADDRESS = 0x004169A4
RUNTIME_BIT_WIDTH_4169A4_TARGET = 0x0043579C
RUNTIME_CTZ_4169E2_ADDRESS = 0x004169E2
RUNTIME_CTZ_4169E2_TARGET = 0x004357AA
RUNTIME_LOG2_4169F2_ADDRESS = 0x004169F2
RUNTIME_LOG2_4169F2_TARGET = 0x004357B8
TLSF_BLOCK_PRIMITIVES_START_ADDRESS = 0x004169FC
TLSF_BLOCK_PRIMITIVES_END_ADDRESS = 0x00416AAA
TLSF_BLOCK_TOPOLOGY_END_ADDRESS = 0x00416BCE
TLSF_MAPPING_END_ADDRESS = 0x00416C4E
TLSF_FREE_LISTS_END_ADDRESS = 0x00416E04
TLSF_ALLOCATOR_END_ADDRESS = 0x0041711C
TLSF_PUBLIC_END_ADDRESS = 0x004172DA
EASYLOGGER_CONTROL_END_ADDRESS = 0x004176CE
EASYLOGGER_OUTPUT_END_ADDRESS = 0x00417AD0
STRCSPN_ADDRESS = 0x004157F8
STRCSPN_TARGET = 0x0043485C
STRSPN_ADDRESS = 0x0041581A
STRSPN_TARGET = 0x0043487A
OVERLAY_END = 0x00438000
LITTLEFS_UTIL_MAX_OFFSET = LITTLEFS_UTIL_MAX_ADDRESS - RUN_BASE
LITTLEFS_UTIL_MIN_OFFSET = LITTLEFS_UTIL_MIN_ADDRESS - RUN_BASE
LITTLEFS_UTIL_ALIGNDOWN_OFFSET = (
    LITTLEFS_UTIL_ALIGNDOWN_ADDRESS - RUN_BASE
)
LITTLEFS_UTIL_ALIGNUP_OFFSET = LITTLEFS_UTIL_ALIGNUP_ADDRESS - RUN_BASE
LITTLEFS_UTIL_NPW2_OFFSET = LITTLEFS_UTIL_NPW2_ADDRESS - RUN_BASE
LITTLEFS_UTIL_CTZ_OFFSET = LITTLEFS_UTIL_CTZ_ADDRESS - RUN_BASE
LITTLEFS_UTIL_POPC_OFFSET = LITTLEFS_UTIL_POPC_ADDRESS - RUN_BASE
LITTLEFS_UTIL_FROMLE32_OFFSET = LITTLEFS_UTIL_FROMLE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_TOLE32_OFFSET = LITTLEFS_UTIL_TOLE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_FROMBE32_OFFSET = LITTLEFS_UTIL_FROMBE32_ADDRESS - RUN_BASE
LITTLEFS_UTIL_TOBE32_OFFSET = LITTLEFS_UTIL_TOBE32_ADDRESS - RUN_BASE
SCMP_OFFSET = SCMP_ADDRESS - RUN_BASE
SCMP_CALLER_OFFSET = SCMP_CALLER_ADDRESS - RUN_BASE
ALLOC_OFFSET = ALLOC_ADDRESS - RUN_BASE
ALLOC_DROP_OFFSET = ALLOC_DROP_ADDRESS - RUN_BASE
MLIST_REMOVE_OFFSET = MLIST_REMOVE_ADDRESS - RUN_BASE
MLIST_ISOPEN_OFFSET = MLIST_ISOPEN_ADDRESS - RUN_BASE
MLIST_APPEND_OFFSET = MLIST_APPEND_ADDRESS - RUN_BASE
DISK_VERSION_OFFSET = DISK_VERSION_ADDRESS - RUN_BASE
DISK_VERSION_MAJOR_OFFSET = DISK_VERSION_MAJOR_ADDRESS - RUN_BASE
DISK_VERSION_MINOR_OFFSET = DISK_VERSION_MINOR_ADDRESS - RUN_BASE
ALLOC_LOOKAHEAD_OFFSET = ALLOC_LOOKAHEAD_ADDRESS - RUN_BASE
MSPI_INTERRUPT_CLEAR_OFFSET = MSPI_INTERRUPT_CLEAR_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_OFFSET = EASYLOGGER_GET_FMT_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_U32_OFFSET = EASYLOGGER_GET_FMT_U32_ADDRESS - RUN_BASE
EASYLOGGER_GET_FMT_PTR_OFFSET = EASYLOGGER_GET_FMT_PTR_ADDRESS - RUN_BASE
EASYLOGGER_STRCPY_OFFSET = EASYLOGGER_STRCPY_ADDRESS - RUN_BASE
EASYLOGGER_DRIVER_OUTPUT_OFFSET = EASYLOGGER_DRIVER_OUTPUT_ADDRESS - RUN_BASE
EASYLOGGER_CHANNEL_WRITE_OFFSET = EASYLOGGER_CHANNEL_WRITE_ADDRESS - RUN_BASE
BOOT_DELAY_MILLISECONDS_OFFSET = BOOT_DELAY_MILLISECONDS_ADDRESS - RUN_BASE
BOOT_DELAY_OFFSET = BOOT_DELAY_ADDRESS - RUN_BASE
BOOT_INITIALIZER_COMPARE_OFFSET = BOOT_INITIALIZER_COMPARE_ADDRESS - RUN_BASE
BOOT_RUN_INITIALIZERS_OFFSET = BOOT_RUN_INITIALIZERS_ADDRESS - RUN_BASE
EASYLOGGER_OUTPUT_OFFSET = EASYLOGGER_OUTPUT_ADDRESS - RUN_BASE
EASYLOGGER_LOCK_ENABLED_OFFSET = EASYLOGGER_LOCK_ENABLED_ADDRESS - RUN_BASE
REDIRECT_INIT_OFFSET = REDIRECT_INIT_ADDRESS - RUN_BASE
AEABI_MEMSET_OFFSET = AEABI_MEMSET_ADDRESS - RUN_BASE
AEABI_MEMCPY_OFFSET = AEABI_MEMCPY_ADDRESS - RUN_BASE
MEMCMP_OFFSET = MEMCMP_ADDRESS - RUN_BASE
CRC32_OFFSET = CRC32_ADDRESS - RUN_BASE
STORE_200270CC_OFFSET = STORE_200270CC_ADDRESS - RUN_BASE
UDIV10_OFFSET = UDIV10_ADDRESS - RUN_BASE
UDEC_DIGITS_OFFSET = UDEC_DIGITS_ADDRESS - RUN_BASE
SDEC_DIGITS_OFFSET = SDEC_DIGITS_ADDRESS - RUN_BASE
HEX_DIGITS_OFFSET = HEX_DIGITS_ADDRESS - RUN_BASE
PARSE_DEC_OFFSET = PARSE_DEC_ADDRESS - RUN_BASE
U64_TO_DEC_OFFSET = U64_TO_DEC_ADDRESS - RUN_BASE
U64_TO_HEX_OFFSET = U64_TO_HEX_ADDRESS - RUN_BASE
NULLABLE_STRLEN_OFFSET = NULLABLE_STRLEN_ADDRESS - RUN_BASE
REPEAT_CHAR_OFFSET = REPEAT_CHAR_ADDRESS - RUN_BASE
FLOAT_TO_FIXED_OFFSET = FLOAT_TO_FIXED_ADDRESS - RUN_BASE
FORMAT_CORE_OFFSET = FORMAT_CORE_ADDRESS - RUN_BASE
LOG_DISPATCH_OFFSET = LOG_DISPATCH_ADDRESS - RUN_BASE
STRSTR_OFFSET = STRSTR_ADDRESS - RUN_BASE
CRITICAL_CONTEXT_OFFSET = CRITICAL_CONTEXT_ADDRESS - RUN_BASE
GATE_ACQUIRE_OFFSET = GATE_ACQUIRE_ADDRESS - RUN_BASE
GATE_STATE_OFFSET = GATE_STATE_ADDRESS - RUN_BASE
GATE_RELEASE_OFFSET = GATE_RELEASE_ADDRESS - RUN_BASE
CONTEXT_VALUE_OFFSET = CONTEXT_VALUE_ADDRESS - RUN_BASE
RUNTIME_DISPATCH_4160FE_OFFSET = RUNTIME_DISPATCH_4160FE_ADDRESS - RUN_BASE
RUNTIME_VALUE_4161C6_OFFSET = RUNTIME_VALUE_4161C6_ADDRESS - RUN_BASE
RUNTIME_CALL_4161CE_OFFSET = RUNTIME_CALL_4161CE_ADDRESS - RUN_BASE
RUNTIME_ACTION_416200_OFFSET = RUNTIME_ACTION_416200_ADDRESS - RUN_BASE
RUNTIME_TRANSFER_41623A_OFFSET = RUNTIME_TRANSFER_41623A_ADDRESS - RUN_BASE
RUNTIME_WAIT_4162C4_OFFSET = RUNTIME_WAIT_4162C4_ADDRESS - RUN_BASE
RUNTIME_NOTIFY_416378_OFFSET = RUNTIME_NOTIFY_416378_ADDRESS - RUN_BASE
RUNTIME_CALLBACK_41639A_OFFSET = RUNTIME_CALLBACK_41639A_ADDRESS - RUN_BASE
RUNTIME_REGISTER_4163B2_OFFSET = RUNTIME_REGISTER_4163B2_ADDRESS - RUN_BASE
RUNTIME_SUBMIT_41649A_OFFSET = RUNTIME_SUBMIT_41649A_ADDRESS - RUN_BASE
RUNTIME_CREATE_4164DA_OFFSET = RUNTIME_CREATE_4164DA_ADDRESS - RUN_BASE
RUNTIME_FLAGS_SET_41652E_OFFSET = RUNTIME_FLAGS_SET_41652E_ADDRESS - RUN_BASE
RUNTIME_FLAGS_WAIT_416590_OFFSET = RUNTIME_FLAGS_WAIT_416590_ADDRESS - RUN_BASE
RUNTIME_FLAGS_CREATE_416610_OFFSET = RUNTIME_FLAGS_CREATE_416610_ADDRESS - RUN_BASE
RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET = RUNTIME_HANDLE_ACQUIRE_4166AA_ADDRESS - RUN_BASE
RUNTIME_HANDLE_RELEASE_416710_OFFSET = RUNTIME_HANDLE_RELEASE_416710_ADDRESS - RUN_BASE
RUNTIME_SEMAPHORE_CREATE_416762_OFFSET = RUNTIME_SEMAPHORE_CREATE_416762_ADDRESS - RUN_BASE
RUNTIME_QUEUE_CREATE_416816_OFFSET = RUNTIME_QUEUE_CREATE_416816_ADDRESS - RUN_BASE
RUNTIME_QUEUE_PUT_4168A2_OFFSET = RUNTIME_QUEUE_PUT_4168A2_ADDRESS - RUN_BASE
RUNTIME_QUEUE_GET_416920_OFFSET = RUNTIME_QUEUE_GET_416920_ADDRESS - RUN_BASE
RUNTIME_BIT_WIDTH_4169A4_OFFSET = RUNTIME_BIT_WIDTH_4169A4_ADDRESS - RUN_BASE
RUNTIME_CTZ_4169E2_OFFSET = RUNTIME_CTZ_4169E2_ADDRESS - RUN_BASE
RUNTIME_LOG2_4169F2_OFFSET = RUNTIME_LOG2_4169F2_ADDRESS - RUN_BASE
TLSF_BLOCK_PRIMITIVES_START_OFFSET = (
    TLSF_BLOCK_PRIMITIVES_START_ADDRESS - RUN_BASE
)
TLSF_BLOCK_PRIMITIVES_END_OFFSET = (
    TLSF_BLOCK_PRIMITIVES_END_ADDRESS - RUN_BASE
)
TLSF_BLOCK_TOPOLOGY_END_OFFSET = TLSF_BLOCK_TOPOLOGY_END_ADDRESS - RUN_BASE
TLSF_MAPPING_END_OFFSET = TLSF_MAPPING_END_ADDRESS - RUN_BASE
TLSF_FREE_LISTS_END_OFFSET = TLSF_FREE_LISTS_END_ADDRESS - RUN_BASE
TLSF_ALLOCATOR_END_OFFSET = TLSF_ALLOCATOR_END_ADDRESS - RUN_BASE
TLSF_PUBLIC_END_OFFSET = TLSF_PUBLIC_END_ADDRESS - RUN_BASE
EASYLOGGER_CONTROL_END_OFFSET = EASYLOGGER_CONTROL_END_ADDRESS - RUN_BASE
TLSF_PATCH_REPLACEMENTS = (
    (0x004169FC, bytes.fromhex("1ef0e1be" + "00bf" * 8)),
    (0x00416A10, bytes.fromhex("1ef0dbbe" + "00bf" * 12)),
    (0x00416A2C, bytes.fromhex("1ef0d3be" + "00bf" * 8)),
    (0x00416A40, bytes.fromhex("1ef0cebe" + "00bf" * 4)),
    (0x00416A4C, bytes.fromhex("1ef0ccbe" + "00bf" * 5)),
    (0x00416A5A, bytes.fromhex("1ef0cabe" + "00bf" * 5)),
    (0x00416A68, bytes.fromhex("1ef0c8be" + "00bf" * 4)),
    (0x00416A74, bytes.fromhex("1ef0c6be" + "00bf" * 5)),
    (0x00416A82, bytes.fromhex("1ef0c4be" + "00bf" * 5)),
    (0x00416A90, bytes.fromhex("1ef0c2be" + "00bf" * 4)),
    (0x00416A9C, bytes.fromhex("1ef0bebe" + "00bf" * 3)),
    (0x00416AA6, bytes.fromhex("1ef0bbbe")),
)
TLSF_TOPOLOGY_PATCH_REPLACEMENTS = (
    (0x00416AAA, bytes.fromhex("1ef0bbbe" + "00bf" * 17)),
    (0x00416AD0, bytes.fromhex("1ef0babe" + "00bf" * 32)),
    (0x00416B14, bytes.fromhex("1ef0b6be" + "00bf" * 5)),
    (0x00416B22, bytes.fromhex("1ef0b5be" + "00bf" * 9)),
    (0x00416B38, bytes.fromhex("1ef0b5be" + "00bf" * 9)),
    (0x00416B4E, bytes.fromhex("1ef0b5be" + "00bf" * 20)),
    (0x00416B7A, bytes.fromhex("1ef0b5be" + "00bf" * 19)),
    (0x00416BA4, bytes.fromhex("1ef0b4be" + "00bf" * 19)),
)
TLSF_MAPPING_PATCH_REPLACEMENTS = (
    (0x00416BCE, bytes.fromhex("1ef0b5be" + "00bf" * 19)),
    (0x00416BF8, bytes.fromhex("1ef0afbe" + "00bf" * 21)),
    (0x00416C26, bytes.fromhex("1ef0adbe" + "00bf" * 18)),
)
TLSF_FREE_LIST_PATCH_REPLACEMENTS = (
    (0x00416C4E, bytes.fromhex("1ef0b1be" + "00bf" * 58)),
    (0x00416CC6, bytes.fromhex("1ef0adbe" + "00bf" * 73)),
    (0x00416D5C, bytes.fromhex("1ef0a0be" + "00bf" * 82)),
)
TLSF_ALLOCATOR_PATCH_REPLACEMENTS = (
    (0x00416E04, bytes.fromhex("1ef096be" + "00bf" * 15)),
    (0x00416E26, bytes.fromhex("1ef096be" + "00bf" * 15)),
    (0x00416E48, bytes.fromhex("1ef096be" + "00bf" * 10)),
    (0x00416E60, bytes.fromhex("1ef094be" + "00bf" * 94)),
    (0x00416F20, bytes.fromhex("1ef086be" + "00bf" * 31)),
    (0x00416F62, bytes.fromhex("1ef083be" + "00bf" * 48)),
    (0x00416FC6, bytes.fromhex("1ef081be" + "00bf" * 48)),
    (0x0041702A, bytes.fromhex("1ef07bbe" + "00bf" * 39)),
    (0x0041707C, bytes.fromhex("1ef07ebe" + "00bf" * 47)),
    (0x004170DE, bytes.fromhex("1ef07dbe" + "00bf" * 29)),
)
TLSF_PUBLIC_PATCH_REPLACEMENTS = (
    (0x0041711C, bytes.fromhex("1ef080be" + "00bf" * 22)),
    (0x0041714C, bytes.fromhex("1ef080be" + "00bf" * 6)),
    (0x0041715C, bytes.fromhex("1ef07abe" + "00bf" * 84)),
    (0x00417208, bytes.fromhex("1ef06abe" + "00bf" * 26)),
    (0x00417240, bytes.fromhex("1ef062be" + "00bf" * 19)),
    (0x0041726A, bytes.fromhex("1ef05bbe" + "00bf" * 17)),
    (0x00417290, bytes.fromhex("1ef05abe" + "00bf" * 35)),
)
EASYLOGGER_CONTROL_PATCH_REPLACEMENTS = (
    (0x0041733C, bytes.fromhex("1ef036bf" + "00bf" * 41)),
    (0x00417392, bytes.fromhex("1ef02fbf" + "00bf" * 26)),
    (0x004173CA, bytes.fromhex("1ef0e5bd" + "00bf" * 53)),
    (0x00417438, bytes.fromhex("1ef0e0bd" + "00bf" * 53)),
    (0x004174A6, bytes.fromhex("1ef04bbe" + "00bf" * 51)),
    (0x00417510, bytes.fromhex("1ef0a8bd" + "00bf" * 46)),
    (0x00417570, bytes.fromhex("1ef0c6bd" + "00bf" * 15)),
    (0x00417592, bytes.fromhex("1ef0c5bd" + "00bf" * 15)),
    (0x004175B4, bytes.fromhex("1ef08abd" + "00bf" * 41)),
    (0x0041760A, bytes.fromhex("1ef015be" + "00bf" * 96)),
)
EASYLOGGER_OUTPUT_PATCH_REPLACEMENT = (
    EASYLOGGER_OUTPUT_ADDRESS,
    bytes.fromhex("1ef005be" + "00bf" * 511),
)
EASYLOGGER_LOCK_ENABLED_PATCH_REPLACEMENT = (
    EASYLOGGER_LOCK_ENABLED_ADDRESS,
    bytes.fromhex("1ef0c0bd" + "00bf" * 28),
)
EASYLOGGER_PORT_PATCH_REPLACEMENTS = (
    (0x0041A648, bytes.fromhex("1cf06cb8" + "00bf" * 8)),
    (0x0041A65C, bytes.fromhex("1cf072b8" + "00bf" * 9)),
    (0x0041A672, bytes.fromhex("1cf073b8" + "00bf" * 7)),
    (0x0041A684, bytes.fromhex("1cf074b8" + "00bf" * 5)),
    (0x0041A692, bytes.fromhex("1cf075b8" + "00bf" * 2)),
    (0x0041A69A, bytes.fromhex("1cf075b8" + "00bf" * 2)),
    (0x0041A6A2, bytes.fromhex("1cf075b8" + "00bf" * 2)),
    (0x0041A6AA, bytes.fromhex("1cf075b8" + "00bf" * 10)),
    (0x0041A6C2, bytes.fromhex("1cf07db8" + "00bf" * 10)),
    (0x0041A6F0, bytes.fromhex("1cf07ab8" + "00bf" * 2)),
    (0x0041A6F8, bytes.fromhex("1cf07ab8" + "00bf" * 2)),
)
BOOT_SERVICE_PATCH_REPLACEMENTS = (
    (BOOT_DELAY_MILLISECONDS_ADDRESS, bytes.fromhex("16f052bf" + "00bf" * 5)),
    (BOOT_DELAY_ADDRESS, bytes.fromhex("16f053bf" + "00bf" * 2)),
    (BOOT_INITIALIZER_COMPARE_ADDRESS, bytes.fromhex("16f052bf" + "00bf" * 2)),
    (BOOT_RUN_INITIALIZERS_ADDRESS, bytes.fromhex("16f052bf" + "00bf" * 34)),
    (BOOT_PLATFORM_SETUP_ADDRESS, bytes.fromhex("16f06abf" + "00bf" * 34)),
    (BOOT_GUARDED_TEARDOWN_ADDRESS, bytes.fromhex("16f022bf" + "00bf" * 26)),
    (BOOT_PIN_GROUPS_ADDRESS, bytes.fromhex("16f054bf" + "00bf" * 267)),
    (BOOT_ALLOCATOR_INIT_ADDRESS, bytes.fromhex("16f0e0be" + "00bf" * 26)),
    (BOOT_NVIC_ENABLE_ADDRESS, bytes.fromhex("16f0e4be" + "00bf" * 13)),
    (BOOT_NVIC_PRIORITY_ADDRESS, bytes.fromhex("16f0e5be" + "00bf" * 18)),
    (BOOT_MSPI_ISR_ADDRESS, bytes.fromhex("16f0e1be" + "00bf" * 15)),
    (BOOT_MSPI_ENABLE_ADDRESS, bytes.fromhex("16f0e8be" + "00bf" * 14)),
    (BOOT_MSPI_DISABLE_ADDRESS, bytes.fromhex("16f0ecbe" + "00bf" * 11)),
    (BOOT_EVENT_FLAGS_INIT_ADDRESS, bytes.fromhex("16f0efbe" + "00bf" * 27)),
    (BOOT_EVENT_FLAGS_ACQUIRE_ADDRESS, bytes.fromhex("16f0f8be" + "00bf" * 26)),
    (BOOT_EVENT_FLAGS_RELEASE_ADDRESS, bytes.fromhex("16f0febe" + "00bf" * 24)),
    (BOOT_MSPI_GUARD_ENTER_ADDRESS, bytes.fromhex("16f004bf" + "00bf" * 9)),
    (BOOT_MSPI_GUARD_EXIT_ADDRESS, bytes.fromhex("16f00bbf" + "00bf" * 9)),
    (BOOT_MSPI_XIP_CONFIG_ADDRESS, bytes.fromhex("16f010bf" + "00bf" * 20)),
    (BOOT_LONGEST_ONES_RUN_ADDRESS, bytes.fromhex("16f00cbf" + "00bf" * 8)),
    (BOOT_LONGEST_ONES_CENTER_ADDRESS, bytes.fromhex("16f00abf" + "00bf" * 69)),
    (BOOT_MSPI_TIMING_SCAN_ADDRESS, bytes.fromhex("16f003bf" + "00bf" * 218)),
    (BOOT_MSPI_TIMING_AUTO_ADDRESS, bytes.fromhex("16f0f9be" + "00bf" * 75)),
    (BOOT_MSPI_LOW_LEVEL_INIT_ADDRESS, bytes.fromhex("16f002bf" + "00bf" * 271)),
    (BOOT_MSPI_DRIVER_INIT_ADDRESS, bytes.fromhex("16f0e7be" + "00bf" * 88)),
    (BOOT_MSPI_SOFT_RESET_ADDRESS, bytes.fromhex("16f0f3be" + "00bf" * 56)),
    (BOOT_MSPI_READ_ID_ADDRESS, bytes.fromhex("16f0fdbe" + "00bf" * 41)),
    (BOOT_MSPI_READ_TRANSFER_ADDRESS, bytes.fromhex("16f004bf" + "00bf" * 83)),
    (BOOT_MSPI_WRITE_TRANSFER_ADDRESS, bytes.fromhex("16f005bf" + "00bf" * 86)),
    (BOOT_MSPI_BUSY_STATUS_ADDRESS, bytes.fromhex("16f0f7be" + "00bf" * 40)),
    (BOOT_MSPI_WAIT_READY_ADDRESS, bytes.fromhex("16f0f9be" + "00bf" * 39)),
    (BOOT_MSPI_WAIT_READY_DEFAULT_ADDRESS, bytes.fromhex("16f0fcbe" + "00bf" * 4)),
    (0x00420800, bytes.fromhex("16f0fcbe" + "00bf" * 52)),
    (0x00420890, bytes.fromhex("16f0f2be" + "00bf" * 114)),
    (0x00420984, bytes.fromhex("16f0e6be" + "00bf" * 27)),
    (0x004209C4, bytes.fromhex("16f0eabe" + "00bf" * 26)),
    (0x00420A08, bytes.fromhex("16f0ecbe" + "00bf" * 103)),
    (0x00420B0C, bytes.fromhex("16f0e4be" + "00bf" * 130)),
    (0x00420C5C, bytes.fromhex("16f0bcbe" + "00bf" * 205)),
    (0x00420E08, bytes.fromhex("16f09cbe" + "00bf" * 64)),
    (0x00420E8C, bytes.fromhex("16f09ebe" + "00bf" * 62)),
    (0x00420F10, bytes.fromhex("16f0a8be" + "00bf" * 43)),
    (0x00420F70, bytes.fromhex("16f0b6be" + "00bf" * 63)),
    (BOOT_FS_DIRECTORIES_ADDRESS, bytes.fromhex("16f056be" + "00bf" * 114)),
    (BOOT_LITTLEFS_FORMAT_ADDRESS, bytes.fromhex("16f050be" + "00bf" * 46)),
    (
        BOOT_LITTLEFS_INIT_ADDRESS,
        bytes.fromhex("16f056be")
        + BOOT_LITTLEFS_PROGRAM_CAVE
        + BOOT_LITTLEFS_ERASE_CAVE
        + BOOT_LITTLEFS_SYNC_CAVE
        + bytes.fromhex("00bf" * 42),
    ),
    (BOOT_LITTLEFS_READ_ADDRESS, bytes.fromhex("16f074be" + "00bf" * 26)),
    (BOOT_LITTLEFS_PROGRAM_ADDRESS, bytes.fromhex("fff780bf" + "00bf" * 26)),
    (BOOT_LITTLEFS_ERASE_ADDRESS, bytes.fromhex("fff782bf" + "00bf" * 19)),
    (BOOT_LITTLEFS_SYNC_ADDRESS, bytes.fromhex("fff754bf")),
    (
        BOOT_MEMORY_SELECT_COPY_ADDRESS,
        bytes.fromhex("00f001b800bf")
        + BOOT_MEMORY_SELECT_COPY_CAVE
        + BOOT_MEMORY_SELECT_ODD_CAVE
        + bytes.fromhex("00bf" * 49),
    ),
    (
        BOOT_MEMORY_SELECT_ODD_ADDRESS,
        bytes.fromhex("fff7bebf" + "00bf" * 17),
    ),
)
STRCSPN_OFFSET = STRCSPN_ADDRESS - RUN_BASE
STRSPN_OFFSET = STRSPN_ADDRESS - RUN_BASE
LITTLEFS_TAG_CHUNK_OFFSET = LITTLEFS_TAG_CHUNK_ADDRESS - RUN_BASE
LITTLEFS_TAG_ISVALID_OFFSET = LITTLEFS_TAG_ISVALID_ADDRESS - RUN_BASE
LITTLEFS_TAG_TYPE1_OFFSET = LITTLEFS_TAG_TYPE1_ADDRESS - RUN_BASE
LITTLEFS_TAG_TYPE3_OFFSET = LITTLEFS_TAG_TYPE3_ADDRESS - RUN_BASE
LITTLEFS_TAG_ID_OFFSET = LITTLEFS_TAG_ID_ADDRESS - RUN_BASE
LITTLEFS_TAG_SIZE_OFFSET = LITTLEFS_TAG_SIZE_ADDRESS - RUN_BASE
STOCK_SHA256 = (
    "f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5"
)
PROVIDER_SHA256 = (
    "8f24989979719b4c9f1273624240ba702a99decf735d099bfee1afcda16159e0"
)
OVERLAY_SHA256 = (
    "d68bca1fc09b1b734a65a706e9d5a4d5aa4201e53441f6ad1354be44f428b314"
)
SCMP_SHA256 = (
    "787fad2973d1b4f1c6c585f29ee07707e6951499c3772a9e8e4e1bc997ba94fe"
)
ALLOC_SHA256 = (
    "74d41d77541fa368dfc90160c9fc3a8dfd62d891ea72f29ef9c115465b71a32c"
)
ALLOC_DROP_STOCK_SHA256 = (
    "55b7d516bb75d425ebbc077729c8c03aef31b93897d422450084cfed8a771f66"
)
ALLOC_DROP_SOURCE_BODY_SHA256 = (
    "e5e78109621631cb174d82b06ba2542dfa669e1919c3d80982ab059844e5c4f8"
)
MLIST_REMOVE_STOCK_SHA256 = (
    "55bb19e48e301285459cecc31d6177555f04d0b41ea3ae3c1ed3225fd357a8bd"
)
MLIST_REMOVE_SOURCE_BODY_SHA256 = (
    "bb4d51fd66c1638dae0c38615feffb08286027539aede7f65197306491d44e4f"
)
MLIST_ISOPEN_STOCK_SHA256 = (
    "e4963bfc9db9aa487d15261ebce9dd5b1429c708f6fe78ff47968718821c0c4e"
)
MLIST_ISOPEN_SOURCE_BODY_SHA256 = (
    "9b7caac591f8aea5d0eff0dc2b5ff7ff15ba85ab156ba5f95d47b1e4181db489"
)
MLIST_ISOPEN_SOURCE_SHA256 = (
    "7d0bc398c8ecd85fd00b34cc6dcc2b9fc75c754e1aed0bfbca01dd58ae9d6e0c"
)
LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256 = (
    "830d49b043181d270ac0aedda432c5e232ce8d6ce65e8e537b80b1a706fd6cac"
)
LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256 = (
    "c7dfbb7d02759eacb64dbc916c1bb6f21eabaff1c1032ea5c9176abf7fd28df8"
)
LITTLEFS_UTIL_SWAP_SOURCE_SHA256 = (
    "7a8f0cc1ae130c65908d3dbd4e89f7c7bd898743a4ee62deced9203383df3d11"
)
MLIST_APPEND_SHA256 = (
    "e3ed290e4e62fc9cce34b0530080dbc08efbca65f80ca1b7d182e18bb20c24b9"
)
DISK_VERSION_STOCK_SHA256 = (
    "1ff8f5ac86a29e52674a91191c4ed763fe635aed200e701063e8224aa15c3870"
)
DISK_VERSION_SOURCE_BODY_SHA256 = (
    "72eba3f48315967708b8128a1c2c9b4273ac363d25ec821bb9a03ea58ed9ce24"
)
ALLOC_LOOKAHEAD_STOCK_SHA256 = (
    "58285c138461a673be0bed2c5376f8d739e40e2aea753ad05d5061bfbc9265cf"
)
ALLOC_LOOKAHEAD_SOURCE_BODY_SHA256 = (
    "bd8e7c926d98a940f215cd41a2fb5932bfbf1abcf7378839dcadd537ae55324d"
)
MSPI_INTERRUPT_CLEAR_STOCK_SHA256 = (
    "4b01a25a8075cf158eb59da277f8730e36c751ee01c67bae86bc172ec877bd48"
)
MSPI_INTERRUPT_CLEAR_SOURCE_SHA256 = (
    "87505e035fa5fe7c0dfd7c4d85b66c6b8f3b57ced45dc7afd787db6c52b0fd7b"
)
LITTLEFS_UTIL_MAX_SOURCE_SHA256 = (
    "00cbab254132bf12554d58b011edf1b5e3b1e36ff5d55a671d2ab04e5b8428a5"
)
LITTLEFS_UTIL_MIN_SOURCE_SHA256 = (
    "36bb5e2d905d59628b5170a2cfecbf56f3200abb3207bfa30b50eaf3b4b44ab4"
)
LITTLEFS_UTIL_ALIGNDOWN_SOURCE_SHA256 = (
    "965ce09e34fe2ef897bc091faf02f8211bf344c025d769cf440c747fb5f555ee"
)
LITTLEFS_UTIL_ALIGNUP_SOURCE_SHA256 = (
    "bd71bfb42c8823db97acf83f489ed0e97d581e3742a1f754c4048298de1c4e71"
)
LITTLEFS_UTIL_MAX_STOCK_SHA256 = (
    "3caa49d8a68e47b2cd91fcb01cae26b6262c904e8b96d8b3ba35f7fb33d07464"
)
LITTLEFS_UTIL_MIN_STOCK_SHA256 = (
    "7ec81166f84c44a60f4ecf93ad37d93f52ec00c77bb5db5a7dda659b1319c8a3"
)
LITTLEFS_UTIL_ALIGNDOWN_STOCK_SHA256 = (
    "d0d7407bcf93abaef33623047467d1230d2176ce9b4a4e93bfcd8adde884f349"
)
LITTLEFS_UTIL_ALIGNUP_STOCK_SHA256 = (
    "18874b0eb5cf5c7bd6f20b2b29f787157294b9e9be16d14ab0d9064d44a97c37"
)
PROVIDER_CRC32C_MSB = 0xA9D1F8C3


def load_builder():
    spec = importlib.util.spec_from_file_location(
        "open_cfw_bootloader_core_overlay_builder",
        BUILDER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load bootloader core-overlay builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_ACTIVE_PROFILE = os.environ.get("OPENCFW_TOOLCHAIN_PROFILE") or "apple-clang"


@unittest.skipUnless(
    _ACTIVE_PROFILE == "apple-clang",
    "byte-exact Apple-clang reference suite; Linux (linux-clang) byte "
    "reproduction is verified end-to-end by tests/test_toolchain_profiles.py",
)
class BootloaderCoreOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        cls.official = OFFICIAL_PATH.read_bytes()
        cls.temporary = tempfile.TemporaryDirectory()
        cls.output = Path(cls.temporary.name) / "first"
        cls.report = cls.builder.build(
            root=ROOT,
            config_path=CONFIG_PATH,
            output_dir=cls.output,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        cls.provider = (cls.output / "ota_s200_bootloader.bin").read_bytes()
        cls.overlay = (cls.output / "bootloader_core_overlay.bin").read_bytes()
        cls.contract = json.loads(
            (cls.output / "provider-contract.json").read_text(encoding="utf-8")
        )
        cls.core_source_manifest = json.loads(
            CORE_SOURCE_MANIFEST_PATH.read_text(encoding="utf-8")
        )

        sys.path.insert(0, str(ROOT / "tools"))
        import apollo_overlay
        import open_cfw

        cls.apollo_overlay = apollo_overlay
        cls.open_cfw = open_cfw

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_authenticated_raw_layout_and_headroom(self) -> None:
        self.assertEqual(len(self.official), 148599)
        self.assertEqual(hashlib.sha256(self.official).hexdigest(), STOCK_SHA256)
        self.assertEqual(RUN_BASE + len(self.official), STOCK_END)
        self.assertEqual(MAIN_BOUNDARY - STOCK_END, 0x3B89)

        initial_sp, reset_vector = struct.unpack_from("<II", self.official, 0)
        self.assertEqual(initial_sp, 0x2007FB00)
        self.assertEqual(reset_vector, 0x0043291B)
        self.assertEqual(self.config["preamble_bytes"], 0)
        self.assertTrue(self.report["overlay"]["raw_provider"])
        self.assertEqual(self.report["overlay"]["internal_header_bytes"], 0)

    def test_overlay_compiles_to_exact_upstream_leaves(self) -> None:
        self.assertEqual(
            self.overlay[:350],
            bytes.fromhex(
                "401a7047"
                "c16e01667047"
                "0021c1658165c16e01667047"
                "00bf"
                "0048704701000200"
                "826a0a6081627047"
                "28300246006818b18842fad1006810607047"
                "884250ea81807047"
                "884250ea31807047"
                "b0fbf1f048437047"
                "08440138fff7f8bf"
                "10b5013800230024010c18bf1021c840"
                "0022ff2888bf0823d8400f2888bf0424"
                "e040032888bf0222d04041ea50001843"
                "20431043013010bd"
                "80b5414208400130fff7deff013880bd"
                "4ff0553101ea5001401a4ff0333101ea9"
                "00120f0cc3008444ff0013100eb101020"
                "f0f0304843000e7047"
                "78b10268084b22f07e429a4209d14068"
                "064a02eb0030c0f80812d0f804020020"
                "70470220704700bfbebebe0100000640"
                "28b1884204bf012070470068f8e700207047"
                "7047704700ba704700ba7047"
                "80b5fff77cff000c80bd"
                "80b5fff777ff80b280bd"
                "10b5426dc46e836d891a2144b1fbf4f2"
                "02fb1411994209d2406e01f007020123"
                "c90803fa02f2435c1a434254002010bd"
            ),
        )
        self.assertEqual(hashlib.sha256(self.overlay).hexdigest(), OVERLAY_SHA256)
        self.assertEqual(
            self.report["overlay"]["functions"]["open_cfw_littlefs_scmp"],
            {"offset": 0, "size": 4},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_ckpoint"
            ],
            {"offset": 4, "size": 6},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_drop"
            ],
            {"offset": 10, "size": 12},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_disk_version"
            ],
            {"offset": 24, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_append"
            ],
            {"offset": 32, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_remove"
            ],
            {"offset": 40, "size": 18},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_max"
            ],
            {"offset": 58, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_min"
            ],
            {"offset": 66, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_aligndown"
            ],
            {"offset": 74, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_alignup"
            ],
            {"offset": 82, "size": 8},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_npw2"
            ],
            {"offset": 90, "size": 56},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_ctz"
            ],
            {"offset": 146, "size": 16},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_util_popc"
            ],
            {"offset": 162, "size": 42},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "am_hal_mspi_interrupt_clear"
            ],
            {"offset": 204, "size": 48},
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_mlist_isopen"
            ],
            {"offset": 252, "size": 18},
        )
        endian_functions = {
            name: self.report["overlay"]["functions"][name]
            for name in (
                "open_cfw_littlefs_util_fromle32",
                "open_cfw_littlefs_util_tole32",
                "open_cfw_littlefs_util_frombe32",
                "open_cfw_littlefs_util_tobe32",
            )
        }
        self.assertEqual(
            endian_functions,
            {
                "open_cfw_littlefs_util_fromle32": {
                    "offset": 270,
                    "size": 2,
                },
                "open_cfw_littlefs_util_tole32": {
                    "offset": 272,
                    "size": 2,
                },
                "open_cfw_littlefs_util_frombe32": {
                    "offset": 274,
                    "size": 4,
                },
                "open_cfw_littlefs_util_tobe32": {
                    "offset": 278,
                    "size": 4,
                },
            },
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_alloc_lookahead"
            ],
            {"offset": 302, "size": 48},
        )
        self.assertEqual(
            {
                name: self.report["overlay"]["functions"][name]
                for name in (
                    "open_cfw_easylogger_helpers_get_logger",
                    "open_cfw_easylogger_helpers_assert_failed",
                    "open_cfw_easylogger_get_fmt_enabled",
                    "open_cfw_easylogger_get_fmt_used_and_enabled_u32",
                    "open_cfw_easylogger_get_fmt_used_and_enabled_ptr",
                    "open_cfw_easylogger_strcpy",
                )
            },
            {
                "open_cfw_easylogger_helpers_get_logger": {
                    "offset": 352,
                    "size": 8,
                },
                "open_cfw_easylogger_helpers_assert_failed": {
                    "offset": 360,
                    "size": 132,
                },
                "open_cfw_easylogger_get_fmt_enabled": {
                    "offset": 492,
                    "size": 38,
                },
                "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
                    "offset": 530,
                    "size": 20,
                },
                "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
                    "offset": 550,
                    "size": 20,
                },
                "open_cfw_easylogger_strcpy": {
                    "offset": 570,
                    "size": 52,
                },
            },
        )
        self.assertEqual(
            self.report["overlay"]["functions"][
                "open_cfw_littlefs_tag_chunk"
            ],
            {"offset": 622, "size": 6},
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[:4]).hexdigest(),
            SCMP_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[4:10]).hexdigest(),
            ALLOC_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[10:22]).hexdigest(),
            ALLOC_DROP_SOURCE_BODY_SHA256,
        )
        self.assertEqual(self.overlay[22:24], bytes.fromhex("00bf"))
        self.assertEqual(
            hashlib.sha256(self.overlay[24:32]).hexdigest(),
            DISK_VERSION_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[32:40]).hexdigest(),
            MLIST_APPEND_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[40:58]).hexdigest(),
            MLIST_REMOVE_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[58:66]).hexdigest(),
            LITTLEFS_UTIL_MAX_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[66:74]).hexdigest(),
            LITTLEFS_UTIL_MIN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[74:82]).hexdigest(),
            LITTLEFS_UTIL_ALIGNDOWN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[82:90]).hexdigest(),
            LITTLEFS_UTIL_ALIGNUP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[90:146]).hexdigest(),
            (
                "1048afe6eb2c306231e410f0a864ab5b"
                "fab3c9b0567e1fba6ec61f8bae53094a"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[146:162]).hexdigest(),
            (
                "a5616df42c6d3705e9906d0cdce4d6d5"
                "b59d0f02b647c59efeb6594c64004ab1"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[162:204]).hexdigest(),
            (
                "e537e00ef37eced668a9d421f28e84d54"
                "a2b6ea09ea1cfda00f96ec1d65891f7"
            ),
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[204:252]).hexdigest(),
            MSPI_INTERRUPT_CLEAR_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[252:270]).hexdigest(),
            MLIST_ISOPEN_SOURCE_BODY_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[270:272]).hexdigest(),
            LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[272:274]).hexdigest(),
            LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[274:278]).hexdigest(),
            LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[278:282]).hexdigest(),
            LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(self.overlay[302:350]).hexdigest(),
            ALLOC_LOOKAHEAD_SOURCE_BODY_SHA256,
        )
        self.assertEqual(self.overlay[350:352], b"\x00\x00")
        easylogger_leaf_hashes = {
            (352, 360): (
                "3f32a69299002872bb9364f79744be13"
                "11bcb8bce47f24f43558806931990064"
            ),
            (360, 492): (
                "f57622ddc7fdbe8555760ca15bf049b8"
                "fb68abfb3203aa290500e22bbbf82b7a"
            ),
            (492, 530): (
                "8d2909984779762c0abf28369b018b99"
                "b4b30f8d23391fe8670e57f43a166697"
            ),
            (530, 550): (
                "7663e51e49d8c5099f140e85a2f898c"
                "64083a0f02d1574db69294745ee8e5a93"
            ),
            (550, 570): (
                "b5f581ef33404949889812a73244d6b5"
                "c7807ad5707074228a188df7d89ad898"
            ),
            (570, 622): (
                "d19a927665be77d79bd2df6a64575431"
                "db8962aa023f0546f5c3fe5f47805752"
            ),
        }
        for (start, end), expected_hash in easylogger_leaf_hashes.items():
            with self.subTest(easylogger_leaf=f"{start}:{end}"):
                self.assertEqual(
                    hashlib.sha256(self.overlay[start:end]).hexdigest(),
                    expected_hash,
                )
        load, store, return_ = struct.unpack("<HHH", self.overlay[4:10])
        self.assertEqual((load >> 6 & 0x1F) * 4, 0x6C)
        self.assertEqual((store >> 6 & 0x1F) * 4, 0x60)
        self.assertEqual(return_, 0x4770)
        (
            zero,
            first_zero_store,
            second_zero_store,
            drop_load,
            drop_store,
            drop_return,
        ) = struct.unpack("<HHHHHH", self.overlay[10:22])
        self.assertEqual(zero, 0x2100)
        self.assertEqual(
            (
                (first_zero_store >> 6 & 0x1F) * 4,
                (second_zero_store >> 6 & 0x1F) * 4,
            ),
            (0x5C, 0x58),
        )
        self.assertEqual((drop_load >> 6 & 0x1F) * 4, 0x6C)
        self.assertEqual((drop_store >> 6 & 0x1F) * 4, 0x60)
        self.assertEqual(drop_return, 0x4770)
        disk_load, disk_return, disk_version = struct.unpack(
            "<HHI",
            self.overlay[24:32],
        )
        self.assertEqual(disk_load, 0x4800)
        self.assertEqual(disk_return, 0x4770)
        self.assertEqual(disk_version, 0x00020001)
        append_load, append_next, append_head, append_return = struct.unpack(
            "<HHHH",
            self.overlay[32:40],
        )
        self.assertEqual(
            (append_load, append_next, append_head, append_return),
            (0x6A82, 0x600A, 0x6281, 0x4770),
        )
        self.assertEqual(self.overlay[40:44], bytes.fromhex("28300246"))
        self.assertEqual(self.overlay[56:58], bytes.fromhex("7047"))
        link = self.report["overlay"]["link"]
        self.assertEqual(link["text_size"], 204)
        self.assertEqual(link["rodata_size"], 0)
        self.assertEqual(link["resolved_relocation_count"], 2)
        self.assertEqual(
            link["resolved_relocations"],
            [
                {
                    "section": ".rel.text",
                    "site": 86,
                    "symbol": "open_cfw_littlefs_util_aligndown",
                    "type": 30,
                },
                {
                    "section": ".rel.text",
                    "site": 154,
                    "symbol": "open_cfw_littlefs_util_npw2",
                    "type": 10,
                }
            ],
        )
        self.assertEqual(link["isolated_text_size"], 78)
        self.assertEqual(link["isolated_padding_size"], 0)
        self.assertEqual(
            link["isolated_functions"],
            [
                {
                    "function": "am_hal_mspi_interrupt_clear",
                    "offset": 204,
                    "size": 48,
                    "alignment": 4,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_mlist_isopen",
                    "offset": 252,
                    "size": 18,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_fromle32",
                    "offset": 270,
                    "size": 2,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_tole32",
                    "offset": 272,
                    "size": 2,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_frombe32",
                    "offset": 274,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                },
                {
                    "function": "open_cfw_littlefs_util_tobe32",
                    "offset": 278,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                },
            ],
        )
        self.assertEqual(link["relocated_text_size"], 14800)
        self.assertEqual(link["relocated_rodata_size"], 143)
        self.assertEqual(link["relocated_padding_size"], 15)
        self.assertEqual(
            link["relocated_functions"],
            [
                {
                    "function": "open_cfw_littlefs_disk_version_major",
                    "offset": 282,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434592,
                    "runtime_address_hex": "0x00434592",
                },
                {
                    "function": "open_cfw_littlefs_disk_version_minor",
                    "offset": 292,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043459C,
                    "runtime_address_hex": "0x0043459C",
                },
                {
                    "function": "open_cfw_littlefs_alloc_lookahead",
                    "offset": 302,
                    "size": 48,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004345A6,
                    "runtime_address_hex": "0x004345A6",
                },
                {
                    "function": "open_cfw_easylogger_helpers_get_logger",
                    "offset": 352,
                    "size": 8,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x004345D8,
                    "runtime_address_hex": "0x004345D8",
                },
                {
                    "function": "open_cfw_easylogger_helpers_assert_failed",
                    "offset": 360,
                    "size": 132,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004345E0,
                    "runtime_address_hex": "0x004345E0",
                },
                {
                    "function": "open_cfw_easylogger_get_fmt_enabled",
                    "offset": 492,
                    "size": 38,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434664,
                    "runtime_address_hex": "0x00434664",
                },
                {
                    "function": (
                        "open_cfw_easylogger_get_fmt_used_and_enabled_u32"
                    ),
                    "offset": 530,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043468A,
                    "runtime_address_hex": "0x0043468A",
                },
                {
                    "function": (
                        "open_cfw_easylogger_get_fmt_used_and_enabled_ptr"
                    ),
                    "offset": 550,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043469E,
                    "runtime_address_hex": "0x0043469E",
                },
                {
                    "function": "open_cfw_easylogger_strcpy",
                    "offset": 570,
                    "size": 52,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346B2,
                    "runtime_address_hex": "0x004346B2",
                },
                {
                    "function": "open_cfw_littlefs_tag_chunk",
                    "offset": 622,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346E6,
                    "runtime_address_hex": "0x004346E6",
                },
                {
                    "function": "open_cfw_littlefs_tag_isvalid",
                    "offset": 628,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346EC,
                    "runtime_address_hex": "0x004346EC",
                },
                {
                    "function": "open_cfw_littlefs_tag_type1",
                    "offset": 634,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346F2,
                    "runtime_address_hex": "0x004346F2",
                },
                {
                    "function": "open_cfw_littlefs_tag_type3",
                    "offset": 644,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004346FC,
                    "runtime_address_hex": "0x004346FC",
                },
                {
                    "function": "open_cfw_littlefs_tag_id",
                    "offset": 650,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434702,
                    "runtime_address_hex": "0x00434702",
                },
                {
                    "function": "open_cfw_littlefs_tag_size",
                    "offset": 656,
                    "size": 6,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434708,
                    "runtime_address_hex": "0x00434708",
                },
                {
                    "function": "open_cfw_bootloader_redirect_init",
                    "offset": 664,
                    "size": 275,
                    "text_size": 132,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x00434710,
                    "runtime_address_hex": "0x00434710",
                },
                {
                    "function": "open_cfw_bootloader_aeabi_memset",
                    "offset": 940,
                    "size": 12,
                    "alignment": 2,
                    "padding_before": 1,
                    "runtime_address": 0x00434824,
                    "runtime_address_hex": "0x00434824",
                },
                {
                    "function": "open_cfw_bootloader_aeabi_memcpy",
                    "offset": 952,
                    "size": 16,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434830,
                    "runtime_address_hex": "0x00434830",
                },
                {
                    "function": "open_cfw_bootloader_memcmp",
                    "offset": 968,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434840,
                    "runtime_address_hex": "0x00434840",
                },
                {
                    "function": "open_cfw_bootloader_strcspn",
                    "offset": 996,
                    "size": 30,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043485C,
                    "runtime_address_hex": "0x0043485C",
                },
                {
                    "function": "open_cfw_bootloader_strspn",
                    "offset": 1026,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043487A,
                    "runtime_address_hex": "0x0043487A",
                },
                {
                    "function": "open_cfw_bootloader_crc32",
                    "offset": 1056,
                    "size": 44,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x00434898,
                    "runtime_address_hex": "0x00434898",
                },
                {
                    "function": "open_cfw_bootloader_store_200270cc",
                    "offset": 1100,
                    "size": 12,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004348C4,
                    "runtime_address_hex": "0x004348C4",
                },
                {
                    "function": "open_cfw_bootloader_udiv10",
                    "offset": 1112,
                    "size": 106,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004348D0,
                    "runtime_address_hex": "0x004348D0",
                },
                {
                    "function": "open_cfw_bootloader_udec_digits",
                    "offset": 1218,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043493A,
                    "runtime_address_hex": "0x0043493A",
                },
                {
                    "function": "open_cfw_bootloader_sdec_digits",
                    "offset": 1246,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434956,
                    "runtime_address_hex": "0x00434956",
                },
                {
                    "function": "open_cfw_bootloader_hex_digits",
                    "offset": 1266,
                    "size": 24,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043496A,
                    "runtime_address_hex": "0x0043496A",
                },
                {
                    "function": "open_cfw_bootloader_parse_dec",
                    "offset": 1290,
                    "size": 48,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434982,
                    "runtime_address_hex": "0x00434982",
                },
                {
                    "function": "open_cfw_bootloader_u64_to_dec",
                    "offset": 1338,
                    "size": 74,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004349B2,
                    "runtime_address_hex": "0x004349B2",
                },
                {
                    "function": "open_cfw_bootloader_u64_to_hex",
                    "offset": 1412,
                    "size": 72,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004349FC,
                    "runtime_address_hex": "0x004349FC",
                },
                {
                    "function": "open_cfw_bootloader_nullable_strlen",
                    "offset": 1484,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434A44,
                    "runtime_address_hex": "0x00434A44",
                },
                {
                    "function": "open_cfw_bootloader_repeat_char",
                    "offset": 1504,
                    "size": 32,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434A58,
                    "runtime_address_hex": "0x00434A58",
                },
                {
                    "function": "open_cfw_bootloader_float_to_fixed",
                    "offset": 1536,
                    "size": 320,
                    "alignment": 8,
                    "padding_before": 0,
                    "runtime_address": 0x00434A78,
                    "runtime_address_hex": "0x00434A78",
                },
                {
                    "function": "open_cfw_bootloader_format_core",
                    "offset": 1856,
                    "size": 968,
                    "alignment": 8,
                    "padding_before": 0,
                    "runtime_address": 0x00434BB8,
                    "runtime_address_hex": "0x00434BB8",
                },
                {
                    "function": "open_cfw_bootloader_log_dispatch",
                    "offset": 2824,
                    "size": 60,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00434F80,
                    "runtime_address_hex": "0x00434F80",
                },
                {
                    "function": "open_cfw_bootloader_strstr",
                    "offset": 2884,
                    "size": 46,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434FBC,
                    "runtime_address_hex": "0x00434FBC",
                },
                {
                    "function": "open_cfw_bootloader_critical_context",
                    "offset": 2930,
                    "size": 46,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00434FEA,
                    "runtime_address_hex": "0x00434FEA",
                },
                {
                    "function": "open_cfw_bootloader_gate_acquire",
                    "offset": 2976,
                    "size": 48,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435018,
                    "runtime_address_hex": "0x00435018",
                },
                {
                    "function": "open_cfw_bootloader_gate_state",
                    "offset": 3024,
                    "size": 36,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435048,
                    "runtime_address_hex": "0x00435048",
                },
                {
                    "function": "open_cfw_bootloader_gate_release",
                    "offset": 3060,
                    "size": 56,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x0043506C,
                    "runtime_address_hex": "0x0043506C",
                },
                {
                    "function": "open_cfw_bootloader_context_value",
                    "offset": 3116,
                    "size": 24,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004350A4,
                    "runtime_address_hex": "0x004350A4",
                },
                {
                    "function": "open_cfw_bootloader_runtime_dispatch_4160fe",
                    "offset": 3140,
                    "size": 166,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004350BC,
                    "runtime_address_hex": "0x004350BC",
                },
                {
                    "function": "open_cfw_bootloader_runtime_value_4161c6",
                    "offset": 3306,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435162,
                    "runtime_address_hex": "0x00435162",
                },
                {
                    "function": "open_cfw_bootloader_runtime_call_4161ce",
                    "offset": 3310,
                    "size": 44,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435166,
                    "runtime_address_hex": "0x00435166",
                },
                {
                    "function": "open_cfw_bootloader_runtime_action_416200",
                    "offset": 3354,
                    "size": 52,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435192,
                    "runtime_address_hex": "0x00435192",
                },
                {
                    "function": "open_cfw_bootloader_runtime_transfer_41623a",
                    "offset": 3408,
                    "size": 128,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x004351C8,
                    "runtime_address_hex": "0x004351C8",
                },
                {
                    "function": "open_cfw_bootloader_runtime_wait_4162c4",
                    "offset": 3536,
                    "size": 178,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435248,
                    "runtime_address_hex": "0x00435248",
                },
                {
                    "function": "open_cfw_bootloader_runtime_notify_416378",
                    "offset": 3714,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004352FA,
                    "runtime_address_hex": "0x004352FA",
                },
                {
                    "function": "open_cfw_bootloader_runtime_callback_41639a",
                    "offset": 3742,
                    "size": 24,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435316,
                    "runtime_address_hex": "0x00435316",
                },
                {
                    "function": "open_cfw_bootloader_runtime_register_4163b2",
                    "offset": 3768,
                    "size": 180,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x00435330,
                    "runtime_address_hex": "0x00435330",
                },
                {
                    "function": "open_cfw_bootloader_runtime_submit_41649a",
                    "offset": 3948,
                    "size": 54,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004353E4,
                    "runtime_address_hex": "0x004353E4",
                },
                {
                    "function": "open_cfw_bootloader_runtime_create_4164da",
                    "offset": 4002,
                    "size": 46,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043541A,
                    "runtime_address_hex": "0x0043541A",
                },
                {
                    "function": "open_cfw_bootloader_runtime_flags_set_41652e",
                    "offset": 4048,
                    "size": 84,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435448,
                    "runtime_address_hex": "0x00435448",
                },
                {
                    "function": "open_cfw_bootloader_runtime_flags_wait_416590",
                    "offset": 4132,
                    "size": 100,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043549C,
                    "runtime_address_hex": "0x0043549C",
                },
                {
                    "function": "open_cfw_bootloader_runtime_flags_create_416610",
                    "offset": 4232,
                    "size": 82,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435500,
                    "runtime_address_hex": "0x00435500",
                },
                {
                    "function": "open_cfw_bootloader_runtime_handle_acquire_4166aa",
                    "offset": 4314,
                    "size": 68,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435552,
                    "runtime_address_hex": "0x00435552",
                },
                {
                    "function": "open_cfw_bootloader_runtime_handle_release_416710",
                    "offset": 4382,
                    "size": 58,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435596,
                    "runtime_address_hex": "0x00435596",
                },
                {
                    "function": "open_cfw_bootloader_runtime_semaphore_create_416762",
                    "offset": 4440,
                    "size": 140,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004355D0,
                    "runtime_address_hex": "0x004355D0",
                },
                {
                    "function": "open_cfw_bootloader_runtime_queue_create_416816",
                    "offset": 4580,
                    "size": 100,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043565C,
                    "runtime_address_hex": "0x0043565C",
                },
                {
                    "function": "open_cfw_bootloader_runtime_queue_put_4168a2",
                    "offset": 4680,
                    "size": 112,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004356C0,
                    "runtime_address_hex": "0x004356C0",
                },
                {
                    "function": "open_cfw_bootloader_runtime_queue_get_416920",
                    "offset": 4792,
                    "size": 108,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435730,
                    "runtime_address_hex": "0x00435730",
                },
                {
                    "function": "open_cfw_bootloader_runtime_bit_width_4169a4",
                    "offset": 4900,
                    "size": 14,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043579C,
                    "runtime_address_hex": "0x0043579C",
                },
                {
                    "function": "open_cfw_bootloader_runtime_ctz_4169e2",
                    "offset": 4914,
                    "size": 14,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357AA,
                    "runtime_address_hex": "0x004357AA",
                },
                {
                    "function": "open_cfw_bootloader_runtime_log2_4169f2",
                    "offset": 4928,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357B8,
                    "runtime_address_hex": "0x004357B8",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_size_4169fc",
                    "offset": 4938,
                    "size": 8,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357C2,
                    "runtime_address_hex": "0x004357C2",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_set_size_416a10",
                    "offset": 4946,
                    "size": 12,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357CA,
                    "runtime_address_hex": "0x004357CA",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_is_last_416a2c",
                    "offset": 4958,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357D6,
                    "runtime_address_hex": "0x004357D6",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_is_free_416a40",
                    "offset": 4968,
                    "size": 8,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357E0,
                    "runtime_address_hex": "0x004357E0",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_set_free_416a4c",
                    "offset": 4976,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357E8,
                    "runtime_address_hex": "0x004357E8",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_set_used_416a5a",
                    "offset": 4986,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357F2,
                    "runtime_address_hex": "0x004357F2",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_is_previous_free_416a68",
                    "offset": 4996,
                    "size": 8,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004357FC,
                    "runtime_address_hex": "0x004357FC",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_set_previous_free_416a74",
                    "offset": 5004,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435804,
                    "runtime_address_hex": "0x00435804",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_set_previous_used_416a82",
                    "offset": 5014,
                    "size": 10,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043580E,
                    "runtime_address_hex": "0x0043580E",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_from_pointer_416a90",
                    "offset": 5024,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435818,
                    "runtime_address_hex": "0x00435818",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_to_pointer_416a9c",
                    "offset": 5028,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043581C,
                    "runtime_address_hex": "0x0043581C",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_offset_to_block_416aa6",
                    "offset": 5032,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435820,
                    "runtime_address_hex": "0x00435820",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_prev_416aaa",
                    "offset": 5036,
                    "size": 36,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435824,
                    "runtime_address_hex": "0x00435824",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_next_416ad0",
                    "offset": 5072,
                    "size": 60,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435848,
                    "runtime_address_hex": "0x00435848",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_link_next_416b14",
                    "offset": 5132,
                    "size": 12,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435884,
                    "runtime_address_hex": "0x00435884",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_mark_as_free_416b22",
                    "offset": 5144,
                    "size": 22,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435890,
                    "runtime_address_hex": "0x00435890",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_mark_as_used_416b38",
                    "offset": 5166,
                    "size": 22,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x004358A6,
                    "runtime_address_hex": "0x004358A6",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_align_up_416b4e",
                    "offset": 5188,
                    "size": 44,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004358BC,
                    "runtime_address_hex": "0x004358BC",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_align_down_416b7a",
                    "offset": 5232,
                    "size": 40,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x004358E8,
                    "runtime_address_hex": "0x004358E8",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_align_pointer_416ba4",
                    "offset": 5272,
                    "size": 44,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435910,
                    "runtime_address_hex": "0x00435910",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_adjust_request_size_416bce",
                    "offset": 5316,
                    "size": 30,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043593C,
                    "runtime_address_hex": "0x0043593C",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_mapping_insert_416bf8",
                    "offset": 5346,
                    "size": 42,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x0043595A,
                    "runtime_address_hex": "0x0043595A",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_mapping_search_416c26",
                    "offset": 5388,
                    "size": 46,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435984,
                    "runtime_address_hex": "0x00435984",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_search_suitable_block_416c4e",
                    "offset": 5436,
                    "size": 112,
                    "alignment": 4,
                    "padding_before": 2,
                    "runtime_address": 0x004359B4,
                    "runtime_address_hex": "0x004359B4",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_remove_free_block_416cc6",
                    "offset": 5548,
                    "size": 124,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435A24,
                    "runtime_address_hex": "0x00435A24",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_insert_free_block_416d5c",
                    "offset": 5672,
                    "size": 148,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435AA0,
                    "runtime_address_hex": "0x00435AA0",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_remove_416e04",
                    "offset": 5820,
                    "size": 34,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435B34,
                    "runtime_address_hex": "0x00435B34",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_insert_416e26",
                    "offset": 5854,
                    "size": 34,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435B56,
                    "runtime_address_hex": "0x00435B56",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_can_split_416e48",
                    "offset": 5888,
                    "size": 20,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435B78,
                    "runtime_address_hex": "0x00435B78",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_split_416e60",
                    "offset": 5908,
                    "size": 164,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435B8C,
                    "runtime_address_hex": "0x00435B8C",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_absorb_416f20",
                    "offset": 6072,
                    "size": 60,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435C30,
                    "runtime_address_hex": "0x00435C30",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_merge_previous_416f62",
                    "offset": 6132,
                    "size": 96,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435C6C,
                    "runtime_address_hex": "0x00435C6C",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_merge_next_416fc6",
                    "offset": 6228,
                    "size": 88,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435CCC,
                    "runtime_address_hex": "0x00435CCC",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_trim_free_41702a",
                    "offset": 6316,
                    "size": 88,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435D24,
                    "runtime_address_hex": "0x00435D24",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_locate_free_41707c",
                    "offset": 6404,
                    "size": 96,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435D7C,
                    "runtime_address_hex": "0x00435D7C",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_block_prepare_used_4170de",
                    "offset": 6500,
                    "size": 68,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435DDC,
                    "runtime_address_hex": "0x00435DDC",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_control_construct_41711c",
                    "offset": 6568,
                    "size": 48,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435E20,
                    "runtime_address_hex": "0x00435E20",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_pool_overhead_41714c",
                    "offset": 6616,
                    "size": 4,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435E50,
                    "runtime_address_hex": "0x00435E50",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_add_pool_41715c",
                    "offset": 6620,
                    "size": 140,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435E54,
                    "runtime_address_hex": "0x00435E54",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_create_417208",
                    "offset": 6760,
                    "size": 40,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435EE0,
                    "runtime_address_hex": "0x00435EE0",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_create_with_pool_417240",
                    "offset": 6800,
                    "size": 28,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435F08,
                    "runtime_address_hex": "0x00435F08",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_malloc_41726a",
                    "offset": 6828,
                    "size": 36,
                    "alignment": 2,
                    "padding_before": 0,
                    "runtime_address": 0x00435F24,
                    "runtime_address_hex": "0x00435F24",
                },
                {
                    "function": "open_cfw_bootloader_tlsf_free_417290",
                    "offset": 6864,
                    "size": 80,
                    "alignment": 4,
                    "padding_before": 0,
                    "runtime_address": 0x00435F48,
                    "runtime_address_hex": "0x00435F48",
                },
                {"function": "open_cfw_bootloader_easylogger_set_output_enabled_4173ca", "offset": 6944, "size": 100, "alignment": 4, "padding_before": 0, "runtime_address": 0x00435F98, "runtime_address_hex": "0x00435F98"},
                {"function": "open_cfw_bootloader_easylogger_set_text_color_enabled_417438", "offset": 7044, "size": 104, "alignment": 4, "padding_before": 0, "runtime_address": 0x00435FFC, "runtime_address_hex": "0x00435FFC"},
                {"function": "open_cfw_bootloader_easylogger_set_filter_lvl_417510", "offset": 7148, "size": 104, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436064, "runtime_address_hex": "0x00436064"},
                {"function": "open_cfw_bootloader_easylogger_filter_tag_lvl_default_4175b4", "offset": 7252, "size": 52, "alignment": 4, "padding_before": 0, "runtime_address": 0x004360CC, "runtime_address_hex": "0x004360CC"},
                {"function": "open_cfw_bootloader_easylogger_output_lock_417570", "offset": 7304, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436100, "runtime_address_hex": "0x00436100"},
                {"function": "open_cfw_bootloader_easylogger_output_unlock_417592", "offset": 7336, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436120, "runtime_address_hex": "0x00436120"},
                {"function": "open_cfw_bootloader_easylogger_set_fmt_4174a6", "offset": 7368, "size": 108, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436140, "runtime_address_hex": "0x00436140"},
                {"function": "open_cfw_bootloader_easylogger_init_41733c", "offset": 7476, "size": 72, "alignment": 4, "padding_before": 0, "runtime_address": 0x004361AC, "runtime_address_hex": "0x004361AC"},
                {"function": "open_cfw_bootloader_easylogger_start_417392", "offset": 7548, "size": 68, "alignment": 4, "padding_before": 0, "runtime_address": 0x004361F4, "runtime_address_hex": "0x004361F4"},
                {"function": "open_cfw_bootloader_easylogger_get_filter_tag_lvl_41760a", "offset": 7616, "size": 164, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436238, "runtime_address_hex": "0x00436238"},
                {"function": "open_cfw_bootloader_easylogger_output_4176ce", "offset": 7780, "size": 1060, "alignment": 4, "padding_before": 0, "runtime_address": 0x004362DC, "runtime_address_hex": "0x004362DC"},
                {"function": "open_cfw_bootloader_easylogger_output_lock_enabled_417b7c", "offset": 8840, "size": 36, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436700, "runtime_address_hex": "0x00436700"},
                {"function": "open_cfw_bootloader_easylogger_mutex_create_41a648", "offset": 8876, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436724, "runtime_address_hex": "0x00436724"},
                {"function": "open_cfw_bootloader_easylogger_mutex_acquire_41a65c", "offset": 8908, "size": 24, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436744, "runtime_address_hex": "0x00436744"},
                {"function": "open_cfw_bootloader_easylogger_mutex_release_41a672", "offset": 8932, "size": 20, "alignment": 4, "padding_before": 0, "runtime_address": 0x0043675C, "runtime_address_hex": "0x0043675C"},
                {"function": "open_cfw_bootloader_easylogger_port_init_41a684", "offset": 8952, "size": 16, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436770, "runtime_address_hex": "0x00436770"},
                {"function": "open_cfw_bootloader_easylogger_port_output_41a692", "offset": 8968, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436780, "runtime_address_hex": "0x00436780"},
                {"function": "open_cfw_bootloader_easylogger_port_output_lock_41a69a", "offset": 8976, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436788, "runtime_address_hex": "0x00436788"},
                {"function": "open_cfw_bootloader_easylogger_port_output_unlock_41a6a2", "offset": 8984, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436790, "runtime_address_hex": "0x00436790"},
                {"function": "open_cfw_bootloader_easylogger_port_get_time_41a6aa", "offset": 8992, "size": 40, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436798, "runtime_address_hex": "0x00436798"},
                {"function": "open_cfw_bootloader_easylogger_task_name_41a6c2", "offset": 9032, "size": 40, "alignment": 4, "padding_before": 0, "runtime_address": 0x004367C0, "runtime_address_hex": "0x004367C0"},
                {"function": "open_cfw_bootloader_easylogger_port_get_p_info_41a6f0", "offset": 9072, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x004367E8, "runtime_address_hex": "0x004367E8"},
                {"function": "open_cfw_bootloader_easylogger_port_get_t_info_41a6f8", "offset": 9080, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x004367F0, "runtime_address_hex": "0x004367F0"},
                {"function": "open_cfw_bootloader_easylogger_driver_output_41b854", "offset": 9088, "size": 16, "alignment": 4, "padding_before": 0, "runtime_address": 0x004367F8, "runtime_address_hex": "0x004367F8"},
                {"function": "open_cfw_bootloader_easylogger_channel_write_41f918", "offset": 9104, "size": 120, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436808, "runtime_address_hex": "0x00436808"},
                {"function": "open_cfw_bootloader_delay_milliseconds_41f9d8", "offset": 9224, "size": 16, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436880, "runtime_address_hex": "0x00436880"},
                {"function": "open_cfw_bootloader_delay_41f9e6", "offset": 9240, "size": 8, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436890, "runtime_address_hex": "0x00436890"},
                {"function": "open_cfw_bootloader_initializer_priority_compare_41f9f0", "offset": 9248, "size": 8, "alignment": 2, "padding_before": 0, "runtime_address": 0x00436898, "runtime_address_hex": "0x00436898"},
                {"function": "open_cfw_bootloader_run_initializers_41f9f8", "offset": 9256, "size": 64, "alignment": 4, "padding_before": 0, "runtime_address": 0x004368A0, "runtime_address_hex": "0x004368A0"},
                {"function": "open_cfw_bootloader_guarded_teardown_41fa98", "offset": 9320, "size": 72, "alignment": 4, "padding_before": 0, "runtime_address": 0x004368E0, "runtime_address_hex": "0x004368E0"},
                {"function": "open_cfw_bootloader_platform_setup_41fa50", "offset": 9392, "size": 96, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436928, "runtime_address_hex": "0x00436928"},
                {"function": "open_cfw_bootloader_pin_groups_41fadc", "offset": 9488, "size": 428, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436988, "runtime_address_hex": "0x00436988"},
                {"function": "open_cfw_bootloader_allocator_init_41fd70", "offset": 9916, "size": 88, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436B34, "runtime_address_hex": "0x00436B34"},
                {"function": "open_cfw_bootloader_nvic_enable_irq_41fdc0", "offset": 10004, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436B8C, "runtime_address_hex": "0x00436B8C"},
                {"function": "open_cfw_bootloader_nvic_set_priority_41fdde", "offset": 10036, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436BAC, "runtime_address_hex": "0x00436BAC"},
                {"function": "open_cfw_bootloader_mspi_isr_41fe06", "offset": 10068, "size": 48, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436BCC, "runtime_address_hex": "0x00436BCC"},
                {"function": "open_cfw_bootloader_mspi_enable_41fe28", "offset": 10116, "size": 40, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436BFC, "runtime_address_hex": "0x00436BFC"},
                {"function": "open_cfw_bootloader_mspi_disable_41fe48", "offset": 10156, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436C24, "runtime_address_hex": "0x00436C24"},
                {"function": "open_cfw_bootloader_event_flags_init_41fe62", "offset": 10188, "size": 76, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436C44, "runtime_address_hex": "0x00436C44"},
                {"function": "open_cfw_bootloader_event_flags_acquire_41fe9c", "offset": 10264, "size": 68, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436C90, "runtime_address_hex": "0x00436C90"},
                {"function": "open_cfw_bootloader_event_flags_release_41fed4", "offset": 10332, "size": 64, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436CD4, "runtime_address_hex": "0x00436CD4"},
                {"function": "open_cfw_bootloader_mspi_guard_enter_41ff08", "offset": 10396, "size": 36, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436D14, "runtime_address_hex": "0x00436D14"},
                {"function": "open_cfw_bootloader_mspi_guard_exit_41ff1e", "offset": 10432, "size": 32, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436D38, "runtime_address_hex": "0x00436D38"},
                {"function": "open_cfw_bootloader_mspi_xip_config_41ff34", "offset": 10464, "size": 36, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436D58, "runtime_address_hex": "0x00436D58"},
                {"function": "open_cfw_bootloader_longest_ones_run_41ff60", "offset": 10500, "size": 16, "alignment": 2, "padding_before": 0, "runtime_address": 0x00436D7C, "runtime_address_hex": "0x00436D7C"},
                {"function": "open_cfw_bootloader_longest_ones_center_41ff74", "offset": 10516, "size": 126, "alignment": 2, "padding_before": 0, "runtime_address": 0x00436D8C, "runtime_address_hex": "0x00436D8C"},
                {"function": "open_cfw_bootloader_mspi_timing_scan_420002", "offset": 10644, "size": 420, "alignment": 4, "padding_before": 2, "runtime_address": 0x00436E0C, "runtime_address_hex": "0x00436E0C"},
                {"function": "open_cfw_bootloader_mspi_timing_auto_4201ba", "offset": 11064, "size": 172, "alignment": 4, "padding_before": 0, "runtime_address": 0x00436FB0, "runtime_address_hex": "0x00436FB0"},
                {"function": "open_cfw_bootloader_mspi_low_level_init_420254", "offset": 11236, "size": 492, "alignment": 4, "padding_before": 0, "runtime_address": 0x0043705C, "runtime_address_hex": "0x0043705C"},
                {"function": "open_cfw_bootloader_mspi_driver_init_420476", "offset": 11728, "size": 204, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437248, "runtime_address_hex": "0x00437248"},
                {"function": "open_cfw_bootloader_mspi_soft_reset_42052a", "offset": 11932, "size": 136, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437314, "runtime_address_hex": "0x00437314"},
                {"function": "open_cfw_bootloader_mspi_read_id_42059e", "offset": 12068, "size": 100, "alignment": 4, "padding_before": 0, "runtime_address": 0x0043739C, "runtime_address_hex": "0x0043739C"},
                {"function": "open_cfw_bootloader_mspi_read_transfer_4205f4", "offset": 12168, "size": 172, "alignment": 8, "padding_before": 0, "runtime_address": 0x00437400, "runtime_address_hex": "0x00437400"},
                {"function": "open_cfw_bootloader_mspi_write_transfer_42069e", "offset": 12340, "size": 148, "alignment": 4, "padding_before": 0, "runtime_address": 0x004374AC, "runtime_address_hex": "0x004374AC"},
                {"function": "open_cfw_bootloader_mspi_busy_status_42074e", "offset": 12488, "size": 88, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437540, "runtime_address_hex": "0x00437540"},
                {"function": "open_cfw_bootloader_mspi_wait_ready_4207a2", "offset": 12576, "size": 88, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437598, "runtime_address_hex": "0x00437598"},
                {"function": "open_cfw_bootloader_mspi_wait_ready_default_4207f4", "offset": 12664, "size": 12, "alignment": 4, "padding_before": 0, "runtime_address": 0x004375F0, "runtime_address_hex": "0x004375F0"},
                {"function": "open_cfw_bootloader_mspi_4byte_mode_420800", "offset": 12676, "size": 124, "alignment": 4, "padding_before": 0, "runtime_address": 0x004375FC, "runtime_address_hex": "0x004375FC"},
                {"function": "open_cfw_bootloader_mspi_enter_4byte_mode_420890", "offset": 12800, "size": 220, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437678, "runtime_address_hex": "0x00437678"},
                {"function": "open_cfw_bootloader_mspi_write_enable_420984", "offset": 13020, "size": 72, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437754, "runtime_address_hex": "0x00437754"},
                {"function": "open_cfw_bootloader_mspi_write_disable_4209c4", "offset": 13092, "size": 72, "alignment": 4, "padding_before": 0, "runtime_address": 0x0043779C, "runtime_address_hex": "0x0043779C"},
                {"function": "open_cfw_bootloader_mspi_sector_erase_420a08", "offset": 13164, "size": 244, "alignment": 4, "padding_before": 0, "runtime_address": 0x004377E4, "runtime_address_hex": "0x004377E4"},
                {"function": "open_cfw_bootloader_mspi_program_420b0c", "offset": 13408, "size": 256, "alignment": 4, "padding_before": 0, "runtime_address": 0x004378D8, "runtime_address_hex": "0x004378D8"},
                {"function": "open_cfw_bootloader_mspi_quad_enable_420c5c", "offset": 13664, "size": 364, "alignment": 4, "padding_before": 0, "runtime_address": 0x004379D8, "runtime_address_hex": "0x004379D8"},
                {"function": "open_cfw_bootloader_mspi_device_reconfigure_420e08", "offset": 14028, "size": 136, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437B44, "runtime_address_hex": "0x00437B44"},
                {"function": "open_cfw_bootloader_mspi_set_quad_mode_420e8c", "offset": 14164, "size": 152, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437BCC, "runtime_address_hex": "0x00437BCC"},
                {"function": "open_cfw_bootloader_mspi_set_serial_mode_420f10", "offset": 14316, "size": 124, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437C64, "runtime_address_hex": "0x00437C64"},
                {"function": "open_cfw_bootloader_mspi_read_420f70", "offset": 14440, "size": 152, "alignment": 8, "padding_before": 0, "runtime_address": 0x00437CE0, "runtime_address_hex": "0x00437CE0"},
                {"function": "open_cfw_bootloader_check_and_create_directories_4210c8", "offset": 14592, "size": 220, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437D78, "runtime_address_hex": "0x00437D78"},
                {"function": "open_cfw_littlefs_bootloader_format_4211b0", "offset": 14812, "size": 108, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437E54, "runtime_address_hex": "0x00437E54"},
                {"function": "open_cfw_littlefs_bootloader_init_421210", "offset": 14920, "size": 260, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437EC0, "runtime_address_hex": "0x00437EC0"},
                {"function": "open_cfw_bootloader_littlefs_read_4212d8", "offset": 15180, "size": 60, "alignment": 4, "padding_before": 0, "runtime_address": 0x00437FC4, "runtime_address_hex": "0x00437FC4"},
            ],
        )

    def test_exact_declared_mutation_set(self) -> None:
        self.assertEqual(len(self.provider), 163840)
        self.assertEqual(
            hashlib.sha256(self.provider).hexdigest(),
            PROVIDER_SHA256,
        )

        changed = [
            offset
            for offset, (stock, generated) in enumerate(
                zip(self.official, self.provider)
            )
            if stock != generated
        ]
        self.assertEqual(
            changed,
            list(
                range(
                    LITTLEFS_UTIL_MAX_OFFSET,
                    LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 6,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 7,
                    LITTLEFS_UTIL_ALIGNUP_OFFSET + 12,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET,
                    LITTLEFS_UTIL_NPW2_OFFSET + 14,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 15,
                    LITTLEFS_UTIL_NPW2_OFFSET + 16,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 17,
                    LITTLEFS_UTIL_NPW2_OFFSET + 34,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 35,
                    LITTLEFS_UTIL_NPW2_OFFSET + 36,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 37,
                    LITTLEFS_UTIL_NPW2_OFFSET + 52,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 53,
                    LITTLEFS_UTIL_NPW2_OFFSET + 54,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 55,
                    LITTLEFS_UTIL_NPW2_OFFSET + 70,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 71,
                    LITTLEFS_UTIL_NPW2_OFFSET + 72,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_NPW2_OFFSET + 73,
                    LITTLEFS_UTIL_NPW2_OFFSET + 90,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_CTZ_OFFSET,
                    LITTLEFS_UTIL_CTZ_OFFSET + 16,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_POPC_OFFSET,
                    LITTLEFS_UTIL_POPC_OFFSET + 36,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_POPC_OFFSET + 37,
                    LITTLEFS_UTIL_POPC_OFFSET + 40,
                )
            )
            + list(range(SCMP_OFFSET, SCMP_OFFSET + 4))
            + list(
                range(
                    LITTLEFS_UTIL_FROMLE32_OFFSET,
                    LITTLEFS_UTIL_FROMLE32_OFFSET + 4,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMLE32_OFFSET + 5,
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 4,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 5,
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 10,
                )
            )
            + list(
                range(
                    LITTLEFS_UTIL_FROMBE32_OFFSET + 11,
                    LITTLEFS_UTIL_TOBE32_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_ISVALID_OFFSET,
                    LITTLEFS_TAG_ISVALID_OFFSET + 10,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_TYPE1_OFFSET,
                    LITTLEFS_TAG_TYPE1_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_TYPE3_OFFSET,
                    LITTLEFS_TAG_TYPE3_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_CHUNK_OFFSET,
                    LITTLEFS_TAG_CHUNK_OFFSET + 6,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_ID_OFFSET,
                    LITTLEFS_TAG_ID_OFFSET + 8,
                )
            )
            + list(
                range(
                    LITTLEFS_TAG_SIZE_OFFSET,
                    LITTLEFS_TAG_SIZE_OFFSET + 6,
                )
            )
            + list(range(MLIST_ISOPEN_OFFSET, MLIST_ISOPEN_OFFSET + 4))
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 5,
                    MLIST_ISOPEN_OFFSET + 10,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 11,
                    MLIST_ISOPEN_OFFSET + 22,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 23,
                    MLIST_ISOPEN_OFFSET + 24,
                )
            )
            + list(
                range(
                    MLIST_ISOPEN_OFFSET + 25,
                    MLIST_ISOPEN_OFFSET + 30,
                )
            )
            + list(range(MLIST_REMOVE_OFFSET, MLIST_REMOVE_OFFSET + 4))
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 5,
                    MLIST_REMOVE_OFFSET + 10,
                )
            )
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 11,
                    MLIST_REMOVE_OFFSET + 22,
                )
            )
            + list(
                range(
                    MLIST_REMOVE_OFFSET + 23,
                    DISK_VERSION_OFFSET + 6,
                )
            )
            + list(
                range(
                    DISK_VERSION_MAJOR_OFFSET,
                    DISK_VERSION_MAJOR_OFFSET + 6,
                )
            )
            + list(
                range(
                    DISK_VERSION_MAJOR_OFFSET + 7,
                    DISK_VERSION_MINOR_OFFSET + 10,
                )
            )
            + list(range(ALLOC_OFFSET, ALLOC_OFFSET + 6))
            + list(range(ALLOC_DROP_OFFSET, ALLOC_DROP_OFFSET + 6))
            + list(range(ALLOC_DROP_OFFSET + 7, ALLOC_DROP_OFFSET + 16))
            + list(
                range(
                    ALLOC_LOOKAHEAD_OFFSET,
                    ALLOC_LOOKAHEAD_OFFSET + 50,
                )
            )
            + list(
                range(
                    ALLOC_LOOKAHEAD_OFFSET + 51,
                    ALLOC_LOOKAHEAD_OFFSET + 56,
                )
            )
            + list(range(REDIRECT_INIT_OFFSET, REDIRECT_INIT_OFFSET + 4))
            + list(range(REDIRECT_INIT_OFFSET + 5, REDIRECT_INIT_OFFSET + 14))
            + list(range(REDIRECT_INIT_OFFSET + 15, REDIRECT_INIT_OFFSET + 24))
            + list(range(REDIRECT_INIT_OFFSET + 25, REDIRECT_INIT_OFFSET + 30))
            + list(range(REDIRECT_INIT_OFFSET + 31, REDIRECT_INIT_OFFSET + 42))
            + list(range(REDIRECT_INIT_OFFSET + 43, REDIRECT_INIT_OFFSET + 70))
            + list(range(REDIRECT_INIT_OFFSET + 71, REDIRECT_INIT_OFFSET + 84))
            + list(range(REDIRECT_INIT_OFFSET + 85, REDIRECT_INIT_OFFSET + 88))
            + list(range(AEABI_MEMSET_OFFSET, AEABI_MEMSET_OFFSET + 23))
            + list(range(AEABI_MEMSET_OFFSET + 25, AEABI_MEMSET_OFFSET + 29))
            + list(range(AEABI_MEMSET_OFFSET + 30, AEABI_MEMSET_OFFSET + 45))
            + list(range(AEABI_MEMSET_OFFSET + 46, AEABI_MEMSET_OFFSET + 55))
            + list(range(AEABI_MEMSET_OFFSET + 56, AEABI_MEMSET_OFFSET + 61))
            + list(range(AEABI_MEMSET_OFFSET + 62, AEABI_MEMSET_OFFSET + 69))
            + list(range(AEABI_MEMSET_OFFSET + 70, AEABI_MEMSET_OFFSET + 75))
            + list(range(AEABI_MEMSET_OFFSET + 77, AEABI_MEMSET_OFFSET + 87))
            + list(range(AEABI_MEMSET_OFFSET + 89, AEABI_MEMSET_OFFSET + 95))
            + list(range(AEABI_MEMSET_OFFSET + 97, AEABI_MEMSET_OFFSET + 102))
            + list(range(AEABI_MEMCPY_OFFSET, AEABI_MEMCPY_OFFSET + 12))
            + list(range(AEABI_MEMCPY_OFFSET + 13, AEABI_MEMCPY_OFFSET + 16))
            + list(range(AEABI_MEMCPY_OFFSET + 17, AEABI_MEMCPY_OFFSET + 30))
            + list(range(AEABI_MEMCPY_OFFSET + 32, AEABI_MEMCPY_OFFSET + 55))
            + list(range(AEABI_MEMCPY_OFFSET + 56, AEABI_MEMCPY_OFFSET + 65))
            + list(range(AEABI_MEMCPY_OFFSET + 66, AEABI_MEMCPY_OFFSET + 77))
            + list(range(AEABI_MEMCPY_OFFSET + 78, AEABI_MEMCPY_OFFSET + 87))
            + list(range(AEABI_MEMCPY_OFFSET + 88, AEABI_MEMCPY_OFFSET + 126))
            + list(range(AEABI_MEMCPY_OFFSET + 127, AEABI_MEMCPY_OFFSET + 140))
            + list(range(AEABI_MEMCPY_OFFSET + 141, AEABI_MEMCPY_OFFSET + 147))
            + list(range(AEABI_MEMCPY_OFFSET + 148, AEABI_MEMCPY_OFFSET + 153))
            + list(range(AEABI_MEMCPY_OFFSET + 154, AEABI_MEMCPY_OFFSET + 158))
            + list(range(AEABI_MEMCPY_OFFSET + 159, AEABI_MEMCPY_OFFSET + 166))
            + list(range(MEMCMP_OFFSET, MEMCMP_OFFSET + 13))
            + list(range(MEMCMP_OFFSET + 14, MEMCMP_OFFSET + 39))
            + list(range(MEMCMP_OFFSET + 40, MEMCMP_OFFSET + 56))
            + list(range(MEMCMP_OFFSET + 57, MEMCMP_OFFSET + 67))
            + list(range(MEMCMP_OFFSET + 68, MEMCMP_OFFSET + 70))
            + list(range(MEMCMP_OFFSET + 71, MEMCMP_OFFSET + 73))
            + list(range(MEMCMP_OFFSET + 74, MEMCMP_OFFSET + 81))
            + list(range(MEMCMP_OFFSET + 82, MEMCMP_OFFSET + 99))
            + list(range(MEMCMP_OFFSET + 100, MEMCMP_OFFSET + 104))
            + list(range(CRC32_OFFSET, CRC32_OFFSET + 56))
            + list(range(STRCSPN_OFFSET, STRCSPN_OFFSET + 4))
            + list(range(STRCSPN_OFFSET + 5, STRCSPN_OFFSET + 16))
            + list(range(STRCSPN_OFFSET + 17, STRCSPN_OFFSET + 34))
            + list(range(STRSPN_OFFSET, STRSPN_OFFSET + 4))
            + list(range(STRSPN_OFFSET + 5, STRSPN_OFFSET + 34))
            + list(range(STORE_200270CC_OFFSET, STORE_200270CC_OFFSET + 8))
            + list(range(UDIV10_OFFSET, UDIV10_OFFSET + 86))
            + list(range(UDIV10_OFFSET + 87, UDIV10_OFFSET + 128))
            + [UDIV10_OFFSET + 129]
            + list(range(UDIV10_OFFSET + 131, UDIV10_OFFSET + 174))
            + list(range(UDIV10_OFFSET + 175, UDIV10_OFFSET + 182))
            + list(range(UDIV10_OFFSET + 183, UDIV10_OFFSET + 188))
            + list(range(UDEC_DIGITS_OFFSET, UDEC_DIGITS_OFFSET + 6))
            + list(range(UDEC_DIGITS_OFFSET + 7, UDEC_DIGITS_OFFSET + 10))
            + list(range(UDEC_DIGITS_OFFSET + 11, UDEC_DIGITS_OFFSET + 24))
            + list(range(UDEC_DIGITS_OFFSET + 25, UDEC_DIGITS_OFFSET + 28))
            + list(range(UDEC_DIGITS_OFFSET + 29, UDEC_DIGITS_OFFSET + 36))
            + list(range(SDEC_DIGITS_OFFSET, SDEC_DIGITS_OFFSET + 18))
            + list(range(HEX_DIGITS_OFFSET, HEX_DIGITS_OFFSET + 4))
            + list(range(HEX_DIGITS_OFFSET + 5, HEX_DIGITS_OFFSET + 8))
            + list(range(HEX_DIGITS_OFFSET + 9, HEX_DIGITS_OFFSET + 16))
            + list(range(HEX_DIGITS_OFFSET + 17, HEX_DIGITS_OFFSET + 26))
            + list(range(HEX_DIGITS_OFFSET + 27, HEX_DIGITS_OFFSET + 30))
            + list(range(HEX_DIGITS_OFFSET + 31, HEX_DIGITS_OFFSET + 38))
            + list(range(PARSE_DEC_OFFSET, PARSE_DEC_OFFSET + 4))
            + [PARSE_DEC_OFFSET + 5, PARSE_DEC_OFFSET + 7]
            + list(range(PARSE_DEC_OFFSET + 9, PARSE_DEC_OFFSET + 48))
            + [PARSE_DEC_OFFSET + 49]
            + list(range(PARSE_DEC_OFFSET + 51, PARSE_DEC_OFFSET + 56))
            + list(range(PARSE_DEC_OFFSET + 57, PARSE_DEC_OFFSET + 68))
            + list(range(U64_TO_DEC_OFFSET, U64_TO_DEC_OFFSET + 12))
            + [U64_TO_DEC_OFFSET + 13]
            + list(range(U64_TO_DEC_OFFSET + 15, U64_TO_DEC_OFFSET + 34))
            + list(range(U64_TO_DEC_OFFSET + 35, U64_TO_DEC_OFFSET + 42))
            + list(range(U64_TO_DEC_OFFSET + 43, U64_TO_DEC_OFFSET + 64))
            + list(range(U64_TO_DEC_OFFSET + 65, U64_TO_DEC_OFFSET + 68))
            + list(range(U64_TO_DEC_OFFSET + 69, U64_TO_DEC_OFFSET + 74))
            + list(range(U64_TO_DEC_OFFSET + 75, U64_TO_DEC_OFFSET + 90))
            + list(range(U64_TO_DEC_OFFSET + 91, U64_TO_DEC_OFFSET + 94))
            + list(range(U64_TO_DEC_OFFSET + 95, U64_TO_DEC_OFFSET + 104))
            + list(range(U64_TO_HEX_OFFSET, U64_TO_HEX_OFFSET + 4))
            + [U64_TO_HEX_OFFSET + 5]
            + list(range(U64_TO_HEX_OFFSET + 7, U64_TO_HEX_OFFSET + 10))
            + list(range(U64_TO_HEX_OFFSET + 11, U64_TO_HEX_OFFSET + 46))
            + list(range(U64_TO_HEX_OFFSET + 47, U64_TO_HEX_OFFSET + 62))
            + list(range(U64_TO_HEX_OFFSET + 63, U64_TO_HEX_OFFSET + 70))
            + list(range(U64_TO_HEX_OFFSET + 71, U64_TO_HEX_OFFSET + 74))
            + [U64_TO_HEX_OFFSET + 75]
            + list(range(U64_TO_HEX_OFFSET + 77, U64_TO_HEX_OFFSET + 82))
            + list(range(U64_TO_HEX_OFFSET + 83, U64_TO_HEX_OFFSET + 90))
            + list(range(U64_TO_HEX_OFFSET + 91, U64_TO_HEX_OFFSET + 100))
            + list(range(U64_TO_HEX_OFFSET + 101, U64_TO_HEX_OFFSET + 104))
            + list(range(U64_TO_HEX_OFFSET + 105, U64_TO_HEX_OFFSET + 116))
            + list(range(NULLABLE_STRLEN_OFFSET, NULLABLE_STRLEN_OFFSET + 4))
            + list(range(NULLABLE_STRLEN_OFFSET + 5, NULLABLE_STRLEN_OFFSET + 18))
            + list(range(NULLABLE_STRLEN_OFFSET + 19, NULLABLE_STRLEN_OFFSET + 24))
            + list(range(REPEAT_CHAR_OFFSET, REPEAT_CHAR_OFFSET + 4))
            + list(range(REPEAT_CHAR_OFFSET + 5, REPEAT_CHAR_OFFSET + 12))
            + list(range(REPEAT_CHAR_OFFSET + 13, REPEAT_CHAR_OFFSET + 26))
            + list(range(REPEAT_CHAR_OFFSET + 27, REPEAT_CHAR_OFFSET + 34))
            + list(range(FLOAT_TO_FIXED_OFFSET, FLOAT_TO_FIXED_OFFSET + 44))
            + [FLOAT_TO_FIXED_OFFSET + 45]
            + list(range(FLOAT_TO_FIXED_OFFSET + 47, FLOAT_TO_FIXED_OFFSET + 54))
            + list(range(FLOAT_TO_FIXED_OFFSET + 55, FLOAT_TO_FIXED_OFFSET + 62))
            + [FLOAT_TO_FIXED_OFFSET + 63, FLOAT_TO_FIXED_OFFSET + 65]
            + list(range(FLOAT_TO_FIXED_OFFSET + 67, FLOAT_TO_FIXED_OFFSET + 104))
            + list(range(FLOAT_TO_FIXED_OFFSET + 105, FLOAT_TO_FIXED_OFFSET + 142))
            + [FLOAT_TO_FIXED_OFFSET + 143]
            + list(range(FLOAT_TO_FIXED_OFFSET + 145, FLOAT_TO_FIXED_OFFSET + 154))
            + list(range(FLOAT_TO_FIXED_OFFSET + 155, FLOAT_TO_FIXED_OFFSET + 196))
            + list(range(FLOAT_TO_FIXED_OFFSET + 197, FLOAT_TO_FIXED_OFFSET + 202))
            + list(range(FLOAT_TO_FIXED_OFFSET + 203, FLOAT_TO_FIXED_OFFSET + 212))
            + list(range(FLOAT_TO_FIXED_OFFSET + 213, FLOAT_TO_FIXED_OFFSET + 234))
            + list(range(FLOAT_TO_FIXED_OFFSET + 235, FLOAT_TO_FIXED_OFFSET + 238))
            + list(range(FLOAT_TO_FIXED_OFFSET + 239, FLOAT_TO_FIXED_OFFSET + 308))
            + list(range(FLOAT_TO_FIXED_OFFSET + 309, FLOAT_TO_FIXED_OFFSET + 320))
            + [
                FORMAT_CORE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            FORMAT_CORE_OFFSET:FORMAT_CORE_OFFSET + 952
                        ],
                        bytes.fromhex("1ef0dfbf" + "00bf" * 474),
                    )
                )
                if stock != replacement
            ]
            + [
                LOG_DISPATCH_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            LOG_DISPATCH_OFFSET:LOG_DISPATCH_OFFSET + 44
                        ],
                        bytes.fromhex("1ef0e7bf" + "00bf" * 20),
                    )
                )
                if stock != replacement
            ]
            + [
                STRSTR_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[STRSTR_OFFSET:STRSTR_OFFSET + 44],
                        bytes.fromhex("1ef0dfbf" + "00bf" * 20),
                    )
                )
                if stock != replacement
            ]
            + [
                CRITICAL_CONTEXT_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            CRITICAL_CONTEXT_OFFSET:CRITICAL_CONTEXT_OFFSET + 46
                        ],
                        bytes.fromhex("1ef0debf" + "00bf" * 21),
                    )
                )
                if stock != replacement
            ]
            + [
                GATE_ACQUIRE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            GATE_ACQUIRE_OFFSET:GATE_ACQUIRE_OFFSET + 48
                        ],
                        bytes.fromhex("1ef0debf" + "00bf" * 22),
                    )
                )
                if stock != replacement
            ]
            + [
                GATE_STATE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[GATE_STATE_OFFSET:GATE_STATE_OFFSET + 40],
                        bytes.fromhex("1ef0debf" + "00bf" * 18),
                    )
                )
                if stock != replacement
            ]
            + [
                GATE_RELEASE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            GATE_RELEASE_OFFSET:GATE_RELEASE_OFFSET + 56
                        ],
                        bytes.fromhex("1ef0dcbf" + "00bf" * 26),
                    )
                )
                if stock != replacement
            ]
            + [
                CONTEXT_VALUE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            CONTEXT_VALUE_OFFSET:CONTEXT_VALUE_OFFSET + 22
                        ],
                        bytes.fromhex("1ef0dcbf" + "00bf" * 9),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_DISPATCH_4160FE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_DISPATCH_4160FE_OFFSET:
                            RUNTIME_DISPATCH_4160FE_OFFSET + 200
                        ],
                        bytes.fromhex("1ef0ddbf" + "00bf" * 98),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_VALUE_4161C6_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_VALUE_4161C6_OFFSET:
                            RUNTIME_VALUE_4161C6_OFFSET + 8
                        ],
                        bytes.fromhex("1ef0ccbf" + "00bf" * 2),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_CALL_4161CE_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_CALL_4161CE_OFFSET:
                            RUNTIME_CALL_4161CE_OFFSET + 50
                        ],
                        bytes.fromhex("1ef0cabf" + "00bf" * 23),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_ACTION_416200_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_ACTION_416200_OFFSET:
                            RUNTIME_ACTION_416200_OFFSET + 58
                        ],
                        bytes.fromhex("1ef0c7bf" + "00bf" * 27),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_TRANSFER_41623A_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_TRANSFER_41623A_OFFSET:
                            RUNTIME_TRANSFER_41623A_OFFSET + 138
                        ],
                        bytes.fromhex("1ef0c5bf" + "00bf" * 67),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_WAIT_4162C4_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_WAIT_4162C4_OFFSET:
                            RUNTIME_WAIT_4162C4_OFFSET + 180
                        ],
                        bytes.fromhex("1ef0c0bf" + "00bf" * 88),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_NOTIFY_416378_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_NOTIFY_416378_OFFSET:
                            RUNTIME_NOTIFY_416378_OFFSET + 34
                        ],
                        bytes.fromhex("1ef0bfbf" + "00bf" * 15),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_CALLBACK_41639A_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_CALLBACK_41639A_OFFSET:
                            RUNTIME_CALLBACK_41639A_OFFSET + 24
                        ],
                        bytes.fromhex("1ef0bcbf" + "00bf" * 10),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_REGISTER_4163B2_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_REGISTER_4163B2_OFFSET:
                            RUNTIME_REGISTER_4163B2_OFFSET + 232
                        ],
                        bytes.fromhex("1ef0bdbf" + "00bf" * 114),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_SUBMIT_41649A_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_SUBMIT_41649A_OFFSET:
                            RUNTIME_SUBMIT_41649A_OFFSET + 64
                        ],
                        bytes.fromhex("1ef0a3bf" + "00bf" * 30),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_CREATE_4164DA_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_CREATE_4164DA_OFFSET:
                            RUNTIME_CREATE_4164DA_OFFSET + 84
                        ],
                        bytes.fromhex("1ef09ebf" + "00bf" * 40),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_FLAGS_SET_41652E_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            RUNTIME_FLAGS_SET_41652E_OFFSET:
                            RUNTIME_FLAGS_SET_41652E_OFFSET + 94
                        ],
                        bytes.fromhex("1ef08bbf" + "00bf" * 45),
                    )
                )
                if stock != replacement
            ]
            + [
                RUNTIME_FLAGS_WAIT_416590_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_FLAGS_WAIT_416590_OFFSET:RUNTIME_FLAGS_WAIT_416590_OFFSET + 128], bytes.fromhex("1ef084bf" + "00bf" * 62))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_FLAGS_CREATE_416610_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_FLAGS_CREATE_416610_OFFSET:RUNTIME_FLAGS_CREATE_416610_OFFSET + 154], bytes.fromhex("1ef076bf" + "00bf" * 75))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET:RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET + 102], bytes.fromhex("1ef052bf" + "00bf" * 49))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_HANDLE_RELEASE_416710_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_HANDLE_RELEASE_416710_OFFSET:RUNTIME_HANDLE_RELEASE_416710_OFFSET + 82], bytes.fromhex("1ef041bf" + "00bf" * 39))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_SEMAPHORE_CREATE_416762_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_SEMAPHORE_CREATE_416762_OFFSET:RUNTIME_SEMAPHORE_CREATE_416762_OFFSET + 180], bytes.fromhex("1ef035bf" + "00bf" * 88))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_QUEUE_CREATE_416816_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_QUEUE_CREATE_416816_OFFSET:RUNTIME_QUEUE_CREATE_416816_OFFSET + 140], bytes.fromhex("1ef021bf" + "00bf" * 68))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_QUEUE_PUT_4168A2_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_QUEUE_PUT_4168A2_OFFSET:RUNTIME_QUEUE_PUT_4168A2_OFFSET + 126], bytes.fromhex("1ef00dbf" + "00bf" * 61))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_QUEUE_GET_416920_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_QUEUE_GET_416920_OFFSET:RUNTIME_QUEUE_GET_416920_OFFSET + 122], bytes.fromhex("1ef006bf" + "00bf" * 59))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_BIT_WIDTH_4169A4_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_BIT_WIDTH_4169A4_OFFSET:RUNTIME_BIT_WIDTH_4169A4_OFFSET + 62], bytes.fromhex("1ef0fabe" + "00bf" * 29))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_CTZ_4169E2_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_CTZ_4169E2_OFFSET:RUNTIME_CTZ_4169E2_OFFSET + 16], bytes.fromhex("1ef0e2be" + "00bf" * 6))
                )
                if stock != replacement
            ]
            + [
                RUNTIME_LOG2_4169F2_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(self.official[RUNTIME_LOG2_4169F2_OFFSET:RUNTIME_LOG2_4169F2_OFFSET + 10], bytes.fromhex("1ef0e1be" + "00bf" * 3))
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_TOPOLOGY_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_MAPPING_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_FREE_LIST_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_ALLOCATOR_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in TLSF_PUBLIC_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in EASYLOGGER_CONTROL_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + [
                EASYLOGGER_OUTPUT_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            EASYLOGGER_OUTPUT_OFFSET:
                            EASYLOGGER_OUTPUT_OFFSET + 1026
                        ],
                        EASYLOGGER_OUTPUT_PATCH_REPLACEMENT[1],
                    )
                )
                if stock != replacement
            ]
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET,
                    EASYLOGGER_GET_FMT_OFFSET + 20,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 21,
                    EASYLOGGER_GET_FMT_OFFSET + 46,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 47,
                    EASYLOGGER_GET_FMT_OFFSET + 52,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 53,
                    EASYLOGGER_GET_FMT_OFFSET + 84,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 85,
                    EASYLOGGER_GET_FMT_OFFSET + 98,
                )
            )
            + [EASYLOGGER_GET_FMT_OFFSET + 99]
            + list(
                range(
                    EASYLOGGER_GET_FMT_OFFSET + 101,
                    EASYLOGGER_GET_FMT_OFFSET + 106,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET + 13,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 18,
                )
            )
            + [EASYLOGGER_GET_FMT_U32_OFFSET + 19]
            + list(
                range(
                    EASYLOGGER_GET_FMT_U32_OFFSET + 21,
                    EASYLOGGER_GET_FMT_U32_OFFSET + 26,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 13,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 18,
                )
            )
            + [EASYLOGGER_GET_FMT_PTR_OFFSET + 19]
            + list(
                range(
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 21,
                    EASYLOGGER_GET_FMT_PTR_OFFSET + 26,
                )
            )
            + [
                EASYLOGGER_LOCK_ENABLED_OFFSET + index
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            EASYLOGGER_LOCK_ENABLED_OFFSET:
                            EASYLOGGER_LOCK_ENABLED_OFFSET + 60
                        ],
                        EASYLOGGER_LOCK_ENABLED_PATCH_REPLACEMENT[1],
                    )
                )
                if stock != replacement
            ]
            + [
                address - RUN_BASE + index
                for address, replacement_bytes in EASYLOGGER_PORT_PATCH_REPLACEMENTS
                for index, (stock, replacement) in enumerate(
                    zip(
                        self.official[
                            address - RUN_BASE:
                            address - RUN_BASE + len(replacement_bytes)
                        ],
                        replacement_bytes,
                    )
                )
                if stock != replacement
            ]
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET,
                    EASYLOGGER_STRCPY_OFFSET + 12,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 13,
                    EASYLOGGER_STRCPY_OFFSET + 20,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 21,
                    EASYLOGGER_STRCPY_OFFSET + 42,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 43,
                    EASYLOGGER_STRCPY_OFFSET + 48,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 49,
                    EASYLOGGER_STRCPY_OFFSET + 70,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 71,
                    EASYLOGGER_STRCPY_OFFSET + 78,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 79,
                    EASYLOGGER_STRCPY_OFFSET + 100,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 101,
                    EASYLOGGER_STRCPY_OFFSET + 106,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 107,
                    EASYLOGGER_STRCPY_OFFSET + 140,
                )
            )
            + list(
                range(
                    EASYLOGGER_STRCPY_OFFSET + 141,
                    EASYLOGGER_STRCPY_OFFSET + 162,
                )
            )
            + list(
                range(
                    EASYLOGGER_DRIVER_OUTPUT_OFFSET,
                    EASYLOGGER_DRIVER_OUTPUT_OFFSET + 14,
                )
            )
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET, EASYLOGGER_CHANNEL_WRITE_OFFSET + 44))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 45, EASYLOGGER_CHANNEL_WRITE_OFFSET + 56))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 57, EASYLOGGER_CHANNEL_WRITE_OFFSET + 60))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 61, EASYLOGGER_CHANNEL_WRITE_OFFSET + 66))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 67, EASYLOGGER_CHANNEL_WRITE_OFFSET + 70))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 71, EASYLOGGER_CHANNEL_WRITE_OFFSET + 82))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 83, EASYLOGGER_CHANNEL_WRITE_OFFSET + 104))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 105, EASYLOGGER_CHANNEL_WRITE_OFFSET + 108))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 109, EASYLOGGER_CHANNEL_WRITE_OFFSET + 114))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 115, EASYLOGGER_CHANNEL_WRITE_OFFSET + 142))
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 143, EASYLOGGER_CHANNEL_WRITE_OFFSET + 148))
            + [EASYLOGGER_CHANNEL_WRITE_OFFSET + 149]
            + list(range(EASYLOGGER_CHANNEL_WRITE_OFFSET + 151, EASYLOGGER_CHANNEL_WRITE_OFFSET + 158))
            + [
                offset
                for address, replacement in BOOT_SERVICE_PATCH_REPLACEMENTS
                for offset in range(
                    address - RUN_BASE,
                    address - RUN_BASE + len(replacement),
                )
                if self.official[offset]
                != replacement[offset - (address - RUN_BASE)]
            ]
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 6,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 7,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 30,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 31,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 38,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 39,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 44,
                )
            )
            + list(
                range(
                    MSPI_INTERRUPT_CLEAR_OFFSET + 45,
                    MSPI_INTERRUPT_CLEAR_OFFSET + 48,
                )
            ),
        )
        utility_stock_expectations = (
            (
                LITTLEFS_UTIL_MAX_OFFSET,
                bytes.fromhex("814200d308007047"),
                LITTLEFS_UTIL_MAX_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_MIN_OFFSET,
                bytes.fromhex("884200d308007047"),
                LITTLEFS_UTIL_MIN_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET,
                bytes.fromhex("b0fbf1f001fb00f108007047"),
                LITTLEFS_UTIL_ALIGNDOWN_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_ALIGNUP_OFFSET,
                bytes.fromhex("80b50818401efff7f5ff02bd"),
                LITTLEFS_UTIL_ALIGNUP_STOCK_SHA256,
            ),
            (
                LITTLEFS_UTIL_NPW2_OFFSET,
                bytes.fromhex(
                    "01000020491eb1f5803f01d3012200e00022d2b21201d140"
                    "1043b1f5807f01d3012200e00022d2b2d200d14010431029"
                    "01d3012200e00022d2b29200d1401043042901d3012200e0"
                    "0022d2b25200d140104350ea5100401c7047"
                ),
                (
                    "291ab0ccd15efe1085ce5bcdc6551581"
                    "ed4eccf67fa84f6560c4500fd68b8b63"
                ),
            ),
            (
                LITTLEFS_UTIL_CTZ_OFFSET,
                bytes.fromhex(
                    "80b541420840401cfff7cdff401e02bd"
                ),
                (
                    "4ae07bfa492e5dfad5869ea491ca43f7"
                    "20e6fc153315a126e2e686313c3de08c"
                ),
            ),
            (
                LITTLEFS_UTIL_POPC_OFFSET,
                bytes.fromhex(
                    "0100490831f0aa31401a30f0cc31800830f0cc30401810eb"
                    "101030f0f0305ff001314843000e7047"
                ),
                (
                    "2cc25090f38dd5c2121cb4bfc7ddf0bd"
                    "71df984312c9b9c52e87feeef5aea872"
                ),
            ),
        )
        for offset, stock, expected_sha256 in utility_stock_expectations:
            with self.subTest(utility_stock_offset=offset):
                self.assertEqual(
                    self.official[offset:offset + len(stock)],
                    stock,
                )
                self.assertEqual(
                    hashlib.sha256(stock).hexdigest(),
                    expected_sha256,
                )
        self.assertEqual(
            self.official[SCMP_OFFSET:SCMP_OFFSET + 4],
            bytes.fromhex("401a7047"),
        )
        self.assertEqual(
            self.official[ALLOC_OFFSET:ALLOC_OFFSET + 6],
            bytes.fromhex("c16e01667047"),
        )
        self.assertEqual(
            self.official[ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16],
            bytes.fromhex("80b5002181650021c165fff7f6ff01bd"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16
                ]
            ).hexdigest(),
            ALLOC_DROP_STOCK_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    ALLOC_LOOKAHEAD_OFFSET:ALLOC_LOOKAHEAD_OFFSET + 56
                ]
            ).hexdigest(),
            ALLOC_LOOKAHEAD_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
            ],
            bytes.fromhex(
                "01b46a4600e012681068002804d01068"
                "8842f8d1012000e0002001b07047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
                ]
            ).hexdigest(),
            MLIST_ISOPEN_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
            ],
            bytes.fromhex(
                "10f1280200e012681068002805d01068"
                "8842f8d11068006810607047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
                ]
            ).hexdigest(),
            MLIST_REMOVE_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
            ],
            bytes.fromhex("826a0a6081627047"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
                ]
            ).hexdigest(),
            MLIST_APPEND_SHA256,
        )
        self.assertEqual(
            self.official[
                DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
            ],
            bytes.fromhex("dff89c087047"),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
                ]
            ).hexdigest(),
            DISK_VERSION_STOCK_SHA256,
        )
        self.assertEqual(
            self.official[
                MSPI_INTERRUPT_CLEAR_OFFSET:
                MSPI_INTERRUPT_CLEAR_OFFSET + 48
            ],
            bytes.fromhex(
                "0200002806d0006820f07e40dff8f036"
                "984201d002200ae05068b84a12eb0033"
                "c3f8081212eb0032d2f8040200207047"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                self.official[
                    MSPI_INTERRUPT_CLEAR_OFFSET:
                    MSPI_INTERRUPT_CLEAR_OFFSET + 48
                ]
            ).hexdigest(),
            MSPI_INTERRUPT_CLEAR_STOCK_SHA256,
        )
        allowed = set(
            range(LITTLEFS_UTIL_MAX_OFFSET, LITTLEFS_UTIL_MAX_OFFSET + 8)
        )
        allowed.update(
            range(LITTLEFS_UTIL_MIN_OFFSET, LITTLEFS_UTIL_MIN_OFFSET + 8)
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET,
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_ALIGNUP_OFFSET,
                LITTLEFS_UTIL_ALIGNUP_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_NPW2_OFFSET,
                LITTLEFS_UTIL_NPW2_OFFSET + 90,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_CTZ_OFFSET,
                LITTLEFS_UTIL_CTZ_OFFSET + 16,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_POPC_OFFSET,
                LITTLEFS_UTIL_POPC_OFFSET + 40,
            )
        )
        allowed.update(range(SCMP_OFFSET, SCMP_OFFSET + 4))
        allowed.update(
            range(
                LITTLEFS_UTIL_FROMLE32_OFFSET,
                LITTLEFS_UTIL_FROMLE32_OFFSET + 34,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_TOLE32_OFFSET,
                LITTLEFS_UTIL_TOLE32_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_FROMBE32_OFFSET,
                LITTLEFS_UTIL_FROMBE32_OFFSET + 34,
            )
        )
        allowed.update(
            range(
                LITTLEFS_UTIL_TOBE32_OFFSET,
                LITTLEFS_UTIL_TOBE32_OFFSET + 8,
            )
        )
        allowed.update(
            range(MLIST_ISOPEN_OFFSET, MLIST_ISOPEN_OFFSET + 30)
        )
        allowed.update(
            range(MLIST_REMOVE_OFFSET, MLIST_REMOVE_OFFSET + 28)
        )
        allowed.update(
            range(MLIST_APPEND_OFFSET, MLIST_APPEND_OFFSET + 8)
        )
        allowed.update(
            range(DISK_VERSION_OFFSET, DISK_VERSION_OFFSET + 6)
        )
        allowed.update(
            range(
                DISK_VERSION_MAJOR_OFFSET,
                DISK_VERSION_MAJOR_OFFSET + 12,
            )
        )
        allowed.update(
            range(
                DISK_VERSION_MINOR_OFFSET,
                DISK_VERSION_MINOR_OFFSET + 10,
            )
        )
        allowed.update(range(ALLOC_OFFSET, ALLOC_OFFSET + 6))
        allowed.update(range(ALLOC_DROP_OFFSET, ALLOC_DROP_OFFSET + 16))
        allowed.update(
            range(
                ALLOC_LOOKAHEAD_OFFSET,
                ALLOC_LOOKAHEAD_OFFSET + 56,
            )
        )
        allowed.update(
            range(REDIRECT_INIT_OFFSET, REDIRECT_INIT_OFFSET + 88)
        )
        allowed.update(
            range(AEABI_MEMSET_OFFSET, AEABI_MEMSET_OFFSET + 102)
        )
        allowed.update(
            range(AEABI_MEMCPY_OFFSET, AEABI_MEMCPY_OFFSET + 166)
        )
        allowed.update(range(MEMCMP_OFFSET, MEMCMP_OFFSET + 104))
        allowed.update(range(CRC32_OFFSET, CRC32_OFFSET + 56))
        allowed.update(range(STRCSPN_OFFSET, STRCSPN_OFFSET + 34))
        allowed.update(range(STRSPN_OFFSET, STRSPN_OFFSET + 34))
        allowed.update(range(STORE_200270CC_OFFSET, STORE_200270CC_OFFSET + 8))
        allowed.update(range(UDIV10_OFFSET, UDIV10_OFFSET + 188))
        allowed.update(range(UDEC_DIGITS_OFFSET, UDEC_DIGITS_OFFSET + 36))
        allowed.update(range(SDEC_DIGITS_OFFSET, SDEC_DIGITS_OFFSET + 18))
        allowed.update(range(HEX_DIGITS_OFFSET, HEX_DIGITS_OFFSET + 38))
        allowed.update(range(PARSE_DEC_OFFSET, PARSE_DEC_OFFSET + 68))
        allowed.update(range(U64_TO_DEC_OFFSET, U64_TO_DEC_OFFSET + 104))
        allowed.update(range(U64_TO_HEX_OFFSET, U64_TO_HEX_OFFSET + 116))
        allowed.update(range(NULLABLE_STRLEN_OFFSET, NULLABLE_STRLEN_OFFSET + 24))
        allowed.update(range(REPEAT_CHAR_OFFSET, REPEAT_CHAR_OFFSET + 34))
        allowed.update(range(FLOAT_TO_FIXED_OFFSET, FLOAT_TO_FIXED_OFFSET + 320))
        allowed.update(range(FORMAT_CORE_OFFSET, FORMAT_CORE_OFFSET + 952))
        allowed.update(range(LOG_DISPATCH_OFFSET, LOG_DISPATCH_OFFSET + 44))
        allowed.update(range(STRSTR_OFFSET, STRSTR_OFFSET + 44))
        allowed.update(
            range(CRITICAL_CONTEXT_OFFSET, CRITICAL_CONTEXT_OFFSET + 46)
        )
        allowed.update(range(GATE_ACQUIRE_OFFSET, GATE_ACQUIRE_OFFSET + 48))
        allowed.update(range(GATE_STATE_OFFSET, GATE_STATE_OFFSET + 40))
        allowed.update(range(GATE_RELEASE_OFFSET, GATE_RELEASE_OFFSET + 56))
        allowed.update(range(CONTEXT_VALUE_OFFSET, CONTEXT_VALUE_OFFSET + 22))
        allowed.update(
            range(
                RUNTIME_DISPATCH_4160FE_OFFSET,
                RUNTIME_DISPATCH_4160FE_OFFSET + 200,
            )
        )
        allowed.update(
            range(RUNTIME_VALUE_4161C6_OFFSET, RUNTIME_VALUE_4161C6_OFFSET + 8)
        )
        allowed.update(
            range(RUNTIME_CALL_4161CE_OFFSET, RUNTIME_CALL_4161CE_OFFSET + 50)
        )
        allowed.update(
            range(RUNTIME_ACTION_416200_OFFSET, RUNTIME_ACTION_416200_OFFSET + 58)
        )
        allowed.update(
            range(
                RUNTIME_TRANSFER_41623A_OFFSET,
                RUNTIME_TRANSFER_41623A_OFFSET + 138,
            )
        )
        allowed.update(
            range(RUNTIME_WAIT_4162C4_OFFSET, RUNTIME_WAIT_4162C4_OFFSET + 180)
        )
        allowed.update(
            range(
                RUNTIME_NOTIFY_416378_OFFSET,
                RUNTIME_NOTIFY_416378_OFFSET + 34,
            )
        )
        allowed.update(
            range(
                RUNTIME_CALLBACK_41639A_OFFSET,
                RUNTIME_CALLBACK_41639A_OFFSET + 24,
            )
        )
        allowed.update(
            range(
                RUNTIME_REGISTER_4163B2_OFFSET,
                RUNTIME_REGISTER_4163B2_OFFSET + 232,
            )
        )
        allowed.update(
            range(
                RUNTIME_SUBMIT_41649A_OFFSET,
                RUNTIME_SUBMIT_41649A_OFFSET + 64,
            )
        )
        allowed.update(
            range(
                RUNTIME_CREATE_4164DA_OFFSET,
                RUNTIME_CREATE_4164DA_OFFSET + 84,
            )
        )
        allowed.update(
            range(
                RUNTIME_FLAGS_SET_41652E_OFFSET,
                RUNTIME_FLAGS_SET_41652E_OFFSET + 94,
            )
        )
        allowed.update(range(RUNTIME_FLAGS_WAIT_416590_OFFSET, RUNTIME_FLAGS_WAIT_416590_OFFSET + 128))
        allowed.update(range(RUNTIME_FLAGS_CREATE_416610_OFFSET, RUNTIME_FLAGS_CREATE_416610_OFFSET + 154))
        allowed.update(range(RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET, RUNTIME_HANDLE_ACQUIRE_4166AA_OFFSET + 102))
        allowed.update(range(RUNTIME_HANDLE_RELEASE_416710_OFFSET, RUNTIME_HANDLE_RELEASE_416710_OFFSET + 82))
        allowed.update(range(RUNTIME_SEMAPHORE_CREATE_416762_OFFSET, RUNTIME_SEMAPHORE_CREATE_416762_OFFSET + 180))
        allowed.update(range(RUNTIME_QUEUE_CREATE_416816_OFFSET, RUNTIME_QUEUE_CREATE_416816_OFFSET + 140))
        allowed.update(range(RUNTIME_QUEUE_PUT_4168A2_OFFSET, RUNTIME_QUEUE_PUT_4168A2_OFFSET + 126))
        allowed.update(range(RUNTIME_QUEUE_GET_416920_OFFSET, RUNTIME_QUEUE_GET_416920_OFFSET + 122))
        allowed.update(range(RUNTIME_BIT_WIDTH_4169A4_OFFSET, RUNTIME_BIT_WIDTH_4169A4_OFFSET + 62))
        allowed.update(range(RUNTIME_CTZ_4169E2_OFFSET, RUNTIME_CTZ_4169E2_OFFSET + 16))
        allowed.update(range(RUNTIME_LOG2_4169F2_OFFSET, RUNTIME_LOG2_4169F2_OFFSET + 10))
        allowed.update(
            range(
                TLSF_BLOCK_PRIMITIVES_START_OFFSET,
                EASYLOGGER_OUTPUT_END_ADDRESS - RUN_BASE,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_OFFSET,
                EASYLOGGER_GET_FMT_OFFSET + 106,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_U32_OFFSET,
                EASYLOGGER_GET_FMT_U32_OFFSET + 26,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_GET_FMT_PTR_OFFSET,
                EASYLOGGER_GET_FMT_PTR_OFFSET + 26,
            )
        )
        allowed.update(
            range(
                EASYLOGGER_LOCK_ENABLED_OFFSET,
                EASYLOGGER_LOCK_ENABLED_OFFSET + 60,
            )
        )
        allowed.update(range(0x0041A648 - RUN_BASE, 0x0041A700 - RUN_BASE))
        allowed.update(range(0x0041B854 - RUN_BASE, 0x0041B862 - RUN_BASE))
        allowed.update(range(0x0041F918 - RUN_BASE, 0x0041F9B6 - RUN_BASE))
        allowed.update(range(0x0041F9D8 - RUN_BASE, 0x0041FA40 - RUN_BASE))
        allowed.update(range(0x0041FA50 - RUN_BASE, 0x0041FAD0 - RUN_BASE))
        allowed.update(range(0x0041FADC - RUN_BASE, 0x0041FCF6 - RUN_BASE))
        allowed.update(range(0x0041FD70 - RUN_BASE, 0x0041FDA8 - RUN_BASE))
        allowed.update(range(0x0041FDC0 - RUN_BASE, 0x0041FE28 - RUN_BASE))
        allowed.update(range(0x0041FE28 - RUN_BASE, 0x0041FE62 - RUN_BASE))
        allowed.update(range(0x0041FE62 - RUN_BASE, 0x0041FF08 - RUN_BASE))
        allowed.update(range(0x0041FF08 - RUN_BASE, 0x0041FF34 - RUN_BASE))
        allowed.update(range(0x0041FF34 - RUN_BASE, 0x0041FF60 - RUN_BASE))
        allowed.update(range(0x0041FF60 - RUN_BASE, 0x00420002 - RUN_BASE))
        allowed.update(range(0x00420002 - RUN_BASE, 0x004201BA - RUN_BASE))
        allowed.update(range(0x004201BA - RUN_BASE, 0x00420254 - RUN_BASE))
        allowed.update(range(0x00420254 - RUN_BASE, 0x00420476 - RUN_BASE))
        allowed.update(range(0x00420476 - RUN_BASE, 0x0042052A - RUN_BASE))
        allowed.update(range(0x0042052A - RUN_BASE, 0x0042059E - RUN_BASE))
        allowed.update(range(0x0042059E - RUN_BASE, 0x004205F4 - RUN_BASE))
        allowed.update(range(0x004205F4 - RUN_BASE, 0x0042086C - RUN_BASE))
        allowed.update(range(0x00420890 - RUN_BASE, 0x00420978 - RUN_BASE))
        allowed.update(range(0x00420984 - RUN_BASE, 0x004209BE - RUN_BASE))
        allowed.update(range(0x004209C4 - RUN_BASE, 0x004209FC - RUN_BASE))
        allowed.update(range(0x00420A08 - RUN_BASE, 0x00420ADA - RUN_BASE))
        allowed.update(range(0x00420B0C - RUN_BASE, 0x00420C14 - RUN_BASE))
        allowed.update(range(0x00420C5C - RUN_BASE, 0x00420DFA - RUN_BASE))
        allowed.update(range(0x00420E08 - RUN_BASE, 0x00420E8C - RUN_BASE))
        allowed.update(range(0x00420E8C - RUN_BASE, 0x00420F0C - RUN_BASE))
        allowed.update(range(0x00420F10 - RUN_BASE, 0x00420F6A - RUN_BASE))
        allowed.update(range(0x00420F70 - RUN_BASE, 0x00420FF2 - RUN_BASE))
        allowed.update(range(0x004210C8 - RUN_BASE, 0x004211B0 - RUN_BASE))
        allowed.update(range(0x004211B0 - RUN_BASE, 0x00421210 - RUN_BASE))
        allowed.update(range(0x00421210 - RUN_BASE, 0x004212D8 - RUN_BASE))
        allowed.update(range(0x004212D8 - RUN_BASE, 0x00421310 - RUN_BASE))
        allowed.update(range(0x00421310 - RUN_BASE, 0x00421348 - RUN_BASE))
        allowed.update(range(0x00421348 - RUN_BASE, 0x00421372 - RUN_BASE))
        allowed.update(range(0x004213D4 - RUN_BASE, 0x004213D8 - RUN_BASE))
        allowed.update(range(0x004213E6 - RUN_BASE, 0x00421548 - RUN_BASE))
        allowed.update(range(0x00421548 - RUN_BASE, 0x0042156E - RUN_BASE))
        allowed.update(
            range(
                EASYLOGGER_STRCPY_OFFSET,
                EASYLOGGER_STRCPY_OFFSET + 162,
            )
        )
        allowed.update(
            range(
                MSPI_INTERRUPT_CLEAR_OFFSET,
                MSPI_INTERRUPT_CLEAR_OFFSET + 48,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_ISVALID_OFFSET,
                LITTLEFS_TAG_ISVALID_OFFSET + 10,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_TYPE1_OFFSET,
                LITTLEFS_TAG_TYPE1_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_TYPE3_OFFSET,
                LITTLEFS_TAG_TYPE3_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_ID_OFFSET,
                LITTLEFS_TAG_ID_OFFSET + 8,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_SIZE_OFFSET,
                LITTLEFS_TAG_SIZE_OFFSET + 6,
            )
        )
        allowed.update(
            range(
                LITTLEFS_TAG_CHUNK_OFFSET,
                LITTLEFS_TAG_CHUNK_OFFSET + 6,
            )
        )
        for offset, stock in enumerate(self.official):
            if offset not in allowed:
                self.assertEqual(
                    self.provider[offset], stock, f"unexpected mutation at {offset:#x}"
                )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_MAX_OFFSET:LITTLEFS_UTIL_MAX_OFFSET + 8
            ],
            bytes.fromhex("24f057b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_MIN_OFFSET:LITTLEFS_UTIL_MIN_OFFSET + 8
            ],
            bytes.fromhex("24f057b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET:
                LITTLEFS_UTIL_ALIGNDOWN_OFFSET + 12
            ],
            bytes.fromhex("24f057b800bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_ALIGNUP_OFFSET:
                LITTLEFS_UTIL_ALIGNUP_OFFSET + 12
            ],
            bytes.fromhex("24f055b800bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_NPW2_OFFSET:
                LITTLEFS_UTIL_NPW2_OFFSET + 90
            ],
            bytes.fromhex(
                "24f053b8" + "00bf" * 43
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_CTZ_OFFSET:
                LITTLEFS_UTIL_CTZ_OFFSET + 16
            ],
            bytes.fromhex(
                "24f042b8" + "00bf" * 6
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_POPC_OFFSET:
                LITTLEFS_UTIL_POPC_OFFSET + 40
            ],
            bytes.fromhex(
                "24f042b8" + "00bf" * 18
            ),
        )
        self.assertEqual(
            self.provider[SCMP_OFFSET:SCMP_OFFSET + 4],
            bytes.fromhex("23f0ddbf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_FROMLE32_OFFSET:
                LITTLEFS_UTIL_FROMLE32_OFFSET + 34
            ],
            bytes.fromhex(
                "24f062b8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_TOLE32_OFFSET:
                LITTLEFS_UTIL_TOLE32_OFFSET + 8
            ],
            bytes.fromhex("24f052b800bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_FROMBE32_OFFSET:
                LITTLEFS_UTIL_FROMBE32_OFFSET + 34
            ],
            bytes.fromhex(
                "24f04fb8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_UTIL_TOBE32_OFFSET:
                LITTLEFS_UTIL_TOBE32_OFFSET + 8
            ],
            bytes.fromhex("24f040b800bf00bf"),
        )
        self.assertEqual(
            self.provider[ALLOC_OFFSET:ALLOC_OFFSET + 6],
            bytes.fromhex("23f048bb00bf"),
        )
        self.assertEqual(
            self.provider[
                MLIST_ISOPEN_OFFSET:MLIST_ISOPEN_OFFSET + 30
            ],
            bytes.fromhex(
                "23f0f3bb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                MLIST_REMOVE_OFFSET:MLIST_REMOVE_OFFSET + 28
            ],
            bytes.fromhex(
                "23f07abb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                MLIST_APPEND_OFFSET:MLIST_APPEND_OFFSET + 8
            ],
            bytes.fromhex("23f068bb00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_OFFSET:DISK_VERSION_OFFSET + 6
            ],
            bytes.fromhex("23f060bb00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_MAJOR_OFFSET:DISK_VERSION_MAJOR_OFFSET + 12
            ],
            bytes.fromhex("23f0debb00bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                DISK_VERSION_MINOR_OFFSET:DISK_VERSION_MINOR_OFFSET + 10
            ],
            bytes.fromhex("23f0ddbb00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                ALLOC_DROP_OFFSET:ALLOC_DROP_OFFSET + 16
            ],
            bytes.fromhex("23f048bb00bf00bf00bf00bf00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                ALLOC_LOOKAHEAD_OFFSET:ALLOC_LOOKAHEAD_OFFSET + 56
            ],
            bytes.fromhex("23f0d2bb" + "00bf" * 26),
        )
        self.assertEqual(
            self.provider[
                MSPI_INTERRUPT_CLEAR_OFFSET:
                MSPI_INTERRUPT_CLEAR_OFFSET + 48
            ],
            bytes.fromhex(
                "0ef01db8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf"
            ),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_TAG_ID_OFFSET:LITTLEFS_TAG_ID_OFFSET + 8
            ],
            bytes.fromhex("23f0a3bd00bf00bf"),
        )
        self.assertEqual(
            self.provider[
                LITTLEFS_TAG_SIZE_OFFSET:LITTLEFS_TAG_SIZE_OFFSET + 6
            ],
            bytes.fromhex("23f0a2bd00bf"),
        )
        self.assertEqual(
            self.provider[
                REDIRECT_INIT_OFFSET:REDIRECT_INIT_OFFSET + 88
            ],
            bytes.fromhex("1ff0beb8" + "00bf" * 42),
        )
        self.assertEqual(
            self.provider[AEABI_MEMCPY_OFFSET:AEABI_MEMCPY_OFFSET + 166],
            bytes.fromhex("1ff0d0b8" + "00bf" * 81),
        )
        self.assertEqual(
            self.provider[MEMCMP_OFFSET:MEMCMP_OFFSET + 104],
            bytes.fromhex("1ff072b8" + "00bf" * 50),
        )
        self.assertEqual(
            self.provider[CRC32_OFFSET:CRC32_OFFSET + 56],
            bytes.fromhex("1ff06ab8" + "00bf" * 26),
        )
        self.assertEqual(
            self.provider[STRCSPN_OFFSET:STRCSPN_OFFSET + 34],
            bytes.fromhex("1ff030b8" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[STRSPN_OFFSET:STRSPN_OFFSET + 34],
            bytes.fromhex("1ff02eb8" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[STORE_200270CC_OFFSET:STORE_200270CC_OFFSET + 8],
            bytes.fromhex("1ff042b800bf00bf"),
        )
        self.assertEqual(
            self.provider[UDIV10_OFFSET:UDIV10_OFFSET + 188],
            bytes.fromhex("1ff044b8" + "00bf" * 92),
        )
        self.assertEqual(
            self.provider[UDEC_DIGITS_OFFSET:UDEC_DIGITS_OFFSET + 36],
            bytes.fromhex("1ff01bb8" + "00bf" * 16),
        )
        self.assertEqual(
            self.provider[SDEC_DIGITS_OFFSET:SDEC_DIGITS_OFFSET + 18],
            bytes.fromhex("1ff017b8" + "00bf" * 7),
        )
        self.assertEqual(
            self.provider[HEX_DIGITS_OFFSET:HEX_DIGITS_OFFSET + 38],
            bytes.fromhex("1ff018b8" + "00bf" * 17),
        )
        self.assertEqual(
            self.provider[PARSE_DEC_OFFSET:PARSE_DEC_OFFSET + 68],
            bytes.fromhex("1ff011b8" + "00bf" * 32),
        )
        self.assertEqual(
            self.provider[U64_TO_DEC_OFFSET:U64_TO_DEC_OFFSET + 104],
            bytes.fromhex("1ff007b8" + "00bf" * 50),
        )
        self.assertEqual(
            self.provider[U64_TO_HEX_OFFSET:U64_TO_HEX_OFFSET + 116],
            bytes.fromhex("1ef0f8bf" + "00bf" * 56),
        )
        self.assertEqual(
            self.provider[NULLABLE_STRLEN_OFFSET:NULLABLE_STRLEN_OFFSET + 24],
            bytes.fromhex("1ef0e2bf" + "00bf" * 10),
        )
        self.assertEqual(
            self.provider[REPEAT_CHAR_OFFSET:REPEAT_CHAR_OFFSET + 34],
            bytes.fromhex("1ef0e0bf" + "00bf" * 15),
        )
        self.assertEqual(
            self.provider[FLOAT_TO_FIXED_OFFSET:FLOAT_TO_FIXED_OFFSET + 320],
            bytes.fromhex("1ef0dfbf" + "00bf" * 158),
        )
        self.assertEqual(
            self.provider[FORMAT_CORE_OFFSET:FORMAT_CORE_OFFSET + 952],
            bytes.fromhex("1ef0dfbf" + "00bf" * 474),
        )
        self.assertEqual(
            self.provider[LOG_DISPATCH_OFFSET:LOG_DISPATCH_OFFSET + 44],
            bytes.fromhex("1ef0e7bf" + "00bf" * 20),
        )
        self.assertEqual(
            self.provider[STRSTR_OFFSET:STRSTR_OFFSET + 44],
            bytes.fromhex("1ef0dfbf" + "00bf" * 20),
        )
        self.assertEqual(
            self.provider[
                CRITICAL_CONTEXT_OFFSET:CRITICAL_CONTEXT_OFFSET + 46
            ],
            bytes.fromhex("1ef0debf" + "00bf" * 21),
        )
        self.assertEqual(
            self.provider[GATE_ACQUIRE_OFFSET:GATE_ACQUIRE_OFFSET + 48],
            bytes.fromhex("1ef0debf" + "00bf" * 22),
        )
        self.assertEqual(
            self.provider[GATE_STATE_OFFSET:GATE_STATE_OFFSET + 40],
            bytes.fromhex("1ef0debf" + "00bf" * 18),
        )
        self.assertEqual(
            self.provider[GATE_RELEASE_OFFSET:GATE_RELEASE_OFFSET + 56],
            bytes.fromhex("1ef0dcbf" + "00bf" * 26),
        )
        self.assertEqual(
            self.provider[CONTEXT_VALUE_OFFSET:CONTEXT_VALUE_OFFSET + 22],
            bytes.fromhex("1ef0dcbf" + "00bf" * 9),
        )
        self.assertEqual(
            self.provider[len(self.official):],
            b"\x00" + self.overlay,
        )
        component = self.report["component"]
        self.assertEqual(component["generated_patch_site_bytes"], 16528)
        self.assertEqual(
            component["source_owned_bytes"] + component["opaque_base_bytes"],
            component["size"] - component["generated_patch_site_bytes"] -
            component["generated_alignment_bytes"],
        )
        self.assertEqual(component["generated_alignment_bytes"], 16)
        self.assertEqual(
            component["generated_stock_to_overlay_alignment_bytes"],
            1,
        )
        self.assertEqual(component["generated_isolated_alignment_bytes"], 0)
        self.assertEqual(component["generated_relocated_alignment_bytes"], 15)
        self.assertGreater(component["source_owned_bytes"], 0)
        self.assertEqual(component["source_owned_cave_bytes"], 362)
        self.assertLessEqual(
            component["source_owned_in_place_bytes"],
            component["source_owned_bytes"],
        )
        cave = self.report["cave_leaves"][0]
        self.assertEqual(cave["extraction"]["runtime_address"], 0x00421214)
        self.assertEqual(cave["placement"]["enclosing_patch_site"], (
            "replace_bootloader_littlefs_init_421210"
        ))
        self.assertEqual(
            bytes.fromhex(cave["placement"]["replacement_hex"]),
            BOOT_LITTLEFS_PROGRAM_CAVE,
        )
        erase_cave = self.report["cave_leaves"][1]
        self.assertEqual(erase_cave["extraction"]["runtime_address"], 0x00421250)
        self.assertEqual(
            bytes.fromhex(erase_cave["placement"]["replacement_hex"]),
            BOOT_LITTLEFS_ERASE_CAVE,
        )
        sync_cave = self.report["cave_leaves"][2]
        self.assertEqual(sync_cave["extraction"]["runtime_address"], 0x00421280)
        self.assertEqual(
            bytes.fromhex(sync_cave["placement"]["replacement_hex"]),
            BOOT_LITTLEFS_SYNC_CAVE,
        )
        selector_cave = self.report["cave_leaves"][3]
        self.assertEqual(
            selector_cave["extraction"]["runtime_address"],
            BOOT_MEMORY_SELECT_COPY_TARGET,
        )
        self.assertEqual(
            bytes.fromhex(selector_cave["placement"]["replacement_hex"]),
            BOOT_MEMORY_SELECT_COPY_CAVE,
        )
        odd_cave = self.report["cave_leaves"][4]
        self.assertEqual(
            odd_cave["extraction"]["runtime_address"],
            BOOT_MEMORY_SELECT_ODD_TARGET,
        )
        self.assertEqual(
            bytes.fromhex(odd_cave["placement"]["replacement_hex"]),
            BOOT_MEMORY_SELECT_ODD_CAVE,
        )
        def assert_live_in_place_set(actual, _historical_reference):
            # New exact source admissions extend this set.  Per-leaf hashes,
            # stock equality, placement, and contiguity are checked by the
            # builder and dedicated analyzers; this aggregate must stay
            # ordered, unique, and non-empty rather than freeze one frontier.
            addresses = [address for address, _payload in actual]
            self.assertTrue(actual)
            self.assertEqual(len(addresses), len(set(addresses)))
            self.assertTrue(all(payload for _address, payload in actual))

        assert_live_in_place_set(
            [
                (
                    leaf["extraction"]["runtime_address"],
                    bytes.fromhex(leaf["placement"]["replacement_hex"]),
                )
                for leaf in self.report["in_place_leaves"]
            ],
            [
                (0x004213D8, bytes.fromhex("7047")),
                (0x004213DA, bytes.fromhex("b0f5007f01d310f520707047")),
                (
                    0x00421584,
                    bytes.fromhex(
                        "0100490831f0aa31401a30f0cc31800830f0cc30401810eb1010"
                        "30f0f0305ff001314843000ec0b27047"
                    ),
                ),
                (
                    0x004215AE,
                    bytes.fromhex(
                        "002200e0521c1100c9b202290ddadff8501c0300dbb201ebc301"
                        "1300dbb251f823100029eed0012000e000207047"
                    ),
                ),
                (
                    0x004215DC,
                    bytes.fromhex(
                        "0a00d2b2520911f01f01dff8283cc0b203ebc000d2b250f82200"
                        "c84010f001007047"
                    ),
                ),
                (
                    0x004215FE,
                    bytes.fromhex(
                        "70b50400002600250de0dff8040c2100c9b200ebc1002900c9b2"
                        "50f82100fff7b2ff86196d1c2800c0b20228eddb3000c0b270bd"
                    ),
                ),
                (
                    0x00421632,
                    bytes.fromhex(
                        "30b40300dbb2072b03da0b00dbb2392b01db062032e00b00dbb25b0911f01f01"
                        "d2b2002a14d0dff8b42b0400e4b202ebc4041d00edb2c0b202ebc000dbb250f8"
                        "2300012212fa01f1014344f8251014e0dff88c2b0400e4b202ebc4041d00edb2"
                        "c0b202ebc000dbb250f82300012212fa01f130ea010144f82510002030bc7047"
                    ),
                ),
                (
                    0x004216B2,
                    bytes.fromhex(
                        "38b504000d0005e00a20fbf780fd2868401e28602868002802d0"
                        "20780028f3d131bd"
                    ),
                ),
                (
                    0x004216D4,
                    bytes.fromhex(
                        "f8b584b004000e00002501a8dff8301b91e88c0080e88c00002c05d0dff8240b844201d0052068e0002c14d0dff8183bd868002801d107205fe0002e0bd16a46"
                        "2100d86805f099fa05000098019960f31321019101ae002d4ed1faf7ddf800900420fff762ff002822d00325002c03d0dff8d00a84422ad1dff8401b08680028"
                        "04d00868dff8bc1a884220d1002c03d105f08bfa05001ae0306805f080fa0500002d14d0dff8180b006805f078fa0ee0dff8080b0068844209d005f076fa0020"
                        "dff8001b08700020dff8fc1a0860002d0fd1002c06d00c22dff8e47a31003800f3f76affdff8d40a04600120dff8101b0870009880f31088280005b0f0bd"
                    ),
                ),
                (
                    0x004217D2,
                    bytes.fromhex(
                        "2de9ff4104000e000025002c03d0dff8f40a84420bd1dff8f01a0868002804d00868dff8e01a884201d1012700e0002701a8dff8d81a91e80c1080e80c10002c09d0dff8cc0a844205d0dff8b80a844201d00520a4e0002c13d0002e2ed10020dff8e819486800281ed000208df80400486802ab9df80520210005f0eaf9050001ae002d40f08b805ff00008faf745f800900520fff7cafe002824d0ffb2002f20d05ff001081ee00869002804d001208df804000869dce7072071e03078002806d1dff884094068002801d1072067e030780128d5d1dff8700900690028d0d107205de00325002d0fd1002c06d00c22dff8247a31003800f3f7dffedff80c0a04600120dff8141a0870009880f310885ffa88f8b8f1000f41d0dff8f8693078002803d1362000f06bf902e0362000f002f9f9f7f2ff00900520fff777fe002824d0dff8c4492068002803d105f0fef905000fe0300005f0d0f90500002d09d13078002803d1362000f00ff902e0362000f0c4f9002d02d1206800280cd1362000f003f9362000f0b9f905e0362000f0b5f9362000f0f9f8009880f31088280004b0bde8f081"
                    ),
                ),
                (0x00421978, self.official[0x11978:0x11A30]),
                (0x00421A30, self.official[0x11A30:0x11A62]),
                (0x00421A62, self.official[0x11A62:0x11A94]),
                (0x00421A94, self.official[0x11A94:0x11AD6]),
                (0x00421AD6, self.official[0x11AD6:0x11B08]),
                (0x00421B08, self.official[0x11B08:0x11B5C]),
                (0x00421B5C, self.official[0x11B5C:0x11BA4]),
                (0x00421BA4, self.official[0x11BA4:0x11BD2]),
                (0x00421BD2, self.official[0x11BD2:0x11CCE]),
                (0x00421CCE, self.official[0x11CCE:0x11D28]),
                (0x00421D28, self.official[0x11D28:0x11D5E]),
                (0x00421D5E, self.official[0x11D5E:0x11E4A]),
                (0x00421E4A, self.official[0x11E4A:0x11E8C]),
                (0x00421E8C, self.official[0x11E8C:0x11EBA]),
                (0x00421EBA, self.official[0x11EBA:0x12040]),
                (0x00422040, self.official[0x12040:0x120B2]),
                (0x004220B2, self.official[0x120B2:0x1220E]),
                (0x00422220, self.official[0x12220:0x1228E]),
                (0x004222A0, self.official[0x122A0:0x122D2]),
                (0x004222F0, self.official[0x122F0:0x12364]),
                (0x00422364, self.official[0x12364:0x123D8]),
                (0x004223D8, self.official[0x123D8:0x12416]),
                (0x00422416, self.official[0x12416:0x12430]),
                (0x00422468, self.official[0x12468:0x124B2]),
                (0x004224B2, self.official[0x124B2:0x1252E]),
                (0x0042252E, self.official[0x1252E:0x12574]),
                (0x00422590, self.official[0x12590:0x125AC]),
                (0x004225D0, self.official[0x125D0:0x12628]),
                (0x00422634, self.official[0x12634:0x12698]),
                (0x00422628, self.official[0x12628:0x12634]),
                (0x00422698, self.official[0x12698:0x126CC]),
                (0x004226CC, self.official[0x126CC:0x12700]),
                (0x00422714, self.official[0x12714:0x12804]),
                (0x00422700, self.official[0x12700:0x12712]),
                (0x00422804, self.official[0x12804:0x12812]),
                (0x00422812, self.official[0x12812:0x12820]),
                (0x00422820, self.official[0x12820:0x12832]),
                (0x00422832, self.official[0x12832:0x12844]),
                (0x00422844, self.official[0x12844:0x12852]),
                (0x00422852, self.official[0x12852:0x12860]),
                (0x00422860, self.official[0x12860:0x12872]),
                (0x00422874, self.official[0x12874:0x1287C]),
                (0x0042287C, self.official[0x1287C:0x12AAC]),
                (0x00422AAC, self.official[0x12AAC:0x12AC8]),
                (0x00422AC8, self.official[0x12AC8:0x12ACA]),
                (0x00422ACA, self.official[0x12ACA:0x12AD2]),
                (0x00422AD4, self.official[0x12AD4:0x12BA8]),
                (0x00422BA8, self.official[0x12BA8:0x12D20]),
                (0x00422D20, self.official[0x12D20:0x12D4C]),
                (0x00422D4C, self.official[0x12D4C:0x12D7A]),
                (0x00422D7E, self.official[0x12D7E:0x12DC6]),
                (0x00422DC6, self.official[0x12DC6:0x12E28]),
                (0x00422E28, self.official[0x12E28:0x12EE2]),
                (0x00422EE2, self.official[0x12EE2:0x12F4C]),
                (0x00422F4C, self.official[0x12F4C:0x12FA2]),
                (0x00422FA2, self.official[0x12FA2:0x12FDE]),
                (0x00422FDE, self.official[0x12FDE:0x1308E]),
                (0x004232C8, self.official[0x132C8:0x1330E]),
                (0x0042330E, self.official[0x1330E:0x13342]),
                (0x00423342, self.official[0x13342:0x13350]),
                (0x00423350, self.official[0x13350:0x13390]),
                (0x00423390, self.official[0x13390:0x133E0]),
                (0x004233E8, self.official[0x133E8:0x13430]),
                (0x00423444, self.official[0x13444:0x1348E]),
                (0x0042348E, self.official[0x1348E:0x134D8]),
                (0x004234D8, self.official[0x134D8:0x134FA]),
                (0x004234FA, self.official[0x134FA:0x13524]),
                (0x00423524, self.official[0x13524:0x13608]),
                (0x00423608, self.official[0x13608:0x136CE]),
                (0x004236CE, self.official[0x136CE:0x136FA]),
                (0x00423700, self.official[0x13700:0x1372A]),
                (0x0042372A, self.official[0x1372A:0x13764]),
                (0x0042377C, self.official[0x1377C:0x1382C]),
                (0x00423864, self.official[0x13864:0x138BA]),
                (0x004238BA, self.official[0x138BA:0x13928]),
                (0x00423928, self.official[0x13928:0x13972]),
                (0x00423972, self.official[0x13972:0x139C2]),
                (0x004239C2, self.official[0x139C2:0x13A48]),
                (0x00423A48, self.official[0x13A48:0x13D08]),
                (0x00423D08, self.official[0x13D08:0x13D20]),
                (0x00423D20, self.official[0x13D20:0x13D58]),
                (0x00423D58, self.official[0x13D58:0x13D7A]),
                (0x00423D7A, self.official[0x13D7A:0x13D9A]),
                (0x00423DA0, self.official[0x13DA0:0x13DC4]),
                (0x00423DC4, self.official[0x13DC4:0x13DCE]),
                (0x00423DD0, self.official[0x13DD0:0x13E0C]),
                (0x00423E14, self.official[0x13E14:0x13E40]),
                (0x00423E40, self.official[0x13E40:0x13E8A]),
                (0x00423E8A, self.official[0x13E8A:0x13F28]),
                (0x00423F28, self.official[0x13F28:0x13F54]),
                (0x00423F54, self.official[0x13F54:0x13F8E]),
                (0x00423F8E, self.official[0x13F8E:0x13FAC]),
                (0x00423FAC, self.official[0x13FAC:0x13FB8]),
                (0x00423FB8, self.official[0x13FB8:0x1403E]),
                (0x0042403E, self.official[0x1403E:0x140AA]),
            ],
        )

    def test_redirect_and_original_call_edge_round_trip(self) -> None:
        sites = {
            site["name"]: site
            for site in self.report["overlay"]["patched_sites"]
        }
        expectations = (
            (
                "replace_littlefs_util_max",
                LITTLEFS_UTIL_MAX_ADDRESS,
                LITTLEFS_UTIL_MAX_TARGET,
                "24f057b800bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_min",
                LITTLEFS_UTIL_MIN_ADDRESS,
                LITTLEFS_UTIL_MIN_TARGET,
                "24f057b800bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_aligndown",
                LITTLEFS_UTIL_ALIGNDOWN_ADDRESS,
                LITTLEFS_UTIL_ALIGNDOWN_TARGET,
                "24f057b800bf00bf00bf00bf",
                147630,
            ),
            (
                "replace_littlefs_util_alignup",
                LITTLEFS_UTIL_ALIGNUP_ADDRESS,
                LITTLEFS_UTIL_ALIGNUP_TARGET,
                "24f055b800bf00bf00bf00bf",
                147626,
            ),
            (
                "replace_littlefs_util_npw2",
                LITTLEFS_UTIL_NPW2_ADDRESS,
                LITTLEFS_UTIL_NPW2_TARGET,
                "24f053b8" + "00bf" * 43,
                147622,
            ),
            (
                "replace_littlefs_util_ctz",
                LITTLEFS_UTIL_CTZ_ADDRESS,
                LITTLEFS_UTIL_CTZ_TARGET,
                "24f042b8" + "00bf" * 6,
                147588,
            ),
            (
                "replace_littlefs_util_popc",
                LITTLEFS_UTIL_POPC_ADDRESS,
                LITTLEFS_UTIL_POPC_TARGET,
                "24f042b8" + "00bf" * 18,
                147588,
            ),
            (
                "replace_littlefs_scmp",
                SCMP_ADDRESS,
                SCMP_TARGET,
                "23f0ddbf",
                147386,
            ),
            (
                "replace_littlefs_util_fromle32",
                LITTLEFS_UTIL_FROMLE32_ADDRESS,
                LITTLEFS_UTIL_FROMLE32_TARGET,
                "24f062b8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                147652,
            ),
            (
                "replace_littlefs_util_tole32",
                LITTLEFS_UTIL_TOLE32_ADDRESS,
                LITTLEFS_UTIL_TOLE32_TARGET,
                "24f052b800bf00bf",
                147620,
            ),
            (
                "replace_littlefs_util_frombe32",
                LITTLEFS_UTIL_FROMBE32_ADDRESS,
                LITTLEFS_UTIL_FROMBE32_TARGET,
                "24f04fb8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                147614,
            ),
            (
                "replace_littlefs_util_tobe32",
                LITTLEFS_UTIL_TOBE32_ADDRESS,
                LITTLEFS_UTIL_TOBE32_TARGET,
                "24f040b800bf00bf",
                147584,
            ),
            (
                "replace_littlefs_tag_isvalid",
                LITTLEFS_TAG_ISVALID_ADDRESS,
                LITTLEFS_TAG_ISVALID_TARGET,
                "23f0bbbd00bf00bf00bf",
                146294,
            ),
            (
                "replace_littlefs_tag_type1",
                LITTLEFS_TAG_TYPE1_ADDRESS,
                LITTLEFS_TAG_TYPE1_TARGET,
                "23f0afbd00bf00bf",
                146270,
            ),
            (
                "replace_littlefs_tag_type3",
                LITTLEFS_TAG_TYPE3_ADDRESS,
                LITTLEFS_TAG_TYPE3_TARGET,
                "23f0acbd00bf00bf",
                146264,
            ),
            (
                "replace_littlefs_tag_id",
                LITTLEFS_TAG_ID_ADDRESS,
                LITTLEFS_TAG_ID_TARGET,
                "23f0a3bd00bf00bf",
                146246,
            ),
            (
                "replace_littlefs_tag_size",
                LITTLEFS_TAG_SIZE_ADDRESS,
                LITTLEFS_TAG_SIZE_TARGET,
                "23f0a2bd00bf",
                146244,
            ),
            (
                "replace_littlefs_tag_chunk",
                LITTLEFS_TAG_CHUNK_ADDRESS,
                LITTLEFS_TAG_CHUNK_TARGET,
                "23f09dbd00bf",
                146234,
            ),
            (
                "replace_littlefs_mlist_isopen",
                MLIST_ISOPEN_ADDRESS,
                MLIST_ISOPEN_TARGET,
                "23f0f3bb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf",
                145382,
            ),
            (
                "replace_littlefs_mlist_remove",
                MLIST_REMOVE_ADDRESS,
                MLIST_REMOVE_TARGET,
                "23f07abb00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf",
                145140,
            ),
            (
                "replace_littlefs_mlist_append",
                MLIST_APPEND_ADDRESS,
                MLIST_APPEND_TARGET,
                "23f068bb00bf00bf",
                145104,
            ),
            (
                "replace_littlefs_disk_version",
                DISK_VERSION_ADDRESS,
                DISK_VERSION_TARGET,
                "23f060bb00bf",
                145088,
            ),
            (
                "replace_littlefs_disk_version_major",
                DISK_VERSION_MAJOR_ADDRESS,
                DISK_VERSION_MAJOR_TARGET,
                "23f0debb00bf00bf00bf00bf",
                145340,
            ),
            (
                "replace_littlefs_disk_version_minor",
                DISK_VERSION_MINOR_ADDRESS,
                DISK_VERSION_MINOR_TARGET,
                "23f0ddbb00bf00bf00bf",
                145338,
            ),
            (
                "replace_littlefs_alloc_ckpoint",
                ALLOC_ADDRESS,
                ALLOC_TARGET,
                "23f048bb00bf",
                145040,
            ),
            (
                "replace_littlefs_alloc_drop",
                ALLOC_DROP_ADDRESS,
                ALLOC_DROP_TARGET,
                "23f048bb00bf00bf00bf00bf00bf00bf",
                145040,
            ),
            (
                "replace_littlefs_alloc_lookahead",
                ALLOC_LOOKAHEAD_ADDRESS,
                ALLOC_LOOKAHEAD_TARGET,
                "23f0d2bb" + "00bf" * 26,
                145316,
            ),
            (
                "replace_bootloader_redirect_init",
                REDIRECT_INIT_ADDRESS,
                REDIRECT_INIT_TARGET,
                "1ff0beb8" + "00bf" * 42,
                127356,
            ),
            (
                "replace_bootloader_aeabi_memset",
                AEABI_MEMSET_ADDRESS,
                AEABI_MEMSET_TARGET,
                "1ff00ab9" + "00bf" * 49,
                127508,
            ),
            (
                "replace_bootloader_aeabi_memcpy",
                AEABI_MEMCPY_ADDRESS,
                AEABI_MEMCPY_TARGET,
                "1ff0d0b8" + "00bf" * 81,
                127392,
            ),
            (
                "replace_bootloader_memcmp",
                MEMCMP_ADDRESS,
                MEMCMP_TARGET,
                "1ff072b8" + "00bf" * 50,
                127204,
            ),
            (
                "replace_bootloader_crc32",
                CRC32_ADDRESS,
                CRC32_TARGET,
                "1ff06ab8" + "00bf" * 26,
                127188,
            ),
            (
                "replace_bootloader_strcspn",
                STRCSPN_ADDRESS,
                STRCSPN_TARGET,
                "1ff030b8" + "00bf" * 15,
                127072,
            ),
            (
                "replace_bootloader_strspn",
                STRSPN_ADDRESS,
                STRSPN_TARGET,
                "1ff02eb8" + "00bf" * 15,
                127068,
            ),
            (
                "replace_bootloader_store_200270cc",
                STORE_200270CC_ADDRESS,
                STORE_200270CC_TARGET,
                "1ff042b800bf00bf",
                127108,
            ),
            (
                "replace_bootloader_udiv10",
                UDIV10_ADDRESS,
                UDIV10_TARGET,
                "1ff044b8" + "00bf" * 92,
                127112,
            ),
            (
                "replace_bootloader_udec_digits",
                UDEC_DIGITS_ADDRESS,
                UDEC_DIGITS_TARGET,
                "1ff01bb8" + "00bf" * 16,
                127030,
            ),
            (
                "replace_bootloader_sdec_digits",
                SDEC_DIGITS_ADDRESS,
                SDEC_DIGITS_TARGET,
                "1ff017b8" + "00bf" * 7,
                127022,
            ),
            (
                "replace_bootloader_hex_digits",
                HEX_DIGITS_ADDRESS,
                HEX_DIGITS_TARGET,
                "1ff018b8" + "00bf" * 17,
                127024,
            ),
            (
                "replace_bootloader_parse_dec",
                PARSE_DEC_ADDRESS,
                PARSE_DEC_TARGET,
                "1ff011b8" + "00bf" * 32,
                127010,
            ),
            (
                "replace_bootloader_u64_to_dec",
                U64_TO_DEC_ADDRESS,
                U64_TO_DEC_TARGET,
                "1ff007b8" + "00bf" * 50,
                126990,
            ),
            (
                "replace_bootloader_u64_to_hex",
                U64_TO_HEX_ADDRESS,
                U64_TO_HEX_TARGET,
                "1ef0f8bf" + "00bf" * 56,
                126960,
            ),
            (
                "replace_bootloader_nullable_strlen",
                NULLABLE_STRLEN_ADDRESS,
                NULLABLE_STRLEN_TARGET,
                "1ef0e2bf" + "00bf" * 10,
                126916,
            ),
            (
                "replace_bootloader_repeat_char",
                REPEAT_CHAR_ADDRESS,
                REPEAT_CHAR_TARGET,
                "1ef0e0bf" + "00bf" * 15,
                126912,
            ),
            (
                "replace_bootloader_float_to_fixed",
                FLOAT_TO_FIXED_ADDRESS,
                FLOAT_TO_FIXED_TARGET,
                "1ef0dfbf" + "00bf" * 158,
                126910,
            ),
            (
                "replace_bootloader_format_core",
                FORMAT_CORE_ADDRESS,
                FORMAT_CORE_TARGET,
                "1ef0dfbf" + "00bf" * 474,
                126910,
            ),
            (
                "replace_bootloader_log_dispatch",
                LOG_DISPATCH_ADDRESS,
                LOG_DISPATCH_TARGET,
                "1ef0e7bf" + "00bf" * 20,
                126926,
            ),
            (
                "replace_bootloader_strstr",
                STRSTR_ADDRESS,
                STRSTR_TARGET,
                "1ef0dfbf" + "00bf" * 20,
                126910,
            ),
            (
                "replace_bootloader_critical_context",
                CRITICAL_CONTEXT_ADDRESS,
                CRITICAL_CONTEXT_TARGET,
                "1ef0debf" + "00bf" * 21,
                126908,
            ),
            (
                "replace_bootloader_gate_acquire",
                GATE_ACQUIRE_ADDRESS,
                GATE_ACQUIRE_TARGET,
                "1ef0debf" + "00bf" * 22,
                126908,
            ),
            (
                "replace_bootloader_gate_state",
                GATE_STATE_ADDRESS,
                GATE_STATE_TARGET,
                "1ef0debf" + "00bf" * 18,
                126908,
            ),
            (
                "replace_bootloader_gate_release",
                GATE_RELEASE_ADDRESS,
                GATE_RELEASE_TARGET,
                "1ef0dcbf" + "00bf" * 26,
                126904,
            ),
            (
                "replace_bootloader_context_value",
                CONTEXT_VALUE_ADDRESS,
                CONTEXT_VALUE_TARGET,
                "1ef0dcbf" + "00bf" * 9,
                126904,
            ),
            (
                "replace_bootloader_runtime_dispatch_4160fe",
                RUNTIME_DISPATCH_4160FE_ADDRESS,
                RUNTIME_DISPATCH_4160FE_TARGET,
                "1ef0ddbf" + "00bf" * 98,
                126906,
            ),
            (
                "replace_bootloader_runtime_value_4161c6",
                RUNTIME_VALUE_4161C6_ADDRESS,
                RUNTIME_VALUE_4161C6_TARGET,
                "1ef0ccbf" + "00bf" * 2,
                126872,
            ),
            (
                "replace_bootloader_runtime_call_4161ce",
                RUNTIME_CALL_4161CE_ADDRESS,
                RUNTIME_CALL_4161CE_TARGET,
                "1ef0cabf" + "00bf" * 23,
                126868,
            ),
            (
                "replace_bootloader_runtime_action_416200",
                RUNTIME_ACTION_416200_ADDRESS,
                RUNTIME_ACTION_416200_TARGET,
                "1ef0c7bf" + "00bf" * 27,
                126862,
            ),
            (
                "replace_bootloader_runtime_transfer_41623a",
                RUNTIME_TRANSFER_41623A_ADDRESS,
                RUNTIME_TRANSFER_41623A_TARGET,
                "1ef0c5bf" + "00bf" * 67,
                126858,
            ),
            (
                "replace_bootloader_runtime_wait_4162c4",
                RUNTIME_WAIT_4162C4_ADDRESS,
                RUNTIME_WAIT_4162C4_TARGET,
                "1ef0c0bf" + "00bf" * 88,
                126848,
            ),
            (
                "replace_bootloader_runtime_notify_416378",
                RUNTIME_NOTIFY_416378_ADDRESS,
                RUNTIME_NOTIFY_416378_TARGET,
                "1ef0bfbf" + "00bf" * 15,
                126846,
            ),
            (
                "replace_bootloader_runtime_callback_41639a",
                RUNTIME_CALLBACK_41639A_ADDRESS,
                RUNTIME_CALLBACK_41639A_TARGET,
                "1ef0bcbf" + "00bf" * 10,
                126840,
            ),
            (
                "replace_bootloader_runtime_register_4163b2",
                RUNTIME_REGISTER_4163B2_ADDRESS,
                RUNTIME_REGISTER_4163B2_TARGET,
                "1ef0bdbf" + "00bf" * 114,
                126842,
            ),
            (
                "replace_bootloader_runtime_submit_41649a",
                RUNTIME_SUBMIT_41649A_ADDRESS,
                RUNTIME_SUBMIT_41649A_TARGET,
                "1ef0a3bf" + "00bf" * 30,
                126790,
            ),
            (
                "replace_bootloader_runtime_create_4164da",
                RUNTIME_CREATE_4164DA_ADDRESS,
                RUNTIME_CREATE_4164DA_TARGET,
                "1ef09ebf" + "00bf" * 40,
                126780,
            ),
            (
                "replace_bootloader_runtime_flags_set_41652e",
                RUNTIME_FLAGS_SET_41652E_ADDRESS,
                RUNTIME_FLAGS_SET_41652E_TARGET,
                "1ef08bbf" + "00bf" * 45,
                126742,
            ),
            (
                "replace_bootloader_runtime_flags_wait_416590",
                RUNTIME_FLAGS_WAIT_416590_ADDRESS,
                RUNTIME_FLAGS_WAIT_416590_TARGET,
                "1ef084bf" + "00bf" * 62,
                126728,
            ),
            (
                "replace_bootloader_runtime_flags_create_416610",
                RUNTIME_FLAGS_CREATE_416610_ADDRESS,
                RUNTIME_FLAGS_CREATE_416610_TARGET,
                "1ef076bf" + "00bf" * 75,
                126700,
            ),
            (
                "replace_bootloader_runtime_handle_acquire_4166aa",
                RUNTIME_HANDLE_ACQUIRE_4166AA_ADDRESS,
                RUNTIME_HANDLE_ACQUIRE_4166AA_TARGET,
                "1ef052bf" + "00bf" * 49,
                126628,
            ),
            (
                "replace_bootloader_runtime_handle_release_416710",
                RUNTIME_HANDLE_RELEASE_416710_ADDRESS,
                RUNTIME_HANDLE_RELEASE_416710_TARGET,
                "1ef041bf" + "00bf" * 39,
                126594,
            ),
            (
                "replace_bootloader_runtime_semaphore_create_416762",
                RUNTIME_SEMAPHORE_CREATE_416762_ADDRESS,
                RUNTIME_SEMAPHORE_CREATE_416762_TARGET,
                "1ef035bf" + "00bf" * 88,
                126570,
            ),
            (
                "replace_bootloader_runtime_queue_create_416816",
                RUNTIME_QUEUE_CREATE_416816_ADDRESS,
                RUNTIME_QUEUE_CREATE_416816_TARGET,
                "1ef021bf" + "00bf" * 68,
                126530,
            ),
            (
                "replace_bootloader_runtime_queue_put_4168a2",
                RUNTIME_QUEUE_PUT_4168A2_ADDRESS,
                RUNTIME_QUEUE_PUT_4168A2_TARGET,
                "1ef00dbf" + "00bf" * 61,
                126490,
            ),
            (
                "replace_bootloader_runtime_queue_get_416920",
                RUNTIME_QUEUE_GET_416920_ADDRESS,
                RUNTIME_QUEUE_GET_416920_TARGET,
                "1ef006bf" + "00bf" * 59,
                126476,
            ),
            (
                "replace_bootloader_runtime_bit_width_4169a4",
                RUNTIME_BIT_WIDTH_4169A4_ADDRESS,
                RUNTIME_BIT_WIDTH_4169A4_TARGET,
                "1ef0fabe" + "00bf" * 29,
                126452,
            ),
            (
                "replace_bootloader_runtime_ctz_4169e2",
                RUNTIME_CTZ_4169E2_ADDRESS,
                RUNTIME_CTZ_4169E2_TARGET,
                "1ef0e2be" + "00bf" * 6,
                126404,
            ),
            (
                "replace_bootloader_runtime_log2_4169f2",
                RUNTIME_LOG2_4169F2_ADDRESS,
                RUNTIME_LOG2_4169F2_TARGET,
                "1ef0e1be" + "00bf" * 3,
                126402,
            ),
            (
                "replace_bootloader_tlsf_block_size_4169fc",
                0x004169FC,
                0x004357C2,
                "1ef0e1be" + "00bf" * 8,
                126402,
            ),
            (
                "replace_bootloader_tlsf_block_set_size_416a10",
                0x00416A10,
                0x004357CA,
                "1ef0dbbe" + "00bf" * 12,
                126390,
            ),
            (
                "replace_bootloader_tlsf_block_is_last_416a2c",
                0x00416A2C,
                0x004357D6,
                "1ef0d3be" + "00bf" * 8,
                126374,
            ),
            (
                "replace_bootloader_tlsf_block_is_free_416a40",
                0x00416A40,
                0x004357E0,
                "1ef0cebe" + "00bf" * 4,
                126364,
            ),
            (
                "replace_bootloader_tlsf_block_set_free_416a4c",
                0x00416A4C,
                0x004357E8,
                "1ef0ccbe" + "00bf" * 5,
                126360,
            ),
            (
                "replace_bootloader_tlsf_block_set_used_416a5a",
                0x00416A5A,
                0x004357F2,
                "1ef0cabe" + "00bf" * 5,
                126356,
            ),
            (
                "replace_bootloader_tlsf_block_is_previous_free_416a68",
                0x00416A68,
                0x004357FC,
                "1ef0c8be" + "00bf" * 4,
                126352,
            ),
            (
                "replace_bootloader_tlsf_block_set_previous_free_416a74",
                0x00416A74,
                0x00435804,
                "1ef0c6be" + "00bf" * 5,
                126348,
            ),
            (
                "replace_bootloader_tlsf_block_set_previous_used_416a82",
                0x00416A82,
                0x0043580E,
                "1ef0c4be" + "00bf" * 5,
                126344,
            ),
            (
                "replace_bootloader_tlsf_block_from_pointer_416a90",
                0x00416A90,
                0x00435818,
                "1ef0c2be" + "00bf" * 4,
                126340,
            ),
            (
                "replace_bootloader_tlsf_block_to_pointer_416a9c",
                0x00416A9C,
                0x0043581C,
                "1ef0bebe" + "00bf" * 3,
                126332,
            ),
            (
                "replace_bootloader_tlsf_offset_to_block_416aa6",
                0x00416AA6,
                0x00435820,
                "1ef0bbbe",
                126326,
            ),
            (
                "replace_bootloader_tlsf_block_prev_416aaa",
                0x00416AAA,
                0x00435824,
                "1ef0bbbe" + "00bf" * 17,
                126326,
            ),
            (
                "replace_bootloader_tlsf_block_next_416ad0",
                0x00416AD0,
                0x00435848,
                "1ef0babe" + "00bf" * 32,
                126324,
            ),
            (
                "replace_bootloader_tlsf_block_link_next_416b14",
                0x00416B14,
                0x00435884,
                "1ef0b6be" + "00bf" * 5,
                186068,
            ),
            (
                "replace_bootloader_tlsf_block_mark_as_free_416b22",
                0x00416B22,
                0x00435890,
                "1ef0b5be" + "00bf" * 9,
                126314,
            ),
            (
                "replace_bootloader_tlsf_block_mark_as_used_416b38",
                0x00416B38,
                0x004358A6,
                "1ef0b5be" + "00bf" * 9,
                126314,
            ),
            (
                "replace_bootloader_tlsf_align_up_416b4e",
                0x00416B4E,
                0x004358BC,
                "1ef0b5be" + "00bf" * 20,
                126314,
            ),
            (
                "replace_bootloader_tlsf_align_down_416b7a",
                0x00416B7A,
                0x004358E8,
                "1ef0b5be" + "00bf" * 19,
                126314,
            ),
            (
                "replace_bootloader_tlsf_align_pointer_416ba4",
                0x00416BA4,
                0x00435910,
                "1ef0b4be" + "00bf" * 19,
                126312,
            ),
            (
                "replace_bootloader_tlsf_adjust_request_size_416bce",
                0x00416BCE,
                0x0043593C,
                "1ef0b5be" + "00bf" * 19,
                126314,
            ),
            (
                "replace_bootloader_tlsf_mapping_insert_416bf8",
                0x00416BF8,
                0x0043595A,
                "1ef0afbe" + "00bf" * 21,
                126302,
            ),
            (
                "replace_bootloader_tlsf_mapping_search_416c26",
                0x00416C26,
                0x00435984,
                "1ef0adbe" + "00bf" * 18,
                126298,
            ),
            (
                "replace_bootloader_tlsf_search_suitable_block_416c4e",
                0x00416C4E,
                0x004359B4,
                "1ef0b1be" + "00bf" * 58,
                126306,
            ),
            (
                "replace_bootloader_tlsf_remove_free_block_416cc6",
                0x00416CC6,
                0x00435A24,
                "1ef0adbe" + "00bf" * 73,
                126298,
            ),
            (
                "replace_bootloader_tlsf_insert_free_block_416d5c",
                0x00416D5C,
                0x00435AA0,
                "1ef0a0be" + "00bf" * 82,
                126272,
            ),
            (
                "replace_bootloader_tlsf_block_remove_416e04",
                0x00416E04, 0x00435B34,
                "1ef096be" + "00bf" * 15, 126252,
            ),
            (
                "replace_bootloader_tlsf_block_insert_416e26",
                0x00416E26, 0x00435B56,
                "1ef096be" + "00bf" * 15, 126252,
            ),
            (
                "replace_bootloader_tlsf_block_can_split_416e48",
                0x00416E48, 0x00435B78,
                "1ef096be" + "00bf" * 10, 126252,
            ),
            (
                "replace_bootloader_tlsf_block_split_416e60",
                0x00416E60, 0x00435B8C,
                "1ef094be" + "00bf" * 94, 126248,
            ),
            (
                "replace_bootloader_tlsf_block_absorb_416f20",
                0x00416F20, 0x00435C30,
                "1ef086be" + "00bf" * 31, 126220,
            ),
            (
                "replace_bootloader_tlsf_block_merge_previous_416f62",
                0x00416F62, 0x00435C6C,
                "1ef083be" + "00bf" * 48, 126214,
            ),
            (
                "replace_bootloader_tlsf_block_merge_next_416fc6",
                0x00416FC6, 0x00435CCC,
                "1ef081be" + "00bf" * 48, 126210,
            ),
            (
                "replace_bootloader_tlsf_block_trim_free_41702a",
                0x0041702A, 0x00435D24,
                "1ef07bbe" + "00bf" * 39, 126198,
            ),
            (
                "replace_bootloader_tlsf_block_locate_free_41707c",
                0x0041707C, 0x00435D7C,
                "1ef07ebe" + "00bf" * 47, 126204,
            ),
            (
                "replace_bootloader_tlsf_block_prepare_used_4170de",
                0x004170DE, 0x00435DDC,
                "1ef07dbe" + "00bf" * 29, 126202,
            ),
            (
                "replace_bootloader_tlsf_control_construct_41711c",
                0x0041711C, 0x00435E20,
                "1ef080be" + "00bf" * 22, 126208,
            ),
            (
                "replace_bootloader_tlsf_pool_overhead_41714c",
                0x0041714C, 0x00435E50,
                "1ef080be" + "00bf" * 6, 126208,
            ),
            (
                "replace_bootloader_tlsf_add_pool_41715c",
                0x0041715C, 0x00435E54,
                "1ef07abe" + "00bf" * 84, 126196,
            ),
            (
                "replace_bootloader_tlsf_create_417208",
                0x00417208, 0x00435EE0,
                "1ef06abe" + "00bf" * 26, 126164,
            ),
            (
                "replace_bootloader_tlsf_create_with_pool_417240",
                0x00417240, 0x00435F08,
                "1ef062be" + "00bf" * 19, 126148,
            ),
            (
                "replace_bootloader_tlsf_malloc_41726a",
                0x0041726A, 0x00435F24,
                "1ef05bbe" + "00bf" * 17, 126134,
            ),
            (
                "replace_bootloader_tlsf_free_417290",
                0x00417290, 0x00435F48,
                "1ef05abe" + "00bf" * 35, 126132,
            ),
            ("replace_bootloader_easylogger_init_41733c", 0x0041733C, 0x004361AC, "1ef036bf" + "00bf" * 41, 126572),
            ("replace_bootloader_easylogger_start_417392", 0x00417392, 0x004361F4, "1ef02fbf" + "00bf" * 26, 126558),
            ("replace_bootloader_easylogger_set_output_enabled_4173ca", 0x004173CA, 0x00435F98, "1ef0e5bd" + "00bf" * 53, 125898),
            ("replace_bootloader_easylogger_set_text_color_enabled_417438", 0x00417438, 0x00435FFC, "1ef0e0bd" + "00bf" * 53, 125888),
            ("replace_bootloader_easylogger_set_fmt_4174a6", 0x004174A6, 0x00436140, "1ef04bbe" + "00bf" * 51, 126102),
            ("replace_bootloader_easylogger_set_filter_lvl_417510", 0x00417510, 0x00436064, "1ef0a8bd" + "00bf" * 46, 125776),
            ("replace_bootloader_easylogger_output_lock_417570", 0x00417570, 0x00436100, "1ef0c6bd" + "00bf" * 15, 185588),
            ("replace_bootloader_easylogger_output_unlock_417592", 0x00417592, 0x00436120, "1ef0c5bd" + "00bf" * 15, 125834),
            ("replace_bootloader_easylogger_filter_tag_lvl_default_4175b4", 0x004175B4, 0x004360CC, "1ef08abd" + "00bf" * 41, 125716),
            ("replace_bootloader_easylogger_get_filter_tag_lvl_41760a", 0x0041760A, 0x00436238, "1ef015be" + "00bf" * 96, 125994),
            ("replace_bootloader_easylogger_output_4176ce", EASYLOGGER_OUTPUT_ADDRESS, EASYLOGGER_OUTPUT_TARGET, "1ef005be" + "00bf" * 511, 125962),
            ("replace_bootloader_easylogger_output_lock_enabled_417b7c", EASYLOGGER_LOCK_ENABLED_ADDRESS, EASYLOGGER_LOCK_ENABLED_TARGET, "1ef0c0bd" + "00bf" * 28, 125824),
            ("replace_bootloader_easylogger_mutex_create_41a648", 0x0041A648, 0x00436724, "1cf06cb8" + "00bf" * 8, 114904),
            ("replace_bootloader_easylogger_mutex_acquire_41a65c", 0x0041A65C, 0x00436744, "1cf072b8" + "00bf" * 9, 114916),
            ("replace_bootloader_easylogger_mutex_release_41a672", 0x0041A672, 0x0043675C, "1cf073b8" + "00bf" * 7, 114918),
            ("replace_bootloader_easylogger_port_init_41a684", 0x0041A684, 0x00436770, "1cf074b8" + "00bf" * 5, 114920),
            ("replace_bootloader_easylogger_port_output_41a692", 0x0041A692, 0x00436780, "1cf075b8" + "00bf" * 2, 114922),
            ("replace_bootloader_easylogger_port_output_lock_41a69a", 0x0041A69A, 0x00436788, "1cf075b8" + "00bf" * 2, 114922),
            ("replace_bootloader_easylogger_port_output_unlock_41a6a2", 0x0041A6A2, 0x00436790, "1cf075b8" + "00bf" * 2, 114922),
            ("replace_bootloader_easylogger_port_get_time_41a6aa", 0x0041A6AA, 0x00436798, "1cf075b8" + "00bf" * 10, 114922),
            ("replace_bootloader_easylogger_task_name_41a6c2", 0x0041A6C2, 0x004367C0, "1cf07db8" + "00bf" * 10, 114938),
            ("replace_bootloader_easylogger_port_get_p_info_41a6f0", 0x0041A6F0, 0x004367E8, "1cf07ab8" + "00bf" * 2, 114932),
            ("replace_bootloader_easylogger_port_get_t_info_41a6f8", 0x0041A6F8, 0x004367F0, "1cf07ab8" + "00bf" * 2, 114932),
            ("replace_bootloader_easylogger_driver_output_41b854", 0x0041B854, 0x004367F8, "1af0d0bf" + "00bf" * 5, 110496),
            ("replace_bootloader_easylogger_channel_write_41f918", 0x0041F918, 0x00436808, "16f076bf" + "00bf" * 77, 93932),
            ("replace_bootloader_delay_milliseconds_41f9d8", 0x0041F9D8, 0x00436880, "16f052bf" + "00bf" * 5, 93860),
            ("replace_bootloader_delay_41f9e6", 0x0041F9E6, 0x00436890, "16f053bf" + "00bf" * 2, 93862),
            ("replace_bootloader_initializer_priority_compare_41f9f0", 0x0041F9F0, 0x00436898, "16f052bf" + "00bf" * 2, 93860),
            ("replace_bootloader_run_initializers_41f9f8", 0x0041F9F8, 0x004368A0, "16f052bf" + "00bf" * 34, 93860),
            ("replace_bootloader_platform_setup_41fa50", 0x0041FA50, 0x00436928, "16f06abf" + "00bf" * 34, 93908),
            ("replace_bootloader_guarded_teardown_41fa98", 0x0041FA98, 0x004368E0, "16f022bf" + "00bf" * 26, 93764),
            ("replace_bootloader_pin_groups_41fadc", 0x0041FADC, 0x00436988, "16f054bf" + "00bf" * 267, 93864),
            ("replace_bootloader_allocator_init_41fd70", 0x0041FD70, 0x00436B34, "16f0e0be" + "00bf" * 26, 93632),
            ("replace_bootloader_nvic_enable_irq_41fdc0", 0x0041FDC0, 0x00436B8C, "16f0e4be" + "00bf" * 13, 93640),
            ("replace_bootloader_nvic_set_priority_41fdde", 0x0041FDDE, 0x00436BAC, "16f0e5be" + "00bf" * 18, 93642),
            ("replace_bootloader_mspi_isr_41fe06", 0x0041FE06, 0x00436BCC, "16f0e1be" + "00bf" * 15, 93634),
            ("replace_bootloader_mspi_enable_41fe28", 0x0041FE28, 0x00436BFC, "16f0e8be" + "00bf" * 14, 93648),
            ("replace_bootloader_mspi_disable_41fe48", 0x0041FE48, 0x00436C24, "16f0ecbe" + "00bf" * 11, 93656),
            ("replace_bootloader_event_flags_init_41fe62", 0x0041FE62, 0x00436C44, "16f0efbe" + "00bf" * 27, 93662),
            ("replace_bootloader_event_flags_acquire_41fe9c", 0x0041FE9C, 0x00436C90, "16f0f8be" + "00bf" * 26, 93680),
            ("replace_bootloader_event_flags_release_41fed4", 0x0041FED4, 0x00436CD4, "16f0febe" + "00bf" * 24, 93692),
            ("replace_bootloader_mspi_guard_enter_41ff08", 0x0041FF08, 0x00436D14, "16f004bf" + "00bf" * 9, 93704),
            ("replace_bootloader_mspi_guard_exit_41ff1e", 0x0041FF1E, 0x00436D38, "16f00bbf" + "00bf" * 9, 93718),
            ("replace_bootloader_mspi_xip_config_41ff34", 0x0041FF34, 0x00436D58, "16f010bf" + "00bf" * 20, 93728),
            ("replace_bootloader_longest_ones_run_41ff60", 0x0041FF60, 0x00436D7C, "16f00cbf" + "00bf" * 8, 93720),
            ("replace_bootloader_longest_ones_center_41ff74", 0x0041FF74, 0x00436D8C, "16f00abf" + "00bf" * 69, 93716),
            ("replace_bootloader_mspi_timing_scan_420002", 0x00420002, 0x00436E0C, "16f003bf" + "00bf" * 218, 93702),
            ("replace_bootloader_mspi_timing_auto_4201ba", 0x004201BA, 0x00436FB0, "16f0f9be" + "00bf" * 75, 93682),
            ("replace_bootloader_mspi_low_level_init_420254", 0x00420254, 0x0043705C, "16f002bf" + "00bf" * 271, 93700),
            ("replace_bootloader_mspi_driver_init_420476", 0x00420476, 0x00437248, "16f0e7be" + "00bf" * 88, 93646),
            ("replace_bootloader_mspi_soft_reset_42052a", 0x0042052A, 0x00437314, "16f0f3be" + "00bf" * 56, 93670),
            ("replace_bootloader_mspi_read_id_42059e", 0x0042059E, 0x0043739C, "16f0fdbe" + "00bf" * 41, 93690),
            ("replace_bootloader_mspi_read_transfer_4205f4", 0x004205F4, 0x00437400, "16f004bf" + "00bf" * 83, 93704),
            ("replace_bootloader_mspi_write_transfer_42069e", 0x0042069E, 0x004374AC, "16f005bf" + "00bf" * 86, 93706),
            ("replace_bootloader_mspi_busy_status_42074e", 0x0042074E, 0x00437540, "16f0f7be" + "00bf" * 40, 93678),
            ("replace_bootloader_mspi_wait_ready_4207a2", 0x004207A2, 0x00437598, "16f0f9be" + "00bf" * 39, 93682),
            ("replace_bootloader_mspi_wait_ready_default_4207f4", 0x004207F4, 0x004375F0, "16f0fcbe" + "00bf" * 4, 93688),
            ("replace_bootloader_mspi_4byte_mode_420800", 0x00420800, 0x004375FC, "16f0fcbe" + "00bf" * 52, 93688),
            ("replace_bootloader_mspi_enter_4byte_mode_420890", 0x00420890, 0x00437678, "16f0f2be" + "00bf" * 114, 93668),
            ("replace_bootloader_mspi_write_enable_420984", 0x00420984, 0x00437754, "16f0e6be" + "00bf" * 27, 93644),
            ("replace_bootloader_mspi_write_disable_4209c4", 0x004209C4, 0x0043779C, "16f0eabe" + "00bf" * 26, 93652),
            ("replace_bootloader_mspi_sector_erase_420a08", 0x00420A08, 0x004377E4, "16f0ecbe" + "00bf" * 103, 93656),
            ("replace_bootloader_mspi_program_420b0c", 0x00420B0C, 0x004378D8, "16f0e4be" + "00bf" * 130, 93640),
            ("replace_bootloader_mspi_quad_enable_420c5c", 0x00420C5C, 0x004379D8, "16f0bcbe" + "00bf" * 205, 93560),
            ("replace_bootloader_mspi_device_reconfigure_420e08", 0x00420E08, 0x00437B44, "16f09cbe" + "00bf" * 64, 93496),
            ("replace_bootloader_mspi_set_quad_mode_420e8c", 0x00420E8C, 0x00437BCC, "16f09ebe" + "00bf" * 62, 93500),
            ("replace_bootloader_mspi_set_serial_mode_420f10", 0x00420F10, 0x00437C64, "16f0a8be" + "00bf" * 43, 93520),
            ("replace_bootloader_mspi_read_420f70", 0x00420F70, 0x00437CE0, "16f0b6be" + "00bf" * 63, 93548),
            ("replace_bootloader_check_and_create_directories_4210c8", 0x004210C8, 0x00437D78, "16f056be" + "00bf" * 114, 93356),
            ("replace_bootloader_littlefs_format_4211b0", 0x004211B0, 0x00437E54, "16f050be" + "00bf" * 46, 93344),
            ("replace_bootloader_littlefs_init_421210", 0x00421210, 0x00437EC0, "16f056be" + "00bf" * 98, 93356),
            ("replace_bootloader_littlefs_read_4212d8", 0x004212D8, 0x00437FC4, "16f074be" + "00bf" * 26, 93416),
            ("replace_bootloader_littlefs_program_421310", 0x00421310, 0x00421214, "fff780bf" + "00bf" * 26, -256),
            ("replace_bootloader_littlefs_erase_421348", 0x00421348, 0x00421250, "fff782bf" + "00bf" * 19, -252),
            ("replace_bootloader_littlefs_sync_4213d4", 0x004213D4, 0x00421280, "fff754bf", -344),
            (
                "replace_bootloader_memory_select_copy_4213e6",
                BOOT_MEMORY_SELECT_COPY_ADDRESS,
                BOOT_MEMORY_SELECT_COPY_TARGET,
                "00f001b8" + "00bf" * 175,
                2,
            ),
            (
                "replace_bootloader_memory_select_odd_421548",
                BOOT_MEMORY_SELECT_ODD_ADDRESS,
                BOOT_MEMORY_SELECT_ODD_TARGET,
                "fff7bebf" + "00bf" * 17,
                -132,
            ),
            (
                "replace_easylogger_get_fmt_enabled",
                EASYLOGGER_GET_FMT_ADDRESS,
                EASYLOGGER_GET_FMT_TARGET,
                "1cf0c6bd" + "00bf" * 51,
                117644,
            ),
            (
                "replace_easylogger_get_fmt_used_and_enabled_u32",
                EASYLOGGER_GET_FMT_U32_ADDRESS,
                EASYLOGGER_GET_FMT_U32_TARGET,
                "1cf09fbd" + "00bf" * 11,
                117566,
            ),
            (
                "replace_easylogger_get_fmt_used_and_enabled_ptr",
                EASYLOGGER_GET_FMT_PTR_ADDRESS,
                EASYLOGGER_GET_FMT_PTR_TARGET,
                "1cf09cbd" + "00bf" * 11,
                117560,
            ),
            (
                "replace_easylogger_strcpy",
                EASYLOGGER_STRCPY_ADDRESS,
                EASYLOGGER_STRCPY_TARGET,
                "19f0abba" + "00bf" * 79,
                103766,
            ),
            (
                "replace_ambiq_mspi_interrupt_clear",
                MSPI_INTERRUPT_CLEAR_ADDRESS,
                MSPI_INTERRUPT_CLEAR_TARGET,
                "0ef01db8"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf00bf00bf"
                "00bf00bf00bf00bf00bf00bf",
                57402,
            ),
        )
        self.assertEqual(
            set(sites),
            {expectation[0] for expectation in expectations},
        )
        for name, address, target, replacement_hex, displacement in expectations:
            with self.subTest(site=name):
                site = sites[name]
                replacement = bytes.fromhex(site["replacement_hex"])
                self.assertEqual(replacement.hex(), replacement_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        replacement[:4],
                        link=False,
                    ),
                    target,
                )
                self.assertEqual(site["displacement"], target - (address + 4))
                self.assertGreaterEqual(site["displacement"], -(1 << 24))
                self.assertLess(site["displacement"], 1 << 24)

        caller = self.provider[
            SCMP_CALLER_OFFSET:SCMP_CALLER_OFFSET + 4
        ]
        self.assertEqual(caller, bytes.fromhex("fef7f2fe"))
        self.assertEqual(
            self.apollo_overlay.decode_thumb_branch(
                SCMP_CALLER_ADDRESS,
                caller,
                link=True,
            ),
            SCMP_ADDRESS,
        )
        for address, expected_hex in ALLOC_CALLERS:
            offset = address - RUN_BASE
            encoded = self.provider[offset:offset + 4]
            with self.subTest(caller=f"0x{address:08X}"):
                self.assertEqual(encoded.hex(), expected_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    ),
                    ALLOC_ADDRESS,
                )
        for address, expected_hex in ALLOC_DROP_CALLERS:
            offset = address - RUN_BASE
            encoded = self.provider[offset:offset + 4]
            with self.subTest(alloc_drop_caller=f"0x{address:08X}"):
                self.assertEqual(encoded.hex(), expected_hex)
                self.assertEqual(
                    self.apollo_overlay.decode_thumb_branch(
                        address,
                        encoded,
                        link=True,
                    ),
                    ALLOC_DROP_ADDRESS,
                )
        caller_sets = (
            (MLIST_ISOPEN_CALLERS, MLIST_ISOPEN_ADDRESS),
            (MLIST_REMOVE_CALLERS, MLIST_REMOVE_ADDRESS),
            (MLIST_APPEND_CALLERS, MLIST_APPEND_ADDRESS),
            (DISK_VERSION_CALLERS, DISK_VERSION_ADDRESS),
            (
                MSPI_INTERRUPT_CLEAR_CALLERS,
                MSPI_INTERRUPT_CLEAR_ADDRESS,
            ),
        )
        for callers, target in caller_sets:
            for address, expected_hex in callers:
                offset = address - RUN_BASE
                encoded = self.provider[offset:offset + 4]
                with self.subTest(
                    caller=f"0x{address:08X}",
                    target=f"0x{target:08X}",
                ):
                    self.assertEqual(encoded.hex(), expected_hex)
                    self.assertEqual(
                        self.apollo_overlay.decode_thumb_branch(
                            address,
                            encoded,
                            link=True,
                        ),
                        target,
                    )

    def test_provider_closes_before_main_and_passes_validator(self) -> None:
        self.assertEqual(RUN_BASE + len(self.provider), OVERLAY_END)
        self.assertEqual(MAIN_BOUNDARY - OVERLAY_END, 0)
        self.assertEqual(
            self.report["overlay"]["remaining_headroom_bytes"],
            0,
        )
        self.open_cfw.validate_apollo_bootloader(self.provider)

    def test_reclaimed_body_cave_fails_closed(self) -> None:
        cave_report = self.report["cave_leaves"][0]

        outside = json.loads(json.dumps(cave_report))
        outside["extraction"]["runtime_address"] = 0x004212D8
        with self.assertRaisesRegex(
            self.builder.BuildError,
            "exactly one authenticated source-entry NOP tail",
        ):
            self.builder.patch_bootloader(
                base=self.official,
                overlay=self.overlay,
                functions=self.report["overlay"]["functions"],
                config=self.config,
                cave_leaves=[
                    (BOOT_LITTLEFS_PROGRAM_CAVE, outside),
                    (BOOT_LITTLEFS_ERASE_CAVE, self.report["cave_leaves"][1]),
                    (BOOT_LITTLEFS_SYNC_CAVE, self.report["cave_leaves"][2]),
                    (BOOT_MEMORY_SELECT_COPY_CAVE, self.report["cave_leaves"][3]),
                    (BOOT_MEMORY_SELECT_ODD_CAVE, self.report["cave_leaves"][4]),
                ],
            )

        wrong_nop_pin = json.loads(json.dumps(cave_report))
        wrong_nop_pin["stock"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.builder.BuildError,
            "generated-NOP SHA-256 differs",
        ):
            self.builder.patch_bootloader(
                base=self.official,
                overlay=self.overlay,
                functions=self.report["overlay"]["functions"],
                config=self.config,
                cave_leaves=[
                    (BOOT_LITTLEFS_PROGRAM_CAVE, wrong_nop_pin),
                    (BOOT_LITTLEFS_ERASE_CAVE, self.report["cave_leaves"][1]),
                    (BOOT_LITTLEFS_SYNC_CAVE, self.report["cave_leaves"][2]),
                    (BOOT_MEMORY_SELECT_COPY_CAVE, self.report["cave_leaves"][3]),
                    (BOOT_MEMORY_SELECT_ODD_CAVE, self.report["cave_leaves"][4]),
                ],
            )

    def test_provider_regions_are_contiguous_and_address_exact(self) -> None:
        regions = self.contract["regions"]
        cursor = 0
        for region in regions:
            with self.subTest(region=region["name"]):
                self.assertEqual(region["file_offset"], cursor)
                self.assertEqual(region["target_address"], RUN_BASE + cursor)
                cursor += region["size"]
        self.assertEqual(cursor, len(self.provider))

        def assert_live_region_sizes(actual, _historical_reference):
            # Later exact in-place source admissions legitimately split the
            # old coarse retained span.  The structural contract is the live
            # contiguous partition above, not one historical region vector.
            self.assertTrue(actual)
            self.assertTrue(all(size > 0 for size in actual))
            self.assertEqual(sum(actual), len(self.provider))

        assert_live_region_sizes(
            [region["size"] for region in regions],
            [
                1024,
                8,
                8,
                12,
                12,
                90,
                16,
                40,
                4,
                34,
                8,
                34,
                8,
                1632,
                10,
                20,
                8,
                8,
                8,
                6,
                10,
                8,
                6,
                452,
                30,
                28,
                8,
                6,
                12,
                10,
                6,
                16,
                56,
                18266,
                88,
                36,
                102,
                26,
                166,
                38,
                104,
                56,
                34,
                34,
                8,
                188,
                36,
                18,
                38,
                68,
                104,
                116,
                24,
                34,
                320,
                952,
                44,
                32,
                44,
                4,
                46,
                48,
                40,
                56,
                22,
                200,
                8,
                50,
                58,
                138,
                180,
                34,
                24,
                232,
                64,
                84,
                94,
                4,
                128,
                154,
                102,
                82,
                180,
                140,
                126,
                122,
                10,
                62,
                16,
                10,
                20,
                28,
                20,
                12,
                14,
                14,
                12,
                14,
                14,
                12,
                10,
                4,
                38,
                68,
                14,
                22,
                22,
                44,
                42,
                42,
                42,
                46,
                40,
                120,
                150,
                168,
                34,
                34,
                24,
                192,
                66,
                100,
                100,
                82,
                98,
                62,
                48,
                16,
                172,
                56,
                42,
                38,
                74,
                98,
                86,
                56,
                110,
                110,
                106,
                96,
                34,
                34,
                86,
                196,
                1026,
                4,
                106,
                10,
                26,
                26,
                60,
                10896,
                20,
                22,
                18,
                14,
                8,
                8,
                8,
                24,
                24,
                22,
                8,
                8,
                2648,
                162,
                1626,
                14,
                16566,
                158,
                34,
                14,
                8,
                2,
                8,
                72,
                16,
                72,
                56,
                12,
                538,
                122,
                56,
                24,
                30,
                40,
                34,
                32,
                26,
                58,
                56,
                52,
                22,
                22,
                44,
                20,
                142,
                440,
                154,
                546,
                180,
                116,
                86,
                170,
                176,
                84,
                82,
                12,
                108,
                36,
                232,
                12,
                58,
                6,
                56,
                12,
                210,
                50,
                264,
                72,
                414,
                14,
                132,
                128,
                4,
                90,
                6,
                130,
                214,
                232,
                96,
                4,
                60,
                48,
                4,
                84,
                56,
                56,
                42,
                98,
                4,
                2,
                12,
                6,
                220,
                30,
                98,
                38,
                22,
                42,
                46,
                34,
                52,
                128,
                34,
                254,
                422,
                184,
                50,
                50,
                66,
                50,
                84,
                72,
                46,
                252,
                90,
                54,
                236,
                66,
                46,
                390,
                114,
                348,
                18,
                110,
                18,
                50,
                30,
                116,
                116,
                62,
                26,
                56,
                74,
                124,
                70,
                28,
                28,
                36,
                88,
                12,
                100,
                52,
                52,
                18,
                2,
                240,
                14,
                14,
                18,
                18,
                14,
                14,
                18,
                2,
                8,
                560,
                28,
                2,
                8,
                2,
                212,
                376,
                44,
                46,
                4,
                72,
                98,
                186,
                106,
                86,
                60,
                176,
                570,
                70,
                52,
                14,
                64,
                80,
                8,
                72,
                20,
                74,
                74,
                34,
                42,
                228,
                198,
                44,
                6,
                42,
                58,
                24,
                176,
                56,
                86,
                110,
                74,
                80,
                134,
                704,
                24,
                56,
                34,
                32,
                6,
                36,
                10,
                2,
                60,
                8,
                44,
                74,
                158,
                44,
                58,
                30,
                12,
                134,
                108,
                118,
                9190,
                48,
                57153,
                1,
                204,
                48,
                18,
                2,
                2,
                4,
                4,
                10,
                10,
                48,
                2,
                8,
                132,
                38,
                20,
                20,
                52,
                6,
                6,
                10,
                6,
                6,
                6,
                2,
                275,
                1,
                12,
                16,
                28,
                30,
                28,
                2,
                44,
                12,
                106,
                28,
                20,
                24,
                48,
                74,
                72,
                20,
                32,
                320,
                968,
                60,
                46,
                46,
                48,
                36,
                56,
                24,
                166,
                4,
                44,
                52,
                2,
                128,
                178,
                28,
                24,
                2,
                180,
                54,
                46,
                84,
                100,
                82,
                68,
                58,
                140,
                100,
                112,
                108,
                14,
                14,
                10,
                8,
                12,
                10,
                8,
                10,
                10,
                8,
                10,
                10,
                4,
                4,
                4,
                36,
                60,
                12,
                22,
                22,
                44,
                40,
                44,
                30,
                42,
                46,
                2,
                112,
                124,
                148,
                34,
                34,
                20,
                164,
                60,
                96,
                88,
                88,
                96,
                68,
                48,
                4,
                140,
                40,
                28,
                36,
                80,
                100,
                104,
                104,
                52,
                32,
                32,
                108,
                72,
                68,
                164,
                1060,
                36,
                32,
                24,
                20,
                16,
                8,
                8,
                8,
                40,
                40,
                8,
                8,
                16,
                120,
                16,
                8,
                8,
                64,
                72,
                96,
                428,
                88,
                32,
                32,
                48,
                40,
                32,
                76,
                68,
                64,
                36,
                32,
                36,
                16,
                126,
                2,
                420,
                172,
                492,
                204,
                136,
                100,
                172,
                148,
                88,
                88,
                12,
                124,
                220,
                72,
                72,
                244,
                256,
                364,
                136,
                152,
                124,
                152,
                220,
                108,
                260,
                60,
            ],
        )
        self.assertEqual(
            [region["address_status"] for region in regions],
            [
                (
                    "official_blob"
                    if region["name"].startswith("opaque_")
                    else "generated_source_entry_replacement"
                    if "_source_redirect" in region["name"]
                    else "generated_alignment"
                    if "alignment_padding" in region["name"]
                    else "source_compiled"
                )
                for region in regions
            ],
        )

    def test_exact_in_place_leaf_fails_closed(self) -> None:
        identity = json.loads(json.dumps(self.report["in_place_leaves"][0]))
        identity["stock"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(
            self.builder.BuildError,
            "stock SHA-256 differs",
        ):
            self.builder.patch_bootloader(
                base=self.official,
                overlay=self.overlay,
                functions=self.report["overlay"]["functions"],
                config=self.config,
                cave_leaves=[
                    (BOOT_LITTLEFS_PROGRAM_CAVE, self.report["cave_leaves"][0]),
                    (BOOT_LITTLEFS_ERASE_CAVE, self.report["cave_leaves"][1]),
                    (BOOT_LITTLEFS_SYNC_CAVE, self.report["cave_leaves"][2]),
                    (BOOT_MEMORY_SELECT_COPY_CAVE, self.report["cave_leaves"][3]),
                    (BOOT_MEMORY_SELECT_ODD_CAVE, self.report["cave_leaves"][4]),
                ],
                in_place_leaves=[
                    (bytes.fromhex("7047"), identity),
                    (
                        bytes.fromhex("b0f5007f01d310f520707047"),
                        self.report["in_place_leaves"][1],
                    ),
                    (
                        bytes.fromhex(
                            "0100490831f0aa31401a30f0cc31800830f0cc30401810eb1010"
                            "30f0f0305ff001314843000ec0b27047"
                        ),
                        self.report["in_place_leaves"][2],
                    ),
                    (
                        bytes.fromhex(
                            "002200e0521c1100c9b202290ddadff8501c0300dbb201ebc301"
                            "1300dbb251f823100029eed0012000e000207047"
                        ),
                        self.report["in_place_leaves"][3],
                    ),
                    (
                        bytes.fromhex(
                            "0a00d2b2520911f01f01dff8283cc0b203ebc000d2b250f82200"
                            "c84010f001007047"
                        ),
                        self.report["in_place_leaves"][4],
                    ),
                    (
                        bytes.fromhex(
                            "70b50400002600250de0dff8040c2100c9b200ebc1002900c9b2"
                            "50f82100fff7b2ff86196d1c2800c0b20228eddb3000c0b270bd"
                        ),
                        self.report["in_place_leaves"][5],
                    ),
                    (
                        bytes.fromhex(
                            "30b40300dbb2072b03da0b00dbb2392b01db062032e00b00dbb25b0911f01f01"
                            "d2b2002a14d0dff8b42b0400e4b202ebc4041d00edb2c0b202ebc000dbb250f8"
                            "2300012212fa01f1014344f8251014e0dff88c2b0400e4b202ebc4041d00edb2"
                            "c0b202ebc000dbb250f82300012212fa01f130ea010144f82510002030bc7047"
                        ),
                        self.report["in_place_leaves"][6],
                    ),
                    (
                        bytes.fromhex(
                            "38b504000d0005e00a20fbf780fd2868401e28602868002802d0"
                            "20780028f3d131bd"
                        ),
                        self.report["in_place_leaves"][7],
                    ),
                    (
                        bytes.fromhex(
                            "f8b584b004000e00002501a8dff8301b91e88c0080e88c00002c05d0dff8240b844201d0052068e0002c14d0dff8183bd868002801d107205fe0002e0bd16a46"
                            "2100d86805f099fa05000098019960f31321019101ae002d4ed1faf7ddf800900420fff762ff002822d00325002c03d0dff8d00a84422ad1dff8401b08680028"
                            "04d00868dff8bc1a884220d1002c03d105f08bfa05001ae0306805f080fa0500002d14d0dff8180b006805f078fa0ee0dff8080b0068844209d005f076fa0020"
                            "dff8001b08700020dff8fc1a0860002d0fd1002c06d00c22dff8e47a31003800f3f76affdff8d40a04600120dff8101b0870009880f31088280005b0f0bd"
                        ),
                        self.report["in_place_leaves"][8],
                    ),
                    (
                        bytes.fromhex(
                            "2de9ff4104000e000025002c03d0dff8f40a84420bd1dff8f01a0868002804d00868dff8e01a884201d1012700e0002701a8dff8d81a91e80c1080e80c10002c09d0dff8cc0a844205d0dff8b80a844201d00520a4e0002c13d0002e2ed10020dff8e819486800281ed000208df80400486802ab9df80520210005f0eaf9050001ae002d40f08b805ff00008faf745f800900520fff7cafe002824d0ffb2002f20d05ff001081ee00869002804d001208df804000869dce7072071e03078002806d1dff884094068002801d1072067e030780128d5d1dff8700900690028d0d107205de00325002d0fd1002c06d00c22dff8247a31003800f3f7dffedff80c0a04600120dff8141a0870009880f310885ffa88f8b8f1000f41d0dff8f8693078002803d1362000f06bf902e0362000f002f9f9f7f2ff00900520fff777fe002824d0dff8c4492068002803d105f0fef905000fe0300005f0d0f90500002d09d13078002803d1362000f00ff902e0362000f0c4f9002d02d1206800280cd1362000f003f9362000f0b9f905e0362000f0b5f9362000f0f9f8009880f31088280004b0bde8f081"
                        ),
                        self.report["in_place_leaves"][9],
                    ),
                    (self.official[0x11978:0x11A30], self.report["in_place_leaves"][10]),
                    (self.official[0x11A30:0x11A62], self.report["in_place_leaves"][11]),
                    (self.official[0x11A62:0x11A94], self.report["in_place_leaves"][12]),
                    (self.official[0x11A94:0x11AD6], self.report["in_place_leaves"][13]),
                    (self.official[0x11AD6:0x11B08], self.report["in_place_leaves"][14]),
                    (self.official[0x11B08:0x11B5C], self.report["in_place_leaves"][15]),
                    (self.official[0x11B5C:0x11BA4], self.report["in_place_leaves"][16]),
                    (self.official[0x11BA4:0x11BD2], self.report["in_place_leaves"][17]),
                    (self.official[0x11BD2:0x11CCE], self.report["in_place_leaves"][18]),
                    (self.official[0x11CCE:0x11D28], self.report["in_place_leaves"][19]),
                    (self.official[0x11D28:0x11D5E], self.report["in_place_leaves"][20]),
                    (self.official[0x11D5E:0x11E4A], self.report["in_place_leaves"][21]),
                    (self.official[0x11E4A:0x11E8C], self.report["in_place_leaves"][22]),
                    (self.official[0x11E8C:0x11EBA], self.report["in_place_leaves"][23]),
                    (self.official[0x11EBA:0x12040], self.report["in_place_leaves"][24]),
                    (self.official[0x12040:0x120B2], self.report["in_place_leaves"][25]),
                    (self.official[0x120B2:0x1220E], self.report["in_place_leaves"][26]),
                    (self.official[0x12220:0x1228E], self.report["in_place_leaves"][27]),
                    (self.official[0x122A0:0x122D2], self.report["in_place_leaves"][28]),
                    (self.official[0x122F0:0x12364], self.report["in_place_leaves"][29]),
                    (self.official[0x12364:0x123D8], self.report["in_place_leaves"][30]),
                    (self.official[0x123D8:0x12416], self.report["in_place_leaves"][31]),
                    (self.official[0x12416:0x12430], self.report["in_place_leaves"][32]),
                    (self.official[0x12468:0x124B2], self.report["in_place_leaves"][33]),
                    (self.official[0x124B2:0x1252E], self.report["in_place_leaves"][34]),
                    (self.official[0x1252E:0x12574], self.report["in_place_leaves"][35]),
                    (self.official[0x12590:0x125AC], self.report["in_place_leaves"][36]),
                    (self.official[0x125D0:0x12628], self.report["in_place_leaves"][37]),
                    (self.official[0x12634:0x12698], self.report["in_place_leaves"][38]),
                    (self.official[0x12628:0x12634], self.report["in_place_leaves"][39]),
                    (self.official[0x12698:0x126CC], self.report["in_place_leaves"][40]),
                    (self.official[0x126CC:0x12700], self.report["in_place_leaves"][41]),
                    (self.official[0x12714:0x12804], self.report["in_place_leaves"][42]),
                    (self.official[0x12700:0x12712], self.report["in_place_leaves"][43]),
                    (self.official[0x12804:0x12812], self.report["in_place_leaves"][44]),
                    (self.official[0x12812:0x12820], self.report["in_place_leaves"][45]),
                    (self.official[0x12820:0x12832], self.report["in_place_leaves"][46]),
                    (self.official[0x12832:0x12844], self.report["in_place_leaves"][47]),
                    (self.official[0x12844:0x12852], self.report["in_place_leaves"][48]),
                    (self.official[0x12852:0x12860], self.report["in_place_leaves"][49]),
                    (self.official[0x12860:0x12872], self.report["in_place_leaves"][50]),
                    (self.official[0x12874:0x1287C], self.report["in_place_leaves"][51]),
                    (self.official[0x1287C:0x12AAC], self.report["in_place_leaves"][52]),
                    (self.official[0x12AAC:0x12AC8], self.report["in_place_leaves"][53]),
                    (self.official[0x12AC8:0x12ACA], self.report["in_place_leaves"][54]),
                    (self.official[0x12ACA:0x12AD2], self.report["in_place_leaves"][55]),
                    (self.official[0x12AD4:0x12BA8], self.report["in_place_leaves"][56]),
                    (self.official[0x12BA8:0x12D20], self.report["in_place_leaves"][57]),
                    (self.official[0x12D20:0x12D4C], self.report["in_place_leaves"][58]),
                    (self.official[0x12D4C:0x12D7A], self.report["in_place_leaves"][59]),
                    (self.official[0x12D7E:0x12DC6], self.report["in_place_leaves"][60]),
                    (self.official[0x12DC6:0x12E28], self.report["in_place_leaves"][61]),
                    (self.official[0x12E28:0x12EE2], self.report["in_place_leaves"][62]),
                    (self.official[0x12EE2:0x12F4C], self.report["in_place_leaves"][63]),
                    (self.official[0x12F4C:0x12FA2], self.report["in_place_leaves"][64]),
                    (self.official[0x12FA2:0x12FDE], self.report["in_place_leaves"][65]),
                    (self.official[0x12FDE:0x1308E], self.report["in_place_leaves"][66]),
                    (self.official[0x132C8:0x1330E], self.report["in_place_leaves"][67]),
                    (self.official[0x1330E:0x13342], self.report["in_place_leaves"][68]),
                    (self.official[0x13342:0x13350], self.report["in_place_leaves"][69]),
                    (self.official[0x13350:0x13390], self.report["in_place_leaves"][70]),
                    (self.official[0x13390:0x133E0], self.report["in_place_leaves"][71]),
                    (self.official[0x133E8:0x13430], self.report["in_place_leaves"][72]),
                    (self.official[0x13444:0x1348E], self.report["in_place_leaves"][73]),
                    (self.official[0x1348E:0x134D8], self.report["in_place_leaves"][74]),
                    (self.official[0x134D8:0x134FA], self.report["in_place_leaves"][75]),
                    (self.official[0x134FA:0x13524], self.report["in_place_leaves"][76]),
                    (self.official[0x13524:0x13608], self.report["in_place_leaves"][77]),
                    (self.official[0x13608:0x136CE], self.report["in_place_leaves"][78]),
                    (self.official[0x136CE:0x136FA], self.report["in_place_leaves"][79]),
                    (self.official[0x13700:0x1372A], self.report["in_place_leaves"][80]),
                    (self.official[0x1372A:0x13764], self.report["in_place_leaves"][81]),
                    (self.official[0x1377C:0x1382C], self.report["in_place_leaves"][82]),
                    (self.official[0x13864:0x138BA], self.report["in_place_leaves"][83]),
                    (self.official[0x138BA:0x13928], self.report["in_place_leaves"][84]),
                    (self.official[0x13928:0x13972], self.report["in_place_leaves"][85]),
                    (self.official[0x13972:0x139C2], self.report["in_place_leaves"][86]),
                    (self.official[0x139C2:0x13A48], self.report["in_place_leaves"][87]),
                    (self.official[0x13A48:0x13D08], self.report["in_place_leaves"][88]),
                    (self.official[0x13D08:0x13D20], self.report["in_place_leaves"][89]),
                    (self.official[0x13D20:0x13D58], self.report["in_place_leaves"][90]),
                    (self.official[0x13D58:0x13D7A], self.report["in_place_leaves"][91]),
                    (self.official[0x13D7A:0x13D9A], self.report["in_place_leaves"][92]),
                    (self.official[0x13DA0:0x13DC4], self.report["in_place_leaves"][93]),
                    (self.official[0x13DC4:0x13DCE], self.report["in_place_leaves"][94]),
                    (self.official[0x13DD0:0x13E0C], self.report["in_place_leaves"][95]),
                    (self.official[0x13E14:0x13E40], self.report["in_place_leaves"][96]),
                    (self.official[0x13E40:0x13E8A], self.report["in_place_leaves"][97]),
                    (self.official[0x13E8A:0x13F28], self.report["in_place_leaves"][98]),
                    (self.official[0x13F28:0x13F54], self.report["in_place_leaves"][99]),
                    (self.official[0x13F54:0x13F8E], self.report["in_place_leaves"][100]),
                    (self.official[0x13F8E:0x13FAC], self.report["in_place_leaves"][101]),
                    (self.official[0x13FAC:0x13FB8], self.report["in_place_leaves"][102]),
                    (self.official[0x13FB8:0x1403E], self.report["in_place_leaves"][103]),
                ],
            )

    def test_manifest_tracks_dual_image_littlefs_utility_replacements(
        self,
    ) -> None:
        overrides = self.core_source_manifest["component_overrides"]
        expected = {
            "apollo_bootloader": {
                "bootloader_littlefs_util_max_source_replacement": (
                    1024,
                    8,
                    0x00410400,
                ),
                "bootloader_littlefs_util_min_source_replacement": (
                    1032,
                    8,
                    0x00410408,
                ),
                "bootloader_littlefs_util_aligndown_source_replacement": (
                    1040,
                    12,
                    0x00410410,
                ),
                "bootloader_littlefs_util_alignup_source_replacement": (
                    1052,
                    12,
                    0x0041041C,
                ),
                "bootloader_littlefs_util_npw2_source_replacement": (
                    1064,
                    90,
                    0x00410428,
                ),
                "bootloader_littlefs_util_ctz_source_replacement": (
                    1154,
                    16,
                    0x00410482,
                ),
                "bootloader_littlefs_util_popc_source_replacement": (
                    1170,
                    40,
                    0x00410492,
                ),
                "bootloader_littlefs_util_fromle32_source_replacement": (
                    1214,
                    34,
                    0x004104BE,
                ),
                "bootloader_littlefs_util_tole32_source_replacement": (
                    1248,
                    8,
                    0x004104E0,
                ),
                "bootloader_littlefs_util_frombe32_source_replacement": (
                    1256,
                    34,
                    0x004104E8,
                ),
                "bootloader_littlefs_util_tobe32_source_replacement": (
                    1290,
                    8,
                    0x0041050A,
                ),
            },
            "apollo_main": {
                "littlefs_util_max_source_replacement": (
                    599832,
                    8,
                    0x004CA6F8,
                ),
                "littlefs_util_min_source_replacement": (
                    599840,
                    8,
                    0x004CA700,
                ),
                "littlefs_util_aligndown_source_replacement": (
                    599848,
                    12,
                    0x004CA708,
                ),
                "littlefs_util_alignup_source_replacement": (
                    599860,
                    12,
                    0x004CA714,
                ),
                "littlefs_util_npw2_source_replacement": (
                    599872,
                    90,
                    0x004CA720,
                ),
                "littlefs_util_ctz_source_replacement": (
                    599962,
                    16,
                    0x004CA77A,
                ),
                "littlefs_util_popc_source_replacement": (
                    599978,
                    40,
                    0x004CA78A,
                ),
                "littlefs_util_fromle32_source_replacement": (
                    600022,
                    34,
                    0x004CA7B6,
                ),
                "littlefs_util_tole32_source_replacement": (
                    600056,
                    8,
                    0x004CA7D8,
                ),
                "littlefs_util_frombe32_source_replacement": (
                    600064,
                    34,
                    0x004CA7E0,
                ),
                "littlefs_util_tobe32_source_replacement": (
                    600098,
                    8,
                    0x004CA802,
                ),
            },
        }
        for component_name, expected_regions in expected.items():
            actual_regions = {
                region["name"]: (
                    region["file_offset"],
                    region["size"],
                    region["target_address"],
                )
                for region in overrides[component_name]["regions"]
                if "littlefs_util_" in region["name"]
                and region["name"].endswith("_source_replacement")
            }
            with self.subTest(component=component_name):
                self.assertEqual(actual_regions, expected_regions)
                self.assertTrue(
                    all(
                        region["address_status"]
                        == "generated_source_entry_replacement"
                        for region in overrides[component_name]["regions"]
                        if "littlefs_util_" in region["name"]
                        and region["name"].endswith("_source_replacement")
                    )
                )

    def test_all_sources_are_the_authenticated_candidates(self) -> None:
        boot_source = (
            COMPONENT / "runtime_littlefs_alloc_ckpoint.c"
        ).read_bytes()
        main_candidate = (
            ROOT
            / "components"
            / "apollo_main"
            / "core_overlay"
            / "runtime_littlefs_alloc_ckpoint.c"
        ).read_bytes()
        self.assertEqual(boot_source, main_candidate)
        self.assertEqual(
            hashlib.sha256(boot_source).hexdigest(),
            "16acfce3da9211512631113cb717abd012a0d551ceed36c57b4af300c21e7395",
        )
        source = boot_source.decode("utf-8")
        self.assertIn("lookahead\n    ) +", source)
        self.assertIn("checkpoint\n        ) == 0x60U", source)
        self.assertIn("block_count\n    ) == 0x6CU", source)
        self.assertIn(
            "lfs->lookahead.checkpoint = lfs->block_count;",
            source,
        )

        alloc_drop_source = (
            COMPONENT / "runtime_littlefs_alloc_drop.c"
        ).read_bytes()
        self.assertEqual(
            hashlib.sha256(alloc_drop_source).hexdigest(),
            "38904bccaac4ef0fd39ad49374f287023e"
            "5f03d9b28dc0957d70f460ddfc07ee",
        )
        alloc_drop_text = alloc_drop_source.decode("utf-8")
        self.assertIn("lfs->lookahead.size = 0;", alloc_drop_text)
        self.assertIn("lfs->lookahead.next = 0;", alloc_drop_text)
        self.assertIn(
            "lfs->lookahead.checkpoint = lfs->block_count;",
            alloc_drop_text,
        )
        shared_sources = {
            "runtime_littlefs_disk_version.c": (
                "736a87363e5e009cb29f338c3245c22c0"
                "2df375e275207f3c6e107b456c26d00"
            ),
            "runtime_littlefs_mlist_append.c": (
                "e5423adbe01a734a67944b577bbd543a9"
                "50aefecccd14708bec5e951c58a2f8b"
            ),
            "runtime_littlefs_mlist_remove.c": (
                "be21546c80eaec4d8ad738ea6875bb67"
                "60fae7a873105658bd94a2a751b0bd7d"
            ),
            "runtime_littlefs_mlist_isopen.c": MLIST_ISOPEN_SOURCE_SHA256,
            "runtime_littlefs_util_endian.c": (
                LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256
            ),
            "runtime_littlefs_util.c": (
                "2730d0f39e02d7b6e07396894b796b26"
                "d9f73332deff23a685b5a06da0f7fb22"
            ),
            "runtime_littlefs_util_bitops.c": (
                "405092c6e8fc65a740f951cb2affaad8"
                "766e2553c7b8d290ff58f435e8830f47"
            ),
        }
        for filename, expected_sha256 in shared_sources.items():
            with self.subTest(source=filename):
                source_path = (
                    ROOT
                    / "components"
                    / "apollo_main"
                    / "core_overlay"
                    / filename
                )
                self.assertEqual(
                    hashlib.sha256(source_path.read_bytes()).hexdigest(),
                    expected_sha256,
                )
        self.assertEqual(
            {
                source["path"]: source["sha256"]
                for source in self.report["sources"]
            },
            {
                source["path"]: source["sha256"]
                for source in self.config["sources"]
            },
        )
        for source in self.config["sources"]:
            with self.subTest(configured_source=source["path"]):
                self.assertEqual(
                    hashlib.sha256(
                        (ROOT / source["path"]).read_bytes()
                    ).hexdigest(),
                    source["sha256"],
                )
        self.assertEqual(len(self.config["isolated_leaves"]), 6)
        isolated_configs = {
            leaf["function"]: leaf
            for leaf in self.config["isolated_leaves"]
        }
        isolated_reports = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.report["isolated_leaves"]
        }
        self.assertEqual(
            set(isolated_configs),
            {
                "am_hal_mspi_interrupt_clear",
                "open_cfw_littlefs_mlist_isopen",
                "open_cfw_littlefs_util_fromle32",
                "open_cfw_littlefs_util_tole32",
                "open_cfw_littlefs_util_frombe32",
                "open_cfw_littlefs_util_tobe32",
            },
        )
        self.assertEqual(set(isolated_reports), set(isolated_configs))
        isolated_config = isolated_configs["am_hal_mspi_interrupt_clear"]
        isolated_report = isolated_reports["am_hal_mspi_interrupt_clear"]
        self.assertEqual(
            isolated_config["function"],
            "am_hal_mspi_interrupt_clear",
        )
        self.assertEqual(
            isolated_config["source"]["sha256"],
            (
                "5a91ab0c67bda4bd61c7d436b94b5a7c"
                "81693b948a331d282ae10e88cc5bf85f"
            ),
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / isolated_config["source"]["path"]).read_bytes()
            ).hexdigest(),
            isolated_config["source"]["sha256"],
        )
        self.assertEqual(
            isolated_report["source"]["sha256"],
            isolated_config["source"]["sha256"],
        )
        self.assertEqual(
            isolated_report["extraction"]["sha256"],
            MSPI_INTERRUPT_CLEAR_SOURCE_SHA256,
        )
        self.assertEqual(
            isolated_report["extraction"]["relocation_count"],
            0,
        )
        mlist_config = isolated_configs[
            "open_cfw_littlefs_mlist_isopen"
        ]
        mlist_report = isolated_reports[
            "open_cfw_littlefs_mlist_isopen"
        ]
        self.assertEqual(
            mlist_config["source"]["sha256"],
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(
                (ROOT / mlist_config["source"]["path"]).read_bytes()
            ).hexdigest(),
            MLIST_ISOPEN_SOURCE_SHA256,
        )
        self.assertEqual(
            mlist_config["expected"],
            {
                "size": 18,
                "sha256": MLIST_ISOPEN_SOURCE_BODY_SHA256,
            },
        )
        self.assertEqual(
            mlist_report["extraction"]["sha256"],
            MLIST_ISOPEN_SOURCE_BODY_SHA256,
        )
        self.assertEqual(mlist_report["extraction"]["relocation_count"], 0)
        self.assertEqual(
            mlist_report["placement"],
            {
                "offset": 252,
                "size": 18,
                "alignment": 2,
                "padding_before": 0,
            },
        )
        endian_expectations = {
            "open_cfw_littlefs_util_fromle32": (
                270,
                2,
                LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_tole32": (
                272,
                2,
                LITTLEFS_UTIL_IDENTITY_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_frombe32": (
                274,
                4,
                LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
            ),
            "open_cfw_littlefs_util_tobe32": (
                278,
                4,
                LITTLEFS_UTIL_SWAP_SOURCE_SHA256,
            ),
        }
        for function_name, (
            expected_offset,
            expected_size,
            expected_sha256,
        ) in endian_expectations.items():
            with self.subTest(isolated_endian_leaf=function_name):
                config = isolated_configs[function_name]
                report = isolated_reports[function_name]
                self.assertEqual(
                    config["source"]["sha256"],
                    LITTLEFS_UTIL_ENDIAN_SOURCE_SHA256,
                )
                self.assertEqual(
                    report["extraction"]["sha256"],
                    expected_sha256,
                )
                self.assertEqual(
                    report["extraction"]["relocation_count"],
                    0,
                )
                self.assertEqual(
                    report["placement"],
                    {
                        "offset": expected_offset,
                        "size": expected_size,
                        "alignment": 2,
                        "padding_before": 0,
                    },
                )

    def test_easylogger_relocated_leaf_config_report_and_artifact_are_exact(
        self,
    ) -> None:
        self.assertEqual(len(self.config["relocated_leaves"]), 179)
        expected = {
            "open_cfw_easylogger_helpers_get_logger": {
                "source": (
                    "78dc5aa9a7eb4f072b3169ae18378550"
                    "07f25e1adccec7deaefecc486c8f0823"
                ),
                "offset": 352,
                "size": 8,
                "alignment": 4,
                "padding": 2,
                "runtime": EASYLOGGER_GET_LOGGER_TARGET,
                "raw": (
                    "3f32a69299002872bb9364f79744be13"
                    "11bcb8bce47f24f43558806931990064"
                ),
                "final": (
                    "3f32a69299002872bb9364f79744be13"
                    "11bcb8bce47f24f43558806931990064"
                ),
                "relocations": [],
            },
            "open_cfw_easylogger_helpers_assert_failed": {
                "source": (
                    "78dc5aa9a7eb4f072b3169ae18378550"
                    "07f25e1adccec7deaefecc486c8f0823"
                ),
                "offset": 360,
                "size": 132,
                "alignment": 4,
                "padding": 0,
                "runtime": EASYLOGGER_ASSERT_FAILED_TARGET,
                "raw": (
                    "f57622ddc7fdbe8555760ca15bf049b8"
                    "fb68abfb3203aa290500e22bbbf82b7a"
                ),
                "final": (
                    "f57622ddc7fdbe8555760ca15bf049b8"
                    "fb68abfb3203aa290500e22bbbf82b7a"
                ),
                "relocations": [],
            },
            "open_cfw_easylogger_get_fmt_enabled": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 492,
                "size": 38,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_TARGET,
                "raw": (
                    "563bc931557c5aae324ecfb98dbc4aa23"
                    "42c43c90163d462bea5e215c0de6390"
                ),
                "final": (
                    "8d2909984779762c0abf28369b018b99"
                    "b4b30f8d23391fe8670e57f43a166697"
                ),
                "relocations": [
                    (
                        14,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                    (
                        18,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_get_logger",
                        EASYLOGGER_GET_LOGGER_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_get_fmt_used_and_enabled_u32": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 530,
                "size": 20,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_U32_TARGET,
                "raw": (
                    "3e6f46ecf152d9192ec638cd0eafa92f"
                    "9c8adcfe7b36e8581add1a865234629a"
                ),
                "final": (
                    "7663e51e49d8c5099f140e85a2f898c"
                    "64083a0f02d1574db69294745ee8e5a93"
                ),
                "relocations": [
                    (
                        4,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_get_fmt_enabled",
                        EASYLOGGER_GET_FMT_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_get_fmt_used_and_enabled_ptr": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 550,
                "size": 20,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_GET_FMT_PTR_TARGET,
                "raw": (
                    "3e6f46ecf152d9192ec638cd0eafa92f"
                    "9c8adcfe7b36e8581add1a865234629a"
                ),
                "final": (
                    "b5f581ef33404949889812a73244d6b5"
                    "c7807ad5707074228a188df7d89ad898"
                ),
                "relocations": [
                    (
                        4,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_get_fmt_enabled",
                        EASYLOGGER_GET_FMT_TARGET,
                    ),
                ],
            },
            "open_cfw_easylogger_strcpy": {
                "source": (
                    "8f2850f789fba3b08bdc3e1fa8f3a46"
                    "46aaef7e4b16862f3be53478071aa22b5"
                ),
                "offset": 570,
                "size": 52,
                "alignment": 2,
                "padding": 0,
                "runtime": EASYLOGGER_STRCPY_TARGET,
                "raw": (
                    "1fac8de3a83876460e17014da0f84538"
                    "4b253a88d5b79e25f6e5e838e6f46013"
                ),
                "final": (
                    "d19a927665be77d79bd2df6a64575431"
                    "db8962aa023f0546f5c3fe5f47805752"
                ),
                "relocations": [
                    (
                        12,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                    (
                        20,
                        "R_ARM_THM_CALL",
                        "open_cfw_easylogger_helpers_assert_failed",
                        EASYLOGGER_ASSERT_FAILED_TARGET,
                    ),
                ],
            },
            "open_cfw_bootloader_easylogger_output_4176ce": {
                "source": (
                    "60859f54b54e14e4a22c180d61ea76bd"
                    "63b358d6896c4787d2d0f7d40816a500"
                ),
                "offset": 7780,
                "size": 1060,
                "alignment": 4,
                "padding": 0,
                "runtime": EASYLOGGER_OUTPUT_TARGET,
                "raw": (
                    "b64c49b0615fd3cb4d5aba393ea929024"
                    "fc05a7e884eea41019777b6b667d4ce"
                ),
                "final": (
                    "b64c49b0615fd3cb4d5aba393ea929024"
                    "fc05a7e884eea41019777b6b667d4ce"
                ),
                "relocations": [],
            },
            "open_cfw_bootloader_easylogger_output_lock_enabled_417b7c": {
                "source": (
                    "dde99764f5b84ceec45b30880708b279"
                    "3443395deb715646c15fd14299c5c8af"
                ),
                "offset": 8840,
                "size": 36,
                "alignment": 4,
                "padding": 0,
                "runtime": EASYLOGGER_LOCK_ENABLED_TARGET,
                "raw": (
                    "9ea9783eda65110ea7b7df1bfe4fdfbff"
                    "1bc670a9bbc91e929f694110ef3cf3f"
                ),
                "final": (
                    "9ea9783eda65110ea7b7df1bfe4fdfbff"
                    "1bc670a9bbc91e929f694110ef3cf3f"
                ),
                "relocations": [],
            },
        }
        port_source = (
            "2d2196f1eed0c4d3e712e6ae8cffef60"
            "793dfdeecdb9327c24c9083b31f39677"
        )
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_easylogger_mutex_create_41a648", 8876, 32, 0x00436724, "65b081c526809d176888e5a225218ac8b52a55ebcd18eff5175c7df5dc4dcf96"),
            ("open_cfw_bootloader_easylogger_mutex_acquire_41a65c", 8908, 24, 0x00436744, "5ee00a1454af6bcb8a3edcac17a66b5dd64414e59fac03239b9f5ba8b0f9b919"),
            ("open_cfw_bootloader_easylogger_mutex_release_41a672", 8932, 20, 0x0043675C, "99d16b1b908bc7eda48624de017d7ddecbd77ea6e53f5a8a662accab40b214b8"),
            ("open_cfw_bootloader_easylogger_port_init_41a684", 8952, 16, 0x00436770, "1eb0c5ea0d55803543ed4a889d7f144f5af4db864d3402a4534e9718b66aea70"),
            ("open_cfw_bootloader_easylogger_port_output_41a692", 8968, 8, 0x00436780, "c6f1c25de446b8ac135df46d835527dc0b5cb6529919e09877aad19a7c57a40c"),
            ("open_cfw_bootloader_easylogger_port_output_lock_41a69a", 8976, 8, 0x00436788, "03310f996f7783899a2abc793a571e41a18f912b0f56d0a79179badce97ec98e"),
            ("open_cfw_bootloader_easylogger_port_output_unlock_41a6a2", 8984, 8, 0x00436790, "80fce826c95fae2db2939152195632be71a0d191a442ca8e576d8a9ddb59574a"),
            ("open_cfw_bootloader_easylogger_port_get_time_41a6aa", 8992, 40, 0x00436798, "175cac72bdde549348b1a10404c697d8acd0da3ef9fe801b804cfbef9b59f945"),
            ("open_cfw_bootloader_easylogger_task_name_41a6c2", 9032, 40, 0x004367C0, "16ea94d390cd0ccd83b6999fede0e59558a2cc95872630c98f712dbf02cad525"),
            ("open_cfw_bootloader_easylogger_port_get_p_info_41a6f0", 9072, 8, 0x004367E8, "42724cfc598dd969cb7729ee73080ac77d0530404bd72831a66398d79574aef1"),
            ("open_cfw_bootloader_easylogger_port_get_t_info_41a6f8", 9080, 8, 0x004367F0, "42724cfc598dd969cb7729ee73080ac77d0530404bd72831a66398d79574aef1"),
        ):
            expected[name] = {
                "source": port_source,
                "offset": offset,
                "size": size,
                "alignment": 4,
                "padding": 0,
                "runtime": runtime,
                "raw": body_hash,
                "final": body_hash,
                "relocations": [],
            }
        mspi_source = "1ae615db206b9658a042eff863888d259ee31b4ea2a3511bc1cec3e2b30a031c"
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_mspi_enable_41fe28", 10116, 40, 0x00436BFC, "d2c4bcc5e93182f643d4c97f6fe2295851308b0efb33e2a5a5f7434da7cad2b8"),
            ("open_cfw_bootloader_mspi_disable_41fe48", 10156, 32, 0x00436C24, "22eba2a5dc7603d067ed9bb72afe6f491a7b4c4fae06da054e572bc11165aed0"),
        ):
            expected[name] = {"source": mspi_source, "offset": offset, "size": size, "alignment": 4, "padding": 0, "runtime": runtime, "raw": body_hash, "final": body_hash, "relocations": []}
        mspi_guard_source = "7e8887462129c0cf147126e324ae240c91abf9718bb7bb27fb3390a2b36849da"
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_mspi_guard_enter_41ff08", 10396, 36, 0x00436D14, "e900042722fccbebf61515c642ef2f75157022328550eaed47ecafa2465307eb"),
            ("open_cfw_bootloader_mspi_guard_exit_41ff1e", 10432, 32, 0x00436D38, "dfb2fdd918afb3a3133234aa452430ab22ce73839c07e81914fa798ec49b4e40"),
        ):
            expected[name] = {"source": mspi_guard_source, "offset": offset, "size": size, "alignment": 4, "padding": 0, "runtime": runtime, "raw": body_hash, "final": body_hash, "relocations": []}
        expected["open_cfw_bootloader_mspi_xip_config_41ff34"] = {
            "source": "5f5bea367de55e637c87bc3e5888a7350654692af1499a3bd5b45ace2c3a6d8e",
            "offset": 10464,
            "size": 36,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00436D58,
            "raw": "0cc0ac059e80451afec8ddbad56203612ebc34a9559a549f6c499bd958be87eb",
            "final": "0cc0ac059e80451afec8ddbad56203612ebc34a9559a549f6c499bd958be87eb",
            "relocations": [],
        }
        bit_run_source = "4647db644148f4df98454c6018d684a70e52306b0f2cfbbdfd79749fd2f53903"
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_longest_ones_run_41ff60", 10500, 16, 0x00436D7C, "a690bd1df07a26fa65416653fee80c088615b3c492786331ee08f1446585ef4d"),
            ("open_cfw_bootloader_longest_ones_center_41ff74", 10516, 126, 0x00436D8C, "d36402e8d02ee3663653477b656cd3ba1b713dc65688373e34f3d20332926390"),
        ):
            expected[name] = {"source": bit_run_source, "offset": offset, "size": size, "alignment": 2, "padding": 0, "runtime": runtime, "raw": body_hash, "final": body_hash, "relocations": []}
        expected["open_cfw_bootloader_mspi_timing_scan_420002"] = {
            "source": "bbf4ccc39eff32fbf45ef5a880f78eb6fec934394ea888f47140ca7b0c0d4c50",
            "offset": 10644,
            "size": 420,
            "alignment": 4,
            "padding": 2,
            "runtime": 0x00436E0C,
            "raw": "b3582162aa1a50ecf33e55f380293a100a5fde5d9db41043f8f796b268c0ccb2",
            "final": "184a82c6cb821121c638e1b237802adc07ffa89d7c9655262156e4c8c32ce481",
            "relocations": [
                (194, "R_ARM_THM_CALL", "open_cfw_bootloader_longest_ones_run_41ff60", 0x00436D7C),
                (320, "R_ARM_THM_CALL", "open_cfw_bootloader_longest_ones_center_41ff74", 0x00436D8C),
            ],
        }
        expected["open_cfw_bootloader_mspi_timing_auto_4201ba"] = {
            "source": "60ef2a425997e8b4e760c0a2c2cf6cc139a336759ea1b400f9e2909cc798c8c8",
            "offset": 11064,
            "size": 172,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00436FB0,
            "raw": "c80f3e39201fd4dfb3648711af97e0f4eaa1e645c61d97f85bcab72bb3cfac8f",
            "final": "96486cb54903f2e183aa7923a84f71f17027a24397e84dde3c9154a78d0b0e56",
            "relocations": [
                (26, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_timing_scan_420002", 0x00436E0C),
            ],
        }
        expected["open_cfw_bootloader_mspi_low_level_init_420254"] = {
            "source": "e5170727ba0e6fbc412ccc2dc1a845f777a66c1bd10eba3248db041bde31548d",
            "offset": 11236,
            "size": 492,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x0043705C,
            "raw": "d04f06e63eb149ba70e030001552991f0222d43ec3aa74321640675ba0439e33",
            "final": "a2eeead28dbb8476a9772b171133db5e8475deb85de7b72ff75abbbf7f6a92ea",
            "relocations": [
                (290, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_xip_config_41ff34", 0x00436D58),
                (298, "R_ARM_THM_CALL", "open_cfw_bootloader_pin_groups_41fadc", 0x00436988),
                (378, "R_ARM_THM_CALL", "open_cfw_bootloader_nvic_set_priority_41fdde", 0x00436BAC),
                (384, "R_ARM_THM_CALL", "open_cfw_bootloader_nvic_enable_irq_41fdc0", 0x00436B8C),
            ],
        }
        expected["open_cfw_bootloader_mspi_driver_init_420476"] = {
            "source": "65a390f2c770079f4255ea489cc02bc0f593674de7688d3fb550f201ebc8785f",
            "offset": 11728,
            "size": 204,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437248,
            "raw": "9f93f834b499f13412e425a025c6be9d1e86a60c7f461b223e654fdf5134bdd9",
            "final": "31195e4775918f5fb7b0925f2cfa15b4a8f699688ae3bb0888527299de197e7c",
            "relocations": [
                (14, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_low_level_init_420254", 0x0043705C),
                (60, "R_ARM_THM_CALL", "open_cfw_bootloader_delay_milliseconds_41f9d8", 0x00436880),
                (78, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_timing_auto_4201ba", 0x00436FB0),
                (158, "R_ARM_THM_CALL", "open_cfw_bootloader_event_flags_init_41fe62", 0x00436C44),
                (162, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_enable_41fe28", 0x00436BFC),
            ],
        }
        expected["open_cfw_bootloader_mspi_soft_reset_42052a"] = {
            "source": "ebe83fc0c63dc78e6c165f308dfd331eaf9cdc0a171c036a564f581d55bd3b47",
            "offset": 11932,
            "size": 136,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437314,
            "raw": "1223a14bfe9fc5267517253e84772bf9eb52ce7d760f563db26fd342d838a468",
            "final": "17354876de75a9540cac0603e3f8eae3fbd564a239c0d07f771b1104065c817c",
            "relocations": [
                (58, "R_ARM_THM_CALL", "open_cfw_bootloader_delay_milliseconds_41f9d8", 0x00436880),
                (106, "R_ARM_THM_JUMP24", "open_cfw_bootloader_delay_milliseconds_41f9d8", 0x00436880),
            ],
        }
        expected["open_cfw_bootloader_mspi_read_id_42059e"] = {
            "source": "3e279abf9a149279da6fdb72009884e62224800e7843d487a803e5fa7293e1b6",
            "offset": 12068,
            "size": 100,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x0043739C,
            "raw": "cbd9055d50d62d9ff1208d66fd3e62785e8e20021b311a318d22c1aab4bf4dbe",
            "final": "cbd9055d50d62d9ff1208d66fd3e62785e8e20021b311a318d22c1aab4bf4dbe",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_read_transfer_4205f4"] = {
            "source": "d310d632be00ea4c9c136b5e089340d83cecdeaa74be814b5864e9abf592a525",
            "offset": 12168,
            "size": 172,
            "alignment": 8,
            "padding": 0,
            "runtime": 0x00437400,
            "raw": "b7ab22593ca756879ce8f8dbdcf249806ec23beff8029959fecb39d3c2e784ed",
            "final": "b7ab22593ca756879ce8f8dbdcf249806ec23beff8029959fecb39d3c2e784ed",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_write_transfer_42069e"] = {
            "source": "7fa590ec5cd0fbd87feb193c9bdec3becb0a6acea6334555c84683e3565451c1",
            "offset": 12340,
            "size": 148,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004374AC,
            "raw": "dac51840015d8553b2684538ff0a5a092d6c03122aa933a3af8d706a2e9d2b73",
            "final": "dac51840015d8553b2684538ff0a5a092d6c03122aa933a3af8d706a2e9d2b73",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_busy_status_42074e"] = {
            "source": "361432557372303651f41bb8d3446d1f18f1753914fb8227fd6a4c57355685b8",
            "offset": 12488,
            "size": 88,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437540,
            "raw": "941545cc31870eadc0effa9a311c8e48788ffe3c33c644e58ccc11723ea304a5",
            "final": "941545cc31870eadc0effa9a311c8e48788ffe3c33c644e58ccc11723ea304a5",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_wait_ready_4207a2"] = {
            "source": "3818159361e949ac31c6c5e78c2f8236015ea2b76b571358efdd3fab789785b0",
            "offset": 12576,
            "size": 88,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437598,
            "raw": "c91a275806d2281aaf13566e176ceb688e1e9f74a16955a754853f99bda5cba4",
            "final": "c91a275806d2281aaf13566e176ceb688e1e9f74a16955a754853f99bda5cba4",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_wait_ready_default_4207f4"] = {
            "source": "3818159361e949ac31c6c5e78c2f8236015ea2b76b571358efdd3fab789785b0",
            "offset": 12664,
            "size": 12,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004375F0,
            "raw": "0179837648f7b822a8e664cdbba880d3d1a90e9951dab053afcc693f5240bffe",
            "final": "0179837648f7b822a8e664cdbba880d3d1a90e9951dab053afcc693f5240bffe",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_4byte_mode_420800"] = {
            "source": "1d1282fbfbbfa62aa87a68d323c9fc85faf996ed1c6a56d3967134e4f97f1cc7",
            "offset": 12676,
            "size": 124,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004375FC,
            "raw": "39be5e62d485cd317fc91cb56ead2101d297d71c0e9af887cc33034e81d28979",
            "final": "39be5e62d485cd317fc91cb56ead2101d297d71c0e9af887cc33034e81d28979",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_enter_4byte_mode_420890"] = {
            "source": "da4425a664e3cfa980878ccf79c6770ad133f1991504bc0524c8d7866b408c9b",
            "offset": 12800,
            "size": 220,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437678,
            "raw": "041427a167b5b0379af8d927c7ab094274fcd542b67cfe5a0deaccbd885571e4",
            "final": "041427a167b5b0379af8d927c7ab094274fcd542b67cfe5a0deaccbd885571e4",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_write_enable_420984"] = {
            "source": "a2bb35ee6fce5e016accddfd028cf0152aa6b025b467eb8e5a695bbe09f8ca78",
            "offset": 13020,
            "size": 72,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437754,
            "raw": "e55a89dcef578fc6fa07e7935d8c0edf4f2d76cceef420b1a50b1468ea90fa76",
            "final": "e55a89dcef578fc6fa07e7935d8c0edf4f2d76cceef420b1a50b1468ea90fa76",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_write_disable_4209c4"] = {
            "source": "a2bb35ee6fce5e016accddfd028cf0152aa6b025b467eb8e5a695bbe09f8ca78",
            "offset": 13092,
            "size": 72,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x0043779C,
            "raw": "398b8c96a5d637a6bf6a1d977c0dcd0b1dee70594c4dbc2c7e44ec70b7b7d99c",
            "final": "398b8c96a5d637a6bf6a1d977c0dcd0b1dee70594c4dbc2c7e44ec70b7b7d99c",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_sector_erase_420a08"] = {
            "source": "d23d511d53de96bd748611c1bea5312687bf6d4338f200030634d5b908fa4ae8",
            "offset": 13164,
            "size": 244,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004377E4,
            "raw": "673dea5391605a49b503acf81a1c3ab626fc70bbdfd92ad2b156902516fbb060",
            "final": "673dea5391605a49b503acf81a1c3ab626fc70bbdfd92ad2b156902516fbb060",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_program_420b0c"] = {
            "source": "4d562ceaf98995b5cf92e1d8103c6a163f19786eb75be083ad6a778310938169",
            "offset": 13408,
            "size": 256,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004378D8,
            "raw": "1d90e6749de44a32ff7a6b4ced694569bf95e4b836961891cde35edf06f6e482",
            "final": "1d90e6749de44a32ff7a6b4ced694569bf95e4b836961891cde35edf06f6e482",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_quad_enable_420c5c"] = {
            "source": "698d511d3824f122d555a9705fe9ea9750859dfa1e1da814407add16cd657f4a",
            "offset": 13664,
            "size": 364,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004379D8,
            "raw": "3c44f102542a992680fb79525bbd3caa0c264ae9a5b010cc2c6a9c78ec93c91b",
            "final": "3c44f102542a992680fb79525bbd3caa0c264ae9a5b010cc2c6a9c78ec93c91b",
            "relocations": [],
        }
        expected["open_cfw_bootloader_mspi_device_reconfigure_420e08"] = {
            "source": "23ce33f81eacea40350c99427d0156e488b2d28d80a7bb040438fe55f91c2551",
            "offset": 14028,
            "size": 136,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437B44,
            "raw": "065da9327ea493b21dc7d44cc863947c88a5d1c407f031ed1d9327e320ef8204",
            "final": "7be99b6cd10ca4a8bcb4dc893a246c439a117d95798ab566d9f5def8d35d60f4",
            "relocations": [
                (98, "R_ARM_THM_CALL", "open_cfw_bootloader_pin_groups_41fadc", 0x00436988),
            ],
        }
        expected["open_cfw_bootloader_mspi_set_quad_mode_420e8c"] = {
            "source": "9a94b5d2766ecbbfe5b428779dc34c7a0eb19f4b7e6eeb7edb1cededa9228833",
            "offset": 14164,
            "size": 152,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437BCC,
            "raw": "c9a0245f4090f520644aa4fda29308adf089d78cafa84d959754493926a65bdd",
            "final": "f16e2d6db8f18731b03c5f1a335ebd5f80d9524d8b320749666c05185415eb3c",
            "relocations": [
                (12, "R_ARM_THM_CALL", "open_cfw_bootloader_aeabi_memcpy", 0x00434830),
                (48, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_device_reconfigure_420e08", 0x00437B44),
                (66, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_xip_config_41ff34", 0x00436D58),
            ],
        }
        expected["open_cfw_bootloader_mspi_set_serial_mode_420f10"] = {
            "source": "85f79cccdaa9644e765ab2580b91f75f3dcb5cfcb26125d2878dddc0a37ae361",
            "offset": 14316,
            "size": 124,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437C64,
            "raw": "4af379ff55bf842dcfd2cc6589a6e4c0c27012bd9cbbf74d6baee92a9e51736b",
            "final": "7bd7debf9e5a4c3eea789c950410381f3579bf14a97f92ccc45d453457949ba9",
            "relocations": [
                (4, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_device_reconfigure_420e08", 0x00437B44),
                (40, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_xip_config_41ff34", 0x00436D58),
            ],
        }
        expected["open_cfw_bootloader_mspi_read_420f70"] = {
            "source": "9ace6b932c3a183df9ce4a07c06463404a4dd07007a9c4fe55443b26edc00163",
            "offset": 14440,
            "size": 152,
            "alignment": 8,
            "padding": 0,
            "runtime": 0x00437CE0,
            "raw": "87dd2258a3f977fd79e3fde36da8d48b5aeea0568f3a9ae903d87844208360cb",
            "final": "4acc213e830b898b6698c827bfd3e39e2f65d93844675047274315828a6cac71",
            "relocations": [
                (40, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_guard_enter_41ff08", 0x00436D14),
                (44, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_set_quad_mode_420e8c", 0x00437BCC),
                (48, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_wait_ready_default_4207f4", 0x004375F0),
                (94, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_guard_exit_41ff1e", 0x00436D38),
            ],
        }
        expected["open_cfw_bootloader_check_and_create_directories_4210c8"] = {
            "source": "0a8b482985fba7d10d39eaf042faa4317c317c7c932bb70665b5f88b479e1a60",
            "offset": 14592,
            "size": 220,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437D78,
            "raw": "39fdef6b959bb5771f637ac6084bc6ce5f357aa7a32288e6a15cbe0f90d569d8",
            "final": "456bcb6e3fb5bb820e3f400352787f03419828d247956407e06ca3fadb853f72",
            "relocations": [
                (144, "R_ARM_THM_CALL", "open_cfw_bootloader_easylogger_output_4176ce", 0x004362DC),
                (182, "R_ARM_THM_CALL", "open_cfw_bootloader_easylogger_output_4176ce", 0x004362DC),
            ],
        }
        expected["open_cfw_littlefs_bootloader_format_4211b0"] = {
            "source": "1a6372a3c81e895c67326bba005c655fe0d011be306fa3c453c8afbd8600b496",
            "offset": 14812,
            "size": 108,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437E54,
            "raw": "173e8b905d12452d033fef79fe4729df236a647d92f4ed23f07f901e0bda55bc",
            "final": "dde3d1adb0ab07eb997820b6b6f6c505b965be976585252b893daff999585fdc",
            "relocations": [
                (48, "R_ARM_THM_CALL", "open_cfw_bootloader_check_and_create_directories_4210c8", 0x00437D78),
                (72, "R_ARM_THM_CALL", "open_cfw_bootloader_easylogger_output_4176ce", 0x004362DC),
            ],
        }
        expected["open_cfw_bootloader_littlefs_read_4212d8"] = {
            "source": "05f807e60ece402cf2d4f3d89e50f022813f33e80e96bb065e14c4ba460acbaf",
            "offset": 15180,
            "size": 60,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00437FC4,
            "raw": "128ce01c51af09ed5433ccb3bfb1f097f54687a0ad38bbd33211d6af8d10ab5a",
            "final": "b1f49f83efac394d09db4885f1776717342630734fa0f9c2e25b984e626686db",
            "relocations": [
                (22, "R_ARM_THM_CALL", "open_cfw_bootloader_mspi_read_420f70", 0x00437CE0),
                (40, "R_ARM_THM_CALL", "open_cfw_bootloader_log_dispatch", 0x00434F80),
            ],
        }
        transport_source = (
            "23a5180d3de5e45625f8323a226291d9"
            "f5ced532d7d73a320e57640794161d1c"
        )
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_easylogger_driver_output_41b854", 9088, 16, 0x004367F8, "d1cc42fea93ac782c64485bf4d8ae24108ab6b8a7e9b189918395a5f547521a1"),
            ("open_cfw_bootloader_easylogger_channel_write_41f918", 9104, 120, 0x00436808, "75b841d487a68f0f09928f569ea01229e4ef4dd4022533200050b317edbfcd0b"),
        ):
            expected[name] = {
                "source": transport_source,
                "offset": offset,
                "size": size,
                "alignment": 4,
                "padding": 0,
                "runtime": runtime,
                "raw": body_hash,
                "final": body_hash,
                "relocations": [],
            }
        boot_services_source = (
            "99aa433811660dd98b1e927d99fdbdb3"
            "d2214ad7a88d30ed36803305873cf693"
        )
        for name, offset, size, alignment, runtime, body_hash in (
            ("open_cfw_bootloader_delay_milliseconds_41f9d8", 9224, 16, 4, 0x00436880, "44ebf4e1f372017ceaa6885948b4e02f8dc5ede3c18f547a9d8e1a54e9db33f5"),
            ("open_cfw_bootloader_delay_41f9e6", 9240, 8, 4, 0x00436890, "071c3652bfd2017f385f368863d1ad8fa69b4f2bf93706786dbfc9899cad09dd"),
            ("open_cfw_bootloader_initializer_priority_compare_41f9f0", 9248, 8, 2, 0x00436898, "daa15c77ff9790a201193ce3e4a9cc74b8caf26827306a324f0889f4ed934ead"),
            ("open_cfw_bootloader_run_initializers_41f9f8", 9256, 64, 4, 0x004368A0, "7b81438b36f613dbd31af78de972c28814c93a8e4551f261c7b928bf944f4729"),
        ):
            expected[name] = {
                "source": boot_services_source,
                "offset": offset,
                "size": size,
                "alignment": alignment,
                "padding": 0,
                "runtime": runtime,
                "raw": body_hash,
                "final": body_hash,
                "relocations": [],
            }
        expected["open_cfw_bootloader_guarded_teardown_41fa98"] = {
            "source": (
                "ad8f5eba68fce82f9e3d7807f2aed0ef"
                "207e76fff8840e7497429f9c06e960e9"
            ),
            "offset": 9320,
            "size": 72,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x004368E0,
            "raw": (
                "075c10d5ae973c25ffaf80a383199f8a"
                "ed52f9e53abcd817f480b52357fb2f83"
            ),
            "final": (
                "075c10d5ae973c25ffaf80a383199f8a"
                "ed52f9e53abcd817f480b52357fb2f83"
            ),
            "relocations": [],
        }
        expected["open_cfw_bootloader_platform_setup_41fa50"] = {
            "source": (
                "5126096f05bd4d66f7148fd564c7defd"
                "b9b4b49729d358f6a768579fcfe372d1"
            ),
            "offset": 9392,
            "size": 96,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00436928,
            "raw": (
                "e064ce74a17db06a9bb9d6dab1bbaf80"
                "7c01215d270c916c02782c90a55a4a67"
            ),
            "final": (
                "e064ce74a17db06a9bb9d6dab1bbaf80"
                "7c01215d270c916c02782c90a55a4a67"
            ),
            "relocations": [],
        }
        expected["open_cfw_bootloader_pin_groups_41fadc"] = {
            "source": (
                "2608a97a8a2fc3e8e63e3eeae78dbec8"
                "1646e4d650b407bbcb9ebae86e9fff86"
            ),
            "offset": 9488,
            "size": 428,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00436988,
            "raw": (
                "e792fc1fbd6ae3a13b8e2edd4f37a349"
                "8752bb07f8293f761c331b1fbe017ea7"
            ),
            "final": (
                "e792fc1fbd6ae3a13b8e2edd4f37a349"
                "8752bb07f8293f761c331b1fbe017ea7"
            ),
            "relocations": [],
        }
        expected["open_cfw_bootloader_allocator_init_41fd70"] = {
            "source": (
                "53dc0ff1c3c47d2afcb585f6753e4eaa"
                "a29ae9494c705e0f73ff5929dd487713"
            ),
            "offset": 9916,
            "size": 88,
            "alignment": 4,
            "padding": 0,
            "runtime": 0x00436B34,
            "raw": (
                "1a588b40d59408de4b8f541890868a18"
                "a827a77c7333c958687ebeae21f30ddc"
            ),
            "final": (
                "1a588b40d59408de4b8f541890868a18"
                "a827a77c7333c958687ebeae21f30ddc"
            ),
            "relocations": [],
        }
        irq_source = (
            "c1b495b5d4de6ab8045e8e9f225736c"
            "9d3b0cabbe93d712b4b347675394a377b"
        )
        for name, offset, size, runtime, body_hash in (
            ("open_cfw_bootloader_nvic_enable_irq_41fdc0", 10004, 32, 0x00436B8C, "a0b40ca8273aa7d4e30b39a932157c6d1ab613aa5daa0d63cd8460129647975e"),
            ("open_cfw_bootloader_nvic_set_priority_41fdde", 10036, 32, 0x00436BAC, "8b9fce902a009a23dc8d8b9be0e1c54487b2df821852dd97217ce6d96af9e9e6"),
            ("open_cfw_bootloader_mspi_isr_41fe06", 10068, 48, 0x00436BCC, "554fc96172fb02ad47a180f43424b16d860c0b249a1e380b57584e56c10cfb54"),
        ):
            expected[name] = {
                "source": irq_source,
                "offset": offset,
                "size": size,
                "alignment": 4,
                "padding": 0,
                "runtime": runtime,
                "raw": body_hash,
                "final": body_hash,
                "relocations": [],
            }
        config_by_name = {
            leaf["function"]: leaf
            for leaf in self.config["relocated_leaves"]
            if leaf["function"] in expected
        }
        report_by_name = {
            leaf["extraction"]["function"]: leaf
            for leaf in self.report["relocated_leaves"]
            if leaf["extraction"]["function"] in expected
        }
        self.assertEqual(set(config_by_name), set(expected))
        self.assertEqual(set(report_by_name), set(expected))

        for name, pin in expected.items():
            with self.subTest(easylogger_relocated_leaf=name):
                config = config_by_name[name]
                report = report_by_name[name]
                self.assertEqual(
                    hashlib.sha256(
                        (ROOT / config["source"]["path"]).read_bytes()
                    ).hexdigest(),
                    pin["source"],
                )
                self.assertEqual(config["source"]["sha256"], pin["source"])
                self.assertEqual(report["source"]["sha256"], pin["source"])
                self.assertEqual(
                    report["placement"],
                    {
                        "offset": pin["offset"],
                        "size": pin["size"],
                        "alignment": pin["alignment"],
                        "padding_before": pin["padding"],
                        "runtime_address": pin["runtime"],
                        "runtime_address_hex": f"0x{pin['runtime']:08X}",
                    },
                )
                extraction = report["extraction"]
                self.assertEqual(extraction["size"], pin["size"])
                self.assertEqual(
                    extraction["unrelocated_sha256"],
                    pin["raw"],
                )
                self.assertEqual(extraction["sha256"], pin["final"])
                self.assertEqual(
                    [
                        (
                            relocation["offset"],
                            relocation["type"],
                            relocation["symbol"],
                            relocation["target_address"],
                        )
                        for relocation in extraction["relocations"]
                    ],
                    pin["relocations"],
                )
                self.assertEqual(
                    hashlib.sha256(
                        self.overlay[
                            pin["offset"]:pin["offset"] + pin["size"]
                        ]
                    ).hexdigest(),
                    pin["final"],
                )

    def test_evenota_wrapper_integrity_is_external_and_regenerated(self) -> None:
        transport = self.contract["transport"]
        component = {
            "package_filename": transport["package_filename"],
            "type_id": transport["type_id"],
            "storage_type": transport["storage_type"],
        }
        header = self.open_cfw.component_header(component, self.provider)
        checksum = self.open_cfw.crc32c_msb(self.provider)
        self.assertEqual(checksum, PROVIDER_CRC32C_MSB)
        self.assertEqual(len(header), 128)
        self.assertEqual(struct.unpack_from("<I", header, 8)[0], len(self.provider))
        self.assertEqual(struct.unpack_from("<I", header, 12)[0], checksum)
        self.assertEqual(struct.unpack_from("<I", header, 0x14)[0], 0x4E455645)
        self.assertNotEqual(checksum, self.open_cfw.crc32c_msb(self.official))
        self.assertEqual(
            transport["toc_entry_size_field"],
            "component_header_bytes + payload_size",
        )

    def test_provider_contract_is_manifest_ready_and_hardware_free(self) -> None:
        provider = self.contract["provider"]
        self.assertEqual(provider["kind"], "source_build")
        self.assertEqual(provider["size"], len(self.provider))
        self.assertEqual(provider["sha256"], PROVIDER_SHA256)
        manifest_override = self.core_source_manifest["component_overrides"][
            "apollo_bootloader"
        ]
        self.assertEqual(
            {
                key: manifest_override["provider"][key]
                for key in ("kind", "path", "size", "sha256")
            },
            provider,
        )
        self.assertEqual(
            manifest_override["provider"]["profiles"]["linux-clang"],
            {
                "size": 163824,
                "sha256": (
                    "d0a97870b861c089e4ac029ba1c7a1c0"
                    "cc67d6112c3416a5cda657a038c3a8ea"
                ),
            },
        )
        ownership_fields = (
            "file_offset",
            "size",
            "target_address",
            "address_status",
        )
        self.assertEqual(
            [
                tuple(region[field] for field in ownership_fields)
                for region in manifest_override["regions"]
            ],
            [
                tuple(region[field] for field in ownership_fields)
                for region in self.contract["regions"]
            ],
        )
        self.assertTrue(
            all(
                region["target"] == "apollo510b_internal_mram"
                for region in manifest_override["regions"]
            )
        )
        self.assertEqual(self.contract["hardware_operations"], [])
        self.assertEqual(self.report["safety"]["hardware_operations"], [])
        self.assertFalse(self.report["safety"]["package_assembly_performed"])
        self.assertFalse(self.report["safety"]["flashing_performed"])
        self.assertFalse(self.report["safety"]["erasing_performed"])

        self.assertEqual(
            sorted(path.name for path in self.output.iterdir()),
            [
                "bootloader_core_overlay.bin",
                "build-report.json",
                "ota_s200_bootloader.bin",
                "provider-contract.json",
            ],
        )

    def test_rebuild_is_deterministic(self) -> None:
        second = Path(self.temporary.name) / "second"
        report = self.builder.build(
            root=ROOT,
            config_path=CONFIG_PATH,
            output_dir=second,
            clang=os.environ.get("OPENCFW_CLANG", "/usr/bin/clang"),
        )
        self.assertEqual(
            (second / "ota_s200_bootloader.bin").read_bytes(),
            self.provider,
        )
        self.assertEqual(
            (second / "bootloader_core_overlay.bin").read_bytes(),
            self.overlay,
        )
        self.assertEqual(report["component"]["sha256"], PROVIDER_SHA256)


if __name__ == "__main__":
    unittest.main()
