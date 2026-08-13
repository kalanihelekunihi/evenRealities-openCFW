#!/usr/bin/env python3
"""Fail-closed CmBacktrace version/config audit for the G2 Apollo image.

The analyzer authenticates and reads only the official ``2.2.6.10``
Apollo-main payload.  It pins the linked CmBacktrace message table, selected
function bodies, compiler/RTOS seams, and the two upstream source-history
discriminators that bound the compatible unmodified source interval.  It has
no device, debugger, serial, signing, or flash-writing path.

Run addresses use ``run = file_offset + 0x00437FE0``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "blobs" / "official" / "g2-2.2.6.10" / "ota_s200_firmware_ota.bin"
MAIN_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
LOAD_BASE = 0x00437FE0


class AuditError(RuntimeError):
    """Raised when authenticated bytes or a pinned recovery invariant drift."""


# The real table starts one pointer before the address reported in the first
# identity pass.  Index zero is PRINT_MAIN_STACK_CFG_ERROR; firmware info is
# index one.  The messages are byte-identical to upstream en-US at the
# compatible interval except index eight, where Even prepended its vendored
# Windows addr2line path.
PRINT_INFO_TABLE = 0x006D3718
PRINT_INFO_TABLE_SHA256 = "d1134ec65af98c0d6f2826f9cfe5086f4f0296e154c86fa3437db46e9375a9e0"
PRINT_INFO = (
    (0x006DA1C4, "ERROR: Unable to get the main stack information, please check the configuration of the main stack"),
    (0x007099A4, "Firmware name: %s, hardware version: %s, software version: %s"),
    (0x0077E8C0, "Assert on thread %s"),
    (0x0071C700, "Assert on interrupt or bare metal(no OS) environment"),
    (0x007481EC, "===== Thread stack information ====="),
    (0x00748214, "====== Main stack information ======"),
    (0x0074823C, "Error: Thread stack(%08x) was overflow"),
    (0x00748264, "Error: Main stack(%08x) was overflow"),
    (
        0x0069E9FC,
        "Show more call stack info by run: "
        "third_party/CmBacktrace/tools/addr2line/win64/addr2line.exe "
        "-e %s%s -afpiC %.*s",
    ),
    (0x0075E650, "Dump call stack has an error"),
    (0x0077E8D4, "Fault on thread %s"),
    (0x007274A4, "Fault on interrupt or bare metal(no OS) environment"),
    (0x007099E4, "=================== Registers information ===================="),
    (0x0073C8A4, "Hard fault is caused by failed vector fetch"),
    (0x00700AB8, "Memory management fault is caused by instruction access violation"),
    (0x00712B2C, "Memory management fault is caused by data access violation"),
    (0x0071C738, "Memory management fault is caused by unstacking error"),
    (0x007274D8, "Memory management fault is caused by stacking error"),
    (0x006F1D58, "Memory management fault is caused by floating-point lazy state preservation"),
    (0x0072750C, "Bus fault is caused by instruction access violation"),
    (0x0071C770, "Bus fault is caused by precise data access violation"),
    (0x0071C7A8, "Bus fault is caused by imprecise data access violation"),
    (0x0074828C, "Bus fault is caused by unstacking error"),
    (0x007482B4, "Bus fault is caused by stacking error"),
    (0x00709A24, "Bus fault is caused by floating-point lazy state preservation"),
    (0x006F89E4, "Usage fault is caused by attempts to execute an undefined instruction"),
    (0x006F1DA4, "Usage fault is caused by attempts to switch to an invalid state (e.g., ARM)"),
    (0x006DCBD4, "Usage fault is caused by attempts to do an exception with a bad value in the EXC_RETURN number"),
    (0x006F8A2C, "Usage fault is caused by attempts to execute a coprocessor instruction"),
    (0x006DF8E0, "Usage fault is caused by indicates that a stack overflow (hardware check) has taken place"),
    (0x006E67C0, "Usage fault is caused by indicates that an unaligned access fault has taken place"),
    (0x006A7B24, "Usage fault is caused by Indicates a divide by zero has taken place (can be set only if DIV_0_TRP is set)"),
    (0x00731EA4, "Debug fault is caused by halt requested in NVIC"),
    (0x00727540, "Debug fault is caused by BKPT instruction executed"),
    (0x0073C8D0, "Debug fault is caused by DWT match occurred"),
    (0x00731ED4, "Debug fault is caused by Vector fetch occurred"),
    (0x00731F04, "Debug fault is caused by EDBGRQ signal asserted"),
    (0x0071C7E0, "The memory management fault occurred address is %08x"),
    (0x007482DC, "The bus fault occurred address is %08x"),
)

UPSTREAM_CALL_STACK_FORMAT = (
    "Show more call stack info by run: addr2line -e %s%s -afpiC %.*s"
)
VENDOR_ADDR2LINE_PREFIX = "third_party/CmBacktrace/tools/addr2line/win64/addr2line.exe "

STRING_PINS = {
    0x0078D184: ".out",
    0x0078D17C: "%08lx",
    0x0078D18C: "init_ok",
    0x0078A5F8: "start_addr",
    0x0078D174: "size",
    0x0076A08C: "get_cur_thread_stack_info",
    0x0077E8E8: "cm_backtrace_fault",
    0x006F8B04: "stack_pointer: 0x%08x, stack_start_addr: 0x%08x, stack_end_addr: 0x%08x",
}

# Exact bodies are used instead of loose opcode searches.  Besides protecting
# every recovered literal/call claim, this makes the negative alignment-fix
# finding fail closed if the official image is replaced.
PINNED_BODIES = {
    "cm_backtrace_init": (
        0x005939AE,
        0x00593A38,
        "93eff95cb05fe0c6ae3cf21949ca56c5bad9a589e39ac110f5aa6eca96e0a696",
    ),
    "cm_backtrace_firmware_info": (
        0x00593A38,
        0x00593A78,
        "5c890cff244941ec303187ea779dd7063bdf5610c2812e0c4b2840f7ab7bb21b",
    ),
    "get_cur_thread_stack_info": (
        0x00593A78,
        0x00593AF6,
        "7ea939f6da1775890734fb9bfaf42c018ddb21a4687f2660e0aeac19ca201125",
    ),
    "get_cur_thread_name": (
        0x00593AF6,
        0x00593AFE,
        "75f860b4a8f7d60464eeb5216946dbefe0875c65fb0c7a6641abdd9f9daa979b",
    ),
    "dump_stack": (
        0x00593AFE,
        0x00593C34,
        "cc4c4017f27aa0ac2a0a64af7fc1cd51de560cdef6051a1b85c57daa8ce4fea6",
    ),
    "print_call_stack": (
        0x00593D4A,
        0x00593E0C,
        "7c27c35c89f1a9d410c75470202ce6a95616429362cdf1b913ca01201b36a905",
    ),
    "cm_backtrace_fault": (
        0x005944BC,
        0x005947CE,
        "741e40d38b66bc5047db4744604c4ea9e7d2a06cf29ebedf1d10cfe7314061e5",
    ),
}

# The first window is the complete FreeRTOS adapter: current TCB +0x30 is the
# stack base, +0x54 is the depth (scaled by sizeof(StackType_t)==4), and +0x34
# is the task name.  The second is the post-FPU-adjust path.  It proceeds
# directly to bounds checking and has no saved xPSR bit-9 test/add-four from
# upstream 55e7b69.
FREERTOS_ADAPTER = (
    0x0045601E,
    bytes.fromhex("0f480068006b70470d480068406d70470b48006834307047"),
)
PRE_ALIGNMENT_PATH = (
    0x005945F0,
    bytes.fromhex("203631002800fff758fe05000598854204d3059906984118a94219d2"),
)

INIT_CALLER = (
    0x005CDD58,
    bytes.fromhex("dff8e423 dff8e413 dff8e403 c5f723fe"),
)
INIT_ARGUMENTS = {
    "firmware_name": (0x0074B194, "product/s200/app/Release/Exe/s200_app"),
    "hardware_version": (0x0078DC9C, "V1.0.0"),
    "software_version": (0x0078B57C, "2.2.6.10"),
}
INIT_ARGUMENT_POINTERS = {
    0x005CE140: INIT_ARGUMENTS["software_version"][0],
    0x005CE144: INIT_ARGUMENTS["hardware_version"][0],
    0x005CE148: INIT_ARGUMENTS["firmware_name"][0],
}
INIT_LINKER_LITERALS = {
    0x00594314: 0x2007D000,
    0x0059431C: 0x20080000,
    0x00594324: 0x00438400,
    0x00594328: 0x005FA056,
}
INIT_NAME_BUFFER_LITERALS = {
    0x00594304: 0x2007351C,
    0x00594308: 0x20073548,
    0x0059430C: 0x20073574,
}
OTHER_POINTER_PINS = {
    0x0045605C: 0x20074A20,  # pxCurrentTCB used by all three adapters
    0x005947C0: 0x0078D184,  # print_call_stack CMB_ELF_FILE_EXTENSION_NAME
}

# These are content hashes from the official armink/CmBacktrace Git
# repository, retrieved from Git objects (not GitHub-rendered pages).  Both
# boundary commits retain the MIT LICENSE blob.  Files that changed inside
# the interval did so only in branches compiled out by this FreeRTOS/English
# configuration; therefore those commits are not distinguishable in G2 code.
UPSTREAM = {
    "repository": "https://github.com/armink/CmBacktrace.git",
    "license": "MIT",
    "license_sha256": "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e",
    "tag_before": {
        "name": "1.4.1",
        "commit": "a8973df098d60f7572e839d7456b69e3c2fcf4f9",
        "tree": "711ed6fe132ca92865d9da19fafeecb250b8e19b",
        "advertised_version": "1.4.1",
    },
    "compatible_floor": {
        "commit": "4abadfa0c4f86f22352aa5ab9ebbb4f687125a1c",
        "tree": "545881132a4e538d53f260876d295896674bf541",
        "date": "2023-08-20",
        "advertised_version": "1.4.2",
        "files": {
            "LICENSE": "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e",
            "cm_backtrace/cm_backtrace.c": "b13da2eb10c26bff3e81628f44fd70b6b3f3d2e2b33ef29d014400a64c44e81e",
            "cm_backtrace/cmb_def.h": "34c2b4e0d481404431ba444679f2638051674ca470c8235d5b42cc8b3062d548",
            "cm_backtrace/Languages/en-US/cmb_en_US.h": "ad77299fecaa9a63c766bfbe9d17099c7542751fc11084bf88520bc88c35a844",
        },
    },
    "compatible_ceiling": {
        "commit": "73714489f9d8af130aacb515586b397b604a5768",
        "tree": "541c20dbeb1165f9b2862e2b84cdc63b3d7c718f",
        "date": "2024-07-03",
        "advertised_version": "1.4.2",
        "files": {
            "LICENSE": "e8ed0e84184d2130bd1fcf5a52ce8c16b5bf338c272cab6bbd7993a9d723934e",
            "cm_backtrace/cm_backtrace.c": "6e444224af3ef223067849b88f61281ec0661e3f38425e84758bf12be057e01c",
            "cm_backtrace/cmb_def.h": "897c0818d0e062866edecb467e655d5b02494d7ee1612b036035be08809e75eb",
            "cm_backtrace/Languages/en-US/cmb_en_US.h": "ad77299fecaa9a63c766bfbe9d17099c7542751fc11084bf88520bc88c35a844",
        },
    },
    "first_incompatible_fix": {
        "commit": "55e7b6990640c481e83ae8a3c0f3af2092b9f7a6",
        "tree": "2786177dc0749d4da09ba1ca7e09048f261e75bc",
        "date": "2025-02-18",
        "change": "adds stacked xPSR bit-9 exception-stack realignment handling",
        "cm_backtrace_c_sha256": "bcb65ad69068b3bc17d7b2f70fdd6096656442605605ccfe9c619876e98fca0e",
    },
    "tag_after": {
        "name": "1.5.0",
        "commit": "3be35d99673805f258de5c2f156fac94eb896da4",
        "tree": "7a1120f8d06491c163878c168d1d5aa4e5d9b23f",
        "advertised_version": "1.5.0",
    },
}


def _slice(data: bytes, start: int, end: int) -> bytes:
    first = start - LOAD_BASE
    last = end - LOAD_BASE
    if first < 0 or last < first or last > len(data):
        raise AuditError(f"run span 0x{start:08x}..0x{end:08x} is outside image")
    return data[first:last]


def _u32(data: bytes, run: int) -> int:
    return struct.unpack("<I", _slice(data, run, run + 4))[0]


def _cstr(data: bytes, run: int, limit: int = 256) -> str:
    raw = _slice(data, run, min(run + limit, LOAD_BASE + len(data)))
    end = raw.find(b"\0")
    if end < 0:
        raise AuditError(f"unterminated string at 0x{run:08x}")
    try:
        return raw[:end].decode("ascii")
    except UnicodeDecodeError as exc:
        raise AuditError(f"non-ASCII string at 0x{run:08x}") from exc


def _load() -> bytes:
    data = MAIN.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != MAIN_SHA256:
        raise AuditError(f"official Apollo-main SHA-256 drift: {got}")
    return data


def audit(data: bytes) -> dict[str, Any]:
    """Verify pinned evidence and return only claims supported by it."""

    table = _slice(data, PRINT_INFO_TABLE, PRINT_INFO_TABLE + 4 * len(PRINT_INFO))
    got_table_sha = hashlib.sha256(table).hexdigest()
    if got_table_sha != PRINT_INFO_TABLE_SHA256:
        raise AuditError(f"print_info pointer-table SHA-256 drift: {got_table_sha}")

    for index, (expected_pointer, expected_text) in enumerate(PRINT_INFO):
        pointer = _u32(data, PRINT_INFO_TABLE + index * 4)
        if pointer != expected_pointer:
            raise AuditError(
                f"print_info[{index}] pointer: expected 0x{expected_pointer:08x}, "
                f"got 0x{pointer:08x}"
            )
        text = _cstr(data, pointer, max(256, len(expected_text) + 1))
        if text != expected_text:
            raise AuditError(f"print_info[{index}] text drift: {text!r}")

    for run, expected in STRING_PINS.items():
        got = _cstr(data, run, max(128, len(expected) + 1))
        if got != expected:
            raise AuditError(f"string at 0x{run:08x}: expected {expected!r}, got {got!r}")

    body_findings: dict[str, dict[str, Any]] = {}
    for name, (start, end, expected_sha) in PINNED_BODIES.items():
        got = hashlib.sha256(_slice(data, start, end)).hexdigest()
        if got != expected_sha:
            raise AuditError(f"{name} SHA-256 drift: {got}")
        body_findings[name] = {
            "start": start,
            "end": end,
            "size": end - start,
            "sha256": got,
        }

    for label, (run, expected) in {
        "FreeRTOS adapter": FREERTOS_ADAPTER,
        "pre-alignment path": PRE_ALIGNMENT_PATH,
        "init caller": INIT_CALLER,
    }.items():
        got = _slice(data, run, run + len(expected))
        if got != expected:
            raise AuditError(f"{label} encoding drift at 0x{run:08x}")

    init_arguments: dict[str, dict[str, Any]] = {}
    for role, (run, expected) in INIT_ARGUMENTS.items():
        got = _cstr(data, run, max(128, len(expected) + 1))
        if got != expected:
            raise AuditError(f"CmBacktrace {role} string drift: {got!r}")
        init_arguments[role] = {"address": run, "value": got}

    for run, expected in {
        **INIT_ARGUMENT_POINTERS,
        **INIT_LINKER_LITERALS,
        **INIT_NAME_BUFFER_LITERALS,
        **OTHER_POINTER_PINS,
    }.items():
        got = _u32(data, run)
        if got != expected:
            raise AuditError(
                f"pointer/literal at 0x{run:08x}: expected 0x{expected:08x}, "
                f"got 0x{got:08x}"
            )

    vendor_format = PRINT_INFO[8][1]
    normalized_format = vendor_format.replace(VENDOR_ADDR2LINE_PREFIX, "addr2line ", 1)
    if normalized_format != UPSTREAM_CALL_STACK_FORMAT:
        raise AuditError("vendor addr2line format no longer normalizes to upstream")

    return {
        "component": "armink/CmBacktrace",
        "image_sha256": MAIN_SHA256,
        "identity": {
            "definitive": True,
            "print_info_table": PRINT_INFO_TABLE,
            "print_info_entries": len(PRINT_INFO),
            "fault_entry": PINNED_BODIES["cm_backtrace_fault"][0],
            "vendor_addr2line_path": VENDOR_ADDR2LINE_PREFIX.rstrip(),
        },
        "version_recovery": {
            "exact_release_or_commit": None,
            "classification": "untagged post-1.4.1 1.4.2-development lineage",
            "compatible_unmodified_upstream_interval": {
                "first": UPSTREAM["compatible_floor"]["commit"],
                "last": UPSTREAM["compatible_ceiling"]["commit"],
                "first_date": UPSTREAM["compatible_floor"]["date"],
                "last_date": UPSTREAM["compatible_ceiling"]["date"],
            },
            "lower_bound_evidence": [
                "-afpiC %.*s addr2line format",
                "CMB_CALL_STACK_MAX_DEPTH=32",
                "CMB_DUMP_STACK_DEPTH_SIZE=16",
                "CMB_NAME_MAX+1 storage layout",
            ],
            "upper_bound_evidence": (
                "cm_backtrace_fault proceeds directly from FPU-frame adjustment "
                "to stack bounds checking; upstream 55e7b69 xPSR bit-9 "
                "realignment handling is absent"
            ),
            "why_not_exact": (
                "intervening upstream changes affect RT-Thread, RTX5, ThreadX, "
                "custom-language selection, user-config inclusion, or GHS assembly; "
                "they are compiled out or byte-silent for the recovered "
                "FreeRTOS/English/IAR configuration"
            ),
            "fork_caveat": (
                "a vendor fork can cherry-pick or omit upstream changes, so the "
                "interval bounds compatible unmodified upstream states, not the "
                "unknown vendor-fork checkout date"
            ),
        },
        "effective_configuration": {
            "CMB_USING_OS_PLATFORM": True,
            "CMB_OS_PLATFORM_TYPE": "CMB_OS_PLATFORM_FREERTOS",
            "CMB_USING_DUMP_STACK_INFO": True,
            "CMB_CALL_STACK_MAX_DEPTH": 32,
            "CMB_DUMP_STACK_DEPTH_SIZE": 16,
            "CMB_NAME_MAX": 40,
            "name_buffers": [0x2007351C, 0x20073548, 0x20073574],
            "CMB_PRINT_LANGUAGE_CONTENT": "English (upstream en-US plus vendor addr2line path)",
            "CMB_PRINT_LANGUAGE_MACRO": "English or vendor custom-English is not distinguishable",
            "CMB_CPU_PLATFORM_BEHAVIOR": "M33-class fault map with STKOF and FPU-frame handling",
            "CMB_CPU_PLATFORM_TYPE": "likely CMB_CPU_ARM_CORTEX_M33; vendor M55 alias cannot be excluded",
            "compiler": "IAR (__ICCARM__ branch; .out ELF extension)",
            "sizeof_StackType_t": 4,
            "main_stack_start": 0x2007D000,
            "main_stack_size": 0x3000,
            "code_start": 0x00438400,
            "code_size": 0x1C1C56,
        },
        "freertos_adapter": {
            "current_tcb_pointer": 0x20074A20,
            "stack_base_offset": 0x30,
            "stack_depth_offset": 0x54,
            "task_name_offset": 0x34,
            "entries": {
                "vTaskStackAddr": 0x0045601F,
                "vTaskStackSize": 0x00456027,
                "vTaskName": 0x0045602F,
            },
        },
        "init_arguments": init_arguments,
        "pinned_bodies": body_findings,
        "upstream_provenance": UPSTREAM,
        "license_correction": (
            "CmBacktrace upstream LICENSE is MIT; do not reuse the earlier "
            "openCFW Apache-2.0 classification"
        ),
        "open_questions": [
            "the exact vendor-fork commit within the compatible upstream interval",
            "whether CMB_PRINT_LANGUAGE_ENGLISH was patched or the custom-English selector was used",
            "whether the M55 build used the upstream M33 selector or a vendor-added M55 alias",
        ],
        "analysis_mode": "read-only; no hardware or flash operation",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable findings")
    args = parser.parse_args(argv)
    findings = audit(_load())
    if args.json:
        print(json.dumps(findings, indent=2, sort_keys=True))
        return 0

    interval = findings["version_recovery"]["compatible_unmodified_upstream_interval"]
    config = findings["effective_configuration"]
    print("CmBacktrace identity/version/config audit: OK")
    print(f"version: {findings['version_recovery']['classification']}")
    print(f"compatible unmodified upstream: {interval['first'][:8]}..{interval['last'][:8]}")
    print(
        "configuration: FreeRTOS + dump-stack; IAR .out; "
        f"call/dump/name limits={config['CMB_CALL_STACK_MAX_DEPTH']}/"
        f"{config['CMB_DUMP_STACK_DEPTH_SIZE']}/{config['CMB_NAME_MAX']}"
    )
    print("license: MIT (corrects the earlier Apache-2.0 classification)")
    print("analysis mode: read-only; no device or flash operation performed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
