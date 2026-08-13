#!/usr/bin/env python3
"""Trace the exact AmbiqSuite 5.1.0 gradient ELF under Unicorn.

This is an analysis oracle, not a production implementation. It loads only the
authenticated ``lv_ambiq_gradient_create`` section and its read-only constants,
intercepts every relocated Nema call before execution, and emits the observable
call stream as JSON. No device, transport, signer, or flash path exists.

The tool requires Python Unicorn. The exact archive is intentionally supplied
by the caller because its redistribution status differs from OpenCFW source.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import struct
import sys
from pathlib import Path
from typing import Any

from analyze_g2_nemagfx_ambiq_provenance import AuditError, _ar_member, _elf32_sections


EXPECTED_SECTION_SHA256 = "5870d79c49ee8bd0dfa4b5bf8f6f39b04ed45148c0c00b774467149292d83ae4"
EXPECTED_SECTION_SIZE = 1_416
EXPECTED_RODATA = bytes.fromhex(
    "00007f4300007f4300007f4300007f43"
    "00007f4300007f4300007f4300000000"
    "00000000000000000000000000000000"
)

CODE_BASE = 0x0010_0000
RODATA_BASE = 0x0020_0000
CONTEXT_CELL = 0x0030_0000
CONTEXT_BASE = 0x0030_1000
INPUT_BASE = 0x0040_0000
STACK_BASE = 0x0050_0000
RETURN_ADDRESS = CODE_BASE + 0x900

CALLS = {
    0x02A: "set_clip_temp",
    0x03A: "set_blend",
    0x040: "enable_gradient",
    0x0DA: "interpolate_rect_colors",
    0x0EC: "fill_rect",
    0x0F2: "enable_gradient",
    0x100: "set_clip_pop",
    0x3AC: "set_gradient",
    0x3BE: "fill_rect",
    0x49E: "enable_gradient",
    0x4D2: "rgba",
    0x4E0: "fill_rect",
    0x514: "rgba",
    0x524: "fill_rect",
}


def _float_from_bits(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits & 0xFFFF_FFFF))[0]


def _color(machine: Any, address: int) -> list[float]:
    return list(struct.unpack("<4f", machine.mem_read(address, 16)))


def trace_gradient(
    archive: Path,
    stops: list[float],
    colors: list[list[float]],
    width: int,
    texture: int,
) -> list[dict[str, Any]]:
    try:
        from unicorn import Uc, UcError, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_MCLASS, UC_MODE_THUMB
        from unicorn import arm_const
    except ImportError as exc:
        raise AuditError("Python Unicorn is required for exact-object emulation") from exc

    if len(stops) != len(colors):
        raise AuditError("each stop must have exactly one RGBA float vector")
    if width <= 0 or texture < 0 or texture > 0xFF:
        raise AuditError("width must be positive and texture must fit nema_tex_t")
    if any(len(color) != 4 for color in colors):
        raise AuditError("every color must contain four float channels")

    sections = _elf32_sections(_ar_member(archive.read_bytes(), "ambiq_nema_extension.o"))
    code = bytearray(sections[".text.lv_ambiq_gradient_create"])
    rodata = sections[".rodata"]
    if (
        len(code) != EXPECTED_SECTION_SIZE
        or hashlib.sha256(code).hexdigest() != EXPECTED_SECTION_SHA256
        or rodata != EXPECTED_RODATA
    ):
        raise AuditError("gradient section or read-only constants changed")

    # These are the section's two R_ARM_ABS32 literal relocations. Calls are
    # intercepted at their exact relocation offsets, so no branch relocation
    # rewriting or external library code is needed.
    struct.pack_into("<I", code, 0x278, CONTEXT_CELL)
    struct.pack_into("<I", code, 0x27C, RODATA_BASE)

    machine = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
    for address, size in (
        (CODE_BASE, 0x1000),
        (RODATA_BASE, 0x1000),
        (CONTEXT_CELL, 0x2000),
        (INPUT_BASE, 0x4000),
        (STACK_BASE, 0x2000),
    ):
        machine.mem_map(address, size)
    machine.mem_write(CODE_BASE, bytes(code))
    machine.mem_write(RODATA_BASE, rodata)
    machine.mem_write(CONTEXT_CELL, struct.pack("<I", CONTEXT_BASE))
    machine.mem_write(
        CONTEXT_BASE + 0x3C + texture * 0x18,
        struct.pack("<I", width),
    )

    stops_address = INPUT_BASE
    colors_address = INPUT_BASE + 0x1000
    if stops:
        machine.mem_write(stops_address, struct.pack(f"<{len(stops)}f", *stops))
        flattened = [channel for color in colors for channel in color]
        machine.mem_write(
            colors_address, struct.pack(f"<{len(flattened)}f", *flattened)
        )

    general_registers = [
        arm_const.UC_ARM_REG_R0,
        arm_const.UC_ARM_REG_R1,
        arm_const.UC_ARM_REG_R2,
        arm_const.UC_ARM_REG_R3,
    ]
    single_registers = [
        getattr(arm_const, f"UC_ARM_REG_S{index}") for index in range(12)
    ]
    trace: list[dict[str, Any]] = []

    def hook(machine: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        offset = address - CODE_BASE
        if address == RETURN_ADDRESS:
            machine.emu_stop()
            return
        if offset == 0x0D6:
            # GCC emits an M-profile coprocessor store for the zero color
            # vector on the all-invalid fallback path. Unicorn does not
            # implement this encoding, so reproduce its documented memory
            # effect before the intercepted interpolation call.
            stack = machine.reg_read(arm_const.UC_ARM_REG_SP)
            machine.mem_write(stack + 0x28, bytes(16))
            machine.reg_write(arm_const.UC_ARM_REG_PC, (address + 4) | 1)
            return
        name = CALLS.get(offset)
        if name is None:
            return
        registers = [machine.reg_read(register) for register in general_registers]
        stack = machine.reg_read(arm_const.UC_ARM_REG_SP)
        record: dict[str, Any] = {"operation": name}
        if name == "set_gradient":
            record["floats"] = [
                _float_from_bits(machine.reg_read(register))
                for register in single_registers
            ]
        elif name == "interpolate_rect_colors":
            pointers = list(struct.unpack("<3I", machine.mem_read(stack, 12)))
            record["arguments"] = registers
            record["colors"] = [_color(machine, pointer) for pointer in pointers]
        elif name == "fill_rect":
            color = struct.unpack("<I", machine.mem_read(stack, 4))[0]
            record["arguments"] = registers + [color]
        else:
            record["arguments"] = registers
        if name == "rgba":
            red, green, blue, alpha = (value & 0xFF for value in registers)
            packed = red << 24 | green << 16 | blue << 8 | alpha
            record["result"] = packed
            machine.reg_write(arm_const.UC_ARM_REG_R0, packed)
        trace.append(record)
        if offset == 0x100:  # tail B.W nema_set_clip_pop
            machine.reg_write(arm_const.UC_ARM_REG_PC, RETURN_ADDRESS | 1)
        else:
            machine.reg_write(arm_const.UC_ARM_REG_PC, (address + 4) | 1)

    machine.hook_add(UC_HOOK_CODE, hook)
    machine.reg_write(arm_const.UC_ARM_REG_SP, STACK_BASE + 0x1FF0)
    machine.reg_write(arm_const.UC_ARM_REG_LR, RETURN_ADDRESS | 1)
    machine.reg_write(arm_const.UC_ARM_REG_R0, len(stops))
    machine.reg_write(arm_const.UC_ARM_REG_R1, stops_address)
    machine.reg_write(arm_const.UC_ARM_REG_R2, colors_address)
    machine.reg_write(arm_const.UC_ARM_REG_R3, texture)
    try:
        machine.emu_start(CODE_BASE | 1, RETURN_ADDRESS + 2, count=100_000)
    except UcError as exc:
        program_counter = machine.reg_read(arm_const.UC_ARM_REG_PC)
        raise AuditError(
            f"gradient emulation failed at PC 0x{program_counter:08X}: {exc}"
        ) from exc
    return trace


def _parse_csv_floats(value: str) -> list[float]:
    if not value:
        return []
    return [float(item) for item in value.split(",")]


def _parse_colors(value: str) -> list[list[float]]:
    if not value:
        return []
    return [_parse_csv_floats(item) for item in value.split(";")]


def _json_safe(value: Any) -> Any:
    if isinstance(value, float) and not math.isfinite(value):
        return str(value)
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="exact AmbiqSuite 5.1.0 gpu_patch.a")
    parser.add_argument("--stops", default="0,1", help="comma-separated float stops")
    parser.add_argument(
        "--colors",
        default="255,0,0,255;0,0,255,255",
        help="semicolon-separated RGBA float vectors",
    )
    parser.add_argument("--width", type=int, default=64)
    parser.add_argument("--texture", type=int, default=2)
    args = parser.parse_args(argv)
    try:
        trace = trace_gradient(
            args.archive,
            _parse_csv_floats(args.stops),
            _parse_colors(args.colors),
            args.width,
            args.texture,
        )
    except (AuditError, OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(_json_safe(trace), indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
