#!/usr/bin/env python3
"""Summarize untracked overlay source inputs used by production manifests."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import analyze_g2_production_raw_encoding_quality as raw_quality


OUT = ROOT / "tools/manifests/g2-untracked-overlay-inputs.json"
AM_HELPER_RE = re.compile(r"runtime_liblc3_am(\d+)_helpers\.c$")


def _digest(values: object) -> str:
    return hashlib.sha256(json.dumps(
        values, sort_keys=True, separators=(",", ":")
    ).encode()).hexdigest()


def _ranges(values: list[int]) -> list[dict[str, int]]:
    if not values:
        return []
    ordered = sorted(values)
    ranges = []
    start = previous = ordered[0]
    for value in ordered[1:]:
        if value == previous + 1:
            previous = value
            continue
        ranges.append({"first": start, "last": previous, "count": previous - start + 1})
        start = previous = value
    ranges.append({"first": start, "last": previous, "count": previous - start + 1})
    return ranges


def analyze() -> dict:
    quality = raw_quality.analyze()
    paths = quality["untracked_overlay_source_inputs"]
    rows = []
    family_counts: dict[str, int] = {}
    am_numbers = []
    raw_bearing_inputs = []
    non_raw_inputs = []
    raw_bearing_am_numbers = []
    non_raw_am_numbers = []
    total_bytes = 0
    total_inst_directive_bytes = 0
    for relative in paths:
        path = ROOT / relative
        text = path.read_text()
        raw = path.read_bytes()
        total_bytes += len(raw)
        directive_bytes = raw_quality._directive_bytes(text)
        inst_directive_bytes = (
            directive_bytes["inst"]
            + directive_bytes["inst.n"]
            + directive_bytes["inst.w"]
        )
        total_inst_directive_bytes += inst_directive_bytes
        if inst_directive_bytes:
            raw_bearing_inputs.append(relative)
        else:
            non_raw_inputs.append(relative)
        match = AM_HELPER_RE.match(path.name)
        family = "runtime_liblc3_am_helpers" if match else "other"
        family_counts[family] = family_counts.get(family, 0) + 1
        if match:
            am_number = int(match.group(1))
            am_numbers.append(am_number)
            if inst_directive_bytes:
                raw_bearing_am_numbers.append(am_number)
            else:
                non_raw_am_numbers.append(am_number)
        rows.append({
            "source": relative,
            "bytes": len(raw),
            "inst_directive_bytes": inst_directive_bytes,
            "sha256": hashlib.sha256(raw).hexdigest(),
            "family": family,
        })

    return {
        "schema_version": 1,
        "input_count": len(paths),
        "total_source_bytes": total_bytes,
        "total_inst_directive_bytes": total_inst_directive_bytes,
        "raw_bearing_input_count": len(raw_bearing_inputs),
        "non_raw_input_count": len(non_raw_inputs),
        "raw_bearing_input_path_sha256": _digest(raw_bearing_inputs),
        "non_raw_input_path_sha256": _digest(non_raw_inputs),
        "raw_bearing_am_helper_ranges": _ranges(raw_bearing_am_numbers),
        "non_raw_am_helper_ranges": _ranges(non_raw_am_numbers),
        "path_set_sha256": _digest(paths),
        "family_counts": dict(sorted(family_counts.items())),
        "am_helper_range": {
            "first": min(am_numbers) if am_numbers else None,
            "last": max(am_numbers) if am_numbers else None,
            "count": len(am_numbers),
            "missing": [
                number for number in range(min(am_numbers), max(am_numbers) + 1)
                if number not in set(am_numbers)
            ] if am_numbers else [],
        },
        "largest_inputs": sorted(
            rows, key=lambda row: (-row["inst_directive_bytes"], row["source"])
        )[:12],
        "rows": rows,
    }


def main() -> int:
    report = analyze()
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "input_count": report["input_count"],
        "total_source_bytes": report["total_source_bytes"],
        "total_inst_directive_bytes": report["total_inst_directive_bytes"],
        "raw_bearing_input_count": report["raw_bearing_input_count"],
        "non_raw_input_count": report["non_raw_input_count"],
        "raw_bearing_am_helper_ranges": report["raw_bearing_am_helper_ranges"],
        "non_raw_am_helper_ranges": report["non_raw_am_helper_ranges"],
        "family_counts": report["family_counts"],
        "am_helper_range": report["am_helper_range"],
        "path_set_sha256": report["path_set_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
