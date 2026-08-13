#!/usr/bin/env python3
"""Fail-closed linked-object and provider audit for G2 logger_setting.c."""
from __future__ import annotations

import csv
import hashlib
import json
import re
import struct
import sys
from collections import Counter
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_THUMB, Cs
from capstone.arm import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-logger-setting-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-logger-setting-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-logger-setting-provider-map.tsv"
INPUT_PINS = {
    FUNCTION_MAP: "59a895ca1e293475bb8a1d44ac10a33b57950611ce4945d54132719aafd35d95",
    CLOSURE: "c05b48be508127814baee8b777cea675d17f50ae1f92a36a6839fdf301225d62",
    PROVIDER_MAP: "25794f6c1899cdefd9b884a59300178c34137a8b1a3696adae8197e1cbe3b94c",
}

RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\logger\logger_setting.c"
PATH_RUN = 0x0070_34F4
PATH_POINTER_CELLS = [0x0045_9278, 0x0045_9F94, 0x0045_A4E4]

PHYSICAL = (0x0045_8DF0, 0x0045_A558)
PHYSICAL_BYTES = 5_992
PHYSICAL_SHA256 = "3bb1f02fa548eead3235c46e7727d88d6f9b47252779a7d1e2bb51a5c5190969"
BODY_BYTES = 5_574
BODY_SHA256 = "446ba4d86693170117a537cf7d2b5ddcd72d7cc10135707525f4b62892d44c5e"
REACHABLE_INSTRUCTION_COUNT = 2_015
REACHABLE_CODE_BYTES = 5_466
REACHABLE_CODE_SHA256 = "500bbeaa542babf37865c88dc23bd4ba19bafba459cb9bdedc52bba93cb051a5"
REACHABLE_INSTRUCTION_DIGEST = "e0930a508bf9963120bb2d9c3b058e9f9903a7a9470b040575f0b58a76797adf"

OUTER_POOL_REGIONS = 4
OUTER_POOL_BYTES = 418
OUTER_POOL_SHA256 = "f4feebd6cff026a178bb68a3269f76be6929b2d8bef17e5738553fa60370efab"
EMBEDDED_DATA = [
    (0x0045_91FA, 0x0045_9204),
    (0x0045_9D58, 0x0045_9D60),
    (0x0045_9F8A, 0x0045_9FA4),
    (0x0045_A05A, 0x0045_A074),
    (0x0045_A162, 0x0045_A16C),
    (0x0045_A1C8, 0x0045_A1D0),
    (0x0045_A256, 0x0045_A260),
    (0x0045_A2A6, 0x0045_A2B0),
]
EMBEDDED_DATA_BYTES = 108
EMBEDDED_DATA_SHA256 = "300c5fda85a51250cf37875659080244623140d776006c12d6a4f62fb784be89"

PRECEDING_FUNCTION = (0x0045_8C5E, 0x0045_8D34)
PRECEDING_FUNCTION_SHA256 = "fc22c145cde805453522f42a9ffefa2e1c54b61f107801f18d95b0f962159b4c"
PRECEDING_POOL = (0x0045_8D34, 0x0045_8DF0)
PRECEDING_POOL_SHA256 = "99f99a6a82eefc904fab21473dc9f0e76387b444ad4dad36c8ed808a7e852ecb"
FOLLOWING_FUNCTION = (0x0045_A558, 0x0045_A568)
FOLLOWING_FUNCTION_SHA256 = "38883eb2a0a2fd4563b9ee85a8a44a873148a9c1f20a937333341fed85461f57"

ENTRY_COUNT = 9
EXTERNAL_ENTRY_COUNT = 1
ENTRY_SHA256 = "6517080a3273e84ed0742d96bc5c9cd96cdf4ffaf00d439ea946f84480bff8ab"
BODY_CALL_COUNT = 346
INTERNAL_BODY_CALL_COUNT = 8
BODY_CALL_SHA256 = "4ea40748594a0aa8d345d0c00c86a08394f446b10ea9fd2fba7cafb8882986b6"
STORED = [(0x006A_4564, 0x0045_92DD)]
STORED_SHA256 = "5b69c9e77ac676ec761e208611adb89eb6d9105160ba8c3aa86d94d05868c746"

