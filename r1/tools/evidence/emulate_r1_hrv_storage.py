#!/usr/bin/env python3
"""Execute the production R1 HRV point consumer and hourly aggregator in private RAM.

Only the timestamp, local-hour provider, storage-notification callback, and diagnostics are
replaced with bounded deterministic hooks. Consumer 0x8a83e, aggregator 0x5af60, rolling-average
helper 0x5aba0, and latest-point accessor 0x5af20 execute from the SHA-pinned firmware unchanged.
The fixture never connects to BLE, sensors, health storage, or a physical ring.
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


CONSUMER = 0x0008A83E
AGGREGATOR = 0x0005AF60
LOCAL_HOUR = 0x0005ACA6
TIMESTAMP = 0x0008ADA4
STORAGE_NOTIFICATION = 0x0008B138
LOG_FLAGS = 0x000914EC
LATEST_POINT = 0x0005AF20

ROLLING_AVERAGE_ARRAY = 0x20016648
ROLLING_AVERAGE = ROLLING_AVERAGE_ARRAY + 5 * 8
HOURLY_CACHE = 0x200169C0
HOURLY_CACHE_LENGTH = 0xA0
EVENT = RAM_BASE + 0x35000
LATEST_OUTPUT = RAM_BASE + 0x35100


def decode_slot(raw: bytes, index: int) -> dict[str, int]:
    average, maximum, minimum = struct.unpack_from("<3H", raw, index * 6)
    return {
        "slot_index": index,
        "average": average,
        "maximum": maximum,
        "minimum": minimum,
    }


class HRVStorageFixture:
    def __init__(self, image: bytes, *, firmware_timestamp: int = 0x12345678) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.firmware_timestamp = firmware_timestamp
        self.local_hour_returns: list[int] = []
        self.local_hour_call_count = 0
        self.timestamp_call_count = 0
        self.storage_notifications: list[int] = []
        self.machine.uc.mem_write(HOURLY_CACHE, b"\x00" * HOURLY_CACHE_LENGTH)
        self.machine.uc.mem_write(ROLLING_AVERAGE, b"\x00" * 8)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOCAL_HOUR:
            if not self.local_hour_returns:
                raise RuntimeError("unexpected local-hour helper call")
            self.local_hour_call_count += 1
            self._return(uc, self.local_hour_returns.pop(0))
        elif address == TIMESTAMP:
            self.timestamp_call_count += 1
            self._return(uc, self.firmware_timestamp)
        elif address == STORAGE_NOTIFICATION:
            self.storage_notifications.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc, 0)
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def set_accumulator(
        self,
        *,
        slot: int,
        count: int,
        total: int,
        reserved: int = 0,
    ) -> None:
        self.machine.uc.mem_write(
            ROLLING_AVERAGE,
            struct.pack("<BBHI", slot, reserved, count, total),
        )

    def event(
        self,
        rmssd: int,
        timestamp: int,
        *,
        aggregate_slot: int,
        average_slot: int | None = None,
        reserved: int = 0xA55A,
    ) -> dict[str, Any]:
        if not 0 <= rmssd <= 0xFFFF or not 0 <= timestamp <= 0xFFFFFFFF:
            raise ValueError("point fields must fit their firmware integers")
        average_slot = aggregate_slot if average_slot is None else average_slot
        if not 0 <= aggregate_slot <= 0xFF or not 0 <= average_slot <= 0xFF:
            raise ValueError("slot hook values must fit UInt8")
        self.local_hour_returns = [aggregate_slot, average_slot]
        prior_hour_calls = self.local_hour_call_count
        prior_timestamp_calls = self.timestamp_call_count
        self.machine.uc.mem_write(EVENT, struct.pack("<HHI", rmssd, reserved, timestamp))
        self.machine.call(CONSUMER, EVENT)
        if self.local_hour_returns:
            raise RuntimeError("production path did not consume both local-hour values")
        cache = bytes(self.machine.uc.mem_read(HOURLY_CACHE, HOURLY_CACHE_LENGTH))
        accumulator = bytes(self.machine.uc.mem_read(ROLLING_AVERAGE, 8))
        event_after = bytes(self.machine.uc.mem_read(EVENT, 8))
        accumulator_slot, accumulator_reserved, count, total = struct.unpack(
            "<BBHI", accumulator
        )
        return {
            "input": {
                "rmssd": rmssd,
                "reserved": reserved,
                "timestamp": timestamp,
                "aggregate_slot": aggregate_slot,
                "average_slot": average_slot,
            },
            "event_after_hex": event_after.hex(),
            "effective_timestamp": struct.unpack_from("<I", event_after, 4)[0],
            "timestamp_helper_calls": self.timestamp_call_count - prior_timestamp_calls,
            "local_hour_helper_calls": self.local_hour_call_count - prior_hour_calls,
            "aggregate_slot": decode_slot(cache, aggregate_slot),
            "rolling_accumulator": {
                "slot": accumulator_slot,
                "reserved": accumulator_reserved,
                "count": count,
                "sum": total,
            },
            "latest_point_hex": cache[0x93:0x99].hex(),
            "notification": self.storage_notifications[-1],
        }

    def latest(self) -> dict[str, Any]:
        self.machine.uc.mem_write(LATEST_OUTPUT, b"\xA5" * 6)
        available = self.machine.call(LATEST_POINT, LATEST_OUTPUT)
        return {
            "available": available,
            "output_hex": bytes(self.machine.uc.mem_read(LATEST_OUTPUT, 6)).hex(),
        }

    def null_aggregate_is_noop(self) -> bool:
        cache_before = bytes(self.machine.uc.mem_read(HOURLY_CACHE, HOURLY_CACHE_LENGTH))
        average_before = bytes(self.machine.uc.mem_read(ROLLING_AVERAGE, 8))
        self.machine.call(AGGREGATOR, 0)
        return (
            cache_before
            == bytes(self.machine.uc.mem_read(HOURLY_CACHE, HOURLY_CACHE_LENGTH))
            and average_before == bytes(self.machine.uc.mem_read(ROLLING_AVERAGE, 8))
        )


def run(image: bytes) -> dict[str, Any]:
    zero_timestamp = HRVStorageFixture(image)
    filled = zero_timestamp.event(80, 0, aggregate_slot=4, reserved=0xBEEF)
    filled_latest = zero_timestamp.latest()

    preserved_timestamp = HRVStorageFixture(image)
    preserved = preserved_timestamp.event(90, 0x01020304, aggregate_slot=5)

    same_hour = HRVStorageFixture(image)
    same_hour_updates = [
        same_hour.event(value, 0x1000 + index, aggregate_slot=6)
        for index, value in enumerate((70, 71, 72))
    ]

    changed_hour = same_hour.event(90, 0x2000, aggregate_slot=7)

    mismatched_hour_helpers = HRVStorageFixture(image)
    mismatch = mismatched_hour_helpers.event(
        100,
        0x3000,
        aggregate_slot=2,
        average_slot=3,
    )

    zero_sentinel = HRVStorageFixture(image)
    zero_sentinel_updates = [
        zero_sentinel.event(value, 0x4000 + index, aggregate_slot=8)
        for index, value in enumerate((0, 50, 0, 40))
    ]
    zero_latest = HRVStorageFixture(image)
    zero_latest.event(0, 0x5000, aggregate_slot=9)
    zero_latest_accessor = zero_latest.latest()

    count_wrap_infinity = HRVStorageFixture(image)
    count_wrap_infinity.set_accumulator(slot=10, count=0xFFFF, total=0)
    wrap_infinity = count_wrap_infinity.event(1, 0x6000, aggregate_slot=10)

    count_and_sum_wrap_nan = HRVStorageFixture(image)
    count_and_sum_wrap_nan.set_accumulator(slot=11, count=0xFFFF, total=0xFFFFFFFF)
    wrap_nan = count_and_sum_wrap_nan.event(1, 0x7000, aggregate_slot=11)

    null_fixture = HRVStorageFixture(image)
    null_noop = null_fixture.null_aggregate_is_noop()

    assert filled["event_after_hex"] == "5000efbe78563412"
    assert filled["timestamp_helper_calls"] == 1
    assert filled["local_hour_helper_calls"] == 2
    assert filled["aggregate_slot"] == {
        "slot_index": 4,
        "average": 80,
        "maximum": 80,
        "minimum": 80,
    }
    assert filled_latest == {"available": 1, "output_hex": "500078563412"}
    assert preserved["event_after_hex"] == "5a005aa504030201"
    assert preserved["timestamp_helper_calls"] == 0
    assert [item["aggregate_slot"]["average"] for item in same_hour_updates] == [70, 70, 71]
    assert same_hour_updates[-1]["aggregate_slot"] == {
        "slot_index": 6,
        "average": 71,
        "maximum": 72,
        "minimum": 70,
    }
    assert changed_hour["aggregate_slot"] == {
        "slot_index": 7,
        "average": 90,
        "maximum": 90,
        "minimum": 90,
    }
    assert mismatch["rolling_accumulator"] == {
        "slot": 3,
        "reserved": 0,
        "count": 1,
        "sum": 100,
    }
    assert mismatch["aggregate_slot"]["slot_index"] == 2
    assert mismatch["aggregate_slot"]["average"] == 100
    assert [item["aggregate_slot"]["minimum"] for item in zero_sentinel_updates] == [0, 50, 0, 40]
    assert zero_sentinel_updates[-1]["aggregate_slot"] == {
        "slot_index": 8,
        "average": 22,
        "maximum": 50,
        "minimum": 40,
    }
    assert zero_latest_accessor == {"available": 0, "output_hex": "a5a5a5a5a5a5"}
    assert wrap_infinity["aggregate_slot"]["average"] == 0xFFFF
    assert wrap_infinity["rolling_accumulator"]["count"] == 0
    assert wrap_infinity["rolling_accumulator"]["sum"] == 1
    assert wrap_nan["aggregate_slot"]["average"] == 0
    assert wrap_nan["rolling_accumulator"]["count"] == 0
    assert wrap_nan["rolling_accumulator"]["sum"] == 0
    assert all(item["notification"] == 5 for item in (
        filled,
        preserved,
        *same_hour_updates,
        changed_hour,
        mismatch,
        *zero_sentinel_updates,
        wrap_infinity,
        wrap_nan,
    ))
    assert null_noop

    return {
        "zero_timestamp": filled,
        "zero_timestamp_latest_accessor": filled_latest,
        "preserved_timestamp": preserved,
        "same_hour_updates": same_hour_updates,
        "changed_hour": changed_hour,
        "mismatched_hour_helpers": mismatch,
        "zero_minimum_sentinel_updates": zero_sentinel_updates,
        "zero_rmssd_latest_accessor": zero_latest_accessor,
        "count_wrap_positive_infinity": wrap_infinity,
        "count_and_sum_wrap_nan": wrap_nan,
        "null_aggregate_is_noop": null_noop,
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
