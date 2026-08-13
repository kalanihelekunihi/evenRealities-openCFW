#!/usr/bin/env python3
"""Compare clean-room IAR math/errno candidates with authenticated stock code."""

from __future__ import annotations

import argparse
import random
import struct
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x0043_7FE0
IMAGE_SIZE = 3_523_396
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"

STOCK = {
    "sqrtf": 0x0043_97A8,
    "domain_error": 0x0043_9CA4,
    "range_error": 0x0043_9CB2,
    "errno_address": 0x0043_9CC4,
}
CANDIDATE_BASE = 0x0010_0000
CANDIDATE_OFFSETS = {
    "sqrtf": 0x000,
    "domain_error": 0x100,
    "range_error": 0x200,
    "errno_address": 0x300,
}
STOP_ADDRESS = 0x0010_0F00
SRAM_BASE = 0x2000_0000
SRAM_SIZE = 0x0010_0000
STACK_ADDRESS = SRAM_BASE + 0x0001_0000
ERRNO_ADDRESS = 0x2007_4F14

FILES = {
    "sqrtf": "open_cfw_iar_sqrtf.bin",
    "domain_error": "open_cfw_iar_domain_error.bin",
    "range_error": "open_cfw_iar_range_error.bin",
    "errno_address": "open_cfw_iar_errno_address.bin",
}


class QualificationError(RuntimeError):
    """Raised when candidate target behavior diverges from stock."""


def sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def encode_thumb_b_w(instruction_address: int, target_address: int) -> bytes:
    displacement = target_address - (instruction_address + 4)
    if displacement % 2 or not -(1 << 24) <= displacement < (1 << 24):
        raise QualificationError("candidate branch target is not encodable")
    immediate = (displacement >> 1) & 0xFFFFFF
    sign = (immediate >> 23) & 1
    i1 = (immediate >> 22) & 1
    i2 = (immediate >> 21) & 1
    imm10 = (immediate >> 11) & 0x3FF
    imm11 = immediate & 0x7FF
    j1 = (~(i1 ^ sign)) & 1
    j2 = (~(i2 ^ sign)) & 1
    return struct.pack(
        "<HH",
        0xF000 | (sign << 10) | imm10,
        0x9000 | (j1 << 13) | (j2 << 11) | imm11,
    )


