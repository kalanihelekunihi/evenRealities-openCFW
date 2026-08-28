#!/usr/bin/env python3
"""Normalize the reviewed Ghidra PT-protocol dump into a pinned corpus."""
# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FUNCTION_MAP = ROOT / "tools/manifests/g2-pt-protocol-function-map.tsv"
DEFAULT_OUTPUT = ROOT / "research/corpus/apollo-main/ghidra/pt-protocol"

FUNCTION_RE = re.compile(
    r"FUNCTION\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+([0-9a-fA-F]+)\s+(\S+)"
)
REFERENCE_RE = re.compile(r"REFERENCE\s+([0-9a-fA-F]+)\s+(.+?)\s*(?:\(GhidraScript\))?$")

# Recovered from the authenticated dispatch table in G2 2.2.6.10.  The map is
# deliberately address-based: names inferred by a decompiler are not evidence.
COMMAND_HANDLERS = (
    (0x01, 0x0056FC0C), (0x05, 0x0057293C), (0x06, 0x00572A34),
    (0x07, 0x00572AF0), (0x08, 0x00572BA0), (0x0B, 0x0056FFC4),
    (0x11, 0x0056FDB4), (0x13, 0x00570780), (0x17, 0x005709C4),
    (0x18, 0x00570D40), (0x19, 0x00571064), (0x1A, 0x005713D8),
    (0x1B, 0x0057200C), (0x1C, 0x00570570), (0x20, 0x00571CD4),
    (0x22, 0x00571E44), (0x24, 0x005726F0), (0x25, 0x00572858),
    (0x26, 0x0057222C), (0x29, 0x00572394), (0x2A, 0x00572C64),
    (0x2D, 0x00570210), (0x2E, 0x00570B60), (0x30, 0x005724F4),
    (0x31, 0x0057303C), (0x35, 0x0057320C), (0x38, 0x00573310),
    (0x39, 0x005734CC), (0x3A, 0x00573604), (0x3D, 0x005738D0),
    (0x3E, 0x00573C58), (0x42, 0x00573F88), (0x43, 0x005741E0),
    (0x44, 0x00574464), (0x45, 0x00570438), (0x46, 0x00574580),
    (0x47, 0x00574808), (0x48, 0x00574F60), (0x49, 0x0057522C),
    (0x52, 0x00575470), (0x53, 0x00575548), (0x54, 0x00575708),
    (0x55, 0x005759FC), (0x57, 0x0057536C), (0x58, 0x00575AF8),
    (0x59, 0x00575EB4), (0x5A, 0x0057612C), (0x5B, 0x00576518),
    (0x60, 0x00576714), (0x61, 0x00576800), (0x62, 0x005768C8),
    (0x63, 0x00576A54), (0x64, 0x00576BD4), (0x65, 0x00576D48),
    (0x66, 0x00576DF8), (0x67, 0x00576FD0), (0x69, 0x005770CC),
    (0x6A, 0x005771D4), (0x6B, 0x00577364), (0x6C, 0x0057747C),
    (0x6D, 0x0057757C), (0x6E, 0x00577678), (0x74, 0x00577794),
    (0x75, 0x005778D4), (0x77, 0x005779E0), (0xF3, 0x00577AFC),
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _payload(line: str) -> str:
    marker = "CreateAndDumpFunctions.java> "
    return line.split(marker, 1)[1] if marker in line else line


def parse_log(text: str) -> list[dict]:
    """Parse a CreateAndDumpFunctions log without trusting log prefixes."""
    records: list[dict] = []
    current: dict | None = None
    body: list[str] | None = None

    for raw_line in text.splitlines():
        line = _payload(raw_line)
        function = FUNCTION_RE.search(line)
        if function:
            if current is not None:
                raise ValueError("function marker encountered before decompile end")
            current = {
                "entry": int(function.group(1), 16),
                "body_min": int(function.group(2), 16),
                "body_max_inclusive": int(function.group(3), 16),
                "ghidra_name": function.group(4),
                "references": [],
            }
            continue
        if current is None:
            continue
        reference = REFERENCE_RE.search(line)
        if reference and body is None:
            current["references"].append(
                {"from": int(reference.group(1), 16), "type": reference.group(2).strip()}
            )
            continue
        if "DECOMPILE_ERROR" in line:
            raise ValueError(f"decompiler error for 0x{current['entry']:08X}: {line}")
        if "DECOMPILE_BEGIN" in line:
            if body is not None:
                raise ValueError("nested decompile begin")
            body = []
            continue
        if "DECOMPILE_END" in line:
            if body is None:
                raise ValueError("decompile end without begin")
            c_text = "\n".join(body).strip() + "\n"
            current["decompilation"] = c_text
            current["decompilation_sha256"] = sha256(c_text.encode())
            records.append(current)
            current = None
            body = None
            continue
        if body is not None:
            body.append(line)

    if current is not None or body is not None:
        raise ValueError("unterminated decompilation")
    if not records:
        raise ValueError("no decompilations found")
    entries = [record["entry"] for record in records]
    if len(entries) != len(set(entries)):
        raise ValueError("duplicate function entry")
    return records


def expected_functions() -> list[dict]:
    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def validate(records: list[dict]) -> list[dict]:
    expected = expected_functions()
    expected_entries = [int(row["stock_start"], 0) for row in expected]
    actual_entries = [record["entry"] for record in records]
    if actual_entries != expected_entries:
        raise ValueError("decompiler entries do not exactly match the reviewed function map")
    by_entry = {record["entry"]: record for record in records}
    for command, handler in COMMAND_HANDLERS:
        if handler not in by_entry:
            raise ValueError(f"command 0x{command:02X} handler is absent")
    if len(COMMAND_HANDLERS) != 66:
        raise ValueError("command table does not contain 66 entries")
    if len({command for command, _ in COMMAND_HANDLERS}) != 66:
        raise ValueError("duplicate command")
    if len({handler for _, handler in COMMAND_HANDLERS}) != 66:
        raise ValueError("duplicate command handler")
    return expected


def emit(input_path: Path, output: Path) -> dict:
    input_bytes = input_path.read_bytes()
    records = parse_log(input_bytes.decode("utf-8"))
    expected = validate(records)
    row_by_entry = {int(row["stock_start"], 0): row for row in expected}
    command_by_handler = {handler: command for command, handler in COMMAND_HANDLERS}

    output.mkdir(parents=True, exist_ok=True)
    jsonl = output / "functions.jsonl"
    with jsonl.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            row = row_by_entry[record["entry"]]
            normalized = {
                "ordinal": int(row["ordinal"]),
                "stock_start": f"0x{record['entry']:08X}",
                "stock_end_exclusive": row["stock_end_exclusive"],
                "ghidra_body_max_inclusive": f"0x{record['body_max_inclusive']:08X}",
                "ghidra_name": record["ghidra_name"],
                "role": row["role"],
                "path_anchored": row["path_anchored"] == "yes",
                "command": (
                    f"0x{command_by_handler[record['entry']]:02X}"
                    if record["entry"] in command_by_handler else None
                ),
                "references": [
                    {"from": f"0x{item['from']:08X}", "type": item["type"]}
                    for item in record["references"]
                ],
                "decompilation_sha256": record["decompilation_sha256"],
                "decompilation": record["decompilation"],
            }
            handle.write(json.dumps(normalized, sort_keys=True, separators=(",", ":")) + "\n")

    command_map = output / "command-map.tsv"
    with command_map.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write("command\thandler_stock_start\thandler_ordinal\tdecompilation_sha256\n")
        record_by_entry = {record["entry"]: record for record in records}
        for command, handler in COMMAND_HANDLERS:
            handle.write(
                f"0x{command:02X}\t0x{handler:08X}\t"
                f"{row_by_entry[handler]['ordinal']}\t"
                f"{record_by_entry[handler]['decompilation_sha256']}\n"
            )

    summary = {
        "schema_version": 1,
        "source": {
            "artifact": "authenticated G2 2.2.6.10 Apollo-main image",
            "tool": "Ghidra CreateAndDumpFunctions.java",
            "input_log_sha256": sha256(input_bytes),
        },
        "surface": {
            "functions": len(records),
            "command_handlers": len(COMMAND_HANDLERS),
            "helper_or_orchestration_functions": len(records) - len(COMMAND_HANDLERS),
            "first_entry": f"0x{records[0]['entry']:08X}",
            "last_entry": f"0x{records[-1]['entry']:08X}",
        },
        "status": {
            "semantic_evidence_complete": True,
            "production_c_implemented": False,
            "production_routed": False,
        },
    }
    harvest = output / "HARVEST.json"
    harvest.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    sums = output / "SHA256SUMS"
    artifacts = ("HARVEST.json", "command-map.tsv", "functions.jsonl")
    sums.write_text(
        "".join(f"{sha256((output / name).read_bytes())}  {name}\n" for name in artifacts),
        encoding="utf-8",
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path, help="Ghidra headless output")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(json.dumps(emit(args.input, args.output), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
