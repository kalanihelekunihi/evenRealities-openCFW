#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded semantic/provider batches and final byte typing for G2 touch."""

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

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MANIFEST_DIR = TOOLS / "manifests"
RELOCATED_ANALYZER = TOOLS / "analyze_g2_touch_relocated_partition.py"
PREFIX_ANALYZER = TOOLS / "analyze_g2_touch_prefix_function_map.py"

CONFIG_POINTERS = {
    0x864C: (0x0108, "startup callback pointer"),
    0x8648: (0x0134, "startup callback pointer"),
    0x861C: (0x6EC0, "PDL callback/provider pointer"),
}

# Each is a function boundary because the residual run starts with a standard
# push-LR prologue immediately after a decoded return or typed pool boundary.
LINEAR_PROLOGUE_ENTRIES = {
    0x0320, 0x29F8, 0x2CC6, 0x2D44, 0x2D78, 0x2DEA,
    0x35EC, 0x3780, 0x7750,
}

DISPATCH_TABLES = (
    (0x7DC4, 9, "I2C command switch"),
    (0x81FC, 8, "device-event switch"),
    (0x821C, 20, "SROM status switch"),
)

AMBIGUOUS_SPANS = (
    (0x01B8, 0x01D8, "CRT termination-call literal pool before next prologue"),
    (0x13DC, 0x13F8, "reset/startup literal pool before next prologue"),
    (0x4B40, 0x4B44, "DFU/reset wrapper PC-relative SRAM literal"),
    (0x76CC, 0x76D4, "exit-wrapper literal pool before memset"),
)

RESIDUAL_DATA_SPANS = (
    (0x05B8, 0x05DC, "I2C command/report linked-reference words"),
    (0x38D0, 0x38D4, "event-dispatch descriptor constant"),
    (0x595C, 0x596C, "SROM status/result constants"),
    (0x5970, 0x5974, "SROM status/result constant"),
)

RUNTIME_EXACT = {
    0x76AC: ("exit_wrapper", "runtime ABI behavior; optional fini hook then non-returning _exit"),
    0x76E4: ("__libc_init_array", "walks preinit/init arrays through indirect calls"),
    0x7740: ("_exit_halt", "exact non-returning self-loop"),
    0x7744: ("runtime_init_stub", "callee-saved-register-preserving empty startup stub"),
}

BATCHES = {
    "application_startup_clean_room": {
        "provider": "OpenCFW behavior recovery required",
        "license": "MIT-for-new-clean-room-code",
        "status": "typed_application_or_startup_semantics_unresolved",
        "confidence": "low",
        "rule": "entry < 0x2998; application/startup caller cluster; no public-provider identity asserted",
    },
    "capsense_cat2_mixed": {
        "provider": "Infineon CAPSENSE or CAT2 PDL boundary unresolved",
        "license": "LicenseRef-Infineon-EULA-or-Apache-2.0",
        "status": "typed_vendor_boundary_provider_unresolved",
        "confidence": "low",
        "rule": "0x2998 <= entry < 0x4B14; mixed CapSense/MSCLP/PDL cluster bounded by established provider anchors",
    },
    "system_handoff_mixed": {
        "provider": "system/DFU handoff support boundary unresolved",
        "license": "LicenseRef-Unresolved",
        "status": "typed_system_boundary_provider_unresolved",
        "confidence": "low",
        "rule": "0x4B14 <= entry < 0x4B68 between reset/DFU and Em_EEPROM anchors",
    },
    "emeeprom_eula": {
        "provider": "Infineon Emulated EEPROM middleware",
        "license": "LicenseRef-Infineon-EULA",
        "status": "typed_external_eula_boundary",
        "confidence": "medium",
        "rule": "0x4B68 <= entry < 0x58F0 inside the checksum/read/write Em_EEPROM call cluster",
    },
    "cat2_pdl": {
        "provider": "Infineon mtb-pdl-cat2 candidate cluster",
        "license": "Apache-2.0",
        "status": "typed_upstream_provider_candidate",
        "confidence": "medium",
        "rule": "0x58F0 <= entry < 0x73C0 inside SROM/GPIO/clock/SCB/system PDL cluster",
    },
    "runtime": {
        "provider": "selected ARM EABI/C runtime",
        "license": "LicenseRef-Upstream-Toolchain-Runtime",
        "status": "exact_runtime_abi_candidate",
        "confidence": "high",
        "rule": "entry >= 0x73C0 and exact ABI/control-flow behavior listed in RUNTIME_EXACT",
    },
}

