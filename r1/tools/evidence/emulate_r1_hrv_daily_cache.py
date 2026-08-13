#!/usr/bin/env python3
"""Execute the production HRV daily callbacks and unsynced FIFO in private RAM.

Reset/read/write callbacks 0x706be/0x706d8/0x7073c, the nested early-clock gate, enqueue,
empty, consume, and queue-to-day-builder functions execute unchanged from the SHA-pinned image.
Only time/status and disabled diagnostics are deterministic hooks. No BLE, ring, sensor, flash, or
health-store interface is opened.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


RESET = 0x000706BE
READ = 0x000706D8
WRITE = 0x0007073C
TIME_STATUS = 0x0008AD98
TIMESTAMP = 0x0008ADA4
QUEUE_EMPTY = 0x00040A74
QUEUE_ENQUEUE = 0x00040A88
QUEUE_CONSUME = 0x00040984
QUEUE_MERGE = 0x00041638
LOG_FLAGS = 0x000914EC

CACHE = 0x200169C0
CACHE_LENGTH = 0xA0
QUEUE_METADATA = 0x200067AB
QUEUE_STORAGE = 0x2001636C
QUEUE_ENTRY_LENGTH = 20
QUEUE_CAPACITY = 24

SLOT_INPUT = RAM_BASE + 0x35000
SLOT_OUTPUT = RAM_BASE + 0x35100
BUILDER = RAM_BASE + 0x35200


def aggregate(raw: bytes, offset: int = 0) -> dict[str, int]:
    average, maximum, minimum = struct.unpack_from("<3H", raw, offset)
    return {"average": average, "maximum": maximum, "minimum": minimum}


def queue_entry(raw: bytes) -> dict[str, Any]:
    average, maximum, minimum = struct.unpack_from("<3H", raw)
    day, timestamp = struct.unpack_from("<2I", raw, 8)
    offset, hour, tail = struct.unpack_from("<hBB", raw, 16)
    return {
        "aggregate": {"average": average, "maximum": maximum, "minimum": minimum},
        "reserved_after_aggregate_hex": raw[6:8].hex(),
        "day_start": day,
        "recorded_timestamp": timestamp,
        "utc_offset_minutes": offset,
        "hour": hour,
        "reserved_tail": tail,
    }


class HRVDailyCacheFixture:
    def __init__(self, image: bytes, *, storage_fill: int = 0) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.time_status = 1
        self.timestamp_returns: list[int] = []
        self.timestamp_default = 1_000
        self.timestamp_call_count = 0
        self.machine.uc.mem_write(CACHE, b"\x00" * CACHE_LENGTH)
        self.machine.uc.mem_write(QUEUE_METADATA, b"\x00" * 3)
        self.machine.uc.mem_write(
            QUEUE_STORAGE,
            bytes([storage_fill]) * (QUEUE_CAPACITY * QUEUE_ENTRY_LENGTH),
        )
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == TIME_STATUS:
            self._return(uc, self.time_status)
        elif address == TIMESTAMP:
            self.timestamp_call_count += 1
            value = self.timestamp_returns.pop(0) if self.timestamp_returns else self.timestamp_default
            self._return(uc, value)
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def metadata(self) -> dict[str, int]:
        read, write, count = bytes(self.machine.uc.mem_read(QUEUE_METADATA, 3))
        return {"read": read, "write": write, "count": count}

    def ordered_entries(self) -> list[dict[str, Any]]:
        metadata = self.metadata()
        result = []
        for position in range(metadata["count"]):
            index = (metadata["read"] + position) % QUEUE_CAPACITY
            raw = bytes(self.machine.uc.mem_read(
                QUEUE_STORAGE + index * QUEUE_ENTRY_LENGTH,
                QUEUE_ENTRY_LENGTH,
            ))
            result.append(queue_entry(raw))
        return result

    def reset(self, day_start: int, utc_offset_minutes: int) -> bytes:
        self.machine.call(RESET, day_start, utc_offset_minutes & 0xFFFF)
        return bytes(self.machine.uc.mem_read(CACHE, CACHE_LENGTH))

    def write(self, index: int, values: tuple[int, int, int]) -> None:
        self.machine.uc.mem_write(SLOT_INPUT, struct.pack("<3H", *values))
        self.machine.call(WRITE, index, SLOT_INPUT)

    def read(
        self,
        index: int,
        *,
        status: int,
        timestamps: list[int],
    ) -> dict[str, Any]:
        self.time_status = status
        self.timestamp_returns = list(timestamps)
        prior_calls = self.timestamp_call_count
        self.machine.uc.mem_write(SLOT_OUTPUT, b"\x5a" * 6)
        self.machine.call(READ, index, SLOT_OUTPUT)
        return {
            "output": aggregate(bytes(self.machine.uc.mem_read(SLOT_OUTPUT, 6))),
            "timestamp_calls": self.timestamp_call_count - prior_calls,
            "unused_timestamp_returns": self.timestamp_returns,
            "metadata": self.metadata(),
            "entries": self.ordered_entries(),
        }

    def enqueue(
        self,
        values: tuple[int, int, int],
        *,
        day_start: int,
        timestamp: int,
        offset: int,
        hour: int,
        now: int = 1_000,
    ) -> None:
        self.machine.uc.mem_write(SLOT_INPUT, struct.pack("<3H", *values))
        self.timestamp_returns = [now]
        self.machine.call(
            QUEUE_ENQUEUE,
            day_start,
            offset & 0xFFFF,
            hour,
            SLOT_INPUT,
            timestamp,
        )

    def consume(self, cutoff: int) -> None:
        self.machine.call(QUEUE_CONSUME, cutoff)

    def merge(self, now: int) -> dict[str, Any]:
        self.machine.uc.mem_write(BUILDER, b"\x00" * 0xDC)
        self.machine.uc.mem_write(BUILDER + 0xD0, struct.pack("<H", 0x1234))
        self.machine.uc.mem_write(BUILDER + 0xD4, struct.pack("<I", 0))
        self.machine.uc.mem_write(BUILDER + 0xD8, b"\x01")
        self.timestamp_returns = [now]
        self.machine.call(QUEUE_MERGE, BUILDER)
        raw = bytes(self.machine.uc.mem_read(BUILDER, 0xDC))
        active = []
        for hour in range(24):
            if raw[hour]:
                offset = 0x18 + hour * 7
                active.append({"hour": raw[offset], **aggregate(raw, offset + 1)})
        return {
            "count": raw[0xC0],
            "day_start": struct.unpack_from("<I", raw, 0xC4)[0],
            "utc_offset_minutes": struct.unpack_from("<h", raw, 0xC8)[0],
            "maximum_recorded_timestamp": struct.unpack_from("<I", raw, 0xCC)[0],
            "active_slots": active,
            "preserved_config_hex": raw[0xD0:0xD9].hex(),
        }


def run(image: bytes) -> dict[str, Any]:
    reset_fixture = HRVDailyCacheFixture(image)
    reset_fixture.machine.uc.mem_write(CACHE, b"\xa5" * CACHE_LENGTH)
    reset_raw = reset_fixture.reset(0x01020304, -300)
    reset = {
        "slots_zero": reset_raw[:0x90] == b"\x00" * 0x90,
        "utc_offset_minutes": struct.unpack_from("<h", reset_raw, 0x90)[0],
        "preserved_92_9b_hex": reset_raw[0x92:0x9C].hex(),
        "day_start": struct.unpack_from("<I", reset_raw, 0x9C)[0],
    }

    reads = HRVDailyCacheFixture(image, storage_fill=0xA5)
    reads.reset(0, 120)
    reads.write(5, (70, 82, 60))
    valid = reads.read(5, status=1, timestamps=[])
    plausible = reads.read(5, status=0, timestamps=[946_080_001])
    queued = reads.read(5, status=0, timestamps=[1_000, 1_000, 1_000])

    negative = HRVDailyCacheFixture(image)
    negative.reset(0, -300)
    negative.write(5, (70, 82, 60))
    negative_offset = negative.read(5, status=0, timestamps=[1_000])

    backward_gate = HRVDailyCacheFixture(image)
    backward_gate.reset(0, 120)
    backward_gate.write(5, (70, 82, 60))
    backward_validation = backward_gate.read(5, status=0, timestamps=[1_000, 999])

    backward_writer = HRVDailyCacheFixture(image)
    backward_writer.reset(0, 120)
    backward_writer.write(5, (70, 82, 60))
    backward_queue = backward_writer.read(5, status=0, timestamps=[1_000, 1_000, 999])

    zero_average_fixture = HRVDailyCacheFixture(image)
    zero_average_fixture.reset(0, 0)
    zero_average_fixture.write(6, (0, 100, 50))
    zero_average = zero_average_fixture.read(6, status=0, timestamps=[1_000])

    overflow = HRVDailyCacheFixture(image, storage_fill=0xA5)
    for value in range(1, 26):
        overflow.enqueue(
            (value, value + 10, value),
            day_start=0,
            timestamp=value,
            offset=0,
            hour=value % 24,
        )
    overflow_before_consume = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
        "last_timestamp": overflow.ordered_entries()[-1]["recorded_timestamp"],
        "first_reserved_hex": overflow.ordered_entries()[0]["reserved_after_aggregate_hex"],
    }
    overflow.consume(10)
    overflow_after_consume = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
    }

    merge_fixture = HRVDailyCacheFixture(image)
    merge_fixture.enqueue((10, 15, 9), day_start=100, timestamp=101, offset=-300, hour=2)
    merge_fixture.enqueue((11, 16, 10), day_start=100, timestamp=102, offset=-300, hour=2)
    merge_fixture.enqueue((13, 18, 12), day_start=300, timestamp=999, offset=0, hour=4)
    merged = merge_fixture.merge(250)

    assert reset == {
        "slots_zero": True,
        "utc_offset_minutes": -300,
        "preserved_92_9b_hex": "a5" * 10,
        "day_start": 0x01020304,
    }
    assert valid["output"] == {"average": 70, "maximum": 82, "minimum": 60}
    assert valid["timestamp_calls"] == 0
    assert plausible["output"] == valid["output"] and plausible["timestamp_calls"] == 1
    assert queued["output"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert queued["timestamp_calls"] == 3 and queued["metadata"]["count"] == 1
    assert queued["entries"][0] == {
        "aggregate": {"average": 70, "maximum": 82, "minimum": 60},
        "reserved_after_aggregate_hex": "a5a5",
        "day_start": 0,
        "recorded_timestamp": 1_000,
        "utc_offset_minutes": 0,
        "hour": 3,
        "reserved_tail": 0xA5,
    }
    assert negative_offset["output"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert negative_offset["timestamp_calls"] == 1
    assert negative_offset["metadata"]["count"] == 0
    assert backward_validation["timestamp_calls"] == 2
    assert backward_validation["metadata"]["count"] == 0
    assert backward_queue["timestamp_calls"] == 3
    assert backward_queue["metadata"]["count"] == 0
    assert zero_average["output"] == {"average": 0, "maximum": 100, "minimum": 50}
    assert zero_average["timestamp_calls"] == 1
    assert overflow_before_consume == {
        "metadata": {"read": 1, "write": 1, "count": 24},
        "first_timestamp": 2,
        "last_timestamp": 25,
        "first_reserved_hex": "a5a5",
    }
    assert overflow_after_consume == {
        "metadata": {"read": 10, "write": 1, "count": 15},
        "first_timestamp": 11,
    }
    assert overflow.machine.call(QUEUE_EMPTY) == 0
    assert merged["count"] == 1
    assert merged["day_start"] == 100
    assert merged["utc_offset_minutes"] == -300
    assert merged["maximum_recorded_timestamp"] == 102
    assert merged["active_slots"] == [{
        "hour": 2, "average": 11, "maximum": 16, "minimum": 10,
    }]
    assert merged["preserved_config_hex"] == "341200000000000001"

    return {
        "reset": reset,
        "read_valid_clock": valid,
        "read_plausible_clock": plausible,
        "read_queued_and_redacted": queued,
        "read_negative_offset_redacted": negative_offset,
        "read_backward_validation_redacted": backward_validation,
        "read_backward_queue_clock_redacted": backward_queue,
        "read_zero_average_returned": zero_average,
        "overflow_before_consume": overflow_before_consume,
        "overflow_after_consume": overflow_after_consume,
        "queue_merge": merged,
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
