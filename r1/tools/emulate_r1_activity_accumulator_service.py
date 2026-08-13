#!/usr/bin/env python3
"""Execute the production activity-total producer, refresh, and pending-delta accessor.

The SHA-pinned Thumb functions run in private emulated flash/RAM with clock, sleep-result,
wear-fusion, logging, and internal-event calls stubbed. No BLE, physical ring, sensor, flash, or
host health store exists.
"""

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
    UC_ARM_REG_R2,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


PERIODIC_PRODUCER = 0x00048E68
EXPLICIT_REFRESH = 0x00049068
PENDING_DELTA = 0x00048D48
FIRMWARE_TIMESTAMP = 0x0008ADA4
LOCAL_DAY_START = 0x0008AD64
SLEEP_RESULT_STATUS = 0x0004A8BC
WEAR_FUSION_STATE = 0x0004C5B8
CONFIRMED_WEAR = 0x0004C634
INTERNAL_PUBLISH = 0x0008D8FC
LOG_FLAGS = 0x000914EC

STATE = 0x20006EBC
COUNTERS = RAM_BASE + 0x38000
OUTPUT = RAM_BASE + 0x38100


def counters(steps: int, all_kcal: int, active_kcal: int) -> dict[str, int]:
    return {
        "steps": steps,
        "all_kcal": all_kcal,
        "active_kcal": active_kcal,
    }


def event_fields(raw: bytes) -> dict[str, int]:
    all_kcal, active_kcal, steps, duration, timestamp = struct.unpack("<4HI", raw)
    return {
        "all_kcal": all_kcal,
        "active_kcal": active_kcal,
        "steps_low_u16": steps,
        "duration_seconds": duration,
        "timestamp": timestamp,
    }


class ActivityAccumulatorFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.firmware_timestamp = 0
        self.local_day_start = 0
        self.sleep_result_status = 0
        self.wear_fusion_state = 2
        self.events: list[dict[str, Any]] = []
        self.machine.uc.mem_write(STATE, b"\x00" * 24)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == FIRMWARE_TIMESTAMP:
            self._return(uc, self.firmware_timestamp)
        elif address == LOCAL_DAY_START:
            self._return(uc, self.local_day_start)
        elif address == SLEEP_RESULT_STATUS:
            self._return(uc, self.sleep_result_status)
        elif address == WEAR_FUSION_STATE:
            self._return(uc, self.wear_fusion_state)
        elif address == CONFIRMED_WEAR:
            self._return(uc, int(self.wear_fusion_state == 2))
        elif address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == INTERNAL_PUBLISH:
            event_id = uc.reg_read(UC_ARM_REG_R0) & 0xFFFF
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            raw = bytes(uc.mem_read(pointer, length)) if pointer and length else b""
            self.events.append({
                "event_id": event_id,
                "length": length,
                "raw_hex": raw.hex(),
                "fields": event_fields(raw) if event_id == 0x000B and length == 12 else None,
            })
            self._return(uc, 1)

    def set_state(
        self,
        *,
        window_published: int = 0,
        transition_pending: int = 0,
        reserved: int = 0,
        transition_started: int = 0,
        baseline: tuple[int, int, int] = (0, 0, 0),
        current: tuple[int, int, int] = (0, 0, 0),
    ) -> None:
        raw = struct.pack(
            "<BBHIIHHIHH",
            window_published,
            transition_pending,
            reserved,
            transition_started,
            baseline[0],
            baseline[1],
            baseline[2],
            current[0],
            current[1],
            current[2],
        )
        self.machine.uc.mem_write(STATE, raw)

    def state(self) -> dict[str, Any]:
        raw = bytes(self.machine.uc.mem_read(STATE, 24))
        (
            window,
            pending,
            reserved,
            transition_started,
            baseline_steps,
            baseline_all,
            baseline_active,
            current_steps,
            current_all,
            current_active,
        ) = struct.unpack("<BBHIIHHIHH", raw)
        return {
            "window_published_raw": window,
            "transition_pending_raw": pending,
            "reserved_raw": reserved,
            "transition_started": transition_started,
            "baseline": counters(baseline_steps, baseline_all, baseline_active),
            "current": counters(current_steps, current_all, current_active),
            "raw_hex": raw.hex(),
        }

    def periodic(
        self,
        *,
        timestamp: int,
        local_day_start: int,
        current: tuple[int, int, int],
        sleep_result_status: int = 0,
        wear_fusion_state: int = 2,
    ) -> dict[str, Any]:
        self.events.clear()
        self.firmware_timestamp = timestamp
        self.local_day_start = local_day_start
        self.sleep_result_status = sleep_result_status
        self.wear_fusion_state = wear_fusion_state
        self.machine.uc.mem_write(COUNTERS, struct.pack("<IHH", *current))
        before = self.state()
        self.machine.call(PERIODIC_PRODUCER, COUNTERS)
        return {"before": before, "after": self.state(), "events": list(self.events)}

    def refresh(
        self,
        *,
        timestamp: int,
        sleep_result_status: int = 0,
        wear_fusion_state: int = 2,
    ) -> dict[str, Any]:
        self.events.clear()
        self.firmware_timestamp = timestamp
        self.sleep_result_status = sleep_result_status
        self.wear_fusion_state = wear_fusion_state
        before = self.state()
        self.machine.call(EXPLICIT_REFRESH)
        return {"before": before, "after": self.state(), "events": list(self.events)}

    def pending_delta(
        self,
        *,
        sleep_result_status: int = 0,
        wear_fusion_state: int = 2,
    ) -> dict[str, Any]:
        self.sleep_result_status = sleep_result_status
        self.wear_fusion_state = wear_fusion_state
        self.machine.uc.mem_write(OUTPUT, b"\xA5" * 12)
        self.machine.call(PENDING_DELTA, OUTPUT)
        raw = bytes(self.machine.uc.mem_read(OUTPUT, 12))
        return {"raw_hex": raw.hex(), "fields": event_fields(raw)}