EXPECTED = {
    "semantic_rows": 223,
    "batch_counts": {
        "application_startup_clean_room": 99,
        "capsense_cat2_mixed": 55,
        "cat2_pdl": 54,
        "emeeprom_eula": 10,
        "runtime": 4,
        "system_handoff_mixed": 1,
    },
    "exact_runtime_rows": 4,
    "concrete_project_source_rows": 0,
    "expanded_function_entries": 301,
    "dispatch_case_entries": 23,
    "final_code_partition": {
        "cfg_instruction_candidate": 27674,
        "dispatch_case_instruction_candidate": 482,
        "referenced_literal_data": 1964,
        "residual_arch_nop_padding": 8,
        "residual_legacy_nop_padding": 126,
        "residual_return_tail": 4,
        "residual_typed_data": 60,
        "residual_zero_halfword_alignment_or_data": 46,
    },
    "prior_1584_partition": {
        "cfg_instruction_candidate": 782,
        "dispatch_case_instruction_candidate": 482,
        "referenced_literal_data": 76,
        "residual_arch_nop_padding": 8,
        "residual_legacy_nop_padding": 126,
        "residual_return_tail": 4,
        "residual_typed_data": 60,
        "residual_zero_halfword_alignment_or_data": 46,
    },
    "resolved_prior_ambiguous_bytes": 72,
    "semantic_digest": "84fd01c5d0b8fe7ad0d1784e03c10f179ecdad90fcde2cf8cc863bd118b45864",
    "byte_digest": "e8cd2af0475a22c070e04962a51977a370b12cc5ce6c86a271e686a10393df58",
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


def _batch(entry: int) -> str:
    if entry < 0x2998:
        return "application_startup_clean_room"
    if entry < 0x4B14:
        return "capsense_cat2_mixed"
    if entry < 0x4B68:
        return "system_handoff_mixed"
    if entry < 0x58F0:
        return "emeeprom_eula"
    if entry < 0x73C0:
        return "cat2_pdl"
    return "runtime"


def _set_row(category: str, addresses: set[int], payload: bytes,
             evidence: str) -> dict:
    ordered = sorted(addresses)
    return {
        "category": category, "bytes": len(ordered),
        "start": min(ordered), "end": max(ordered) + 1,
        "address_set_sha256": sha256(b"".join(
            struct.pack("<I", value) for value in ordered
        )),
        "content_sha256": sha256(bytes(payload[value] for value in ordered)),
        "evidence": evidence,
    }


def analyze(*, enforce_expected: bool = True) -> dict:
    relocated_mod = _load(RELOCATED_ANALYZER, "touch_semantic_relocated")
    prefix = _load(PREFIX_ANALYZER, "touch_semantic_prefix")
    relocated = relocated_mod.analyze()
    payload = prefix.BLOB.read_bytes()[prefix.RECORD_OFFSET:
                                      prefix.RECORD_OFFSET + prefix.RECORD_SIZE]
    universe = set(range(prefix.CODE_START, prefix.CODE_END))

    base_entries = {row["entry"] for row in relocated["function_rows"]}
    base_bodies, base_cfg = relocated_mod._body_bytes(prefix, payload, base_entries)
    base_refs = relocated_mod._literal_targets(base_bodies)
    base_literals = {byte for target in base_refs
                     for byte in range(target, target + 4)}
    prior_residual = universe - base_cfg - base_literals
    require(len(prior_residual) == 1584, "prior residual set changed")

    for word_offset, (entry, _role) in CONFIG_POINTERS.items():
        value = struct.unpack_from("<I", payload, word_offset)[0]
        require(value & 1 and (value & ~1) - relocated_mod.LINK_BASE == entry,
                f"config pointer changed at {word_offset:#x}")

    entries = base_entries | {item[0] for item in CONFIG_POINTERS.values()}
    entries |= LINEAR_PROLOGUE_ENTRIES
    sources = {entry: set() for entry in entries}
    entries = relocated_mod._direct_closure(prefix, payload, entries, sources)
    bodies, cfg = relocated_mod._body_bytes(prefix, payload, entries)
    refs = relocated_mod._literal_targets(bodies)
    literals = {byte for target in refs for byte in range(target, target + 4)}

    dispatch_entries = set()
    dispatch_rows = []
    for table, count, role in DISPATCH_TABLES:
        values = struct.unpack_from(f"<{count}I", payload, table)
        targets = sorted({(value & ~1) - relocated_mod.LINK_BASE
                          for value in values})
        require(all(prefix.CODE_START <= target < prefix.CODE_END
                    for target in targets), f"{role} target escaped code")
        dispatch_entries.update(targets)
        dispatch_rows.append({
            "table_offset": table, "entries": count, "role": role,
            "unique_targets": targets,
            "table_sha256": sha256(payload[table:table + count * 4]),
        })
    dispatch_bytes = {
        byte
        for entry in dispatch_entries
        for address, insn in prefix._walk(payload, entry, entries)["instructions"].items()
        for byte in range(address, address + insn.size)
    } - cfg - literals

    typed_data = {byte for start, end, _role in RESIDUAL_DATA_SPANS
                  for byte in range(start, end)}
    remaining = universe - (cfg - literals) - dispatch_bytes - literals - typed_data
    pattern_sets = {
        "residual_legacy_nop_padding": set(),
        "residual_arch_nop_padding": set(),
        "residual_zero_halfword_alignment_or_data": set(),
        "residual_return_tail": set(),
    }
    encodings = {
        b"\xC0\x46": "residual_legacy_nop_padding",
        b"\x00\xBF": "residual_arch_nop_padding",
        b"\x00\x00": "residual_zero_halfword_alignment_or_data",
        b"\x70\x47": "residual_return_tail",
    }
    residual_pairs = []
    pending = set(remaining)
    while pending:
        address = min(pending)
        require(address % 2 == 0 and {address, address + 1} <= pending,
                "residual contains an unpaired or unaligned byte")
        pending.difference_update((address, address + 1))
        residual_pairs.append(address)
    for address in residual_pairs:
        pair = payload[address:address + 2]
        require(pair in encodings,
                f"untyped residual halfword {pair.hex()} at {address:#x}")
        pattern_sets[encodings[pair]].update((address, address + 1))

    category_sets = {
        "cfg_instruction_candidate": cfg - literals,
        "dispatch_case_instruction_candidate": dispatch_bytes,
        "referenced_literal_data": literals,
        "residual_typed_data": typed_data,
        **pattern_sets,
    }
    require(set().union(*category_sets.values()) == universe,
            "final semantic byte partition is not exhaustive")
    require(sum(map(len, category_sets.values())) == len(universe),
            "final semantic byte partition overlaps")

    ambiguity_rows = []
    ambiguity_bytes = set()
    for start, end, evidence in AMBIGUOUS_SPANS:
        addresses = set(range(start, end))
        require(addresses <= literals,
                f"former ambiguity {start:#x}-{end:#x} is not literal data")
        ambiguity_bytes |= addresses
        ambiguity_rows.append({
            "start": start, "end": end, "bytes": end - start,
            "resolution": "referenced_literal_data_precedence",
            "sha256": sha256(payload[start:end]), "evidence": evidence,
        })

    by_entry = {row["entry"]: row for row in relocated["function_rows"]}
    opaque_entries = {entry for entry, row in by_entry.items()
                      if row["disposition"] == "semantic_source_unclassified"}
    callers = {entry: set() for entry in base_entries}
    for entry, body in base_bodies.items():
        for call in body["calls"]:
            if call["target"] in callers:
                callers[call["target"]].add(entry)
    semantic_rows = []
    for entry in sorted(opaque_entries):
        batch_name = _batch(entry)
        batch = BATCHES[batch_name]
        body = base_bodies[entry]
        if batch_name == "runtime":
            require(entry in RUNTIME_EXACT,
                    f"runtime entry {entry:#x} lacks exact evidence")
            proposed_name, evidence = RUNTIME_EXACT[entry]
            name_status = "exact_runtime_abi_candidate"
        else:
            proposed_name = f"touch_sub_{entry:04x}"
            evidence = batch["rule"]
            name_status = "typed_batch_only"
        semantic_rows.append({
            "entry": entry, "proposed_name": proposed_name,
            "batch": batch_name, "status": batch["status"],
            "provider": batch["provider"], "license": batch["license"],
            "confidence": batch["confidence"], "name_status": name_status,
            "concrete_project_source": False,
            "instruction_bytes": body["instruction_bytes"],
            "instruction_sha256": body["instruction_sha256"],
            "callers": sorted(callers[entry]),
            "callees": sorted({call["target"] for call in body["calls"]
                                if call["target"] in base_entries}),
            "evidence": evidence,
        })

    byte_rows = [
        _set_row(category, addresses, payload, {
            "cfg_instruction_candidate": "relocated evidence/direct-call/config-pointer/linear-prologue CFG; source not implied",
            "dispatch_case_instruction_candidate": "targets from three shipped linked switch tables; case entries are not standalone function claims",
            "referenced_literal_data": "PC-relative literal targets take precedence over linear fallthrough, including all former 72 ambiguous bytes",
            "residual_typed_data": "four bounded constant/reference spans; no executable claim",
            "residual_legacy_nop_padding": "all remaining halfwords equal Thumb legacy NOP encoding 0x46C0",
            "residual_arch_nop_padding": "all remaining halfwords equal Thumb NOP encoding 0xBF00",
            "residual_zero_halfword_alignment_or_data": "all remaining halfwords are zero; alignment versus data is intentionally unresolved",
            "residual_return_tail": "two remaining Thumb BX LR halfwords at established runtime boundaries",
        }[category])
        for category, addresses in sorted(category_sets.items())
    ]
    final_counts = {key: len(value) for key, value in sorted(category_sets.items())}
    prior_counts = {key: len(value & prior_residual)
                    for key, value in sorted(category_sets.items())}
    metrics = {
        "semantic_rows": len(semantic_rows),
        "batch_counts": dict(sorted(Counter(row["batch"]
                                             for row in semantic_rows).items())),
        "exact_runtime_rows": sum(row["name_status"] ==
                                  "exact_runtime_abi_candidate"
                                  for row in semantic_rows),
        "concrete_project_source_rows": sum(row["concrete_project_source"]
                                            for row in semantic_rows),
        "expanded_function_entries": len(entries),
        "dispatch_case_entries": len(dispatch_entries),
        "final_code_partition": final_counts,
        "prior_1584_partition": prior_counts,
        "resolved_prior_ambiguous_bytes": len(ambiguity_bytes),
        "semantic_digest": _digest(semantic_rows, (
            "entry", "proposed_name", "batch", "status", "provider", "license",
            "confidence", "name_status", "concrete_project_source",
            "instruction_bytes", "instruction_sha256", "callers", "callees",
        )),
        "byte_digest": _digest(byte_rows, (
            "category", "bytes", "start", "end", "address_set_sha256",
            "content_sha256",
        )),
    }
    if enforce_expected:
        for key, expected in EXPECTED.items():
            require(metrics[key] == expected,
                    f"semantic closure {key} changed: {metrics[key]!r} != {expected!r}")

    return {
        "schema_version": 1,
        "component": "G2 touch relocation-corrected semantic/provider batches",
        "analysis_mode": "offline CFG/caller/register/provider and byte-boundary analysis; no hardware, MMIO, reset, DFU, signing, or flash operation",
        "metrics": metrics,
        "batches": BATCHES,
        "semantic_rows": semantic_rows,
        "byte_rows": byte_rows,
        "ambiguity_rows": ambiguity_rows,
        "dispatch_rows": dispatch_rows,
        "source_rule": "No newly batched row is concrete project source. Apache/EULA/runtime labels are provider boundaries; mixed/private behavior remains typed external or unresolved.",
        "remaining_opacity": {
            "semantic_source_unclassified_entries": 223,
            "byte_unclassified": 0,
            "byte_semantically_ambiguous": 46,
            "note": "All physical code-span bytes are typed; 46 zero bytes retain alignment-versus-data ambiguity and 223 functions still need behavior-level recovery or exact public signatures.",
        },
    }


def write_manifests(result: dict) -> list[Path]:
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    semantics = MANIFEST_DIR / "g2-touch-relocated-semantic-batches.tsv"
    with semantics.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["entry", "proposed_name", "batch", "status", "provider",
                         "license", "confidence", "name_status",
                         "concrete_project_source", "instruction_bytes",
                         "instruction_sha256", "callers", "callees", "evidence"])
        for row in result["semantic_rows"]:
            writer.writerow([
                f"0x{row['entry']:04X}", row["proposed_name"], row["batch"],
                row["status"], row["provider"], row["license"], row["confidence"],
                row["name_status"], str(row["concrete_project_source"]).lower(),
                row["instruction_bytes"], row["instruction_sha256"],
                ",".join(f"0x{x:04X}" for x in row["callers"]),
                ",".join(f"0x{x:04X}" for x in row["callees"]), row["evidence"],
            ])

    byte_path = MANIFEST_DIR / "g2-touch-relocated-final-byte-types.tsv"
    with byte_path.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["category", "bytes", "start", "end_exclusive",
                         "address_set_sha256", "content_sha256", "evidence"])
        for row in result["byte_rows"]:
            writer.writerow([
                row["category"], row["bytes"], f"0x{row['start']:04X}",
                f"0x{row['end']:04X}", row["address_set_sha256"],
                row["content_sha256"], row["evidence"],
            ])

    ambiguity = MANIFEST_DIR / "g2-touch-relocated-ambiguity-resolution.tsv"
    with ambiguity.open("w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["# SPDX-License-Identifier: MIT"])
        writer.writerow(["start", "end_exclusive", "bytes", "resolution",
                         "sha256", "evidence"])
        for row in result["ambiguity_rows"]:
            writer.writerow([
                f"0x{row['start']:04X}", f"0x{row['end']:04X}", row["bytes"],
                row["resolution"], row["sha256"], row["evidence"],
            ])

    summary = MANIFEST_DIR / "g2-touch-relocated-semantic-summary.json"
    slim = {key: value for key, value in result.items()
            if key not in ("semantic_rows", "byte_rows")}
    slim["semantic_row_count"] = len(result["semantic_rows"])
    slim["byte_row_count"] = len(result["byte_rows"])
    summary.write_text(json.dumps(slim, indent=2, sort_keys=True) + "\n")
    return [semantics, byte_path, ambiguity, summary]


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
                          if key not in ("semantic_rows", "byte_rows")},
                         indent=2, sort_keys=True))
    else:
        print(f"semantic/provider rows: {result['metrics']['semantic_rows']}")
        print(f"expanded entries: {result['metrics']['expanded_function_entries']}")
        print(f"unclassified bytes: {result['remaining_opacity']['byte_unclassified']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except AuditError as exc:
        raise SystemExit(f"Touch relocated semantic audit failed: {exc}") from exc
