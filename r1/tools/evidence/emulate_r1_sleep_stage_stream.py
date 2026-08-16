#!/usr/bin/env python3
"""Assert the stock 0x60DC4 sleep-stage stream orchestration contract."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE
from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


SLEEP_STAGE_STREAM = 0x00060DC4
STAGE_CLASSIFIER = 0x00088450
STATE = RAM_BASE + 0x5C000
PEAKS = RAM_BASE + 0x5F000
ACTIVITY = RAM_BASE + 0x5F100
TIME = RAM_BASE + 0x5F200
STATUS = RAM_BASE + 0x5F300
OUTPUT = RAM_BASE + 0x5F400
STATE_BYTES = 8440


class SleepStageStreamFixture:
    def __init__(self, image: bytes, selected: int | None) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.selected = selected
        self.classifier_calls: list[int] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address != STAGE_CLASSIFIER:
            return
        if self.selected is None:
            raise AssertionError("unexpected sleep-stage classifier call")
        result = uc.reg_read(UC_ARM_REG_R0)
        iteration = bytes(uc.mem_read(STATE + 1003, 1))[0]
        self.classifier_calls.append(iteration)
        uc.mem_write(
            result,
            struct.pack("<4fb", 9.0, 1.0, 3.0, 2.0, self.selected),
        )
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def run(
        self,
        *,
        active: int,
        batch_count: int,
        stored_peaks: list[int],
        classifier_iteration: int,
        mode: int,
        update_counter: int,
        input_peaks: list[int],
        timestamp: int,
        activity_enabled: bool,
    ) -> dict[str, Any]:
        state = bytearray(STATE_BYTES)
        state[1000] = active
        state[1001] = batch_count
        state[1002] = len(stored_peaks)
        state[1003] = classifier_iteration
        state[8437] = mode
        struct.pack_into("<H", state, 998, update_counter)
        for index, peak in enumerate(stored_peaks):
            struct.pack_into("<h", state, 726 + index * 2, peak)
        for index in range(90):
            struct.pack_into("<f", state, 1004 + index * 4, float(index))
        peak_record = bytes(input_peaks) + bytes(16 - len(input_peaks)) + \
            bytes([len(input_peaks)])
        self.machine.uc.mem_write(STATE, bytes(state))
        self.machine.uc.mem_write(PEAKS, peak_record)
        self.machine.uc.mem_write(
            ACTIVITY, bytes(26) + bytes([int(activity_enabled)])
        )
        self.machine.uc.mem_write(TIME, struct.pack("<I", timestamp))
        self.machine.uc.mem_write(STATUS, struct.pack("<fBBB", 0.0, 1, 0, 0))
        self.machine.uc.mem_write(OUTPUT, b"\xa5" * 3)
        result = self.machine.call(
            SLEEP_STAGE_STREAM,
            STATE, 0, PEAKS, ACTIVITY, TIME, STATUS, OUTPUT,
        )
        final = bytes(self.machine.uc.mem_read(STATE, STATE_BYTES))
        final_peak_count = final[1002]
        return {
            "return": result,
            "output": list(self.machine.uc.mem_read(OUTPUT, 3)),
            "active": final[1000],
            "batch_count": final[1001],
            "peak_count": final_peak_count,
            "classifier_iteration": final[1003],
            "update_counter": struct.unpack_from("<H", final, 998)[0],
            "peaks": [
                struct.unpack_from("<h", final, 726 + index * 2)[0]
                for index in range(final_peak_count)
            ],
            "selected_stage": struct.unpack_from("<b", final, 8436)[0],
            "mode": final[8437],
            "previous_timestamp": struct.unpack_from("<I", final, 720)[0],
            "previous_packed_value": final[724],
            "packed_head": final[:4].hex(),
            "window_head": list(struct.unpack_from("<3f", final, 1004)),
            "window_tail": list(struct.unpack_from("<3f", final, 1004 + 57 * 4)),
            "classifier_calls": self.classifier_calls,
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    inactive = SleepStageStreamFixture(image, None).run(
        active=0, batch_count=0, stored_peaks=[], classifier_iteration=0,
        mode=0, update_counter=0, input_peaks=[], timestamp=30,
        activity_enabled=False,
    )
    assert inactive["return"] == 0 and inactive["output"] == [0, 0, 0]
    assert inactive["packed_head"] == "08000000"
    assert inactive["previous_timestamp"] == 30
    assert inactive["previous_packed_value"] == 1

    accumulation = SleepStageStreamFixture(image, None).run(
        active=1, batch_count=2, stored_peaks=[], classifier_iteration=0,
        mode=100, update_counter=4, input_peaks=[5, 10], timestamp=60,
        activity_enabled=True,
    )
    assert accumulation["return"] == 0
    assert accumulation["output"] == [0xA5, 0, 0]
    assert accumulation["batch_count"] == 3
    assert accumulation["peaks"] == [55, 60]

    publication = SleepStageStreamFixture(image, 1).run(
        active=1, batch_count=2, stored_peaks=[], classifier_iteration=1,
        mode=0, update_counter=0, input_peaks=[], timestamp=60,
        activity_enabled=True,
    )
    assert publication["return"] == 0
    assert publication["output"] == [1, 1, 1]
    assert publication["classifier_calls"] == [1]
    assert publication["classifier_iteration"] == 0
    assert publication["selected_stage"] == 1
    assert publication["packed_head"] == "04000000"
    assert publication["window_head"] == [30.0, 31.0, 32.0]
    assert publication["window_tail"] == [87.0, 88.0, 89.0]

    rollover = SleepStageStreamFixture(image, -1).run(
        active=1, batch_count=31, stored_peaks=[740, 760],
        classifier_iteration=0, mode=0, update_counter=7,
        input_peaks=[10], timestamp=60, activity_enabled=True,
    )
    assert rollover["return"] == 0
    assert rollover["output"] == [0xA5, 0, 1]
    assert rollover["batch_count"] == 2
    assert rollover["update_counter"] == 8
    assert rollover["peaks"] == [10, 35]
    assert rollover["classifier_calls"] == [1]
    assert rollover["classifier_iteration"] == 2

    print(json.dumps({
        "function": "0x00060dc4",
        "inactive_packing": inactive,
        "active_accumulation": accumulation,
        "stage_publication": publication,
        "window_rollover": rollover,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
