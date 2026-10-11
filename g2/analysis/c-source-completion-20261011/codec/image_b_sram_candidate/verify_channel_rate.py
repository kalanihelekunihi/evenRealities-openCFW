#!/usr/bin/env python3
"""Bounded image-B channel rate: pinned correction table and field arithmetic."""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
stock = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
source = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_audio_channels.c"
data = stock.read_bytes()
assert hashlib.sha256(data).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
native = list(data[0x10012aac - 0x10003000:0x10012ab1 - 0x10003000])
body = source.read_text()
match = re.search(r"rate_correction\[5\]\s*=\s*\{([^}]+)\}", body)
assert match
candidate = [int(x.strip().rstrip("u")) for x in match.group(1).split(",")]
assert native == candidate
cases = 0
for rate in range(0, 16384):
    quotient = rate // 6
    index = (quotient - 4) & 0xffffffff
    correction = native[index] if index < 5 else 0
    field = (rate % 6 + quotient + correction) & 63
    assert 0 <= field < 64
    cases += 1
receipt = {"stock_image_sha256": hashlib.sha256(data).hexdigest(),
           "native_table_address": "0x10012aac", "native_correction": native,
           "candidate_correction": candidate, "bounded_rates_checked": cases,
           "scope": "table identity and arithmetic domain; no MMIO runtime equality"}
(HERE / "channel-rate-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(f"{len(native)} correction values match; {cases} bounded rates")
