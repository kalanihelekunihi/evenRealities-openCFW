#!/usr/bin/env python3
"""Exercise complete active-only per-iteration coordinator `0x721b4` in private RAM.

The parent mode is not enabled and no device is accessed. Synthetic state/input records validate
the production order of routing, speed filtering, HR validation/carry, HR wrapper selection,
optional ratio accumulation, final history copies, and the early-error boundary.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_dormant_speed_routes import (
    CONFIG,
    CORE_STATE,
    DYNAMICS_STATE,
    INPUT,
    PER_ITERATION,
    dynamics_record,
    float_bits,
    float_record,
    smoother_record,
)
from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture


def signed32(value: int) -> int:
    return struct.unpack("<i", struct.pack("<I", value & 0xFFFFFFFF))[0]


def signed16(value: int) -> int:
    return struct.unpack("<h", struct.pack("<H", value & 0xFFFF))[0]


def heart_filter_record(state: bytes) -> dict[str, Any]:
    return {
        "header": list(state[:8]),
        "missing_count": struct.unpack_from("<I", state, 8)[0],
        "last_effective_input": struct.unpack_from("<i", state, 12)[0],
        "average": float_record(struct.unpack_from("<I", state, 16)[0]),
        "history": [float_record(bits) for bits in struct.unpack_from("<20I", state, 20)],
    }


def modeled_state_record(state: bytes) -> dict[str, Any]:
    return {
        "selected_heart_rate": struct.unpack_from("<i", state, 0x1C)[0],
        "previous_heart_rate": struct.unpack_from("<i", state, 0x20)[0],
        "selected_speed": float_record(struct.unpack_from("<I", state, 0x24)[0]),
        "previous_speed": float_record(struct.unpack_from("<I", state, 0x28)[0]),
        "current_auxiliary": float_record(struct.unpack_from("<I", state, 0x2C)[0]),
        "previous_auxiliary": float_record(struct.unpack_from("<I", state, 0x30)[0]),
        "smoother_produced": float_record(struct.unpack_from("<I", state, 0x34)[0]),
        "copied_auxiliary_1": float_record(struct.unpack_from("<I", state, 0x38)[0]),
        "copied_auxiliary_2": float_record(struct.unpack_from("<I", state, 0x3C)[0]),
        "raw_status": signed16(struct.unpack_from("<H", state, 0x52)[0]),
        "route_flag_word": f"0x{struct.unpack_from('<H', state, 0x56)[0]:04x}",
        "validation_latch_raw": state[0x60],
        "speed_filter_history": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x184)
        ],
        "ratio_primary_sums": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x1C0)
        ],
        "ratio_primary_counts": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x1D8)
        ],
        "ratio_moments": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x210)
        ],
        "ratio_secondary_sums": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x228)
        ],
        "ratio_secondary_counts": [
            float_record(bits) for bits in struct.unpack_from("<6I", state, 0x240)
        ],
        "heart_rate_filter": heart_filter_record(state[0x278:0x2DC]),
        "speed_smoother": smoother_record(state[0x2DC:0x2FC]),
        "dynamics": dynamics_record(state[0x2FC:0x328]),
    }


def run_case(
    image: bytes,
    *,
    sample_index: int,
    heart_rate: int,
    selected_speed: float,
    auxiliaries: tuple[float, float, float],
    trailing_input: float,
    route_flag_word: int,
    primary_config: float,
    alternate_config: float,
    previous_heart_rate: int = 0,
    previous_speed: float = 0,
    validation_latch_raw: int = 0,
    speed_history: tuple[float, float, float, float, float, float] = (0, 0, 0, 0, 0, 0),
    heart_filter_enabled_raw: int = 0,
    smoother_enabled_raw: int = 0,
    smoother_limits: tuple[float, float, float, float] = (0, 0, 0, 0),
    dynamics_state_first: float = 0,
    dynamics_state_second: float = 0,
    dynamics_flag_word: int = 0,
    ratio_profile_flag_raw: int = 0,
    ratio_thresholds: tuple[float, float, float, float, float] = (0, 0, 0, 0, 0),
) -> dict[str, Any]:
    fixture = LocomotionFirmwareFixture(image)
    core = bytearray(0x33C)
    struct.pack_into("<i", core, 0x20, previous_heart_rate)
    struct.pack_into("<f", core, 0x28, previous_speed)
    struct.pack_into("<H", core, 0x56, route_flag_word)
    core[0x60] = validation_latch_raw
    core[0x0D] = ratio_profile_flag_raw
    struct.pack_into("<5f", core, 0x170, *ratio_thresholds)
    struct.pack_into("<6f", core, 0x184, *speed_history)
    core[0x278] = heart_filter_enabled_raw
    core[0x2DC] = smoother_enabled_raw
    struct.pack_into("<4f", core, 0x2EC, *smoother_limits)
    struct.pack_into("<2f", core, 0x2FC, dynamics_state_first, dynamics_state_second)
    struct.pack_into("<H", core, 0x320, dynamics_flag_word)
    fixture.uc.mem_write(CORE_STATE, bytes(core))

    config = bytearray(32)
    struct.pack_into("<f", config, 8, primary_config)
    struct.pack_into("<f", config, 12, alternate_config)
    fixture.uc.mem_write(CONFIG, bytes(config))
    input_record = struct.pack(
        "<IIiffffIf",
        1_000,
        sample_index,
        heart_rate,
        selected_speed,
        auxiliaries[0],
        auxiliaries[1],
        auxiliaries[2],
        CONFIG,
        trailing_input,
    )
    fixture.uc.mem_write(INPUT, input_record)
    return_code = fixture.call(PER_ITERATION, CORE_STATE, INPUT)
    final_state = bytes(fixture.uc.mem_read(CORE_STATE, 0x33C))
    final_input = bytes(fixture.uc.mem_read(INPUT, len(input_record)))
    final_config = bytes(fixture.uc.mem_read(CONFIG, 32))
    return {
        "return_code": signed32(return_code),
        "input_heart_rate_after": struct.unpack_from("<i", final_input, 8)[0],
        "primary_config_after": float_record(struct.unpack_from("<I", final_config, 8)[0]),
        "alternate_config_after": float_record(struct.unpack_from("<I", final_config, 12)[0]),
        "state": modeled_state_record(final_state),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    cases = {
        "stock_success": run_case(
            image,
            sample_index=0,
            heart_rate=72,
            selected_speed=10,
            auxiliaries=(2, 3, 4),
            trailing_input=5,
            route_flag_word=0,
            primary_config=7,
            alternate_config=9,
        ),
        "invalid_heart_rate_early_exit": run_case(
            image,
            sample_index=0,
            heart_rate=35,
            selected_speed=10,
            auxiliaries=(2, 3, 4),
            trailing_input=5,
            route_flag_word=0,
            primary_config=7,
            alternate_config=9,
        ),
        "zero_heart_rate_carries_previous": run_case(
            image,
            sample_index=1,
            heart_rate=0,
            selected_speed=12,
            auxiliaries=(2, 3, 4),
            trailing_input=5,
            route_flag_word=0,
            primary_config=7,
            alternate_config=9,
            previous_heart_rate=72,
            previous_speed=10,
            validation_latch_raw=1,
            speed_history=(10, 0, 0, 0, 0, 0),
        ),
        "mode_one_inactive_smoother": run_case(
            image,
            sample_index=0,
            heart_rate=72,
            selected_speed=10,
            auxiliaries=(2, 3, 4),
            trailing_input=5,
            route_flag_word=0x0040,
            primary_config=7,
            alternate_config=9,
        ),
        "enabled_hr_and_ratio": run_case(
            image,
            sample_index=0,
            heart_rate=80,
            selected_speed=10,
            auxiliaries=(6, 3, 4),
            trailing_input=5,
            route_flag_word=0x040C,
            primary_config=7,
            alternate_config=9,
            heart_filter_enabled_raw=1,
            smoother_enabled_raw=1,
            smoother_limits=(5, 4, 3, 2),
            dynamics_state_first=1.2,
            dynamics_state_second=70,
            ratio_thresholds=(90, 110, 130, 150, 170),
        ),
    }

    def bits(items: list[dict[str, Any]]) -> list[str]:
        return [item["bits"] for item in items]

    stock = cases["stock_success"]
    assert (
        stock["return_code"], stock["input_heart_rate_after"],
        stock["state"]["selected_heart_rate"], stock["state"]["previous_heart_rate"],
        stock["state"]["selected_speed"]["bits"],
        stock["state"]["previous_speed"]["bits"],
        stock["state"]["validation_latch_raw"], stock["state"]["raw_status"],
    ) == (0, 72, 72, 72, "0x41200000", "0x41200000", 1, 0)
    assert bits(stock["state"]["speed_filter_history"]) == [
        "0x41200000", "0x00000000", "0x00000000",
        "0x00000000", "0x00000000", "0x00000000",
    ]

    invalid = cases["invalid_heart_rate_early_exit"]
    assert (
        invalid["return_code"], invalid["state"]["raw_status"],
        invalid["state"]["validation_latch_raw"],
        invalid["state"]["selected_heart_rate"], invalid["state"]["previous_heart_rate"],
        invalid["state"]["selected_speed"]["bits"],
        invalid["state"]["previous_speed"]["bits"],
        invalid["state"]["previous_auxiliary"]["bits"],
    ) == (-1016, -1016, 0, 0, 0, "0x41200000", "0x00000000", "0x00000000")
    assert bits(invalid["state"]["speed_filter_history"])[0] == "0x41200000"
    assert invalid["state"]["heart_rate_filter"]["header"] == [0] * 8

    carried = cases["zero_heart_rate_carries_previous"]
    assert (
        carried["return_code"], carried["input_heart_rate_after"],
        carried["state"]["selected_heart_rate"], carried["state"]["previous_heart_rate"],
        carried["state"]["selected_speed"]["bits"],
    ) == (0, 72, 72, 72, "0x41300000")
    assert bits(carried["state"]["speed_filter_history"])[:2] == [
        "0x41200000", "0x41400000",
    ]

    mode_one = cases["mode_one_inactive_smoother"]
    assert (
        mode_one["return_code"], mode_one["state"]["smoother_produced"]["bits"],
        mode_one["state"]["selected_speed"]["bits"],
        mode_one["state"]["previous_speed"]["bits"],
    ) == (0, "0x00000000", "0x411ffff7", "0x411ffff7")
    assert bits(mode_one["state"]["dynamics"]["float32_words"]) == [
        "0x00000000", "0x00000000", "0x4031c71d", "0x00000000",
        "0x00000000", "0x00000000", "0x4031c713", "0x00000000",
        "0x00000000",
    ]

    enabled = cases["enabled_hr_and_ratio"]
    assert (
        enabled["return_code"], enabled["primary_config_after"]["bits"],
        enabled["state"]["selected_heart_rate"],
        enabled["state"]["selected_speed"]["bits"],
        enabled["state"]["speed_smoother"]["sample_count"],
        enabled["state"]["heart_rate_filter"]["average"]["bits"],
        enabled["state"]["ratio_primary_sums"][0]["bits"],
        enabled["state"]["ratio_primary_counts"][0]["bits"],
    ) == (0, "0x00000000", 80, "0x411fb885", 1, "0x42a00000",
          "0x3e1be332", "0x3f800000")
    assert enabled["state"]["heart_rate_filter"]["header"] == [1, 1, 1, 1, 1, 0, 0, 0]
    assert bits(enabled["state"]["ratio_moments"]) == [
        "0x42a00000", "0x3f800000", "0x45c80000",
        "0x42a00000", "0x411fb885", "0x3f800000",
    ]
    assert bits(enabled["state"]["dynamics"]["float32_words"]) == [
        "0x3f99999a", "0x428c0000", "0x4031c71d", "0x00000000",
        "0x438707e8", "0x00000000", "0x403177b0", "0x00000000",
        "0x00000000",
    ]

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{PER_ITERATION:08x}",
        "cases": cases,
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
