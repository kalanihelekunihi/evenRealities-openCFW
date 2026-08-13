#!/usr/bin/env python3
"""Generate deterministic, halfword-aligned Apollo-main Ghidra chunks."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re


EXPECTED_FIRMWARE_SIZE = 3_523_396
EXPECTED_FIRMWARE_SHA256 = (
    "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
)
LOADER_BASE = 0x0043_7FE0
APPLICATION_START = 0x0043_8000
APPLICATION_END = 0x0079_4324
DEFAULT_CHUNKS = 64
FUNCTION_ENTRY = re.compile(r"OPENCFW_FUNCTION_BEGIN entry=([0-9A-Fa-f]+)\b")


class ChunkError(RuntimeError):
    """Raised when the authenticated image or generated tiling is invalid."""


def authenticate_firmware(path: Path) -> None:
    data = path.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if len(data) != EXPECTED_FIRMWARE_SIZE or digest != EXPECTED_FIRMWARE_SHA256:
        raise ChunkError(
            "unexpected Apollo firmware identity: "
            f"size={len(data)} sha256={digest}"
        )
    if LOADER_BASE + len(data) != APPLICATION_END:
        raise ChunkError("loader base and authenticated file size no longer agree")


def chunk_boundaries(count: int = DEFAULT_CHUNKS) -> list[int]:
    if count <= 0:
        raise ChunkError("chunk count must be positive")
    size = APPLICATION_END - APPLICATION_START
    boundaries = [
        APPLICATION_START + (((size * index) // count) & ~1)
        for index in range(count)
    ]
    boundaries.append(APPLICATION_END)
    if any(right <= left for left, right in zip(boundaries, boundaries[1:])):
        raise ChunkError("chunk count is too large for a non-empty tiling")
    if boundaries[0] != APPLICATION_START or boundaries[-1] != APPLICATION_END:
        raise ChunkError("generated chunks do not cover the application")
    return boundaries


def balanced_boundaries(entries: list[int], count: int = DEFAULT_CHUNKS) -> list[int]:
    entries = sorted(set(entries))
    if len(entries) < count:
        raise ChunkError("fewer discovered functions than requested chunks")
    if any(entry < APPLICATION_START or entry >= APPLICATION_END for entry in entries):
        raise ChunkError("discovered function lies outside Apollo main")
    boundaries = [APPLICATION_START]
    for index in range(1, count):
        boundary = entries[(len(entries) * index) // count]
        if boundary <= boundaries[-1] or boundary & 1:
            raise ChunkError("function-balanced boundary is not increasing/aligned")
        boundaries.append(boundary)
    boundaries.append(APPLICATION_END)
    return boundaries


def load_function_entries(log_dir: Path) -> list[int]:
    paths = sorted(log_dir.glob("*.log"))
    if not paths:
        raise ChunkError(f"no Ghidra logs found in {log_dir}")
    entries: list[int] = []
    for path in paths:
        for match in FUNCTION_ENTRY.finditer(path.read_text(errors="replace")):
            entries.append(int(match.group(1), 16))
    if not entries:
        raise ChunkError("Ghidra logs contain no function entries")
    if len(entries) != len(set(entries)):
        raise ChunkError("Ghidra log corpus contains duplicate function entries")
    return sorted(entries)


def render_manifest(
    count: int = DEFAULT_CHUNKS,
    boundaries: list[int] | None = None,
) -> str:
    boundaries = chunk_boundaries(count) if boundaries is None else boundaries
    if len(boundaries) != count + 1:
        raise ChunkError("boundary count does not match chunk count")
    lines = [
        "# shard_id\tstart\tend_exclusive\tfile_offset_start\tfile_offset_end",
    ]
    for index, (start, end) in enumerate(zip(boundaries, boundaries[1:])):
        lines.append(
            f"apollo-{index:02d}\t0x{start:08X}\t0x{end:08X}\t"
            f"0x{start - LOADER_BASE:08X}\t0x{end - LOADER_BASE:08X}"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--firmware",
        type=Path,
        default=root / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin",
    )
    parser.add_argument("--chunks", type=int, default=DEFAULT_CHUNKS)
    parser.add_argument(
        "--balance-log-dir",
        type=Path,
        help="balance boundaries by OPENCFW_FUNCTION_BEGIN entries in batch logs",
    )
    parser.add_argument("--expected-functions", type=int)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    authenticate_firmware(args.firmware)
    boundaries = None
    if args.balance_log_dir is not None:
        entries = load_function_entries(args.balance_log_dir)
        if args.expected_functions is not None and len(entries) != args.expected_functions:
            raise ChunkError(
                f"expected {args.expected_functions} functions, observed {len(entries)}"
            )
        boundaries = balanced_boundaries(entries, args.chunks)
    manifest = render_manifest(args.chunks, boundaries)
    if args.output is None:
        print(manifest, end="")
    else:
        args.output.write_text(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
