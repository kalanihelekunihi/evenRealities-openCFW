#!/usr/bin/env python3
"""Find small scalar VFP AM helpers safe for local-label conversion."""

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
OUT = ROOT / "tools/manifests/g2-am-scalar-vector-branch-candidates.json"
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
ALLOWED_VECTOR_BASES = {
    "vcmp",
    "vcvt",
    "vldr",
    "vmov",
    "vmrs",
    "vstr",
    "vsub",
}


def target_offset(op_str: str) -> int | None:
    if not op_str.startswith("#"):
        return None
    try:
        return int(op_str[1:], 0) - 0x1000
    except ValueError:
        return None


def classify_body(md: Cs, values: list[int]) -> dict | None:
    reasons, consumed = classify_values(md, values)
    if reasons != {"vector_instruction_text_not_apple_clang_roundtrip_safe"}:
        return None
    data = b"".join(value.to_bytes(2, "little") for value in values)
    instructions = list(md.disasm(data, 0x1000))
    if consumed != len(data) or sum(instruction.size for instruction in instructions) != len(data):
        return None
    if len(data) > 48:
        return None
    targets: set[int] = set()
    has_vector = False
    has_branch = False
    for instruction in instructions:
        mnemonic = instruction.mnemonic.lower()
        mnemonic_base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        if mnemonic_base.startswith("bl") or mnemonic_base in {"blx", "bx", "cbz", "cbnz"}:
            return None
        if mnemonic_base.startswith("v"):
            has_vector = True
            if mnemonic_base not in ALLOWED_VECTOR_BASES:
                return None
        if mnemonic_base in {"adr", "mcr", "mcr2", "mrc", "mrc2", "ldc", "ldc2", "stc", "stc2"}:
            return None
        if "pc" in f" {op_str}" and mnemonic_base != "vldr":
            return None
        if mnemonic_base in BRANCHES:
            has_branch = True
            target = target_offset(op_str)
            if target is None or target < 0 or target > len(data) or target % 2:
                return None
            targets.add(target)
    if not has_vector or not has_branch:
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
