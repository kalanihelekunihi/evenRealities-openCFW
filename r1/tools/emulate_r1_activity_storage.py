#!/usr/bin/env python3
"""Execute production activity cache/FIFO callbacks in private emulated RAM.

No BLE stack, physical ring, sensor, flash partition, or host health store is present.
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


ACCUMULATE = 0x0005AA14
BUCKET_RESOLVER = 0x0005AC74
RESET = 0x00048288
READ = 0x000482A8
WRITE = 0x0004832C
TIME_STATUS = 0x0008AD98
TIMESTAMP = 0x0008ADA4
QUEUE_EMPTY = 0x0003BED0
QUEUE_ENQUEUE = 0x0003BEE4
QUEUE_CONSUME = 0x0003BDD8
QUEUE_MERGE = 0x0003CB80
LOG_FLAGS = 0x000914EC

CACHE = 0x200166C4
CACHE_LENGTH = 0x248
QUEUE_METADATA = 0x200067A8
QUEUE_STORAGE = 0x20015A6C
ENTRY_LENGTH = 16
CAPACITY = 144

EVENT = RAM_BASE + 0x35000
SLOT_INPUT = RAM_BASE + 0x35100
SLOT_OUTPUT = RAM_BASE + 0x35200
BUCKET_INPUT = RAM_BASE + 0x35300
BUILDER = RAM_BASE + 0x35400


def unpack_bucket(packed: int, index: int) -> dict[str, int]:
    return {
        "index": index,
        "steps": packed & 0xFFF,
        "active_kcal": (packed >> 12) & 0x3FF,
        "all_kcal": (packed >> 22) & 0x3FF,
        "packed": packed,
    }


def queue_entry(raw: bytes) -> dict[str, Any]:
    packed, day, timestamp = struct.unpack_from("<III", raw)
    offset, index, tail = struct.unpack_from("<hBB", raw, 12)
    return {
        "bucket": unpack_bucket(packed, index),
        "day_start": day,
        "recorded_timestamp": timestamp,
        "utc_offset_minutes": offset,
        "reserved_tail": tail,
    }


class ActivityFixture:
    def __init__(self, image: bytes, *, queue_fill: int = 0) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.time_status = 1
        self.timestamp_returns: list[int] = []
        self.timestamp_default = 1_000
        self.timestamp_calls = 0
        self.bucket_returns: list[int] = []
        self.bucket_calls = 0
        self.machine.uc.mem_write(CACHE, b"\x00" * CACHE_LENGTH)
        self.machine.uc.mem_write(QUEUE_METADATA, b"\x00" * 3)
        self.machine.uc.mem_write(
            QUEUE_STORAGE, bytes([queue_fill]) * (CAPACITY * ENTRY_LENGTH)
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
            self.timestamp_calls += 1
            value = (
                self.timestamp_returns.pop(0)
                if self.timestamp_returns
                else self.timestamp_default
            )
            self._return(uc, value)
        elif address == BUCKET_RESOLVER:
            self.bucket_calls += 1
            if not self.bucket_returns:
                raise RuntimeError("unexpected ten-minute-bucket resolver call")
            self._return(uc, self.bucket_returns.pop(0))
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
            raw = bytes(
                self.machine.uc.mem_read(
                    QUEUE_STORAGE + index * ENTRY_LENGTH, ENTRY_LENGTH
                )
            )
            result.append(queue_entry(raw))
        return result

    def cache_bucket(self, index: int) -> dict[str, int]:
        packed = struct.unpack(
            "<I", bytes(self.machine.uc.mem_read(CACHE + index * 4, 4))
        )[0]
        return unpack_bucket(packed, index)

    def accumulate(
        self,
        *,
        all_kcal: int,
        active_kcal: int,
        steps: int,
        duration: int,
        timestamp: int,
        start_bucket: int,
        end_bucket: int,
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(
            EVENT,
            struct.pack("<4HI", all_kcal, active_kcal, steps, duration, timestamp),
        )
        self.bucket_returns = [start_bucket, end_bucket]
        before = self.bucket_calls
        self.machine.call(ACCUMULATE, EVENT)
        return {
            "event_hex": bytes(self.machine.uc.mem_read(EVENT, 12)).hex(),
            "bucket_calls": self.bucket_calls - before,
            "start_bucket": self.cache_bucket(start_bucket),
            "end_bucket": self.cache_bucket(end_bucket),
            "crossed_boundary": start_bucket != end_bucket,
        }

    def reset(self, day: int, offset: int) -> bytes:
        self.machine.call(RESET, day, offset & 0xFFFF)
        return bytes(self.machine.uc.mem_read(CACHE, CACHE_LENGTH))

    def write_hour(self, hour: int, words: list[int]) -> None:
        if len(words) != 6:
            raise ValueError("an activity hour requires six packed words")
        self.machine.uc.mem_write(SLOT_INPUT, struct.pack("<6I", *words))
        self.machine.call(WRITE, hour, SLOT_INPUT)

    def read_hour(
        self, hour: int, *, status: int, timestamps: list[int]
    ) -> dict[str, Any]:
        self.time_status = status
        self.timestamp_returns = list(timestamps)
        before = self.timestamp_calls
        self.machine.uc.mem_write(SLOT_OUTPUT, b"\x5a" * 24)
        self.machine.call(READ, hour, SLOT_OUTPUT)
        words = struct.unpack("<6I", bytes(self.machine.uc.mem_read(SLOT_OUTPUT, 24)))
        return {
            "words": list(words),
            "timestamp_calls": self.timestamp_calls - before,
            "metadata": self.metadata(),
            "entries": self.ordered_entries(),
        }

    def enqueue(
        self,
        packed: int,
        *,
        day: int,
        timestamp: int,
        offset: int,
        index: int,
        now: int,
    ) -> None:
        self.machine.uc.mem_write(BUCKET_INPUT, struct.pack("<I", packed))
        self.timestamp_returns = [now]
        self.machine.call(
            QUEUE_ENQUEUE,
            day,
            offset & 0xFFFF,
            index,
            BUCKET_INPUT,
            timestamp,
        )

    def consume(self, cutoff: int) -> None:
        self.machine.call(QUEUE_CONSUME, cutoff)

    def merge(self, now: int) -> dict[str, Any]:
        self.machine.uc.mem_write(BUILDER, b"\x00" * 0x49C)
        self.machine.uc.mem_write(BUILDER + 0x490, struct.pack("<H", 0x1234))
        self.machine.uc.mem_write(BUILDER + 0x494, struct.pack("<I", 0x55667788))
        self.machine.uc.mem_write(BUILDER + 0x498, b"\x01")
        self.timestamp_returns = [now]
        self.machine.call(QUEUE_MERGE, BUILDER)
        raw = bytes(self.machine.uc.mem_read(BUILDER, 0x49C))
        active = []
        for index in range(144):
            if raw[index]:
                item_offset = 0x90 + index * 7
                bucket_index, steps, active_kcal, all_kcal = struct.unpack_from(
                    "<BHHH", raw, item_offset
                )
                active.append({
                    "index": bucket_index,
                    "steps": steps,
                    "active_kcal": active_kcal,
                    "all_kcal": all_kcal,
                })
        return {
            "count": raw[0x480],
            "day_start": struct.unpack_from("<I", raw, 0x484)[0],
            "utc_offset_minutes": struct.unpack_from("<h", raw, 0x488)[0],
            "maximum_recorded_timestamp": struct.unpack_from("<I", raw, 0x48C)[0],
            "active_buckets": active,
            "preserved_context": struct.unpack_from("<H", raw, 0x490)[0],
            "preserved_ack_pointer": struct.unpack_from("<I", raw, 0x494)[0],
            "preserved_mode": raw[0x498],
        }


def packed(steps: int, active_kcal: int, all_kcal: int) -> int:
    return (steps & 0xFFF) | ((active_kcal & 0x3FF) << 12) | ((all_kcal & 0x3FF) << 22)


def run(image: bytes) -> dict[str, Any]:
    producer = ActivityFixture(image)
    ordinary = producer.accumulate(
        all_kcal=3,
        active_kcal=2,
        steps=100,
        duration=601,
        timestamp=0x12345678,
        start_bucket=5,
        end_bucket=6,
    )
    wrapped = producer.accumulate(
        all_kcal=1_021,
        active_kcal=1_022,
        steps=3_996,
        duration=1,
        timestamp=1,
        start_bucket=5,
        end_bucket=5,
    )

    reset_fixture = ActivityFixture(image)
    reset_fixture.machine.uc.mem_write(CACHE, b"\xa5" * CACHE_LENGTH)
    reset_raw = reset_fixture.reset(0x01020304, -300)
    reset = {
        "slots_zero": reset_raw[:0x240] == b"\x00" * 0x240,
        "utc_offset_minutes": struct.unpack_from("<h", reset_raw, 0x240)[0],
        "preserved_reserved_hex": reset_raw[0x242:0x244].hex(),
        "day_start": struct.unpack_from("<I", reset_raw, 0x244)[0],
    }

    first = packed(12, 34, 56)
    second = packed(78, 90, 12)
    reads = ActivityFixture(image, queue_fill=0xA5)
    reads.reset(0, 120)
    reads.write_hour(5, [first, 0, second, 0, 0, 0])
    valid = reads.read_hour(5, status=1, timestamps=[])
    plausible = reads.read_hour(5, status=0, timestamps=[946_080_001])
    queued = reads.read_hour(
        5, status=0, timestamps=[1_000, 1_000, 1_000, 1_000]
    )

    negative = ActivityFixture(image)
    negative.reset(0, -300)
    negative.write_hour(5, [first, 0, second, 0, 0, 0])
    negative_read = negative.read_hour(5, status=0, timestamps=[1_000])

    backward_gate = ActivityFixture(image)
    backward_gate.reset(0, 120)
    backward_gate.write_hour(5, [first, 0, second, 0, 0, 0])
    backward_validation = backward_gate.read_hour(
        5, status=0, timestamps=[1_000, 999]
    )

    backward_queue = ActivityFixture(image)
    backward_queue.reset(0, 120)
    backward_queue.write_hour(5, [first, 0, second, 0, 0, 0])
    backward_enqueue = backward_queue.read_hour(
        5, status=0, timestamps=[1_000, 1_000, 999, 999]
    )

    overflow = ActivityFixture(image, queue_fill=0xA5)
    for value in range(1, 146):
        overflow.enqueue(
            value,
            day=0,
            timestamp=value,
            offset=0,
            index=value % 144,
            now=value,
        )
    overflow_before = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
        "last_timestamp": overflow.ordered_entries()[-1]["recorded_timestamp"],
        "first_reserved_tail": overflow.ordered_entries()[0]["reserved_tail"],
    }
    overflow.consume(10)
    overflow_after = {
        "metadata": overflow.metadata(),
        "first_timestamp": overflow.ordered_entries()[0]["recorded_timestamp"],
    }

    merge_fixture = ActivityFixture(image)
    merge_fixture.enqueue(
        first, day=100, timestamp=101, offset=-300, index=2, now=1_000
    )
    merge_fixture.enqueue(
        second, day=100, timestamp=102, offset=-300, index=2, now=1_000
    )
    merge_fixture.enqueue(
        first, day=300, timestamp=999, offset=0, index=4, now=1_000
    )
    merged = merge_fixture.merge(250)

    assert ordinary["event_hex"] == "030002006400590278563412"
    assert ordinary["bucket_calls"] == 2 and ordinary["crossed_boundary"]
    assert ordinary["start_bucket"] == unpack_bucket(packed(100, 2, 3), 5)
    assert ordinary["end_bucket"] == unpack_bucket(0, 6)
    assert wrapped["start_bucket"] == unpack_bucket(0, 5)
    assert reset == {
        "slots_zero": True,
        "utc_offset_minutes": -300,
        "preserved_reserved_hex": "a5a5",
        "day_start": 0x01020304,
    }
    assert valid["words"] == [first, 0, second, 0, 0, 0]
    assert valid["timestamp_calls"] == 0
    assert plausible["words"] == valid["words"] and plausible["timestamp_calls"] == 1
    assert queued["words"] == [0] * 6 and queued["timestamp_calls"] == 4
    assert queued["metadata"] == {"read": 0, "write": 2, "count": 2}
    assert [item["bucket"]["index"] for item in queued["entries"]] == [18, 20]
    assert [item["bucket"]["packed"] for item in queued["entries"]] == [first, second]
    assert all(item["reserved_tail"] == 0xA5 for item in queued["entries"])
    assert negative_read["words"] == [0] * 6
    assert negative_read["timestamp_calls"] == 1
    assert negative_read["metadata"]["count"] == 0
    assert backward_validation["timestamp_calls"] == 2
    assert backward_validation["metadata"]["count"] == 0
    assert backward_enqueue["timestamp_calls"] == 4
    assert backward_enqueue["metadata"]["count"] == 0
    assert overflow_before == {
        "metadata": {"read": 1, "write": 1, "count": 144},
        "first_timestamp": 2,
        "last_timestamp": 145,
        "first_reserved_tail": 0xA5,
    }
    assert overflow_after == {
        "metadata": {"read": 10, "write": 1, "count": 135},
        "first_timestamp": 11,
    }
    assert overflow.machine.call(QUEUE_EMPTY) == 0
    assert merged == {
        "count": 1,
        "day_start": 100,
        "utc_offset_minutes": -300,
        "maximum_recorded_timestamp": 102,
        "active_buckets": [{
            "index": 2,
            "steps": 78,
            "active_kcal": 90,
            "all_kcal": 12,
        }],
        "preserved_context": 0x1234,
        "preserved_ack_pointer": 0x55667788,
        "preserved_mode": 1,
    }

    return {
        "delta_cross_bucket_uses_start": ordinary,
        "independent_field_wrap": wrapped,
        "reset": reset,
        "read_valid_clock": valid,
        "read_plausible_clock": plausible,
        "read_queued_and_redacted": queued,
        "read_negative_offset_redacted": negative_read,
        "read_backward_validation_redacted": backward_validation,
        "read_backward_queue_clock_redacted": backward_enqueue,
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