def qualify(
    binary_dir: Path,
    image: Path = DEFAULT_IMAGE,
    iterations: int = 2_000,
    seed: int = 0x4397A8,
) -> dict[str, int]:
    try:
        from unicorn import Uc, UC_ARCH_ARM, UC_MODE_THUMB
        from unicorn.arm_const import (
            UC_ARM_REG_CPSR,
            UC_ARM_REG_LR,
            UC_ARM_REG_R0,
            UC_ARM_REG_R1,
            UC_ARM_REG_R2,
            UC_ARM_REG_R3,
            UC_ARM_REG_R7,
            UC_ARM_REG_R12,
            UC_ARM_REG_S0,
            UC_ARM_REG_SP,
            UC_CPU_ARM_CORTEX_M33,
        )
    except ImportError as exc:
        raise QualificationError("Python unicorn is required for target emulation") from exc

    stock_blob = image.read_bytes()
    if len(stock_blob) != IMAGE_SIZE or sha256(stock_blob) != IMAGE_SHA256:
        raise QualificationError("official Apollo-main image identity mismatch")

    candidates = {name: (binary_dir / filename).read_bytes() for name, filename in FILES.items()}
    if len(candidates["sqrtf"]) != 28:
        raise QualificationError("sqrtf candidate size changed")
    patched_sqrtf = bytearray(candidates["sqrtf"])
    branch_site = CANDIDATE_BASE + CANDIDATE_OFFSETS["sqrtf"] + 24
    domain_target = CANDIDATE_BASE + CANDIDATE_OFFSETS["domain_error"]
    patched_sqrtf[24:28] = encode_thumb_b_w(branch_site, domain_target)
    candidates["sqrtf"] = bytes(patched_sqrtf)

    engine = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    # Unicorn has no Cortex-M55 model. M33 supplies the same Armv8-M
    # single-precision VFP instructions used by this bounded function.
    engine.ctl_set_cpu_model(UC_CPU_ARM_CORTEX_M33)
    stock_map_base = LOAD_BASE & ~0xFFF
    stock_prefix = LOAD_BASE - stock_map_base
    stock_map_size = (stock_prefix + len(stock_blob) + 0xFFF) & ~0xFFF
    engine.mem_map(stock_map_base, stock_map_size)
    engine.mem_write(LOAD_BASE, stock_blob)
    engine.mem_map(CANDIDATE_BASE, 0x1000)
    engine.mem_map(SRAM_BASE, SRAM_SIZE)
    for name, body in candidates.items():
        engine.mem_write(CANDIDATE_BASE + CANDIDATE_OFFSETS[name], body)

    core_registers = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)

    def reset(register_seed: int, s0_bits: int = 0) -> None:
        values = (
            register_seed ^ 0x1020_3040,
            register_seed ^ 0x5060_7080,
            register_seed ^ 0x90A0_B0C0,
            register_seed ^ 0xD0E0_F000,
        )
        for register, value in zip(core_registers, values):
            engine.reg_write(register, value & 0xFFFF_FFFF)
        engine.reg_write(UC_ARM_REG_R7, (register_seed ^ 0x7777_7777) & 0xFFFF_FFFF)
        engine.reg_write(UC_ARM_REG_R12, (register_seed ^ 0xCCCC_CCCC) & 0xFFFF_FFFF)
        engine.reg_write(UC_ARM_REG_S0, s0_bits)
        engine.reg_write(UC_ARM_REG_SP, STACK_ADDRESS)
        engine.reg_write(UC_ARM_REG_LR, STOP_ADDRESS | 1)
        engine.reg_write(UC_ARM_REG_CPSR, engine.reg_read(UC_ARM_REG_CPSR) | (1 << 5))
        engine.mem_write(ERRNO_ADDRESS, struct.pack("<I", 0xA5A5_A5A5))

    def run(address: int) -> tuple[int, int, tuple[int, ...], int, int]:
        engine.emu_start(address | 1, STOP_ADDRESS, count=10_000)
        return (
            engine.reg_read(UC_ARM_REG_S0) & 0xFFFF_FFFF,
            struct.unpack("<I", engine.mem_read(ERRNO_ADDRESS, 4))[0],
            tuple(engine.reg_read(register) & 0xFFFF_FFFF for register in core_registers),
            engine.reg_read(UC_ARM_REG_R12) & 0xFFFF_FFFF,
            engine.reg_read(UC_ARM_REG_SP) & 0xFFFF_FFFF,
        )

    def compare(name: str, register_seed: int, s0_bits: int = 0) -> None:
        reset(register_seed, s0_bits)
        expected = run(STOCK[name])
        reset(register_seed, s0_bits)
        observed = run(CANDIDATE_BASE + CANDIDATE_OFFSETS[name])
        if name == "errno_address":
            # r1 is caller-saved and stock happens to return the saved r7 value there.
            expected = (expected[0], expected[1], (expected[2][0],), expected[3], expected[4])
            observed = (observed[0], observed[1], (observed[2][0],), observed[3], observed[4])
        if observed != expected:
            raise QualificationError(
                f"{name} diverged: seed=0x{register_seed:08x} "
                f"s0=0x{s0_bits:08x} expected={expected!r} observed={observed!r}"
            )

    rng = random.Random(seed)
    fixed_float_bits = (
        0x0000_0000,
        0x8000_0000,
        0x3F80_0000,
        0x4000_0000,
        0x7F7F_FFFF,
        0x7F80_0000,
        0xBF80_0000,
        0xFF80_0000,
        0x7FC0_0001,
        0x7F80_0001,
        0xFFC0_0001,
    )
    completed = {name: 0 for name in STOCK}
    for iteration in range(iterations):
        bits = fixed_float_bits[iteration] if iteration < len(fixed_float_bits) else rng.getrandbits(32)
        compare("sqrtf", rng.getrandbits(32), bits)
        completed["sqrtf"] += 1

    for name in ("domain_error", "range_error", "errno_address"):
        for _ in range(max(64, iterations // 8)):
            compare(name, rng.getrandbits(32))
            completed[name] += 1
    return completed


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary_dir", type=Path)
    parser.add_argument("--image", type=Path, default=DEFAULT_IMAGE)
    parser.add_argument("--iterations", type=int, default=2_000)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x4397A8)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = qualify(args.binary_dir, args.image, args.iterations, args.seed)
    print("G2 IAR math/errno candidate emulation: PASS")
    for name in STOCK:
        print(f"{name}: {result[name]} vectors")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
