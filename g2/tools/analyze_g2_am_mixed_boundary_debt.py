#!/usr/bin/env python3
"""Classify remaining AM helper raw-instruction sources by boundary risk."""

from __future__ import annotations

import json
import re
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs


ROOT = Path(__file__).resolve().parents[1]
RAW_SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
OUT = ROOT / "tools/manifests/g2-am-mixed-boundary-debt-summary.json"
FUNC_RE = re.compile(
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")


def sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def is_it_halfword(value: int) -> bool:
    return (value & 0xFF00) == 0xBF00 and (value & 0x000F) != 0


def classify_values(md: Cs, values: list[int]) -> tuple[set[str], int]:
    data = b"".join(value.to_bytes(2, "little") for value in values)
    reasons: set[str] = set()
    if any(is_it_halfword(value) for value in values):
        reasons.add("it_block_requires_conditional_text_or_whole_body_source")
    consumed = 0
    for insn in md.disasm(data, 0x1001):
        consumed += insn.size
        mnemonic = insn.mnemonic.lower()
        if mnemonic.startswith("v"):
            reasons.add("vector_instruction_text_not_apple_clang_roundtrip_safe")
        if " pc" in f" {insn.op_str.lower()}" and "," in insn.op_str:
            reasons.add("pc_relative_or_pc_operand_needs_boundary_model")
    if consumed != len(data):
        reasons.add("nonlinear_data_or_literal_island")
    if not reasons:
        reasons.add("linear_raw_instruction_text_still_needs_source_model")
    return reasons, consumed


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    rows = []
    function_class_counts: dict[str, dict[str, int]] = {}
    for source in summary["public_unrouted_raw_instruction_sources"]:
        relative = source["source"]
        if not relative.startswith("components/apollo_main/core_overlay/runtime_liblc3_am"):
            continue
        path = ROOT / relative
        text = path.read_text()
        file_reasons: set[str] = set()
        function_rows = []
        for function, body in FUNC_RE.findall(text):
            values = [int(value, 16) for value in INST_RE.findall(body)]
            if not values:
                continue
            reasons, consumed = classify_values(md, values)
            if reasons:
                linear = consumed == len(values) * 2
                class_key = (
                    ("linear" if linear else "mixed")
                    + ":"
                    + ",".join(sorted(reasons))
                )
                class_record = function_class_counts.setdefault(
                    class_key, {"functions": 0, "bytes": 0}
                )
                class_record["functions"] += 1
                class_record["bytes"] += len(values) * 2
                function_rows.append({
                    "function": function,
                    "byte_length": len(values) * 2,
                    "linear_disassembly_bytes": consumed,
                    "reasons": sorted(reasons),
                })
                file_reasons.update(reasons)
        function_rows.sort(
            key=lambda row: (-row["byte_length"], row["function"])
        )
        rows.append({
            "source": relative,
            "inst_directive_bytes": source["inst_directive_bytes"],
            "source_sha256": sha256(path.read_bytes()),
            "function_count": len(FUNC_RE.findall(text)),
            "blocked_function_count": len(function_rows),
            "blocked_function_bytes": sum(
                row["byte_length"] for row in function_rows),
            "reasons": sorted(file_reasons or {"unclassified_mixed_boundary"}),
            "blocked_functions": function_rows,
        })
    return {
        "schema_version": 1,
        "source_count": len(rows),
        "inst_directive_bytes": sum(row["inst_directive_bytes"] for row in rows),
        "reason_counts": {
            reason: sum(1 for row in rows if reason in row["reasons"])
            for reason in sorted({reason for row in rows for reason in row["reasons"]})
        },
        "function_class_counts": {
            key: function_class_counts[key]
            for key in sorted(
                function_class_counts,
                key=lambda item: (
                    -function_class_counts[item]["bytes"],
                    item,
                ),
            )
        },
        "sources": rows,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "source_count": report["source_count"],
        "inst_directive_bytes": report["inst_directive_bytes"],
        "reason_counts": report["reason_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
