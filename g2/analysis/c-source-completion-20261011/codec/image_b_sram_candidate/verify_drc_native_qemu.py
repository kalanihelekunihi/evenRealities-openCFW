#!/usr/bin/env python3
"""Compare all eight output halfwords of one native/source DRC frame.

The stock image is linked only into an original-byte QEMU test ELF. The
source ELF uses the reconstructed C body and a gain-one power child for the
gain_db=0 test. This is finite numerical evidence, not firmware output.
"""
from __future__ import annotations
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
OUT = HERE / "native-drc-oracle-run"
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
QEMU = ROOT / "g2/build/offline-xuantie-csky-dsp-20261009T201800Z/qemu-system-cskyv2"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate/backup_stage2_drc_process.c"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def repo(path: Path) -> str:
    return "/repo/" + str(path.relative_to(ROOT))

def tool(args: list[str]) -> None:
    command = ["docker", "run", "--rm", "--network=none",
               "--platform", "linux/amd64", "-v", f"{ROOT}:/repo",
               "-v", f"{TOOL}:/tool:ro", "-w", repo(HERE),
               "opencfw/iar-base:10.10.2-local", *args]
    subprocess.run(command, check=True, capture_output=True, text=True)

def execute(elf: Path) -> int:
    command = ["docker", "run", "--rm", "--network=none",
               "-v", f"{ROOT}:/repo", "-w", "/repo",
               "opencfw/qemu-csky-builddeps:20261009t201800", "sh", "-lc",
               f"timeout 15s {repo(QEMU)} -M virt -m 1G -cpu ck804ef "
               f"-nographic -monitor none -kernel {repo(elf)} "
               "-d guest_errors -D /tmp/drc.log; cat /tmp/drc.log"]
    result = subprocess.run(command, capture_output=True, text=True,
                            check=True, timeout=30)
    match = re.search(r"csky_exit_write: exit\((\d+)\)", result.stdout)
    if match is None:
        raise RuntimeError(result.stdout + result.stderr)
    return int(match.group(1))

def main() -> None:
    OUT.mkdir(exist_ok=True)
    results = []
    for index in range(8):
        record = {"index": index}
        for mode in ("original", "source"):
            elf = OUT / f"{mode}-{index}.elf"
            command = ["/tool/bin/csky-abiv2-elf-gcc", "-mcpu=ck804ef",
                       "-mhard-float", "-O2", "-nostdlib", "-nostartfiles",
                       f"-DOUTPUT_INDEX={index}",
                       "-Wl,-T,process_native_oracle.ld" if mode == "original"
                       else "-Wl,-T,process_source_oracle.ld",
                       "-o", repo(elf), "process_native_oracle_start.S",
                       "drc_native_oracle_main.c"]
            if mode == "original":
                command.append("process_native_oracle_stock.S")
            else:
                command.extend(["-DSOURCE_MODE", repo(SOURCE)])
            tool(command)
            record[mode] = execute(elf)
        if record["original"] != record["source"]:
            raise AssertionError(record)
        results.append(record)
    receipt = {"result": "PASS", "samples": results,
               "source_sha256": sha(SOURCE), "stock_sha256": sha(STOCK),
               "scope": "eight full 16-bit output samples, gain_db=0, QEMU CK804EF; source power child fixed at gain one only for this finite test; hardware rounding and wider domains unqualified"}
    path = OUT / "receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(path)

if __name__ == "__main__":
    main()
