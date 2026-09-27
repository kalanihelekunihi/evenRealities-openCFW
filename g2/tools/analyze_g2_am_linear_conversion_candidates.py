#!/usr/bin/env python3
"""Find AM helper raw-instruction bodies safe for local-label conversion."""

from __future__ import annotations

import json
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs


ROOT = Path(__file__).resolve().parents[1]
RAW_SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
OUT = ROOT / "tools/manifests/g2-am-linear-conversion-candidates.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")
BRANCHES = {
    "b", "beq", "bne", "bgt", "blt", "bge", "ble", "bhi", "blo",
    "bhs", "bls", "bpl", "bmi", "bcs", "bcc",
}
UNSAFE_MNEMONIC_PREFIXES = ("v", "it")


def instruction_target_offset(op_str: str) -> int | None:
    if not op_str.startswith("#"):
        return None
    try:
        return int(op_str[1:], 0) - 0x1000
    except ValueError:
        return None


def classify_body(md: Cs, values: list[int]) -> dict | None:
    data = b"".join(value.to_bytes(2, "little") for value in values)
    instructions = list(md.disasm(data, 0x1000))
    if sum(instruction.size for instruction in instructions) != len(data):
        return None
    targets: set[int] = set()
    has_branch = False
    has_call = False
    has_pc_operand = False
    unsafe_mnemonic = False
    for instruction in instructions:
        mnemonic = instruction.mnemonic.lower()
        mnemonic_base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        if mnemonic_base.startswith("bl"):
            has_call = True
        if mnemonic_base.startswith(UNSAFE_MNEMONIC_PREFIXES):
            unsafe_mnemonic = True
        if mnemonic_base == "adr":
            has_pc_operand = True
        if "pc" in f" {op_str}":
            has_pc_operand = True
        if mnemonic_base in {"cbz", "cbnz"}:
            # Capstone gives register+immediate operands as text.  Keep these
            # out until the converter can parse and label their target safely.
            return None
        if mnemonic_base in BRANCHES:
            has_branch = True
            target = instruction_target_offset(op_str)
            if target is None or target < 0 or target > len(data) or target % 2:
                return None
            targets.add(target)
    if has_call or has_pc_operand or unsafe_mnemonic:
        return None
    if not has_branch:
        return None
    return {
        "byte_length": len(data),
        "instruction_count": len(instructions),
        "branch_targets": sorted(targets),
        "mnemonics": [
            {
                "offset": instruction.address - 0x1000,
                "mnemonic": instruction.mnemonic,
                "op_str": instruction.op_str,
                "size": instruction.size,
            }
            for instruction in instructions
        ],
    }


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    candidates = []
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        for macro, function, body in FUNC_RE.findall(path.read_text()):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            candidate = classify_body(md, values)
            if candidate is None:
                continue
            candidates.append({
                "source": relative,
                "macro": macro,
                "function": function,
                **candidate,
            })
    return {
        "schema_version": 1,
        "candidate_count": len(candidates),
        "candidate_bytes": sum(candidate["byte_length"] for candidate in candidates),
        "candidates": candidates,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "candidate_count": report["candidate_count"],
        "candidate_bytes": report["candidate_bytes"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
