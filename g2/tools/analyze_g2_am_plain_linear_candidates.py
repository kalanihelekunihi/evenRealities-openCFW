#!/usr/bin/env python3
"""Find branchless AM helper raw bodies safe for mnemonic conversion."""

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
OUT = ROOT / "tools/manifests/g2-am-plain-linear-candidates.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")
BLOCKED_BASES = {
    "adr",
    "b",
    "bfc",
    "bfi",
    "bkpt",
    "bl",
    "blx",
    "bx",
    "cbnz",
    "cbz",
    "cdp",
    "cdp2",
    "it",
    "ldc",
    "ldc2",
    "ldc2l",
    "ldm",
    "mcr",
    "mcr2",
    "mcrr",
    "mcrr2",
    "mrc",
    "mrc2",
    "mrrc",
    "mrrc2",
    "pop",
    "push",
    "svc",
    "stc",
    "stc2",
    "stc2l",
    "stm",
    "stmdb",
    "udf",
}


def classify_body(md: Cs, values: list[int]) -> dict | None:
    reasons, consumed = classify_values(md, values)
    if reasons:
        return None
    data = b"".join(value.to_bytes(2, "little") for value in values)
    instructions = list(md.disasm(data, 0x1000))
    if consumed != len(data):
        return None
    if sum(instruction.size for instruction in instructions) != len(data):
        return None
    if len(data) > 32:
        return None
    for instruction in instructions:
        mnemonic = instruction.mnemonic.lower()
        mnemonic_base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        if mnemonic.startswith("v") or mnemonic_base in BLOCKED_BASES:
            return None
        if mnemonic_base.startswith("b"):
            return None
        if "pc" in f" {op_str}":
            return None
        if mnemonic == "movs" and op_str == "r0, r0" and len(instructions) > 1:
            return None
    return {
        "byte_length": len(data),
        "instruction_count": len(instructions),
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
