#!/usr/bin/env python3
# SPDX-License-Identifier: MIT

"""Solve the authenticated G2 CFF flash-capacity boundary without writing it.

The solver deliberately distinguishes bytes present in the current package
from bytes that could become dead only after a different, independently
guarded CFF registration route exists.  Conditional and scattered capacity is
reported as an optimistic upper bound, never as a writable placement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


G2 = Path(__file__).resolve().parents[1]
FLASH_PLAN = G2 / "build/flash-plan.json"
BUILD_REPORT = G2 / "build/build-report.json"
PACKAGE = G2 / "build/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
ARTIFACT_ROOT = G2 / "build"
CFF_MAP = G2 / "tools/manifests/g2-freetype-cff-function-map.json"
GHIDRA = G2 / "research/corpus/apollo-main/ghidra/decomp/functions.jsonl"
PLACEMENT = G2 / "tools/manifests/g2-freetype-cff-placement-link.json"
MANIFEST = G2 / "tools/manifests/g2-freetype-cff-capacity-solver.json"

PINS = {
    FLASH_PLAN: (4_490_259, "963c0cc5459a9d2ddbf522ab0b47cb03683f850334c910c9c68c92070d0a3c01"),
    BUILD_REPORT: (2_323, "4bdeb983c577698af8e8e90bd33374bf0cfdc0940c18e06ac86c4005eb6453e3"),
    PACKAGE: (4_739_498, "115c5ad73e32e308287034d1b1120f8ed576ec3c3c9294cafce1bfc561b727f9"),
    CFF_MAP: (70_973, "f16b49ec344534f7cea59ce0a41350fb44ac7c2991baf884ba6b9bc96a2b2641"),
    GHIDRA: (3_270_703, "9fd9c1c34e17abb977f2ccb32a931d9b96743db2db10707de19bf9ea6ae42662"),
    PLACEMENT: (37_673, "c8ff1ebfd687c6bbc546776c42e5f26bbba7517333a3801f043c054d15d1fd87"),
}

RUN_BASE = 0x00438000
PREAMBLE_BYTES = 32
CANDIDATE = (0x007ECA44, 0x007FE000)
PACKAGE_COMPONENT_HEADER_BYTES = 128
EXPECTED_APOLLO_ENTRY = {
    "entry_id": 6,
    "type_id": 0,
    "filename": "ota/s200_firmware_ota.bin",
    "storage_type": 3,
    "package_offset": 787_024,
    "package_offset_hex": "0x000C0250",
    "entry_size": 3_952_474,
    "payload_size": 3_952_346,
    "crc32c_msb": "0xCA5BB68B",
}
EXPECTED_BOOT_ENTRY = {
    "entry_id": 5,
    "type_id": 1,
    "filename": "ota/s200_bootloader.bin",
    "storage_type": 3,
    "package_offset": 628_976,
    "package_offset_hex": "0x000998F0",
    "entry_size": 158_048,
    "payload_size": 157_920,
    "crc32c_msb": "0x745D8D1E",
}
EXPECTED_APOLLO_PAYLOAD_SHA256 = (
    "dc578472f06af2d499b9cb771fc185df4f739a05de558098088b56da9a5e4ce0"
)
EXPECTED_BOOT_PAYLOAD_SHA256 = (
    "56350fb0fc8d663dc2202f11389573b52ddd30536e81f44539006f7810f2744d"
)
EXPECTED_FINAL_PAYLOADS = {"apple-clang": 26_794, "linux-clang": 26_726}
STOCK_CFF_ENVELOPE = (0x005ABEF8, 0x005B0114)
STOCK_CFF_ENVELOPE_SHA256 = (
    "58b8b5e4c1b801d7ac4c6883dc8afeccd7cf370e3e9cccdf95f938e20b91358b"
)

# Exact table words already authenticated by the complete CFF map.  Only the
# checked words, not adjacent structure bytes, enter the optimistic bound.
CFF_TABLE_INTERVALS = (
    (0x0074805C, 80, "cff-cmap-classes", "f6b60ed1a15fa9b024d58d8b5a51606a78b331d7b80024bf58df8620bd93e8ac"),
    (0x006DCB74, 96, "cff-driver-class", "df476f0f8f7344a32318751d94fed3094488ff1ac6472da99ca645bdb8e2c42b"),
    (0x0077E848, 40, "cff-ps-info-load-services", "74859def6db873480b3328675d6584d75349fe27dd834c28031e37de62aa3b3e"),
    (0x007480B0, 36, "cff-multiple-masters-service", "53a94660c02dbcb40aac6f4d84e4847a8884189e2ec552e2e276810e69fefcd9"),
    (0x0075E5AC, 36, "cff-metrics-variations-service", "f93785c473ee982aaee46b31338dd02062f47650863780b9e46747e863f188d2"),
)
CFF_CALLBACK_SLOTS = (
    0x005AC5EC, 0x0067F350, 0x0067F388, 0x0067F414, 0x0067F468,
    0x0067F484, 0x0067F7B0, 0x0067F83C, 0x0067F858, 0x0067F874,
    0x0067F9FC, 0x0067FA18, 0x0078A5EC, 0x0078A5F0, 0x0078A5F4,
    0x0078D144, 0x0078D148, 0x0078EEA0, 0x0078EEA4,
)
CFF_CALLBACK_SLOTS_SHA256 = (
    "856d98a69e0f19ab84b1908dbdf8c2ffbd62816b5aa0c059707cbae801803c74"
)


class CapacityError(RuntimeError):
    """Raised when capacity evidence or arithmetic drifts."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CapacityError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def payload_slice(payload: bytes, start: int, end: int) -> bytes:
    first = start - RUN_BASE + PREAMBLE_BYTES
    last = end - RUN_BASE + PREAMBLE_BYTES
    require(0 <= first <= last <= len(payload),
            f"Apollo payload interval unavailable: 0x{start:08X}..0x{end:08X}")
    return payload[first:last]


