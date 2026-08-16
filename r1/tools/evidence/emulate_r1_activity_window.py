#!/usr/bin/env python3
"""Assert the stock 0x6138C activity-window state-machine contract.

The SHA-pinned production Thumb routine executes with synthetic RAM. Its private
250-sample decision helper is intercepted only to select a deterministic positive
or negative vote; input conditioning and the equal-rate window transform execute
from the production image.
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
    UC_ARM_REG_S0,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ACTIVITY_WINDOW = 0x0006138C
WINDOW_DECISION = 0x00096E74
STATE = RAM_BASE + 0x52000
CONFIGURATION = RAM_BASE + 0x53000
INPUT = RAM_BASE + 0x53100
OUTPUT = RAM_BASE + 0x53200
SAMPLES = RAM_BASE + 0x53300
AXES = (RAM_BASE + 0x53400, RAM_BASE + 0x53500, RAM_BASE + 0x53600)
STATE_BYTES = 1028


def f32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


class ActivityWindowFixture:
    def __init__(self, image: bytes, vote: int | None) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.vote = vote
        self.decision_calls = 0
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)
        axis = struct.pack("<25f", *([1000.0] * 25))
        zero_axis = struct.pack("<25f", *([0.0] * 25))
        self.machine.uc.mem_write(AXES[0], axis)
        self.machine.uc.mem_write(AXES[1], zero_axis)
        self.machine.uc.mem_write(AXES[2], zero_axis)
        self.machine.uc.mem_write(
            CONFIGURATION, struct.pack("<III", *AXES) + b"\x00"
        )

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address != WINDOW_DECISION:
            return
        if self.vote is None:
            raise AssertionError("unexpected activity-window decision")
        self.decision_calls += 1
        uc.reg_write(UC_ARM_REG_R0, self.vote)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def run(
        self,
        *,
        state_code: int,
        score: float = 0.0,
        reset_threshold: float = 0.5,
        transition_count: int = 0,
        accumulated_samples: int = 0,
        hold_samples: int = 180,
        positive_windows: int = 0,
        negative_windows: int = 0,
        sample_count: int = 25,
        channel_count: int = 1,
        input_quality: float = 1.0,
        alternate_conditioning: bool = False,
        samples: list[float] | None = None,
    ) -> dict[str, Any]:
        state = bytearray(STATE_BYTES)
        struct.pack_into("<f", state, 0, score)
        state[4] = state_code
        struct.pack_into("<iii", state, 1008, transition_count,
                         accumulated_samples, hold_samples)
        struct.pack_into("<f", state, 1020, reset_threshold)
        state[1024] = positive_windows
        state[1025] = negative_windows
        self.machine.uc.mem_write(STATE, bytes(state))
        self.machine.uc.mem_write(
            CONFIGURATION + 12, bytes([int(alternate_conditioning)])
        )

        source = samples if samples is not None else [500.0 + x for x in range(27)]
        self.machine.uc.mem_write(SAMPLES, struct.pack(f"<{len(source)}f", *source))
        self.machine.uc.mem_write(
            INPUT,
            struct.pack("<IhB", SAMPLES if channel_count else 0,
                        sample_count, channel_count),
        )
        self.machine.uc.mem_write(OUTPUT, b"\xa5\xa5")
        self.machine.uc.reg_write(UC_ARM_REG_S0, f32_bits(input_quality))
        result = self.machine.call(
            ACTIVITY_WINDOW, STATE, CONFIGURATION, INPUT, OUTPUT
        )
        final = bytes(self.machine.uc.mem_read(STATE, STATE_BYTES))
        return {
            "return": result,
            "score_bits": f"0x{struct.unpack_from('<I', final, 0)[0]:08x}",
            "state": final[4],
            "transition_count": struct.unpack_from("<i", final, 1008)[0],
            "accumulated_samples": struct.unpack_from("<i", final, 1012)[0],
            "hold_samples": struct.unpack_from("<i", final, 1016)[0],
            "reset_threshold_bits":
                f"0x{struct.unpack_from('<I', final, 1020)[0]:08x}",
            "positive_windows": final[1024],
            "negative_windows": final[1025],
            "output": list(self.machine.uc.mem_read(OUTPUT, 2)),
            "window_head_bits": [
                f"0x{x:08x}" for x in struct.unpack_from("<2I", final, 8)
            ],
            "window_tail_bits": [
                f"0x{x:08x}" for x in struct.unpack_from("<2I", final, 1000)
            ],
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    positive_fixture = ActivityWindowFixture(image, 1)
    positive = positive_fixture.run(
        state_code=0, accumulated_samples=225, positive_windows=4
    )
    assert positive["return"] == 0
    assert positive["state"] == 4 and positive["hold_samples"] == 180
    assert positive["accumulated_samples"] == 0
    assert positive["positive_windows"] == positive["negative_windows"] == 0
    assert positive["output"] == [1, 0]
    assert positive_fixture.decision_calls == 1

    negative_fixture = ActivityWindowFixture(image, 0)
    negative = negative_fixture.run(
        state_code=2, accumulated_samples=225, hold_samples=500,
        negative_windows=4,
    )
    assert negative["state"] == 1 and negative["hold_samples"] == 600
    assert negative["accumulated_samples"] == 0
    assert negative["output"] == [0, 0]
    assert negative_fixture.decision_calls == 1

    transition_fixture = ActivityWindowFixture(image, None)
    transition = transition_fixture.run(
        state_code=1, transition_count=179, hold_samples=180
    )
    assert transition["state"] == 2 and transition["transition_count"] == 0
    assert transition["output"] == [0, 1]

    reset_fixture = ActivityWindowFixture(image, None)
    reset = reset_fixture.run(
        state_code=2, score=1.0, transition_count=3,
        accumulated_samples=200, positive_windows=4, negative_windows=2,
    )
    assert reset["score_bits"] == "0x3f666666"
    assert reset["state"] == 3 and reset["transition_count"] == 0
    assert reset["accumulated_samples"] == 0
    assert reset["positive_windows"] == reset["negative_windows"] == 0
    assert reset["output"] == [0, 0]

    alternate_fixture = ActivityWindowFixture(image, None)
    alternate = alternate_fixture.run(
        state_code=3, score=0.05, reset_threshold=2.0,
        alternate_conditioning=True,
    )
    assert alternate["score_bits"] == "0x3dc28f5c"
    assert alternate["state"] == 3 and alternate["output"] == [0, 1]

    zero_channel_fixture = ActivityWindowFixture(image, None)
    zero_channel = zero_channel_fixture.run(
        state_code=0, accumulated_samples=225, channel_count=0
    )
    assert zero_channel["state"] == 4
    assert zero_channel["output"] == [1, 0]

    spill_fixture = ActivityWindowFixture(image, None)
    spill_samples = [0.0] * 25 + [1.0]
    spill = spill_fixture.run(
        state_code=0, sample_count=26, samples=spill_samples
    )
    assert spill["transition_count"] == 0x3F800000
    assert spill["accumulated_samples"] == 25
    assert spill["state"] == 0 and spill["output"] == [255, 1]

    print(json.dumps({
        "function": "0x0006138c",
        "positive_threshold": positive,
        "negative_threshold": negative,
        "transition_hold": transition,
        "score_reset": reset,
        "alternate_conditioning": alternate,
        "zero_channel": zero_channel,
        "count_26_metadata_spill": spill,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
