#!/usr/bin/env python3
"""Verify distinct stock clock source records and corrected C binding."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
IMAGE = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_a_stage2_sram.bin"
OBJECT = HERE / "clock-mode1-correction/clock_mode1_literals.o"
SOURCE = ROOT / "g2/components/gx8002/app_callback_candidate/resident_clock_initialize_candidate.c"
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"


def section_bytes(section):
    output = subprocess.check_output([str(READELF), "-x", section, str(OBJECT)], text=True)
    chunks = []
    for line in output.splitlines():
        match = re.match(r"^\s*0x[0-9a-f]+\s+((?:[0-9a-f]{8}\s*){1,4})", line)
        if match:
            chunks.extend(re.findall(r"[0-9a-f]{8}", match.group(1)))
    return bytes.fromhex("".join(chunks))


def main():
    native = IMAGE.read_bytes()
    pairs = [(0x10025cd0, ".gx8002.clock_boot.25cd0"),
             (0x10025cf4, ".gx8002.clock_boot.25cf4")]
    checks = []
    for address, section in pairs:
        stock = native[address - 0x10023400:address - 0x10023400 + 16]
        compiled = section_bytes(section)
        assert len(stock) == len(compiled) == 16
        assert stock == compiled, section
        checks.append({"native_address": hex(address), "section": section,
                       "bytes": 16, "sha256": hashlib.sha256(stock).hexdigest(),
                       "words": [int.from_bytes(stock[i:i+4], "little")
                                 for i in range(0, 16, 4)]})
    assert checks[0]["words"] == [28, 0, 18, 1]
    assert checks[1]["words"] == [16, 0, 0, 1]
    text = SOURCE.read_text()
    assert "gx8002_clock_startmode1_sources_25cf4, 16u" in text
    result = {"native_image_sha256": hashlib.sha256(native).hexdigest(),
              "compiled_data_object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
              "initializer_source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
              "checks": checks,
              "native_consumer_instructions": [
                  "0x10025a1c lrw r1, 0x10025cd0; 0x10025a1e bsr 0x10025738",
                  "0x10025af0 lrw r1, 0x10025cf4; 0x10025af4 bsr 0x10025738",
              ],
              "compiled_data_equal_stock": True,
              "native_runtime_equivalence_proven": False}
    out = HERE / "clock-mode1-correction/receipt.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print({"pairs": len(checks), "bytes": 32, "equal": True})


if __name__ == "__main__":
    main()
