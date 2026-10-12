#!/usr/bin/env python3
"""Join separately sourced BINH B stages at the authenticated boundary.

This is a package-shape artifact for offline review, never a flash image.
"""
import hashlib
import json
import struct
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
stage1_dir = here.parent / "image_b_stage1_candidate"
stage1_receipt = json.loads((stage1_dir / "layout-probe-receipt.json").read_text())
stage2_receipt = json.loads((here / "stock-length-fit-receipt.json").read_text())
stage1 = (stage1_dir / "build/layout_probe_stage1_binh.bin").read_bytes()
stage2 = (here / "build-stock-length-bss-slot-round/image_b_source_payload.bin").read_bytes()
sha = lambda data: hashlib.sha256(data).hexdigest()
assert stage1_receipt["result"] == "PASS_LAYOUT_PROBE"
assert stage2_receipt["result"] == "PASS_SOURCE_LAYOUT_WITHIN_STOCK_TRANSFER"
assert sha(stage1) == stage1_receipt["generated_stage1_binh_sha256"]
assert sha(stage2) == stage2_receipt["extracted_c_source_payload_sha256"]
magic, medium, version, stage2_length, stage1_length, load = struct.unpack_from("<6I", stage1)
assert (magic, medium, version, stage2_length, stage1_length, load) == (
    0x484e4942, 0x55aa55aa, 0x203, 0x1408c, 0x3000, 0x20000000)
assert len(stage1) == stage1_length and len(stage2) == stage2_length

stock_dir = root / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images"
stock_payload = (stock_dir / "codec_payload.bin").read_bytes()
stock_stage1 = (stock_dir / "binh_b_stage1.bin").read_bytes()
stock_stage2 = (stock_dir / "binh_b_stage2.bin").read_bytes()
stock_offset = stock_payload.find(stock_stage1)
assert stock_offset >= 0 and stock_payload.find(stock_stage1, stock_offset + 1) < 0
stock_stage2_offset = stock_payload.find(stock_stage2)
assert stock_stage2_offset > stock_offset
separator = stock_payload[stock_offset + stage1_length:stock_stage2_offset]
assert separator == b"\x00" * 4
assert stock_stage2_offset == stock_offset + stage1_length + len(separator)
assert stock_stage1[:24] == stage1[:24]

combined = stage1 + separator + stage2
out = here / "build-stock-length-bss-slot-round/image_b_source_binh_experimental.bin"
out.write_bytes(combined)
result = {
    "result": "PASS_OFFLINE_BINH_STAGE_PAIR_SHAPE",
    "source_stage1_sha256": sha(stage1),
    "source_stage2_sha256": sha(stage2),
    "joined_bytes": len(combined),
    "joined_sha256": sha(combined),
    "stock_payload_binh_b_offset": stock_offset,
    "stock_observed_interstage_separator_hex": separator.hex(),
    "stock_stage2_payload_offset": stock_stage2_offset,
    "header_fields": {"magic": hex(magic), "medium": hex(medium),
                      "version": hex(version), "stage2_length": stage2_length,
                      "stage1_length": stage1_length, "load": hex(load)},
    "limits": [
        "Offline stage pair only; not an outer codec package or flashable artifact.",
        "The four-byte zero separator is observed in the stock outer payload; its field meaning is unqualified.",
        "Stage1 generated footer/CRC is experimental; product authentication and transport are unqualified.",
        "Stage1 loader and IRAM/DRAM alias, physical execution, and behavioral timing remain unqualified.",
    ],
}
(here / "source-binh-stage-pair-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["result"], len(combined))
