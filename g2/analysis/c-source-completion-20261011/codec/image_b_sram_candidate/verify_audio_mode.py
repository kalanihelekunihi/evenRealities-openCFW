#!/usr/bin/env python3
"""Bounded source/native check of the eight-way image-B audio mode tail."""
import hashlib
import json
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_audio_mode.c"
OBJECT = HERE / "build/backup_audio_mode.o"
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"


def disassemble(args):
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only",
           "--platform", "linux/amd64", "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={STOCK.parent},dst=/stock,readonly",
           "--mount", f"type=bind,src={OBJECT.parent},dst=/out,readonly",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-objdump"] + args
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout


def main():
    stock = STOCK.read_bytes()
    assert hashlib.sha256(stock).hexdigest() == "d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941"
    off = 0x10012ab4 - 0x10003000
    targets = [struct.unpack_from("<I", stock, off + i * 4)[0] for i in range(8)]
    native = disassemble(["-D", "-b", "binary", "-m", "csky", "--no-show-raw-insn",
                          "--adjust-vma=0x10003000", "--start-address=0x10005ec8",
                          "--stop-address=0x10005ff2", "/stock/" + STOCK.name])
    source_values = [int(x) for x in re.search(r"command_for_mode\[8\]\s*=\s*\{([^}]+)\}",
                                             SOURCE.read_text(), re.S).group(1).replace("u", "").split(",")]
    native_values = []
    for target in targets:
        line = next(x for x in native.splitlines() if x.strip().startswith(f"{target + 4:x}:"))
        native_values.append(int(re.search(r"movi\s+r2,\s*(\d+)", line).group(1)))
    compiled = disassemble(["-d", "/out/" + OBJECT.name])
    native_lines = native.splitlines()
    initial = [line for line in native_lines if re.match(r"\s*10005(?:ec|ed|ee|ef)[0-9a-f]:", line)]
    common = [line for line in native_lines if re.match(r"\s*10005f[0-9a-f]{2}:", line)
              and 0x10005f0e <= int(line.split(":", 1)[0], 16) < 0x10005f9e]
    stock_writes = sum("st.w" in line for line in initial + common) + 1
    source_writes = sum("st.w" in line for line in compiled.splitlines())
    receipt = {"stock_image_sha256": hashlib.sha256(stock).hexdigest(),
               "target_addresses": [f"0x{x:08x}" for x in targets],
               "native_commands": native_values, "source_commands": source_values,
               "commands_match": native_values == source_values,
               "native_writes_per_path": stock_writes,
               "candidate_write_sites": source_writes,
               "write_count_match": stock_writes == source_writes,
               "scope": "table values and static per-path store count; no hardware transition timing or runtime equality"}
    (HERE / "audio-mode-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"{len(targets)} commands match={receipt['commands_match']}, {stock_writes}/{source_writes} writes")
    if not (receipt["commands_match"] and receipt["write_count_match"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
