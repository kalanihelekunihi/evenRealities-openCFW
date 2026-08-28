#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministic function map for the shipped G2 touch-controller prefix.

The input is the authenticated type-3 FWPK payload.  Discovery starts only at
vector targets and function entries already established by the touch identity,
I2C-protocol, and sensing audits.  Direct in-prefix BL targets are added to a
fixed point.  Calls are never followed as ordinary control flow; conditional
and unconditional direct branches are followed, with branches into another
known entry represented as shared/tail-call boundaries.

This is deliberately not a raw-halfword BL sweep: literal pools can decode as
plausible Thumb instructions.  It is also not a resident-flash map.  Tables and
the DFU implementation beyond the 0x8680 shipped prefix are an unavailable
external ABI and never become function rows.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_GRP_CALL,
    CS_GRP_JUMP,
    CS_GRP_RET,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_MCLASS,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_INS_CBNZ, ARM_INS_CBZ, ARM_OP_IMM

ROOT = Path(__file__).resolve().parents[1]
BLOB = ROOT / "blobs/official/g2-2.2.6.10/firmware_touch.bin"
IDENTITY_ANALYZER = ROOT / "tools/analyze_g2_touch_identity.py"
PROTOCOL_ANALYZER = ROOT / "tools/analyze_g2_touch_i2c_protocol.py"
MANIFEST_DIR = ROOT / "tools/manifests"

BLOB_SHA256 = "0d13d8bb1337bf22989dc16143e3d5eca29a31cc1ed753ff624668750ea9470d"
RECORD_OFFSET = 0x20
RECORD_SIZE = 0x8680
CODE_START = 0x00C0
CODE_END = 0x775C
RESIDENT_START = RECORD_SIZE
FLASH_END = 0x10000

# Entries established by earlier byte-pinned audits.  Alternate callback and
# vector entries are intentionally retained even when they share a suffix.
EVIDENCE_ENTRIES = {
    0x02F4: ("sensor_read_mux", "I2C protocol sensor_read_mux span"),
    0x0378: ("i2c_slave_init", "I2C protocol initialization span"),
    0x0400: ("i2c_irq_handler", "I2C protocol IRQ span"),
    0x0824: ("report_builder", "I2C protocol report span"),
    0x0BE0: ("logger_stub", "I2C protocol compiled-out logger span"),
    0x3624: ("i2c_payload_callback_entry", "resident callback registry pointer"),
    0x36C4: ("msc_sensing_loop", "touch sensing MSC_SPAN"),
    0x37C0: ("event_dispatcher", "I2C protocol event-dispatch span"),
    0x4B14: ("NVIC_SystemReset", "I2C protocol reset span"),
    0x4B30: ("enter_dfu_mailbox_and_reset", "I2C protocol DFU handoff"),
    0x67D8: ("i2c_tx_descriptor_arm", "I2C protocol FIFO helper"),
    0x67F0: ("i2c_rx_descriptor_arm", "I2C protocol FIFO helper"),
    0x6806: ("i2c_rx_position_get", "I2C protocol FIFO helper"),
    0x703C: ("power_mode_set", "I2C protocol power-management span"),
    0x7074: ("sleep_wfi_entry", "I2C protocol power-management span"),
    0x7088: ("sflash_trim_load", "I2C protocol power-management span"),
}

# These are exact executable entry labels within the IRQ dispatcher, but not
# independent functions.  Keeping that distinction avoids false function rows.
COMMAND_CASE_ENTRIES = {
    0x0446: "version_identity_query_case",
    0x0466: "read_saved_proximity_baseline_case",
    0x0480: "read_long_press_threshold_case",
    0x04A0: "save_proximity_baseline_case",
    0x04C8: "write_gesture_configuration_case",
    0x052C: "enter_dfu_case",
    0x054C: "read_current_sensor_report_case",
}

MSC_SPAN = (
    0x36C4,
    0x376C,
    "5cee0e3336b8a6e052adc77ba845ff2d03d1dd5c9f4926588d523217aa7a13bc",
)

