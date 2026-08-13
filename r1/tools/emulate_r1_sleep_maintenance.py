#!/usr/bin/env python3
"""Execute R1 sleep.db initialization, counting, and reset decisions in private RAM.

All partition lookup, flash-device lookup, read, erase, and logging calls are intercepted. The
fixture never mutates its private partition and cannot reach a ring, BLE, sensors, or health data.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import UC_ARM_REG_LR, UC_ARM_REG_PC, UC_ARM_REG_R0, UC_ARM_REG_R1

from emulate_r1_sleep_sector_policy import (
    DESCRIPTOR,
    ERASE_STUB,
    OPERATIONS,
    PARTITION,
    READ_STUB,
    SECTOR_BYTES,
    SECTOR_COUNT_RAW,
    STORAGE_GLOBAL,
    SleepSectorPolicyFixture,
)


INITIALIZE = 0x0005B0F8
DELETE_ALL = 0x0005B23C
FULL_RESET = 0x0005B2F8
RECORD_COUNT = 0x0005B32C
PARTITION_LOOKUP = 0x00063150
FLASH_DEVICE_LOOKUP = 0x00062DF4
LOG_FLAGS = 0x000914EC
LOG_STRUCTURED = 0x00091638
LOG_TEXT = 0x000799C0
LOG_TEXT_ARGS = 0x000799C8
LOG_TYPED = 0x00090FEC

ERASED = 0xFFFFFFFF


class SleepMaintenanceFixture(SleepSectorPolicyFixture):
    def __init__(self, image: bytes) -> None:
        self.partition_lookup_result = DESCRIPTOR
        self.device_lookup_result = OPERATIONS
        self.erase_results: list[int] = []
        self.lookup_calls: list[tuple[str, int]] = []
        self.log_calls: list[int] = []
        super().__init__(image)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == PARTITION_LOOKUP:
            self.lookup_calls.append(("partition", uc.reg_read(UC_ARM_REG_R0)))
            self._return(uc, self.partition_lookup_result)
        elif address == FLASH_DEVICE_LOOKUP:
            self.lookup_calls.append(("device", uc.reg_read(UC_ARM_REG_R0)))
            self._return(uc, self.device_lookup_result)
        elif address == ERASE_STUB:
            destination = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            self.erase_calls.append((destination, length))
            result = self.erase_results.pop(0) if self.erase_results else 0
            self._return(uc, result)
        elif address in (LOG_FLAGS, LOG_STRUCTURED, LOG_TEXT, LOG_TEXT_ARGS, LOG_TYPED):
            self.log_calls.append(address)
            self._return(uc, 0)
        else:
            super()._hook(uc, address, 0, None)

    def reset_observations(self) -> None:
        super().reset_observations()
        self.lookup_calls.clear()
        self.log_calls.clear()

    def runtime_state(self) -> dict[str, int]:
        raw = bytes(self.machine.uc.mem_read(STORAGE_GLOBAL, 12))
        initialized = raw[0]
        partition, device = struct.unpack_from("<II", raw, 4)
        return {
            "initialized_raw": initialized,
            "partition_handle_raw": partition,
            "flash_device_handle_raw": device,
        }

    def initialize(
        self,
        *,
        prior_initialized: int,
        prior_partition: int,
        prior_device: int,
        partition_found: bool,
        device_found: bool | None,
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(
            STORAGE_GLOBAL,
            bytes([prior_initialized, 0xA1, 0xB2, 0xC3])
            + struct.pack("<II", prior_partition, prior_device),
        )
        self.partition_lookup_result = DESCRIPTOR if partition_found else 0
        self.device_lookup_result = OPERATIONS if device_found else 0
        self.reset_observations()
        self.machine.call(INITIALIZE)
        return {
            "state": self.runtime_state(),
            "reserved_bytes": bytes(
                self.machine.uc.mem_read(STORAGE_GLOBAL + 1, 3)
            ).hex(),
            "lookup_kinds": [kind for kind, _ in self.lookup_calls],
            "log_call_count": len(self.log_calls),
        }

    def set_record_headers(self, sectors: list[list[tuple[int, int]]]) -> None:
        if len(sectors) != SECTOR_COUNT_RAW or any(len(items) != 8 for items in sectors):
            raise ValueError("fixture requires two sectors with eight timestamp pairs each")
        self.machine.uc.mem_write(STORAGE_GLOBAL + 4, struct.pack("<II", DESCRIPTOR, OPERATIONS))
        self.machine.uc.mem_write(PARTITION, b"\xff" * (SECTOR_BYTES * SECTOR_COUNT_RAW))
        for sector_index, records in enumerate(sectors):
            for slot_index, (start, end) in enumerate(records):
                header = bytearray(b"\xff" * 24)
                struct.pack_into("<II", header, 8, start, end)
                self.machine.uc.mem_write(
                    PARTITION
                    + sector_index * SECTOR_BYTES
                    + 0x10
                    + slot_index * 0x18,
                    bytes(header),
                )

    def count(self, sectors: list[list[tuple[int, int]]]) -> dict[str, Any]:
        self.set_record_headers(sectors)
        self.reset_observations()
        result = self.machine.call(RECORD_COUNT)
        return {
            "return_raw": result,
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "erase_calls": len(self.erase_calls),
        }

    def full_reset(self, erase_results: list[int]) -> dict[str, Any]:
        before = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW))
        self.erase_results = list(erase_results)
        self.reset_observations()
        self.machine.call(FULL_RESET)
        after = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW))
        return {
            "erase_calls": [
                [address - PARTITION, length] for address, length in self.erase_calls
            ],
            "unused_erase_results": list(self.erase_results),
            "partition_unchanged": before == after,
        }

    def delete_all(
        self,
        sectors: list[list[tuple[int, int]]],
        erase_results: list[int],
    ) -> dict[str, Any]:
        self.set_record_headers(sectors)
        before = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW))
        self.erase_results = list(erase_results)
        self.reset_observations()
        self.machine.call(DELETE_ALL)
        after = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW))
        return {
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "erase_calls": [
                [address - PARTITION, length] for address, length in self.erase_calls
            ],
            "unused_erase_results": list(self.erase_results),
            "partition_unchanged": before == after,
        }


def occupied(count: int) -> list[tuple[int, int]]:
    return [
        (1_000 + index * 100, 1_050 + index * 100) if index < count
        else (ERASED, ERASED)
        for index in range(8)
    ]


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepMaintenanceFixture(image)

    init_success = fixture.initialize(
        prior_initialized=0,
        prior_partition=0,
        prior_device=0,
        partition_found=True,
        device_found=True,
    )
    init_partition_missing = fixture.initialize(
        prior_initialized=0x7A,
        prior_partition=0x11111111,
        prior_device=0x22222222,
        partition_found=False,
        device_found=None,
    )
    init_device_missing = fixture.initialize(
        prior_initialized=0x6B,
        prior_partition=0x33333333,
        prior_device=0x44444444,
        partition_found=True,
        device_found=False,
    )

    count_empty = fixture.count([occupied(0), occupied(0)])
    count_split = fixture.count([occupied(2), occupied(1)])
    asymmetric = occupied(0)
    asymmetric[0] = (ERASED, 2_000)
    asymmetric[1] = (3_000, 4_000)
    count_asymmetric_stop = fixture.count([asymmetric, occupied(1)])
    count_full = fixture.count([occupied(8), occupied(8)])

    reset_success = fixture.full_reset([0, 0])
    reset_ignores_failures = fixture.full_reset([7, 8])
    delete_empty = fixture.delete_all([occupied(0), occupied(0)], [9, 10])
    delete_nonempty = fixture.delete_all([occupied(1), occupied(0)], [9, 10])

    assert init_success["state"] == {
        "initialized_raw": 1,
        "partition_handle_raw": DESCRIPTOR,
        "flash_device_handle_raw": OPERATIONS,
    }
    assert init_success["reserved_bytes"] == "a1b2c3"
    assert init_success["lookup_kinds"] == ["partition", "device"]

    assert init_partition_missing["state"] == {
        "initialized_raw": 0x7A,
        "partition_handle_raw": 0,
        "flash_device_handle_raw": 0x22222222,
    }
    assert init_partition_missing["lookup_kinds"] == ["partition"]

    assert init_device_missing["state"] == {
        "initialized_raw": 0x6B,
        "partition_handle_raw": 0,
        "flash_device_handle_raw": 0,
    }
    assert init_device_missing["lookup_kinds"] == ["partition", "device"]

    assert count_empty["return_raw"] == 0
    assert count_empty["read_offsets"] == [0x10, 0x1010], count_empty
    assert count_split["return_raw"] == 3
    assert count_split["read_offsets"] == [0x10, 0x28, 0x40, 0x1010, 0x1028], count_split
    assert count_asymmetric_stop["return_raw"] == 1
    assert count_asymmetric_stop["read_offsets"] == [0x10, 0x1010, 0x1028], (
        count_asymmetric_stop
    )
    assert count_full["return_raw"] == 16
    assert len(count_full["read_offsets"]) == 16

    expected_erases = [[0, SECTOR_BYTES], [SECTOR_BYTES, SECTOR_BYTES]]
    assert reset_success["erase_calls"] == expected_erases
    assert reset_success["unused_erase_results"] == []
    assert reset_success["partition_unchanged"]
    assert reset_ignores_failures["erase_calls"] == expected_erases
    assert reset_ignores_failures["unused_erase_results"] == []
    assert reset_ignores_failures["partition_unchanged"]
    assert delete_empty["erase_calls"] == []
    assert delete_empty["unused_erase_results"] == [9, 10]
    assert delete_empty["partition_unchanged"]
    assert delete_nonempty["erase_calls"] == expected_erases
    assert delete_nonempty["unused_erase_results"] == []
    assert delete_nonempty["partition_unchanged"]

    return {
        "fixture_groups": 11,
        "initialization_success": init_success,
        "initialization_partition_missing": init_partition_missing,
        "initialization_flash_device_missing": init_device_missing,
        "count_empty": count_empty,
        "count_split": count_split,
        "count_asymmetric_timestamp_stops_sector": count_asymmetric_stop,
        "count_full": count_full,
        "full_reset_success": reset_success,
        "full_reset_ignores_erase_failures": reset_ignores_failures,
        "delete_empty_skips_reset": delete_empty,
        "delete_nonempty_requests_reset": delete_nonempty,
        "safety": {
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "partition_callbacks_intercepted": True,
            "partition_fixture_mutated": False,
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
