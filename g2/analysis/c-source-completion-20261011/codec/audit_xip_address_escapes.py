#!/usr/bin/env python3
"""Bounded raw-address check for current overflowing image-A XIP providers.

This checks exact aligned/unaligned little-endian address words in the two
authenticated BINH-A loaded regions. It does not prove absence of encoded
branches, arithmetic address construction, or references from other stages.
"""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=Path("g2/analysis/c-source-completion-20261011/codec/xip-link-eligibility-os-manifest.json"))
    parser.add_argument("--images", type=Path, default=Path("g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"))
    parser.add_argument("--output", type=Path, default=Path("g2/analysis/c-source-completion-20261011/codec/xip-overflow-address-escapes.json"))
    args = parser.parse_args()
    source = args.manifest.read_bytes()
    manifest = json.loads(source)
    regions = [
        ("image_a_sram", 0x10023400, args.images / "binh_a_stage2_sram.bin"),
        ("image_a_xip", 0x10203004, args.images / "binh_a_stage2_xip.bin"),
    ]
    loaded = [(name, base, path.read_bytes(), path) for name, base, path in regions]
    gaps = [(int(g["start"], 16), int(g["end_exclusive"], 16)) for g in manifest["unplaced_native_gap_ranges"]]
    rows = []
    for slot in manifest["native_function_slots"]:
        if slot["placement_status"] != "section_slot_overflow":
            continue
        address = int(slot["entry"], 16)
        needle = struct.pack("<I", address)
        hits = []
        for region_name, base, data, _ in loaded:
            at = 0
            while (index := data.find(needle, at)) >= 0:
                absolute = base + index
                gap = next(((start, end) for start, end in gaps if start <= absolute < end), None)
                hits.append({
                    "region": region_name,
                    "address": f"0x{absolute:08x}",
                    "word_aligned": absolute % 4 == 0,
                    "native_catalogue_gap": [f"0x{gap[0]:08x}", f"0x{gap[1]:08x}"] if gap else None,
                })
                at = index + 1
        rows.append({
            "entry": slot["entry"],
            "native_name": slot["native_name"],
            "overflow_bytes": slot["excess_section_bytes_if_fixed"],
            "candidate_symbol": slot["direct_symbols"][0]["name"],
            "candidate_section_relocations": slot["compiled_section_relocations"],
            "raw_address_hits": hits,
        })
    result = {
        "purpose": "bounded raw address escapes for current fixed-slot overflows",
        "eligibility_manifest_sha256": hashlib.sha256(source).hexdigest(),
        "regions": [{"name": name, "base": f"0x{base:08x}", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "path": str(path)} for name, base, data, path in loaded],
        "overflow_provider_count": len(rows),
        "providers_with_raw_hits": sum(bool(r["raw_address_hits"]) for r in rows),
        "providers_with_sram_hits": sum(any(h["region"] == "image_a_sram" for h in r["raw_address_hits"]) for r in rows),
        "providers_with_xip_hits_outside_catalogue_gaps": sum(any(h["region"] == "image_a_xip" and h["native_catalogue_gap"] is None for h in r["raw_address_hits"]) for r in rows),
        "overflow_providers": rows,
        "limits": ["Raw four-byte address matches only; direct branch encodings and computed addresses are not inspected.", "Only BINH-A image SRAM and XIP loaded regions are searched; image-B, ROM, and external references are not covered.", "A native fixed-slot overflow may still be solved by a source-owned relocated placement, but no spare XIP allocation or full reference rewrite is established here."],
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"{len(rows)} overflowing providers; {result['providers_with_raw_hits']} raw-hit providers; {result['providers_with_sram_hits']} SRAM; {result['providers_with_xip_hits_outside_catalogue_gaps']} XIP outside catalogue gaps")


if __name__ == "__main__":
    main()