def family(region: str) -> str:
    value = region.split("_", 1)[0]
    require(value in {"ambiqsuite", "cordio", "iar", "s200", "service"},
            f"unclassified late-Apollo region family: {region}")
    return value


def validate_contiguous(rows: list[dict[str, Any]], start: int, end: int) -> None:
    cursor = start
    for row in rows:
        row_start = max(start, row["target_address"])
        row_end = min(end, row["end_exclusive"])
        if row_start >= row_end:
            continue
        require(row_start == cursor,
                f"unexpected free gap or overlap at 0x{cursor:08X}")
        cursor = row_end
    require(cursor == end, "late-Apollo occupied-span endpoint drift")


def minimal_live_rows(
    rows: list[dict[str, Any]], shortfall: int, start: int, end: int
) -> dict[str, Any]:
    candidates = []
    for row in rows:
        if row["address_status"] != "source_compiled":
            continue
        clipped = min(end, row["end_exclusive"]) - max(start, row["target_address"])
        if clipped > 0:
            candidates.append((clipped, row))
    candidates.sort(key=lambda pair: (-pair[0], pair[1]["target_address"]))
    selected: list[dict[str, Any]] = []
    total = 0
    for size, row in candidates:
        selected.append({
            "region": row["region"],
            "target_address": f"0x{row['target_address']:08X}",
            "bytes": size,
        })
        total += size
        if total >= shortfall:
            break
    require(total >= shortfall, "live-row shortfall cover disappeared")
    require(sum(item["bytes"] for item in selected[:-1]) < shortfall,
            "live-row lower-bound selection is not minimal by count")
    return {
        "minimum_distinct_live_source_rows_by_byte_capacity": len(selected),
        "selected_live_source_bytes": total,
        "shortfall_to_cover": shortfall,
        "rows": selected,
        "warning": (
            "these holes are noncontiguous; the count is only a byte-capacity "
            "lower bound and is not a placement plan"
        ),
    }


def contiguous_suffix_blocker(
    rows: list[dict[str, Any]], required: int, end: int
) -> dict[str, Any]:
    threshold = end - required
    suffix = [row for row in rows if row["end_exclusive"] > threshold]
    require(suffix, "contiguous suffix blocker disappeared")
    first = suffix[0]["target_address"]
    require(first == 0x007F7060 and len(suffix) == 171,
            "minimal whole-region suffix census drift")
    cursor = first
    for row in suffix:
        require(row["target_address"] == cursor,
                f"suffix region gap or overlap at 0x{cursor:08X}")
        cursor = row["end_exclusive"]
    require(cursor == 0x007FCEBA and end - first >= required,
            "suffix capacity arithmetic drift")
    require(end - suffix[0]["end_exclusive"] < required,
            "suffix does not begin at the minimal whole-region boundary")
    return {
        "required_payload_bytes": required,
        "mathematical_latest_start": f"0x{threshold:08X}",
        "minimal_whole_region_suffix_start": f"0x{first:08X}",
        "minimal_whole_region_suffix_rows": len(suffix),
        "source_compiled_rows": sum(
            row["address_status"] == "source_compiled" for row in suffix
        ),
        "generated_alignment_rows": sum(
            row["address_status"] == "generated_alignment" for row in suffix
        ),
        "occupied_bytes_that_require_displacement": sum(
            row["size"] for row in suffix
        ),
        "contiguous_bytes_after_displacement": end - first,
        "first_live_region": suffix[0]["region"],
        "contains_live_ancc_dispatch": any(
            row["region"] ==
            "ambiqsuite_ancc_profile_open-cfw-ancc-dispatch_source_text"
            for row in suffix
        ),
        "route_feasible_without_displacement": False,
    }


