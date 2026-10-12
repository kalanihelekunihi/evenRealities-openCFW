#!/usr/bin/env python3
"""Find aligned stock address words into uncatalogued image-A code gaps.

These are pointer-shaped words, not a proof that each word is consumed as a
function pointer. They make final-layout indirect-entry review finite.
"""
import bisect
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IMAGES = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"


def load_gaps(name):
    if name == "xip":
        return json.loads((HERE / "xip-function-range-gap-receipt.json").read_text())["gaps"]
    return json.loads((HERE / "sram-function-range-gap-receipt.json").read_text())["residual_gaps"]


def main():
    images = {
        "xip": (IMAGES / "binh_a_stage2_xip.bin", 0x10203004),
        "sram": (IMAGES / "binh_a_stage2_sram.bin", 0x10023400),
    }
    gaps = {}
    for region in images:
        gaps[region] = sorted(
            (int(g["start"], 16), int(g["end_exclusive"], 16), g)
            for g in load_gaps(region)
        )
    scans = {}
    for source, (path, base) in images.items():
        raw = path.read_bytes()
        for dest, intervals in gaps.items():
            starts = [a for a, _, _ in intervals]
            hits = []
            for offset in range(0, len(raw) - 3, 4):
                value = int.from_bytes(raw[offset:offset + 4], "little")
                index = bisect.bisect_right(starts, value) - 1
                if index < 0 or value >= intervals[index][1]:
                    continue
                start, end, gap = intervals[index]
                hits.append({
                    "source_address": hex(base + offset),
                    "target_address": hex(value),
                    "target_gap": [hex(start), hex(end)],
                    "gap_bytes": end - start,
                    "catalogue_gap_kind": gap.get("kind"),
                    "catalogue_attribution": gap.get("attribution"),
                })
            scans[f"{source}_to_{dest}"] = {
                "source_image_sha256": hashlib.sha256(raw).hexdigest(),
                "aligned_word_hits": hits,
                "count": len(hits),
            }
    result = {
        "scans": scans,
        "pointer_word_count": sum(x["count"] for x in scans.values()),
        "native_indirect_root_absence_proven": False,
        "limits": [
            "A value in a code gap can be a jump-table target, literal or accidental scalar; classify consumer instruction and source table before treating it as an entry.",
            "This scan covers aligned words in the loaded image-A XIP/SRAM payload only; encoded, halfword, computed and other-stage references remain outside scope.",
            "The Ghidra range gaps include continuation code and literal pools and do not themselves imply missing C bodies.",
        ],
    }
    out = HERE / "excluded-section-eligibility/native-gap-pointer-words.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print({name: scan["count"] for name, scan in scans.items()})


if __name__ == "__main__":
    main()
