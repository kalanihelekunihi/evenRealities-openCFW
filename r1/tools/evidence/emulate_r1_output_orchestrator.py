#!/usr/bin/env python3
"""Execute the isolated production-Thumb 16-stage output orchestrator."""

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
    UC_ARM_REG_R1,
    UC_ARM_REG_S0,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ORCHESTRATOR = 0x0005FF94
NOOP = 0x000578C8
ENGINE = RAM_BASE + 0x30000
ENGINE_BYTES = 0x3894

# Address, substate, control, status, stock stage number. Order is execution order.
STAGES = [
    (0x00060680, 0x01F8, 0x3848, 0x3800, 3),
    (0x0005ED14, 0x08F4, 0x384C, 0x3804, 7),
    (0x0005F4B6, 0x0B62, 0x384D, 0x3805, 8),
    (0x0005EF1C, 0x0B74, 0x384E, 0x3806, 9),
    (0x000610C8, 0x0BD0, 0x384F, 0x3807, 10),
    (0x0005F3D8, 0x0BD4, 0x3850, 0x3808, 11),
    (0x000605DC, 0x0C54, 0x3857, 0x380F, 18),
    (0x0005F56C, 0x0C58, 0x3859, 0x3811, 20),
    (0x0005FEB8, 0x0CB4, 0x385C, 0x3814, 23),
    (0x0005F264, 0x33B4, 0x3868, 0x3820, 35),
    (0x00060B80, 0x0FF0, 0x3861, 0x3819, 28),
    (0x00060AF4, 0x112C, 0x3863, 0x381B, 30),
    (0x00060DC4, 0x12B8, 0x3865, 0x381D, 32),
    (0x0006138C, 0x33D8, 0x3877, 0x382F, 50),
    (0x00061198, 0x37DC, 0x3881, 0x3839, 60),
    (0x00061274, 0x37F8, 0x3886, 0x383E, 65),
]


class OrchestratorFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.calls: list[dict[str, Any]] = []
        self.noop_stages: list[int] = []
        self.by_address = {
            address: (index, state_offset)
            for index, (address, state_offset, _, _, _) in enumerate(STAGES)
        }
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address in self.by_address:
            index, state_offset = self.by_address[address]
            if address == 0x0006138C:
                elapsed = struct.unpack(
                    "<f", struct.pack("<I", uc.reg_read(UC_ARM_REG_S0))
                )[0]
            else:
                elapsed = uc.reg_read(UC_ARM_REG_R1)
            self.calls.append({
                "index": index,
                "address": f"0x{address:08x}",
                "state_offset": uc.reg_read(UC_ARM_REG_R0) - ENGINE,
                "expected_state_offset": state_offset,
                "elapsed": elapsed,
            })
            self._return(uc, 0xA0 + index)
        elif address == NOOP:
            self.noop_stages.append(uc.reg_read(UC_ARM_REG_R1))
            self._return(uc)

    def run(self, control: int, elapsed: int) -> dict[str, Any]:
        self.calls = []
        self.noop_stages = []
        self.machine.uc.mem_write(ENGINE, b"\x00" * ENGINE_BYTES)
        for _, _, control_offset, _, _ in STAGES:
            self.machine.uc.mem_write(ENGINE + control_offset, bytes([control]))
        result = self.machine.call(ORCHESTRATOR, ENGINE, elapsed)
        return {
            "control_input": control,
            "result_offset": result - ENGINE,
            "calls": self.calls,
            "noop_stages": self.noop_stages,
            "controls": [
                self.machine.uc.mem_read(ENGINE + item[2], 1)[0]
                for item in STAGES
            ],
            "statuses": [
                self.machine.uc.mem_read(ENGINE + item[3], 1)[0]
                for item in STAGES
            ],
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = OrchestratorFixture(image)
    normal = fixture.run(0, 7)
    assert normal["result_offset"] == 0x37FD
    assert [item["index"] for item in normal["calls"]] == list(range(16))
    assert all(item["state_offset"] == item["expected_state_offset"]
               for item in normal["calls"])
    assert [item["elapsed"] for item in normal["calls"]] == [7] * 13 + [7.0] + [7] * 2
    assert normal["noop_stages"] == [item[4] for item in STAGES]
    assert normal["controls"] == [0] * 16
    assert normal["statuses"] == list(range(0xA0, 0xB0))

    forced = fixture.run(1, 99)
    assert [item["elapsed"] for item in forced["calls"]] == [1] * 13 + [1.0] + [1] * 2
    assert forced["controls"] == [0] * 16
    assert forced["statuses"] == list(range(0xA0, 0xB0))

    disabled = fixture.run(2, 5)
    assert disabled["calls"] == []
    assert disabled["controls"] == [3] * 16
    assert disabled["statuses"] == [0] * 16
    assert disabled["noop_stages"] == [item[4] for item in STAGES]

    held = fixture.run(3, 5)
    assert held["calls"] == []
    assert held["controls"] == [3] * 16
    assert held["statuses"] == [0] * 16

    return {
        "fixture_groups": 4,
        "normal": normal,
        "forced_one_update": forced,
        "disable_transition": disabled,
        "held_disabled": held,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
