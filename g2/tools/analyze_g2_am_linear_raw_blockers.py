#!/usr/bin/env python3
"""Break down remaining AM linear raw-instruction bodies by blocker type."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_g2_am_mixed_boundary_debt import classify_values

RAW_SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
OUT = ROOT / "tools/manifests/g2-am-linear-raw-blockers.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")
BRANCH_BASES = {
    "b", "beq", "bne", "bgt", "blt", "bge", "ble", "bhi", "blo",
    "bhs", "bls", "bpl", "bmi", "bcs", "bcc",
}
SYSTEM_BASES = {
    "bkpt",
    "cdp",
    "cdp2",
    "ldc",
    "ldc2",
    "ldc2l",
    "mcr",
    "mcr2",
    "mcrr",
    "mcrr2",
    "mrc",
    "mrc2",
    "mrrc",
    "mrrc2",
    "svc",
    "stc",
    "stc2",
    "stc2l",
    "udf",
}
STACK_OR_MULTI_BASES = {"push", "pop", "ldm", "stm", "stmdb"}


def _target_offset(op_str: str) -> int | None:
    operand = op_str.split(",")[-1].strip()
    if not operand.startswith("#"):
        return None
    try:
        return int(operand[1:], 0) - 0x1000
    except ValueError:
        return None


def _blockers(md: Cs, values: list[int]) -> tuple[list[str], int] | None:
    reasons, consumed = classify_values(md, values)
    if reasons != {"linear_raw_instruction_text_still_needs_source_model"}:
        return None
    data = b"".join(value.to_bytes(2, "little") for value in values)
    instructions = list(md.disasm(data, 0x1000))
    if consumed != len(data):
        return None
    if sum(instruction.size for instruction in instructions) != len(data):
        return None
    blockers: set[str] = set()
    for instruction in instructions:
        mnemonic = instruction.mnemonic.lower()
        base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        if base in {"bl", "blx"}:
            blockers.add("external_call_or_indirect_branch")
        elif base in BRANCH_BASES or base in {"cbz", "cbnz"}:
            target = _target_offset(op_str)
            if target is None or target < 0 or target > len(data) or target % 2:
                blockers.add("external_or_unmodeled_branch_target")
            else:
                blockers.add("local_branch_control_flow_needs_source_model")
        if base == "adr" or "pc" in f" {op_str}":
            blockers.add("pc_relative_operand")
        if base in STACK_OR_MULTI_BASES:
            blockers.add("stack_or_multi_register_flow")
        if base in SYSTEM_BASES:
            blockers.add("system_or_undefined_decode")
        if mnemonic.startswith("v"):
            blockers.add("vector_decode")
    if not blockers:
        blockers.add("branchless_register_memory_text_needs_semantic_review")
    return sorted(blockers), len(data)


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    class_counts: dict[str, dict[str, int]] = {}
    examples: dict[str, dict[str, object]] = {}
    total_functions = 0
    total_bytes = 0
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        for _macro, function, body in FUNC_RE.findall(path.read_text()):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            result = _blockers(md, values)
            if result is None:
                continue
            blockers, byte_length = result
            key = ",".join(blockers)
            record = class_counts.setdefault(key, {"functions": 0, "bytes": 0})
            record["functions"] += 1
            record["bytes"] += byte_length
            total_functions += 1
            total_bytes += byte_length
            examples.setdefault(key, {
                "source": relative,
                "function": function,
                "byte_length": byte_length,
            })
    return {
        "schema_version": 1,
        "function_count": total_functions,
        "byte_count": total_bytes,
        "blocker_class_counts": {
            key: class_counts[key]
            for key in sorted(
                class_counts,
                key=lambda item: (-class_counts[item]["bytes"], item),
            )
        },
        "examples": examples,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "function_count": report["function_count"],
        "byte_count": report["byte_count"],
        "blocker_class_count": len(report["blocker_class_counts"]),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