EXTERNAL_TARGET_COUNTS = {
    0x0043_9BE4: 1, 0x0043_9C04: 8, 0x0043_C0E4: 13,
    0x0043_CE9E: 50, 0x0043_CF8C: 1, 0x0043_D0CE: 150,
    0x0043_D0D4: 1, 0x0043_D3A6: 1, 0x0043_D574: 50,
    0x0044_8CB8: 2, 0x0044_B5A0: 3, 0x0044_B610: 2,
    0x0044_B728: 5, 0x0045_4B4C: 1, 0x0045_A568: 6,
    0x0046_5480: 2, 0x0046_CACC: 6, 0x0047_4550: 1,
    0x0047_45F4: 1, 0x0047_4814: 1, 0x0047_4870: 1,
    0x0047_498C: 2, 0x0047_4B02: 2, 0x0047_4BB8: 2,
    0x0047_4C66: 2, 0x0047_5B14: 6, 0x0047_5FC0: 1,
    0x0047_8110: 1, 0x0048_F49C: 2, 0x0049_0120: 2,
    0x0049_05F4: 6, 0x0049_0C32: 6,
}

STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0045_904C: "r",
    0x0045_91FC: ".",
    0x0045_9200: "..",
    0x0075_4FE0: "loggerSetting_cancel_ble_transmit",
    0x0077_7DBC: "delete_all_files_in_dir",
    0x0078_6230: "scan_log_files",
    0x0075_5070: "loggerSetting_common_data_handler",
    0x0077_7DEC: "simplify_log_filename",
    0x0078_D81C: "/log",
    0x0077_7DD4: "compress_manager.bin",
    0x0078_D834: "L:/log/",
    0x0078_D83C: "R:/log/",
    0x0077_F93C: "compress_log_%d.bin",
    0x0078_D844: "%c:%d",
    0x0078_6240: "hardfault.txt",
    0x0078_D84C: "%c:h",
}


class AuditError(RuntimeError):
    """Raised when authenticated evidence or the closed object changes."""


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _slice(blob: bytes, start: int, end: int) -> bytes:
    first, last = start - BASE, end - BASE
    if first < 0 or last > len(blob) or first > last:
        raise AuditError(f"invalid image interval [0x{start:08x},0x{end:08x})")
    return blob[first:last]


def _pair_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<II", *pair) for pair in pairs))


def _instruction_digest(pairs: list[tuple[int, int]]) -> str:
    return _sha256(b"".join(struct.pack("<IH", *pair) for pair in pairs))


