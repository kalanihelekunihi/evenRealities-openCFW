#!/usr/bin/env python3
"""Static nonstack write counts for native image-B audio buffer controls."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
OBJECT = HERE / "build/backup_audio_buffers.o"
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"

def disassemble(arguments):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
           "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
           "--mount", f"type=bind,src={OBJECT.parent},dst=/out,readonly",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + arguments
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

def stores(text, low, high):
    return sum("st.w" in line and "(r14" not in line
               for line in text.splitlines()
               if (match := re.match(r"\s*([0-9a-f]+):", line))
               and low <= int(match.group(1), 16) < high)

native = disassemble(["-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
                      "--adjust-vma=0x10003000", "--start-address=0x10005490",
                      "--stop-address=0x100055da", "/stock/" + STOCK.name])
candidate = disassemble(["-d", "/out/" + OBJECT.name])
start = int(re.search(r"^([0-9a-f]+) <gx8002_image_b_dual_buffer_100054cc>:",
                      candidate, re.M).group(1), 16)
checks = [("channel_sources", stores(native, 0x10005490, 0x100054cc),
           stores(candidate, 0, start)),
          ("dual_buffer", stores(native, 0x100054cc, 0x100055da),
           stores(candidate, start, 1 << 32))]
assert checks == [("channel_sources", 4, 4), ("dual_buffer", 21, 21)]
receipt = {"stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "candidate_object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
           "checks": [{"body": name, "native_nonstack_stores": old,
                       "candidate_nonstack_stores": new} for name, old, new in checks],
           "scope": "static peripheral/SRAM store-site counts; no native execution or hardware proof"}
(HERE / "audio-buffers-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("channel 4/4 and dual-buffer 21/21 nonstack writes")
