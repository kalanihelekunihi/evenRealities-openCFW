#!/usr/bin/env python3
"""Differentially emulate the AM-015 LVGL display accessors under Unicorn.

For each of the thirteen `lv_display_accessors.c` leaves, this loads the
*authenticated stock bytes* straight out of the official G2 2.2.6.10 image at
their real flash addresses, and separately compiles and loads
`lv_display_accessors.c` into a scratch code region. Both are executed under
the same Cortex-M/Thumb-2 emulator, with the two callees outside this leaf's
stock range (the display-default resolver and the invalidate hook) replaced
by an identical scripted mock for both runs, and their final register 0,
written object-memory bytes, and mocked call trace are required to match
exactly across many synthetic `open_cfw_lv_display_t` states.

This is an analysis/differential-test oracle, matching the pattern used by
`emulate_g2_iar_memory.py` and `analyze_g2_lvgl_display_port_closure.py`. No
device, flash, or signing operation exists here.
"""

from __future__ import annotations

import argparse
import hashlib
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402

DEFAULT_IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
LOAD_BASE = 0x0043_7FE0
SOURCE = ROOT / "components/apollo_main/core_overlay/lv_display_accessors.c"

CANDIDATE_CODE_BASE = 0x1000_0000
OBJECT_BASE = 0x2000_0000
OBJECT_SIZE = 0x1000
STACK_BASE = 0x2010_0000
STACK_SIZE = 0x1000
STOP_ADDRESS = 0x3000_0000

GET_DEFAULT_ENTRY = 0x0044FA1A
INVALIDATE_ENTRY = 0x00440656

TARGET_FLAGS = (
    "--target=thumbv7em-none-eabi",
    "-mthumb",
    "-ffreestanding",
    "-fno-builtin",
    "-ffunction-sections",
    "-fdata-sections",
    "-fno-jump-tables",
    "-fomit-frame-pointer",
    "-fno-unwind-tables",
    "-fno-asynchronous-unwind-tables",
    "-mno-unaligned-access",
    "-fropi",
    "-O2",
    "-Wall",
    "-Wextra",
    "-Werror",
)

# name -> (stock entry, arg count, has_default_fallback, has_return)
FUNCTIONS: dict[str, tuple[int, int, bool, bool]] = {
    "open_cfw_lv_display_set_offset": (0x0044FA5E, 4, True, True),
    "open_cfw_lv_display_get_horizontal_resolution": (0x0044FA7E, 1, True, True),
    "open_cfw_lv_display_get_vertical_resolution": (0x0044FAA8, 1, True, True),
    "open_cfw_lv_display_get_physical_horizontal_resolution": (0x0044FAD2, 1, True, True),
    "open_cfw_lv_display_get_physical_vertical_resolution": (0x0044FB10, 1, True, True),
    "open_cfw_lv_display_get_offset_x": (0x0044FB4E, 1, True, True),
    "open_cfw_lv_display_get_offset_y": (0x0044FB9A, 1, True, True),
    "open_cfw_lv_display_get_dpi": (0x0044FBE6, 1, True, True),
    "open_cfw_lv_display_set_buffers_internal": (0x0044FBFC, 4, True, True),
    "open_cfw_lv_display_set_byte_flag": (0x0044FC18, 2, True, False),
    "open_cfw_lv_display_set_word_field": (0x0044FC2E, 2, True, False),
    "open_cfw_lv_display_get_render_flag": (0x0044FC42, 1, False, True),
    "open_cfw_lv_display_is_double_buffered": (0x0044FC52, 1, False, True),
}
# Body byte counts/hashes pinned from
# g2/research/corpus/apollo-main/ghidra/decomp/functions.jsonl.
EXPECTED_STOCK = {
    "open_cfw_lv_display_set_offset": (32, "207ec1f42d241acae67fd6ac9dda7579ffe6e5a5cfcde2a8e250a3553f7121b8"),
    "open_cfw_lv_display_get_horizontal_resolution": (42, "bb9432604de3f11096811192d7ba407f60a48b4f736ceedf94bdee4729526540"),
    "open_cfw_lv_display_get_vertical_resolution": (42, "ba1d300d5102ccb76f7992c9ded37b560991bfb3d303205e8c9dd791e2860456"),
    "open_cfw_lv_display_get_physical_horizontal_resolution": (62, "e469a04f4c0706ca615030ae70ef941d8d5bc6b706693cdc11a2a549efbc5f56"),
    "open_cfw_lv_display_get_physical_vertical_resolution": (62, "c82c27fb9682d5bbee5fa063662aa15cde1e32b0a00894ecb6d9afe1f221503d"),
    "open_cfw_lv_display_get_offset_x": (76, "f1ca36caeeb2a10800670ccb2d42622fee342cf16b5da112ff632fa3fcb21b31"),
    "open_cfw_lv_display_get_offset_y": (76, "cb16b1ee30e7925dd6ebd633259e7dc8b43dc5b1050f301310250ee4d866cf98"),
    "open_cfw_lv_display_get_dpi": (22, "112e2c66bf0691ca9fe81bbce131de2be642f7992d647fe0b4315bf8a5759edf"),
    "open_cfw_lv_display_set_buffers_internal": (28, "72565f03710f396e2f6f4bb93d7de924d9ac57212ad6daeb57854ffca2914906"),
    "open_cfw_lv_display_set_byte_flag": (22, "1c859358b7db28e0907073e22da3e3cf49ec8ff3742c085fbf72c32e8a79283d"),
    "open_cfw_lv_display_set_word_field": (20, "69698f7766e713df6494edf41dcbcd8d2b7616863366939655ab947a24ef90f8"),
    "open_cfw_lv_display_get_render_flag": (16, "7270a021bfb6c1162ba590b3ebdacf4d0c50ddd9a1929f17e791e1c445cb130e"),
    "open_cfw_lv_display_is_double_buffered": (16, "38a97c5fd4d983f78e9e385b4f9ca02e680d2555a6feb29825b52fca132b4d15"),
}
OBJECT_SIZE_BYTES = 0x300


