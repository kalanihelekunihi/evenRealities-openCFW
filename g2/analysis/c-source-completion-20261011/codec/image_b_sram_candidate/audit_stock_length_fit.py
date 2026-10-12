#!/usr/bin/env python3
"""Verify candidate source layout fits the authenticated fixed B transfer."""
import json
import hashlib
import re
import subprocess
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parents[4]
receipt = json.loads((here / "build-stock-length-bss-slot-round/receipt.json").read_text())
sections = receipt["sections"]
stock_start, stock_end = 0x10003000, 0x1001708c
assert receipt["result"] == "PASS_LAYOUT_ONLY"
assert ".late_audio" not in sections
assert sections[".vectors"]["lma"] == stock_start
assert sections[".kernel_coefficients"]["lma"] + sections[".kernel_coefficients"]["size"] == stock_end
assert sections[".rodata"]["vma"] + sections[".rodata"]["size"] <= sections[".clock_state"]["lma"]
for name, section in sections.items():
    if name in {".bss", ".image_b_retained.energy", ".image_b_retained.ring",
                ".image_b_retained.dsp_operations", ".image_b_retained.imcra_setting",
                ".comment", ".csky_stack_size", ".csky.attributes"}:
        continue
    assert stock_start <= section["lma"] and section["lma"] + section["size"] <= stock_end, name
nm = root / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-nm"
listing = subprocess.check_output([str(nm), "-S", str(root / receipt["elf"])], text=True)
audio = []
for line in listing.splitlines():
    match = re.fullmatch(r"([0-9a-f]+) ([0-9a-f]+) [Tt] (gx8002_image_b_audio_out_\S+)", line)
    if match:
        address, size = int(match[1], 16), int(match[2], 16)
        if size and address >= 0x10003100:
            assert address + size <= sections[".clock_state"]["lma"]
            audio.append(match[3])
assert len(audio) >= 21
objcopy = nm.with_name("csky-elfabiv2-objcopy")
payload = here / "build-stock-length-bss-slot-round/image_b_source_payload.bin"
subprocess.run([str(objcopy), "-O", "binary", str(root / receipt["elf"]), str(payload)], check=True)
payload_bytes = payload.read_bytes()
assert len(payload_bytes) == stock_end - stock_start
for symbol, expected in (
    ("gx8002_image_b_platform_shadow_20017398", 0x20017398),
    ("gx8002_image_b_mode_loop_2002d2b4", 0x2002d2b4),
    ("gx8002_image_b_mode_index_2002d2b8", 0x2002d2b8),
    ("gx8002_image_b_token_cursor_2002d3e0", 0x2002d3e0),
):
    assert re.search(rf"(?m)^{expected:08x} [0-9a-f]+ B {symbol}$", listing)
result = {
    "result": "PASS_SOURCE_LAYOUT_WITHIN_STOCK_TRANSFER",
    "elf_sha256": receipt["elf_sha256"],
    "stock_transfer": [hex(stock_start), hex(stock_end)],
    "extracted_c_source_payload_bytes": len(payload_bytes),
    "extracted_c_source_payload_sha256": hashlib.sha256(payload_bytes).hexdigest(),
    "source_audio_functions_in_transfer": len(audio),
    "native_bss_slots_bound": 4,
    "rodata_to_fixed_data_gap_bytes": sections[".clock_state"]["lma"] -
                                (sections[".rodata"]["vma"] + sections[".rodata"]["size"]),
    "limits": [
        "This checks linked source placement, not source completeness or a signed/product package.",
        "The stage1 transfer and IRAM/DRAM alias still need stock loader and hardware qualification.",
        "CRC and quarter-wave data are behavioral size variants; execution timing and FP exceptions remain open.",
        "The extracted ELF payload has stock length, but BINH package authentication and live load behavior remain unqualified.",
    ],
}
(here / "stock-length-fit-receipt.json").write_text(json.dumps(result, indent=2) + "\n")
print(result["result"], result["rodata_to_fixed_data_gap_bytes"])
