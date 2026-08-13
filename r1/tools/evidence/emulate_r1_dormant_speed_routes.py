#!/usr/bin/env python3
"""Exercise the dormant per-iteration speed router, smoother, targets and shared state.

This production-Thumb harness uses only synthetic inputs and private RAM. It validates flag-route
priority, config mutation, the two eight-byte veneers, their target functions, official zero-state
effects, and caller-order sequential composition without enabling a device or touching live state.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2, UC_ARM_REG_SP

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


PER_ITERATION = 0x000721B4
MODE_ZERO_VENEER = 0x00029382
MODE_ONE_VENEER = 0x0002938A
MODE_ZERO_TARGET = 0x0006825C
MODE_ONE_TARGET = 0x00067488
CORE_STATE = RAM_BASE + 0x7400
INPUT = RAM_BASE + 0x7800
CONFIG = RAM_BASE + 0x7900
DYNAMICS_STATE = RAM_BASE + 0x7B00
OUTPUT = RAM_BASE + 0x7C00
REDUCER = 0x000888A0
FINALIZER = 0x0008141C


def float_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


def dynamics_record(state: bytes) -> dict[str, Any]:
    return {
        "float32_words": [float_record(bits) for bits in struct.unpack("<9I", state[:36])],
        "flag_word": f"0x{struct.unpack('<H', state[0x24:0x26])[0]:04x}",
        "initialized_raw": state[0x26],
        "opaque_tail": state[0x27:0x2C].hex(),
    }


def smoother_record(state: bytes) -> dict[str, Any]:
    return {
        "enabled_raw": state[0],
        "sample_count": state[1],
        "reserved_header": state[2:4].hex(),
        "float32_words": [float_record(bits) for bits in struct.unpack("<7I", state[4:32])],
    }


def direct_veneer_case(
    image: bytes,
    *,
    veneer: int,
    auxiliary_input: float,
    selected_speed: float,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(DYNAMICS_STATE, bytes(44))
    fixture.uc.mem_write(OUTPUT, b"\xa5" * 4)
    fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(auxiliary_input))
    fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(selected_speed))
    fixture.call(veneer, DYNAMICS_STATE, OUTPUT)
    state = bytes(fixture.uc.mem_read(DYNAMICS_STATE, 44))
    output_bits = struct.unpack("<I", fixture.uc.mem_read(OUTPUT, 4))[0]
    return {
        "veneer": f"0x{veneer:08x}",
        "auxiliary_input": float_record(float_bits(auxiliary_input)),
        "selected_speed": float_record(float_bits(selected_speed)),
        "output": float_record(output_bits),
        "state": dynamics_record(state),
    }


def direct_sequence_case(
    image: bytes,
    *,
    veneer: int,
    samples: list[tuple[float, float]],
    state_first: float,
    state_second: float,
    flag_word: int = 0,
    initial_words_2_through_8: tuple[float, float, float, float, float, float, float] = (
        0, 0, 0, 0, 0, 0, 0
    ),
    initialized_raw: int = 0,
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    state = bytearray(44)
    struct.pack_into("<2f", state, 0, state_first, state_second)
    struct.pack_into("<7f", state, 8, *initial_words_2_through_8)
    struct.pack_into("<H", state, 0x24, flag_word)
    state[0x26] = initialized_raw
    fixture.uc.mem_write(DYNAMICS_STATE, bytes(state))
    reducer_inputs: list[tuple[int, int, int]] = []
    finalizer_inputs: list[tuple[int, int]] = []

    def capture_reducer(uc, address, size, user_data) -> None:
        del address, size, user_data
        reducer_inputs.append(tuple(
            uc.reg_read(register)
            for register in (UC_ARM_REG_S0, UC_ARM_REG_S1, UC_ARM_REG_S2)
        ))

    def capture_finalizer(uc, address, size, user_data) -> None:
        del address, size, user_data
        finalizer_inputs.append((
            uc.reg_read(UC_ARM_REG_S0), uc.reg_read(UC_ARM_REG_S1)
        ))

    fixture.uc.hook_add(UC_HOOK_CODE, capture_reducer, begin=REDUCER, end=REDUCER)
    fixture.uc.hook_add(UC_HOOK_CODE, capture_finalizer, begin=FINALIZER, end=FINALIZER)
    records = []
    for first_input, selected_speed in samples:
        fixture.uc.mem_write(OUTPUT, b"\xa5" * 4)
        fixture.uc.reg_write(UC_ARM_REG_S0, float_bits(first_input))
        fixture.uc.reg_write(UC_ARM_REG_S1, float_bits(selected_speed))
        fixture.call(veneer, DYNAMICS_STATE, OUTPUT)
        state_after = bytes(fixture.uc.mem_read(DYNAMICS_STATE, 44))
        output_bits = struct.unpack("<I", fixture.uc.mem_read(OUTPUT, 4))[0]
        reducer = reducer_inputs[-1]
        finalizer = finalizer_inputs[-1]
        records.append({
            "first_input": float_record(float_bits(first_input)),
            "selected_speed": float_record(float_bits(selected_speed)),
            "reducer_inputs": [float_record(bits) for bits in reducer],
            "finalizer_inputs": [float_record(bits) for bits in finalizer],
            "output": float_record(output_bits),
            "state": dynamics_record(state_after),
        })
    return {
        "veneer": f"0x{veneer:08x}",
        "initial_state_first": float_record(float_bits(state_first)),
        "initial_state_second": float_record(float_bits(state_second)),
        "flag_word": f"0x{flag_word:04x}",
        "initial_initialized_raw": initialized_raw,
        "samples": records,
    }


def routed_case(image: bytes, *, flag_word: int) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    fixture.uc.mem_write(CORE_STATE, bytes(0x33C))
    fixture.uc.mem_write(CONFIG, bytes(32))
    fixture.uc.mem_write(CORE_STATE + 0x56, struct.pack("<H", flag_word))
    fixture.uc.mem_write(CONFIG + 8, struct.pack("<f", 7.0))
    fixture.uc.mem_write(CONFIG + 12, struct.pack("<f", 9.0))
    fixture.uc.mem_write(
        INPUT,
        struct.pack(
            "<IIiffffIf",
            1_000,
            0,
            72,
            10.0,
            0.0,
            0.0,
            0.0,
            CONFIG,
            0.0,
        ),
    )
    return_code = fixture.call(PER_ITERATION, CORE_STATE, INPUT)
    state = bytes(fixture.uc.mem_read(CORE_STATE, 0x33C))
    config = bytes(fixture.uc.mem_read(CONFIG, 16))
    return {
        "flag_word": f"0x{flag_word:04x}",
        "return_code": return_code,
        "final_config_8": float_record(struct.unpack("<I", config[8:12])[0]),
        "final_config_c": float_record(struct.unpack("<I", config[12:16])[0]),
        "pre_shared_filter_value": float_record(struct.unpack("<I", state[0x24:0x28])[0]),
        "previous_speed_value": float_record(struct.unpack("<I", state[0x28:0x2C])[0]),
        "smoother_produced_value": float_record(struct.unpack("<I", state[0x34:0x38])[0]),
        "smoother_enabled_raw": state[0x2DC],
        "dynamics": dynamics_record(state[0x2FC:0x328]),
    }


def routed_sequence_case(
    image: bytes,
    *,
    flag_word: int,
    samples: list[tuple[float, float, float]],
    smoother_enabled_raw: int,
    smoother_limits: tuple[float, float, float, float],
    state_first: float,
    state_second: float,
    dynamics_flag_word: int = 0,
) -> dict[str, Any]:
    """Run the exact `0x721b4` caller slice while retaining smoother/target state."""
    fixture = LocomotionFirmwareFixture(image)
    core = bytearray(0x33C)
    struct.pack_into("<H", core, 0x56, flag_word)
    core[0x2DC] = smoother_enabled_raw
    struct.pack_into("<4f", core, 0x2EC, *smoother_limits)
    struct.pack_into("<2f", core, 0x2FC, state_first, state_second)
    struct.pack_into("<H", core, 0x320, dynamics_flag_word)
    fixture.uc.mem_write(CORE_STATE, bytes(core))
    fixture.uc.mem_write(CONFIG, bytes(32))

    target_inputs: list[tuple[int, int]] = []
    target_outputs: list[int] = []

    def capture_target_inputs(uc, address, size, user_data) -> None:
        del address, size, user_data
        target_inputs.append((
            uc.reg_read(UC_ARM_REG_S0),
            uc.reg_read(UC_ARM_REG_S1),
        ))

    def capture_target_output(uc, address, size, user_data) -> None:
        del address, size, user_data
        stack_pointer = uc.reg_read(UC_ARM_REG_SP)
        target_outputs.append(struct.unpack("<I", uc.mem_read(stack_pointer + 0x10, 4))[0])

    fixture.uc.hook_add(
        UC_HOOK_CODE, capture_target_inputs,
        begin=MODE_ZERO_TARGET, end=MODE_ZERO_TARGET,
    )
    fixture.uc.hook_add(
        UC_HOOK_CODE, capture_target_inputs,
        begin=MODE_ONE_TARGET, end=MODE_ONE_TARGET,
    )
    # Instructions immediately after the two veneer calls, before the shared speed filters.
    fixture.uc.hook_add(UC_HOOK_CODE, capture_target_output, begin=0x72234, end=0x72234)
    fixture.uc.hook_add(UC_HOOK_CODE, capture_target_output, begin=0x72250, end=0x72250)

    records = []
    for index, (primary_config, alternate_config, selected_speed) in enumerate(samples):
        fixture.uc.mem_write(CONFIG + 8, struct.pack("<f", primary_config))
        fixture.uc.mem_write(CONFIG + 12, struct.pack("<f", alternate_config))
        fixture.uc.mem_write(
            INPUT,
            struct.pack(
                "<IIiffffIf",
                1_000,
                index,
                72,
                selected_speed,
                0.0,
                0.0,
                0.0,
                CONFIG,
                0.0,
            ),
        )
        target_count_before = len(target_inputs)
        return_code = fixture.call(PER_ITERATION, CORE_STATE, INPUT)
        assert len(target_inputs) == target_count_before + 1
        config = bytes(fixture.uc.mem_read(CONFIG, 16))
        state = bytes(fixture.uc.mem_read(CORE_STATE, 0x33C))
        first_input_bits, target_selected_bits = target_inputs[-1]
        records.append({
            "primary_config": float_record(float_bits(primary_config)),
            "alternate_config": float_record(float_bits(alternate_config)),
            "input_selected_speed": float_record(float_bits(selected_speed)),
            "return_code": return_code,
            "final_primary_config": float_record(struct.unpack("<I", config[8:12])[0]),
            "target_first_input": float_record(first_input_bits),
            "target_selected_speed": float_record(target_selected_bits),
            "target_output_before_shared_filters": float_record(target_outputs[-1]),
            "smoother": smoother_record(state[0x2DC:0x2FC]),
            "dynamics": dynamics_record(state[0x2FC:0x328]),
        })
    return {
        "route_flag_word": f"0x{flag_word:04x}",
        "dynamics_flag_word": f"0x{dynamics_flag_word:04x}",
        "initial_smoother_enabled_raw": smoother_enabled_raw,
        "smoother_limits": [float_record(float_bits(value)) for value in smoother_limits],
        "samples": records,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    direct = {
        "mode_zero_grade_9_speed_10": direct_veneer_case(
            image, veneer=MODE_ZERO_VENEER, auxiliary_input=9, selected_speed=10
        ),
        "mode_zero_grade_50_speed_4": direct_veneer_case(
            image, veneer=MODE_ZERO_VENEER, auxiliary_input=50, selected_speed=4
        ),
        "mode_one_aux_0_speed_10": direct_veneer_case(
            image, veneer=MODE_ONE_VENEER, auxiliary_input=0, selected_speed=10
        ),
        "mode_one_aux_7_speed_36": direct_veneer_case(
            image, veneer=MODE_ONE_VENEER, auxiliary_input=7, selected_speed=36
        ),
        "mode_one_negative_speed": direct_veneer_case(
            image, veneer=MODE_ONE_VENEER, auxiliary_input=7, selected_speed=-1
        ),
    }
    routed = {
        name: routed_case(image, flag_word=flag)
        for name, flag in {
            "no_route": 0,
            "mode_zero": 0x0008,
            "mode_one_without_config_zero": 0x0040,
            "mode_one_with_config_zero": 0x0004,
            "mode_one_priority_over_mode_zero": 0x000C,
        }.items()
    }
    sequences = {
        "mode_one_unflagged": direct_sequence_case(
            image,
            veneer=MODE_ONE_VENEER,
            samples=[(7, 36), (9, 36), (4, 18)],
            state_first=1.2,
            state_second=70,
        ),
        "mode_zero_unflagged": direct_sequence_case(
            image,
            veneer=MODE_ZERO_VENEER,
            samples=[(50, 4), (50, 8), (-50, 8), (0, 36)],
            state_first=1.2,
            state_second=70,
        ),
        "mode_one_flagged": direct_sequence_case(
            image,
            veneer=MODE_ONE_VENEER,
            samples=[(7, 36), (9, 36)],
            state_first=1.2,
            state_second=70,
            flag_word=0x0440,
        ),
        "mode_zero_flagged": direct_sequence_case(
            image,
            veneer=MODE_ZERO_VENEER,
            samples=[(50, 4), (-50, 8)],
            state_first=1.2,
            state_second=70,
            flag_word=0x0440,
        ),
        "mode_one_preserves_nonzero_initialized_raw": direct_sequence_case(
            image,
            veneer=MODE_ONE_VENEER,
            samples=[(9, 36)],
            state_first=1.2,
            state_second=70,
            initial_words_2_through_8=(5, 7, 11, 13, 17, 19, 23),
            initialized_raw=2,
        ),
    }
    routed_sequences = {
        "mode_one_enabled_smoother": routed_sequence_case(
            image,
            flag_word=0x0040,
            samples=[(10, 9, 36), (20, 9, 36), (40, 9, 18)],
            smoother_enabled_raw=1,
            smoother_limits=(5, 4, 3, 2),
            state_first=1.2,
            state_second=70,
        ),
        "mode_one_invalid_smoother_uses_caller_zero": routed_sequence_case(
            image,
            flag_word=0x0040,
            samples=[(10, 9, 10)],
            smoother_enabled_raw=1,
            smoother_limits=(0, 4, 3, 2),
            state_first=0,
            state_second=0,
        ),
        "mode_one_zeroed_config": routed_sequence_case(
            image,
            flag_word=0x0004,
            samples=[(10, 9, 10)],
            smoother_enabled_raw=1,
            smoother_limits=(5, 4, 3, 2),
            state_first=0,
            state_second=0,
        ),
        "mode_zero_bypasses_enabled_smoother": routed_sequence_case(
            image,
            flag_word=0x0008,
            samples=[(10, 50, 4)],
            smoother_enabled_raw=1,
            smoother_limits=(5, 4, 3, 2),
            state_first=1.2,
            state_second=70,
            dynamics_flag_word=0x0440,
        ),
    }

    assert direct["mode_zero_grade_9_speed_10"]["output"]["bits"] == "0x00000000"
    assert direct["mode_zero_grade_50_speed_4"]["output"]["bits"] == "0x4064f92e"
    assert direct["mode_one_aux_0_speed_10"]["output"]["bits"] == "0x411ffff7"
    assert direct["mode_one_aux_7_speed_36"]["output"]["bits"] == "0x42100001"
    assert direct["mode_one_negative_speed"]["output"]["bits"] == "0x00000000"
    assert all(item["state"]["initialized_raw"] == 1 for item in direct.values())

    assert routed["no_route"]["dynamics"]["initialized_raw"] == 0
    assert routed["no_route"]["pre_shared_filter_value"]["bits"] == "0x41200000"
    assert routed["mode_zero"]["dynamics"]["initialized_raw"] == 1
    assert routed["mode_zero"]["pre_shared_filter_value"]["bits"] == "0x00000000"
    for name in (
        "mode_one_without_config_zero",
        "mode_one_with_config_zero",
        "mode_one_priority_over_mode_zero",
    ):
        assert routed[name]["pre_shared_filter_value"]["bits"] == "0x411ffff7"
        assert routed[name]["smoother_enabled_raw"] == 0
        assert routed[name]["smoother_produced_value"]["bits"] == "0x00000000"
    assert routed["mode_one_without_config_zero"]["final_config_8"]["bits"] == "0x40e00000"
    assert routed["mode_one_with_config_zero"]["final_config_8"]["bits"] == "0x00000000"
    assert routed["mode_one_priority_over_mode_zero"]["final_config_8"]["bits"] == "0x00000000"

    assert {
        name: [(
            [value["bits"] for value in sample["reducer_inputs"]],
            [value["bits"] for value in sample["finalizer_inputs"]],
            sample["output"]["bits"],
            [value["bits"] for value in sample["state"]["float32_words"]],
            sample["state"]["initialized_raw"],
        ) for sample in sequence["samples"]]
        for name, sequence in sequences.items()
    } == {
        "mode_one_unflagged": [
            (["0x41200000", "0x00000000", "0x43250000"],
             ["0x441802e0", "0x43250000"], "0x420fc546",
             ["0x3f99999a", "0x428c0000", "0x41200000", "0x40e00000",
              "0x455ac000", "0x00000000", "0x411fbec0", "0x00000000",
              "0x00000000"], 1),
            (["0x41200000", "0x40000000", "0x43250000"],
             ["0x44ba5b54", "0x43250000"], "0x42652549",
             ["0x3f99999a", "0x428c0000", "0x41232b2b", "0x41100000",
              "0x45638000", "0x00000000", "0x417e9b35", "0x00000000",
              "0x00000000"], 1),
            (["0x40a00000", "0xc0a00000", "0x43250000"],
             ["0x00000000", "0x43250000"], "0x00000000",
             ["0x3f99999a", "0x428c0000", "0x40e24632", "0x40800000",
              "0x44dac004", "0x00000000", "0x00000000", "0x00000000",
              "0x00000000"], 1),
        ],
        "mode_zero_unflagged": [
            (["0x3f7e6a34", "0x3efe6a34", "0x43250000"],
             ["0x43768cf5", "0x43250000"], "0x41a57734",
             ["0x3f99999a", "0x428c0000", "0x3f7e6a34", "0x00000000",
              "0x420a4589", "0x00000000", "0x40b7d9c8", "0x00000000",
              "0x00000000"], 1),
            (["0x3ffe6a34", "0x3f7e6a34", "0x43250000"],
             ["0x441244e8", "0x43250000"], "0x42198c7c",
             ["0x3f99999a", "0x428c0000", "0x400e38e4", "0x00000000",
              "0x432cd6eb", "0x00000000", "0x412a9c18", "0x00000000",
              "0x00000000"], 1),
            (["0x3ffe6a34", "0xbf7e6a34", "0x43250000"],
             ["0x00000000", "0x43250000"], "0x00000000",
             ["0x3f99999a", "0x428c0000", "0x400e38e4", "0x00000000",
              "0x432cd6eb", "0x00000000", "0x00000000", "0x00000000",
              "0x00000000"], 1),
            (["0x41200000", "0x00000000", "0x43250000"],
             ["0x452d2f7f", "0x43250000"], "0x42b70331",
             ["0x3f99999a", "0x428c0000", "0x41200000", "0x00000000",
              "0x455ac000", "0x00000000", "0x41cb58e2", "0x00000000",
              "0x00000000"], 1),
        ],
        "mode_one_flagged": [
            (["0x41200000", "0x00000000", "0x403a2ef5"],
             ["0x42c04ecd", "0x403a2ef5"], "0x421022e8",
             ["0x3f99999a", "0x428c0000", "0x41200000", "0x40e00000",
              "0x455ac000", "0x00000000", "0x412026c9", "0x00000000",
              "0x00000000"], 1),
            (["0x41200000", "0x40000000", "0x403a2ef5"],
             ["0x446add94", "0x403a2ef5"], "0x42a005f7",
             ["0x3f99999a", "0x428c0000", "0x41232b2b", "0x41100000",
              "0x45638000", "0x00000000", "0x41b1cdbd", "0x00000000",
              "0x00000000"], 1),
        ],
        "mode_zero_flagged": [
            (["0x3f7e6a34", "0x3efe6a34", "0x3fdd5076"],
             ["0x433f6492", "0x3fdd5076"], "0x43295afd",
             ["0x3f99999a", "0x428c0000", "0x3f7e6a34", "0x00000000",
              "0x420a4589", "0x00000000", "0x428668b9", "0x00000000",
              "0x00000000"], 1),
            (["0x3ffe6a34", "0xbf7e6a34", "0x400f5f36"],
             ["0x00000000", "0x400f5f36"], "0x00000000",
             ["0x3f99999a", "0x428c0000", "0x400e38e4", "0x00000000",
              "0x432cd6eb", "0x00000000", "0x00000000", "0x00000000",
              "0x00000000"], 1),
        ],
        "mode_one_preserves_nonzero_initialized_raw": [
            (["0x41200000", "0x40000000", "0x43250000"],
             ["0x456e9939", "0x43250000"], "0x42b11193",
             ["0x3f99999a", "0x428c0000", "0x41232b2b", "0x41100000",
              "0x45638000", "0x41500000", "0x41c4be32", "0x00000000",
              "0x00000000"], 2),
        ],
    }

    routed_sequence_summary = {
        name: [(
            sample["final_primary_config"]["bits"],
            sample["target_first_input"]["bits"],
            sample["target_selected_speed"]["bits"],
            sample["target_output_before_shared_filters"]["bits"],
            sample["smoother"]["sample_count"],
            [value["bits"] for value in sample["smoother"]["float32_words"]],
            [value["bits"] for value in sample["dynamics"]["float32_words"]],
        ) for sample in sequence["samples"]]
        for name, sequence in routed_sequences.items()
    }
    assert routed_sequence_summary == {
        "mode_one_enabled_smoother": [
            ("0x41200000", "0x41200000", "0x42100000", "0x420fc546", 1,
             ["0x41200000", "0x41200000", "0x41200000", "0x40a00000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x3f99999a", "0x428c0000", "0x41200000", "0x41200000",
              "0x455ac000", "0x00000000", "0x411fbec0", "0x00000000",
              "0x00000000"]),
            ("0x41a00000", "0x41500000", "0x42100000", "0x4284a22d", 2,
             ["0x41f00000", "0x41500000", "0x41a00000", "0x40a00000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x3f99999a", "0x428c0000", "0x41270b7e", "0x41500000",
              "0x456e6ffe", "0x00000000", "0x41935edd", "0x00000000",
              "0x00000000"]),
            ("0x42200000", "0x41800000", "0x41900000", "0x42734de9", 3,
             ["0x425c0000", "0x41800000", "0x42200000", "0x40a00000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x3f99999a", "0x428c0000", "0x40ba9729", "0x41800000",
              "0x4494c001", "0x00000000", "0x41872b49", "0x00000000",
              "0x00000000"]),
        ],
        "mode_one_invalid_smoother_uses_caller_zero": [
            ("0x41200000", "0x00000000", "0x41200000", "0x411ffff7", 0,
             ["0x00000000", "0x00000000", "0x00000000", "0x00000000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x00000000", "0x00000000", "0x4031c71d", "0x00000000",
              "0x00000000", "0x00000000", "0x4031c713", "0x00000000",
              "0x00000000"]),
        ],
        "mode_one_zeroed_config": [
            ("0x00000000", "0x00000000", "0x41200000", "0x411ffff7", 1,
             ["0x00000000", "0x00000000", "0x00000000", "0x40a00000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x00000000", "0x00000000", "0x4031c71d", "0x00000000",
              "0x00000000", "0x00000000", "0x4031c713", "0x00000000",
              "0x00000000"]),
        ],
        "mode_zero_bypasses_enabled_smoother": [
            ("0x41200000", "0x42480000", "0x40800000", "0x43295afd", 0,
             ["0x00000000", "0x00000000", "0x00000000", "0x40a00000",
              "0x40800000", "0x40400000", "0x40000000"],
             ["0x3f99999a", "0x428c0000", "0x3f7e6a34", "0x00000000",
              "0x420a4589", "0x00000000", "0x428668b9", "0x00000000",
              "0x00000000"]),
        ],
    }

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "functions": {
            "per_iteration": f"0x{PER_ITERATION:08x}",
            "mode_zero_veneer": f"0x{MODE_ZERO_VENEER:08x}",
            "mode_zero_target": f"0x{MODE_ZERO_TARGET:08x}",
            "mode_one_veneer": f"0x{MODE_ONE_VENEER:08x}",
            "mode_one_target": f"0x{MODE_ONE_TARGET:08x}",
        },
        "direct_zero_state": direct,
        "per_iteration_routes": routed,
        "direct_sequences": sequences,
        "routed_sequences": routed_sequences,
        "routed_sequence_summary": routed_sequence_summary,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "firmware_execution_outside_private_emulation": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
