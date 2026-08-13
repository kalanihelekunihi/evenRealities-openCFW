#!/usr/bin/env python3
"""Execute removeRingNotify with response and both destructive setters intercepted.

The handler runs only in private emulator RAM. No BLE transmission, KV mutation, synchronized
flash write, pairing-state change, sensor access, or physical-device operation is performed.
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


HANDLER = 0x000844B0
FINAL_RESPONSE = 0x000828B4
FLAG_SETTER = 0x00073834
PEER_SETTER = 0x000738A8
REQUEST = RAM_BASE + 0x37200
SESSION = RAM_BASE + 0x37300


class RemoveRingFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
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
            self.effects.append({
                "operation": "response",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_pointer_raw": f"0x{payload_pointer:08x}",
                "payload_length": payload_length,
            })
            self._return(uc, 1)
        elif address == FLAG_SETTER:
            self.effects.append({
                "operation": "set_glasses_connected_ring_flag",
                "value_raw": uc.reg_read(UC_ARM_REG_R0),
            })
            self._return(uc, 0)
        elif address == PEER_SETTER:
            peer_a = uc.reg_read(UC_ARM_REG_R0)
            peer_b = uc.reg_read(UC_ARM_REG_R1)
            self.effects.append({
                "operation": "set_peer_slots",
                "slot_a_hex": bytes(uc.mem_read(peer_a, 6)).hex(),
                "slot_b_hex": bytes(uc.mem_read(peer_b, 6)).hex(),
                "pointers_equal": peer_a == peer_b,
            })
            self._return(uc, 0)

    def run(
        self,
        *,
        declared_frame_length: int,
        serial: int,
        request_fill: int,
        argument2: int,
        argument3: int,
    ) -> dict[str, Any]:
        request = bytearray([request_fill] * 32)
        struct.pack_into("<H", request, 3, serial)
        struct.pack_into("<H", request, 8, declared_frame_length)
        self.machine.uc.mem_write(REQUEST, bytes(request))
        self.effects.clear()
        self.machine.call(HANDLER, SESSION, REQUEST, argument2, argument3)
        return {
            "declared_frame_length": declared_frame_length,
            "serial": serial,
            "effects": list(self.effects),
        }


def accepted_effects(serial: int) -> list[dict[str, Any]]:
    return [
        {
            "operation": "response",
            "session": f"0x{SESSION:08x}",
            "header_hex": f"03010082{serial & 0xff:02x}{serial >> 8:02x}0000",
            "payload_pointer_raw": "0x00000000",
            "payload_length": 0,
        },
        {
            "operation": "set_glasses_connected_ring_flag",
            "value_raw": 0,
        },
        {
            "operation": "set_peer_slots",
            "slot_a_hex": "ffffffffffff",
            "slot_b_hex": "ffffffffffff",
            "pointers_equal": True,
        },
    ]


def run(image: bytes) -> dict[str, Any]:
    fixture = RemoveRingFixture(image)
    exact_empty = fixture.run(
        declared_frame_length=12,
        serial=0x1234,
        request_fill=0,
        argument2=0,
        argument3=0,
    )
    one_payload_byte = fixture.run(
        declared_frame_length=13,
        serial=0x1234,
        request_fill=0xA5,
        argument2=0x55667788,
        argument3=0x99AABBCC,
    )
    malformed_zero_length = fixture.run(
        declared_frame_length=0,
        serial=0xFFFF,
        request_fill=0xFF,
        argument2=0xFFFFFFFF,
        argument3=0xFFFFFFFF,
    )

    assert exact_empty["effects"] == []
    assert one_payload_byte["effects"] == accepted_effects(0x1234)
    assert malformed_zero_length["effects"] == accepted_effects(0xFFFF)

    return {
        "fixture_groups": 3,
        "exact_header_only_no_action": exact_empty,
        "one_payload_byte_destructive_route": one_payload_byte,
        "malformed_declared_zero_still_destructive": malformed_zero_length,
        "interpretation": {
            "only_declared_length_12_is_non_destructive": True,
            "payload_contents_read": False,
            "response_precedes_state_changes": True,
            "live_read_only_classification_is_safe": False,
        },
        "safety": {
            "physical_device_access": False,
            "ble_response_intercepted": True,
            "both_persistent_setters_intercepted": True,
            "flash_access": False,
            "pairing_state_mutation": False,
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
