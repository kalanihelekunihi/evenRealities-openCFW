#!/usr/bin/env python3
"""Execute production deviceInfo/deviceSn handlers with identity sources intercepted.

The response constructors run in private emulated RAM. Compiled version strings are copied from
the image; the serial getter uses synthetic fixture bytes. Final BLE transport is intercepted.
No physical identifier, live KV state, sensor, storage, hardware, or health store is accessed.
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


DEVICE_INFO_HANDLER = 0x00083D5C
DEVICE_SERIAL_HANDLER = 0x00083DB0
BOUNDED_FORMATTER = 0x00038080
SERIAL_GETTER = 0x0007BA78
CURRENT_SESSION = 0x0004CBA4
FINAL_RESPONSE = 0x000828B4
REQUEST = RAM_BASE + 0x37600
INCOMING_SESSION = RAM_BASE + 0x37700
INFO_SESSION = RAM_BASE + 0x37800
SYNTHETIC_SERIAL = b"SN1234567890123"


class IdentityFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
        self.serial_bytes = SYNTHETIC_SERIAL
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == BOUNDED_FORMATTER:
            destination = uc.reg_read(UC_ARM_REG_R0)
            capacity = uc.reg_read(UC_ARM_REG_R1)
            format_pointer = uc.reg_read(UC_ARM_REG_R2)
            source_pointer = uc.reg_read(UC_ARM_REG_R3)
            source = bytes(uc.mem_read(source_pointer, capacity))
            text = source.split(b"\0", 1)[0][: max(0, capacity - 1)]
            output = text + b"\0" + b"\0" * max(0, capacity - len(text) - 1)
            uc.mem_write(destination, output[:capacity])
            self.effects.append({
                "operation": "bounded_format",
                "capacity": capacity,
                "format_pointer": f"0x{format_pointer:08x}",
                "source_pointer": f"0x{source_pointer:08x}",
                "text": text.decode("ascii"),
            })
            self._return(uc)
        elif address == SERIAL_GETTER:
            destination = uc.reg_read(UC_ARM_REG_R0)
            length_pointer = uc.reg_read(UC_ARM_REG_R1)
            uc.mem_write(destination, self.serial_bytes)
            if length_pointer:
                uc.mem_write(length_pointer, bytes([0 if self.serial_bytes == b"\xff" * 15 else 15]))
            self.effects.append({
                "operation": "serial_getter",
                "payload_hex": self.serial_bytes.hex(),
                "optional_length_pointer_raw": f"0x{length_pointer:08x}",
            })
            self._return(uc)
        elif address == CURRENT_SESSION:
            self.effects.append({"operation": "current_session"})
            self._return(uc, INFO_SESSION)
        elif address == FINAL_RESPONSE:
            header_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_pointer = uc.reg_read(UC_ARM_REG_R2)
            payload_length = uc.reg_read(UC_ARM_REG_R3)
            self.effects.append({
                "operation": "response",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_hex": bytes(uc.mem_read(payload_pointer, payload_length)).hex(),
                "payload_length": payload_length,
            })
            self._return(uc, 1)

    def request(self, serial: int) -> None:
        request = bytearray(16)
        struct.pack_into("<H", request, 3, serial)
        self.machine.uc.mem_write(REQUEST, bytes(request))

    def run_device_info(self, serial: int) -> dict[str, Any]:
        self.request(serial)
        self.effects.clear()
        self.machine.call(
            DEVICE_INFO_HANDLER,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {"serial": serial, "effects": list(self.effects)}

    def run_device_serial(self, serial: int, serial_bytes: bytes) -> dict[str, Any]:
        if len(serial_bytes) != 15:
            raise ValueError("synthetic serial fixture must be exactly 15 bytes")
        self.request(serial)
        self.serial_bytes = serial_bytes
        self.effects.clear()
        self.machine.call(
            DEVICE_SERIAL_HANDLER,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {"serial": serial, "effects": list(self.effects)}


def run(image: bytes) -> dict[str, Any]:
    fixture = IdentityFixture(image)
    info = fixture.run_device_info(0x1234)
    valid_serial = fixture.run_device_serial(0x1234, SYNTHETIC_SERIAL)
    unavailable_serial = fixture.run_device_serial(0xFFFF, b"\xff" * 15)

    info_payload = (
        b"2.2.6.0009\0" + b"\0" * 5
        + b"603MV1.9.3\0" + b"\0" * 5
    )
    assert len(info_payload) == 32
    assert info["effects"] == [
        {
            "operation": "bounded_format",
            "capacity": 16,
            "format_pointer": "0x00083da0",
            "source_pointer": "0x00083d94",
            "text": "2.2.6.0009",
        },
        {
            "operation": "bounded_format",
            "capacity": 16,
            "format_pointer": "0x00083da0",
            "source_pointer": "0x00083da4",
            "text": "603MV1.9.3",
        },
        {"operation": "current_session"},
        {
            "operation": "response",
            "session": f"0x{INFO_SESSION:08x}",
            "header_hex": "0301000234120000",
            "payload_hex": info_payload.hex(),
            "payload_length": 32,
        },
    ]
    assert valid_serial["effects"] == [
        {
            "operation": "serial_getter",
            "payload_hex": SYNTHETIC_SERIAL.hex(),
            "optional_length_pointer_raw": "0x00000000",
        },
        {
            "operation": "response",
            "session": f"0x{INCOMING_SESSION:08x}",
            "header_hex": "0301001034120000",
            "payload_hex": SYNTHETIC_SERIAL.hex(),
            "payload_length": 15,
        },
    ]
    assert unavailable_serial["effects"][1] == {
        "operation": "response",
        "session": f"0x{INCOMING_SESSION:08x}",
        "header_hex": "03010010ffff0000",
        "payload_hex": "ff" * 15,
        "payload_length": 15,
    }

    return {
        "fixture_groups": 3,
        "device_info": info,
        "device_serial_valid_synthetic": valid_serial,
        "device_serial_unavailable_sentinel": unavailable_serial,
        "interpretation": {
            "production_device_info_payload_bytes": 32,
            "production_device_info_slot_bytes": 16,
            "device_info_slot_order": ["application_version", "hardware_version"],
            "production_device_serial_payload_bytes": 15,
            "device_serial_requires_nul_terminator": False,
            "device_serial_unavailable_is_ff15": True,
        },
        "safety": {
            "physical_device_access": False,
            "ble_sender_intercepted": True,
            "serial_getter_intercepted_with_synthetic_bytes": True,
            "live_identity_access": False,
            "storage_access": False,
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
