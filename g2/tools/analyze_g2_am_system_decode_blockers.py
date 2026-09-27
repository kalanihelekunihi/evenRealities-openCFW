#!/usr/bin/env python3
"""Pin AM helper bodies blocked only by system/undefined instruction decodes."""

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
OUT = ROOT / "tools/manifests/g2-am-system-decode-blockers.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")
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


def _longest_zero_halfword_run(values: list[int]) -> int:
    longest = 0
    current = 0
    for value in values:
        if value == 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def classify_body(md: Cs, values: list[int]) -> dict | None:
    blockers = _blockers(md, values)
    if blockers is None or blockers[0] != ["system_or_undefined_decode"]:
        return None

    data = b"".join(value.to_bytes(2, "little") for value in values)
    system_counts: dict[str, int] = {}
    instruction_count = 0
    examples = []
    for instruction in md.disasm(data, 0x1000):
        instruction_count += 1
        base = instruction.mnemonic.lower().split(".", 1)[0]
        if base not in SYSTEM_BASES:
            continue
        system_counts[base] = system_counts.get(base, 0) + 1
        if len(examples) < 4:
            examples.append({
                "offset": instruction.address - 0x1000,
                "instruction": f"{instruction.mnemonic} {instruction.op_str}".strip(),
            })

    return {
        "byte_length": len(data),
        "instruction_count": instruction_count,
        "system_instruction_count": sum(system_counts.values()),
        "zero_halfword_count": values.count(0),
        "longest_zero_halfword_run": _longest_zero_halfword_run(values),
        "system_counts": dict(sorted(system_counts.items())),
        "system_examples": examples,
    }


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
    md = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_MCLASS | CS_MODE_LITTLE_ENDIAN)
    blockers = []
    aggregate_system_counts: dict[str, int] = {}
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
            for key, value in blocked["system_counts"].items():
                aggregate_system_counts[key] = aggregate_system_counts.get(key, 0) + value
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
        "system_instruction_count": sum(
            blocker["system_instruction_count"] for blocker in blockers
        ),
        "zero_halfword_count": sum(blocker["zero_halfword_count"] for blocker in blockers),
        "aggregate_system_counts": dict(sorted(aggregate_system_counts.items())),
        "blockers": blockers,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "blocker_count": report["blocker_count"],
        "blocker_bytes": report["blocker_bytes"],
        "system_instruction_count": report["system_instruction_count"],
        "zero_halfword_count": report["zero_halfword_count"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
