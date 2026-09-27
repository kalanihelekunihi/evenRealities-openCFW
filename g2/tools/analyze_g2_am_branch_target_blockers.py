#!/usr/bin/env python3
"""Classify branch/call targets inside remaining AM linear raw bodies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_GRP_CALL, CS_GRP_JUMP
from capstone import CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS, CS_MODE_THUMB, Cs
from capstone.arm_const import ARM_OP_IMM


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_g2_am_linear_raw_blockers import FUNC_RE, INST_RE, RAW_SUMMARY, _blockers

OUT = ROOT / "tools/manifests/g2-am-branch-target-blockers.json"
ENTRY_RE = re.compile(r"_(?:0x)?([0-9a-f]+)$")


def _entry(function: str) -> int:
    match = ENTRY_RE.search(function)
    if match is None:
        raise ValueError(f"missing helper entry in {function}")
    return int(match.group(1), 16)


def _load_am_functions() -> list[dict[str, object]]:
    summary = json.loads(RAW_SUMMARY.read_text())
    functions = []
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        for macro, function, body in FUNC_RE.findall(path.read_text()):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            functions.append({
                "source": relative,
                "macro": macro,
                "function": function,
                "entry": _entry(function),
                "values": values,
            })
    return functions


def analyze() -> dict:
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    md.detail = True
    functions = _load_am_functions()
    known_entries = {
        function["entry"]: {
            "source": function["source"],
            "function": function["function"],
        }
        for function in functions
    }

    relation_counts: dict[str, int] = {}
    examples: dict[str, dict[str, object]] = {}
    function_count = 0
    byte_count = 0
    for function in functions:
        values = function["values"]
        blockers = _blockers(md, values)
        if blockers is None or not (
            "external_call_or_indirect_branch" in blockers[0]
            or "external_or_unmodeled_branch_target" in blockers[0]
            or "local_branch_control_flow_needs_source_model" in blockers[0]
        ):
            continue

        data = b"".join(value.to_bytes(2, "little") for value in values)
        entry = int(function["entry"])
        end = entry + len(data)
        function_count += 1
        byte_count += len(data)
        for instruction in md.disasm(data, entry):
            base = instruction.mnemonic.lower().split(".", 1)[0]
            if not (
                instruction.group(CS_GRP_JUMP)
                or instruction.group(CS_GRP_CALL)
                or base in {"cbz", "cbnz"}
            ):
                continue
            target = None
            if instruction.operands and instruction.operands[-1].type == ARM_OP_IMM:
                target = instruction.operands[-1].imm & ~1

            site_kind = "call" if instruction.group(CS_GRP_CALL) else "branch"
            if target is None:
                relation = "indirect_or_no_imm"
            elif entry <= target < end:
                relation = "inside_body"
            elif target in known_entries:
                relation = "known_am_helper_entry"
            else:
                relation = "outside_unmodeled"

            key = f"{site_kind}:{relation}"
            relation_counts[key] = relation_counts.get(key, 0) + 1
            examples.setdefault(key, {
                "source": function["source"],
                "function": function["function"],
                "site": f"0x{instruction.address:08x}",
                "instruction": f"{instruction.mnemonic} {instruction.op_str}".strip(),
                "target": None if target is None else f"0x{target:08x}",
            })

    return {
        "schema_version": 1,
        "function_count": function_count,
        "byte_count": byte_count,
        "site_count": sum(relation_counts.values()),
        "relation_counts": dict(sorted(relation_counts.items())),
        "examples": examples,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "function_count": report["function_count"],
        "byte_count": report["byte_count"],
        "site_count": report["site_count"],
        "relation_counts": report["relation_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