def run(image: bytes) -> dict[str, Any]:
    periodic = ActivityAccumulatorFixture(image)
    periodic.set_state(
        window_published=1,
        reserved=0xBEEF,
        baseline=(1_000, 100, 50),
        current=(1_000, 100, 50),
    )
    early = periodic.periodic(
        timestamp=1_000,
        local_day_start=0,
        current=(1_005, 102, 51),
    )
    tail = periodic.periodic(
        timestamp=1_195,
        local_day_start=0,
        current=(1_010, 103, 52),
    )
    repeated = periodic.periodic(
        timestamp=1_196,
        local_day_start=0,
        current=(1_012, 104, 53),
    )
    refresh_after_periodic = periodic.refresh(timestamp=1_301)

    rollback_fixture = ActivityAccumulatorFixture(image)
    rollback_fixture.set_state(
        baseline=(100, 10, 10),
        current=(100, 10, 10),
    )
    rollback = rollback_fixture.periodic(
        timestamp=1_795,
        local_day_start=0,
        current=(99, 9, 9),
    )

    midnight_fixture = ActivityAccumulatorFixture(image)
    midnight_fixture.set_state(
        window_published=1,
        baseline=(1, 1, 1),
        current=(1, 1, 1),
    )
    midnight = midnight_fixture.periodic(
        timestamp=86_400,
        local_day_start=86_400,
        current=(500, 40, 20),
    )

    transition_fixture = ActivityAccumulatorFixture(image)
    transition_fixture.set_state(
        reserved=0x1234,
        baseline=(10, 2, 1),
        current=(20, 4, 2),
    )
    transition_start = transition_fixture.refresh(timestamp=2_000, wear_fusion_state=1)
    transition_900 = transition_fixture.refresh(timestamp=2_900, wear_fusion_state=1)
    transition_901 = transition_fixture.refresh(timestamp=2_901, wear_fusion_state=1)

    unavailable_fixture = ActivityAccumulatorFixture(image)
    unavailable_fixture.set_state(
        transition_pending=1,
        transition_started=100,
        baseline=(10, 2, 1),
        current=(20, 4, 2),
    )
    unavailable = unavailable_fixture.refresh(timestamp=200, sleep_result_status=1)

    low16_fixture = ActivityAccumulatorFixture(image)
    low16_fixture.set_state(
        window_published=7,
        baseline=(0, 10, 20),
        current=(65_537, 13, 22),
    )
    low16 = low16_fixture.refresh(timestamp=1_301)

    pending_fixture = ActivityAccumulatorFixture(image)
    pending_fixture.set_state(
        baseline=(1_000, 100, 50),
        current=(1_010, 103, 52),
    )
    pending = pending_fixture.pending_delta()
    pending_unavailable = pending_fixture.pending_delta(sleep_result_status=1)

    assert early["events"] == []
    assert early["after"]["window_published_raw"] == 0
    assert early["after"]["current"] == counters(1_005, 102, 51)
    assert early["after"]["reserved_raw"] == 0xBEEF
    assert tail["events"][0]["fields"] == {
        "all_kcal": 3,
        "active_kcal": 2,
        "steps_low_u16": 10,
        "duration_seconds": 595,
        "timestamp": 1_195,
    }
    assert tail["after"]["window_published_raw"] == 1
    assert repeated["events"] == []
    assert repeated["after"]["current"] == counters(1_012, 104, 53)
    assert refresh_after_periodic["events"][0]["fields"] == {
        "all_kcal": 1,
        "active_kcal": 1,
        "steps_low_u16": 2,
        "duration_seconds": 101,
        "timestamp": 1_301,
    }
    assert refresh_after_periodic["after"]["window_published_raw"] == 1
    assert rollback["events"] == []
    assert rollback["after"]["baseline"] == counters(99, 9, 9)
    assert rollback["after"]["window_published_raw"] == 1
    assert midnight["events"] == []
    assert midnight["after"]["baseline"] == counters(500, 40, 20)
    assert midnight["after"]["window_published_raw"] == 0
    assert transition_start["after"]["transition_pending_raw"] == 1
    assert transition_start["after"]["transition_started"] == 2_000
    assert transition_900["after"]["baseline"] == counters(10, 2, 1)
    assert transition_901["after"]["baseline"] == counters(20, 4, 2)
    assert transition_901["after"]["transition_pending_raw"] == 0
    assert unavailable["after"]["baseline"] == counters(20, 4, 2)
    assert unavailable["after"]["transition_pending_raw"] == 0
    assert low16["events"][0]["fields"] == {
        "all_kcal": 3,
        "active_kcal": 2,
        "steps_low_u16": 1,
        "duration_seconds": 101,
        "timestamp": 1_301,
    }
    assert low16["after"]["window_published_raw"] == 7
    assert pending["fields"] == {
        "all_kcal": 3,
        "active_kcal": 2,
        "steps_low_u16": 10,
        "duration_seconds": 0,
        "timestamp": 0,
    }
    assert pending_unavailable["raw_hex"] == "00" * 12

    return {
        "periodic_early": early,
        "periodic_tail": tail,
        "periodic_repeat_suppressed": repeated,
        "explicit_refresh_after_periodic": refresh_after_periodic,
        "periodic_rollback": rollback,
        "midnight_clean": midnight,
        "transition_start": transition_start,
        "transition_elapsed_900": transition_900,
        "transition_elapsed_901": transition_901,
        "unavailable_rebase": unavailable,
        "step_delta_low_u16_and_refresh_flag_preservation": low16,
        "pending_delta": pending,
        "pending_delta_unavailable": pending_unavailable,
        "safety": {
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
