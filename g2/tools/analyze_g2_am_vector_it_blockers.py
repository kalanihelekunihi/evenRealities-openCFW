#!/usr/bin/env python3
"""Pin remaining AM helpers blocked by vector mnemonics or Thumb IT state."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from capstone import CS_ARCH_ARM, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS
from capstone import CS_MODE_THUMB, Cs


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools.analyze_g2_am_mixed_boundary_debt import (
    FUNC_RE,
    INST_RE,
    RAW_SUMMARY,
    classify_values,
    is_it_halfword,
)

OUT = ROOT / "tools/manifests/g2-am-vector-it-blockers.json"


def _decode(md: Cs, values: list[int]) -> list[dict[str, object]]:
    data = b"".join(value.to_bytes(2, "little") for value in values)
    return [
        {
            "offset": instruction.address - 0x1001,
            "mnemonic": instruction.mnemonic,
            "op_str": instruction.op_str,
            "size": instruction.size,
        }
        for instruction in md.disasm(data, 0x1001)
    ]


def _it_offsets(values: list[int]) -> list[int]:
    return [index * 2 for index, value in enumerate(values) if is_it_halfword(value)]


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    blockers = []
    class_counts: dict[str, dict[str, int]] = {}
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
            interesting = [
                reason for reason in (
                    "it_block_requires_conditional_text_or_whole_body_source",
                    "vector_instruction_text_not_apple_clang_roundtrip_safe",
                )
                if reason in reasons
            ]
            if not interesting:
                continue

            decoded = _decode(md, values)
            vector_examples = [
                instruction for instruction in decoded
                if instruction["mnemonic"].lower().startswith("v")
            ][:4]
            record = {
                "source": relative,
                "function": function,
                "byte_length": len(values) * 2,
                "linear_disassembly_bytes": consumed,
                "boundary_kind": "linear" if consumed == len(values) * 2 else "mixed",
                "reasons": sorted(reasons),
                "it_offsets": _it_offsets(values)[:8],
                "vector_examples": vector_examples,
            }
            blockers.append(record)

            key = record["boundary_kind"] + ":" + ",".join(sorted(interesting))
            counts = class_counts.setdefault(key, {"functions": 0, "bytes": 0})
            counts["functions"] += 1
            counts["bytes"] += record["byte_length"]

    return {
        "schema_version": 1,
        "blocker_count": len(blockers),
        "blocker_bytes": sum(blocker["byte_length"] for blocker in blockers),
        "it_blocker_count": sum(
            1 for blocker in blockers
            if "it_block_requires_conditional_text_or_whole_body_source"
            in blocker["reasons"]
        ),
        "vector_blocker_count": sum(
            1 for blocker in blockers
            if "vector_instruction_text_not_apple_clang_roundtrip_safe"
            in blocker["reasons"]
        ),
        "class_counts": dict(sorted(class_counts.items())),
        "blockers": blockers,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "blocker_count": report["blocker_count"],
        "blocker_bytes": report["blocker_bytes"],
        "it_blocker_count": report["it_blocker_count"],
        "vector_blocker_count": report["vector_blocker_count"],
        "class_counts": report["class_counts"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
