#!/usr/bin/env python3
"""Execute production SpO2 consumer, daily cache, offline FIFO, and merge in private RAM."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


CONSUMER = 0x0008A8AE
LATEST = 0x0005BAF4
LOCAL_HOUR = 0x0005ACA6
NOTIFICATION = 0x0008B138
RESET = 0x00090DD4
READ = 0x00090DF0
WRITE = 0x00090E4C
TIME_STATUS = 0x0008AD98
TIMESTAMP = 0x0008ADA4
QUEUE_EMPTY = 0x00043D90
QUEUE_ENQUEUE = 0x00043DA4
QUEUE_CONSUME = 0x00043CA0
QUEUE_MERGE = 0x000448B0
LOG_FLAGS = 0x000914EC

CACHE = 0x200165A0
CACHE_LENGTH = 0x54
ACCUMULATOR = 0x20016650
QUEUE_METADATA = 0x2000679B
QUEUE_STORAGE = 0x200158EC
ENTRY_LENGTH = 16
CAPACITY = 24

EVENT = RAM_BASE + 0x35000
SLOT_INPUT = RAM_BASE + 0x35100
SLOT_OUTPUT = RAM_BASE + 0x35200
LATEST_OUTPUT = RAM_BASE + 0x35300
BUILDER = RAM_BASE + 0x35400


def aggregate(raw: bytes, offset: int = 0) -> dict[str, int]:
    return {"average": raw[offset], "maximum": raw[offset + 1], "minimum": raw[offset + 2]}


def entry(raw: bytes) -> dict[str, Any]:
    day, timestamp = struct.unpack_from("<2I", raw, 4)
    offset, hour, tail = struct.unpack_from("<hBB", raw, 12)
    return {
        "aggregate": aggregate(raw),
        "reserved_after_aggregate": raw[3],
        "day_start": day,
        "recorded_timestamp": timestamp,
        "utc_offset_minutes": offset,
        "hour": hour,
        "reserved_tail": tail,
    }


class SpO2Fixture:
    def __init__(self, image: bytes, *, queue_fill: int = 0) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.time_status = 1
        self.timestamp_returns: list[int] = []
        self.timestamp_default = 1_000
        self.timestamp_calls = 0
        self.local_hour_returns: list[int] = []
        self.local_hour_calls = 0
        self.notifications: list[int] = []
        self.machine.uc.mem_write(CACHE, b"\x00" * CACHE_LENGTH)
        self.machine.uc.mem_write(ACCUMULATOR, b"\x00" * 8)
        self.machine.uc.mem_write(QUEUE_METADATA, b"\x00" * 3)
        self.machine.uc.mem_write(QUEUE_STORAGE, bytes([queue_fill]) * (CAPACITY * ENTRY_LENGTH))
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
            self.timestamp_calls += 1
            value = self.timestamp_returns.pop(0) if self.timestamp_returns else self.timestamp_default
            self._return(uc, value)
        elif address == LOCAL_HOUR:
            self.local_hour_calls += 1
            if not self.local_hour_returns:
                raise RuntimeError("unexpected local-hour call")
            self._return(uc, self.local_hour_returns.pop(0))
        elif address == NOTIFICATION:
            self.notifications.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc, 0)
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def metadata(self) -> dict[str, int]:
        read, write, count = bytes(self.machine.uc.mem_read(QUEUE_METADATA, 3))
        return {"read": read, "write": write, "count": count}

    def ordered_entries(self) -> list[dict[str, Any]]:
        metadata = self.metadata()
        result = []
        for position in range(metadata["count"]):
            index = (metadata["read"] + position) % CAPACITY
            raw = bytes(self.machine.uc.mem_read(QUEUE_STORAGE + index * ENTRY_LENGTH, ENTRY_LENGTH))
            result.append(entry(raw))
        return result

    def event(self, value: int, timestamp: int, *, aggregate_hour: int, average_hour: int) -> dict[str, Any]:
        self.timestamp_returns = [timestamp]
        self.local_hour_returns = [aggregate_hour, average_hour]
        prior_timestamp = self.timestamp_calls
        prior_hour = self.local_hour_calls
        self.machine.uc.mem_write(EVENT, bytes([value, 1, 2, 3, 4, 5, 6, 7]))
        self.machine.call(CONSUMER, EVENT)
        cache = bytes(self.machine.uc.mem_read(CACHE, CACHE_LENGTH))
        accumulator = bytes(self.machine.uc.mem_read(ACCUMULATOR, 8))
        available = self.machine.call(LATEST, LATEST_OUTPUT)
        return {
            "value": value,
            "timestamp": timestamp,
            "event_after_hex": bytes(self.machine.uc.mem_read(EVENT, 8)).hex(),
            "timestamp_calls": self.timestamp_calls - prior_timestamp,
            "local_hour_calls": self.local_hour_calls - prior_hour,
            "slot": aggregate(cache, aggregate_hour * 3),
            "accumulator": dict(zip(
                ("hour", "reserved", "count", "sum"),
                struct.unpack("<BBHI", accumulator),
            )),
            "latest_available": available,
            "latest_hex": bytes(self.machine.uc.mem_read(LATEST_OUTPUT, 5)).hex(),
            "notification": self.notifications[-1] if self.notifications else None,
        }

    def reset(self, day: int, offset: int) -> bytes:
        self.machine.call(RESET, day, offset & 0xFFFF)
        return bytes(self.machine.uc.mem_read(CACHE, CACHE_LENGTH))

    def write(self, index: int, values: tuple[int, int, int]) -> None:
        self.machine.uc.mem_write(SLOT_INPUT, bytes(values))
        self.machine.call(WRITE, index, SLOT_INPUT)

    def read(self, index: int, *, status: int, timestamps: list[int]) -> dict[str, Any]:
        self.time_status = status
        self.timestamp_returns = list(timestamps)
        prior = self.timestamp_calls
        self.machine.uc.mem_write(SLOT_OUTPUT, b"\x5a" * 3)
        self.machine.call(READ, index, SLOT_OUTPUT)
        return {
            "output": aggregate(bytes(self.machine.uc.mem_read(SLOT_OUTPUT, 3))),
            "timestamp_calls": self.timestamp_calls - prior,
            "metadata": self.metadata(),
            "entries": self.ordered_entries(),
        }

    def enqueue(
        self,
        values: tuple[int, int, int],
        *,
        day: int,
        timestamp: int,
        offset: int,
        hour: int,
        now: int = 1_000,
    ) -> None:
        self.machine.uc.mem_write(SLOT_INPUT, bytes(values))
        self.timestamp_returns = [now]
        self.machine.call(QUEUE_ENQUEUE, day, offset & 0xFFFF, hour, SLOT_INPUT, timestamp)

    def consume(self, cutoff: int) -> None:
        self.machine.call(QUEUE_CONSUME, cutoff)

    def merge(self, now: int) -> dict[str, Any]:
        self.machine.uc.mem_write(BUILDER, b"\x00" * 0x94)
        self.machine.uc.mem_write(BUILDER + 0x88, struct.pack("<H", 0x1234))
        self.machine.uc.mem_write(BUILDER + 0x8C, struct.pack("<I", 0))
        self.machine.uc.mem_write(BUILDER + 0x90, b"\x01")
        self.timestamp_returns = [now]
        self.machine.call(QUEUE_MERGE, BUILDER)
        raw = bytes(self.machine.uc.mem_read(BUILDER, 0x94))
        active = []
        for hour in range(24):
            if raw[hour]:
                offset = 0x18 + hour * 4
                active.append({"hour": raw[offset], **aggregate(raw, offset + 1)})
        return {
            "count": raw[0x78],
            "day_start": struct.unpack_from("<I", raw, 0x7C)[0],
            "utc_offset_minutes": struct.unpack_from("<h", raw, 0x80)[0],
            "maximum_recorded_timestamp": struct.unpack_from("<I", raw, 0x84)[0],
            "active_slots": active,
            "preserved_config_hex": raw[0x88:0x91].hex(),
        }


def run(image: bytes) -> dict[str, Any]:
    storage = SpO2Fixture(image)
    stored = storage.event(98, 0x12345678, aggregate_hour=4, average_hour=4)
    mismatch = SpO2Fixture(image).event(101, 9, aggregate_hour=5, average_hour=6)
    rejected = SpO2Fixture(image).event(69, 7, aggregate_hour=1, average_hour=1)

    reset_fixture = SpO2Fixture(image)
    reset_fixture.machine.uc.mem_write(CACHE, b"\xa5" * CACHE_LENGTH)
    reset_raw = reset_fixture.reset(0x01020304, -300)
    reset = {
        "slots_zero": reset_raw[:0x48] == b"\x00" * 0x48,
        "utc_offset_minutes": struct.unpack_from("<h", reset_raw, 0x48)[0],
        "preserved_4a_4f_hex": reset_raw[0x4A:0x50].hex(),
        "day_start": struct.unpack_from("<I", reset_raw, 0x50)[0],
    }

    reads = SpO2Fixture(image, queue_fill=0xA5)
    reads.reset(0, 120)
    reads.write(5, (96, 99, 93))
    valid = reads.read(5, status=1, timestamps=[])
    plausible = reads.read(5, status=0, timestamps=[946_080_001])
    queued = reads.read(5, status=0, timestamps=[1_000, 1_000, 1_000])

    negative = SpO2Fixture(image)
    negative.reset(0, -300)
    negative.write(5, (96, 99, 93))
    negative_read = negative.read(5, status=0, timestamps=[1_000])

    backward_gate = SpO2Fixture(image)
    backward_gate.reset(0, 120)
    backward_gate.write(5, (96, 99, 93))
    backward_validation = backward_gate.read(5, status=0, timestamps=[1_000, 999])

    backward_writer = SpO2Fixture(image)
    backward_writer.reset(0, 120)
    backward_writer.write(5, (96, 99, 93))
    backward_queue = backward_writer.read(5, status=0, timestamps=[1_000, 1_000, 999])

    zero_fixture = SpO2Fixture(image)
    zero_fixture.reset(0, 0)
    zero_fixture.write(6, (0, 100, 90))
    zero_average = zero_fixture.read(6, status=0, timestamps=[1_000])

    overflow = SpO2Fixture(image, queue_fill=0xA5)
    for value in range(1, 26):
        overflow.enqueue((value, value + 10, value), day=0, timestamp=value, offset=0, hour=value % 24)
    overflow_before = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
        "last_timestamp": overflow.ordered_entries()[-1]["recorded_timestamp"],
        "first_reserved": overflow.ordered_entries()[0]["reserved_after_aggregate"],
        "first_tail": overflow.ordered_entries()[0]["reserved_tail"],
    }
    overflow.consume(10)
    overflow_after = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
    }

    merge_fixture = SpO2Fixture(image)
    merge_fixture.enqueue((95, 97, 93), day=100, timestamp=101, offset=-300, hour=2)
    merge_fixture.enqueue((96, 98, 94), day=100, timestamp=102, offset=-300, hour=2)
    merge_fixture.enqueue((98, 100, 96), day=300, timestamp=999, offset=0, hour=4)
    merged = merge_fixture.merge(250)

    assert stored["event_after_hex"] == "6201020378563412"
    assert stored["timestamp_calls"] == 1 and stored["local_hour_calls"] == 2
    assert stored["slot"] == {"average": 98, "maximum": 98, "minimum": 98}
    assert stored["accumulator"] == {"hour": 4, "reserved": 0, "count": 1, "sum": 98}
    assert stored["latest_available"] == 1 and stored["latest_hex"] == "6278563412"
    assert stored["notification"] == 1
    assert mismatch["slot"]["average"] == 101 and mismatch["accumulator"]["hour"] == 6
    assert rejected["timestamp_calls"] == 0 and rejected["local_hour_calls"] == 0
    assert rejected["notification"] is None
    assert reset == {
        "slots_zero": True,
        "utc_offset_minutes": -300,
        "preserved_4a_4f_hex": "a5" * 6,
        "day_start": 0x01020304,
    }
    assert valid["output"] == {"average": 96, "maximum": 99, "minimum": 93}
    assert valid["timestamp_calls"] == 0
    assert plausible["output"] == valid["output"] and plausible["timestamp_calls"] == 1
    assert queued["output"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert queued["timestamp_calls"] == 3 and queued["metadata"]["count"] == 1
    assert queued["entries"][0] == {
        "aggregate": {"average": 96, "maximum": 99, "minimum": 93},
        "reserved_after_aggregate": 0xA5,
        "day_start": 0,
        "recorded_timestamp": 1_000,
        "utc_offset_minutes": 0,
        "hour": 3,
        "reserved_tail": 0xA5,
    }
    assert negative_read["output"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert negative_read["timestamp_calls"] == 1 and negative_read["metadata"]["count"] == 0
    assert backward_validation["timestamp_calls"] == 2 and backward_validation["metadata"]["count"] == 0
    assert backward_queue["timestamp_calls"] == 3 and backward_queue["metadata"]["count"] == 0
    assert zero_average["output"] == {"average": 0, "maximum": 100, "minimum": 90}
    assert overflow_before == {
        "metadata": {"read": 1, "write": 1, "count": 24},
        "first_timestamp": 2,
        "last_timestamp": 25,
        "first_reserved": 0xA5,
        "first_tail": 0xA5,
    }
    assert overflow_after == {
        "metadata": {"read": 10, "write": 1, "count": 15},
        "first_timestamp": 11,
    }
    assert overflow.machine.call(QUEUE_EMPTY) == 0
    assert merged["count"] == 1 and merged["day_start"] == 100
    assert merged["utc_offset_minutes"] == -300
    assert merged["maximum_recorded_timestamp"] == 102
    assert merged["active_slots"] == [{
        "hour": 2, "average": 96, "maximum": 98, "minimum": 94,
    }]
    assert merged["preserved_config_hex"] == "341200000000000001"

    return {
        "storage_accepted": stored,
        "storage_consumer_only_upper_value": mismatch,
        "storage_rejected_below_70": rejected,
        "reset": reset,
        "read_valid_clock": valid,
        "read_plausible_clock": plausible,
        "read_queued_and_redacted": queued,
        "read_negative_offset_redacted": negative_read,
        "read_backward_validation_redacted": backward_validation,
        "read_backward_queue_clock_redacted": backward_queue,
        "read_zero_average_returned": zero_average,
        "overflow_before_consume": overflow_before,
        "overflow_after_consume": overflow_after,
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
