#!/usr/bin/env python3
"""Generate and verify the transparent R1 model-data C initializer."""

from __future__ import annotations

import argparse
import hashlib
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
DEFAULT_OUTPUT = (
    ROOT / "reconstructed/model_data/r1_model_data_generated.inc"
)
LOAD_BASE = 0x00027000
IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"
MODEL_START = 0x000B19E4
MODEL_END = 0x000BCED8
MODEL_SHA256 = "cde455f534ef8528509bca8e7c65460af63187d835274ec4fa007ce1811dd470"
VIEWS = {
    "Goodix generated model": (
        0x000B19E4,
        0x000B5734,
        "655f94539fd186e8c99d5e616c296dba63b247a114963870c044798cd75fef47",
    ),
    "GoMore sleep model below 100": (
        0x000B2458,
        0x000B7998,
        "da353b02976da84378f6321b2f5ec7cbc4c184eb706b1d6a7fad5499258c4861",
    ),
    "GoMore sleep model 100 and above": (
        0x000B7998,
        0x000BCED8,
        "09f807f0c73daae139a0f2aa39ec37b4c57db8c6a7178e943aec6bd8913ee82c",
    ),
}


def recovered_region(image_path: Path) -> bytes:
    image = image_path.read_bytes()
    if hashlib.sha256(image).hexdigest() != IMAGE_SHA256:
        raise ValueError("unexpected reconstructed application SHA-256")
    region = image[MODEL_START - LOAD_BASE:MODEL_END - LOAD_BASE]
    if len(region) != MODEL_END - MODEL_START or \
            hashlib.sha256(region).hexdigest() != MODEL_SHA256:
        raise ValueError("recovered model-region extent or SHA-256 changed")
    for name, (start, end, expected) in VIEWS.items():
        data = image[start - LOAD_BASE:end - LOAD_BASE]
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"{name} SHA-256 changed")
    return region


def render(region: bytes) -> str:
    if len(region) % 4:
        raise ValueError("model region is not word aligned")
    words = struct.unpack(f"<{len(region) // 4}I", region)
    lines = [
        "/* Generated from the SHA-pinned Ghidra model-data region",
        " * 0x000B19E4..<0x000BCED8.  Do not edit by hand. */",
    ]
    for offset in range(0, len(words), 6):
        values = ", ".join(
            f"UINT32_C(0x{word:08X})" for word in words[offset:offset + 6]
        )
        lines.append(f"    {values},")
    return "\n".join(lines) + "\n"


def verify(image_path: Path = DEFAULT_IMAGE,
           output_path: Path = DEFAULT_OUTPUT) -> None:
    expected = render(recovered_region(image_path))
    if not output_path.is_file() or output_path.read_text() != expected:
        raise AssertionError(
            f"transparent model-data initializer is stale: {output_path}"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = render(recovered_region(args.image))
    if args.check:
        if not args.output.is_file() or args.output.read_text() != generated:
            raise SystemExit(f"stale generated model data: {args.output}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(generated)
    print(
        "R1 model data verified: 11,581 transparent words, "
        "Goodix 3,924 words, GoMore 5,456 + 5,456 words"
    )


if __name__ == "__main__":
    main()
