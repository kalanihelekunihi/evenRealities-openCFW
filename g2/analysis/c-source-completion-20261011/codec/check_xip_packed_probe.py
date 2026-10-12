#!/usr/bin/env python3
"""Test a packed relocatable placement for direct named image-A XIP code."""

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
READELF = ROOT / "g2/build/pseudocode-first/20260930T190500Z/tools/csky-binutils-001/install/bin/csky-elfabiv2-readelf"
LINKER = HERE / "image_a_xip_packed_probe.ld"
START, END = 0x10203004, 0x1020A8AA


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--eligibility", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    placed = args.output / "xip-packed-probe.o"
    cmd = ["docker", "run", "--rm", "--network=none", "--read-only", "--platform", "linux/amd64",
           "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
           "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
           "--mount", f"type=bind,src={args.output.resolve()},dst=/out", "--tmpfs", "/tmp:rw",
           "opencfw/iar-base:10.10.2-local", "/tool/bin/csky-abiv2-elf-gcc",
           "-mcpu=ck804ef", "-mhard-float", "-nostdlib", "-nostartfiles", "-Wl,-r", "-Wl,-A,ck803",
           f"-Wl,-T,/repo/{LINKER.relative_to(ROOT)}", f"/repo/{args.candidate.resolve().relative_to(ROOT)}",
           "-o", "/out/xip-packed-probe.o"]
    subprocess.run(cmd, check=True)
    sections = subprocess.run([str(READELF), "-SW", str(placed)], capture_output=True, text=True, check=True).stdout
    match = re.search(r"\[\s*(\d+)\]\s+\.gx8002_xip_packed\s+PROGBITS\s+([0-9a-f]+)\s+[0-9a-f]+\s+([0-9a-f]+)", sections)
    assert match, "packed XIP section absent"
    section_index, start, size = int(match[1]), int(match[2], 16), int(match[3], 16)
    assert start == START and start + size <= END
    symbols = subprocess.run([str(READELF), "-sW", str(placed)], capture_output=True, text=True, check=True).stdout
    packed = set()
    for line in symbols.splitlines():
        found = re.search(r"^\s*\d+:\s+[0-9a-f]+\s+\d+\s+FUNC\s+GLOBAL\s+DEFAULT\s+" + str(section_index) + r"\s+(\S+)", line)
        if found:
            packed.add(found[1])
    manifest = json.loads(args.eligibility.read_text())
    expected = {symbol["name"] for slot in manifest["native_function_slots"] for symbol in slot["direct_symbols"]}
    missing = sorted(expected - packed)
    assert not missing, f"named direct XIP symbols not packed: {missing}"
    result = {"status": "PASS", "candidate_sha256": sha(args.candidate),
              "eligibility_sha256": sha(args.eligibility), "linker_script_sha256": sha(LINKER),
              "placed_object_sha256": sha(placed), "native_code_span": [hex(START), hex(END)],
              "native_code_span_bytes": END - START, "packed_start": hex(start),
              "packed_bytes": size, "packed_end_exclusive": hex(start + size),
              "remaining_native_code_span_bytes": END - (start + size),
              "expected_direct_symbols": len(expected), "packed_expected_direct_symbols": len(expected - set(missing)),
              "extra_packed_symbols": sorted(packed - expected),
              "limits": ["This relocatable packed link checks named source code size and symbol membership only.",
                         "It does not include all helper code/rodata/literal-tail data in the packed region.",
                         "It does not resolve final XIP address space, branch reach, outside-stage references, loader copy, or runtime equality."]}
    (args.output / "receipt.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("status", "packed_bytes", "remaining_native_code_span_bytes", "expected_direct_symbols", "extra_packed_symbols")}))


if __name__ == "__main__":
    main()
