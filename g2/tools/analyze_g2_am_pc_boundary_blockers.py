#!/usr/bin/env python3
"""Classify PC-relative references across all remaining AM boundary blockers."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_GRP_CALL, CS_GRP_JUMP
from capstone import CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_g2_am_mixed_boundary_debt import (
    FUNC_RE,
    INST_RE,
    RAW_SUMMARY,
    classify_values,
)
from tools.open_cfw import load_manifest

OUT = ROOT / "tools/manifests/g2-am-pc-boundary-blockers.json"
SOURCE_ONLY_MANIFEST = ROOT / "manifests/g2-2.2.6.10-source-only.json"
ENTRY_RE = re.compile(r"_(?:0x)?([0-9a-f]+)$")


def _entry(function: str) -> int:
    match = ENTRY_RE.search(function)
    if match is None:
        raise ValueError(f"missing helper entry in {function}")
    return int(match.group(1), 16)


def _immediate_target(op_str: str) -> int | None:
    operand = op_str.split(",")[-1].strip()
    if not operand.startswith("#"):
        return None
    try:
        return int(operand[1:], 0) - 0x1001
    except ValueError:
        return None


def _pc_memory_target(offset: int, op_str: str) -> int | None:
    match = re.search(r"\[pc(?:,\s*#(-?0x[0-9a-fA-F]+|-?\d+))?\]", op_str)
    if match is None:
        return None
    immediate = int(match.group(1), 0) if match.group(1) else 0
    return ((offset + 4) & ~3) + immediate


def _pc_references(md: Cs, values: list[int]) -> list[dict[str, object]]:
    data = b"".join(value.to_bytes(2, "little") for value in values)
    refs = []
    for instruction in md.disasm(data, 0x1001):
        offset = instruction.address - 0x1001
        mnemonic = instruction.mnemonic.lower()
        base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        if base != "adr" and " pc" not in f" {op_str}":
            continue
        target = _immediate_target(op_str) if base == "adr" else _pc_memory_target(offset, op_str)
        if (
            target is None
            and (
                base in {"pop", "ldm", "ldmia", "ldmdb"}
                or (base == "ldr" and op_str.startswith("pc,"))
                or (base.startswith("bx") and op_str == "pc")
            )
        ):
            relation = "pc_control_operand"
        elif target is None and base in {"add", "addw", "adr", "mov"}:
            relation = "pc_address_arithmetic"
        elif target is None:
            relation = "pc_general_operand"
        elif 0 <= target < len(data):
            relation = "inside_body"
        else:
            relation = "outside_body"
        refs.append({
            "offset": offset,
            "instruction": f"{instruction.mnemonic} {instruction.op_str}".strip(),
            "target_offset": target,
            "target_relation": relation,
        })
    return refs


def _return_terminated_segments(
    byte_length: int,
    refs: list[dict[str, object]],
) -> list[dict[str, int]]:
    segments = []
    start = 0
    for ref in refs:
        if ref["target_relation"] != "pc_control_operand":
            continue
        end = int(ref["offset"]) + 2
        if end <= start:
            continue
        segments.append({
            "start_offset": start,
            "end_offset": end,
            "byte_length": end - start,
        })
        start = end
    if start < byte_length:
        segments.append({
            "start_offset": start,
            "end_offset": byte_length,
            "byte_length": byte_length - start,
        })
    return segments


def _branch_site_summary(
    md: Cs,
    data: bytes,
    entry: int,
    segment: dict[str, int],
    address_owner_lookup: list[dict[str, object]],
) -> dict[str, object]:
    start = segment["start_offset"]
    end = segment["end_offset"]
    segment_data = data[start:end]
    counts: dict[str, int] = {}
    owner_counts: dict[str, int] = {}
    owner_target_counts: dict[tuple[str, int], int] = {}
    owner_targets: dict[tuple[str, int], dict[str, object]] = {}
    owner_target_call_sites: dict[tuple[str, int], list[dict[str, object]]] = {}
    source_field_path_counts: dict[str, int] = {}
    examples = []
    unresolved_examples = []
    last_register_write: dict[str, dict[str, object]] = {}
    for instruction in md.disasm(segment_data, entry + start):
        operands = [
            item.strip().lower()
            for item in instruction.op_str.split(",")
            if item.strip()
        ]
        base = instruction.mnemonic.lower().split(".", 1)[0]
        if not (
            instruction.group(CS_GRP_CALL)
            or instruction.group(CS_GRP_JUMP)
            or base in {"cbz", "cbnz"}
        ):
            destination = operands[0] if operands else None
            if (
                destination is not None
                and re.fullmatch(
                    r"(?:r(?:1[0-2]|[0-9])|sp|lr|pc|ip|sl|fp)",
                    destination,
                )
            ):
                last_register_write[destination] = {
                    "offset": instruction.address - entry,
                    "instruction": (
                        f"{instruction.mnemonic} {instruction.op_str}".strip()
                    ),
                }
            continue
        target = None
        if instruction.operands and instruction.operands[-1].type == ARM_OP_IMM:
            target = instruction.operands[-1].imm & ~1
        if target is None:
            relation = "indirect_or_no_imm"
        elif entry <= target < entry + len(data):
            relation = "inside_function"
        else:
            relation = "outside_function"
        kind = "call" if instruction.group(CS_GRP_CALL) else "branch"
        key = f"{kind}:{relation}"
        counts[key] = counts.get(key, 0) + 1
        owner = _address_owner(
            target,
            address_owner_lookup,
        ) if target is not None else None
        if owner is None and target is None:
            owner_key = "unresolved:indirect_or_no_imm"
        elif owner is None:
            owner_key = "unresolved:target_owner_missing"
        else:
            owner_key = (
                f"{owner['component']}:{owner['region']}:"
                f"{owner['address_status']}"
            )
        owner_counts[owner_key] = owner_counts.get(owner_key, 0) + 1
        if target is not None:
            owner_target_key = (owner_key, target)
            owner_target_counts[owner_target_key] = (
                owner_target_counts.get(owner_target_key, 0) + 1
            )
            if owner_target_key not in owner_targets:
                owner_targets[owner_target_key] = {
                    "owner": owner_key,
                    "target_address": target,
                    "target_owner": owner,
                }
            call_sites = owner_target_call_sites.setdefault(owner_target_key, [])
            if len(call_sites) < 8:
                call_sites.append({
                    "offset": instruction.address - entry,
                    "instruction": (
                        f"{instruction.mnemonic} {instruction.op_str}".strip()
                    ),
                    "target_offset": target - entry,
                    "target_relation": relation,
                })
        if owner is None and len(unresolved_examples) < 8:
            source_register = (
                instruction.op_str.strip().lower()
                if target is None else None
            )
            source_write = (
                None if source_register is None else
                last_register_write.get(source_register)
            )
            source_base_register = (
                None if source_write is None else
                _register_base_from_memory_operand(str(source_write["instruction"]))
            )
            pointer_chain = _source_pointer_chain(
                source_register,
                last_register_write,
            )
            source_field_path = _source_field_path(pointer_chain)
            if source_field_path is not None:
                source_field_path_counts[source_field_path] = (
                    source_field_path_counts.get(source_field_path, 0) + 1)
            unresolved_examples.append({
                "offset": instruction.address - entry,
                "instruction": (
                    f"{instruction.mnemonic} {instruction.op_str}".strip()
                ),
                "target_offset": (
                    None if target is None else target - entry
                ),
                "target_relation": relation,
                "unresolved_kind": (
                    "indirect_or_no_imm"
                    if target is None else "target_owner_missing"
                ),
                "source_register": source_register,
                "source_register_last_write": source_write,
                "source_base_register": source_base_register,
                "source_base_register_last_write": (
                    None if source_base_register is None else
                    last_register_write.get(source_base_register)
                ),
                "source_pointer_chain": pointer_chain,
                "source_field_path": source_field_path,
            })
        if len(examples) < 8:
            examples.append({
                "offset": instruction.address - entry,
                "instruction": (
                    f"{instruction.mnemonic} {instruction.op_str}".strip()
                ),
                "target_offset": (
                    None if target is None else target - entry
                ),
                "target_relation": relation,
                "target_owner": owner,
            })
    return {
        "branch_site_counts": dict(sorted(counts.items())),
        "branch_target_owner_counts": dict(sorted(owner_counts.items())),
        "branch_target_site_frontier": [
            {
                **owner_targets[key],
                "count": count,
                "call_site_examples": owner_target_call_sites[key],
            }
            for key, count in sorted(
                owner_target_counts.items(),
                key=lambda item: (
                    -item[1],
                    item[0][0],
                    item[0][1],
                ),
            )
        ],
        "unresolved_source_field_path_counts": dict(
            sorted(source_field_path_counts.items())),
        "branch_site_examples": examples,
        "unresolved_branch_site_examples": unresolved_examples,
    }


def _register_base_from_memory_operand(instruction: str) -> str | None:
    match = re.search(r"\[([a-z][a-z0-9]*)(?:,|\])", instruction.lower())
    return match.group(1) if match is not None else None


def _memory_load_details(record: dict[str, object] | None) -> dict[str, object] | None:
    if record is None:
        return None
    instruction = str(record["instruction"]).lower()
    match = re.search(
        r"^(?:ldr(?:\.\w+)?|ldrb|ldrh)\s+([a-z][a-z0-9]*),\s*"
        r"\[([a-z][a-z0-9]*)(?:,\s*#(0x[0-9a-f]+|\d+))?\]",
        instruction,
    )
    if match is None:
        return None
    return {
        "load_offset": record["offset"],
        "destination_register": match.group(1),
        "base_register": match.group(2),
        "field_offset": int(match.group(3), 0) if match.group(3) else 0,
        "instruction": record["instruction"],
    }


def _register_move_source(record: dict[str, object] | None) -> str | None:
    if record is None:
        return None
    match = re.search(
        r"^movs?\s+[a-z][a-z0-9]*,\s*([a-z][a-z0-9]*)$",
        str(record["instruction"]).lower(),
    )
    return match.group(1) if match is not None else None


def _source_pointer_chain(
    source_register: str | None,
    last_register_write: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    if source_register is None:
        return []
    chain = []
    current = source_register
    seen = set()
    while current not in seen:
        seen.add(current)
        record = last_register_write.get(current)
        details = _memory_load_details(record)
        if details is None:
            moved_from = _register_move_source(record)
            if moved_from is not None:
                chain.append({
                    "register": current,
                    "source_register": moved_from,
                    "source_kind": "register_move",
                    "write": record,
                })
            break
        chain.append({
            "register": current,
            "source_kind": "memory_load",
            "base_register": details["base_register"],
            "field_offset": details["field_offset"],
            "load_offset": details["load_offset"],
            "instruction": details["instruction"],
        })
        current = str(details["base_register"])
    return chain


def _source_field_path(chain: list[dict[str, object]]) -> str | None:
    if len(chain) < 3:
        return None
    if (
        chain[0].get("source_kind") != "memory_load"
        or chain[1].get("source_kind") != "memory_load"
        or chain[2].get("source_kind") != "register_move"
    ):
        return None
    root = chain[2].get("source_register")
    mid = chain[1].get("field_offset")
    leaf = chain[0].get("field_offset")
    if not isinstance(root, str) or not isinstance(mid, int) or not isinstance(leaf, int):
        return None
    return f"{root}+0x{mid:x}->+0x{leaf:x}"


def _address_owner(
    address: int,
    address_owner_lookup: list[dict[str, object]],
) -> dict[str, object] | None:
    for row in address_owner_lookup:
        start = int(row["start"])
        end = int(row["end"])
        if start <= address < end:
            return {
                "component": row["component"],
                "region": row["region"],
                "address_status": row["address_status"],
                "region_start": start,
                "offset_in_region": address - start,
            }
    return None


def _address_owner_lookup() -> list[dict[str, object]]:
    manifest = load_manifest(SOURCE_ONLY_MANIFEST)
    rows = []
    for component in manifest["components"]:
        for region in component.get("regions", []):
            address = region.get("target_address")
            if not isinstance(address, int):
                continue
            rows.append({
                "component": component["name"],
                "region": region["name"],
                "address_status": region["address_status"],
                "start": address,
                "end": address + region["size"],
            })
    for region in manifest.get("protected_regions", []):
        rows.append({
            "component": "protected_region",
            "region": region["name"],
            "address_status": region["policy"],
            "start": region["start"],
            "end": region["end_exclusive"],
        })
    return sorted(rows, key=lambda row: (int(row["start"]), str(row["region"])))


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    address_owner_lookup = _address_owner_lookup()
    blockers = []
    relation_counts: dict[str, int] = {}
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        for function, body in FUNC_RE.findall(path.read_text()):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            reasons, consumed = classify_values(md, values)
            if "pc_relative_or_pc_operand_needs_boundary_model" not in reasons:
                continue
            data = b"".join(value.to_bytes(2, "little") for value in values)
            refs = _pc_references(md, values)
            byte_length = len(values) * 2
            return_segments = _return_terminated_segments(byte_length, refs)
            largest_segments = sorted(
                return_segments,
                key=lambda row: (-row["byte_length"], row["start_offset"]),
            )[:8]
            for segment in largest_segments:
                segment.update(_branch_site_summary(
                    md, data, _entry(function), segment, address_owner_lookup))
            unresolved_source_field_path_counts: dict[str, int] = {}
            for segment in largest_segments:
                for path, count in segment[
                    "unresolved_source_field_path_counts"].items():
                    unresolved_source_field_path_counts[path] = (
                        unresolved_source_field_path_counts.get(path, 0) + count
                    )
            function_relation_counts: dict[str, int] = {}
            for ref in refs:
                relation = str(ref["target_relation"])
                relation_counts[relation] = relation_counts.get(relation, 0) + 1
                function_relation_counts[relation] = (
                    function_relation_counts.get(relation, 0) + 1)
            blockers.append({
                "source": relative,
                "function": function,
                "byte_length": byte_length,
                "linear_disassembly_bytes": consumed,
                "boundary_kind": "linear" if consumed == len(values) * 2 else "mixed",
                "reasons": sorted(reasons),
                "pc_reference_count": len(refs),
                "pc_reference_relation_counts": dict(
                    sorted(function_relation_counts.items())),
                "return_terminated_segment_count": len(return_segments),
                "unresolved_source_field_path_counts": dict(
                    sorted(unresolved_source_field_path_counts.items())),
                "largest_return_terminated_segments": largest_segments,
                "pc_references": refs[:8],
            })

    return {
        "schema_version": 1,
        "blocker_count": len(blockers),
        "blocker_bytes": sum(blocker["byte_length"] for blocker in blockers),
        "pc_reference_count": sum(blocker["pc_reference_count"] for blocker in blockers),
        "relation_counts": dict(sorted(relation_counts.items())),
        "blockers": blockers,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "blocker_count": report["blocker_count"],
        "blocker_bytes": report["blocker_bytes"],
        "pc_reference_count": report["pc_reference_count"],
        "relation_counts": report["relation_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
