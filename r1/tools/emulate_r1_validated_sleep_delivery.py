#!/usr/bin/env python3
"""Execute isolated production-Thumb validated-sleep delivery fixtures."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


STORAGE_APPEND = 0x0005B890
AUTOMATIC_SYNC_GATE = 0x0008B138
STORAGE_CONSUMER = 0x0008DC94
INITIAL_CONSUMER = 0x0008DD90
SYSTEM_EVENT = 0x0008D8FC
LOG_FLAGS = 0x000914EC

RECORD = RAM_BASE + 0x53000


class ValidatedSleepFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.storage_event_result = 1
        self.storage_append_result = 1
        self.intercept_storage_consumer = False
        self.system_events: list[tuple[int, bytes]] = []
        self.direct_storage_fallbacks: list[int] = []
        self.storage_append_calls: list[tuple[int, int]] = []
        self.automatic_sync_arguments: list[int] = []
        self.machine.uc.mem_write(RECORD, b"\x00" * 0x10000)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)
        self.machine.uc.hook_add(UC_HOOK_MEM_INVALID, self._invalid_memory)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == SYSTEM_EVENT:
            event_id = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            payload = bytes(uc.mem_read(pointer, length)) if length else b""
            self.system_events.append((event_id, payload))
            self._return(uc, self.storage_event_result)
        elif address == STORAGE_CONSUMER and self.intercept_storage_consumer:
            self.direct_storage_fallbacks.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)
        elif address == STORAGE_APPEND:
            self.storage_append_calls.append((
                uc.reg_read(UC_ARM_REG_R0),
                uc.reg_read(UC_ARM_REG_R1),
            ))
            self._return(uc, self.storage_append_result)
        elif address == AUTOMATIC_SYNC_GATE:
            self.automatic_sync_arguments.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)

    def _invalid_memory(
        self,
        uc: Any,
        access: int,
        address: int,
        size: int,
        value: int,
        user_data: Any,
    ) -> bool:
        del access, size, value, user_data
        raise RuntimeError(
            f"invalid firmware fixture memory at 0x{address:08x}, "
            f"pc=0x{uc.reg_read(UC_ARM_REG_PC):08x}"
        )

    def reset_observations(self) -> None:
        self.system_events.clear()
        self.direct_storage_fallbacks.clear()
        self.storage_append_calls.clear()
        self.automatic_sync_arguments.clear()

    def write_record(
        self,
        start: int,
        end: int,
        compact_count: int,
        body: bytes = b"",
    ) -> None:
        header = bytearray(32)
        header[0] = 2
        struct.pack_into("<I", header, 0x0C, start)
        struct.pack_into("<I", header, 0x10, end)
        struct.pack_into("<H", header, 0x1E, compact_count)
        self.machine.uc.mem_write(RECORD, bytes(header) + body)


def run(image: bytes) -> dict[str, Any]:
    fixture = ValidatedSleepFixture(image)
    fixture.intercept_storage_consumer = True

    fixture.write_record(100, 3_699, 1, b"\x08")
    fixture.reset_observations()
    fixture.machine.call(INITIAL_CONSUMER, RECORD)
    below_hour_events = list(fixture.system_events)

    fixture.write_record(100, 3_700, 1, b"\x08")
    fixture.storage_event_result = 1
    fixture.reset_observations()
    fixture.machine.call(INITIAL_CONSUMER, RECORD)
    exact_hour_events = list(fixture.system_events)
    exact_hour_fallbacks = list(fixture.direct_storage_fallbacks)

    fixture.write_record(100, 99, 1, b"\x08")
    fixture.reset_observations()
    fixture.machine.call(INITIAL_CONSUMER, RECORD)
    backwards_events = list(fixture.system_events)

    fixture.write_record(0, 3_600, 0xFFE0)
    fixture.reset_observations()
    fixture.machine.call(INITIAL_CONSUMER, RECORD)
    wrapping_events = list(fixture.system_events)

    fixture.write_record(100, 3_700, 1, b"\x08")
    fixture.storage_event_result = 0
    fixture.reset_observations()
    fixture.machine.call(INITIAL_CONSUMER, RECORD)
    failed_queue_events = list(fixture.system_events)
    failed_queue_fallbacks = list(fixture.direct_storage_fallbacks)

    fixture.intercept_storage_consumer = False
    fixture.storage_event_result = 1
    fixture.reset_observations()
    fixture.machine.call(STORAGE_CONSUMER, 0)
    null_storage_calls = list(fixture.storage_append_calls)

    fixture.write_record(100, 3_700, 1, b"\x08")
    fixture.storage_append_result = 0
    fixture.reset_observations()
    fixture.machine.call(STORAGE_CONSUMER, RECORD)
    failed_append_calls = list(fixture.storage_append_calls)
    failed_append_sync = list(fixture.automatic_sync_arguments)

    fixture.storage_append_result = 1
    fixture.reset_observations()
    fixture.machine.call(STORAGE_CONSUMER, RECORD)
    successful_append_calls = list(fixture.storage_append_calls)
    successful_append_sync = list(fixture.automatic_sync_arguments)

    fixture.write_record(0, 3_600, 0xFFE0)
    fixture.reset_observations()
    fixture.machine.call(STORAGE_CONSUMER, RECORD)
    wrapping_append_calls = list(fixture.storage_append_calls)

    assert below_hour_events == []
    assert len(exact_hour_events) == 1
    assert exact_hour_events[0][0] == 0x2000
    assert len(exact_hour_events[0][1]) == 33
    assert exact_hour_fallbacks == []
    assert len(backwards_events) == 1 and len(backwards_events[0][1]) == 33
    assert wrapping_events == [(0x2000, b"")]
    assert len(failed_queue_events) == 1
    assert failed_queue_fallbacks == [RECORD]
    assert null_storage_calls == []
    assert failed_append_calls == [(RECORD, 33)]
    assert failed_append_sync == []
    assert successful_append_calls == [(RECORD, 33)]
    assert successful_append_sync == [6]
    assert wrapping_append_calls == [(RECORD, 0)]

    return {
        "fixture_groups": 9,
        "initial_consumer": {
            "below_hour_events": len(below_hour_events),
            "exact_hour_event": [
                exact_hour_events[0][0], len(exact_hour_events[0][1])
            ],
            "backwards_timestamp_event_bytes": len(backwards_events[0][1]),
            "wrapping_count_event_bytes": len(wrapping_events[0][1]),
            "queue_failure_direct_fallback": failed_queue_fallbacks == [RECORD],
        },
        "storage_consumer": {
            "null_append_calls": len(null_storage_calls),
            "failed_append_sync_calls": len(failed_append_sync),
            "successful_append_length": successful_append_calls[0][1],
            "successful_sync_argument": successful_append_sync[0],
            "wrapping_append_length": wrapping_append_calls[0][1],
        },
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
