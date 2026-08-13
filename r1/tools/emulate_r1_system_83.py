#!/usr/bin/env python3
"""Execute system subcommand 0x83 with the final transport sender intercepted.

The production handler and response wrapper run in private emulated RAM. BLE, internal events,
sensors, storage, physical hardware, and host health stores are absent.
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
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture, RAM_BASE


HANDLER = 0x00084860
FINAL_RESPONSE = 0x000828B4
REQUEST = RAM_BASE + 0x37000
SESSION = RAM_BASE + 0x37100


class System83Fixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.responses: list[dict[str, Any]] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == FINAL_RESPONSE:
            header_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_pointer = uc.reg_read(UC_ARM_REG_R2)
            payload_length = uc.reg_read(UC_ARM_REG_R3)
            self.responses.append({
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_pointer_raw": f"0x{payload_pointer:08x}",
                "payload_length": payload_length,
            })
            self._return(uc, 1)

    def run(
        self,
        *,
        serial: int,
        request_prefix: bytes,
        opaque_argument2: int,
        opaque_argument3: int,
    ) -> dict[str, Any]:
        if len(request_prefix) < 8:
            raise ValueError("fixture request must contain at least eight bytes")
        request = bytearray(request_prefix)
        struct.pack_into("<H", request, 3, serial)
        self.machine.uc.mem_write(REQUEST, bytes(request))
        self.responses.clear()
        self.machine.call(
            HANDLER,
            SESSION,
            REQUEST,
            opaque_argument2,
            opaque_argument3,
        )
        return {
            "serial": serial,
            "request_hex": bytes(request).hex(),
            "responses": list(self.responses),
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = System83Fixture(image)
    zero = fixture.run(
        serial=0,
        request_prefix=b"\x00" * 8,
        opaque_argument2=0,
        opaque_argument3=0,
    )
    ordinary = fixture.run(
        serial=0x1234,
        request_prefix=bytes.fromhex("a1b2c3d4e5f60718"),
        opaque_argument2=0x55667788,
        opaque_argument3=0x99AABBCC,
    )
    all_bits = fixture.run(
        serial=0xFFFF,
        request_prefix=b"\xff" * 8,
        opaque_argument2=0xFFFFFFFF,
        opaque_argument3=0xFFFFFFFF,
    )

    expected_zero = {
        "session": f"0x{SESSION:08x}",
        "header_hex": "0301008300000000",
        "payload_pointer_raw": "0x00000000",
        "payload_length": 0,
    }
    assert zero["responses"] == [expected_zero]
    expected_ordinary = dict(expected_zero)
    expected_ordinary["header_hex"] = "0301008334120000"
    assert ordinary["responses"] == [expected_ordinary]
    expected_all_bits = dict(expected_zero)
    expected_all_bits["header_hex"] = "03010083ffff0000"
    assert all_bits["responses"] == [expected_all_bits]

    return {
        "fixture_groups": 3,
        "zero_serial": zero,
        "ordinary_serial_and_ignored_request_bytes": ordinary,
        "all_bits_and_ignored_extra_arguments": all_bits,
        "response_layout": {
            "header_hex_for_serial_0x1234": "0301008334120000",
            "status_or_flags_raw": 3,
            "response_type_raw": 1,
            "identifier": "0x0083",
            "request_serial": "0x1234",
            "reserved_raw": 0,
            "payload_bytes": 0,
        },
        "safety": {
            "physical_device_access": False,
            "ble_sender_intercepted": True,
            "internal_event_access": False,
            "sensor_access": False,
            "storage_access": False,
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
