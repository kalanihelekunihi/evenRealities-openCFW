#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independently reconstruct the two G2 Touch residual NOP-padding categories.

`g2-touch-final-physical-byte-buckets.tsv` (and the analyzer that produced it,
`analyze_g2_touch_relocated_semantics.py`) already establish -- from the
authenticated stock Touch FWPK -- that two small, scattered halfword sets in
the typed_external_or_unsupported complement are each a single repeated Thumb
instruction encoding:

- ``residual_arch_nop_padding``   (8 bytes / 4 halfwords)  -- ``NOP`` (0xBF00)
- ``residual_legacy_nop_padding`` (126 bytes / 63 halfwords) -- the legacy
  ``MOV r8, r8`` NOP idiom (0x46C0)

Those rows are pinned with a `content_sha256` of the exact stock bytes at
those addresses, but the pin was never independently reconstructed -- the TSV
still records "reconstructible semantics; stock authority unresolved". This
tool closes that gap for the two padding categories only: it assembles the
two canonical Thumb instructions with the project's own ARMv6-M clang/lld
toolchain (the same toolchain used for the Touch source image), extracts
their compiled 2-byte encodings, tiles them to the pinned byte counts, and
requires the SHA-256 of the *compiler-produced* bytes to equal the SHA-256
already pinned in the manifest for the authenticated stock bytes.

This does not place the reconstructed bytes into any buildable firmware
image (the source-built Touch candidate is a freestanding link with its own
layout, not an address-matched replacement of the stock image), so it does
not by itself production-route any bytes. It converts an unverified
"reconstructible" claim into a verified one and leaves everything else in the
19,442-byte typed complement exactly as pinned.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUCKETS_TSV = ROOT / "tools/manifests/g2-touch-final-physical-byte-buckets.tsv"

# (bucket row name, Thumb source line, expected little-endian encoding)
CATEGORIES = [
    {
        "bucket": "typed_code_residual_arch_nop_padding",
        "asm": "nop",
        "encoding": b"\x00\xbf",
        "mnemonic": "NOP (Thumb T1 hint, ARMv6-M)",
    },
    {
        "bucket": "typed_code_residual_legacy_nop_padding",
        "asm": "mov r8, r8",
        "encoding": b"\xc0\x46",
        "mnemonic": "MOV r8, r8 (legacy NOP idiom)",
    },
]


class ReconstructionError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tool(candidates: list[str]) -> str:
    for candidate in candidates:
        if os.path.isabs(candidate) and Path(candidate).is_file():
            return candidate
        resolved = shutil.which(candidate)
        if resolved:
            return resolved
    raise ReconstructionError(f"required build tool unavailable: {', '.join(candidates)}")


def load_pinned_buckets() -> dict[str, dict[str, str]]:
    if not BUCKETS_TSV.exists():
        raise ReconstructionError(f"missing pinned bucket manifest: {BUCKETS_TSV}")
    rows: dict[str, dict[str, str]] = {}
    with BUCKETS_TSV.open(newline="") as handle:
        lines = [line for line in handle if not line.startswith("# ")]
    for row in csv.DictReader(lines, delimiter="\t"):
        rows[row["category"]] = row
    return rows


def compile_encoding(clang: str, objcopy: str, asm: str, workdir: Path) -> bytes:
    source = workdir / "insn.s"
    source.write_text(f".syntax unified\n.thumb\n.text\n{asm}\n")
    obj = workdir / "insn.o"
    subprocess.run(
        [clang, "--target=armv6m-none-eabi", "-mcpu=cortex-m0plus", "-mthumb",
         "-c", str(source), "-o", str(obj)],
        check=True, capture_output=True, text=True,
    )
    raw = workdir / "insn.bin"
    subprocess.run([objcopy, "-O", "binary", str(obj), str(raw)],
                    check=True, capture_output=True, text=True)
    data = raw.read_bytes()
    if len(data) != 2:
        raise ReconstructionError(f"expected a single 2-byte Thumb instruction, got {len(data)} bytes")
    return data


def reconstruct(clang: str | None = None, objcopy: str | None = None) -> dict:
    clang_tool = tool([clang] if clang else [
        "/opt/homebrew/opt/llvm/bin/clang", "clang",
    ])
    objcopy_tool = tool([objcopy] if objcopy else [
        "/opt/homebrew/opt/llvm/bin/llvm-objcopy", "llvm-objcopy",
    ])
    pinned = load_pinned_buckets()
    results = []
    with tempfile.TemporaryDirectory(prefix="g2-touch-nop-padding-") as directory:
        workdir = Path(directory)
        for category in CATEGORIES:
            row = pinned.get(category["bucket"])
            if row is None:
                raise ReconstructionError(f"pinned bucket missing: {category['bucket']}")
            byte_count = int(row["bytes"])
            if byte_count % 2 != 0:
                raise ReconstructionError(f"{category['bucket']}: odd byte count {byte_count}")
            compiled = compile_encoding(clang_tool, objcopy_tool, category["asm"], workdir)
            if compiled != category["encoding"]:
                raise ReconstructionError(
                    f"{category['bucket']}: compiled encoding {compiled.hex()} != "
                    f"expected {category['encoding'].hex()} for {category['mnemonic']!r}; "
                    "toolchain no longer emits the assumed idiom"
                )
            reconstructed = compiled * (byte_count // 2)
            observed_sha256 = sha256(reconstructed)
            pinned_sha256 = row["content_sha256"]
            if observed_sha256 != pinned_sha256:
                raise ReconstructionError(
                    f"{category['bucket']}: reconstructed SHA-256 {observed_sha256} does not "
                    f"match pinned stock content SHA-256 {pinned_sha256}"
                )
            results.append({
                "bucket": category["bucket"],
                "mnemonic": category["mnemonic"],
                "bytes": byte_count,
                "compiled_encoding": compiled.hex(),
                "content_sha256": observed_sha256,
                "matches_pinned_stock_content": True,
                "production_routed": False,
            })
    total_bytes = sum(entry["bytes"] for entry in results)
    return {
        "schema_version": 1,
        "component": "G2 Touch residual NOP-padding reconstruction",
        "toolchain": {"clang": clang_tool, "llvm_objcopy": objcopy_tool},
        "categories": results,
        "reconstructed_bytes": total_bytes,
        "production_routed": False,
        "note": (
            "Reconstruction proves the pinned stock content is exactly the "
            "compiler-emitted Thumb NOP idiom at the byte level. It does not "
            "place these bytes in any buildable firmware image."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clang")
    parser.add_argument("--objcopy")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    report = reconstruct(args.clang, args.objcopy)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for entry in report["categories"]:
            print(f"{entry['bucket']}: {entry['bytes']} bytes reconstructed and verified "
                  f"({entry['mnemonic']})")
        print(f"total reconstructed_bytes={report['reconstructed_bytes']} "
              f"production_routed={report['production_routed']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ReconstructionError, subprocess.CalledProcessError) as error:
        raise SystemExit(f"Touch NOP-padding reconstruction failed: {error}") from error