# Filled from the authenticated output of this algorithm.  These pins make a
# decoder/version drift or control-flow change fail closed.
EXPECTED_MAP = {
    "function_count": 63,
    "instruction_instances": 3171,
    "function_instruction_bytes": 6620,
    "unique_instruction_bytes": 6316,
    "shared_instruction_bytes": 162,
    "maximum_owners_per_byte": 3,
    "row_digest": "335e09b1d61057a49e69d4f58f9e9117f4e8db4f475068f76ba3f544919a5e7a",
}


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _decoder() -> Cs:
    decoder = Cs(
        CS_ARCH_ARM,
        CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS,
    )
    decoder.detail = True
    return decoder


def _direct_target(insn) -> int | None:
    if (
        insn.operands
        and insn.operands[-1].type == ARM_OP_IMM
        and (
            insn.group(CS_GRP_JUMP)
            or insn.id in (ARM_INS_CBZ, ARM_INS_CBNZ)
            or insn.group(CS_GRP_CALL)
        )
    ):
        return insn.operands[-1].imm & ~1
    return None


def _walk(payload: bytes, entry: int, entries: set[int]) -> dict:
    decoder = _decoder()
    pending = [entry]
    instructions = {}
    calls = []
    tail_entries = set()
    indirect_exits = []

    while pending:
        address = pending.pop()
        if address in instructions:
            continue
        require(address % 2 == 0, f"unaligned branch from {entry:#x} to {address:#x}")
        require(CODE_START <= address < CODE_END,
                f"CFG from {entry:#x} escaped shipped code at {address:#x}")
        insn = next(decoder.disasm(payload[address:address + 4], address, count=1), None)
        require(insn is not None, f"decode failed for {entry:#x} at {address:#x}")
        require(address + insn.size <= CODE_END,
                f"instruction at {address:#x} crosses shipped code end")
        instructions[address] = insn

        target = _direct_target(insn)
        is_call = insn.group(CS_GRP_CALL)
        if is_call:
            calls.append({
                "site": address,
                "target": target,
                "kind": "direct" if target is not None else "indirect",
            })

        is_return = (
            insn.group(CS_GRP_RET)
            or (insn.mnemonic == "pop" and "pc" in insn.op_str)
            or (insn.mnemonic == "bx" and insn.op_str == "lr")
        )
        is_jump = (
            insn.group(CS_GRP_JUMP)
            or insn.id in (ARM_INS_CBZ, ARM_INS_CBNZ)
        ) and not is_call
        is_unconditional = insn.mnemonic in ("b", "b.w", "bx")

        if is_jump:
            if target is None:
                if not is_return:
                    indirect_exits.append(address)
            elif target in entries and target != entry:
                tail_entries.add(target)
            else:
                require(CODE_START <= target < CODE_END,
                        f"direct branch from {address:#x} leaves shipped code")
                pending.append(target)
        if not is_return and not is_unconditional:
            pending.append(address + insn.size)

    ordered = sorted(instructions)
    spans = []
    for address in ordered:
        end = address + instructions[address].size
        if spans and address == spans[-1][1]:
            spans[-1] = (spans[-1][0], end)
        else:
            spans.append((address, end))
    body = b"".join(payload[a:a + instructions[a].size] for a in ordered)
    return {
        "entry": entry,
        "instructions": instructions,
        "instruction_count": len(ordered),
        "instruction_bytes": len(body),
        "instruction_sha256": sha256(body),
        "spans": spans,
        "calls": sorted(calls, key=lambda item: item["site"]),
        "tail_entries": sorted(tail_entries),
        "indirect_exits": sorted(indirect_exits),
    }


def _discover(payload: bytes, vector_entries: set[int]) -> tuple[set[int], dict[int, set[str]]]:
    entries = set(EVIDENCE_ENTRIES) | vector_entries
    sources = {entry: set() for entry in entries}
    for entry in EVIDENCE_ENTRIES:
        sources[entry].add("evidence")
    for entry in vector_entries:
        sources[entry].add("vector")

    while True:
        additions = {}
        for entry in sorted(entries):
            body = _walk(payload, entry, entries)
            for call in body["calls"]:
                target = call["target"]
                if target is not None and CODE_START <= target < CODE_END:
                    additions.setdefault(target, set()).add(
                        f"bl@0x{call['site']:04X}"
                    )
        new_entries = set(additions) - entries
        for entry, found_sources in additions.items():
            sources.setdefault(entry, set()).update(found_sources)
        if not new_entries:
            return entries, sources
        entries.update(new_entries)