def verify_component_rows(
    *, rows: list[dict[str, Any]], payload: bytes, runtime_base: int,
    file_preamble: int, artifact_root: Path, expected_end: int,
) -> None:
    require(rows and rows[0]["target_address"] == runtime_base,
            "component flash-plan start drift")
    cursor = runtime_base
    for row in rows:
        require(row["target_address"] == cursor and
                row["size"] == row["end_exclusive"] - row["target_address"],
                f"component row gap, overlap, or size drift: {row['region']}")
        expected_offset = row["target_address"] - runtime_base + file_preamble
        require(row["component_file_offset"] == expected_offset,
                f"component runtime/file-offset drift: {row['region']}")
        artifact = (artifact_root / row["artifact"]).read_bytes()
        package_bytes = payload[expected_offset:expected_offset + row["size"]]
        require(artifact == package_bytes and len(artifact) == row["size"] and
                sha256(artifact) == row["sha256"],
                f"component artifact/package drift: {row['region']}")
        cursor = row["end_exclusive"]
    require(cursor == expected_end, "component flash-plan end drift")


def stock_cff_reference_audit(
    *, payload: bytes, cff_map: dict[str, Any], ghidra_data: bytes
) -> dict[str, Any]:
    starts = {int(row["start"], 16) for row in cff_map["functions"]}
    require(len(starts) == 101, "complete CFF start-set drift")
    external_calls: list[tuple[int, int]] = []
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        caller = int(row["entry"], 16)
        for value in row.get("callees", []):
            callee = int(value, 16)
            if callee in starts and not (
                STOCK_CFF_ENVELOPE[0] <= caller < STOCK_CFF_ENVELOPE[1]
            ):
                external_calls.append((caller, callee))
    require(not external_calls, "direct caller into stock CFF envelope appeared")

    compact = [
        (address, address + size)
        for address, size, _name, _digest in CFF_TABLE_INTERVALS
    ]
    counters: Counter[str] = Counter()
    targets: set[int] = set()
    unexpected: list[tuple[int, int]] = []
    payload_runtime_base = RUN_BASE - PREAMBLE_BYTES
    for offset in range(0, len(payload) - 3, 2):
        value = int.from_bytes(payload[offset:offset + 4], "little")
        target = value & ~1
        if target not in starts:
            continue
        address = payload_runtime_base + offset
        targets.add(target)
        if STOCK_CFF_ENVELOPE[0] <= address < STOCK_CFF_ENVELOPE[1]:
            counters["inside-cff-envelope"] += 1
        elif any(first <= address < last for first, last in compact):
            counters["authenticated-compact-table"] += 1
        elif address in CFF_CALLBACK_SLOTS:
            counters["authenticated-callback-slot"] += 1
        else:
            counters["outside-authenticated-cff-data"] += 1
            unexpected.append((address, value))
    require(counters == {
        "authenticated-compact-table": 40,
        "authenticated-callback-slot": 18,
        "inside-cff-envelope": 3,
        "outside-authenticated-cff-data": 1,
    } and len(targets) == 58,
            "stock CFF pointer-word census drift")
    require(unexpected == [(0x004CD47E, 0x005AF88D)],
            "unexpected stock CFF pointer-like word drift")
    # The sole outside word is four instruction bytes at a halfword boundary,
    # not data: it lies inside pinned Ghidra body 0x004CD3AA..0x004CD550.
    containing = []
    for line in ghidra_data.splitlines():
        row = json.loads(line)
        if any(int(first, 16) <= 0x004CD47E <= int(last, 16)
               for first, last in row["ranges"]):
            containing.append(row["entry"])
    require("004cd3aa" in containing,
            "pointer-like instruction collision containment drift")
    return {
        "direct_external_cff_call_edges": 0,
        "pointer_like_words": sum(counters.values()),
        "distinct_cff_targets": len(targets),
        "classification_counts": dict(sorted(counters.items())),
        "instruction_collision": {
            "address": "0x004CD47E", "value": "0x005AF88D",
            "containing_function": "0x004CD3AA",
            "classification": "halfword-aligned-instruction-bytes-not-data",
        },
        "old_envelope_has_no_authenticated_direct_external_entry": True,
    }


