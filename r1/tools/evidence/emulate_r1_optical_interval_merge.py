#!/usr/bin/env python3
"""Assert the stock 0x4857C optical-interval merge contract."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


OPTICAL_INTERVAL_MERGE = 0x0004857C
STATE = RAM_BASE + 0x5A000
ENDS = RAM_BASE + 0x5B000
STARTS = RAM_BASE + 0x5B100
COUNT = RAM_BASE + 0x5B200
OUTPUT = RAM_BASE + 0x5B300
STATE_BYTES = 1736
RECORD_OFFSET = 88
SIGNAL_OFFSET = 728


def f32_bits(value: float) -> str:
    return f"0x{struct.unpack('<I', struct.pack('<f', value))[0]:08x}"


class OpticalIntervalFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)

    def run(
        self,
        *,
        current_window: int,
        records: list[tuple[int, int, int, int, float, float]],
        ends: list[int],
        starts: list[int],
    ) -> dict[str, Any]:
        if len(ends) != len(starts) or len(ends) > 255:
            raise ValueError("candidate arrays must have the same UInt8 length")
        state = bytearray(STATE_BYTES)
        state[81] = len(records)
        struct.pack_into("<I", state, 84, current_window)
        for index, record in enumerate(records):
            struct.pack_into("<HHHHff", state, RECORD_OFFSET + index * 16,
                             *record)
        struct.pack_into(
            "<250f", state, SIGNAL_OFFSET,
            *(float(index * index) for index in range(250)),
        )
        self.machine.uc.mem_write(STATE, bytes(state))
        self.machine.uc.mem_write(ENDS, bytes(ends) if ends else b"\x00")
        self.machine.uc.mem_write(STARTS, bytes(starts) if starts else b"\x00")
        self.machine.uc.mem_write(COUNT, bytes([len(ends)]))
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 4)
        result = self.machine.call(
            OPTICAL_INTERVAL_MERGE, STATE, ENDS, STARTS, COUNT, OUTPUT
        )
        final = bytes(self.machine.uc.mem_read(STATE, STATE_BYTES))
        interval_count = final[81]
        final_records = [
            struct.unpack_from("<HHHHff", final, RECORD_OFFSET + index * 16)
            for index in range(interval_count)
        ]
        output = struct.unpack("<f", bytes(self.machine.uc.mem_read(OUTPUT, 4)))[0]
        return {
            "return": result,
            "interval_count": interval_count,
            "records": [
                {
                    "end": record[0],
                    "start": record[1],
                    "peak": record[2],
                    "padding": record[3],
                    "end_value_bits": f32_bits(record[4]),
                    "start_value_bits": f32_bits(record[5]),
                }
                for record in final_records
            ],
            "mean_amplitude_bits": f32_bits(output),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    empty = OpticalIntervalFixture(image).run(
        current_window=20, records=[], ends=[20, 40], starts=[10, 30]
    )
    assert empty["return"] == 0 and empty["interval_count"] == 2
    assert empty["records"] == [
        {
            "end": 270, "start": 260, "peak": 269, "padding": 0,
            "end_value_bits": "0x43c80000", "start_value_bits": "0x42c80000",
        },
        {
            "end": 290, "start": 280, "peak": 289, "padding": 0,
            "end_value_bits": "0x44c80000", "start_value_bits": "0x44610000",
        },
    ]
    assert empty["mean_amplitude_bits"] == "0x43fa0000"

    insertion = OpticalIntervalFixture(image).run(
        current_window=20,
        records=[
            (270, 260, 269, 0, 400.0, 100.0),
            (310, 300, 309, 0, 1600.0, 900.0),
        ],
        ends=[5], starts=[1],
    )
    assert insertion["return"] == 0 and insertion["interval_count"] == 3
    assert [(record["end"], record["start"], record["peak"])
            for record in insertion["records"]] == [
                (255, 251, 254), (270, 260, 269), (310, 300, 309),
            ]
    assert insertion["records"][0]["end_value_bits"] == "0x41c80000"
    assert insertion["records"][0]["start_value_bits"] == "0x3f800000"
    assert insertion["mean_amplitude_bits"] == "0x43aaaaab"

    replacement = OpticalIntervalFixture(image).run(
        current_window=20,
        records=[(270, 260, 269, 0, 400.0, 100.0)],
        ends=[15], starts=[5],
    )
    assert replacement["return"] == 0 and replacement["interval_count"] == 1
    assert (replacement["records"][0]["end"],
            replacement["records"][0]["start"],
            replacement["records"][0]["peak"]) == (265, 255, 264)
    assert replacement["mean_amplitude_bits"] == "0x43480000"

    compacted = OpticalIntervalFixture(image).run(
        current_window=21,
        records=[
            (270, 260, 269, 0, 400.0, 100.0),
            (310, 300, 309, 0, 1600.0, 900.0),
        ],
        ends=[], starts=[],
    )
    assert compacted["return"] == 0 and compacted["interval_count"] == 2
    assert [(record["end"], record["start"])
            for record in compacted["records"]] == [(245, 235), (285, 275)]
    assert compacted["mean_amplitude_bits"] == "0x43fa0000"

    print(json.dumps({
        "function": "0x0004857c",
        "empty_build": empty,
        "ordered_insertion": insertion,
        "tail_replacement": replacement,
        "window_compaction": compacted,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
