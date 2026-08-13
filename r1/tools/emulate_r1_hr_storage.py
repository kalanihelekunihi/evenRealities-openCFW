#!/usr/bin/env python3
"""Execute production HR consumer, daily cache, offline FIFO, and merge in private RAM."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

import emulate_r1_spo2_storage as common


# The HR and SpO2 families use identical record geometry but distinct code and SRAM roots. Reuse
# only the private-RAM harness mechanics; every address below is independently version-pinned by
# summarize_r1_hr_storage.py.
common.CONSUMER = 0x0008A80A
common.LATEST = 0x0005ACE8
common.RESET = 0x0007062C
common.READ = 0x00070648
common.WRITE = 0x000706A4
common.QUEUE_EMPTY = 0x0003FB90
common.QUEUE_ENQUEUE = 0x0003FBA4
common.QUEUE_CONSUME = 0x0003FAA4
common.QUEUE_MERGE = 0x00040700
common.CACHE = 0x2001654C
common.ACCUMULATOR = 0x20016648
common.QUEUE_METADATA = 0x20006798
common.QUEUE_STORAGE = 0x2001576C


class HeartRateFixture(common.SpO2Fixture):
    def event(
        self,
        value: int,
        event_timestamp: int,
        *,
        firmware_timestamp: int,
        aggregate_hour: int,
        average_hour: int,
    ) -> dict[str, Any]:
        self.timestamp_returns = [firmware_timestamp]
        self.local_hour_returns = [aggregate_hour, average_hour]
        prior_timestamp = self.timestamp_calls
        prior_hour = self.local_hour_calls
        self.machine.uc.mem_write(
            common.EVENT,
            bytes([value, 1, 2, 3]) + struct.pack("<I", event_timestamp),
        )
        self.machine.call(common.CONSUMER, common.EVENT)
        cache = bytes(self.machine.uc.mem_read(common.CACHE, common.CACHE_LENGTH))
        accumulator = bytes(self.machine.uc.mem_read(common.ACCUMULATOR, 8))
        available = self.machine.call(common.LATEST, common.LATEST_OUTPUT)
        return {
            "value": value,
            "event_timestamp": event_timestamp,
            "firmware_timestamp": firmware_timestamp,
            "event_after_hex": bytes(self.machine.uc.mem_read(common.EVENT, 8)).hex(),
            "timestamp_calls": self.timestamp_calls - prior_timestamp,
            "local_hour_calls": self.local_hour_calls - prior_hour,
            "slot": common.aggregate(cache, aggregate_hour * 3),
            "accumulator": dict(zip(
                ("hour", "reserved", "count", "sum"),
                struct.unpack("<BBHI", accumulator),
            )),
            "latest_available": available,
            "latest_hex": bytes(self.machine.uc.mem_read(common.LATEST_OUTPUT, 5)).hex(),
            "notification": self.notifications[-1] if self.notifications else None,
        }


def run(image: bytes) -> dict[str, Any]:
    filled = HeartRateFixture(image).event(
        80,
        0,
        firmware_timestamp=0x12345678,
        aggregate_hour=4,
        average_hour=5,
    )
    preserved = HeartRateFixture(image).event(
        220,
        9,
        firmware_timestamp=10,
        aggregate_hour=6,
        average_hour=6,
    )
    rejected_low = HeartRateFixture(image).event(
        39,
        7,
        firmware_timestamp=10,
        aggregate_hour=1,
        average_hour=1,
    )
    rejected_high = HeartRateFixture(image).event(
        221,
        7,
        firmware_timestamp=10,
        aggregate_hour=1,
        average_hour=1,
    )

    reset_fixture = HeartRateFixture(image)
    reset_fixture.machine.uc.mem_write(common.CACHE, b"\xa5" * common.CACHE_LENGTH)
    reset_raw = reset_fixture.reset(0x01020304, -300)
    reset = {
        "slots_zero": reset_raw[:0x48] == b"\x00" * 0x48,
        "utc_offset_minutes": struct.unpack_from("<h", reset_raw, 0x48)[0],
        "preserved_4a_4f_hex": reset_raw[0x4A:0x50].hex(),
        "day_start": struct.unpack_from("<I", reset_raw, 0x50)[0],
    }

    reads = HeartRateFixture(image, queue_fill=0xA5)
    reads.reset(0, 120)
    reads.write(5, (80, 90, 70))
    valid = reads.read(5, status=1, timestamps=[])
    plausible = reads.read(5, status=0, timestamps=[946_080_001])
    queued = reads.read(5, status=0, timestamps=[1_000, 1_000, 1_000])

    negative = HeartRateFixture(image)
    negative.reset(0, -300)
    negative.write(5, (80, 90, 70))
    negative_read = negative.read(5, status=0, timestamps=[1_000])

    backward_gate = HeartRateFixture(image)
    backward_gate.reset(0, 120)
    backward_gate.write(5, (80, 90, 70))
    backward_validation = backward_gate.read(5, status=0, timestamps=[1_000, 999])

    backward_writer = HeartRateFixture(image)
    backward_writer.reset(0, 120)
    backward_writer.write(5, (80, 90, 70))
    backward_queue = backward_writer.read(5, status=0, timestamps=[1_000, 1_000, 999])

    zero_fixture = HeartRateFixture(image)
    zero_fixture.reset(0, 0)
    zero_fixture.write(6, (0, 100, 40))
    zero_average = zero_fixture.read(6, status=0, timestamps=[1_000])

    overflow = HeartRateFixture(image, queue_fill=0xA5)
    for value in range(1, 26):
        overflow.enqueue((value, value + 10, value), day=0, timestamp=value, offset=0,
                         hour=value % 24)
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

    merge_fixture = HeartRateFixture(image)
    merge_fixture.enqueue((75, 85, 65), day=100, timestamp=101, offset=-300, hour=2)
    merge_fixture.enqueue((80, 90, 70), day=100, timestamp=102, offset=-300, hour=2)
    merge_fixture.enqueue((98, 100, 96), day=300, timestamp=999, offset=0, hour=4)
    merged = merge_fixture.merge(250)

    assert filled["event_after_hex"] == "5001020378563412"
    assert filled["timestamp_calls"] == 1 and filled["local_hour_calls"] == 2
    assert filled["slot"] == {"average": 80, "maximum": 80, "minimum": 80}
    assert filled["accumulator"] == {"hour": 5, "reserved": 0, "count": 1, "sum": 80}
    assert filled["latest_available"] == 1 and filled["latest_hex"] == "5078563412"
    assert filled["notification"] == 0
    assert preserved["event_after_hex"] == "dc01020309000000"
    assert preserved["timestamp_calls"] == 0 and preserved["latest_hex"] == "dc09000000"
    for rejected in (rejected_low, rejected_high):
        assert rejected["timestamp_calls"] == 0 and rejected["local_hour_calls"] == 0
        assert rejected["notification"] is None
    assert reset == {
        "slots_zero": True,
        "utc_offset_minutes": -300,
        "preserved_4a_4f_hex": "a5" * 6,
        "day_start": 0x01020304,
    }
    assert valid["output"] == {"average": 80, "maximum": 90, "minimum": 70}
    assert valid["timestamp_calls"] == 0
    assert plausible["output"] == valid["output"] and plausible["timestamp_calls"] == 1
    assert queued["output"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert queued["timestamp_calls"] == 3 and queued["metadata"]["count"] == 1
    assert queued["entries"][0]["hour"] == 3
    assert queued["entries"][0]["reserved_after_aggregate"] == 0xA5
    assert queued["entries"][0]["reserved_tail"] == 0xA5
    assert negative_read["timestamp_calls"] == 1 and negative_read["metadata"]["count"] == 0
    assert backward_validation["timestamp_calls"] == 2
    assert backward_validation["metadata"]["count"] == 0
    assert backward_queue["timestamp_calls"] == 3 and backward_queue["metadata"]["count"] == 0
    assert zero_average["output"] == {"average": 0, "maximum": 100, "minimum": 40}
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
    assert overflow.machine.call(common.QUEUE_EMPTY) == 0
    assert merged["count"] == 1 and merged["day_start"] == 100
    assert merged["utc_offset_minutes"] == -300
    assert merged["maximum_recorded_timestamp"] == 102
    assert merged["active_slots"] == [{
        "hour": 2, "average": 80, "maximum": 90, "minimum": 70,
    }]

    return {
        "storage_zero_timestamp_filled": filled,
        "storage_nonzero_timestamp_preserved": preserved,
        "storage_rejected_below_40": rejected_low,
        "storage_rejected_above_220": rejected_high,
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
