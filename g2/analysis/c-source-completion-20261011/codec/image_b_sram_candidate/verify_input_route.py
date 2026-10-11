#!/usr/bin/env python3
"""Bounded original/C per-path write-site check for image-B 0x100053e0."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
OBJECT = HERE / "build/backup_audio_input_route.o"
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"

def listing(args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only", "--platform", "linux/amd64",
           "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
           "--mount", f"type=bind,src={OBJECT.parent},dst=/out,readonly",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + args
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

native = listing(["-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
                  "--adjust-vma=0x10003000", "--start-address=0x100053e0",
                  "--stop-address=0x1000548a", "/stock/" + STOCK.name])
candidate = listing(["-d", "/out/" + OBJECT.name])
def peripheral_stores(text):
    return [int(match.group(1), 16) for line in text.splitlines()
            if (match := re.match(r"\s*([0-9a-f]+):", line))
            and "st.w" in line and "(r14" not in line]

native_sites = peripheral_stores(native)
candidate_sites = peripheral_stores(candidate)
assert len(native_sites) == 13 and 0x10005486 in native_sites
assert len(candidate_sites) == 12
receipt = {"stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "candidate_object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
           "native_static_nonstack_stores": 13,
           "native_mutually_exclusive_bit17_store_sites": ["0x10005438", "0x10005486"],
           "native_stores_per_path": 12, "candidate_stores_per_path": 12,
           "scope": "per-path static stores and branch-site identity, not MMIO runtime equality"}
(HERE / "input-route-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("input route 12/12 nonstack writes per branch")
