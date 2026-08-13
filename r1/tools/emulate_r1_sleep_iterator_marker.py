#!/usr/bin/env python3
"""Execute the R1 sleep.db iterator and marker writer against private emulated RAM.

All allocation, partition read/write, CRC, event, callback, and logging effects are intercepted.
The production routines cannot reach a ring, BLE, sensors, physical flash, or a host health store.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path
from typing import Any

from unicorn.arm_const import (
    UC_ARM_REG_LR,
    UC_ARM_REG_PC,
    UC_ARM_REG_R0,
    UC_ARM_REG_R1,
    UC_ARM_REG_R2,
    UC_ARM_REG_R3,
)

from emulate_r1_locomotion_window import RAM_BASE
from emulate_r1_sleep_sector_policy import (
    PARTITION,
    READ_STUB,
    SECTOR_BYTES,
    SECTOR_COUNT_RAW,
    WRITE_STUB,
    SleepSectorPolicyFixture,
)


ITERATOR = 0x0005B39C
MARKER_WRITER = 0x0005B6F4
CRC16_MODBUS = 0x0005D87C
MALLOC = 0x000855A0
FREE = 0x00095D48
SYSTEM_EVENT = 0x0008D8FC
LOG_FLAGS = 0x000914EC
LOG_STRUCTURED = 0x00091638
LOG_TEXT = 0x000799C0
LOG_TEXT_ARGS = 0x000799C8

CALLBACK_STUB = RAM_BASE + 0x53300
ALLOCATION = RAM_BASE + 0x54000
CONTEXTS = RAM_BASE + 0x55000
ARBITRARY_HEADER = RAM_BASE + 0x57000

HEADER_BYTES = 24
HEADER_START = 0x10
DATA_START = 0xD0
MARKER = 0x11223344
ERASED = 0xFFFFFFFF


class SleepIteratorMarkerFixture(SleepSectorPolicyFixture):
    def __init__(self, image: bytes) -> None:
        self.malloc_succeeds = True
        self.read_results: list[int] = []
        self.write_results: list[int] = []
        self.callback_results: list[int] = []
        self.malloc_calls: list[int] = []
        self.free_calls: list[int] = []
        self.read_observations: list[tuple[int, int, int]] = []
        self.write_observations: list[tuple[int, bytes, int]] = []
        self.callback_observations: list[dict[str, Any]] = []
        self.event_calls: list[tuple[int, int]] = []
        self.crc_lengths: list[int] = []
        self.log_calls: list[int] = []
        super().__init__(image)
        self.machine.uc.mem_write(ALLOCATION, b"\x00" * 0x1000)
        self.machine.uc.mem_write(CONTEXTS, b"\x00" * 0x2000)
        self.machine.uc.mem_write(ARBITRARY_HEADER, b"\xff" * HEADER_BYTES)

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

    @staticmethod
    def _is_fixture_read(address: int, length: int) -> bool:
        partition_end = PARTITION + SECTOR_BYTES * SECTOR_COUNT_RAW
        return (
            PARTITION <= address
            and address + length <= partition_end
        ) or (
            ARBITRARY_HEADER <= address
            and address + length <= ARBITRARY_HEADER + HEADER_BYTES
        )

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == MALLOC:
            requested = uc.reg_read(UC_ARM_REG_R0)
            self.malloc_calls.append(requested)
            self._return(uc, ALLOCATION if self.malloc_succeeds else 0)
        elif address == FREE:
            self.free_calls.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc, 0)
        elif address == READ_STUB:
            source = uc.reg_read(UC_ARM_REG_R0)
            destination = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            if not self._is_fixture_read(source, length):
                raise RuntimeError(
                    f"out-of-fixture storage read at 0x{source:08x} length {length}"
                )
            uc.mem_write(destination, bytes(uc.mem_read(source, length)))
            result = self.read_results.pop(0) if self.read_results else 0
            self.read_observations.append((source, length, result))
            self._return(uc, result)
        elif address == WRITE_STUB:
            destination = uc.reg_read(UC_ARM_REG_R0)
            source = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            payload = bytes(uc.mem_read(source, length))
            result = self.write_results.pop(0) if self.write_results else 0
            self.write_observations.append((destination, payload, result))
            self._return(uc, result)
        elif address == CRC16_MODBUS:
            source = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            payload = bytes(uc.mem_read(source, length))
            self.crc_lengths.append(length)
            self._return(uc, self._crc16_modbus(payload))
        elif address == SYSTEM_EVENT:
            self.event_calls.append((
                uc.reg_read(UC_ARM_REG_R0),
                uc.reg_read(UC_ARM_REG_R1),
            ))
            self._return(uc, 0)
        elif address == CALLBACK_STUB:
            metadata = uc.reg_read(UC_ARM_REG_R0)
            payload = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            caller_context = uc.reg_read(UC_ARM_REG_R3)
            self.callback_observations.append({
                "metadata_hex": bytes(uc.mem_read(metadata, 8)).hex(),
                "payload_hex": bytes(uc.mem_read(payload, length)).hex(),
                "length": length,
                "caller_context_raw": caller_context,
            })
            result = self.callback_results.pop(0) if self.callback_results else 1
            self._return(uc, result)
        elif address in (LOG_FLAGS, LOG_STRUCTURED, LOG_TEXT, LOG_TEXT_ARGS):
            self.log_calls.append(address)
            self._return(uc, 0)
        else:
            super()._hook(uc, address, 0, None)

    def reset_observations(self) -> None:
        super().reset_observations()
        self.malloc_calls.clear()
        self.free_calls.clear()
        self.read_observations.clear()
        self.write_observations.clear()
        self.callback_observations.clear()
        self.event_calls.clear()
        self.crc_lengths.clear()
        self.log_calls.clear()

    @classmethod
    def header(
        cls,
        *,
        aligned_length: int,
        payload_offset: int,
        start: int,
        end: int,
        payload: bytes,
        marker: int = ERASED,
        crc_override: int | None = None,
    ) -> bytes:
        result = bytearray(b"\xff" * HEADER_BYTES)
        crc = cls._crc16_modbus(payload[:aligned_length])
        if crc_override is not None:
            crc = crc_override
        struct.pack_into("<HH", result, 0, aligned_length, payload_offset)
        struct.pack_into("<II", result, 8, start, end)
        struct.pack_into("<H", result, 18, crc)
        struct.pack_into("<I", result, 20, marker)
        return bytes(result)

    def clear_partition(self) -> None:
        self.machine.uc.mem_write(
            PARTITION,
            b"\xff" * (SECTOR_BYTES * SECTOR_COUNT_RAW),
        )

    def write_record(
        self,
        *,
        sector: int,
        slot: int,
        payload: bytes,
        payload_offset: int,
        aligned_length: int | None = None,
        start: int = 1_000,
        end: int = 4_600,
        marker: int = ERASED,
        crc_override: int | None = None,
    ) -> int:
        length = len(payload) if aligned_length is None else aligned_length
        if len(payload) < length:
            payload = payload + b"\x00" * (length - len(payload))
        header_address = (
            PARTITION
            + sector * SECTOR_BYTES
            + HEADER_START
            + slot * HEADER_BYTES
        )
        payload_address = PARTITION + sector * SECTOR_BYTES + payload_offset
        self.machine.uc.mem_write(payload_address, payload[:length])
        self.machine.uc.mem_write(
            header_address,
            self.header(
                aligned_length=length,
                payload_offset=payload_offset,
                start=start,
                end=end,
                payload=payload,
                marker=marker,
                crc_override=crc_override,
            ),
        )
        return header_address

    def iterator(
        self,
        *,
        skip_synchronized_raw: int,
        callback_available: bool = True,
        malloc_succeeds: bool = True,
        callback_results: list[int] | None = None,
        read_results: list[int] | None = None,
        caller_context_raw: int = 0x12345678,
    ) -> dict[str, Any]:
        before = bytes(
            self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW)
        )
        self.malloc_succeeds = malloc_succeeds
        self.callback_results = list(callback_results or [])
        self.read_results = list(read_results or [])
        self.write_results = []
        self.reset_observations()
        result = self.machine.call(
            ITERATOR,
            skip_synchronized_raw,
            CALLBACK_STUB | 1 if callback_available else 0,
            caller_context_raw,
        )
        after = bytes(
            self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW)
        )
        if self.callback_results:
            raise AssertionError("fixture supplied unused callback results")
        if self.read_results:
            raise AssertionError("fixture supplied unused read results")
        return {
            "return_raw": result,
            "malloc_requests": list(self.malloc_calls),
            "free_pointers": list(self.free_calls),
            "read_calls": [
                {
                    "address": f"0x{address:08x}",
                    "offset": address - PARTITION,
                    "length": length,
                    "supplied_result_raw": supplied,
                }
                for address, length, supplied in self.read_observations
            ],
            "callbacks": list(self.callback_observations),
            "crc_lengths": list(self.crc_lengths),
            "events": [
                [f"0x{identifier:04x}", f"0x{argument:08x}"]
                for identifier, argument in self.event_calls
            ],
            "partition_unchanged": before == after,
        }

    def marker(
        self,
        data: bytes,
        *,
        byte_count: int | None = None,
        null_buffer: bool = False,
        read_results: list[int] | None = None,
        write_results: list[int] | None = None,
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(CONTEXTS, data or b"\x00")
        before_partition = bytes(
            self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW)
        )
        before_arbitrary = bytes(self.machine.uc.mem_read(ARBITRARY_HEADER, HEADER_BYTES))
        self.read_results = list(read_results or [])
        self.write_results = list(write_results or [])
        self.callback_results = []
        self.reset_observations()
        self.machine.call(
            MARKER_WRITER,
            0 if null_buffer else CONTEXTS,
            len(data) if byte_count is None else byte_count,
        )
        after_partition = bytes(
            self.machine.uc.mem_read(PARTITION, SECTOR_BYTES * SECTOR_COUNT_RAW)
        )
        after_arbitrary = bytes(self.machine.uc.mem_read(ARBITRARY_HEADER, HEADER_BYTES))
        if self.read_results:
            raise AssertionError("fixture supplied unused read results")
        if self.write_results:
            raise AssertionError("fixture supplied unused write results")
        return {
            "read_calls": [
                {
                    "address": f"0x{address:08x}",
                    "length": length,
                    "supplied_result_raw": supplied,
                }
                for address, length, supplied in self.read_observations
            ],
            "write_calls": [
                {
                    "address": f"0x{address:08x}",
                    "length": len(payload),
                    "hex": payload.hex(),
                    "supplied_result_raw": supplied,
                }
                for address, payload, supplied in self.write_observations
            ],
            "partition_unchanged": before_partition == after_partition,
            "arbitrary_header_unchanged": before_arbitrary == after_arbitrary,
        }


def context(address: int, start: int, end: int) -> bytes:
    return struct.pack("<III", address, start, end)


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepIteratorMarkerFixture(image)

    fixture.clear_partition()
    null_callback = fixture.iterator(
        skip_synchronized_raw=0,
        callback_available=False,
    )

    fixture.clear_partition()
    allocation_failure = fixture.iterator(
        skip_synchronized_raw=0,
        malloc_succeeds=False,
    )

    fixture.clear_partition()
    empty = fixture.iterator(skip_synchronized_raw=0)

    fixture.clear_partition()
    synced_address = fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\x10\x11\x12\x13\x14\x15\x16\x17",
        payload_offset=DATA_START,
        marker=MARKER,
    )
    unsynced_address = fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\x20\x21\x22\x23\x24\x25\x26\x27",
        payload_offset=DATA_START + 8,
    )
    include_all = fixture.iterator(skip_synchronized_raw=0)
    skip_synchronized = fixture.iterator(skip_synchronized_raw=2)

    fixture.clear_partition()
    fixture.write_record(
        sector=0,
        slot=0,
        payload=bytes(index & 0xFF for index in range(236)),
        payload_offset=DATA_START,
    )
    oversized_followed_by_valid_address = fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\x31\x32\x33\x34\x35\x36\x37\x38",
        payload_offset=DATA_START + 236,
    )
    oversized_is_skipped = fixture.iterator(skip_synchronized_raw=0)

    fixture.clear_partition()
    fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\x41\x42\x43\x44\x45\x46\x47\x48",
        payload_offset=DATA_START,
        crc_override=0,
    )
    fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\x51\x52\x53\x54\x55\x56\x57\x58",
        payload_offset=DATA_START + 8,
    )
    crc_failure = fixture.iterator(skip_synchronized_raw=0)

    fixture.clear_partition()
    fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\x61\x62\x63\x64\x65\x66\x67\x68",
        payload_offset=DATA_START,
    )
    fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\x71\x72\x73\x74\x75\x76\x77\x78",
        payload_offset=DATA_START + 8,
    )
    callback_stop_is_success = fixture.iterator(
        skip_synchronized_raw=0,
        callback_results=[0],
    )

    fixture.clear_partition()
    fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\x81" * 8,
        payload_offset=DATA_START,
        start=ERASED,
        end=4_600,
    )
    fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\x82" * 8,
        payload_offset=DATA_START + 8,
    )
    second_sector_address = fixture.write_record(
        sector=1,
        slot=0,
        payload=b"\x83" * 8,
        payload_offset=DATA_START,
    )
    either_erased_timestamp_stops_sector = fixture.iterator(skip_synchronized_raw=0)

    fixture.clear_partition()
    ignored_read_result_address = fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\x91\x92\x93\x94\x95\x96\x97\x98",
        payload_offset=DATA_START,
    )
    nonzero_read_results_are_ignored = fixture.iterator(
        skip_synchronized_raw=0,
        read_results=[7, 8, 9],
    )

    fixture.clear_partition()
    marker_address0 = fixture.write_record(
        sector=0,
        slot=0,
        payload=b"\xa1" * 8,
        payload_offset=DATA_START,
        start=10,
        end=20,
    )
    marker_address1 = fixture.write_record(
        sector=0,
        slot=1,
        payload=b"\xa2" * 8,
        payload_offset=DATA_START + 8,
        start=30,
        end=40,
    )
    marker_null = fixture.marker(
        context(marker_address0, 10, 20),
        null_buffer=True,
    )
    marker_zero_count = fixture.marker(
        context(marker_address0, 10, 20),
        byte_count=0,
    )
    marker_partial_tail = fixture.marker(
        context(marker_address0, 10, 20) + b"\xee",
        write_results=[0],
    )
    marker_mismatch = fixture.marker(context(marker_address0, 11, 20))
    marker_failure_continues = fixture.marker(
        context(marker_address0, 10, 20)
        + context(marker_address1, 30, 40),
        write_results=[9, 0],
    )
    marker_count_wrap = fixture.marker(b"\x00" * 3_072)

    arbitrary_header = fixture.header(
        aligned_length=8,
        payload_offset=DATA_START,
        start=50,
        end=60,
        payload=b"\x00" * 8,
    )
    fixture.machine.uc.mem_write(ARBITRARY_HEADER, arbitrary_header)
    marker_arbitrary_address = fixture.marker(
        context(ARBITRARY_HEADER, 50, 60),
        write_results=[0],
    )

    assert null_callback["return_raw"] == 0
    assert null_callback["malloc_requests"] == []
    assert allocation_failure["return_raw"] == 0
    assert allocation_failure["malloc_requests"] == [232]
    assert allocation_failure["free_pointers"] == []

    assert empty["return_raw"] == 1
    assert [item["offset"] for item in empty["read_calls"]] == [0x10, 0x1010]
    assert empty["callbacks"] == []
    assert empty["free_pointers"] == [ALLOCATION]

    assert include_all["return_raw"] == 1
    assert len(include_all["callbacks"]) == 2
    assert include_all["callbacks"][0]["metadata_hex"] == (
        "01000000" + struct.pack("<I", synced_address).hex()
    )
    assert include_all["callbacks"][1]["metadata_hex"] == (
        "00000000" + struct.pack("<I", unsynced_address).hex()
    )
    assert include_all["callbacks"][0]["caller_context_raw"] == 0x12345678
    assert len(skip_synchronized["callbacks"]) == 1
    assert skip_synchronized["callbacks"][0]["metadata_hex"] == (
        "00000000" + struct.pack("<I", unsynced_address).hex()
    )

    assert oversized_is_skipped["return_raw"] == 1
    assert len(oversized_is_skipped["callbacks"]) == 1
    assert oversized_is_skipped["callbacks"][0]["metadata_hex"].endswith(
        struct.pack("<I", oversized_followed_by_valid_address).hex()
    )
    assert oversized_is_skipped["crc_lengths"] == [8]

    assert crc_failure["return_raw"] == 0
    assert crc_failure["callbacks"] == []
    assert crc_failure["events"] == [["0x2002", "0x00000000"]]
    assert crc_failure["free_pointers"] == [ALLOCATION]

    assert callback_stop_is_success["return_raw"] == 1
    assert len(callback_stop_is_success["callbacks"]) == 1
    assert callback_stop_is_success["free_pointers"] == [ALLOCATION]

    assert either_erased_timestamp_stops_sector["return_raw"] == 1
    assert len(either_erased_timestamp_stops_sector["callbacks"]) == 1
    assert either_erased_timestamp_stops_sector["callbacks"][0][
        "metadata_hex"
    ].endswith(struct.pack("<I", second_sector_address).hex())

    assert nonzero_read_results_are_ignored["return_raw"] == 1
    assert len(nonzero_read_results_are_ignored["callbacks"]) == 1
    assert nonzero_read_results_are_ignored["callbacks"][0][
        "metadata_hex"
    ].endswith(struct.pack("<I", ignored_read_result_address).hex())
    assert [
        item["supplied_result_raw"]
        for item in nonzero_read_results_are_ignored["read_calls"]
    ] == [7, 8, 9, 0]

    assert marker_null["read_calls"] == []
    assert marker_zero_count["read_calls"] == []
    assert len(marker_partial_tail["read_calls"]) == 1
    assert marker_partial_tail["write_calls"] == [{
        "address": f"0x{marker_address0 + 20:08x}",
        "length": 4,
        "hex": struct.pack("<I", MARKER).hex(),
        "supplied_result_raw": 0,
    }]
    assert marker_mismatch["write_calls"] == []
    assert [item["supplied_result_raw"] for item in marker_failure_continues[
        "write_calls"
    ]] == [9, 0]
    assert marker_count_wrap["read_calls"] == []
    assert marker_count_wrap["write_calls"] == []
    assert marker_arbitrary_address["read_calls"][0]["address"] == (
        f"0x{ARBITRARY_HEADER:08x}"
    )
    assert marker_arbitrary_address["write_calls"][0]["address"] == (
        f"0x{ARBITRARY_HEADER + 20:08x}"
    )

    all_results = [
        null_callback,
        allocation_failure,
        empty,
        include_all,
        skip_synchronized,
        oversized_is_skipped,
        crc_failure,
        callback_stop_is_success,
        either_erased_timestamp_stops_sector,
        nonzero_read_results_are_ignored,
        marker_null,
        marker_zero_count,
        marker_partial_tail,
        marker_mismatch,
        marker_failure_continues,
        marker_count_wrap,
        marker_arbitrary_address,
    ]
    assert all(result["partition_unchanged"] for result in all_results)
    assert all(
        result.get("arbitrary_header_unchanged", True)
        for result in all_results
    )

    return {
        "fixture_groups": 17,
        "iterator": {
            "null_callback": null_callback,
            "allocation_failure": allocation_failure,
            "empty_partition": empty,
            "include_all": include_all,
            "skip_synchronized_nonzero": skip_synchronized,
            "oversized_skipped_then_continue": oversized_is_skipped,
            "crc_failure": crc_failure,
            "callback_stop_is_success": callback_stop_is_success,
            "either_erased_timestamp_stops_sector":
                either_erased_timestamp_stops_sector,
            "nonzero_read_results_are_ignored": nonzero_read_results_are_ignored,
        },
        "marker_writer": {
            "null_buffer": marker_null,
            "zero_count": marker_zero_count,
            "partial_tail_ignored": marker_partial_tail,
            "metadata_mismatch": marker_mismatch,
            "write_failure_continues": marker_failure_continues,
            "low_byte_count_wrap": marker_count_wrap,
            "arbitrary_address_not_validated": marker_arbitrary_address,
        },
        "safety": {
            "physical_device_access": False,
            "physical_flash_reads": False,
            "physical_flash_writes_or_erases": False,
            "allocation_intercepted": True,
            "partition_callbacks_intercepted": True,
            "crc_intercepted_with_modbus_reference": True,
            "system_event_intercepted": True,
            "iterator_callback_intercepted": True,
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
