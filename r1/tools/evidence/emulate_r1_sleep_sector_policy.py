#!/usr/bin/env python3
"""Execute R1 sleep.db sector policy with all partition callbacks intercepted.

The production count, finder, rollover, and closer functions execute against a private RAM image.
Flash read, write, erase, and logging callbacks are replaced. No physical ring, BLE stack, sensor,
firmware partition, host health store, or destructive operation is reachable.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_INVALID
from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ROLLOVER = 0x0008FC6C
SECTOR_COUNT = 0x0008FE14
FINDER = 0x0008FE28
CLOSER = 0x000901E4
LOG_FLAGS = 0x000914EC

STORAGE_GLOBAL = 0x200067B4
PARTITION = RAM_BASE + 0x50000
DESCRIPTOR = RAM_BASE + 0x53000
OPERATIONS = RAM_BASE + 0x53100
READ_STUB = RAM_BASE + 0x53200
WRITE_STUB = RAM_BASE + 0x53210
ERASE_STUB = RAM_BASE + 0x53220

SECTOR_BYTES = 0x1000
SECTOR_COUNT_RAW = 2
FULL0 = 0xCCFFAABB
FULL1 = 0x66889977
ERASED = 0xFFFFFFFF


class SleepSectorPolicyFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.write_result = 0
        self.read_calls: list[tuple[int, int]] = []
        self.write_calls: list[tuple[int, bytes]] = []
        self.erase_calls: list[tuple[int, int]] = []

        self.machine.uc.mem_write(PARTITION, b"\xff" * (SECTOR_BYTES * SECTOR_COUNT_RAW))
        self.machine.uc.mem_write(DESCRIPTOR, b"\x00" * 0x80)
        self.machine.uc.mem_write(OPERATIONS, b"\x00" * 0x80)
        self.machine.uc.mem_write(STORAGE_GLOBAL + 4, struct.pack("<I", DESCRIPTOR))
        self.machine.uc.mem_write(STORAGE_GLOBAL + 8, struct.pack("<I", OPERATIONS))
        self.machine.uc.mem_write(DESCRIPTOR + 0x34, struct.pack("<I", PARTITION))
        self.machine.uc.mem_write(
            DESCRIPTOR + 0x38,
            struct.pack("<I", SECTOR_BYTES * SECTOR_COUNT_RAW),
        )
        self.machine.uc.mem_write(OPERATIONS + 0x28, struct.pack("<I", READ_STUB | 1))
        self.machine.uc.mem_write(OPERATIONS + 0x2C, struct.pack("<I", WRITE_STUB | 1))
        self.machine.uc.mem_write(OPERATIONS + 0x30, struct.pack("<I", ERASE_STUB | 1))
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)
        self.machine.uc.hook_add(UC_HOOK_MEM_INVALID, self._invalid_memory)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == READ_STUB:
            source = uc.reg_read(UC_ARM_REG_R0)
            destination = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            if source < PARTITION or source + length > PARTITION + SECTOR_BYTES * 2:
                raise RuntimeError(f"out-of-fixture partition read at 0x{source:08x}")
            payload = bytes(uc.mem_read(source, length))
            uc.mem_write(destination, payload)
            self.read_calls.append((source, length))
            self._return(uc, 0)
        elif address == WRITE_STUB:
            destination = uc.reg_read(UC_ARM_REG_R0)
            source = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            self.write_calls.append((
                destination,
                bytes(uc.mem_read(source, length)),
            ))
            self._return(uc, self.write_result)
        elif address == ERASE_STUB:
            destination = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            self.erase_calls.append((destination, length))
            self._return(uc, 0)

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

    def set_headers(self, headers: list[tuple[int, int, int, int]]) -> None:
        if len(headers) != SECTOR_COUNT_RAW:
            raise ValueError("fixture requires exactly two sector headers")
        self.machine.uc.mem_write(PARTITION, b"\xff" * (SECTOR_BYTES * SECTOR_COUNT_RAW))
        for index, header in enumerate(headers):
            self.machine.uc.mem_write(
                PARTITION + index * SECTOR_BYTES,
                struct.pack("<4I", *header),
            )

    def reset_observations(self) -> None:
        self.read_calls.clear()
        self.write_calls.clear()
        self.erase_calls.clear()

    def count(self) -> int:
        self.reset_observations()
        return self.machine.call(SECTOR_COUNT)

    def finder(self, headers: list[tuple[int, int, int, int]]) -> dict[str, Any]:
        self.set_headers(headers)
        self.reset_observations()
        result = self.machine.call(FINDER)
        return {
            "return_raw": result,
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "read_lengths": [length for _, length in self.read_calls],
            "write_calls": len(self.write_calls),
            "erase_calls": len(self.erase_calls),
        }

    def rollover(self, headers: list[tuple[int, int, int, int]]) -> dict[str, Any]:
        self.set_headers(headers)
        before = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * 2))
        self.reset_observations()
        result = self.machine.call(ROLLOVER)
        after = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * 2))
        return {
            "return_raw": result,
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "erase_calls": [
                [address - PARTITION, length] for address, length in self.erase_calls
            ],
            "partition_unchanged": before == after,
            "write_calls": len(self.write_calls),
        }

    def close(
        self,
        headers: list[tuple[int, int, int, int]],
        *,
        sector_index: int,
        write_result: int,
    ) -> dict[str, Any]:
        self.set_headers(headers)
        before = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * 2))
        self.write_result = write_result
        self.reset_observations()
        result = self.machine.call(CLOSER, sector_index)
        after = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * 2))
        return {
            "return_raw": result,
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "write_calls": [
                [address - PARTITION, payload.hex()]
                for address, payload in self.write_calls
            ],
            "erase_calls": len(self.erase_calls),
            "partition_unchanged": before == after,
        }


def header(
    word0: int,
    word1: int,
    sequence: int,
    reserved: int = ERASED,
) -> tuple[int, int, int, int]:
    return word0, word1, sequence, reserved


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepSectorPolicyFixture(image)
    erased = header(ERASED, ERASED, ERASED)
    full3 = header(FULL0, FULL1, 3, 0)
    full7 = header(FULL0, FULL1, 7, 0)
    full9 = header(FULL0, FULL1, 9, 0)

    count = fixture.count()
    finder_first_erased = fixture.finder([erased, full3])
    finder_second_erased = fixture.finder([full3, erased])
    finder_erased_tail = fixture.finder([
        header(0x12345678, ERASED, ERASED, 0),
        full3,
    ])
    finder_interrupted = fixture.finder([
        header(FULL0, 0, 7, 0),
        full3,
    ])
    finder_none = fixture.finder([full3, full7])

    rollover_minimum = fixture.rollover([full9, full3])
    rollover_tie = fixture.rollover([full3, full3])
    rollover_all_erased = fixture.rollover([erased, erased])

    close_first = fixture.close([erased, erased], sector_index=0, write_result=0)
    close_minimum = fixture.close([full3, full9], sector_index=1, write_result=0)
    close_write_failure = fixture.close([full3, full9], sector_index=1, write_result=5)

    assert count == 2
    assert finder_first_erased["return_raw"] == 0
    assert finder_first_erased["read_offsets"] == [0]
    assert finder_second_erased["return_raw"] == 1
    assert finder_second_erased["read_offsets"] == [0, SECTOR_BYTES]
    assert finder_erased_tail["return_raw"] == 0
    assert finder_interrupted["return_raw"] == 0
    assert finder_none["return_raw"] == ERASED
    assert finder_none["read_offsets"] == [0, SECTOR_BYTES]
    for result in (
        finder_first_erased,
        finder_second_erased,
        finder_erased_tail,
        finder_interrupted,
        finder_none,
    ):
        assert result["read_lengths"] == [16] * len(result["read_offsets"])
        assert result["write_calls"] == 0
        assert result["erase_calls"] == 0

    assert rollover_minimum["return_raw"] == 1
    assert rollover_minimum["read_offsets"] == [0, SECTOR_BYTES]
    assert rollover_minimum["erase_calls"] == [[SECTOR_BYTES, SECTOR_BYTES]]
    assert rollover_tie["return_raw"] == 0
    assert rollover_tie["erase_calls"] == [[0, SECTOR_BYTES]]
    assert rollover_all_erased["return_raw"] == 0
    assert rollover_all_erased["erase_calls"] == [[0, SECTOR_BYTES]]
    for result in (rollover_minimum, rollover_tie, rollover_all_erased):
        assert result["partition_unchanged"]
        assert result["write_calls"] == 0

    expected_first_header = struct.pack("<4I", FULL0, FULL1, 1, 0).hex()
    expected_minimum_header = struct.pack("<4I", FULL0, FULL1, 4, 0).hex()
    assert close_first["return_raw"] == 1
    assert close_first["read_offsets"] == [0, SECTOR_BYTES]
    assert close_first["write_calls"] == [[0, expected_first_header]]
    assert close_minimum["return_raw"] == 1
    assert close_minimum["write_calls"] == [[SECTOR_BYTES, expected_minimum_header]]
    assert close_write_failure["return_raw"] == 0
    assert close_write_failure["write_calls"] == [[SECTOR_BYTES, expected_minimum_header]]
    for result in (close_first, close_minimum, close_write_failure):
        assert result["partition_unchanged"]
        assert result["erase_calls"] == 0

    return {
        "fixture_groups": 12,
        "sector_count_raw": count,
        "finder": {
            "first_erased": finder_first_erased,
            "second_erased": finder_second_erased,
            "erased_tail": finder_erased_tail,
            "interrupted_full_header": finder_interrupted,
            "no_writable_sector": finder_none,
        },
        "rollover": {
            "strict_minimum": rollover_minimum,
            "first_index_tie": rollover_tie,
            "all_erased_fallback": rollover_all_erased,
        },
        "closer": {
            "first_sequence": close_first,
            "minimum_not_maximum": close_minimum,
            "write_failure": close_write_failure,
        },
        "safety": {
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "partition_callbacks_intercepted": True,
            "fixture_partition_mutated": False,
            "ble_access": False,
            "sensor_access": False,
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
