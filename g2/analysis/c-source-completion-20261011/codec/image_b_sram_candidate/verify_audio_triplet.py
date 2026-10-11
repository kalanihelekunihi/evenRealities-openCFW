#!/usr/bin/env python3
"""Native/C selector and invalid-address store qualification for 0x10005a5c."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
OBJECT = HERE / "build/backup_audio_triplet.o"
assert hashlib.sha256(STOCK.read_bytes()).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"

def disassemble(args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only", "--platform", "linux/amd64",
           "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
           "--mount", f"type=bind,src={OBJECT.parent},dst=/out,readonly",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + args
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout

native = disassemble(["-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
                      "--adjust-vma=0x10003000", "--start-address=0x10005a5c",
                      "--stop-address=0x10005aaa", "/stock/" + STOCK.name])
candidate = disassemble(["-d", "--no-show-raw-insn", "/out/" + OBJECT.name])
for text in (native, candidate):
    body = "\n".join(line.split(":", 1)[-1] for line in text.splitlines()
                     if re.match(r"\s*[0-9a-f]+:", line))
    assert re.search(r"movi\s+r3,\s*0", body)
    positions = [body.index(f"(r3, 0x{offset:x})") for offset in (8, 12, 16)]
    assert positions == sorted(positions)
assert sum("st.w" in line and "(r14" not in line for line in native.splitlines()) == 5
assert sum("st.w" in line and "(r14" not in line for line in candidate.splitlines()) == 8
receipt = {"stock_sha256": hashlib.sha256(STOCK.read_bytes()).hexdigest(),
           "candidate_object_sha256": hashlib.sha256(OBJECT.read_bytes()).hexdigest(),
           "native_static_nonstack_stores": 5,
           "candidate_static_nonstack_stores": 8,
           "per_selector_path_stores": {"invalid": 3, "one": 3, "two": 4, "four": 4},
           "invalid_selector_stores": ["0x8", "0xc", "0x10"],
           "valid_selector_bases": ["0xa0a00010", "0xa0a00030", "0xa0a00050"],
           "scope": "static target instruction/store qualification; no invalid-selector hardware execution"}
(HERE / "audio-triplet-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print("native/C path stores 3,3,4,4; invalid-address sequence retained")
