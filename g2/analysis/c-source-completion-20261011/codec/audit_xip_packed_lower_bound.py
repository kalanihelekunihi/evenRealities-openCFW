#!/usr/bin/env python3
"""Count a conservative source XIP size floor beside the packed-code probe."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"
NATIVE_XIP = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_xip.bin"
HELPERS = ["__adddf3", "__subdf3", "__muldf3", "__divdf3", "__gedf2",
           "__fixdfsi", "__fixunsdfsi", "__floatunsidf", "__udivdi3",
           "__muldi3", "crc32_no_comp", "g2_codec_dw_uart_dma_burst",
           "g2_codec_dw_uart_putc", "g2_codec_dw_uart_getc",
           "g2_codec_gpio_set_level", "g2_codec_queue_is_empty",
           "g2_codec_queue_is_full", "gx8002_tfp_putchw.isra.1"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--packed-receipt", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    packed = json.loads(args.packed_receipt.read_text())
    assert packed["candidate_sha256"] == sha(args.candidate)
    sections_text = subprocess.run([str(READELF), "-SW", str(args.candidate)],
                                   check=True, capture_output=True, text=True).stdout
    sections = {}
    for line in sections_text.splitlines():
        found = re.search(r"^\s*\[\s*(\d+)\]\s+(\S+)\s+(PROGBITS|NOBITS)\s+[0-9a-f]+\s+[0-9a-f]+\s+([0-9a-f]+)", line)
        if found:
            sections[int(found[1])] = (found[2], int(found[4], 16))
    symbols_text = subprocess.run([str(READELF), "-sW", str(args.candidate)],
                                  check=True, capture_output=True, text=True).stdout
    symbols = {}
    for line in symbols_text.splitlines():
        found = re.search(r"^\s*\d+:\s+[0-9a-f]+\s+(\d+)\s+FUNC\s+(?:GLOBAL|LOCAL)\s+DEFAULT\s+(\d+)\s+(\S+)", line)
        if found:
            symbols[found[3]] = (int(found[1]), int(found[2]))
    helpers = []
    for name in HELPERS:
        size, section_index = symbols[name]
        section_name, _ = sections[section_index]
        assert size and not section_name.startswith(".text.gx8002_xip_"), (name, section_name)
        helpers.append({"symbol": name, "body_bytes": size, "section": section_name})
    xip_rodata = [{"section": name, "bytes": size} for name, size in sections.values()
                  if name.startswith(".rodata.gx8002_xip_")]
    sample_names = [{"section": name, "bytes": size} for name, size in sections.values()
                    if name.startswith(".gx8002.sample_name.")]
    parts = {"packed_direct_text": packed["packed_bytes"],
             "distinct_mapped_helper_bodies": sum(x["body_bytes"] for x in helpers),
             "named_xip_rodata": sum(x["bytes"] for x in xip_rodata),
             "sample_name_rodata": sum(x["bytes"] for x in sample_names)}
    result = {"candidate_sha256": sha(args.candidate), "packed_receipt_sha256": sha(args.packed_receipt),
              "native_xip_sha256": sha(NATIVE_XIP), "native_xip_bytes": NATIVE_XIP.stat().st_size,
              "counted_parts": parts, "counted_lower_bound_bytes": sum(parts.values()),
              "remaining_native_xip_bytes_after_floor": NATIVE_XIP.stat().st_size - sum(parts.values()),
              "mapped_helper_bodies": helpers, "named_xip_rodata_sections": xip_rodata,
              "sample_name_sections": sample_names,
              "limits": ["This is a conservative byte floor only if all listed source sections remain in the image-A XIP payload.",
                         "Other mapped helpers, FENV/shift code, alignment, tables, literals, and relocation veneers are omitted.",
                         "Relocating functions to other authenticated memory might alter this XIP floor, but no such final allocation is proven."]}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({key: result[key] for key in ("counted_parts", "counted_lower_bound_bytes", "native_xip_bytes", "remaining_native_xip_bytes_after_floor")})


if __name__ == "__main__":
    main()
