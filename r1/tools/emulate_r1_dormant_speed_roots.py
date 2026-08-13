#!/usr/bin/env python3
"""Exercise dormant rational/root helpers in private production-Thumb emulation."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_R1,
    UC_ARM_REG_S0,
    UC_ARM_REG_S1,
    UC_ARM_REG_S2,
    UC_ARM_REG_S3,
    UC_ARM_REG_S17,
)

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


DIMENSIONLESS = 0x000568AC
QUADRATIC = 0x0006818C
CUBIC = 0x0006808C
ROOT_BUILDER = 0x00068D18
ALTERNATE_ROOT_SOLVER = 0x00069DC8
FINALIZER = 0x0008141C
ROOT_SELECTOR = 0x00068420
ROOT_WRITER = 0x000908AC
STATE = RAM_BASE + 0x7E00


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


def dimensionless_case(image: bytes, value: float, state_first: float) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(STATE, struct.pack("<f", state_first) + bytes(40))
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(value))
    fixture.call(DIMENSIONLESS, STATE)
    return {
        "input": float_record(float_bits(value)),
        "state_first": float_record(float_bits(state_first)),
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
    }


def quadratic_case(
    image: bytes,
    a: float,
    b: float,
    c: float,
    initial_roots: tuple[float, float, float] = (0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<3f", state, 0x18, *initial_roots)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(a))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(b))
    fixture.uc.reg_write(UC_ARM_REG_S2, float_bits(c))
    fixture.call(QUADRATIC, STATE)
    roots = struct.unpack("<3I", fixture.uc.mem_read(STATE + 0x18, 12))
    return {
        "coefficients": [float_record(float_bits(value)) for value in (a, b, c)],
        "initial_roots": [float_record(float_bits(value)) for value in initial_roots],
        "final_roots": [float_record(bits) for bits in roots],
    }


def selector_case(
    image: bytes,
    target: float,
    roots: tuple[float, float, float],
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<3f", state, 0x18, *roots)
    fixture.uc.mem_write(STATE, bytes(state))
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(target))
    fixture.call(ROOT_SELECTOR, STATE)
    return {
        "target": float_record(float_bits(target)),
        "roots": [float_record(float_bits(value)) for value in roots],
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
    }


def cubic_case(
    image: bytes,
    a: float,
    b: float,
    c: float,
    d: float,
    initial_roots: tuple[float, float, float] = (0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<3f", state, 0x18, *initial_roots)
    fixture.uc.mem_write(STATE, bytes(state))
    candidate_bytes: list[bytes] = []

    def capture_candidates(uc, address, size, user_data) -> None:
        del address, size, user_data
        pointer = uc.reg_read(UC_ARM_REG_R1)
        candidate_bytes.append(bytes(uc.mem_read(pointer, 24)))

    fixture.uc.hook_add(
        UC_HOOK_CODE,
        capture_candidates,
        begin=ROOT_WRITER,
        end=ROOT_WRITER,
    )
    for register, value in zip(
        (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2, UC_ARM_REG_S3),
        (a, b, c, d),
    ):
        fixture.uc.reg_write(register, float_bits(value))
    fixture.call(CUBIC, STATE)
    roots = struct.unpack("<3I", fixture.uc.mem_read(STATE + 0x18, 12))
    candidates = struct.unpack("<6I", candidate_bytes[-1])
    return {
        "coefficients": [float_record(float_bits(value)) for value in (a, b, c, d)],
        "initial_roots": [float_record(float_bits(value)) for value in initial_roots],
        "final_roots": [float_record(bits) for bits in roots],
        "candidates": [
            {
                "real": float_record(candidates[index * 2]),
                "imaginary": float_record(candidates[index * 2 + 1]),
            }
            for index in range(3)
        ],
    }


def builder_case(
    image: bytes,
    *,
    primary: float,
    auxiliary: float,
    state_first: float,
    state_second: float,
    mode: int,
    initial_roots: tuple[float, float, float] = (0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<2f", state, 0, state_first, state_second)
    struct.pack_into("<3f", state, 0x18, *initial_roots)
    fixture.uc.mem_write(STATE, bytes(state))
    coefficient_bits: list[int] = []

    def capture_coefficients(uc, address, size, user_data) -> None:
        del size, user_data
        registers = (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2)
        coefficient_bits.extend(uc.reg_read(register) for register in registers)
        if address == CUBIC:
            coefficient_bits.append(uc.reg_read(UC_ARM_REG_S3))

    fixture.uc.hook_add(
        UC_HOOK_CODE,
        capture_coefficients,
        begin=CUBIC if mode else QUADRATIC,
        end=CUBIC if mode else QUADRATIC,
    )
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(primary))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(auxiliary))
    fixture.call(ROOT_BUILDER, STATE, mode)
    final_roots = struct.unpack("<3I", fixture.uc.mem_read(STATE + 0x18, 12))
    return {
        "primary": float_record(float_bits(primary)),
        "auxiliary": float_record(float_bits(auxiliary)),
        "state_first": float_record(float_bits(state_first)),
        "state_second": float_record(float_bits(state_second)),
        "mode": mode,
        "coefficients": [float_record(bits) for bits in coefficient_bits],
        "initial_roots": [float_record(float_bits(value)) for value in initial_roots],
        "final_roots": [float_record(bits) for bits in final_roots],
    }


def alternate_solver_case(
    image: bytes,
    *,
    primary: float,
    auxiliary: float,
    state_first: float,
    state_second: float,
    mode: int,
    initial_roots: tuple[float, float, float] = (0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<2f", state, 0, state_first, state_second)
    struct.pack_into("<3f", state, 0x18, *initial_roots)
    fixture.uc.mem_write(STATE, bytes(state))
    coefficient_bits: list[int] = []
    target_bits: list[int] = []
    selected_root_bits: list[int] = []

    def capture_coefficients(uc, address, size, user_data) -> None:
        del size, user_data
        coefficient_bits.extend(
            uc.reg_read(register)
            for register in (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2)
        )
        if address == CUBIC:
            coefficient_bits.append(uc.reg_read(UC_ARM_REG_S3))

    def capture_selected_root(uc, address, size, user_data) -> None:
        del address, size, user_data
        selected_root_bits.append(uc.reg_read(UC_ARM_REG_S0))

    def capture_target(uc, address, size, user_data) -> None:
        del address, size, user_data
        target_bits.append(uc.reg_read(UC_ARM_REG_S0))

    solver = CUBIC if mode else QUADRATIC
    fixture.uc.hook_add(UC_HOOK_CODE, capture_coefficients, begin=solver, end=solver)
    fixture.uc.hook_add(
        UC_HOOK_CODE,
        capture_target,
        begin=0x00069E52,
        end=0x00069E52,
    )
    fixture.uc.hook_add(
        UC_HOOK_CODE,
        capture_selected_root,
        begin=0x00069E56,
        end=0x00069E56,
    )
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(primary))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(auxiliary))
    fixture.call(ALTERNATE_ROOT_SOLVER, STATE, mode)
    final_roots = struct.unpack("<3I", fixture.uc.mem_read(STATE + 0x18, 12))
    output_bits = fixture.uc.reg_read(UC_ARM_REG_S0)
    return {
        "primary": float_record(float_bits(primary)),
        "auxiliary": float_record(float_bits(auxiliary)),
        "state_first": float_record(float_bits(state_first)),
        "state_second": float_record(float_bits(state_second)),
        "mode": mode,
        "coefficients": [float_record(bits) for bits in coefficient_bits],
        "initial_roots": [float_record(float_bits(value)) for value in initial_roots],
        "final_roots": [float_record(bits) for bits in final_roots],
        "dimensionless_target": float_record(target_bits[-1]),
        "selected_root_before_attenuation": float_record(selected_root_bits[-1]),
        "output": float_record(output_bits),
    }


def finalizer_case(
    image: bytes,
    *,
    input_value: float,
    auxiliary: float,
    state_first: float,
    state_second: float,
    flags: int,
    mode: int,
    initial_roots: tuple[float, float, float] = (0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<2f", state, 0, state_first, state_second)
    struct.pack_into("<3f", state, 0x18, *initial_roots)
    struct.pack_into("<H", state, 0x24, flags)
    fixture.uc.mem_write(STATE, bytes(state))
    routes: list[str] = []
    normalized_bits: list[int] = []
    baseline_bits: list[int] = []
    dimensionless_bits: list[int] = []

    def capture_normalized(uc, address, size, user_data) -> None:
        del address, size, user_data
        normalized_bits.append(uc.reg_read(UC_ARM_REG_S17))

    def capture_route(uc, address, size, user_data) -> None:
        del size, user_data
        route = {
            0x00090C54: "baseline",
            ROOT_BUILDER: "root_builder",
            ALTERNATE_ROOT_SOLVER: "alternate_root_solver",
            ROOT_SELECTOR: "root_selector",
        }.get(address)
        if route is not None:
            routes.append(route)

    def capture_baseline(uc, address, size, user_data) -> None:
        del address, size, user_data
        baseline_bits.append(uc.reg_read(UC_ARM_REG_S0))

    def capture_dimensionless(uc, address, size, user_data) -> None:
        del address, size, user_data
        dimensionless_bits.append(uc.reg_read(UC_ARM_REG_S0))

    fixture.uc.hook_add(
        UC_HOOK_CODE, capture_normalized, begin=0x0008143A, end=0x0008143A
    )
    for entry in (0x00090C54, ROOT_BUILDER, ALTERNATE_ROOT_SOLVER, ROOT_SELECTOR):
        fixture.uc.hook_add(UC_HOOK_CODE, capture_route, begin=entry, end=entry)
    fixture.uc.hook_add(
        UC_HOOK_CODE, capture_baseline, begin=0x0008149E, end=0x0008149E
    )
    fixture.uc.hook_add(
        UC_HOOK_CODE, capture_dimensionless, begin=0x0008144C, end=0x0008144C
    )
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(input_value))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(auxiliary))
    fixture.call(FINALIZER, STATE, mode)
    final_roots = struct.unpack("<3I", fixture.uc.mem_read(STATE + 0x18, 12))
    return {
        "input": float_record(float_bits(input_value)),
        "auxiliary": float_record(float_bits(auxiliary)),
        "state_first": float_record(float_bits(state_first)),
        "state_second": float_record(float_bits(state_second)),
        "flags": f"0x{flags:04x}",
        "mode": mode,
        "normalized_input": float_record(normalized_bits[-1]),
        "routes": routes,
        "baseline": float_record(baseline_bits[-1]) if baseline_bits else None,
        "dimensionless_target": (
            float_record(dimensionless_bits[-1]) if dimensionless_bits else None
        ),
        "initial_roots": [float_record(float_bits(value)) for value in initial_roots],
        "final_roots": [float_record(bits) for bits in final_roots],
        "output": float_record(fixture.uc.reg_read(UC_ARM_REG_S0)),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    dimensionless = {
        "zero_input": dimensionless_case(image, 0, 1.2),
        "zero_state": dimensionless_case(image, 165, 0),
        "ordinary": dimensionless_case(image, 165, 1.2),
        "negative_input": dimensionless_case(image, -4, 1.2),
    }
    quadratic = {
        "two_positive": quadratic_case(image, 1, -3, 2),
        "two_negative": quadratic_case(image, 1, 3, 2),
        "negative_discriminant_clears": quadratic_case(
            image, 1, 0, 1, (7, 8, 9)
        ),
        "zero_a_clears": quadratic_case(image, 0, 1, 1, (7, 8, 9)),
        "one_positive_retains_other": quadratic_case(
            image, 1, 0, -4, (7, 8, 9)
        ),
    }
    cubic = {
        "roots_one_two_three": cubic_case(image, 1, -6, 11, -6),
        "roots_negative_zero_positive": cubic_case(image, 1, 0, -1, 0),
        "one_positive_root": cubic_case(image, 1, 0, 0, -1),
        "one_negative_root": cubic_case(image, 1, 0, 0, 1),
        "triple_root_two": cubic_case(image, 1, -6, 12, -8),
        "roots_one_two_four": cubic_case(image, 1, -7, 14, -8),
        "roots_half_three_five": cubic_case(image, 1, -8.5, 19, -7.5),
        "one_real_two_complex": cubic_case(image, 1, 2, 3, 4),
        "scaled_roots_one_two_three": cubic_case(image, 2, -12, 22, -12),
    }
    selectors = {
        "all_zero": selector_case(image, 4, (0, 0, 0)),
        "closest": selector_case(image, 4, (7, 3, 9)),
        "later_tie_wins": selector_case(image, 4, (5, 3, 9)),
        "zero_can_remain_closest": selector_case(image, 1, (0, 10, 20)),
        "negative_is_considered": selector_case(image, -3, (5, -2, 9)),
    }
    builders = {
        "mode_zero_primary_100": builder_case(
            image, primary=100, auxiliary=165, state_first=1.2, state_second=70, mode=0
        ),
        "mode_one_primary_100": builder_case(
            image, primary=100, auxiliary=165, state_first=1.2, state_second=70, mode=1
        ),
        "mode_zero_primary_zero": builder_case(
            image, primary=0, auxiliary=165, state_first=1.2, state_second=70, mode=0
        ),
        "mode_one_primary_zero": builder_case(
            image, primary=0, auxiliary=165, state_first=1.2, state_second=70, mode=1
        ),
        "zero_state": builder_case(
            image,
            primary=100,
            auxiliary=165,
            state_first=0,
            state_second=0,
            mode=0,
            initial_roots=(7, 8, 9),
        ),
        "small_auxiliary_mode_one": builder_case(
            image, primary=10, auxiliary=2, state_first=1.2, state_second=70, mode=1
        ),
    }
    next_after_one_point_two_five = struct.unpack(
        "<f", struct.pack("<I", 0x3FA00001)
    )[0]
    alternate_solvers = {
        "mode_zero_ordinary": alternate_solver_case(
            image, primary=100, auxiliary=165,
            state_first=1.2, state_second=70, mode=0
        ),
        "mode_one_ordinary": alternate_solver_case(
            image, primary=100, auxiliary=165,
            state_first=1.2, state_second=70, mode=1
        ),
        "mode_zero_small_auxiliary": alternate_solver_case(
            image, primary=10, auxiliary=2,
            state_first=1.2, state_second=70, mode=0
        ),
        "mode_one_small_auxiliary": alternate_solver_case(
            image, primary=10, auxiliary=2,
            state_first=1.2, state_second=70, mode=1
        ),
        "mode_two_small_auxiliary": alternate_solver_case(
            image, primary=10, auxiliary=2,
            state_first=1.2, state_second=70, mode=2
        ),
        "exact_threshold_retained": alternate_solver_case(
            image, primary=0, auxiliary=2,
            state_first=1.2, state_second=0, mode=0,
            initial_roots=(7, 8, 1.25),
        ),
        "next_float_threshold_attenuated": alternate_solver_case(
            image, primary=0, auxiliary=2,
            state_first=1.2, state_second=0, mode=0,
            initial_roots=(7, 8, next_after_one_point_two_five),
        ),
        "negative_retained_root_clamped": alternate_solver_case(
            image, primary=0, auxiliary=165,
            state_first=1.2, state_second=0, mode=0,
            initial_roots=(7, 8, -1),
        ),
    }
    state_below_dimensionless_threshold = struct.unpack(
        "<f", struct.pack("<I", 0x3F8BE1AC)
    )[0]
    state_above_dimensionless_threshold = struct.unpack(
        "<f", struct.pack("<I", 0x3F8BE1AD)
    )[0]
    finalizers = {
        "unflagged_zero_ratio": finalizer_case(
            image, input_value=0, auxiliary=165,
            state_first=0, state_second=0, flags=0, mode=0
        ),
        "unflagged_small_ratio": finalizer_case(
            image, input_value=0.01, auxiliary=165,
            state_first=0, state_second=0, flags=0, mode=0
        ),
        "unflagged_baseline_zero": finalizer_case(
            image, input_value=-1, auxiliary=165,
            state_first=0, state_second=-2, flags=0, mode=0
        ),
        "unflagged_mode_zero": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0, mode=0
        ),
        "unflagged_mode_one": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0, mode=1
        ),
        "unflagged_mode_zero_stale_roots": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0, mode=0,
            initial_roots=(0, 8, 9),
        ),
        "unflagged_mode_one_stale_roots": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0, mode=1,
            initial_roots=(0, 8, 9),
        ),
        "unflagged_infinity_mode_zero_sole_root_two": finalizer_case(
            image, input_value=float("inf"), auxiliary=165,
            state_first=0, state_second=0, flags=0, mode=0,
            initial_roots=(7, 8, 9),
        ),
        "unflagged_nan_mode_zero_sole_root_two": finalizer_case(
            image, input_value=float("nan"), auxiliary=165,
            state_first=0, state_second=0, flags=0, mode=0,
            initial_roots=(7, 8, 9),
        ),
        "unflagged_nan_mode_one_sole_root_two": finalizer_case(
            image, input_value=float("nan"), auxiliary=165,
            state_first=0, state_second=0, flags=0, mode=1,
            initial_roots=(7, 8, 9),
        ),
        "flagged_low_mode_zero": finalizer_case(
            image, input_value=10, auxiliary=165,
            state_first=1.2, state_second=70, flags=0x0440, mode=0
        ),
        "flagged_high_mode_zero": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0x0400, mode=0
        ),
        "flagged_high_mode_one": finalizer_case(
            image, input_value=10, auxiliary=2,
            state_first=1.2, state_second=70, flags=0x0040, mode=1
        ),
        "flagged_positive_nan_target_returns_negative": finalizer_case(
            image, input_value=0, auxiliary=float("nan"),
            state_first=1.2, state_second=70, flags=0x0040, mode=0,
            initial_roots=(-2, 0, 0),
        ),
        "flagged_target_just_below_threshold": finalizer_case(
            image, input_value=0, auxiliary=2,
            state_first=state_below_dimensionless_threshold,
            state_second=0, flags=0x0040, mode=0,
            initial_roots=(7, 8, 2),
        ),
        "flagged_target_just_above_threshold": finalizer_case(
            image, input_value=0, auxiliary=2,
            state_first=state_above_dimensionless_threshold,
            state_second=0, flags=0x0040, mode=0,
            initial_roots=(7, 8, 2),
        ),
    }

    assert {
        name: fixture["output"]["bits"] for name, fixture in dimensionless.items()
    } == {
        "zero_input": "0x00000000",
        "zero_state": "0x00000000",
        "ordinary": "0xbf737907",
        "negative_input": "0xbf050433",
    }

    assert {
        name: (
            fixture["normalized_input"]["bits"],
            fixture["routes"],
            fixture["baseline"]["bits"] if fixture["baseline"] else None,
            fixture["dimensionless_target"]["bits"]
            if fixture["dimensionless_target"] else None,
            [root["bits"] for root in fixture["final_roots"]],
            fixture["output"]["bits"],
        )
        for name, fixture in finalizers.items()
    } == {
        "unflagged_zero_ratio": (
            "0x00000000", ["baseline"], "0x3da75463", None,
            ["0x00000000", "0x00000000", "0x00000000"], "0x00000000",
        ),
        "unflagged_small_ratio": (
            "0x3c93deba", ["baseline"], "0x3da75463", None,
            ["0x00000000", "0x00000000", "0x00000000"], "0x3e623a7d",
        ),
        "unflagged_baseline_zero": (
            "0xbfe70c03", ["baseline"], "0x00000000", None,
            ["0x00000000", "0x00000000", "0x00000000"], "0x00000000",
        ),
        "unflagged_mode_zero": (
            "0x41906782", ["baseline", "root_builder"], "0x409d9da3", None,
            ["0x41206502", "0x00000000", "0x00000000"], "0x41206502",
        ),
        "unflagged_mode_one": (
            "0x41906782", ["baseline", "root_builder"], "0x409d9da3", None,
            ["0x407205a8", "0x00000000", "0x00000000"], "0x407205a8",
        ),
        "unflagged_mode_zero_stale_roots": (
            "0x41906782", ["baseline", "root_builder"], "0x409d9da3", None,
            ["0x41206502", "0x41000000", "0x41100000"], "0x41103281",
        ),
        "unflagged_mode_one_stale_roots": (
            "0x41906782", ["baseline", "root_builder"], "0x409d9da3", None,
            ["0x407205a8", "0x41000000", "0x41100000"], "0x40ddab9c",
        ),
        "unflagged_infinity_mode_zero_sole_root_two": (
            "0x7f800000", ["baseline", "root_builder"], "0x3da75463", None,
            ["0x00000000", "0x00000000", "0x41100000"], "0x00000000",
        ),
        "unflagged_nan_mode_zero_sole_root_two": (
            "0x7fc00000", ["baseline"], "0x3da75463", None,
            ["0x40e00000", "0x41000000", "0x41100000"], "0x00000000",
        ),
        "unflagged_nan_mode_one_sole_root_two": (
            "0x7fc00000", ["baseline"], "0x3da75463", None,
            ["0x40e00000", "0x41000000", "0x41100000"], "0x00000000",
        ),
        "flagged_low_mode_zero": (
            "0x41906782", ["alternate_root_solver", "root_selector"], None,
            "0xbf737907", ["0x00000000", "0x00000000", "0x00000000"],
            "0x00000000",
        ),
        "flagged_high_mode_zero": (
            "0x41906782", ["root_builder", "root_selector"], None,
            "0x3fca46eb", ["0x41206502", "0x00000000", "0x00000000"],
            "0x41206502",
        ),
        "flagged_high_mode_one": (
            "0x41906782", ["root_builder", "root_selector"], None,
            "0x3fca46eb", ["0x407205a8", "0x00000000", "0x00000000"],
            "0x407205a8",
        ),
        "flagged_positive_nan_target_returns_negative": (
            "0x00000000", ["root_builder", "root_selector"], None,
            "0x7fc00000", ["0xc0000000", "0x00000000", "0x00000000"],
            "0xc0000000",
        ),
        "flagged_target_just_below_threshold": (
            "0x00000000", ["alternate_root_solver", "root_selector"], None,
            "0x3f9fffff", ["0x00000000", "0x00000000", "0x40000000"],
            "0x3fb33333",
        ),
        "flagged_target_just_above_threshold": (
            "0x00000000", ["root_builder", "root_selector"], None,
            "0x3fa00002", ["0x00000000", "0x00000000", "0x40000000"],
            "0x40000000",
        ),
    }
    assert {
        name: [root["bits"] for root in fixture["final_roots"]]
        for name, fixture in quadratic.items()
    } == {
        "two_positive": ["0x40000000", "0x3f800000", "0x00000000"],
        "two_negative": ["0x00000000", "0x00000000", "0x00000000"],
        "negative_discriminant_clears": ["0x00000000", "0x00000000", "0x41100000"],
        "zero_a_clears": ["0x00000000", "0x00000000", "0x41100000"],
        "one_positive_retains_other": ["0x40000000", "0x41000000", "0x41100000"],
    }
    assert {
        name: [root["bits"] for root in fixture["final_roots"]]
        for name, fixture in cubic.items()
    } == {
        "roots_one_two_three": ["0x40400000", "0x3f800000", "0x40000000"],
        "roots_negative_zero_positive": ["0x3f7ffffe", "0x00000000", "0x33000000"],
        "one_positive_root": ["0x3f800000", "0x00000000", "0x00000000"],
        "one_negative_root": ["0x00000000", "0x00000000", "0x3f00000f"],
        "triple_root_two": ["0x40000000", "0x3ffffff9", "0x40000004"],
        "roots_one_two_four": ["0x407ffffc", "0x3f7fffe5", "0x40000009"],
        "roots_half_three_five": ["0x409fffff", "0x3efffff8", "0x40400001"],
        "one_real_two_complex": ["0x00000000", "0x00000000", "0x00000000"],
        "scaled_roots_one_two_three": ["0x40400000", "0x3f800000", "0x40000000"],
    }
    assert cubic["one_negative_root"]["candidates"][2]["imaginary"][
        "bits"
    ] == "0xbf5db3df"
    assert cubic["one_negative_root"]["final_roots"][2]["bits"] == "0x3f00000f"
    assert {
        name: fixture["output"]["bits"] for name, fixture in selectors.items()
    } == {
        "all_zero": "0x00000000",
        "closest": "0x40400000",
        "later_tie_wins": "0x40400000",
        "zero_can_remain_closest": "0x00000000",
        "negative_is_considered": "0xc0000000",
    }
    assert {
        name: (
            [coefficient["bits"] for coefficient in fixture["coefficients"]],
            [root["bits"] for root in fixture["final_roots"]],
        )
        for name, fixture in builders.items()
    } == {
        "mode_zero_primary_100": (
            ["0x40e8d917", "0x409b7c1c", "0x4299dd40"],
            ["0x00000000", "0x00000000", "0x00000000"],
        ),
        "mode_one_primary_100": (
            ["0x3e1704ff", "0x40e8d917", "0x409b7c1c", "0x4299dd40"],
            ["0x00000000", "0x00000000", "0x00000000"],
        ),
        "mode_zero_primary_zero": (
            ["0x40e8d917", "0x409b7c1c", "0x4330eea0"],
            ["0x00000000", "0x00000000", "0x00000000"],
        ),
        "mode_one_primary_zero": (
            ["0x3e1704ff", "0x40e8d917", "0x409b7c1c", "0x4330eea0"],
            ["0x00000000", "0x00000000", "0x00000000"],
        ),
        "zero_state": (
            ["0x00000000", "0x00000000", "0xc2c80000"],
            ["0x00000000", "0x00000000", "0x41100000"],
        ),
        "small_auxiliary_mode_one": (
            ["0x3e1704ff", "0x3db4a234", "0x3d713cae", "0xbfb3a358"],
            ["0x3ff0b55a", "0x00000000", "0x00000000"],
        ),
    }

    assert {
        name: (
            [coefficient["bits"] for coefficient in fixture["coefficients"]],
            [root["bits"] for root in fixture["final_roots"]],
            fixture["dimensionless_target"]["bits"],
            fixture["selected_root_before_attenuation"]["bits"],
            fixture["output"]["bits"],
        )
        for name, fixture in alternate_solvers.items()
    } == {
        "mode_zero_ordinary": (
            ["0x40e8d917", "0x00000000", "0x40947cd0"],
            ["0x00000000", "0x00000000", "0x00000000"],
            "0xbf737907", "0x00000000", "0x00000000",
        ),
        "mode_one_ordinary": (
            ["0x3e1704ff", "0x40e8d917", "0x00000000", "0x40947cd0"],
            ["0x00000000", "0x00000000", "0x3bd3c000"],
            "0xbf737907", "0x00000000", "0x00000000",
        ),
        "mode_zero_small_auxiliary": (
            ["0x3db4a234", "0x00000000", "0xc10bb4c5"],
            ["0x411f324c", "0x00000000", "0x00000000"],
            "0x3fca46eb", "0x411f324c", "0x40dee004",
        ),
        "mode_one_small_auxiliary": (
            ["0x3e1704ff", "0x3db4a234", "0x00000000", "0xc10bb4c5"],
            ["0x406d7431", "0x00000000", "0x00000000"],
            "0x3fca46eb", "0x406d7431", "0x402637bc",
        ),
        "mode_two_small_auxiliary": (
            ["0x3e1704ff", "0x3db4a234", "0x00000000", "0xc10bb4c5"],
            ["0x406d7431", "0x00000000", "0x00000000"],
            "0x3fca46eb", "0x406d7431", "0x402637bc",
        ),
        "exact_threshold_retained": (
            ["0x00000000", "0x00000000", "0x00000000"],
            ["0x00000000", "0x00000000", "0x3fa00000"],
            "0x3fca46eb", "0x3fa00000", "0x3fa00000",
        ),
        "next_float_threshold_attenuated": (
            ["0x00000000", "0x00000000", "0x00000000"],
            ["0x00000000", "0x00000000", "0x3fa00001"],
            "0x3fca46eb", "0x3fa00001", "0x3f600001",
        ),
        "negative_retained_root_clamped": (
            ["0x00000000", "0x00000000", "0x00000000"],
            ["0x00000000", "0x00000000", "0xbf800000"],
            "0xbf737907", "0xbf800000", "0x00000000",
        ),
    }

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "functions": {
            "dimensionless": f"0x{DIMENSIONLESS:08x}",
            "quadratic": f"0x{QUADRATIC:08x}",
            "cubic": f"0x{CUBIC:08x}",
            "root_builder": f"0x{ROOT_BUILDER:08x}",
            "alternate_root_solver": f"0x{ALTERNATE_ROOT_SOLVER:08x}",
            "finalizer": f"0x{FINALIZER:08x}",
            "root_selector": f"0x{ROOT_SELECTOR:08x}",
        },
        "dimensionless": dimensionless,
        "quadratic": quadratic,
        "cubic": cubic,
        "selectors": selectors,
        "builders": builders,
        "alternate_solvers": alternate_solvers,
        "finalizers": finalizers,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "firmware_execution_outside_private_emulation": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True, allow_nan=True))


if __name__ == "__main__":
    main()
