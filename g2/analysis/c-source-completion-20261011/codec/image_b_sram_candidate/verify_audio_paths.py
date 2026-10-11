#!/usr/bin/env python3
"""Bounded original/C static MMIO store-site check for two image-B paths."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
OBJECT = HERE / "build/backup_audio_paths.o"

def disassemble(arguments):
    command = ["docker", "run", "--rm", "--network=none", "--read-only",
               "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
               "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
               "--mount", f"type=bind,src={OBJECT.parent},dst=/out,readonly",
               "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + arguments
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout

def stores(text, low, high):
    count = 0
    for line in text.splitlines():
        match = re.match(r"\s*([0-9a-f]+):", line)
        if match and low <= int(match.group(1), 16) < high and "st.w" in line and "(r14" not in line:
            count += 1
    return count

assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
native = disassemble(["-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
                      "--adjust-vma=0x10003000", "--start-address=0x1000568c",
                      "--stop-address=0x10005838", "/stock/" + STOCK.name])
candidate = disassemble(["-d", "/out/" + OBJECT.name])
first = re.search(r"^([0-9a-f]+) <gx8002_image_b_i2s_input_10005794>:", candidate, re.M)
assert first
second_start = int(first.group(1), 16)
checks = [
    ("pcm_path", stores(native, 0x1000568c, 0x1000578e), stores(candidate, 0, second_start)),
    ("i2s_input", stores(native, 0x10005794, 0x10005838), stores(candidate, second_start, 1 << 32)),
]
assert checks == [("pcm_path", 22, 22), ("i2s_input", 11, 11)]
receipt = {"stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "candidate_object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
           "checks": [{"body": name, "native_nonstack_stores": native_count,
                       "candidate_nonstack_stores": candidate_count}
                      for name, native_count, candidate_count in checks],
           "scope": "static peripheral/SRAM store-site counts; no original C-SKY execution or live hardware proof"}
(HERE / "audio-paths-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("PCM 22/22 and I2S 11/11 nonstack writes")
