#!/usr/bin/env python3
"""Classify source-GC exclusions without equating them to absent native roots."""
import argparse
import hashlib
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--closure", type=Path, required=True)
    parser.add_argument("--gc-receipt", type=Path, required=True)
    parser.add_argument("--xip-eligibility", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    closure = json.loads(args.closure.read_text())
    gc = json.loads(args.gc_receipt.read_text())
    eligibility = json.loads(args.xip_eligibility.read_text())
    assert closure["candidate_sha256"] == gc["candidate_sha256"]
    alloc = {section["section"]: section for section in closure["all_alloc_progbits"]["sections"]}
    reachable = {section["section"] for section in closure["all_source_roots_closure"]["sections"]}
    discarded = set(gc["discarded_sections"])
    assert discarded == set(alloc) - reachable
    direct_symbols = {
        symbol["name"]
        for slot in eligibility["native_function_slots"]
        for symbol in slot["direct_symbols"]
    }
    groups = {
        "pinned_dsp_dependency": [],
        "compiler_arithmetic": [],
        "crc_wrapper": [],
    }
    for name in sorted(discarded):
        symbol = name.removeprefix(".text.")
        group = (
            "pinned_dsp_dependency" if symbol.startswith("csky_")
            else "compiler_arithmetic" if symbol.startswith("__")
            else "crc_wrapper" if symbol == "g2_codec_crc32"
            else None
        )
        assert group is not None, name
        assert symbol not in direct_symbols, symbol
        groups[group].append({
            "section": name,
            "symbol": symbol,
            "bytes": alloc[name]["bytes"],
            "alignment": alloc[name]["alignment"],
            "source_relocation_reachable": False,
            "direct_native_slot_bound": False,
            "discarded_by_target_gc": True,
        })
    assert {k: len(v) for k, v in groups.items()} == {
        "pinned_dsp_dependency": 17,
        "compiler_arithmetic": 7,
        "crc_wrapper": 1,
    }
    result = {
        "candidate_sha256": gc["candidate_sha256"],
        "closure_sha256": hashlib.sha256(args.closure.read_bytes()).hexdigest(),
        "gc_receipt_sha256": hashlib.sha256(args.gc_receipt.read_bytes()).hexdigest(),
        "xip_eligibility_sha256": hashlib.sha256(args.xip_eligibility.read_bytes()).hexdigest(),
        "excluded_section_count": len(discarded),
        "excluded_raw_bytes": sum(alloc[name]["bytes"] for name in discarded),
        "groups": groups,
        "gc_eligible_under_selected_source_roots": True,
        "native_indirect_root_absence_proven": False,
        "final_layout_eligible": False,
        "remaining_evidence": [
            "Audit stock function-pointer and registration data plus external stage interfaces for indirect entries into excluded helpers.",
            "Qualify loader and runtime alias/copy addresses before assigning final XIP and SRAM sections.",
            "The native gap upper bound rules out intact large FFT bodies in unnamed gaps but cannot rule out small indirect helpers.",
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({"sections": result["excluded_section_count"], "bytes": result["excluded_raw_bytes"], "groups": {k: len(v) for k, v in groups.items()}})


if __name__ == "__main__":
    main()
