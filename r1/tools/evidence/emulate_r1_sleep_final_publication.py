#!/usr/bin/env python3
"""Execute isolated production-Thumb final-sleep publication fixtures."""

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


VALIDATE_FINAL_SLEEP = 0x0004A3E8
LOW_POWER_HANDLER = 0x0004A5BC
PUBLISH_FINAL_SLEEP = 0x0004A704
BUILD_FINAL_SLEEP = 0x00069644
GOMORE_OUTPUT_CONSUMER = 0x0006C294

MEMSET = 0x000277AA
GOMORE_AUTHORIZATION = 0x00049410
GOMORE_FINAL_CONVERTER = 0x00067BBC
TABLE_RECORD = 0x000684B4
STAGE_REFINER = 0x00081040
GOMORE_OUTPUT_READY = 0x0006C1C0
GOMORE_OUTPUT_SYNC_BEGIN = 0x0006ACD8
GOMORE_OUTPUT_SYNC_END = 0x0006ACC8
ALLOCATE = 0x000855A0
SYSTEM_EVENT = 0x0008D8FC
FINAL_RECORD_LOOKUP = 0x0008FA3C
STABLE_SLEEP_TEMPERATURE = 0x0004B5B0
LOG_FLAGS = 0x000914EC
ENGINE_LOCK = 0x00094384
FREE = 0x00095D48
SLEEP_SHUTDOWN = 0x0004BD54
FORCED_FINALIZATION = 0x0006B50C

WEAR_RUNTIME = 0x20006E94
SLEEP_BRIDGE = 0x20006ED4
GOMORE_OUTPUT_STATE = 0x20006DC4
GOMORE_ENGINE = 0x2001A56C
RECORD = RAM_BASE + 0x43000
WORKSPACE = RAM_BASE + 0x45000
FINAL_REPORT = RAM_BASE + 0x54000
FINAL_STAGES = RAM_BASE + 0x54100
FINAL_ENGINE = RAM_BASE + 0x58000
FINAL_INTERVAL = RAM_BASE + 0x5A200
FINAL_BUILD_REPORT = RAM_BASE + 0x5A300
FINAL_BUILD_STAGES = RAM_BASE + 0x5A400
FINAL_BUILD_CONTEXT = RAM_BASE + 0x5A500


class SleepFinalFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.record_lookup_pointer = RECORD
        self.intercept_record_lookup = True
        self.body_temperature = 37
        self.allocation_pointer = WORKSPACE
        self.intercept_status_publisher = False
        self.intercept_final_publisher = False
        self.system_events: list[tuple[int, bytes]] = []
        self.status_publications: list[int] = []
        self.final_publication_requests = 0
        self.goMore_requests: list[tuple[int, int]] = []
        self.freed_pointers: list[int] = []
        self.sleep_shutdowns = 0
        self.forced_finalizations = 0
        self.allocation_lengths: list[int] = []
        self.stage_refine_calls = 0
        self.machine.uc.mem_write(WEAR_RUNTIME, b"\x00" * 32)
        self.machine.uc.mem_write(SLEEP_BRIDGE, b"\x00" * 12)
        self.machine.uc.mem_write(GOMORE_OUTPUT_STATE, b"\x00" * 0x80)
        self.machine.uc.mem_write(GOMORE_ENGINE, b"\x00" * 0x100)
        self.machine.uc.mem_write(RECORD, b"\x00" * 0x10000)
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
        elif address == FINAL_RECORD_LOOKUP and self.intercept_record_lookup:
            self._return(uc, self.record_lookup_pointer)
        elif address == STABLE_SLEEP_TEMPERATURE:
            self._return(uc, self.body_temperature)
        elif address == TABLE_RECORD:
            uc.mem_write(uc.reg_read(UC_ARM_REG_R0), b"\x00" * 11)
            self._return(uc)
        elif address == STAGE_REFINER:
            self.stage_refine_calls += 1
            self._return(uc)
        elif address == SYSTEM_EVENT:
            event_id = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            payload = bytes(uc.mem_read(pointer, length)) if length else b""
            self.system_events.append((event_id, payload))
            self._return(uc, 1)
        elif address == SLEEP_SHUTDOWN:
            self.sleep_shutdowns += 1
            self._return(uc)
        elif address == FORCED_FINALIZATION:
            self.forced_finalizations += 1
            self._return(uc)
        elif address == FREE:
            self.freed_pointers.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)
        elif address in (
            GOMORE_OUTPUT_SYNC_BEGIN,
            GOMORE_OUTPUT_SYNC_END,
            ENGINE_LOCK,
        ):
            self._return(uc)
        elif address == GOMORE_OUTPUT_READY:
            self._return(uc, 1)
        elif address == ALLOCATE:
            self.allocation_lengths.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc, self.allocation_pointer)
        elif address == MEMSET:
            pointer = uc.reg_read(UC_ARM_REG_R0)
            length = uc.reg_read(UC_ARM_REG_R1)
            uc.mem_write(pointer, b"\x00" * length)
            self._return(uc, pointer)
        elif address == GOMORE_FINAL_CONVERTER:
            self._return(uc)
        elif address == GOMORE_AUTHORIZATION:
            self.goMore_requests.append((
                uc.reg_read(UC_ARM_REG_R0),
                uc.reg_read(UC_ARM_REG_R1),
            ))
            self._return(uc, 1)
        elif address == 0x0004A7F4 and self.intercept_status_publisher:
            self.status_publications.append(uc.reg_read(UC_ARM_REG_R0) & 0xFF)
            self._return(uc)
        elif address == PUBLISH_FINAL_SLEEP and self.intercept_final_publisher:
            self.final_publication_requests += 1
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

    def reset_observations(self) -> None:
        self.system_events.clear()
        self.status_publications.clear()
        self.final_publication_requests = 0
        self.goMore_requests.clear()
        self.freed_pointers.clear()
        self.sleep_shutdowns = 0
        self.forced_finalizations = 0
        self.allocation_lengths.clear()
        self.stage_refine_calls = 0

    def write_record(self, raw_type: int, compact_count: int, body: bytes = b"") -> None:
        header = bytearray(32)
        header[0] = raw_type
        struct.pack_into("<H", header, 0x1E, compact_count)
        self.machine.uc.mem_write(RECORD, bytes(header) + body)

    def set_living_confirmation(self, raw: int) -> None:
        self.machine.uc.mem_write(WEAR_RUNTIME + 2, bytes([raw & 0xFF]))

    def serialize_final_record(self, wire_type: int) -> tuple[bytes, list[int]]:
        stages = bytes([1] * 64 + [2, 2])
        report = bytearray(88)
        struct.pack_into("<iiI", report, 0, -5, 0x12345678, FINAL_STAGES)
        struct.pack_into("<H", report, 0x10, len(stages))
        struct.pack_into("<f", report, 0x1C, 6.5)
        struct.pack_into("<f", report, 0x28, 0.876)
        struct.pack_into("<f", report, 0x34, 0.20)
        struct.pack_into("<f", report, 0x38, 0.50)
        struct.pack_into("<f", report, 0x3C, 0.15)
        struct.pack_into("<f", report, 0x40, 1.25)
        struct.pack_into("<f", report, 0x44, 2.5)
        struct.pack_into("<f", report, 0x48, 1.5)
        struct.pack_into("<f", report, 0x4C, 1.25)
        struct.pack_into("<f", report, 0x50, 93.9)
        report[0x54] = wire_type & 0xFF
        self.machine.uc.mem_write(FINAL_REPORT, bytes(report))
        self.machine.uc.mem_write(FINAL_STAGES, stages)
        self.machine.uc.mem_write(WORKSPACE, b"\xA5" * 64)
        self.reset_observations()
        self.intercept_record_lookup = False
        pointer = self.machine.call(FINAL_RECORD_LOOKUP, FINAL_REPORT)
        self.intercept_record_lookup = True
        if pointer != WORKSPACE:
            raise AssertionError(f"unexpected serialized pointer 0x{pointer:08x}")
        compact_count = struct.unpack(
            "<H", bytes(self.machine.uc.mem_read(WORKSPACE + 0x1E, 2))
        )[0]
        length = 0x20 + compact_count
        return bytes(self.machine.uc.mem_read(WORKSPACE, length)), list(self.allocation_lengths)

    def build_final_report(self) -> dict[str, Any]:
        engine = bytearray(0x2200)
        for epoch in range(30, 60):
            byte_index = epoch >> 2
            shift = (epoch & 3) << 1
            engine[byte_index] |= 2 << shift
        struct.pack_into("<I", engine, 0x2D0, 1800)
        interval = bytearray(32)
        struct.pack_into("<II", interval, 0, 900, 1800)
        interval[0x1A] = 0x18
        report = bytearray(88)
        struct.pack_into("<I", report, 8, FINAL_BUILD_STAGES)
        self.machine.uc.mem_write(FINAL_ENGINE, bytes(engine))
        self.machine.uc.mem_write(FINAL_INTERVAL, bytes(interval))
        self.machine.uc.mem_write(FINAL_BUILD_REPORT, bytes(report))
        self.machine.uc.mem_write(FINAL_BUILD_STAGES, b"\xA5" * 64)
        self.machine.uc.mem_write(FINAL_BUILD_CONTEXT, b"\x00" * 16)
        self.reset_observations()
        status = self.machine.call(
            BUILD_FINAL_SLEEP,
            FINAL_ENGINE,
            FINAL_BUILD_CONTEXT,
            FINAL_INTERVAL,
            0,
            FINAL_BUILD_REPORT,
        )
        output = bytes(self.machine.uc.mem_read(FINAL_BUILD_REPORT, 88))
        stage_count = struct.unpack_from("<I", output, 0x10)[0]
        stages = bytes(self.machine.uc.mem_read(FINAL_BUILD_STAGES, stage_count))
        return {
            "status": status,
            "wire_type": output[0x54],
            "start": struct.unpack_from("<I", output, 0)[0],
            "end": struct.unpack_from("<I", output, 4)[0],
            "stage_count": stage_count,
            "stages": list(stages),
            "report_float_fields": list(struct.unpack_from("<13f", output, 0x1C)),
            "score": struct.unpack_from("<f", output, 0x50)[0],
            "refine_calls": self.stage_refine_calls,
        }

    def lifecycle(
        self,
        flags: int,
        current_ppg_raw: int,
        previous_ppg_raw: int,
    ) -> dict[str, Any]:
        self.machine.uc.mem_write(GOMORE_OUTPUT_STATE, b"\x00" * 0x80)
        self.machine.uc.mem_write(GOMORE_ENGINE, b"\x00" * 0x100)
        self.machine.uc.mem_write(GOMORE_OUTPUT_STATE + 0x30, b"\x01")
        self.machine.uc.mem_write(
            GOMORE_OUTPUT_STATE + 0x40,
            bytes([previous_ppg_raw & 0xFF]),
        )
        self.machine.uc.mem_write(GOMORE_ENGINE + 0x70, bytes([flags & 0xFF]))
        self.machine.uc.mem_write(
            GOMORE_ENGINE + 0x62,
            bytes([current_ppg_raw & 0xFF]),
        )
        self.reset_observations()
        self.intercept_status_publisher = True
        self.intercept_final_publisher = True
        self.machine.call(GOMORE_OUTPUT_CONSUMER)
        self.intercept_status_publisher = False
        self.intercept_final_publisher = False
        return {
            "status_publications": list(self.status_publications),
            "final_publication_requests": self.final_publication_requests,
            "gomore_requests": [list(value) for value in self.goMore_requests],
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = SleepFinalFixture(image)

    built_report = fixture.build_final_report()
    serialized_long, serialized_long_allocations = fixture.serialize_final_record(1)
    serialized_short, serialized_short_allocations = fixture.serialize_final_record(2)

    fixture.write_record(2, 1, b"\x08")
    fixture.set_living_confirmation(0)
    no_living = fixture.machine.call(VALIDATE_FINAL_SLEEP, RECORD)
    fixture.set_living_confirmation(1)
    accepted_short = fixture.machine.call(VALIDATE_FINAL_SLEEP, RECORD)
    fixture.write_record(1, 0)
    empty_long = fixture.machine.call(VALIDATE_FINAL_SLEEP, RECORD)
    fixture.write_record(1, 1, b"\x08")
    nonempty_long = fixture.machine.call(VALIDATE_FINAL_SLEEP, RECORD)

    fixture.write_record(2, 2, b"\x08\x04")
    fixture.set_living_confirmation(1)
    fixture.reset_observations()
    fixture.machine.call(PUBLISH_FINAL_SLEEP, 1, 1)
    published_event = list(fixture.system_events)
    published_frees = list(fixture.freed_pointers)

    fixture.write_record(2, 2, b"\x08\x04")
    fixture.set_living_confirmation(0)
    fixture.reset_observations()
    fixture.machine.call(PUBLISH_FINAL_SLEEP, 1, 1)
    dropped_events = list(fixture.system_events)
    dropped_frees = list(fixture.freed_pointers)

    fixture.write_record(2, 0xFFE0)
    fixture.set_living_confirmation(1)
    fixture.reset_observations()
    fixture.machine.call(PUBLISH_FINAL_SLEEP, 1, 1)
    wrapping_event = list(fixture.system_events)

    bridge_tail = struct.pack("<BBHII", 1, 0xEF, 0xBEEF, 0x1111, 0x2222)
    fixture.machine.uc.mem_write(SLEEP_BRIDGE, bridge_tail)
    fixture.reset_observations()
    low_power_return = fixture.machine.call(LOW_POWER_HANDLER)
    low_power_state = bytes(fixture.machine.uc.mem_read(SLEEP_BRIDGE, 12))
    low_power_events = list(fixture.system_events)
    low_power_calls = (fixture.sleep_shutdowns, fixture.forced_finalizations)

    inactive = struct.pack("<BBHII", 2, 0xEF, 0xBEEF, 0x1111, 0x2222)
    fixture.machine.uc.mem_write(SLEEP_BRIDGE, inactive)
    fixture.reset_observations()
    inactive_return = fixture.machine.call(LOW_POWER_HANDLER)
    inactive_state = bytes(fixture.machine.uc.mem_read(SLEEP_BRIDGE, 12))

    lifecycle_off_final = fixture.lifecycle(0x0C, 1, 0)
    lifecycle_on_precedence = fixture.lifecycle(0x0E, 0, 1)
    lifecycle_no_change = fixture.lifecycle(0x00, 1, 3)
    fixture.allocation_pointer = 0
    lifecycle_allocation_failure = fixture.lifecycle(0x0C, 1, 0)
    fixture.allocation_pointer = WORKSPACE

    expected_long = bytes.fromhex(
        "01575d000f14320f25000000000000007856341286014b0096005a004b000300fd050a"
    )
    expected_short = bytes.fromhex(
        "0200000000000000000000000000000078563412000000000000000000000000"
    )

    assert serialized_long == expected_long
    assert serialized_short == expected_short
    assert serialized_long_allocations == [35]
    assert serialized_short_allocations == [35]
    assert built_report["status"] == 0
    assert built_report["wire_type"] == 1
    assert built_report["start"] == 900
    assert built_report["end"] == 1800
    assert built_report["stage_count"] == 30
    assert built_report["stages"] == [2] * 30
    assert built_report["report_float_fields"][0] == 15.0
    assert built_report["report_float_fields"][4] == 15.0
    assert built_report["report_float_fields"][5] == 0.0
    assert built_report["report_float_fields"][7] == 1.0
    assert built_report["report_float_fields"][11] == 15.0
    assert built_report["refine_calls"] == 1
    assert no_living == 0
    assert accepted_short == 1
    assert empty_long == 0
    assert nonempty_long == 1
    assert published_event == [(0x0D, bytes.fromhex("02000000000000000000000000000000000000000000000000000000000002000804"))]
    assert published_frees == [RECORD]
    assert dropped_events == []
    assert dropped_frees == [RECORD]
    assert wrapping_event == [(0x0D, b"")]
    assert low_power_return == 1
    assert low_power_state == struct.pack("<BBHII", 0, 0xEF, 0xBEEF, 0x1111, 0x2222)
    assert low_power_events == [(0x0C, b"\x00")]
    assert low_power_calls == (1, 1)
    assert inactive_return == 2
    assert inactive_state == inactive
    assert lifecycle_off_final == {
        "status_publications": [0],
        "final_publication_requests": 1,
        "gomore_requests": [[4, 1]],
    }
    assert lifecycle_on_precedence == {
        "status_publications": [1],
        "final_publication_requests": 0,
        "gomore_requests": [[4, 0]],
    }
    assert lifecycle_no_change == {
        "status_publications": [],
        "final_publication_requests": 0,
        "gomore_requests": [],
    }
    assert lifecycle_allocation_failure == {
        "status_publications": [0],
        "final_publication_requests": 0,
        "gomore_requests": [],
    }

    return {
        "fixture_groups": 9,
        "builder": built_report,
        "serializer": {
            "long_hex": serialized_long.hex(),
            "short_hex": serialized_short.hex(),
            "stock_allocation_bytes": serialized_long_allocations[0],
        },
        "validation": {
            "no_living": no_living,
            "accepted_short": accepted_short,
            "empty_long": empty_long,
            "nonempty_long": nonempty_long,
        },
        "publication": {
            "event_id": published_event[0][0],
            "payload_bytes": len(published_event[0][1]),
            "drop_still_frees_record": dropped_frees == [RECORD],
            "wrapping_length_bytes": len(wrapping_event[0][1]),
        },
        "low_power": {
            "return": low_power_return,
            "event": [low_power_events[0][0], list(low_power_events[0][1])],
            "shutdowns": low_power_calls[0],
            "finalizations": low_power_calls[1],
            "inactive_return": inactive_return,
        },
        "lifecycle": {
            "off_final": lifecycle_off_final,
            "on_precedence": lifecycle_on_precedence,
            "no_change": lifecycle_no_change,
            "allocation_failure": lifecycle_allocation_failure,
        },
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
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
