#!/usr/bin/env python3
"""Run isolated production-Thumb fixtures for the dormant multivariate estimator stage.

Only the SHA-pinned application and private emulated RAM are mapped. Synthetic inputs exercise the
stock-disabled gate, compiled active/bypass modes, replay error, force-invalid flag and 68-byte
status helper. No BLE, sensor, flash, health-store, or physical-device access occurs.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_R1

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


INITIALIZER = 0x000715F8
WRAPPER = 0x0005FEB8
PER_ITERATION = 0x000721B4
ENGINE_INITIALIZER = 0x00071714
STATE = RAM_BASE + 0x6000
PREVIOUS = RAM_BASE + 0x6500
TIMESTAMP = RAM_BASE + 0x6600
HEART_RATE = RAM_BASE + 0x6610
SPEED = RAM_BASE + 0x6620
PROFILE = RAM_BASE + 0x6630
AUXILIARY = RAM_BASE + 0x6650
ENERGY = RAM_BASE + 0x6660
OUTPUT = RAM_BASE + 0x6700
ENGINE = RAM_BASE + 0x6900


class DormantEstimatorFirmwareFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.machine.uc.mem_write(PREVIOUS, b"\x00" * 128)
        self.machine.uc.mem_write(STATE, b"\xa5" * 0x33C)
        self.initializer_return = self.machine.call(INITIALIZER, STATE, PREVIOUS)
        self.core_inputs: list[dict[str, Any]] = []
        self.machine.uc.hook_add(
            UC_HOOK_CODE,
            self._record_core_input,
            begin=PER_ITERATION,
            end=PER_ITERATION,
        )

    def _record_core_input(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del address, size, user_data
        pointer = uc.reg_read(UC_ARM_REG_R1)
        raw = bytes(uc.mem_read(pointer, 36))
        config_pointer = struct.unpack("<I", raw[0x1C:0x20])[0]
        config = bytes(uc.mem_read(config_pointer, 16))
        self.core_inputs.append({
            "current_time": struct.unpack("<I", raw[0:4])[0],
            "sample_index": struct.unpack("<I", raw[4:8])[0],
            "heart_rate": struct.unpack("<i", raw[8:12])[0],
            "selected_speed_bits": f"0x{struct.unpack('<I', raw[12:16])[0]:08x}",
            "auxiliary_bits": [
                f"0x{value:08x}" for value in struct.unpack("<3I", raw[16:28])
            ],
            "config_bits": [
                f"0x{value:08x}" for value in struct.unpack("<4I", config)
            ],
            "trailing_unused_bits": f"0x{struct.unpack('<I', raw[32:36])[0]:08x}",
        })

    def set_mode(self, mode: int) -> None:
        self.machine.uc.mem_write(STATE + 0x330, struct.pack("<I", mode))

    def update(
        self,
        elapsed_seconds: int,
        *,
        output_fill: int = 0xA5,
        force_invalid: bool = False,
        fatal_state: int = 0,
        heart_rate: float = 72.0,
        speed: float = 0.0,
    ) -> dict[str, Any]:
        self.core_inputs = []
        self.machine.uc.mem_write(TIMESTAMP, struct.pack("<I", 1_000))
        self.machine.uc.mem_write(HEART_RATE, struct.pack("<ffB", heart_rate, 1.0, 0))
        self.machine.uc.mem_write(SPEED, struct.pack("<fB", speed, 0))
        self.machine.uc.mem_write(
            PROFILE,
            struct.pack("<6f", 175.0, 75.0, 28.0, 0.0, 0.0, 1.0),
        )
        self.machine.uc.mem_write(AUXILIARY, struct.pack("<3I", 0, 0, 0))
        self.machine.uc.mem_write(ENERGY, struct.pack("<f", 0.1))
        self.machine.uc.mem_write(OUTPUT, bytes([output_fill]) * 68)
        self.machine.uc.mem_write(STATE + 0x334, bytes([int(force_invalid)]))
        self.machine.uc.mem_write(STATE + 0x54, struct.pack("<H", fatal_state))
        return_code = self.machine.call(
            WRAPPER,
            STATE,
            elapsed_seconds,
            TIMESTAMP,
            HEART_RATE,
            SPEED,
            PROFILE,
            AUXILIARY,
            ENERGY,
            OUTPUT,
        )
        state = bytes(self.machine.uc.mem_read(STATE, 0x33C))
        output = bytes(self.machine.uc.mem_read(OUTPUT, 68))
        status = struct.unpack("<h", output[66:68])[0]
        return {
            "return_code": return_code,
            "output_hex": output.hex(),
            "output_prefix_unchanged": output[:66] == bytes([output_fill]) * 66,
            "output_all_zero": output == bytes(68),
            "output_status": status,
            "output_status_low_byte": output[66],
            "core_inputs": self.core_inputs,
            "state": {
                "selected_heart_rate": struct.unpack("<i", state[0x1C:0x20])[0],
                "previous_heart_rate": struct.unpack("<i", state[0x20:0x24])[0],
                "selected_speed_bits": f"0x{struct.unpack('<I', state[0x24:0x28])[0]:08x}",
                "prior_processed_time": struct.unpack("<I", state[0x48:0x4C])[0],
                "scheduled_iteration_count": struct.unpack("<I", state[0x4C:0x50])[0],
                "raw_status": struct.unpack("<h", state[0x52:0x54])[0],
                "fatal_state": struct.unpack("<h", state[0x54:0x56])[0],
                "validation_latch": state[0x60],
                "speed_history_bits": [
                    f"0x{value:08x}" for value in struct.unpack("<6I", state[0x184:0x19C])
                ],
                "accumulated_elapsed": struct.unpack("<I", state[0x328:0x32C])[0],
                "update_count": struct.unpack("<I", state[0x32C:0x330])[0],
                "mode": struct.unpack("<I", state[0x330:0x334])[0],
                "force_invalid": state[0x334],
                "previous_pointer": f"0x{struct.unpack('<I', state[0x338:0x33C])[0]:08x}",
            },
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    initialized_engine = LocomotionFirmwareFixture(image)
    initialized_engine.uc.mem_write(ENGINE, b"\xa5" * 0x1F8)
    initialized_engine.call(ENGINE_INITIALIZER, ENGINE)
    engine_prefix = bytes(initialized_engine.uc.mem_read(ENGINE, 0x118))
    auxiliary_defaults = struct.unpack("<3f", engine_prefix[0x14:0x20])
    config_defaults = tuple(
        struct.unpack("<f", engine_prefix[offset:offset + 4])[0]
        for offset in (0x54, 0x58, 0x5C, 0x68)
    )

    disabled = DormantEstimatorFirmwareFixture(image)
    disabled_case = disabled.update(1)

    bypass = DormantEstimatorFirmwareFixture(image)
    bypass.set_mode(2)
    bypass_case = bypass.update(7)

    active = DormantEstimatorFirmwareFixture(image)
    active.set_mode(1)
    active_first = active.update(1)
    active_gap_error = active.update(20)

    replay = DormantEstimatorFirmwareFixture(image)
    replay.set_mode(1)
    replay_first = replay.update(1, speed=10.0)
    replay_five = replay.update(5, speed=10.0)
    replay_cursor_equal = replay.update(1, speed=10.0)

    invalid = DormantEstimatorFirmwareFixture(image)
    invalid.set_mode(1)
    force_invalid_case = invalid.update(1, force_invalid=True)

    fatal = DormantEstimatorFirmwareFixture(image)
    fatal.set_mode(1)
    fatal_case = fatal.update(1, fatal_state=1)

    force_replay = DormantEstimatorFirmwareFixture(image)
    force_replay.set_mode(1)
    force_replay_first = force_replay.update(1, force_invalid=True)
    force_replay_five = force_replay.update(5, force_invalid=True)

    conversion_cases: dict[str, dict[str, Any]] = {}
    for label, value, expected in (
        ("positive_fraction", 72.9, 72),
        ("negative_fraction", -72.9, -72),
        ("nan", float("nan"), 0),
        ("positive_infinity", float("inf"), 0x7FFFFFFF),
        ("negative_infinity", float("-inf"), -0x80000000),
        ("largest_in_range_float", 2_147_483_520.0, 2_147_483_520),
        ("positive_out_of_range", 2_147_483_648.0, 0x7FFFFFFF),
        ("negative_limit", -2_147_483_648.0, -0x80000000),
    ):
        fixture = DormantEstimatorFirmwareFixture(image)
        fixture.set_mode(1)
        result = fixture.update(1, heart_rate=value)
        assert len(result["core_inputs"]) == 1
        observed = result["core_inputs"][0]["heart_rate"]
        assert observed == expected, (label, observed, expected)
        conversion_cases[label] = {
            "input_float32_bits": f"0x{struct.unpack('<I', struct.pack('<f', value))[0]:08x}",
            "converted_int32": observed,
        }

    assert disabled.initializer_return == 0
    initialized_tail = bytes(disabled.machine.uc.mem_read(STATE + 0x328, 20))
    assert disabled_case["return_code"] == 1
    assert disabled_case["output_prefix_unchanged"]
    assert disabled_case["state"]["update_count"] == 0
    assert bypass_case["return_code"] == 0
    assert bypass_case["output_prefix_unchanged"]
    assert bypass_case["state"]["update_count"] == 1
    assert active_first["return_code"] == 0
    assert active_first["output_status"] == 0
    assert active_first["output_prefix_unchanged"]
    assert active_gap_error["output_status"] == -1027
    assert active_gap_error["output_status_low_byte"] == 0xFD
    assert active_gap_error["state"]["accumulated_elapsed"] == 20
    assert active_gap_error["state"]["update_count"] == 2
    assert replay_first["core_inputs"][0]["sample_index"] == 0
    assert [item["sample_index"] for item in replay_five["core_inputs"]] == [1, 2, 3, 4, 5]
    assert replay_five["state"]["scheduled_iteration_count"] == 5
    assert replay_five["state"]["prior_processed_time"] == 6
    assert replay_five["state"]["accumulated_elapsed"] == 5
    assert [item["sample_index"] for item in replay_cursor_equal["core_inputs"]] == [6]
    assert replay_cursor_equal["state"]["prior_processed_time"] == 6
    assert force_invalid_case["state"]["selected_speed_bits"] == "0xbf800000"
    assert force_replay_first["core_inputs"][0]["heart_rate"] == -1
    assert [item["heart_rate"] for item in force_replay_five["core_inputs"]] == [-1] * 5
    assert force_replay_five["state"]["prior_processed_time"] == 6
    assert force_replay_five["state"]["raw_status"] == -1016
    assert fatal_case["output_all_zero"]
    assert initialized_tail[8:12] == b"\x00" * 4  # stock mode remains zero
    assert auxiliary_defaults == (-1.0, -1.0, -1.0)
    assert config_defaults == (-999.0, -999.0, -999999.0, 0.0)

    print(json.dumps({
        "initializer": {
            "function": f"0x{INITIALIZER:08x}",
            "return_code": disabled.initializer_return,
            "state_bytes": 0x33C,
            "previous_pointer": f"0x{PREVIOUS:08x}",
        },
        "engine_input_defaults": {
            "initializer": f"0x{ENGINE_INITIALIZER:08x}",
            "unresolved_auxiliary": list(auxiliary_defaults),
            "internal_config": list(config_defaults),
            "internal_config_is_user_profile": False,
        },
        "wrapper_function": f"0x{WRAPPER:08x}",
        "cases": {
            "stock_disabled": disabled_case,
            "nonzero_core_bypass": bypass_case,
            "active_first": active_first,
            "active_gap_error": active_gap_error,
            "active_replay_first": replay_first,
            "active_replay_five": replay_five,
            "active_cursor_equal": replay_cursor_equal,
            "force_invalid_inputs": force_invalid_case,
            "force_invalid_replay_first": force_replay_first,
            "force_invalid_replay_five": force_replay_five,
            "fatal_output_clear": fatal_case,
        },
        "heart_rate_vcvt_s32_f32": conversion_cases,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
