#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Relocation-corrected CFG/data partition of the shipped G2 touch image."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import sys

from capstone.arm import ARM_OP_MEM, ARM_REG_PC

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MANIFEST_DIR = TOOLS / "manifests"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"
READINESS_ANALYZER = TOOLS / "analyze_g2_touch_software_readiness.py"
PROTOCOL_ANALYZER = TOOLS / "analyze_g2_touch_i2c_protocol.py"
IDENTITY_ANALYZER = TOOLS / "analyze_g2_touch_identity.py"

LINK_BASE = 0x3300
VECTOR_TARGETS = {
    0x465D: (0x135C, "shared_default_handler", "shared NMI/SVC/PendSV/SysTick/external-IRQ default target"),
    0x465F: (0x135E, "hardfault_halt_handler", "HardFault target calls the pinned halt loop at payload 0x7038"),
    0x4675: (0x1374, "reset_startup_handler", "reset/startup target; bounded before the literal pool at 0x13DC"),
}
VECTOR_SPANS = {
    0x135C: (0x135C, 0x135E,
             "575fc8fa9e92ffe7d57a6aef6f1168f39da04f07d6bcd5b5e17883bff7b33165"),
    0x135E: (0x135E, 0x1366,
             "76df2f1edb1a47699b952e59c124b1c2bc8f442272c16a4192c8adb94de54f3a"),
    0x1374: (0x1374, 0x13DC,
             "db0963144ca483b44bfb640b4a31207f3d90b3cb1cfbc342d19f6217f47cfb2a"),
}

