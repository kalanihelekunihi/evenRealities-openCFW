#!/usr/bin/env python3
"""Find AM helpers whose raw bodies are only 0x0000 Thumb halfwords."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_SUMMARY = ROOT / "tools/manifests/g2-production-raw-encoding-quality-summary.json"
OUT = ROOT / "tools/manifests/g2-am-zero-halfword-padding-candidates.json"
FUNC_RE = re.compile(
    r"#if defined\((OPEN_CFW_AM\d+_[A-Z0-9X]+_ONLY)\).*?"
    r"void\s+(open_cfw_runtime_am\d+_(?:0x)?[0-9a-f]+)\(void\).*?"
    r"__asm__ volatile\(\n(.*?)    \);\n}\n#endif",
    re.S,
)
INST_RE = re.compile(r"\.inst\.n 0x([0-9a-fA-F]{4})")


def analyze() -> dict:
    summary = json.loads(RAW_SUMMARY.read_text())
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
            if any(value != 0 for value in values):
                continue
            candidates.append({
                "source": relative,
                "macro": macro,
                "function": function,
                "byte_length": len(values) * 2,
                "halfword_count": len(values),
                "mnemonic": "movs r0, r0",
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
