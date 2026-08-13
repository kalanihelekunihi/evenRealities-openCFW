#!/usr/bin/env python3
"""Emulate extracted openCFW IAR-memory candidates against Python oracles."""

from __future__ import annotations

import argparse
import random
from pathlib import Path
from typing import Sequence


FUNCTIONS = (
    "open_cfw_iar_memcpy_void",
    "open_cfw_iar_memcpy_aligned_void",
    "open_cfw_iar_memmove_void",
)
CODE_BASE = 0x0010_0000
STOP_ADDRESS = CODE_BASE + 0x0F00
DATA_BASE = 0x0020_0000
DATA_SIZE = 0x4000


class QualificationError(RuntimeError):
    """Raised when an emulated memory provider diverges from its oracle."""


def qualify(binary_dir: Path, iterations: int = 2_000, seed: int = 0x439C04) -> dict[str, int]:
    try:
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
        from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_SP
    except ImportError as exc:
        raise QualificationError("Python unicorn is required for target emulation") from exc

    bodies = {name: (binary_dir / f"{name}.bin").read_bytes() for name in FUNCTIONS}
    engine = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    engine.mem_map(CODE_BASE, 0x1000)
    engine.mem_map(DATA_BASE, DATA_SIZE)
    entries: dict[str, int] = {}
    cursor = CODE_BASE
    for name in FUNCTIONS:
        entries[name] = cursor
        engine.mem_write(cursor, bodies[name])
        cursor = (cursor + len(bodies[name]) + 3) & ~3

    rng = random.Random(seed)
    completed = {name: 0 for name in FUNCTIONS}

    def run(name: str, initial: bytes, destination: int, source: int, count: int) -> bytes:
        engine.mem_write(DATA_BASE, initial)
        engine.reg_write(UC_ARM_REG_R0, DATA_BASE + destination)
        engine.reg_write(UC_ARM_REG_R1, DATA_BASE + source)
        engine.reg_write(UC_ARM_REG_R2, count)
        engine.reg_write(UC_ARM_REG_LR, STOP_ADDRESS | 1)
        engine.reg_write(UC_ARM_REG_SP, DATA_BASE + DATA_SIZE - 16)
        engine.emu_start(entries[name] | 1, STOP_ADDRESS, count=100_000)
        return bytes(engine.mem_read(DATA_BASE, len(initial)))

    fixed_lengths = tuple(range(0, 20)) + (31, 32, 33, 63, 64, 65, 127, 255, 256, 511)
    for name in FUNCTIONS:
        for iteration in range(iterations):
            count = fixed_lengths[iteration % len(fixed_lengths)] if iteration < len(fixed_lengths) else rng.randrange(0, 768)
            initial = bytes(rng.randrange(0, 256) for _ in range(4096))
            if name == "open_cfw_iar_memmove_void":
                source = rng.randrange(32, 2048 - count)
                delta = rng.randrange(-min(24, source - 16), min(24, 2048 - source - count) + 1)
                destination = source + delta
            else:
                source = 32 + rng.randrange(0, 4)
                destination = 2048 + rng.randrange(0, 4)

            expected = bytearray(initial)
            expected[destination:destination + count] = initial[source:source + count]
            observed = run(name, initial, destination, source, count)
            if observed != bytes(expected):
                raise QualificationError(
                    f"{name} diverged at iteration {iteration}: "
                    f"dst={destination} src={source} count={count}"
                )
            completed[name] += 1

    return completed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary_dir", type=Path)
    parser.add_argument("--iterations", type=int, default=2_000)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x439C04)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = qualify(args.binary_dir, args.iterations, args.seed)
    print("G2 IAR memory candidate emulation: PASS")
    for name in FUNCTIONS:
        print(f"{name}: {result[name]} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
