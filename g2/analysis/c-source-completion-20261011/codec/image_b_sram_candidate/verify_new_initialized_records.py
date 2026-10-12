#!/usr/bin/env python3
"""Compile two typed image-B records and compare their stock copy bytes.

This verifies only records with no link-time pointer relocations. The full
300-byte normal-copy image, its CRT copy, and hardware execution are separate.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[5]
HERE = Path(__file__).resolve().parent
TOOL = ROOT / "g2/build/offline-nationalchip-dsp-c-compiler-successor-20261009T195245Z/toolchain"
STOCK = ROOT / "g2/build/pseudocode-first/20260930T190500Z/reviews/codec-canonical-images-003/images/binh_b_stage2.bin"
SOURCE = ROOT / "g2/components/gx8002/image_b_sram_candidate"
RECORDS = (
    ("backup_audio_runtime_initialized_state.c", ".data.image_b.audio_runtime_state", 0x10016f64, 16),
    ("backup_trigonometry_kernel_coefficients.c", ".data.image_b.kernel_coefficients", 0x10017034, 88),
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def target(tool, out, arguments):
    command = [
        "docker", "run", "--rm", "--network=none", "--read-only",
        "--platform", "linux/amd64",
        "--mount", f"type=bind,src={TOOL},dst=/tool,readonly",
        "--mount", f"type=bind,src={ROOT},dst=/repo,readonly",
        "--mount", f"type=bind,src={out},dst=/out",
        "--tmpfs", "/tmp:rw", "opencfw/iar-base:10.10.2-local",
        f"/tool/bin/csky-abiv2-elf-{tool}", *arguments,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def main():
    stock = STOCK.read_bytes()
    results = []
    with tempfile.TemporaryDirectory(prefix="image-b-init-records-", dir=HERE) as temp:
        out = Path(temp)
        for filename, section, address, size in RECORDS:
            source = SOURCE / filename
            stem = source.stem
            target("gcc", out, [
                "-mcpu=ck804ef", "-mhard-float", "-O2", "-fno-builtin",
                "-std=c11", "-Wall", "-Wextra", "-Werror", "-c",
                f"/repo/{source.relative_to(ROOT)}", "-o", f"/out/{stem}.o",
            ])
            target("objcopy", out, ["-O", "binary", "-j", section,
                                     f"/out/{stem}.o", f"/out/{stem}.bin"])
            candidate = (out / f"{stem}.bin").read_bytes()
            expected = stock[address - 0x10003000:address - 0x10003000 + size]
            result = {
                "source": str(source.relative_to(ROOT)),
                "source_sha256": digest(source.read_bytes()),
                "stock_address": f"0x{address:08x}",
                "section": section,
                "size": len(candidate),
                "candidate_sha256": digest(candidate),
                "stock_sha256": digest(expected),
                "bytes_equal": len(candidate) == size and candidate == expected,
            }
            results.append(result)
    receipt = {
        "stock_image_sha256": digest(stock),
        "target": "C-SKY CK804EF hard-float C11",
        "scope": "two typed, relocation-free normal-copy records; no CRT, linker or hardware proof",
        "all_equal": all(item["bytes_equal"] for item in results),
        "records": results,
    }
    path = HERE / "new-initialized-records-receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    if not receipt["all_equal"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
