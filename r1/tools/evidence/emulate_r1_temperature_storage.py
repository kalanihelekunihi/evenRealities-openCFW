#!/usr/bin/env python3
"""Execute the hidden production temperature cache and daily callbacks in private RAM."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

import emulate_r1_spo2_storage as common


common.CONSUMER = 0x0008A8FC
common.RESET = 0x000918DE
common.READ = 0x00091918
common.WRITE = 0x00091954
common.CACHE = 0x200165F4
common.ACCUMULATOR = 0x20016658


class TemperatureFixture(common.SpO2Fixture):
    def event(
        self,
        published: int,
        firmware_timestamp: int,
        *,
        aggregate_hour: int,
        average_hour: int,
    ) -> dict[str, Any]:
        self.timestamp_returns = [firmware_timestamp]
        self.local_hour_returns = [aggregate_hour, average_hour]
        prior_timestamp = self.timestamp_calls
        prior_hour = self.local_hour_calls
        self.machine.uc.mem_write(
            common.EVENT,
            struct.pack("<H", published) + b"\xa1\xa2\x01\x02\x03\x04",
        )
        self.machine.call(common.CONSUMER, common.EVENT)
        cache = bytes(self.machine.uc.mem_read(common.CACHE, common.CACHE_LENGTH))
        accumulator = bytes(self.machine.uc.mem_read(common.ACCUMULATOR, 8))
        return {
            "published_raw": published,
            "event_after_hex": bytes(self.machine.uc.mem_read(common.EVENT, 8)).hex(),
            "timestamp_calls": self.timestamp_calls - prior_timestamp,
            "local_hour_calls": self.local_hour_calls - prior_hour,
            "slot_stored_offsets": common.aggregate(cache, aggregate_hour * 3),
            "accumulator": dict(zip(
                ("hour", "reserved", "count", "sum_stored_offsets"),
                struct.unpack("<BBHI", accumulator),
            )),
            "latest_point_hex": cache[0x4B:0x50].hex(),
            "notification": self.notifications[-1] if self.notifications else None,
        }

    def read_temperature(
        self,
        index: int,
        *,
        status: int,
        timestamps: list[int],
    ) -> dict[str, Any]:
        self.time_status = status
        self.timestamp_returns = list(timestamps)
        prior = self.timestamp_calls
        self.machine.uc.mem_write(common.SLOT_OUTPUT, b"\x5a" * 3)
        self.machine.call(common.READ, index, common.SLOT_OUTPUT)
        return {
            "output_stored_offsets": common.aggregate(
                bytes(self.machine.uc.mem_read(common.SLOT_OUTPUT, 3))
            ),
            "timestamp_calls": self.timestamp_calls - prior,
        }


def run(image: bytes) -> dict[str, Any]:
    accepted = TemperatureFixture(image).event(
        365, 0x12345678, aggregate_hour=4, average_hour=5
    )
    minimum = TemperatureFixture(image).event(
        250, 9, aggregate_hour=6, average_hour=6
    )
    maximum = TemperatureFixture(image).event(
        500, 10, aggregate_hour=7, average_hour=7
    )
    rejected_low = TemperatureFixture(image).event(
        249, 11, aggregate_hour=1, average_hour=1
    )
    rejected_high = TemperatureFixture(image).event(
        501, 12, aggregate_hour=1, average_hour=1
    )

    reset_fixture = TemperatureFixture(image)
    reset_fixture.machine.uc.mem_write(common.CACHE, b"\xa5" * common.CACHE_LENGTH)
    reset_raw = reset_fixture.reset(0x01020304, -300)
    reset = {
        "slots_zero": reset_raw[:0x48] == b"\x00" * 0x48,
        "utc_offset_minutes": struct.unpack_from("<h", reset_raw, 0x48)[0],
        "preserved_4a_4f_hex": reset_raw[0x4A:0x50].hex(),
        "day_start": struct.unpack_from("<I", reset_raw, 0x50)[0],
    }

    reads = TemperatureFixture(image)
    reads.reset(0, 0)
    reads.write(5, (115, 120, 110))
    valid = reads.read_temperature(5, status=1, timestamps=[])
    plausible = reads.read_temperature(5, status=0, timestamps=[946_080_001])
    redacted = reads.read_temperature(5, status=0, timestamps=[1_000])
    reads.write(6, (0, 120, 110))
    zero_average = reads.read_temperature(6, status=0, timestamps=[1_000])

    assert accepted["event_after_hex"] == "6d01a1a278563412"
    assert accepted["timestamp_calls"] == 1 and accepted["local_hour_calls"] == 2
    assert accepted["slot_stored_offsets"] == {
        "average": 115, "maximum": 115, "minimum": 115,
    }
    assert accepted["accumulator"] == {
        "hour": 5, "reserved": 0, "count": 1, "sum_stored_offsets": 115,
    }
    assert accepted["latest_point_hex"] == "7378563412"
    assert accepted["notification"] is None
    assert minimum["slot_stored_offsets"] == {"average": 0, "maximum": 0, "minimum": 0}
    assert minimum["latest_point_hex"] == "0009000000"
    assert maximum["slot_stored_offsets"] == {
        "average": 250, "maximum": 250, "minimum": 250,
    }
    for rejected in (rejected_low, rejected_high):
        assert rejected["timestamp_calls"] == 0
        assert rejected["local_hour_calls"] == 0
        assert rejected["latest_point_hex"] == "0000000000"
    assert reset == {
        "slots_zero": True,
        "utc_offset_minutes": -300,
        "preserved_4a_4f_hex": "a5" * 6,
        "day_start": 0x01020304,
    }
    expected = {"average": 115, "maximum": 120, "minimum": 110}
    assert valid == {"output_stored_offsets": expected, "timestamp_calls": 0}
    assert plausible == {"output_stored_offsets": expected, "timestamp_calls": 1}
    assert redacted == {
        "output_stored_offsets": {"average": 0, "maximum": 0, "minimum": 0},
        "timestamp_calls": 1,
    }
    assert zero_average == {
        "output_stored_offsets": {"average": 0, "maximum": 120, "minimum": 110},
        "timestamp_calls": 1,
    }

    return {
        "storage_accepted_365": accepted,
        "storage_accepted_minimum_250": minimum,
        "storage_accepted_maximum_500": maximum,
        "storage_rejected_below_250": rejected_low,
        "storage_rejected_above_500": rejected_high,
        "reset": reset,
        "read_valid_clock": valid,
        "read_plausible_clock": plausible,
        "read_invalid_early_clock_redacted": redacted,
        "read_zero_average_returned": zero_average,
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
