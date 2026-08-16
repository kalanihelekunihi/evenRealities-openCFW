#!/usr/bin/env python3
"""Assert the stock 0x6BBB0 pKey-page previous-state append contract.

The harness executes the SHA-pinned production Thumb routine with synthetic RAM and an
in-memory 4 KiB flash page.  All flash, allocation, free, and log calls are intercepted; it
has no device, BLE, filesystem-write, or physical-flash access.
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
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
)

from emulate_r1_locomotion_window import (
    LocomotionFirmwareFixture,
    RAM_BASE,
)


APPEND = 0x0006BBB0
LOG_ENABLED = 0x000914EC
ALLOCATE = 0x000855A0
FREE = 0x00095D48
STORE_STATE = 0x20006EE0
PARTITION_DESCRIPTOR = RAM_BASE + 0x12000
DEVICE_TABLE = RAM_BASE + 0x12100
READ_STUB = RAM_BASE + 0x12200
WRITE_STUB = RAM_BASE + 0x12210
ERASE_STUB = RAM_BASE + 0x12220
SOURCE = RAM_BASE + 0x12300
SCRATCH = RAM_BASE + 0x13000
PARTITION_OFFSET = 0x0000A000
PARTITION_BYTES = 0x1000


def u32(data: bytes) -> int:
    return struct.unpack("<I", data)[0]


class PreviousAppendFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.flash = bytearray(b"\xff" * PARTITION_BYTES)
        self.events: list[dict[str, Any]] = []
        self.allocation_sizes: list[int] = []
        self.free_calls = 0

        state = bytearray(12)
        state[0] = 1
        struct.pack_into("<II", state, 4, PARTITION_DESCRIPTOR, DEVICE_TABLE)
        self.machine.uc.mem_write(STORE_STATE, bytes(state))
        descriptor = bytearray(0x38)
        struct.pack_into("<I", descriptor, 0x34, PARTITION_OFFSET)
        self.machine.uc.mem_write(PARTITION_DESCRIPTOR, bytes(descriptor))
        table = bytearray(0x34)
        struct.pack_into("<III", table, 0x28,
                         READ_STUB | 1, WRITE_STUB | 1, ERASE_STUB | 1)
        self.machine.uc.mem_write(DEVICE_TABLE, bytes(table))
        self.machine.uc.mem_write(READ_STUB, b"\x70\x47")
        self.machine.uc.mem_write(WRITE_STUB, b"\x70\x47")
        self.machine.uc.mem_write(ERASE_STUB, b"\x70\x47")
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    def _return(self, value: int = 0) -> None:
        self.machine.uc.reg_write(UC_ARM_REG_R0, value)
        self.machine.uc.reg_write(
            UC_ARM_REG_PC, self.machine.uc.reg_read(UC_ARM_REG_LR)
        )

    def _flash_range(self, offset: int, length: int) -> tuple[int, int]:
        begin = offset - PARTITION_OFFSET
        end = begin + length
        if begin < 0 or end > len(self.flash):
            raise AssertionError(
                f"flash callback range 0x{offset:08x}+{length} is invalid"
            )
        return begin, end

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_ENABLED:
            self._return(0)
            return
        if address == ALLOCATE:
            length = uc.reg_read(UC_ARM_REG_R0)
            self.allocation_sizes.append(length)
            self._return(SCRATCH)
            return
        if address == FREE:
            self.free_calls += 1
            self._return(0)
            return
        if address == READ_STUB:
            offset = uc.reg_read(UC_ARM_REG_R0)
            destination = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            begin, end = self._flash_range(offset, length)
            uc.mem_write(destination, bytes(self.flash[begin:end]))
            self.events.append({"operation": "read", "offset": offset,
                                "length": length})
            self._return(length)
            return
        if address == WRITE_STUB:
            offset = uc.reg_read(UC_ARM_REG_R0)
            source = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            begin, end = self._flash_range(offset, length)
            self.flash[begin:end] = bytes(uc.mem_read(source, length))
            self.events.append({"operation": "write", "offset": offset,
                                "length": length})
            self._return(length)
            return
        if address == ERASE_STUB:
            offset = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            begin, end = self._flash_range(offset, length)
            self.flash[begin:end] = b"\xff" * length
            self.events.append({"operation": "erase", "offset": offset,
                                "length": length})
            self._return(0)

    def configure_key(self, length: int = 64) -> bytes:
        key_record = struct.pack("<II", length, 0x12345678) + bytes(
            (index + 1) & 0xFF for index in range((length + 3) & ~3)
        )
        self.flash[:len(key_record)] = key_record
        return key_record

    def append(self, source: bytes, declared_length: int) -> None:
        self.machine.uc.mem_write(SOURCE, source)
        self.machine.call(APPEND, SOURCE, declared_length)


def compact_events(events: list[dict[str, Any]]) -> list[tuple[str, int, int]]:
    return [(item["operation"], item["offset"], item["length"])
            for item in events]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()
    source = bytes([0x10, 0x20, 0x30, 0x40, 0x50, 0x60, 0x70, 0x80])

    fixture = PreviousAppendFixture(image)
    key_record = fixture.configure_key()
    fixture.append(source, 5)
    first_events = compact_events(fixture.events)
    assert first_events == [
        ("read", 0xA000, 8), ("read", 0xA068, 8),
        ("read", 0xA048, 8), ("write", 0xA048, 8),
        ("write", 0xA050, 8),
    ]
    assert u32(fixture.flash[72:76]) == 5
    assert u32(fixture.flash[76:80]) == 0
    assert fixture.flash[80:88] == source

    fixture.events.clear()
    fixture.append(source, 5)
    second_events = compact_events(fixture.events)
    assert second_events[-2:] == [("write", 0xA058, 8),
                                  ("write", 0xA060, 8)]
    fixture.events.clear()
    fixture.append(source, 5)
    third_events = compact_events(fixture.events)
    assert third_events[-2:] == [("write", 0xA068, 8),
                                 ("write", 0xA070, 8)]

    fixture.events.clear()
    fixture.append(source, 5)
    compaction_events = compact_events(fixture.events)
    assert compaction_events == [
        ("read", 0xA000, 8), ("read", 0xA068, 8),
        ("read", 0xA000, 72), ("erase", 0xA000, 4096),
        ("write", 0xA000, 72), ("write", 0xA048, 8),
        ("write", 0xA050, 8),
    ]
    assert fixture.allocation_sizes == [72]
    assert fixture.free_calls == 1
    assert fixture.flash[:72] == key_record
    assert u32(fixture.flash[72:76]) == 5
    assert u32(fixture.flash[88:92]) == 0xFFFFFFFF

    oversized = PreviousAppendFixture(image)
    oversized.configure_key()
    oversized.append(b"\x00" * 948, 945)
    assert compact_events(oversized.events) == [("read", 0xA000, 8)]

    null_input = PreviousAppendFixture(image)
    null_input.configure_key()
    null_input.machine.call(APPEND, 0, 8)
    assert null_input.events == []

    print(json.dumps({
        "function": "0x0006bbb0",
        "first_append": first_events,
        "second_append": second_events,
        "third_append": third_events,
        "compaction": compaction_events,
        "allocation_sizes": fixture.allocation_sizes,
        "free_calls": fixture.free_calls,
        "oversized_operations": compact_events(oversized.events),
        "null_input_operations": compact_events(null_input.events),
    }, indent=2))


if __name__ == "__main__":
    main()