EXPECTED = {
    "function_entries": 286,
    "entry_origins": {
        "authenticated_evidence": 16,
        "direct_bl_closure": 252,
        "linked_flash_pointer": 15,
        "relocated_vector": 3,
    },
    "function_dispositions": {
        "external_eula_clean_room_required": 20,
        "project_fail_closed_contract": 8,
        "project_source_candidate": 10,
        "semantic_source_unclassified": 223,
        "typed_startup_source_required": 3,
        "unsupported_intentional_noop": 1,
        "upstream_apache_provider": 14,
        "upstream_runtime_provider": 7,
    },
    "literal_targets": 472,
    "linked_pointer_seed_entries": 15,
    "code_partition": {
        "cfg_instruction_candidate": 26892,
        "cfg_literal_overlap_ambiguous": 72,
        "referenced_literal_data": 1816,
        "still_unclassified": 1584,
    },
    "prior_remainder_partition": {
        "new_cfg_instruction_candidate": 20580,
        "new_cfg_literal_overlap_ambiguous": 68,
        "new_referenced_literal_data": 1816,
        "still_unclassified": 1584,
    },
    "function_digest": "601c283cbcd191ef603f92b59f555c5ba1b78c4de72c0f75ebaa83182e50866c",
    "partition_digest": "0b9c47aa5bcb65d74cb4985342f39d54a192450e26b8dbdb07f200c215a25b75",
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
    require(spec is not None and spec.loader is not None,
            f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _digest(rows: list[dict], keys: tuple[str, ...]) -> str:
    stable = [{key: row[key] for key in keys} for row in rows]
    return sha256(json.dumps(stable, sort_keys=True,
                             separators=(",", ":")).encode())


def _body_bytes(prefix, payload: bytes, entries: set[int]) -> tuple[dict, set[int]]:
    bodies = {entry: prefix._walk(payload, entry, entries)
              for entry in sorted(entries)}
    addresses = {
        byte
        for body in bodies.values()
        for address, insn in body["instructions"].items()
        for byte in range(address, address + insn.size)
    }
    return bodies, addresses


def _direct_closure(prefix, payload: bytes, entries: set[int],
                    sources: dict[int, set[str]]) -> set[int]:
    while True:
        additions: dict[int, set[str]] = {}
        for entry in sorted(entries):
            body = prefix._walk(payload, entry, entries)
            for call in body["calls"]:
                target = call["target"]
                if (target is not None and prefix.CODE_START <= target < prefix.CODE_END):
                    additions.setdefault(target, set()).add(
                        f"bl@0x{call['site']:04X}"
                    )
        for entry, found in additions.items():
            sources.setdefault(entry, set()).update(found)
        new = set(additions) - entries
        if not new:
            return entries
        entries.update(new)


def _literal_targets(bodies: dict) -> dict[int, set[int]]:
    refs: dict[int, set[int]] = {}
    for body in bodies.values():
        for address, insn in body["instructions"].items():
            for operand in insn.operands:
                if operand.type == ARM_OP_MEM and operand.mem.base == ARM_REG_PC:
                    target = ((address + 4) & ~3) + operand.mem.disp
                    refs.setdefault(target, set()).add(address)
    return refs


def _set_row(name: str, addresses: set[int], payload: bytes,
             note: str) -> dict:
    ordered = sorted(addresses)
    return {
        "category": name,
        "bytes": len(ordered),
        "start": min(ordered) if ordered else None,
        "end": max(ordered) + 1 if ordered else None,
        "address_set_sha256": sha256(b"".join(
            struct.pack("<I", value) for value in ordered
        )),
        "content_sha256": sha256(bytes(payload[value] for value in ordered)),
        "note": note,
    }


def analyze(*, enforce_expected: bool = True) -> dict:
    prefix = _load(PREFIX_ANALYZER, "touch_relocated_prefix")
    readiness_mod = _load(READINESS_ANALYZER, "touch_relocated_readiness")
    protocol = _load(PROTOCOL_ANALYZER, "touch_relocated_protocol")
    identity = _load(IDENTITY_ANALYZER, "touch_relocated_identity")

    old_map = prefix.analyze()
    readiness = readiness_mod.analyze()
    blob = prefix.BLOB.read_bytes()
    payload = blob[prefix.RECORD_OFFSET:prefix.RECORD_OFFSET + prefix.RECORD_SIZE]

    # Two independent, semantically pinned address correspondences establish
    # the link base without guessing from instruction appearance.
    require(0xAA5C - identity.REGIONS[2][1] == LINK_BASE,
            "string link-base anchor changed")
    require(0xB0C4 - identity.JUMP_TABLE_OFFSET == LINK_BASE,
            "jump-table link-base anchor changed")
    require(sha256(payload[0x775C:0x7DC4]) == identity.REGIONS[2][3],
            "linked string-region anchor changed")
    require(tuple(struct.unpack_from("<9I", payload, 0x7DC4)) == identity.JUMP_TABLE,
            "linked jump-table anchor changed")

    raw_vectors = struct.unpack_from("<48I", payload, 0)
    vector_entries = set()
    vector_rows = []
    for raw, (offset, name, role) in VECTOR_TARGETS.items():
        require(raw in raw_vectors, f"raw vector {raw:#x} disappeared")
        require((raw & ~1) - LINK_BASE == offset,
                f"vector relocation changed for {raw:#x}")
        start, end, digest = VECTOR_SPANS[offset]
        require(sha256(payload[start:end]) == digest,
                f"vector body changed at {offset:#x}")
        vector_entries.add(offset)
        vector_rows.append({
            "raw_vector": raw, "payload_entry": offset,
            "name": name, "role": role, "start": start, "end": end,
            "bytes": end - start, "sha256": digest,
            "source_disposition": "typed startup behavior; provider or MIT clean-room source still required",
        })

    sources = {entry: {"authenticated_evidence"}
               for entry in prefix.EVIDENCE_ENTRIES}
    for entry in vector_entries:
        sources.setdefault(entry, set()).add("relocated_vector")
    entries = _direct_closure(
        prefix, payload, set(prefix.EVIDENCE_ENTRIES) | vector_entries, sources
    )
    bodies, first_cfg_bytes = _body_bytes(prefix, payload, entries)
    first_literals = _literal_targets(bodies)

    pointer_sources: dict[int, set[int]] = {}
    for literal, sites in first_literals.items():
        require(prefix.CODE_START <= literal and literal + 4 <= prefix.CODE_END,
                f"PC literal escaped mixed code/pool span at {literal:#x}")
        value = struct.unpack_from("<I", payload, literal)[0]
        if value & 1 and LINK_BASE <= value < LINK_BASE + prefix.CODE_END:
            target = (value & ~1) - LINK_BASE
            # A pointer into an already decoded body may be a case/callback
            # entry, but does not independently establish a function boundary.
            if target not in {address for body in bodies.values()
                              for address in body["instructions"]}:
                pointer_sources.setdefault(target, set()).update(sites)

    for entry, sites in pointer_sources.items():
        entries.add(entry)
        sources.setdefault(entry, set()).update(
            f"flash_pointer_via_ldr@0x{site:04X}" for site in sites
        )
    entries = _direct_closure(prefix, payload, entries, sources)
    bodies, cfg_bytes = _body_bytes(prefix, payload, entries)
    literal_refs = _literal_targets(bodies)
    literal_bytes = {
        byte for target in literal_refs for byte in range(target, target + 4)
    }
    universe = set(range(prefix.CODE_START, prefix.CODE_END))
    require(literal_bytes <= universe, "literal bytes escaped code/pool span")

    partition_sets = {
        "cfg_instruction_candidate": cfg_bytes - literal_bytes,
        "cfg_literal_overlap_ambiguous": cfg_bytes & literal_bytes,
        "referenced_literal_data": literal_bytes - cfg_bytes,
        "still_unclassified": universe - cfg_bytes - literal_bytes,
    }
    require(set().union(*partition_sets.values()) == universe,
            "partition does not cover code/pool span")
    require(sum(map(len, partition_sets.values())) == len(universe),
            "partition categories overlap")

    old_entries = {row["entry"] for row in old_map["rows"]}
    _old_bodies, old_cfg_bytes = _body_bytes(prefix, payload, old_entries)
    old_remainder = universe - old_cfg_bytes
    prior_sets = {
        "new_cfg_instruction_candidate": partition_sets["cfg_instruction_candidate"] & old_remainder,
        "new_cfg_literal_overlap_ambiguous": partition_sets["cfg_literal_overlap_ambiguous"] & old_remainder,
        "new_referenced_literal_data": partition_sets["referenced_literal_data"] & old_remainder,
        "still_unclassified": partition_sets["still_unclassified"] & old_remainder,
    }
    require(sum(map(len, prior_sets.values())) == len(old_remainder) == 24048,
            "prior remainder was not exhaustively repartitioned")

    readiness_by_entry = {row["entry"]: row for row in readiness["function_rows"]}
    function_rows = []
    for entry in sorted(entries):
        if entry in prefix.EVIDENCE_ENTRIES:
            origin = "authenticated_evidence"
        elif entry in vector_entries:
            origin = "relocated_vector"
        elif entry in pointer_sources:
            origin = "linked_flash_pointer"
        else:
            origin = "direct_bl_closure"
        if entry in readiness_by_entry:
            disposition = readiness_by_entry[entry]["status"]
            provider = readiness_by_entry[entry]["source_or_provider"]
            license_name = readiness_by_entry[entry]["license"]
        elif entry in vector_entries:
            disposition = "typed_startup_source_required"
            provider = "toolchain startup provider or independent MIT replacement"
            license_name = "LicenseRef-Unselected-Upstream-or-MIT"
        else:
            disposition = "semantic_source_unclassified"
            provider = "none"
            license_name = "unknown"
        body = bodies[entry]
        function_rows.append({
            "entry": entry, "origin": origin,
            "disposition": disposition, "provider_candidate": provider,
            "license": license_name,
            "instruction_count": body["instruction_count"],
            "instruction_bytes": body["instruction_bytes"],
            "instruction_sha256": body["instruction_sha256"],
            "discovery_sources": sorted(sources[entry]),
        })

    link_rows = []
    for off, address, role in protocol.RESIDENT_REFS:
        payload_offset = address - LINK_BASE
        require(0 <= payload_offset < len(payload),
                f"linked reference {address:#x} is not shipped")
        require(struct.unpack_from("<I", payload, off)[0] == address,
                f"linked reference word changed at {off:#x}")
        link_rows.append({
            "reference_offset": off, "linked_address": address,
            "payload_offset": payload_offset, "role": role,
            "availability": "shipped_payload_after_relocation",
        })

    partition_rows = [
        _set_row(name, addresses, payload, {
            "cfg_instruction_candidate": "decoded from relocated vector/evidence/direct-BL/linked-pointer CFG; not a source or semantic claim",
            "cfg_literal_overlap_ambiguous": "decoded as instructions but also targeted by PC-relative literal loads; must not be counted as concrete code",
            "referenced_literal_data": "four-byte PC-relative literal-load targets outside decoded CFG bytes",
            "still_unclassified": "neither in the conservative CFG candidate set nor a direct PC-relative literal target",
        }[name])
        for name, addresses in partition_sets.items()
    ]
    entry_origins = dict(sorted(Counter(row["origin"] for row in function_rows).items()))
    code_partition = {key: len(value) for key, value in partition_sets.items()}
    prior_partition = {key: len(value) for key, value in prior_sets.items()}
    metrics = {
        "function_entries": len(function_rows),
        "entry_origins": entry_origins,
        "function_dispositions": dict(sorted(Counter(
            row["disposition"] for row in function_rows
        ).items())),
        "literal_targets": len(literal_refs),
        "linked_pointer_seed_entries": len(pointer_sources),
        "code_span_bytes": len(universe),
        "code_partition": code_partition,
        "prior_remainder_bytes": len(old_remainder),
        "prior_remainder_partition": prior_partition,
        "concrete_source_function_count": sum(
            row["disposition"] == "project_source_candidate"
            for row in function_rows
        ),
        "typed_external_functions_not_counted_as_source": sum(
            row["disposition"] in {
                "external_eula_clean_room_required",
                "project_fail_closed_contract",
                "typed_startup_source_required",
                "upstream_apache_provider",
                "upstream_runtime_provider",
            } for row in function_rows
        ),
        "function_digest": _digest(function_rows, (
            "entry", "origin", "disposition", "provider_candidate", "license",
            "instruction_count", "instruction_bytes", "instruction_sha256",
            "discovery_sources",
        )),
        "partition_digest": _digest(partition_rows, (
            "category", "bytes", "start", "end", "address_set_sha256",
            "content_sha256",
        )),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"relocated partition {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch-controller relocated shipped payload",
        "analysis_mode": "offline relocation/CFG/data-reference analysis; no hardware, MMIO, reset, DFU, signing, or flash operation",
        "identity": old_map["identity"],
        "relocation": {
            "linked_flash_base": LINK_BASE,
            "payload_linked_end": LINK_BASE + len(payload),
            "anchors": [
                {"linked_address": 0xAA5C, "payload_offset": 0x775C,
                 "kind": "version/log strings"},
                {"linked_address": 0xB0C4, "payload_offset": 0x7DC4,
                 "kind": "nine-entry command jump table"},
            ],
            "correction": "absolute linked vectors/tables must be rebased by 0x3300; they are not payload offsets or external resident bytes",
        },
        "metrics": metrics,
        "vector_rows": vector_rows,
        "function_rows": function_rows,
        "partition_rows": partition_rows,
        "linked_reference_rows": link_rows,
        "limitations": [
            "CFG-decoded bytes are instruction candidates, not recovered source or behavior claims.",
            "The 72-byte CFG/literal intersection remains explicitly ambiguous.",
            "The 1,584 residual bytes may mix unreferenced data, padding, and unreachable or indirectly reachable code.",
            "Only ten evidence-backed project-source candidates are counted as concrete source; typed external/provider functions are not.",
            "Indirect calls without a shipped linked pointer remain unresolved.",
        ],
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    functions = MANIFEST_DIR / "g2-touch-relocated-functions.tsv"
    with functions.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "origin", "disposition", "provider_candidate",
                         "license", "instructions", "instruction_bytes",
                         "instruction_sha256", "discovery_sources"])
        for row in result["function_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["origin"], row["disposition"],
                row["provider_candidate"], row["license"], row["instruction_count"],
                row["instruction_bytes"], row["instruction_sha256"],
                ",".join(row["discovery_sources"]),
            ])

    partition = MANIFEST_DIR / "g2-touch-relocated-code-partition.tsv"
    with partition.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["category", "bytes", "start", "end_exclusive",
                         "address_set_sha256", "content_sha256", "note"])
        for row in result["partition_rows"]:
            writer.writerow([
                row["category"], row["bytes"], f"0x{row['start']:04X}",
                f"0x{row['end']:04X}", row["address_set_sha256"],
                row["content_sha256"], row["note"],
            ])

    vectors = MANIFEST_DIR / "g2-touch-relocated-vectors.tsv"
    with vectors.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["raw_vector", "payload_entry", "name", "start", "end",
                         "bytes", "sha256", "role", "source_disposition"])
        for row in result["vector_rows"]:
            writer.writerow([
                f"0x{row['raw_vector']:04X}", f"0x{row['payload_entry']:04X}",
                row["name"], f"0x{row['start']:04X}", f"0x{row['end']:04X}",
                row["bytes"], row["sha256"], row["role"],
                row["source_disposition"],
            ])

    refs = MANIFEST_DIR / "g2-touch-relocated-linked-references.tsv"
    with refs.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["reference_offset", "linked_address", "payload_offset",
                         "availability", "role"])
        for row in result["linked_reference_rows"]:
            writer.writerow([
                f"0x{row['reference_offset']:04X}", f"0x{row['linked_address']:04X}",
                f"0x{row['payload_offset']:04X}", row["availability"], row["role"],
            ])

    summary = MANIFEST_DIR / "g2-touch-relocated-partition-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("function_rows", "partition_rows")}
    slim["function_row_count"] = len(result["function_rows"])
    slim["partition_row_count"] = len(result["partition_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [functions, partition, vectors, refs, summary]


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
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ("function_rows", "partition_rows")},
                         indent=2, sort_keys=True))
    else:
        metrics = result["metrics"]
        print(f"linked flash base: 0x{LINK_BASE:04X}")
        print(f"relocated function entries: {metrics['function_entries']}")
        print(f"still-unclassified code/pool bytes: {metrics['code_partition']['still_unclassified']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch relocated partition audit failed: {exc}") from exc
