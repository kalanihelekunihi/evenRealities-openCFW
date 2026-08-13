#!/usr/bin/env python3
"""Execute the production R1 sleep.db append decision logic with every effect intercepted.

Finder, rollover, writer, logging, and reset calls are replaced before execution. The fixture has
no physical ring, BLE stack, sensor, health store, or flash-writing implementation.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


APPEND = 0x0005B890
RESET = 0x0005B2F8
FINDER = 0x0008FE28
ROLLOVER = 0x0008FC6C
WRITER = 0x0008FE98
LOG_FLAGS = 0x000914EC

INITIALIZED_FLAG = 0x200067B4
RECORD = RAM_BASE + 0x54000


class SleepAppendFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.finder_results: list[int] = []
        self.rollover_results: list[int] = []
        self.writer_results: list[int] = []
        self.finder_calls = 0
        self.rollover_calls = 0
        self.writer_calls: list[dict[str, int]] = []
        self.reset_calls = 0
        self.machine.uc.mem_write(RECORD, b"\x00" * 0x1000)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)
        self.machine.uc.hook_add(UC_HOOK_MEM_INVALID, self._invalid_memory)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    @staticmethod
    def _take(values: list[int], label: str) -> int:
        if not values:
            raise RuntimeError(f"unexpected {label} call")
        return values.pop(0)

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == FINDER:
            self.finder_calls += 1
            self._return(uc, self._take(self.finder_results, "finder"))
        elif address == ROLLOVER:
            self.rollover_calls += 1
            self._return(uc, self._take(self.rollover_results, "rollover"))
        elif address == WRITER:
            self.writer_calls.append({
                "selected_sector_index_raw": uc.reg_read(UC_ARM_REG_R0),
                "record_pointer": uc.reg_read(UC_ARM_REG_R1),
                "payload_length_bytes": uc.reg_read(UC_ARM_REG_R2),
                "r3_raw": uc.reg_read(UC_ARM_REG_R3),
            })
            self._return(uc, self._take(self.writer_results, "writer"))
        elif address == RESET:
            self.reset_calls += 1
            self._return(uc)

    def _invalid_memory(
        self,
        uc: Any,
        access: int,
        address: int,
        size: int,
        value: int,
        user_data: Any,
    ) -> bool:
        del access, size, value, user_data
        raise RuntimeError(
            f"invalid firmware fixture memory at 0x{address:08x}, "
            f"pc=0x{uc.reg_read(UC_ARM_REG_PC):08x}"
        )

    def run(
        self,
        *,
        initialized: bool,
        pointer: int = RECORD,
        length: int,
        finder: list[int] | None = None,
        rollover: list[int] | None = None,
        writer: list[int] | None = None,
    ) -> dict[str, Any]:
        self.finder_results = list(finder or [])
        self.rollover_results = list(rollover or [])
        self.writer_results = list(writer or [])
        self.finder_calls = 0
        self.rollover_calls = 0
        self.writer_calls.clear()
        self.reset_calls = 0
        self.machine.uc.mem_write(INITIALIZED_FLAG, bytes([int(initialized)]))
        result = self.machine.call(APPEND, pointer, length)
        if self.finder_results or self.rollover_results or self.writer_results:
            raise AssertionError("fixture supplied unused intercepted outcomes")
        return {
            "return_raw": result,
            "finder_calls": self.finder_calls,
            "rollover_calls": self.rollover_calls,
            "writer_calls": list(self.writer_calls),
            "reset_calls": self.reset_calls,
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepAppendFixture(image)

    not_initialized = fixture.run(initialized=False, length=1)
    null_record = fixture.run(initialized=True, pointer=0, length=1)
    oversized = fixture.run(initialized=True, length=3_889)

    maximum_first_success = fixture.run(
        initialized=True,
        length=3_888,
        finder=[0x123],
        writer=[9],
    )
    rollover_first_success = fixture.run(
        initialized=True,
        length=24,
        finder=[0xFFFFFFFF],
        rollover=[0x123],
        writer=[1],
    )
    second_success = fixture.run(
        initialized=True,
        length=24,
        finder=[1, 2],
        writer=[0, 1],
    )
    two_failures = fixture.run(
        initialized=True,
        length=24,
        finder=[1, 2],
        writer=[0, 0],
    )
    rollover_twice_then_reset = fixture.run(
        initialized=True,
        length=24,
        finder=[0xFFFFFFFF, 0xFFFFFFFF],
        rollover=[0x101, 0x202],
        writer=[0, 0],
    )

    for rejected in (not_initialized, null_record, oversized):
        assert rejected == {
            "return_raw": 0,
            "finder_calls": 0,
            "rollover_calls": 0,
            "writer_calls": [],
            "reset_calls": 0,
        }

    assert maximum_first_success["return_raw"] == 1
    assert maximum_first_success["finder_calls"] == 1
    assert maximum_first_success["rollover_calls"] == 0
    assert len(maximum_first_success["writer_calls"]) == 1
    assert (
        maximum_first_success["writer_calls"][0]["selected_sector_index_raw"]
        == 0x23
    )
    assert maximum_first_success["writer_calls"][0]["record_pointer"] == RECORD
    assert maximum_first_success["writer_calls"][0]["payload_length_bytes"] == 3_888
    assert maximum_first_success["reset_calls"] == 0

    assert rollover_first_success["return_raw"] == 1
    assert rollover_first_success["finder_calls"] == 1
    assert rollover_first_success["rollover_calls"] == 1
    assert (
        rollover_first_success["writer_calls"][0]["selected_sector_index_raw"]
        == 0x23
    )
    assert rollover_first_success["reset_calls"] == 0

    assert second_success["return_raw"] == 1
    assert second_success["finder_calls"] == 2
    assert second_success["rollover_calls"] == 0
    assert [
        call["selected_sector_index_raw"] for call in second_success["writer_calls"]
    ] == [1, 2]
    assert second_success["reset_calls"] == 0

    assert two_failures["return_raw"] == 0
    assert two_failures["finder_calls"] == 2
    assert two_failures["rollover_calls"] == 0
    assert [
        call["selected_sector_index_raw"] for call in two_failures["writer_calls"]
    ] == [1, 2]
    assert two_failures["reset_calls"] == 1

    assert rollover_twice_then_reset["return_raw"] == 0
    assert rollover_twice_then_reset["finder_calls"] == 2
    assert rollover_twice_then_reset["rollover_calls"] == 2
    assert [
        call["selected_sector_index_raw"]
        for call in rollover_twice_then_reset["writer_calls"]
    ] == [1, 2]
    assert rollover_twice_then_reset["reset_calls"] == 1

    return {
        "fixture_groups": 8,
        "guard_cases": {
            "not_initialized": not_initialized,
            "null_record": null_record,
            "oversized_3889_bytes": oversized,
        },
        "accepted_boundary": maximum_first_success,
        "rollover_first_success": rollover_first_success,
        "second_success": second_success,
        "two_failures": two_failures,
        "rollover_twice_then_reset": rollover_twice_then_reset,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes": False,
            "reset_wrapper_executed": False,
            "health_store_access": False,
            "all_effectful_callees_intercepted": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
