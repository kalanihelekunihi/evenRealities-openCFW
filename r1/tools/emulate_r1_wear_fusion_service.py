#!/usr/bin/env python3
"""Execute isolated production-Thumb wear-fusion and public-mapping boundary fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


WEAR_ON_CANDIDATE = 0x0003D268
WEAR_OFF_CANDIDATE = 0x0003D45C
WEAR_STATE_ACCESSOR = 0x0004C5B8
CONFIRMED_WEAR_ACCESSOR = 0x0004C634
PUBLIC_WEAR_QUERY = 0x00084B24
BOOLEAN_NORMALIZER = 0x00096A40
IR_RANGE_HELPER = 0x0003D06C
TICK_GETTER = 0x0007D28C
SUBSCRIBE = 0x000897E8
UNSUBSCRIBE = 0x00089B08
LOG_FLAGS = 0x000914EC
PUBLIC_RESPONSE = 0x00083C62

WEAR_STATE = 0x2001E454
WEAR_RUNTIME = 0x20006E94
STATS = RAM_BASE + 0x39000
REQUEST = RAM_BASE + 0x39100
SUBSCRIPTION_HANDLE = RAM_BASE + 0x39200


class WearFusionFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.tick = 0
        self.public_responses: list[int] = []
        self.subscription_starts = 0
        self.subscription_stops = 0
        self.machine.uc.mem_write(WEAR_STATE, b"\x00" * 41)
        self.machine.uc.mem_write(WEAR_RUNTIME, b"\x00" * 40)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == TICK_GETTER:
            self._return(uc, self.tick)
        elif address == IR_RANGE_HELPER:
            values = self.history_values()
            previous = self.u32(WEAR_STATE + 0x18)
            if previous:
                values.append(previous)
            value_range = max(values) - min(values) if values else 0
            self._return(uc, value_range)
        elif address == SUBSCRIBE:
            self.subscription_starts += 1
            self._return(uc, SUBSCRIPTION_HANDLE)
        elif address == UNSUBSCRIBE:
            self.subscription_stops += 1
            self._return(uc, 0)
        elif address == PUBLIC_RESPONSE:
            pointer = uc.reg_read(UC_ARM_REG_R0)
            self.public_responses.append(bytes(uc.mem_read(pointer, 1))[0])
            self._return(uc, 1)

    def u32(self, address: int) -> int:
        return struct.unpack("<I", bytes(self.machine.uc.mem_read(address, 4)))[0]

    def history_values(self) -> list[int]:
        count = bytes(self.machine.uc.mem_read(WEAR_STATE + 0x14, 1))[0]
        return list(struct.unpack(
            f"<{count}I",
            bytes(self.machine.uc.mem_read(WEAR_STATE, count * 4)),
        )) if count else []

    def configure(
        self,
        *,
        state: int,
        living_status: int = 0,
        living_tick: int = 0,
        low_ir_count: int = 0,
        table_count: int = 0,
        history: list[int] | None = None,
        previous: int = 0,
        wear_led_status: int = 1,
        sleep_status: int = 0,
        raw_optical_active: bool = False,
        living_probe_active: bool = False,
    ) -> None:
        values = list(history or [])
        if len(values) > 5:
            raise ValueError("wear history exceeds five slots")
        padded = values + [0] * (5 - len(values))
        raw = bytearray(41)
        struct.pack_into("<5I", raw, 0, *padded)
        raw[0x14] = len(values)
        struct.pack_into("<I", raw, 0x18, previous)
        raw[0x1C] = living_status
        struct.pack_into("<I", raw, 0x20, living_tick)
        raw[0x24] = state
        raw[0x25] = 2
        raw[0x27] = low_ir_count
        raw[0x28] = table_count
        self.machine.uc.mem_write(WEAR_STATE, bytes(raw))

        runtime = bytearray(40)
        runtime[0] = wear_led_status
        runtime[1] = sleep_status
        struct.pack_into("<I", runtime, 8, SUBSCRIPTION_HANDLE if raw_optical_active else 0)
        struct.pack_into("<I", runtime, 12, SUBSCRIPTION_HANDLE if living_probe_active else 0)
        self.machine.uc.mem_write(WEAR_RUNTIME, bytes(runtime))
        self.subscription_starts = 0
        self.subscription_stops = 0

    def write_statistics(
        self,
        *,
        mean_y: float = 0,
        variance_x: float = 0,
        variance_y: float = 0,
        variance_z: float = 0,
    ) -> None:
        self.machine.uc.mem_write(
            STATS,
            struct.pack("<6f", 0, mean_y, 0, variance_x, variance_y, variance_z),
        )

    def state(self) -> dict[str, int]:
        raw = bytes(self.machine.uc.mem_read(WEAR_STATE, 41))
        return {
            "wear_state_raw": raw[0x24],
            "living_status_raw": raw[0x1C],
            "living_tick_raw": struct.unpack_from("<I", raw, 0x20)[0],
            "low_ir_count_raw": raw[0x27],
            "table_count_raw": raw[0x28],
            "living_probe_handle": self.u32(WEAR_RUNTIME + 0x0C),
        }

    def wear_on(self) -> dict[str, int]:
        self.machine.call(WEAR_ON_CANDIDATE, STATS)
        return self.state()

    def wear_off(self) -> dict[str, int]:
        self.machine.call(WEAR_OFF_CANDIDATE, STATS)
        return self.state()

    def query(self, state: int) -> int:
        self.machine.uc.mem_write(WEAR_STATE + 0x24, bytes([state]))
        self.machine.uc.mem_write(REQUEST, b"\x00\x00\x00\x34\x12")
        self.public_responses.clear()
        self.machine.call(PUBLIC_WEAR_QUERY, 0, REQUEST)
        if len(self.public_responses) != 1:
            raise RuntimeError(f"expected one public response, got {self.public_responses}")
        return self.public_responses[0]


def run(image: bytes) -> dict[str, Any]:
    fixture = WearFusionFixture(image)

    fixture.configure(state=0)
    fixture.write_statistics(variance_x=2_000)
    motion_boundary = fixture.wear_on()
    fixture.write_statistics(variance_x=2_001)
    motion_above = fixture.wear_on()

    fixture.configure(state=0, history=[9_050_000], raw_optical_active=True)
    fixture.write_statistics()
    ir_boundary = fixture.wear_on()
    fixture.configure(state=0, history=[9_050_001], raw_optical_active=True)
    ir_above = fixture.wear_on()

    fixture.tick = 2_048
    fixture.configure(state=1, living_status=1, living_tick=0)
    fixture.write_statistics()
    living_confirmed = fixture.wear_off()
    fixture.configure(state=1, living_status=0, living_tick=0)
    living_rejected = fixture.wear_off()

    fixture.tick = 2_049
    fixture.configure(
        state=1,
        history=[9_049_999],
        raw_optical_active=True,
        low_ir_count=0,
    )
    low_ir_sequence = [fixture.wear_off() for _ in range(5)]
    fixture.configure(
        state=1,
        history=[9_049_999],
        raw_optical_active=True,
        sleep_status=1,
        low_ir_count=4,
    )
    low_ir_sleep_preserved = fixture.wear_off()

    fixture.configure(state=1, table_count=0)
    fixture.write_statistics(mean_y=1_024)
    table_sequence = [fixture.wear_off() for _ in range(60)]
    fixture.configure(state=1, table_count=59)
    fixture.write_statistics(mean_y=1_024, variance_x=40)
    table_variance_boundary = fixture.wear_off()
    fixture.configure(state=1, table_count=59)
    fixture.write_statistics(mean_y=972)
    table_gravity_boundary = fixture.wear_off()

    query_mapping = {str(state): fixture.query(state) for state in (0, 1, 2, 3)}
    confirmed_mapping = {
        str(state): fixture.machine.call(CONFIRMED_WEAR_ACCESSOR)
        for state in (0, 1, 2)
        for _ in [fixture.machine.uc.mem_write(WEAR_STATE + 0x24, bytes([state]))]
    }
    boolean_mapping = {
        str(state): fixture.machine.call(BOOLEAN_NORMALIZER, state)
        for state in (0, 1, 2, 255)
    }

    expected = {
        "motion_boundary": 0,
        "motion_above": 1,
        "ir_boundary": 0,
        "ir_above": 1,
        "living_confirmed": 2,
        "living_rejected": 0,
        "low_ir_sequence": [1, 1, 1, 1, 0],
        "low_ir_sleep_preserved": 1,
        "table_sequence_tail": [1, 1, 0],
        "table_variance_boundary": 1,
        "table_gravity_boundary": 1,
        "query_mapping": {"0": 1, "1": 2, "2": 0, "3": 0},
        "confirmed_mapping": {"0": 0, "1": 0, "2": 1},
        "boolean_mapping": {"0": 0, "1": 1, "2": 1, "255": 1},
    }
    observed = {
        "motion_boundary": motion_boundary["wear_state_raw"],
        "motion_above": motion_above["wear_state_raw"],
        "ir_boundary": ir_boundary["wear_state_raw"],
        "ir_above": ir_above["wear_state_raw"],
        "living_confirmed": living_confirmed["wear_state_raw"],
        "living_rejected": living_rejected["wear_state_raw"],
        "low_ir_sequence": [item["wear_state_raw"] for item in low_ir_sequence],
        "low_ir_sleep_preserved": low_ir_sleep_preserved["wear_state_raw"],
        "table_sequence_tail": [
            item["wear_state_raw"] for item in table_sequence[-3:]
        ],
        "table_variance_boundary": table_variance_boundary["wear_state_raw"],
        "table_gravity_boundary": table_gravity_boundary["wear_state_raw"],
        "query_mapping": query_mapping,
        "confirmed_mapping": confirmed_mapping,
        "boolean_mapping": boolean_mapping,
    }
    if observed != expected:
        raise ValueError(f"production wear-fusion fixture mismatch: {observed} != {expected}")

    return {
        "validated": True,
        "case_count": 12,
        "observed": observed,
        "safety": {
            "emulated_private_flash_and_ram_only": True,
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
