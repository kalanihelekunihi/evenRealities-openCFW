#!/usr/bin/env python3
"""Compare stock and source-candidate memory providers by Thumb instruction count."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence


CODE_BASE = 0x0010_0000
STOP_ADDRESS = CODE_BASE + 0x0F00
STOCK_BASE = 0x0043_9000
DATA_BASE = 0x0020_0000
DATA_SIZE = 0x8000

CANDIDATE_NAMES = {
    "memcpy": "open_cfw_iar_memcpy_void",
    "memcpy_aligned": "open_cfw_iar_memcpy_aligned_void",
    "memmove": "open_cfw_iar_memmove_void",
}
STOCK_ENTRIES = {
    "memcpy": 0x0043_9BE4,
    "memcpy_aligned": 0x0043_9C04,
    "memmove": 0x0043_9710,
}


class BenchmarkError(RuntimeError):
    """Raised when benchmark inputs or provider results are invalid."""


def benchmark(binary_dir: Path, stock_island: Path) -> dict[str, Any]:
    try:
        from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_HOOK_MEM_INVALID, UC_MODE_THUMB
        from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP
    except ImportError as exc:
        raise BenchmarkError("Python unicorn is required") from exc

    stock = stock_island.read_bytes()
    if len(stock) != 0x0D00:
        raise BenchmarkError("stock island must cover [0x00439000,0x00439D00)")

    engine = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    engine.mem_map(CODE_BASE, 0x1000)
    engine.mem_map(STOCK_BASE, 0x1000)
    engine.mem_map(DATA_BASE, DATA_SIZE)
    engine.mem_write(STOCK_BASE, stock)

    candidate_entries: dict[str, int] = {}
    cursor = CODE_BASE
    for family, name in CANDIDATE_NAMES.items():
        body = (binary_dir / f"{name}.bin").read_bytes()
        candidate_entries[family] = cursor
        engine.mem_write(cursor, body)
        cursor = (cursor + len(body) + 3) & ~3

    counter = [0]
    invalid_access = [None]

    def count_instruction(_engine, _address, _size, _user_data) -> None:
        counter[0] += 1

    engine.hook_add(UC_HOOK_CODE, count_instruction)

    def record_invalid(_engine, access, address, size, value, _user_data) -> bool:
        invalid_access[0] = (access, address, size, value)
        return False

    engine.hook_add(UC_HOOK_MEM_INVALID, record_invalid)
    initial = bytes((index * 29 + 17) & 0xFF for index in range(8192))

    def execute(entry: int, destination: int, source: int, count: int) -> tuple[bytes, int]:
        engine.mem_write(DATA_BASE, initial)
        engine.reg_write(UC_ARM_REG_R0, DATA_BASE + destination)
        engine.reg_write(UC_ARM_REG_R1, DATA_BASE + source)
        engine.reg_write(UC_ARM_REG_R2, count)
        engine.reg_write(UC_ARM_REG_LR, STOP_ADDRESS | 1)
        engine.reg_write(UC_ARM_REG_SP, DATA_BASE + DATA_SIZE - 16)
        counter[0] = 0
        invalid_access[0] = None
        try:
            engine.emu_start(entry | 1, STOP_ADDRESS, count=1_000_000)
        except Exception as exc:
            raise BenchmarkError(
                f"emulation failed at entry 0x{entry:08X}, dst={destination}, "
                f"src={source}, count={count}, invalid={invalid_access[0]!r}"
            ) from exc
        return bytes(engine.mem_read(DATA_BASE, len(initial))), counter[0]

    cases = []
    for family in ("memcpy", "memcpy_aligned"):
        alignments = ((0, 0),) if family == "memcpy_aligned" else ((0, 0), (1, 1), (1, 2))
        for source_alignment, destination_alignment in alignments:
            for count in (0, 1, 4, 16, 64, 256, 1024):
                source = 256 + source_alignment
                destination = 4096 + destination_alignment
                cases.append((family, f"align-{source_alignment}-{destination_alignment}", count, destination, source))
    for overlap_name, destination_delta in (("forward-nonoverlap", 2048), ("backward-overlap-aligned", 8), ("backward-overlap-unaligned", 3)):
        for count in (0, 1, 4, 16, 64, 256, 1024):
            source = 1024
            destination = source + destination_delta
            cases.append(("memmove", overlap_name, count, destination, source))

    records = []
    for family, case, count, destination, source in cases:
        expected = bytearray(initial)
        expected[destination:destination + count] = initial[source:source + count]
        stock_result, stock_instructions = execute(STOCK_ENTRIES[family], destination, source, count)
        candidate_result, candidate_instructions = execute(candidate_entries[family], destination, source, count)
        if stock_result != bytes(expected) or candidate_result != bytes(expected):
            raise BenchmarkError(f"semantic divergence: {family}/{case}/{count}")
        records.append({
            "family": family,
            "case": case,
            "bytes": count,
            "stock_instructions": stock_instructions,
            "candidate_instructions": candidate_instructions,
            "candidate_to_stock_ratio": round(candidate_instructions / stock_instructions, 4),
        })

    return {
        "metric": "Unicorn executed Thumb instruction count; not hardware cycles",
        "records": records,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary_dir", type=Path)
    parser.add_argument("stock_island", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = benchmark(args.binary_dir, args.stock_island)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("G2 IAR memory instruction benchmark: PASS")
        for item in report["records"]:
            if item["bytes"] in (64, 256, 1024):
                print(
                    f"{item['family']} {item['case']} {item['bytes']}: "
                    f"stock={item['stock_instructions']} "
                    f"candidate={item['candidate_instructions']} "
                    f"ratio={item['candidate_to_stock_ratio']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
