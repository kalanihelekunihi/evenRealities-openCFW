#!/usr/bin/env python3
"""Execute the two production public activity handlers with transport calls stubbed.

The production Thumb handlers run in private emulated flash/RAM. BLE transmission, the internal
event queue, sensors, flash storage, a physical ring, and host health stores are not present.
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
    UC_ARM_REG_R3,
    UC_ARM_REG_SP,
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


ALL_DAY_HANDLER = 0x00082C10
DAILY_HANDLER = 0x00082C44
IMMEDIATE_RESPONSE = 0x00082844
INTERNAL_PUBLISH = 0x0008D8FC

REQUEST = RAM_BASE + 0x37000
SESSION = RAM_BASE + 0x37100


class ActivityPublicRouteFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.immediate_responses: list[dict[str, Any]] = []
        self.internal_events: list[dict[str, Any]] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == IMMEDIATE_RESPONSE:
            stack = uc.reg_read(UC_ARM_REG_SP)
            self.immediate_responses.append({
                "session": uc.reg_read(UC_ARM_REG_R0),
                "packed_identifier": uc.reg_read(UC_ARM_REG_R1) & 0xFFFF,
                "response_type": uc.reg_read(UC_ARM_REG_R2) & 0xFF,
                "request_serial": uc.reg_read(UC_ARM_REG_R3) & 0xFFFF,
                "status": struct.unpack(
                    "<I", bytes(uc.mem_read(stack, 4))
                )[0] & 0xFF,
            })
            self._return(uc, 1)
        elif address == INTERNAL_PUBLISH:
            event_id = uc.reg_read(UC_ARM_REG_R0) & 0xFFFF
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            payload = bytes(uc.mem_read(pointer, length)) if pointer and length else b""
            self.internal_events.append({
                "event_id": event_id,
                "payload_hex": payload.hex(),
                "payload_length": length,
            })
            self._return(uc, 1)

    def request(
        self,
        handler: int,
        *,
        flags: int,
        serial: int,
        context: int,
        opaque_third_argument: int = 0x55667788,
    ) -> dict[str, Any]:
        self.immediate_responses.clear()
        self.internal_events.clear()
        request = bytearray(8)
        struct.pack_into("<H", request, 3, serial)
        request[5] = flags
        self.machine.uc.mem_write(REQUEST, bytes(request))
        self.machine.call(
            handler,
            SESSION,
            REQUEST,
            opaque_third_argument,
            context,
        )
        return {
            "flags": flags,
            "serial": serial,
            "context": context,
            "immediate_responses": list(self.immediate_responses),
            "internal_events": list(self.internal_events),
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = ActivityPublicRouteFixture(image)
    all_day = fixture.request(
        ALL_DAY_HANDLER,
        flags=0,
        serial=0x1234,
        context=0x89ABCDEF,
    )
    daily = fixture.request(
        DAILY_HANDLER,
        flags=0,
        serial=0xBEEF,
        context=0x10203040,
    )
    ignored_bit_0 = fixture.request(
        ALL_DAY_HANDLER,
        flags=1,
        serial=7,
        context=9,
    )
    ignored_bit_1 = fixture.request(
        DAILY_HANDLER,
        flags=2,
        serial=7,
        context=9,
    )
    accepted_other_bits = fixture.request(
        ALL_DAY_HANDLER,
        flags=0xFC,
        serial=0x4567,
        context=0x01020304,
    )

    assert all_day["immediate_responses"] == []
    assert all_day["internal_events"] == [{
        "event_id": 0x000E,
        "payload_hex": "04003412efcdab89",
        "payload_length": 8,
    }]
    assert daily["immediate_responses"] == [{
        "session": SESSION,
        "packed_identifier": 0x0501,
        "response_type": 2,
        "request_serial": 0xBEEF,
        "status": 0,
    }]
    assert daily["internal_events"] == [{
        "event_id": 0x000E,
        "payload_hex": "0401efbe40302010",
        "payload_length": 8,
    }]
    assert ignored_bit_0["immediate_responses"] == []
    assert ignored_bit_0["internal_events"] == []
    assert ignored_bit_1["immediate_responses"] == []
    assert ignored_bit_1["internal_events"] == []
    assert accepted_other_bits["internal_events"] == [{
        "event_id": 0x000E,
        "payload_hex": "0400674504030201",
        "payload_length": 8,
    }]

    return {
        "all_day_refresh": all_day,
        "daily_history": daily,
        "ignored_status_bit_0": ignored_bit_0,
        "ignored_status_bit_1": ignored_bit_1,
        "other_status_bits_do_not_block": accepted_other_bits,
        "downstream_static_route": {
            "all_day": "event 14 kind 0 -> system 0x1009 -> accumulator -> internal event 0x000b",
            "daily": "event 14 kind 1 -> history sync 0x0008baec(serial)",
            "all_day_direct_response": None,
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
