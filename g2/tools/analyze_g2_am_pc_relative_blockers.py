#!/usr/bin/env python3
"""Pin AM helper bodies blocked only by PC-relative out-of-body operands."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_g2_am_linear_raw_blockers import _blockers

RAW_SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
OUT = ROOT / "tools/manifests/g2-am-pc-relative-blockers.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")


def _immediate_target(op_str: str) -> int | None:
    operand = op_str.split(",")[-1].strip()
    if not operand.startswith("#"):
        return None
    try:
        return int(operand[1:], 0) - 0x1000
    except ValueError:
        return None


def _ldr_pc_target(offset: int, op_str: str) -> int | None:
    match = re.search(r"\[pc(?:,\s*#(0x[0-9a-fA-F]+|\d+))?\]", op_str)
    if match is None:
        return None
    immediate = int(match.group(1), 0) if match.group(1) else 0
    return ((offset + 4) & ~3) + immediate


def classify_body(md: Cs, values: list[int]) -> dict | None:
    blockers = _blockers(md, values)
    if blockers is None or blockers[0] != ["pc_relative_operand"]:
        return None

    data = b"".join(value.to_bytes(2, "little") for value in values)
    references = []
    for instruction in md.disasm(data, 0x1000):
        offset = instruction.address - 0x1000
        mnemonic = instruction.mnemonic.lower()
        base = mnemonic.split(".", 1)[0]
        op_str = instruction.op_str.lower()
        target = None
        if base == "adr":
            target = _immediate_target(op_str)
        elif "pc" in f" {op_str}":
            target = _ldr_pc_target(offset, op_str)
        if target is None:
            continue
        references.append({
            "offset": offset,
            "instruction": f"{instruction.mnemonic} {instruction.op_str}".strip(),
            "target_offset": target,
            "target_relation": "inside_body" if 0 <= target < len(data) else "outside_body",
        })

    if not references:
        return None
    outside_count = sum(
        1 for reference in references
        if reference["target_relation"] == "outside_body"
    )
    return {
        "byte_length": len(data),
        "instruction_count": sum(1 for _ in md.disasm(data, 0x1000)),
        "pc_reference_count": len(references),
        "outside_body_reference_count": outside_count,
        "references": references,
    }


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    blockers = []
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        for macro, function, body in FUNC_RE.findall(path.read_text()):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            blocked = classify_body(md, values)
            if blocked is None:
                continue
            blockers.append({
                "source": relative,
                "macro": macro,
                "function": function,
                **blocked,
            })

    return {
        "schema_version": 1,
        "blocker_count": len(blockers),
        "blocker_bytes": sum(blocker["byte_length"] for blocker in blockers),
        "outside_body_reference_count": sum(
            blocker["outside_body_reference_count"] for blocker in blockers
        ),
        "blockers": blockers,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "blocker_count": report["blocker_count"],
        "blocker_bytes": report["blocker_bytes"],
        "outside_body_reference_count": report["outside_body_reference_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
