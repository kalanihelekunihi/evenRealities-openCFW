#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify the reconstructed image-A boot-region tail (pad + CRC + XIP length).

Compiles the reviewed data source, independently recomputes the BINH stage-1
block CRC-32/MPEG-2 trailer and stage-2 XIP-text length word from the
authenticated stock image via tools/analyze_g2_codec_fwpk_segments.py's own
parser/CRC (not by trusting the literal in the C source), and requires the
compiled bytes to match both that independent recomputation and the stock
bytes at package offset 0x0000B58C. This is a host-side data check, not a
C-SKY instruction trace; the reconstructed span contains no instructions.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from analyze_g2_codec_fwpk_segments import (
    CODEC_SHA256 as IMAGE_SHA,
    parse_fwpk,
    parse_main_image,
)
from build_transparent_image import Elf32
from verify_gx8002_logging import check_paths

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/firmware_codec.bin"
SOURCE = ROOT / "components/shared/gx8002/runtime_gx8002_image_a_stage1_tail.c"
HEADER = SOURCE.with_suffix(".h")
SYMBOL = "open_cfw_gx8002_image_a_stage1_tail"
SECTION_NAME = ".data." + SYMBOL
PACKAGE_OFFSET = 0x0000B58C
TAIL_SIZE = 4100
ZERO_SIZE = 4092
FLAGS = ["-O2", "-fno-zero-initialized-in-bss", "-mcpu=ck804ef", "-mhard-float", "-ffreestanding", "-fno-builtin",
         "-ffunction-sections", "-fdata-sections", "-Wall", "-Wextra", "-Werror"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compile(prefix: Path, output_dir: Path, crc: int, xip_size: int) -> bytes:
    output_dir.mkdir(parents=True, exist_ok=True)
    obj = output_dir / "image-a-stage1-tail.o"
    pre = str(prefix / "csky-unknown-elf-")
    subprocess.run([pre + "gcc", *FLAGS, f"-DOPEN_CFW_STAGE1_CRC={crc}U",
                    f"-DOPEN_CFW_STAGE2_XIP_SIZE={xip_size}U", "-I", str(SOURCE.parent),
                    "-c", str(SOURCE), "-o", str(obj)], check=True,
                   capture_output=True, text=True)
    elf = Elf32(obj.read_bytes(), str(obj))
    section = next(s for s in elf.sections if s["name"] == SECTION_NAME)
    if elf.relocations(section["index"]):
        raise ValueError("unresolved relocation in generated data section")
    payload = elf.contents(section)
    if len(payload) != TAIL_SIZE:
        raise ValueError("compiled tail size changed")
    return payload


def _expected_bytes(stock: bytes) -> tuple[bytes, dict]:
    if len(stock) != 326092 or sha(stock) != IMAGE_SHA:
        raise ValueError("codec baseline changed")
    parsed = parse_fwpk(stock)
    _, main_record = parsed["records"]
    image_a = parse_main_image(stock[main_record["offset"]:])["image_a"]
    crc = int(image_a["stage1_block_crc32_mpeg2"], 16)
    xip_len = image_a["stage2_xip_text_size"]
    expected = bytearray(TAIL_SIZE)
    expected[ZERO_SIZE:ZERO_SIZE + 4] = crc.to_bytes(4, "little")
    expected[ZERO_SIZE + 4:ZERO_SIZE + 8] = xip_len.to_bytes(4, "little")
    return bytes(expected), image_a


def verify(prefix=None, sdk=None, output=None) -> dict:
    check_paths(prefix, sdk)
    prefix = prefix or (ROOT / "build/csky-macos/install/bin")
    stock = IMAGE.read_bytes()
    stock_slice = stock[PACKAGE_OFFSET:PACKAGE_OFFSET + TAIL_SIZE]
    if len(stock_slice) != TAIL_SIZE:
        raise ValueError("stock slice out of range")
    expected, _ = _expected_bytes(stock)
    if expected != stock_slice:
        raise ValueError("independently recomputed tail does not match stock bytes")
    if any(stock_slice[:ZERO_SIZE]):
        raise ValueError("assumed zero-fill span is not all-zero in stock")

    out_dir = output or (ROOT / "build/continue-analysis/CD-009")
    payload = _compile(prefix, out_dir, int.from_bytes(expected[ZERO_SIZE:ZERO_SIZE+4], "little"),
                       int.from_bytes(expected[ZERO_SIZE+4:ZERO_SIZE+8], "little"))
    if payload != stock_slice:
        raise ValueError("compiled data does not match stock/recomputed bytes")

    result = {
        "functions": [{
            "symbol": SYMBOL,
            "section_name": SECTION_NAME,
            "ownership_kind": "generated_source_data",
            "compiled_bytes": TAIL_SIZE,
            "compiled_sha256": sha(payload),
            "stock_occurrences": [{
                "symbol": SYMBOL,
                "package_offset": PACKAGE_OFFSET,
                "bytes": TAIL_SIZE,
                "sha256": sha(stock_slice),
                "region": "image_a_stage1_tail",
            }],
        }],
        "source_admitted": True,
        "hardware_qualified": False,
        "source_sha256": sha(SOURCE.read_bytes()),
        "verifier_sha256": sha(Path(__file__).read_bytes()),
        "header_sha256": sha(HEADER.read_bytes()),
        "stage1_block_crc32_mpeg2": "0x%08X" % int.from_bytes(stock_slice[ZERO_SIZE:ZERO_SIZE + 4], "little"),
        "stage2_xip_text_size": int.from_bytes(stock_slice[ZERO_SIZE + 4:ZERO_SIZE + 8], "little"),
        "limits": [
            "Covers only the deterministic pad/CRC/length tail; the preceding "
            "BINH stage-1 block header/code and the following stage-2 XIP text "
            "remain separate, still-opaque spans.",
            "The CRC-32/MPEG-2 trailer and XIP length word are format bookkeeping, "
            "independently recomputed here from the public BINH algorithm; they "
            "are not a claim of redistribution rights over the surrounding "
            "still-proprietary block content that the checksum covers.",
        ],
    }
    return result


if __name__ == "__main__":
    (ROOT / "docs/research/gx8002-image-a-stage1-tail-verification.json").write_text(
        json.dumps(verify(), indent=2) + "\n")