def _c_string(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _validate_provider_pins() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger provider commit changed")
    nanopb = json.loads((ROOT / "third_party/nanopb/PROVENANCE.json").read_text())
    if nanopb["upstream"]["selected_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824":
        raise AuditError("nanopb compatibility commit changed")
    if nanopb["selection"]["exact_g2_point_release_proven"]:
        raise AuditError("nanopb exact-point-release qualification changed")
    littlefs = json.loads((ROOT / "third_party/littlefs/PROVENANCE.json").read_text())
    if littlefs["upstream"]["selected_commit"] != "0494ce7169f06a734a7bd7585f49a9fa91fa7318":
        raise AuditError("littlefs source-equivalent commit changed")
    freertos = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if freertos["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise AuditError("FreeRTOS-Kernel provider commit changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    for marker in ("9.20 is therefore a practical lower bound", "9.60.2", "Exact EWARM/ICCARM release"):
        if marker not in iar:
            raise AuditError("IAR family-level provenance assessment changed")


def _recover_function(
    blob: bytes, start: int, end: int, all_starts: set[int]
) -> tuple[dict[int, object], list[tuple[int, int]]]:
    decoder = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN)
    decoder.detail = True
    pending = [start]
    seen: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    while pending:
        address = pending.pop()
        if address in seen:
            continue
        if not start <= address < end:
            raise AuditError(f"control flow escaped function at 0x{address:08x}")
        decoded = list(decoder.disasm(_slice(blob, address, min(address + 4, end)), address, count=1))
        if not decoded:
            raise AuditError(f"Thumb decode failed at 0x{address:08x}")
        instruction = decoded[0]
        if address + instruction.size > end:
            raise AuditError(f"instruction crosses function end at 0x{address:08x}")
        seen[address] = instruction
        following = address + instruction.size
        mnemonic = instruction.mnemonic

        if mnemonic in ("bl", "blx"):
            if not instruction.operands or instruction.operands[0].type != ARM_OP_IMM:
                raise AuditError(f"indirect call inside recovered object at 0x{address:08x}")
            calls.append((address, instruction.operands[0].imm))
            pending.append(following)
            continue
        if (mnemonic.startswith("pop") and "pc" in instruction.op_str) or mnemonic in ("bx", "bxj"):
            continue
        if mnemonic.startswith("ldr") and instruction.op_str.startswith("pc,"):
            continue
        if mnemonic in ("tbb", "tbh"):
            raise AuditError(f"unclosed jump table at 0x{address:08x}")
        if mnemonic in ("cbz", "cbnz"):
            pending.extend((following, instruction.operands[-1].imm))
            continue
        is_branch = mnemonic in ("b", "b.w") or (
            mnemonic.startswith("b") and mnemonic not in ("bic", "bfi", "bfc", "bl", "blx")
        )
        if is_branch:
            if not instruction.operands or instruction.operands[0].type != ARM_OP_IMM:
                raise AuditError(f"unresolved branch at 0x{address:08x}")
            pending.append(instruction.operands[0].imm)
            if mnemonic not in ("b", "b.w"):
                pending.append(following)
            continue
        pending.append(following)
    return seen, calls


def _uncovered(interval: tuple[int, int], instructions: dict[int, object]) -> list[tuple[int, int]]:
    covered: set[int] = set()
    for address, instruction in instructions.items():
        covered.update(range(address, address + instruction.size))
    result: list[tuple[int, int]] = []
    cursor, end = interval
    while cursor < end:
        if cursor in covered:
            cursor += 1
            continue
        gap_end = cursor + 1
        while gap_end < end and gap_end not in covered:
            gap_end += 1
        result.append((cursor, gap_end))
        cursor = gap_end
    return result


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != IMAGE_SIZE or _sha256(blob) != IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    _validate_provider_pins()

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        provider_rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 8 or len(provider_rows) != 8:
        raise AuditError("function or provider inventory changed")
    provider_edges = sum(int(re.match(r"(\d+)", row["edges"]).group(1)) for row in provider_rows)
    if provider_edges != sum(EXTERNAL_TARGET_COUNTS.values()):
        raise AuditError("provider edge accounting changed")

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    outer_gaps: list[bytes] = []
    anchored = 0
    previous_end = PHYSICAL[0]
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if start in starts or start < previous_end or start >= end:
            raise AuditError(f"invalid or overlapping function at 0x{start:08x}")
        if previous_end < start:
            outer_gaps.append(_slice(blob, previous_end, start))
        body = _slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(body)
        anchored += row["source_path_anchor"] == "yes"
        previous_end = end
    if previous_end < PHYSICAL[1]:
        outer_gaps.append(_slice(blob, previous_end, PHYSICAL[1]))
    if intervals[0][0] != PHYSICAL[0] or anchored != 2:
        raise AuditError("object start or path-anchor census changed")
    if sum(map(len, bodies)) != BODY_BYTES or _sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("function-body inventory changed")
    if (
        len(outer_gaps) != OUTER_POOL_REGIONS
        or sum(map(len, outer_gaps)) != OUTER_POOL_BYTES
        or _sha256(b"".join(outer_gaps)) != OUTER_POOL_SHA256
    ):
        raise AuditError("outer compiler-pool inventory changed")
    if len(_slice(blob, *PHYSICAL)) != PHYSICAL_BYTES or _sha256(_slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical logger-settings object changed")
    for bounds, expected, label in (
        (PRECEDING_FUNCTION, PRECEDING_FUNCTION_SHA256, "preceding EFS function"),
        (PRECEDING_POOL, PRECEDING_POOL_SHA256, "preceding EFS pool"),
        (FOLLOWING_FUNCTION, FOLLOWING_FUNCTION_SHA256, "following role-state function"),
    ):
        if _sha256(_slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} boundary changed")

    all_instructions: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    embedded: list[tuple[int, int]] = []
    for interval in intervals:
        recovered, function_calls = _recover_function(blob, *interval, starts)
        if set(recovered).intersection(all_instructions):
            raise AuditError("recursive instruction inventories overlap")
        all_instructions.update(recovered)
        calls.extend(function_calls)
        embedded.extend(_uncovered(interval, recovered))
    instruction_pairs = sorted((address, instruction.size) for address, instruction in all_instructions.items())
    code = b"".join(
        _slice(blob, address, address + instruction.size)
        for address, instruction in sorted(all_instructions.items())
    )
    if (
        len(all_instructions) != REACHABLE_INSTRUCTION_COUNT
        or _instruction_digest(instruction_pairs) != REACHABLE_INSTRUCTION_DIGEST
        or len(code) != REACHABLE_CODE_BYTES
        or _sha256(code) != REACHABLE_CODE_SHA256
    ):
        raise AuditError("recursive reachable-instruction closure changed")
    if embedded != EMBEDDED_DATA:
        raise AuditError(f"embedded compiler-data layout changed: {embedded!r}")
    embedded_bytes = b"".join(_slice(blob, *bounds) for bounds in embedded)
    if len(embedded_bytes) != EMBEDDED_DATA_BYTES or _sha256(embedded_bytes) != EMBEDDED_DATA_SHA256:
        raise AuditError("embedded compiler-data bytes changed")
    calls.sort()
    if len(calls) != BODY_CALL_COUNT or _pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("reachable body-call topology changed")
    if sum(target in starts for _, target in calls) != INTERNAL_BODY_CALL_COUNT:
        raise AuditError("internal body-call census changed")
    external_counts = Counter(target for _, target in calls if target not in starts)
    if dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError(f"provider target accounting changed: {external_counts!r}")

    for address, expected in STRINGS.items():
        if _c_string(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    path_hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        path_hits.append(BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if path_hits != PATH_POINTER_CELLS:
        raise AuditError(f"source-path pointer topology changed: {path_hits!r}")

    sys.path.insert(0, str(ROOT / "tools"))
    import recover_apollo_embedded_source_paths as thumb

    entries: list[tuple[int, int]] = []
    strict: list[tuple[int, int]] = []
    unknown: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = thumb._thumb_bl_target(blob, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            strict.append((site, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            unknown.append((site, target))
    if len(entries) != ENTRY_COUNT or _pair_digest(entries) != ENTRY_SHA256:
        raise AuditError("direct entry topology changed")
    external_entries = sum(not (PHYSICAL[0] <= site < PHYSICAL[1]) for site, _ in entries)
    if external_entries != EXTERNAL_ENTRY_COUNT or strict or unknown:
        raise AuditError("entry/interior closure changed")

    encoded_starts = starts | {start | 1 for start in starts}
    stored: list[tuple[int, int]] = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_starts:
            stored.append((BASE + offset, value))
    if stored != STORED or _pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored callback topology changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = "logger_setting" in json.dumps(overlay).lower()
    if routed:
        raise AuditError("logger settings unexpectedly became production-routed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; fail-closed linked-object and provider audit",
        "image": {"size": len(blob), "sha256": _sha256(blob)},
        "identity": {
            "retained_path": RETAINED_PATH,
            "ownership": "g2_local_logger_file_protocol_and_routing_policy",
            "historical_source_available": False,
            "private_producing_commit_observable": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": len(rows),
            "ghidra_discovered_functions": 3,
            "path_anchored_functions": anchored,
            "baseline_ghidra_path_anchors": 1,
            "additional_recovered_functions": 5,
            "body_bytes": sum(map(len, bodies)),
            "reachable_instruction_bytes": len(code),
            "embedded_data_regions": len(embedded),
            "embedded_data_bytes": len(embedded_bytes),
            "outer_pool_regions": len(outer_gaps),
            "outer_pool_bytes": sum(map(len, outer_gaps)),
            "physical_bytes": PHYSICAL_BYTES,
            "direct_bl_entry_sites": len(entries),
            "external_direct_bl_entry_sites": external_entries,
            "direct_body_calls": len(calls),
            "internal_direct_body_calls": INTERNAL_BODY_CALL_COUNT,
            "external_direct_body_calls": len(calls) - INTERNAL_BODY_CALL_COUNT,
            "stored_entry_pointers": len(stored),
            "strict_interior_raw_bl_decodes": len(strict),
            "unrecovered_direct_object_targets": len(unknown),
        },
        "behavior": {
            "directory": "/log",
            "maximum_file_entries": 20,
            "file_record_bytes": 40,
            "excluded_file": "compress_manager.bin",
            "phone_command_ids": {
                "0": "connect heartbeat",
                "1": "BLE logger switch",
                "2": "BLE logger level",
                "4": "request file list",
                "5": "delete one file",
                "6": "delete all files",
            },
            "peer_event_ids": {"0x0B": "slave file list", "0x0C": "slave delete result"},
            "accepted_delete_prefixes": ["L:/log/", "R:/log/"],
            "simplified_names": ["<role>:<compress index>", "<role>:h"],
            "role_and_phone_forwarding": True,
        },
        "provider_boundary": {
            "provider_rows": len(provider_rows),
            "direct_external_targets": len(external_counts),
            "direct_external_calls": sum(external_counts.values()),
            "easylogger": {
                "version": "2.2.99 source-equivalent core",
                "selected_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
                "diagnostic_calls": 250,
                "control_calls": 4,
            },
            "nanopb": {
                "compatible_release_range": "0.4.7..0.4.9.1",
                "selected_version": "0.4.9",
                "selected_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
                "exact_g2_point_release": None,
                "calls": 16,
            },
            "littlefs": {
                "selected_source_equivalent_version": "v2.10.1",
                "selected_commit": "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
                "direct_calls": 0,
                "wrapper_calls": 12,
                "exact_historical_checkout": None,
            },
            "freertos_kernel": {
                "version": "V10.5.1",
                "selected_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
                "calls": 1,
            },
            "iar_dlib": {
                "floor": "EWARM 9.20+",
                "leading_candidate": "9.60.2",
                "exact_release": None,
                "calls": 39,
                "new_version_discriminator": False,
            },
            "assessment": "all upstream relationships terminate at admitted provider seams; no opaque third-party definition is embedded",
        },
        "boundary": {
            "physical_start": f"0x{PHYSICAL[0]:08x}",
            "physical_end_exclusive": f"0x{PHYSICAL[1]:08x}",
            "path_pointer_cells": [f"0x{value:08x}" for value in PATH_POINTER_CELLS],
            "preceded_by": "EFS function and literal pool",
            "followed_by": "independent role-state function",
        },
        "production": {"candidate": None, "production_routed": routed, "ownership_bytes": 0},
        "limitations": [
            "the exact private G2 source and producing commit remain unavailable",
            "nanopb and littlefs commits are selected compatibility/source-equivalent baselines rather than proof of the private checkout",
            "the object adds no exact IAR release or archive discriminator",
            "production admission requires a clean-room LoggerDataPackage schema/policy implementation and target BLE/filesystem validation",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    print("G2 logger-settings audit: PASS")