class QualificationError(RuntimeError):
    pass


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _compile_candidate() -> Path:
    tmp = Path("/tmp/openCFW-lvgl-display-accessors.o")
    clang = subprocess.run(
        ["xcrun", "-f", "clang"], check=True, capture_output=True, text=True
    ).stdout.strip()
    subprocess.run(
        [clang, *TARGET_FLAGS, "-c", str(SOURCE), "-o", str(tmp)],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    return tmp


def _load_stock() -> bytes:
    data = DEFAULT_IMAGE.read_bytes()
    for name, (entry, _argc, _fallback, _ret) in FUNCTIONS.items():
        size, expected_hash = EXPECTED_STOCK[name]
        offset = entry - LOAD_BASE
        span = data[offset:offset + size]
        digest = _sha256(span)
        if digest != expected_hash:
            raise QualificationError(f"stock span changed for {name}: {digest}")
    return data


def qualify(iterations: int = 500, seed: int = 0x4C56474C) -> dict[str, int]:
    try:
        from unicorn import Uc, UC_ARCH_ARM, UC_HOOK_CODE, UC_MODE_THUMB
        from unicorn.arm_const import (
            UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1,
            UC_ARM_REG_R2, UC_ARM_REG_R3, UC_ARM_REG_SP,
        )
    except ImportError as exc:
        raise QualificationError("Python unicorn is required for target emulation") from exc

    object_path = _compile_candidate()
    stock_image = _load_stock()

    candidate_bodies: dict[str, bytes] = {}
    candidate_entries: dict[str, int] = {}
    cursor = CANDIDATE_CODE_BASE
    for name in FUNCTIONS:
        body, meta = apollo_overlay.extract_isolated_function_section(object_path, name)
        expected_size, _expected_hash = EXPECTED_STOCK[name]
        candidate_bodies[name] = body
        candidate_entries[name] = cursor
        cursor = (cursor + len(body) + 7) & ~7
        if meta["relocation_count"] != 0:
            raise QualificationError(f"{name} candidate is not dependency-free")

    engine = Uc(UC_ARCH_ARM, UC_MODE_THUMB)
    image_page_base = LOAD_BASE & ~0xFFF
    image_map_size = (LOAD_BASE - image_page_base + len(stock_image) + 0xFFF) & ~0xFFF
    engine.mem_map(image_page_base, image_map_size)
    engine.mem_write(LOAD_BASE, stock_image)
    engine.mem_map(CANDIDATE_CODE_BASE, (cursor - CANDIDATE_CODE_BASE + 0xFFF) & ~0xFFF)
    for name, body in candidate_bodies.items():
        engine.mem_write(candidate_entries[name], body)
    engine.mem_map(OBJECT_BASE, OBJECT_SIZE)
    engine.mem_map(STACK_BASE, STACK_SIZE)
    engine.mem_map(STOP_ADDRESS, 0x1000)

    call_log: list[tuple[str, int]] = []
    mock_default = {"value": 0}

    def on_get_default(uc, address, size, user_data):
        uc.reg_write(UC_ARM_REG_R0, mock_default["value"])
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def on_invalidate(uc, address, size, user_data):
        call_log.append(("invalidate", uc.reg_read(UC_ARM_REG_R0)))
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    engine.hook_add(UC_HOOK_CODE, on_get_default, begin=GET_DEFAULT_ENTRY, end=GET_DEFAULT_ENTRY)
    engine.hook_add(UC_HOOK_CODE, on_invalidate, begin=INVALIDATE_ENTRY, end=INVALIDATE_ENTRY)

    arg_regs = (UC_ARM_REG_R0, UC_ARM_REG_R1, UC_ARM_REG_R2, UC_ARM_REG_R3)

    def run(entry: int, args: list[int], object_state: bytes) -> tuple[int, bytes, list]:
        engine.mem_write(OBJECT_BASE, object_state.ljust(OBJECT_SIZE, b"\x00"))
        call_log.clear()
        for reg, value in zip(arg_regs, args):
            engine.reg_write(reg, value & 0xFFFFFFFF)
        engine.reg_write(UC_ARM_REG_LR, STOP_ADDRESS | 1)
        engine.reg_write(UC_ARM_REG_SP, STACK_BASE + STACK_SIZE - 32)
        engine.emu_start(entry | 1, STOP_ADDRESS, count=20_000)
        r0 = engine.reg_read(UC_ARM_REG_R0)
        mem = bytes(engine.mem_read(OBJECT_BASE, OBJECT_SIZE_BYTES))
        return r0, mem, list(call_log)

    rng = random.Random(seed)
    completed = {name: 0 for name in FUNCTIONS}

    def random_object(rotation: int | None = None) -> bytearray:
        state = bytearray(rng.randrange(0, 256) for _ in range(OBJECT_SIZE_BYTES))
        rot = rng.randrange(0, 8) if rotation is None else rotation
        state[0x2FC] = (state[0x2FC] & 0xF8) | rot
        return state

    for name, (entry, argc, has_fallback, _has_return) in FUNCTIONS.items():
        for iteration in range(iterations):
            rotation = iteration % 8 if iteration < 32 else None
            state = random_object(rotation)
            args = [OBJECT_BASE] + [rng.randrange(0, 0x1_0000_0000) for _ in range(argc - 1)]

            if has_fallback and iteration % 5 == 0:
                # Exercise the null-argument / default-resolution path too.
                args[0] = 0
                mock_default["value"] = (
                    OBJECT_BASE if iteration % 10 == 0 else 0
                )
            else:
                mock_default["value"] = 0

            stock_r0, stock_mem, stock_calls = run(entry, args, bytes(state))
            candidate_r0, candidate_mem, candidate_calls = run(
                candidate_entries[name], args, bytes(state)
            )
            stock_r0_cmp = stock_r0 if _has_return else None
            candidate_r0_cmp = candidate_r0 if _has_return else None
            if (stock_r0_cmp, stock_mem, stock_calls) != (
                candidate_r0_cmp, candidate_mem, candidate_calls
            ):
                raise QualificationError(
                    f"{name} diverged at iteration {iteration}: "
                    f"args={args} rotation={rotation} "
                    f"stock=({stock_r0:#x},calls={stock_calls}) "
                    f"candidate=({candidate_r0:#x},calls={candidate_calls})"
                )
            completed[name] += 1

    return completed


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--seed", type=lambda value: int(value, 0), default=0x4C56474C)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result = qualify(args.iterations, args.seed)
    print("G2 LVGL display-accessor emulation: PASS")
    for name, count in result.items():
        print(f"  {name}: {count} vectors")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except QualificationError as error:
        print(f"G2 LVGL display-accessor emulation: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