def analyze(
    *,
    flash_plan_path: Path = FLASH_PLAN,
    build_report_path: Path = BUILD_REPORT,
    package_path: Path = PACKAGE,
    artifact_root: Path = ARTIFACT_ROOT,
    cff_map_path: Path = CFF_MAP,
    ghidra_path: Path = GHIDRA,
    placement_path: Path = PLACEMENT,
) -> dict[str, Any]:
    # Dependency substitution is test-only; the production paths must retain
    # their exact receipts before any semantic inspection is trusted.
    paths = {
        FLASH_PLAN: flash_plan_path,
        BUILD_REPORT: build_report_path,
        PACKAGE: package_path,
        CFF_MAP: cff_map_path,
        GHIDRA: ghidra_path,
        PLACEMENT: placement_path,
    }
    data: dict[Path, bytes] = {}
    for canonical_path, actual_path in paths.items():
        raw = actual_path.read_bytes()
        require((len(raw), sha256(raw)) == PINS[canonical_path],
                f"input pin drift: {canonical_path}")
        data[canonical_path] = raw

    plan = json.loads(data[FLASH_PLAN])
    report = json.loads(data[BUILD_REPORT])
    cff_map = json.loads(data[CFF_MAP])
    ghidra_data = data[GHIDRA]
    placement = json.loads(data[PLACEMENT])
    package = data[PACKAGE]

    require(plan["package_sha256"] == PINS[PACKAGE][1] and
            report["package"]["sha256"] == PINS[PACKAGE][1] and
            report["package"]["byte_identical_to_reference"] is True,
            "flash-plan/build-report/package relation drift")
    entries = [entry for entry in report["entries"] if entry["entry_id"] == 6]
    require(entries == [EXPECTED_APOLLO_ENTRY], "Apollo package entry drift")
    entry = entries[0]
    payload_start = entry["package_offset"] + PACKAGE_COMPONENT_HEADER_BYTES
    payload = package[payload_start:payload_start + entry["payload_size"]]
    require(len(payload) == entry["payload_size"] and
            sha256(payload) == EXPECTED_APOLLO_PAYLOAD_SHA256,
            "Apollo package payload receipt drift")
    planned_end = RUN_BASE + len(payload) - PREAMBLE_BYTES
    require(planned_end == 0x007FCEBA, "Apollo package end arithmetic drift")

    boot_entries = [entry for entry in report["entries"] if entry["entry_id"] == 5]
    require(boot_entries == [EXPECTED_BOOT_ENTRY], "Apollo boot package entry drift")
    boot_entry = boot_entries[0]
    boot_start = boot_entry["package_offset"] + PACKAGE_COMPONENT_HEADER_BYTES
    boot_payload = package[
        boot_start:boot_start + boot_entry["payload_size"]
    ]
    require(len(boot_payload) == boot_entry["payload_size"] and
            sha256(boot_payload) == EXPECTED_BOOT_PAYLOAD_SHA256,
            "Apollo boot package payload receipt drift")

    app_rows = sorted([
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_main" and
        row.get("target") == "apollo510b_internal_mram"
    ], key=lambda row: row["target_address"])
    boot_rows = sorted([
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_bootloader" and
        row.get("target") == "apollo510b_internal_mram"
    ], key=lambda row: row["target_address"])
    require(len(app_rows) == 6_120 and len(boot_rows) == 330,
            "whole Apollo flash-row census drift")
    verify_component_rows(
        rows=app_rows, payload=payload, runtime_base=RUN_BASE,
        file_preamble=PREAMBLE_BYTES, artifact_root=artifact_root,
        expected_end=planned_end,
    )
    boot_runtime_end = 0x00410000 + len(boot_payload)
    require(boot_runtime_end == 0x004368E0,
            "Apollo boot payload end arithmetic drift")
    verify_component_rows(
        rows=boot_rows, payload=boot_payload, runtime_base=0x00410000,
        file_preamble=0, artifact_root=artifact_root,
        expected_end=boot_runtime_end,
    )
    app_status_rows = Counter(row["address_status"] for row in app_rows)
    app_status_bytes = Counter()
    for row in app_rows:
        app_status_bytes[row["address_status"]] += row["size"]
    require(app_status_rows == {
        "generated_source_entry_replacement": 2_291,
        "source_compiled": 1_989,
        "generated_alignment": 897,
        "official_blob": 810,
        "generated_source_data_replacement": 123,
        "generated_source_exact_replacement": 7,
        "source_compiled_rodata": 2,
        "generated_source_exact_load_image": 1,
    }, "whole Apollo address-status row census drift")
    require(app_status_bytes == {
        "official_blob": 3_123_044,
        "source_compiled": 425_682,
        "generated_source_entry_replacement": 397_760,
        "generated_source_data_replacement": 2_200,
        "generated_alignment": 1_888,
        "source_compiled_rodata": 1_600,
        "generated_source_exact_replacement": 134,
        "generated_source_exact_load_image": 6,
    }, "whole Apollo address-status byte census drift")

    start, end = CANDIDATE
    rows = sorted([
        row for row in plan["flash_regions"]
        if row.get("component") == "apollo_main" and
        row["end_exclusive"] > start and row["target_address"] < end
    ], key=lambda row: row["target_address"])
    require(len(rows) == 477 and rows[0]["target_address"] == 0x007EC9B0 and
            rows[-1]["end_exclusive"] == planned_end,
            "candidate occupied-region census drift")
    require({row["address_status"] for row in rows} ==
            {"source_compiled", "generated_alignment"},
            "unexpected late-Apollo address status")
    validate_contiguous(rows, start, planned_end)

    ledger = []
    clipped_by_status: Counter[str] = Counter()
    full_by_status: Counter[str] = Counter()
    by_family: Counter[str] = Counter()
    family_rows: Counter[str] = Counter()
    for row in rows:
        require(row["size"] == row["end_exclusive"] - row["target_address"],
                f"row size arithmetic drift: {row['region']}")
        expected_offset = row["target_address"] - RUN_BASE + PREAMBLE_BYTES
        require(row["component_file_offset"] == expected_offset,
                f"row runtime/file-offset relation drift: {row['region']}")
        source = artifact_root / row["artifact"]
        artifact = source.read_bytes()
        component_bytes = payload[
            row["component_file_offset"]:
            row["component_file_offset"] + row["size"]
        ]
        require(len(artifact) == row["size"] and artifact == component_bytes and
                sha256(artifact) == row["sha256"],
                f"planned artifact/package bytes drift: {row['region']}")
        clipped_start = max(start, row["target_address"])
        clipped_end = min(end, row["end_exclusive"])
        clipped = clipped_end - clipped_start
        status = row["address_status"]
        owner = family(row["region"])
        clipped_by_status[status] += clipped
        full_by_status[status] += row["size"]
        by_family[owner] += clipped
        family_rows[owner] += 1
        ledger.append({
            "region": row["region"],
            "function": row["function"],
            "start": f"0x{row['target_address']:08X}",
            "end_exclusive": f"0x{row['end_exclusive']:08X}",
            "full_row_bytes": row["size"],
            "candidate_bytes": clipped,
            "sha256": row["sha256"],
            "family": owner,
            "classification": (
                "current-package-source-compiled-owned"
                if status == "source_compiled" else
                "current-package-required-layout-alignment"
            ),
            "directly_reclaimable": False,
            "reclaim_condition": (
                "relocate or remove the currently routed source body and reclose "
                "all dependent relocations and entry redirects"
                if status == "source_compiled" else
                "repack the complete later tail and regenerate every affected address"
            ),
            "artifact_and_package_bytes_match": True,
        })
    require(full_by_status == {"source_compiled": 66_524,
                               "generated_alignment": 302},
            "full-row status accounting drift")
    require(clipped_by_status == {"source_compiled": 66_376,
                                  "generated_alignment": 302},
            "candidate status accounting drift")
    require(sum(clipped_by_status.values()) == planned_end - start == 66_678,
            "candidate occupied-byte conservation drift")
    require((family_rows, by_family) == (
        Counter({"cordio": 333, "ambiqsuite": 82, "service": 52,
                 "s200": 8, "iar": 2}),
        Counter({"cordio": 38_988, "ambiqsuite": 16_274,
                 "service": 1_662, "s200": 588, "iar": 9_166}),
    ), "late-Apollo family accounting drift")

    require(cff_map["scope"]["envelope_start"] == "0x005ABEF8" and
            cff_map["scope"]["envelope_end_exclusive"] == "0x005B0114" and
            cff_map["scope"]["physical_bytes"] == 16_924 and
            cff_map["confidence"]["unresolved_code"]["bytes"] == 0,
            "complete CFF envelope evidence drift")
    cff_reference_audit = stock_cff_reference_audit(
        payload=payload, cff_map=cff_map, ghidra_data=ghidra_data
    )
    stock = payload_slice(payload, *STOCK_CFF_ENVELOPE)
    require(sha256(stock) == STOCK_CFF_ENVELOPE_SHA256,
            "current package stock CFF envelope drift")
    table_records = []
    for address, size, name, digest in CFF_TABLE_INTERVALS:
        value = payload_slice(payload, address, address + size)
        require(sha256(value) == digest, f"current CFF table drift: {name}")
        table_records.append({
            "name": name, "start": f"0x{address:08X}", "bytes": size,
            "sha256": digest,
        })
    slot_bytes = b"".join(
        payload_slice(payload, address, address + 4)
        for address in CFF_CALLBACK_SLOTS
    )
    require(sha256(slot_bytes) == CFF_CALLBACK_SLOTS_SHA256,
            "current CFF callback-slot set drift")
    known_table_bytes = sum(row[1] for row in CFF_TABLE_INTERVALS) + len(slot_bytes)
    require(known_table_bytes == 364, "known CFF table-byte accounting drift")
    table_bytes_inside_envelope = sum(
        4 for address in CFF_CALLBACK_SLOTS
        if STOCK_CFF_ENVELOPE[0] <= address < STOCK_CFF_ENVELOPE[1]
    )
    require(table_bytes_inside_envelope == 4,
            "CFF table/envelope overlap accounting drift")
    unique_table_bytes_beyond_envelope = (
        known_table_bytes - table_bytes_inside_envelope
    )

    profiles = placement["deterministic_link"]["profiles"]
    require({name: value["objects"]["final_binary"]["size"]
             for name, value in profiles.items()} == EXPECTED_FINAL_PAYLOADS,
            "CFF final-payload size drift")
    require(placement["routing"]["production_route_feasible_now"] is False and
            placement["routing"]["firmware_image_emitted"] is False,
            "capacity solver must not consume a routed placement manifest")

    free_tail = end - planned_end
    boot_partition_gap = RUN_BASE - boot_runtime_end
    require(boot_partition_gap == 5_920,
            "bootloader-partition headroom arithmetic drift")
    legal_app_scatter_capacity = (
        free_tail + len(stock) + unique_table_bytes_beyond_envelope
    )
    require(legal_app_scatter_capacity == 21_706,
            "legal application scatter upper-bound drift")
    relocation_forms = {
        relocation
        for profile in profiles.values()
        for relocation in profile["relocations"]["by_type"]
    }
    require(relocation_forms == {
        "R_ARM_ABS32", "R_ARM_PREL31", "R_ARM_THM_CALL",
        "R_ARM_THM_JUMP24", "R_ARM_THM_MOVT_ABS", "R_ARM_THM_MOVW_ABS_NC",
    }, "CFF scatter relocation-form census drift")
    retained_addresses = [
        int(value, 16)
        for value in placement["imports"]["authenticated_retained_bindings"].values()
    ]
    widest_branch_domain = max(
        planned_end, *retained_addresses
    ) - min(boot_runtime_end, *retained_addresses)
    require(widest_branch_domain < 16 * 1024 * 1024,
            "Thumb call/jump scatter reach exceeds 16 MiB")
    scatter_profiles = {}
    for name, profile in sorted(profiles.items()):
        final_sections = profile["finalized"]["sections"]
        section_bytes = {
            section: final_sections[section]["size"]
            for section in ("text", "arm_exidx", "rodata", "data", "bss")
        }
        minimum_loadable = sum(
            section_bytes[section]
            for section in ("text", "arm_exidx", "rodata", "data")
        )
        require(section_bytes["data"] == section_bytes["bss"] == 0,
                f"{name}: scatter unexpectedly requires static RAM")
        # Hypothetical cross-component shape: rodata and the finalized exidx
        # fit first in bootloader-partition headroom, then text uses the
        # remaining aligned bytes plus the old CFF envelope and tail.
        cursor = boot_runtime_end + section_bytes["rodata"]
        cursor = (cursor + 3) & ~3
        cursor += section_bytes["arm_exidx"]
        cursor = (cursor + 15) & ~15
        boot_gap_text_capacity = RUN_BASE - cursor
        stock_text_capacity = STOCK_CFF_ENVELOPE[1] - (
            (STOCK_CFF_ENVELOPE[0] + 15) & ~15
        )
        tail_text_capacity = CANDIDATE[1] - ((planned_end + 15) & ~15)
        hypothetical_text_capacity = (
            boot_gap_text_capacity + stock_text_capacity + tail_text_capacity
        )
        require(hypothetical_text_capacity >= section_bytes["text"],
                f"{name}: hypothetical cross-component section shape drift")
        scatter_profiles[name] = {
            "existing_final_binary_bytes": profile["objects"]["final_binary"]["size"],
            "minimum_loadable_section_bytes": minimum_loadable,
            "section_bytes": section_bytes,
            "legal_application_capacity_upper_bound": legal_app_scatter_capacity,
            "legal_application_minimum_shortfall": (
                minimum_loadable - legal_app_scatter_capacity
            ),
            "legal_application_final_binary_shortfall": (
                profile["objects"]["final_binary"]["size"] -
                legal_app_scatter_capacity
            ),
            "hypothetical_cross_component": {
                "bootloader_partition_headroom": boot_partition_gap,
                "boot_gap_text_capacity_after_rodata_exidx": (
                    boot_gap_text_capacity
                ),
                "stock_envelope_aligned_text_capacity": stock_text_capacity,
                "tail_aligned_text_capacity": tail_text_capacity,
                "total_text_capacity": hypothetical_text_capacity,
                "text_margin": hypothetical_text_capacity - section_bytes["text"],
                "section_shape_fits": True,
                "legal_component_ownership": False,
            },
            "production_scatter_feasible": False,
        }

    padding_upper_bound = clipped_by_status["generated_alignment"]
    conditional_cff = len(stock) + unique_table_bytes_beyond_envelope
    optimistic_total = free_tail + padding_upper_bound + conditional_cff
    require((free_tail, padding_upper_bound, conditional_cff, optimistic_total) ==
            (4_422, 302, 17_284, 22_008),
            "optimistic capacity upper-bound arithmetic drift")
    profile_results = {}
    for name, required in EXPECTED_FINAL_PAYLOADS.items():
        shortfall = required - free_tail
        optimistic_shortfall = required - optimistic_total
        require(shortfall > 0 and optimistic_shortfall > 0,
                f"{name}: CFF capacity blocker unexpectedly closed")
        profile_results[name] = {
            "required_payload_bytes": required,
            "authenticated_directly_free_bytes": free_tail,
            "current_shortfall": shortfall,
            "optimistic_known_capacity_upper_bound": optimistic_total,
            "shortfall_even_after_optimistic_upper_bound": optimistic_shortfall,
            "byte_capacity_lower_bound": minimal_live_rows(
                rows, shortfall, start, end
            ),
            "contiguous_final_binary_blocker": contiguous_suffix_blocker(
                rows, required, end
            ),
            "placement_feasible": False,
        }

    require(plan["protected_regions"][0] == {
        "end_exclusive": 0x00410000,
        "end_exclusive_hex": "0x00410000",
        "name": "ambiq_secure_bootloader",
        "policy": "not_present_in_evenota_do_not_overwrite",
        "start": 0x00400000,
        "start_hex": "0x00400000",
        "target": "apollo510b_internal_mram",
    }, "protected secure-bootloader interval drift")
    require(plan["protected_regions"][1] == {
        "end_exclusive": 0x007FE010,
        "end_exclusive_hex": "0x007FE010",
        "name": "update_flag",
        "policy": "bootloader_owned_do_not_include_in_application_image",
        "start": end,
        "start_hex": "0x007FE000",
        "target": "apollo510b_internal_mram",
    }, "protected update interval drift")

    result: dict[str, Any] = {
        "schema_version": 1,
        "status": "g2-freetype-cff-capacity-blocked-by-package-owned-apollo-tail",
        "analysis_mode": "software-only read-only capacity solver",
        "current_package": {
            "package_bytes": len(package),
            "package_sha256": sha256(package),
            "apollo_payload_bytes": len(payload),
            "apollo_payload_sha256": sha256(payload),
            "apollo_runtime_end_exclusive": f"0x{planned_end:08X}",
            "all_477_artifacts_match_package": True,
            "all_6120_application_and_330_boot_rows_match_package": True,
        },
        "whole_address_space": {
            "audited_internal_mram": {
                "start": "0x00400000", "end_exclusive": "0x007FE010",
            },
            "secure_bootloader": {
                "start": "0x00400000", "end_exclusive": "0x00410000",
                "bytes": 65_536, "classification": "protected-not-in-package",
                "reclaimable": False,
            },
            "even_bootloader": {
                "start": "0x00410000",
                "end_exclusive": f"0x{boot_runtime_end:08X}",
                "rows": len(boot_rows), "bytes": len(boot_payload),
                "classification": "separate-package-entry-currently-occupied",
                "reclaimable_by_application": False,
            },
            "bootloader_partition_headroom": {
                "start": f"0x{boot_runtime_end:08X}",
                "end_exclusive": f"0x{RUN_BASE:08X}",
                "bytes": boot_partition_gap,
                "classification": "outside-apollo-application-package-entry",
                "physically_empty_in_pinned_package": True,
                "application_placement_authority": False,
            },
            "apollo_application": {
                "start": f"0x{RUN_BASE:08X}",
                "end_exclusive": f"0x{planned_end:08X}",
                "rows": len(app_rows),
                "installed_bytes": planned_end - RUN_BASE,
                "internal_free_gaps": 0,
                "row_status_counts": dict(sorted(app_status_rows.items())),
                "byte_status_counts": dict(sorted(app_status_bytes.items())),
                "vector_and_first_region_occupied": True,
                "all_source_replacement_rows_treated_as_owned": True,
                "unproven_source_replaced_caves_admitted": 0,
            },
            "application_tail": {
                "start": f"0x{planned_end:08X}",
                "end_exclusive": f"0x{end:08X}",
                "bytes": free_tail, "classification": "application-owned-free-tail",
            },
            "update_record": {
                "start": "0x007FE000", "end_exclusive": "0x007FE010",
                "bytes": 16, "classification": "bootloader-owned-protected",
                "reclaimable": False,
            },
            "physical_gap_count_below_update_record": 2,
            "physical_gap_bytes_below_update_record": (
                boot_partition_gap + free_tail
            ),
            "legal_application_gap_count": 1,
            "legal_application_gap_bytes": free_tail,
        },
        "candidate_interval": {
            "start": f"0x{start:08X}",
            "end_exclusive": f"0x{end:08X}",
            "bytes": end - start,
            "occupied_end_exclusive": f"0x{planned_end:08X}",
            "occupied_regions": len(rows),
            "occupied_bytes": sum(clipped_by_status.values()),
            "directly_free_tail_bytes": free_tail,
            "classification_bytes": dict(sorted(clipped_by_status.items())),
            "classification_full_row_bytes": dict(sorted(full_by_status.items())),
            "family_rows": dict(sorted(family_rows.items())),
            "family_bytes": dict(sorted(by_family.items())),
            "regions": ledger,
        },
        "reclaim_audit": {
            "directly_reclaimable": {
                "bytes": 0,
                "reason": "every occupied candidate byte is present in the current package",
            },
            "repack_only_generated_alignment": {
                "bytes": padding_upper_bound,
                "currently_reclaimable": False,
            },
            "conditionally_superseded_stock_cff": {
                "callable_physical_envelope": {
                    "start": "0x005ABEF8", "end_exclusive": "0x005B0114",
                    "bytes": len(stock), "sha256": sha256(stock),
                },
                "authenticated_table_and_callback_words": {
                    "bytes": known_table_bytes,
                    "bytes_already_inside_callable_physical_envelope": (
                        table_bytes_inside_envelope
                    ),
                    "unique_bytes_beyond_callable_physical_envelope": (
                        unique_table_bytes_beyond_envelope
                    ),
                    "compact_tables": table_records,
                    "callback_slots": len(CFF_CALLBACK_SLOTS),
                    "callback_slot_bytes": len(slot_bytes),
                    "callback_slots_sha256": sha256(slot_bytes),
                },
                "bytes": conditional_cff,
                "currently_reclaimable": False,
                "conditions": [
                    "a source-built CFF class must first own registration",
                    "all old CFF roots and direct references must be retired",
                    "a reviewed noncontiguous linker/relocator must own every interval",
                ],
            },
            "optimistic_known_capacity_upper_bound": {
                "directly_free_tail": free_tail,
                "all_generated_alignment": padding_upper_bound,
                "all_authenticated_stock_cff_code_and_words": conditional_cff,
                "total": optimistic_total,
                "feasible_for_any_profile": False,
                "warning": (
                    "this intentionally overcounts conditional, noncontiguous bytes; "
                    "it is an impossibility bound, not a placement plan"
                ),
            },
            "other_source-replaced_stock_bodies": {
                "bytes_admitted": 0,
                "reason": (
                    "no component-wide alternate-entry, literal, callback, and call-graph "
                    "liveness proof authenticates those scattered bodies as writable caves"
                ),
            },
            "stock_cff_external_reference_audit": cff_reference_audit,
        },
        "profiles": profile_results,
        "scatter_placement": {
            "legal_application_regions": [
                {
                    "start": "0x005ABEF8", "end_exclusive": "0x005B0114",
                    "bytes": len(stock),
                    "classification": "conditional-stock-cff-envelope",
                },
                {
                    "bytes": unique_table_bytes_beyond_envelope,
                    "classification": "conditional-scattered-cff-table-words",
                },
                {
                    "start": f"0x{planned_end:08X}",
                    "end_exclusive": "0x007FE000", "bytes": free_tail,
                    "classification": "directly-free-application-tail",
                },
            ],
            "legal_application_capacity_upper_bound": legal_app_scatter_capacity,
            "profile_results": scatter_profiles,
            "relocation_forms": sorted(relocation_forms),
            "thumb_call_jump_range_bytes_each_direction": 16 * 1024 * 1024,
            "widest_hypothetical_binding_domain_bytes": widest_branch_domain,
            "relocation_encodings_range_compatible": True,
            "data_pointer_encoding_range_compatible": True,
            "input_section_atomicity_required": True,
            "exact_scatter_link_attempted": False,
            "exact_scatter_link_blocker": (
                "legal application-owned capacity is below even the sum of final "
                "loadable section bytes; the only arithmetic fit consumes "
                "bootloader-partition headroom owned by a different package entry"
            ),
            "cross_component_update_atomicity_authenticated": False,
            "production_scatter_feasible": False,
        },
        "protected_boundary": {
            "start": "0x007FE000", "end_exclusive": "0x007FE010",
            "policy": "bootloader_owned_do_not_include_in_application_image",
            "reclaimable": False,
        },
        "minimal_blocker_set": {
            "contiguous_placement": (
                "171 package-owned tail rows beginning with "
                "iar_format_output_source_closure "
                "must be displaced as a closed set for the current contiguous final binary"
            ),
            "noncontiguous_byte_capacity": (
                "at least four package-owned source rows must be displaced; "
                "the three largest "
                "do not cover either profile shortfall"
            ),
            "residual_after_all_known_optimistic_capacity": {
                "apple-clang": 4_786, "linux-clang": 4_718,
            },
        },
        "routing": {
            "production_placement_feasible": False,
            "production_scatter_feasible": False,
            "module_class_pointer_patch_permitted": False,
            "firmware_image_emitted": False,
        },
        "evidence_bounds": {
            "compiler_byte_identity_claimed": False,
            "conditional_capacity_counted_as_writable": False,
            "cross_component_headroom_counted_as_application_writable": False,
            "production_placement_claimed": False,
            "production_routing_claimed": False,
            "font_payload_authenticated": False,
            "stack_or_wcet_qualified": False,
            "hardware_validation_performed": False,
        },
    }
    result["solver_sha256"] = canonical({
        "candidate_interval": result["candidate_interval"],
        "whole_address_space": result["whole_address_space"],
        "reclaim_audit": result["reclaim_audit"],
        "profiles": result["profiles"],
        "scatter_placement": result["scatter_placement"],
        "protected_boundary": result["protected_boundary"],
        "minimal_blocker_set": result["minimal_blocker_set"],
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pretty", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--check-manifest", action="store_true")
    args = parser.parse_args()
    try:
        report = analyze()
        rendered = json.dumps(report, sort_keys=True, indent=2) + "\n"
        if args.write_manifest:
            MANIFEST.write_text(rendered, encoding="utf-8")
        if args.check_manifest:
            require(MANIFEST.is_file() and
                    json.loads(MANIFEST.read_text(encoding="utf-8")) == report,
                    "checked-in CFF capacity-solver manifest drift")
    except (CapacityError, OSError, KeyError, ValueError) as error:
        print(f"G2 FreeType CFF capacity solver failed: {error}", file=sys.stderr)
        return 1
    print(rendered if args.pretty else json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
