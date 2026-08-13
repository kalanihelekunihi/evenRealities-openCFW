#!/usr/bin/env python3
"""Execute the R1 sleep.db record writer with all partition effects intercepted.

The production writer runs against private RAM. Header reads are served from that fixture; body
and header writes plus the sector closer are recorded and returned without mutation. No physical
ring, flash, BLE stack, sensor, or host health store is reachable.
"""

from __future__ import annotations

import argparse
import hashlib
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


WRITER = 0x0008FE98
CLOSER = 0x000901E4
CRC16_MODBUS = 0x0005D87C
LOG_FLAGS = 0x000914EC

STORAGE_GLOBAL = 0x200067B4
PARTITION = RAM_BASE + 0x48000
RECORD = RAM_BASE + 0x51000
DESCRIPTOR = RAM_BASE + 0x53000
OPERATIONS = RAM_BASE + 0x53100
READ_STUB = RAM_BASE + 0x53200
WRITE_STUB = RAM_BASE + 0x53210
ERASE_STUB = RAM_BASE + 0x53220

SECTOR_BYTES = 0x1000
SECTOR_COUNT = 2
HEADER_BYTES = 24
HEADER_START = 0x10
DATA_START = 0xD0
FULL0 = 0xCCFFAABB
FULL1 = 0x66889977
ERASED = 0xFFFFFFFF


class SleepRecordWriterFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.write_results: list[int] = []
        self.close_result = 1
        self.read_calls: list[tuple[int, int]] = []
        self.write_calls: list[tuple[int, bytes]] = []
        self.close_calls: list[int] = []
        self.crc_calls: list[int] = []

        self.machine.uc.mem_write(PARTITION, b"\xff" * (SECTOR_BYTES * SECTOR_COUNT))
        self.machine.uc.mem_write(RECORD, b"\x00" * 0x2000)
        self.machine.uc.mem_write(DESCRIPTOR, b"\x00" * 0x80)
        self.machine.uc.mem_write(OPERATIONS, b"\x00" * 0x80)
        self.machine.uc.mem_write(STORAGE_GLOBAL + 4, struct.pack("<I", DESCRIPTOR))
        self.machine.uc.mem_write(STORAGE_GLOBAL + 8, struct.pack("<I", OPERATIONS))
        self.machine.uc.mem_write(DESCRIPTOR + 0x34, struct.pack("<I", PARTITION))
        self.machine.uc.mem_write(
            DESCRIPTOR + 0x38,
            struct.pack("<I", SECTOR_BYTES * SECTOR_COUNT),
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

    @staticmethod
    def _crc16_modbus(data: bytes) -> int:
        crc = 0xFFFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
        return crc

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
            uc.mem_write(destination, bytes(uc.mem_read(source, length)))
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
            if not self.write_results:
                raise RuntimeError("unexpected partition write")
            self._return(uc, self.write_results.pop(0))
        elif address == CLOSER:
            self.close_calls.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc, self.close_result)
        elif address == CRC16_MODBUS:
            source = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            self.crc_calls.append(length)
            self._return(
                uc,
                self._crc16_modbus(bytes(uc.mem_read(source, length))),
            )
        elif address == ERASE_STUB:
            raise RuntimeError("record writer unexpectedly requested erase")

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

    @staticmethod
    def record_header(
        *,
        aligned_length: int,
        payload_offset: int,
        start: int,
        end: int,
    ) -> bytes:
        data = bytearray(b"\xff" * HEADER_BYTES)
        struct.pack_into("<HH", data, 0, aligned_length, payload_offset)
        struct.pack_into("<II", data, 8, start, end)
        return bytes(data)

    @staticmethod
    def vacant_header() -> bytes:
        return b"\xff" * HEADER_BYTES

    def set_headers(self, sector: int, headers: list[bytes]) -> None:
        if len(headers) != 8 or any(len(value) != HEADER_BYTES for value in headers):
            raise ValueError("fixture requires eight 24-byte headers")
        self.machine.uc.mem_write(PARTITION, b"\xff" * (SECTOR_BYTES * SECTOR_COUNT))
        for index, value in enumerate(headers):
            self.machine.uc.mem_write(
                PARTITION + sector * SECTOR_BYTES + HEADER_START + index * HEADER_BYTES,
                value,
            )

    def set_record(self, length: int) -> bytes:
        aligned = (length + 3) & 0xFFFC
        payload = bytearray((index & 0xFF) for index in range(max(aligned, 20)))
        struct.pack_into("<HII", payload, 10, 0xFE98, 1_000, 4_600)
        self.machine.uc.mem_write(RECORD, bytes(payload))
        return bytes(payload)

    def run(
        self,
        *,
        sector: int,
        headers: list[bytes],
        length: int,
        write_results: list[int] | None = None,
        close_result: int = 1,
    ) -> dict[str, Any]:
        self.set_headers(sector, headers)
        payload = self.set_record(length)
        before = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT))
        self.write_results = list(write_results or [])
        self.close_result = close_result
        self.read_calls.clear()
        self.write_calls.clear()
        self.close_calls.clear()
        self.crc_calls.clear()
        result = self.machine.call(WRITER, sector, RECORD, length)
        after = bytes(self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT))
        if self.write_results:
            raise AssertionError("fixture supplied unused write results")

        def describe_write(address: int, value: bytes) -> dict[str, Any]:
            result: dict[str, Any] = {
                "offset": address - PARTITION,
                "length": len(value),
                "sha256": hashlib.sha256(value).hexdigest(),
            }
            if len(value) <= 64:
                result["hex"] = value.hex()
            else:
                result["head_hex"] = value[:16].hex()
                result["tail_hex"] = value[-16:].hex()
            return result

        return {
            "return_raw": result,
            "requested_length": length,
            "aligned_length": (length + 3) & 0xFFFC,
            "source_bytes": len(payload),
            "source_head_hex": payload[:20].hex(),
            "source_sha256": hashlib.sha256(payload).hexdigest(),
            "read_offsets": [address - PARTITION for address, _ in self.read_calls],
            "write_calls": [
                describe_write(address, value)
                for address, value in self.write_calls
            ],
            "close_calls": list(self.close_calls),
            "crc_lengths": list(self.crc_calls),
            "partition_unchanged": before == after,
        }