def _vector_entries(payload: bytes) -> set[int]:
    vectors = struct.unpack_from("<48I", payload, 0)
    return {
        value & ~1
        for value in vectors[1:]
        if CODE_START <= (value & ~1) < CODE_END
    }


def _row_digest(rows: list[dict]) -> str:
    stable = []
    for row in rows:
        stable.append({
            "entry": row["entry"],
            "instruction_count": row["instruction_count"],
            "instruction_bytes": row["instruction_bytes"],
            "instruction_sha256": row["instruction_sha256"],
            "spans": row["spans"],
            "direct_callees": row["direct_callees"],
            "tail_entries": row["tail_entries"],
        })
    return sha256(json.dumps(stable, sort_keys=True, separators=(",", ":")).encode())


def analyze(blob: bytes | None = None, *, enforce_expected: bool = True) -> dict:
    data = BLOB.read_bytes() if blob is None else blob
    require(len(data) == RECORD_OFFSET + RECORD_SIZE, "touch FWPK size changed")
    require(sha256(data) == BLOB_SHA256, "touch FWPK SHA-256 changed")

    identity = _load(IDENTITY_ANALYZER, "g2_touch_identity_for_prefix_map")
    protocol = _load(PROTOCOL_ANALYZER, "g2_touch_protocol_for_prefix_map")
    identity_report = identity.audit(data)
    protocol_report = protocol.audit(data)
    require(all(x["result"] == "pass" for x in identity_report["checks"]),
            "touch identity audit changed")
    require(all(x["result"] == "pass" for x in protocol_report["checks"]),
            "touch protocol audit changed")

    payload = data[RECORD_OFFSET:RECORD_OFFSET + RECORD_SIZE]
    msc_start, msc_end, msc_digest = MSC_SPAN
    require(sha256(payload[msc_start:msc_end]) == msc_digest,
            "touch sensing MSC span changed")

    vector_entries = _vector_entries(payload)
    entries, sources = _discover(payload, vector_entries)
    bodies = {entry: _walk(payload, entry, entries) for entry in sorted(entries)}

    byte_owners: dict[int, set[int]] = {}
    rows = []
    for entry, body in bodies.items():
        for address, insn in body["instructions"].items():
            for byte in range(address, address + insn.size):
                byte_owners.setdefault(byte, set()).add(entry)
        if entry in EVIDENCE_ENTRIES:
            name, evidence = EVIDENCE_ENTRIES[entry]
            classification = "evidence_named"
        elif entry in vector_entries:
            name = f"vector_entry_{entry:04x}"
            evidence = "authenticated vector-table target; semantic role unresolved"
            classification = "vector_seed_unresolved"
        else:
            name = f"touch_sub_{entry:04x}"
            evidence = "reachable direct BL target from evidence/vector closure"
            classification = "unresolved_shipped_prefix"
        direct_callees = sorted({
            call["target"] for call in body["calls"]
            if call["target"] is not None and call["target"] in entries
        })
        rows.append({
            "entry": entry,
            "name": name,
            "classification": classification,
            "evidence": evidence,
            "discovery_sources": sorted(sources[entry]),
            "instruction_count": body["instruction_count"],
            "instruction_bytes": body["instruction_bytes"],
            "instruction_sha256": body["instruction_sha256"],
            "spans": [{"start": a, "end": b, "bytes": b - a}
                      for a, b in body["spans"]],
            "direct_callees": direct_callees,
            "indirect_call_sites": sorted(
                call["site"] for call in body["calls"]
                if call["kind"] == "indirect"
            ),
            "tail_entries": body["tail_entries"],
            "indirect_jump_exits": body["indirect_exits"],
        })

    metrics = {
        "function_count": len(rows),
        "evidence_named_functions": sum(
            row["classification"] == "evidence_named" for row in rows
        ),
        "vector_seed_functions": sum(
            row["classification"] == "vector_seed_unresolved" for row in rows
        ),
        "unresolved_shipped_functions": sum(
            row["classification"] == "unresolved_shipped_prefix" for row in rows
        ),
        "instruction_instances": sum(row["instruction_count"] for row in rows),
        "function_instruction_bytes": sum(row["instruction_bytes"] for row in rows),
        "unique_instruction_bytes": len(byte_owners),
        "shared_instruction_bytes": sum(len(owners) > 1 for owners in byte_owners.values()),
        "maximum_owners_per_byte": max(map(len, byte_owners.values())),
        "code_span_bytes": CODE_END - CODE_START,
        "code_bytes_not_in_reachable_map": CODE_END - CODE_START - len(byte_owners),
        "indirect_call_sites": sum(len(row["indirect_call_sites"]) for row in rows),
        "indirect_jump_exits": sum(len(row["indirect_jump_exits"]) for row in rows),
        "row_digest": _row_digest(rows),
    }
    if enforce_expected:
        for key, expected in EXPECTED_MAP.items():
            require(metrics[key] == expected,
                    f"touch prefix {key} changed: {metrics[key]!r} != {expected!r}")

    span_anchors = [
        {"name": name, "start": start, "end": end, "size": end - start,
         "sha256": digest, "role": role, "kind": "authenticated_code_region"}
        for name, start, end, digest, role in protocol.SPANS
    ]
    span_anchors.append({
        "name": "msc_sensing_loop", "start": msc_start, "end": msc_end,
        "size": msc_end - msc_start, "sha256": msc_digest,
        "role": "authenticated MSC sensing-loop span",
        "kind": "authenticated_code_region",
    })
    case_anchors = [
        {"name": name, "entry": entry, "kind": "dispatch_case_entry",
         "parent_function": 0x0400}
        for entry, name in sorted(COMMAND_CASE_ENTRIES.items())
    ]
    resident_abi = [
        {"reference_offset": off, "address": address, "role": role,
         "availability": "external_unavailable_abi"}
        for off, address, role in protocol.RESIDENT_REFS
    ]
    resident_abi.append({
        "reference_offset": None,
        "address": None,
        "role": "resident DFU implementation entered after mailbox write and reset; exact resident entry/table unavailable",
        "availability": "external_unavailable_abi",
    })

    require(all(row["entry"] < RESIDENT_START for row in rows),
            "resident address incorrectly emitted as a function")
    require(all(item["address"] is None or item["address"] >= RESIDENT_START
                for item in resident_abi), "external ABI address fell inside prefix")

    return {
        "schema_version": 1,
        "analysis_mode": "offline authenticated Thumb CFG recovery; no hardware, reset, DFU, signing, or flash operation",
        "identity": {
            "blob": str(BLOB.relative_to(ROOT)),
            "sha256": BLOB_SHA256,
            "payload_start": 0,
            "payload_end": RECORD_SIZE,
            "code_start": CODE_START,
            "code_end": CODE_END,
            "resident_external_start": RESIDENT_START,
        },
        "method": {
            "seed_policy": "authenticated vectors plus evidence-established function entries; recursive direct in-prefix BL closure",
            "raw_halfword_bl_sweep_used_as_seed": False,
            "shared_tail_policy": "overlapping reachable suffix bytes retained per function and deduplicated in global coverage",
            "resident_policy": "flash [0x8680,0x10000) and resident DFU/tables are external unavailable ABI",
        },
        "metrics": metrics,
        "rows": rows,
        "span_anchors": span_anchors,
        "case_anchors": case_anchors,
        "resident_abi": resident_abi,
        "licensing": {
            "analyzer_and_manifests": "MIT",
            "official_blob": "provenance evidence only; not relicensed",
            "historical_function_sources": "not inferred from this map; preserve identified upstream provider licenses",
            "resident_abi": "unavailable; no source or license claim",
        },
        "limitations": [
            "This tranche maps only vector/evidence/direct-call reachable entries, not every possible callable entry in code+pools.",
            "Indirect call targets and resident table targets cannot be recovered from the shipped prefix alone.",
            "Evidence-named behavior does not by itself establish historical source ownership or license.",
            "No physical behavior, electrical timing, or release fitness is claimed.",
        ],
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    written = []

    functions = MANIFEST_DIR / "g2-touch-prefix-function-map.tsv"
    lines = [
        "# SPDX-License-Identifier: MIT",
        "# Authenticated shipped-prefix reachable function map; resident flash excluded",
        "entry\tname\tclassification\tinstructions\tinstruction_bytes\tinstruction_sha256\tdiscovery_sources\tdirect_callees\ttail_entries\tspans\tevidence",
    ]
    for row in result["rows"]:
        sources = ",".join(row["discovery_sources"])
        callees = ",".join(f"0x{x:04X}" for x in row["direct_callees"])
        tails = ",".join(f"0x{x:04X}" for x in row["tail_entries"])
        spans = ",".join(f"0x{x['start']:04X}-0x{x['end']:04X}" for x in row["spans"])
        lines.append(
            f"0x{row['entry']:04X}\t{row['name']}\t{row['classification']}\t"
            f"{row['instruction_count']}\t{row['instruction_bytes']}\t"
            f"{row['instruction_sha256']}\t{sources}\t{callees}\t{tails}\t{spans}\t"
            f"{row['evidence']}"
        )
    functions.write_text("\n".join(lines) + "\n")
    written.append(functions)

    anchors = MANIFEST_DIR / "g2-touch-prefix-evidence-anchors.tsv"
    anchor_lines = [
        "# SPDX-License-Identifier: MIT",
        "kind\tname\tstart_or_entry\tend_exclusive\tsize\tsha256\tparent_function\trole",
    ]
    for item in result["span_anchors"]:
        anchor_lines.append(
            f"{item['kind']}\t{item['name']}\t0x{item['start']:04X}\t"
            f"0x{item['end']:04X}\t{item['size']}\t{item['sha256']}\t-\t{item['role']}"
        )
    for item in result["case_anchors"]:
        anchor_lines.append(
            f"{item['kind']}\t{item['name']}\t0x{item['entry']:04X}\t-\t-\t-\t"
            f"0x{item['parent_function']:04X}\texecutable case entry; not a standalone function claim"
        )
    anchors.write_text("\n".join(anchor_lines) + "\n")
    written.append(anchors)

    external = MANIFEST_DIR / "g2-touch-prefix-external-abi.tsv"
    external_lines = [
        "# SPDX-License-Identifier: MIT",
        "reference_offset\tresident_address\tavailability\trole",
    ]
    for item in result["resident_abi"]:
        off = "-" if item["reference_offset"] is None else f"0x{item['reference_offset']:04X}"
        address = "unavailable" if item["address"] is None else f"0x{item['address']:04X}"
        external_lines.append(
            f"{off}\t{address}\t{item['availability']}\t{item['role']}"
        )
    external.write_text("\n".join(external_lines) + "\n")
    written.append(external)

    summary = MANIFEST_DIR / "g2-touch-prefix-function-map-summary.json"
    slim = {key: value for key, value in result.items() if key != "rows"}
    slim["row_count"] = len(result["rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    written.append(summary)
    return written


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifests", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = analyze()
    if args.write_manifests:
        for path in write_manifests(result):
            print(f"wrote {path.relative_to(ROOT)}")
    if args.json:
        print(json.dumps({key: value for key, value in result.items() if key != "rows"},
                         indent=2, sort_keys=True))
    else:
        metrics = result["metrics"]
        print(f"touch prefix functions: {metrics['function_count']}")
        print(f"unique instruction bytes: {metrics['unique_instruction_bytes']}")
        print(f"shared instruction bytes: {metrics['shared_instruction_bytes']}")
        print("resident/DFU: external unavailable ABI; no resident function rows")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch prefix function-map audit failed: {exc}") from exc
