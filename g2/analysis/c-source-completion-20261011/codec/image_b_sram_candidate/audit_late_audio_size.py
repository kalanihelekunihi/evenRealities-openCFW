#!/usr/bin/env python3
"""Measure actual late audio source placement against the stock copy extent."""
import json
import re
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
final = json.loads((here / "build-late-audio-source-final-round/receipt.json").read_text())
elf = root / final["elf"]
nm = root / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-nm"
listing = subprocess.check_output([str(nm), "-S", str(elf)], text=True)
section = final["sections"][".late_audio"]
start, end = section["vma"], section["vma"] + section["size"]
functions = []
for line in listing.splitlines():
    match = re.fullmatch(r"([0-9a-f]+) ([0-9a-f]+) [Tt] (\S+)", line)
    if match:
        address, size = int(match[1], 16), int(match[2], 16)
        if start <= address < end and size:
            functions.append({"symbol": match[3], "address": hex(address), "bytes": size})
functions.sort(key=lambda x: -x["bytes"])
stock_end = 0x1001708c
rodata = final["sections"][".rodata"]
initialized_start = final["sections"][".clock_state"]["lma"]
rodata_end = rodata["vma"] + rodata["size"]
headroom = initialized_start - rodata_end
result = {
    "result": "PASS_SOURCE_SIZE_CENSUS",
    "elf_sha256": final["elf_sha256"],
    "stock_stage2_copy_end": hex(stock_end),
    "late_audio_bytes": section["size"],
    "late_audio_function_count": len(functions),
    "function_bytes_total": sum(f["bytes"] for f in functions),
    "functions_largest_first": functions,
    "rodata_end": hex(rodata_end),
    "authenticated_initialized_data_start": hex(initialized_start),
    "current_headroom_bytes": headroom,
    "additional_reduction_to_move_late_audio_before_fixed_data": section["size"] - headroom,
    "limits": [
        "This measures source function sizes; merging shared MMIO bodies requires caller and effect proof.",
        "The stock loader copies only through 0x1001708c; a late section beyond it is not delivered.",
        "Header extension or segmented loading is not established by this size audit.",
    ],
}
assert result["function_bytes_total"] <= section["size"]
assert result["additional_reduction_to_move_late_audio_before_fixed_data"] > 0
(here / "late-audio-size-census-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["result"], "functions", len(functions), "headroom", headroom,
      "deficit", result["additional_reduction_to_move_late_audio_before_fixed_data"])
