#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Persist the authenticated Ghidra decompilation for the final case frontier."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "tools/manifests/g2-box-ghidra-decomp.c"
FRONTIER = ROOT / "tools/manifests/g2-case-final-function-frontier.tsv"
OUTPUT = ROOT / "research/corpus/case/ghidra/final-frontier"
MARKER = re.compile(r"^/\* FUN 0x([0-9A-Fa-f]{8}) ([^*]+?) \*/\n", re.MULTILINE)
CALL = re.compile(r"\b(?:FUN|thunk_FUN)_([0-9A-Fa-f]{8})\b")


class ExtractionError(RuntimeError):
    """Raised when the authenticated case inputs no longer reconcile."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_frontier() -> list[dict[str, str]]:
    with FRONTIER.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(
            (line for line in handle if not line.startswith("#")),
            delimiter="\t",
        ))


def split_decompilation() -> dict[int, dict[str, str]]:
    text = SOURCE.read_text(encoding="utf-8")
    markers = list(MARKER.finditer(text))
    functions: dict[int, dict[str, str]] = {}
    for index, marker in enumerate(markers):
        start = marker.start()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        address = int(marker.group(1), 16)
        if address in functions:
            raise ExtractionError(f"duplicate Ghidra function at {address:#010x}")
        functions[address] = {
            "name": marker.group(2).strip(),
            "decompilation": text[start:end].rstrip() + "\n",
        }
    return functions


def extract() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    frontier = read_frontier()
    decompiled = split_decompilation()
    if len(frontier) != 222:
        raise ExtractionError(f"expected 222 final-frontier functions, got {len(frontier)}")

    rows: list[dict[str, object]] = []
    calls: list[dict[str, object]] = []
    for row in frontier:
        address = int(row["entry"], 0)
        record = decompiled.get(address)
        if record is None:
            raise ExtractionError(f"missing Ghidra decompilation at {address:#010x}")
        body = record["decompilation"]
        # The Ghidra marker names the current function; only scan the actual
        # decompiler body so every record does not acquire a synthetic self-edge.
        decompiler_body = body.split("{", 1)[1]
        callees = sorted({int(value, 16)
                          for value in CALL.findall(decompiler_body)})
        output = {
            "address": address,
            "address_hex": f"0x{address:08X}",
            "name": row["name"],
            "ghidra_name": record["name"],
            "size": int(row["size"], 0),
            "instruction_sha256": row["instruction_sha256"],
            "prior_classification": row["classification"],
            "decompilation_sha256": sha256(body.encode("utf-8")),
            "callees": [f"0x{callee:08X}" for callee in callees],
            "decompilation": body,
        }
        rows.append(output)
        for callee in callees:
            calls.append({
                "caller": address,
                "callee": callee,
                "callee_in_frontier": any(
                    int(item["entry"], 0) == callee for item in frontier
                ),
            })

    rows.sort(key=lambda item: int(item["address"]))
    calls.sort(key=lambda item: (int(item["caller"]), int(item["callee"])))
    harvest = {
        "schema_version": 1,
        "component": "G2 charging-case final function frontier",
        "analysis_mode": "offline authenticated Ghidra corpus extraction",
        "source": str(SOURCE.relative_to(ROOT)),
        "frontier": str(FRONTIER.relative_to(ROOT)),
        "source_sha256": sha256(SOURCE.read_bytes()),
        "frontier_sha256": sha256(FRONTIER.read_bytes()),
        "functions": len(rows),
        "instruction_bytes": sum(int(row["size"]) for row in rows),
        "call_edges": len(calls),
        "project_source_candidates": sum(
            row["prior_classification"] == "project_source_candidate_not_routed"
            for row in rows
        ),
        "software_recovery_frontier": sum(
            row["prior_classification"] != "project_source_candidate_not_routed"
            for row in rows
        ),
        "hardware_operations": [],
    }
    return rows, calls, harvest


def render(rows: list[dict[str, object]], calls: list[dict[str, object]],
           harvest: dict[str, object]) -> dict[str, bytes]:
    functions = b"".join(
        (json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n").encode()
        for row in rows
    )
    call_lines = ["# SPDX-License-Identifier: MIT\n",
                  "caller\tcallee\tcallee_in_frontier\n"]
    call_lines.extend(
        f"0x{int(row['caller']):08X}\t0x{int(row['callee']):08X}\t"
        f"{str(bool(row['callee_in_frontier'])).lower()}\n"
        for row in calls
    )
    return {
        "functions.jsonl": functions,
        "calls.tsv": "".join(call_lines).encode(),
        "HARVEST.json": (json.dumps(harvest, indent=2, sort_keys=True) + "\n").encode(),
    }


def write_outputs(files: dict[str, bytes]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (OUTPUT / name).write_bytes(data)
    sums = "".join(
        f"{sha256(files[name])}  {name}\n" for name in sorted(files)
    )
    (OUTPUT / "SHA256SUMS").write_text(sums, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    rows, calls, harvest = extract()
    files = render(rows, calls, harvest)
    if args.write:
        write_outputs(files)
    print(json.dumps(harvest, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