def occupied(fixture: SleepRecordWriterFixture, offset: int, length: int = 32) -> bytes:
    return fixture.record_header(
        aligned_length=length,
        payload_offset=offset,
        start=1,
        end=2,
    )


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepRecordWriterFixture(image)
    vacant = fixture.vacant_header()
    empty = [vacant] * 8

    first = fixture.run(
        sector=0,
        headers=empty,
        length=33,
        write_results=[0, 0],
    )
    second = fixture.run(
        sector=1,
        headers=[occupied(fixture, DATA_START, 36)] + [vacant] * 7,
        length=33,
        write_results=[0, 0],
    )
    asymmetric = fixture.run(
        sector=0,
        headers=[
            fixture.record_header(
                aligned_length=36,
                payload_offset=DATA_START,
                start=ERASED,
                end=2,
            )
        ] + [vacant] * 7,
        length=33,
        write_results=[0, 0],
    )
    all_occupied = fixture.run(
        sector=0,
        headers=[occupied(fixture, DATA_START + index * 32) for index in range(8)],
        length=33,
    )
    capacity = fixture.run(
        sector=0,
        headers=[occupied(fixture, 0xFF0, 16)] + [vacant] * 7,
        length=33,
    )
    body_failure = fixture.run(
        sector=0,
        headers=empty,
        length=33,
        write_results=[7],
    )
    header_failure = fixture.run(
        sector=0,
        headers=empty,
        length=33,
        write_results=[0, 8],
    )
    final_headers = [
        occupied(fixture, DATA_START + index * 32) for index in range(7)
    ] + [vacant]
    final_success = fixture.run(
        sector=0,
        headers=final_headers,
        length=33,
        write_results=[0, 0],
        close_result=1,
    )
    final_close_failure = fixture.run(
        sector=0,
        headers=final_headers,
        length=33,
        write_results=[0, 0],
        close_result=0,
    )
    maximum = fixture.run(
        sector=0,
        headers=empty,
        length=3_888,
        write_results=[0, 0],
    )
    oversized = fixture.run(
        sector=0,
        headers=empty,
        length=3_889,
    )

    assert first["return_raw"] == 1
    assert first["aligned_length"] == 36
    assert first["read_offsets"] == [HEADER_START]
    assert [call["offset"] for call in first["write_calls"]] == [DATA_START, HEADER_START]
    assert [call["length"] for call in first["write_calls"]] == [36, 20]
    header = bytes.fromhex(first["write_calls"][1]["hex"])
    assert struct.unpack_from("<HH", header, 0) == (36, DATA_START)
    assert struct.unpack_from("<H", header, 6)[0] == 0xFE98
    assert struct.unpack_from("<II", header, 8) == (1_000, 4_600)
    assert header[4:6] == b"\xff\xff"
    assert header[16:18] == b"\xff\xff"
    assert first["close_calls"] == []
    assert first["crc_lengths"] == [36]

    assert second["return_raw"] == 1
    assert second["read_offsets"] == [0x1010, 0x1028]
    assert [call["offset"] for call in second["write_calls"]] == [0x10F4, 0x1028]
    assert asymmetric["read_offsets"] == [0x10, 0x28]
    assert asymmetric["write_calls"][1]["offset"] == 0x28

    assert all_occupied["return_raw"] == 0
    assert len(all_occupied["read_offsets"]) == 8
    assert all_occupied["write_calls"] == []
    assert all_occupied["close_calls"] == []
    assert all_occupied["crc_lengths"] == []

    assert capacity["return_raw"] == 0
    assert capacity["write_calls"] == []
    assert capacity["close_calls"] == [0]
    assert capacity["crc_lengths"] == []

    assert body_failure["return_raw"] == 0
    assert len(body_failure["write_calls"]) == 1
    assert body_failure["close_calls"] == []
    assert body_failure["crc_lengths"] == []
    assert header_failure["return_raw"] == 0
    assert len(header_failure["write_calls"]) == 2
    assert header_failure["close_calls"] == []
    assert header_failure["crc_lengths"] == [36]

    assert final_success["return_raw"] == 1
    assert final_success["close_calls"] == [0]
    assert final_close_failure["return_raw"] == 0
    assert final_close_failure["close_calls"] == [0]

    assert maximum["return_raw"] == 1
    assert maximum["aligned_length"] == 3_888
    assert [call["offset"] for call in maximum["write_calls"]] == [DATA_START, HEADER_START]
    assert maximum["write_calls"][0]["length"] == 3_888
    assert maximum["crc_lengths"] == [3_888]
    assert oversized["return_raw"] == 0
    assert oversized["aligned_length"] == 3_892
    assert oversized["write_calls"] == []
    assert oversized["close_calls"] == [0]

    for result in (
        first, second, asymmetric, all_occupied, capacity, body_failure,
        header_failure, final_success, final_close_failure, maximum, oversized,
    ):
        assert result["partition_unchanged"]

    return {
        "fixture_groups": 11,
        "first_slot_commit": first,
        "second_sector_second_slot": second,
        "one_erased_timestamp_is_occupied": asymmetric,
        "all_headers_occupied": all_occupied,
        "capacity_close": capacity,
        "body_write_failure": body_failure,
        "header_write_failure_after_body": header_failure,
        "final_slot_close_success": final_success,
        "final_slot_close_failure": final_close_failure,
        "accepted_3888_boundary": maximum,
        "direct_3889_capacity_failure": oversized,
        "safety": {
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "partition_callbacks_intercepted": True,
            "sector_closer_intercepted": True,
            "crc_intercepted_with_modbus_reference": True,
            "fixture_partition_mutated": False,
            "captured_health_payload_emitted": False,
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
