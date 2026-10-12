#!/usr/bin/env python3
"""Crosswalk overflowing image-A XIP entries to native call edges and C relocations."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"
NATIVE = ROOT / "g2/research/corpus/codec/ghidra/open-2026-09-29/image_a_xip/functions-000.jsonl"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--eligibility", type=Path, default=HERE / "xip-link-eligibility-os-manifest.json")
    parser.add_argument("--candidate", type=Path, default=ROOT / "g2/build/c-firmware/20261011/codec-xip-os-policy-round/codec/candidate.o")
    parser.add_argument("--output", type=Path, default=HERE / "xip-overflow-relocation-crosswalk.json")
    args = parser.parse_args()
    eligibility = json.loads(args.eligibility.read_text())
    native = [json.loads(line) for line in NATIVE.read_text().splitlines()]
    text = subprocess.run([str(READELF), "-rW", str(args.candidate)], check=True, capture_output=True, text=True).stdout
    rows = []
    for slot in eligibility["native_function_slots"]:
        if slot["placement_status"] != "section_slot_overflow":
            continue
        entry = slot["entry"][2:]
        symbol = slot["direct_symbols"][0]["name"]
        callers = ["0x" + function["entry"] for function in native if entry in function.get("callees", [])]
        relocations = len(re.findall(r"\b" + re.escape(symbol) + r"\b", text))
        rows.append({"entry": slot["entry"], "native_name": slot["native_name"],
                     "excess_section_bytes_if_fixed": slot["excess_section_bytes_if_fixed"],
                     "candidate_symbol": symbol, "native_direct_callers": callers,
                     "candidate_symbolic_relocations": relocations})
    result = {
        "eligibility_sha256": digest(args.eligibility), "candidate_sha256": digest(args.candidate),
        "native_catalogue_sha256": digest(NATIVE), "readelf_sha256": digest(READELF),
        "overflows": len(rows),
        "native_direct_caller_edges": sum(len(row["native_direct_callers"]) for row in rows),
        "with_native_direct_callers": sum(bool(row["native_direct_callers"]) for row in rows),
        "candidate_symbolic_relocations": sum(row["candidate_symbolic_relocations"] for row in rows),
        "with_candidate_symbolic_relocations": sum(bool(row["candidate_symbolic_relocations"]) for row in rows),
        "without_candidate_symbolic_relocations": [row["entry"] for row in rows if not row["candidate_symbolic_relocations"]],
        "rows": rows,
        "limits": ["Native catalogue callees record direct function edges, not indirect callbacks or outside-stage callers.",
                   "Candidate relocations prove symbols are patchable at link, not that every native reference was reconstructed.",
                   "Final branch reach, XIP space allocation, all literal pools, aliases and loader scatter are not qualified."],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({key: result[key] for key in ("overflows", "native_direct_caller_edges", "candidate_symbolic_relocations", "with_candidate_symbolic_relocations", "without_candidate_symbolic_relocations")})


if __name__ == "__main__":
    main()
