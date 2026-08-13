#!/usr/bin/env python3
"""Execute exact production device/wear status routes with all I/O intercepted.

The handlers and response builders execute in private emulated RAM. Battery/wear inputs, current
sessions, final phone transport, logging, and glasses dispatch are intercepted. No BLE, physical
device, live SRAM/storage, sensor, or health-store access occurs.
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


REQUESTED_DEVICE_STATUS = 0x00083DE4
UNSOLICITED_DEVICE_STATUS = 0x0008345C
REQUESTED_WEAR_STATUS = 0x00084B24
UNSOLICITED_WEAR_STATUS = 0x00043788

BATTERY_PERCENTAGE = 0x00091270
IS_CHARGING = 0x00091256
IS_FULL = 0x00091244
WEAR_STATE_ACCESSOR = 0x0004C5B8
LOG_FLAGS = 0x000914EC
CURRENT_EUS_SESSION = 0x0004CBA4
FINAL_PHONE_RESPONSE = 0x000828B4
CURRENT_GLASSES_SESSION = 0x0004CB34
GLASSES_DISPATCH = 0x00034064

WEAR_STATE = 0x2001E454
WEAR_STATE_OFFSET = 0x24
REQUEST = RAM_BASE + 0x37600
INCOMING_SESSION = RAM_BASE + 0x37700
PHONE_SESSION = RAM_BASE + 0x37800
GLASSES_SESSION = RAM_BASE + 0x37900


class StatusFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
        self.battery_percent = 75
        self.charging = False
        self.full = False
        self.wear_samples: list[int] = []
        self.phone_session_available = True
        self.glasses_session_available = True
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == BATTERY_PERCENTAGE:
            self.effects.append({
                "operation": "battery_percentage",
                "normalized_value": self.battery_percent,
            })
            self._return(uc, self.battery_percent)
        elif address == IS_CHARGING:
            self.effects.append({
                "operation": "is_charging",
                "value": self.charging,
            })
            self._return(uc, int(self.charging))
        elif address == IS_FULL:
            self.effects.append({"operation": "is_full", "value": self.full})
            self._return(uc, int(self.full))
        elif address == WEAR_STATE_ACCESSOR:
            if not self.wear_samples:
                raise AssertionError("wear handler performed an unexpected accessor read")
            value = self.wear_samples.pop(0)
            self.effects.append({
                "operation": "wear_state_accessor",
                "value": value,
            })
            self._return(uc, value)
        elif address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == CURRENT_EUS_SESSION:
            value = PHONE_SESSION if self.phone_session_available else 0xFFFF
            self.effects.append({
                "operation": "current_eus_session",
                "value": f"0x{value:08x}",
            })
            self._return(uc, value)
        elif address == FINAL_PHONE_RESPONSE:
            header_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_pointer = uc.reg_read(UC_ARM_REG_R2)
            payload_length = uc.reg_read(UC_ARM_REG_R3)
            self.effects.append({
                "operation": "phone_response",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_hex": bytes(uc.mem_read(payload_pointer, payload_length)).hex(),
                "payload_length": payload_length,
            })
            self._return(uc, 1)
        elif address == CURRENT_GLASSES_SESSION:
            value = GLASSES_SESSION if self.glasses_session_available else 0xFFFF
            self.effects.append({
                "operation": "current_glasses_session",
                "value": f"0x{value:08x}",
            })
            self._return(uc, value)
        elif address == GLASSES_DISPATCH:
            payload_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_length = uc.reg_read(UC_ARM_REG_R2)
            self.effects.append({
                "operation": "glasses_dispatch",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "payload_hex": bytes(uc.mem_read(payload_pointer, payload_length)).hex(),
                "payload_length": payload_length,
            })
            self._return(uc, 0)

    def request(self, serial: int) -> None:
        request = bytearray(16)
        struct.pack_into("<H", request, 3, serial)
        self.machine.uc.mem_write(REQUEST, bytes(request))

    def run_requested_device(
        self,
        *,
        serial: int,
        battery_percent: int,
        charging: bool,
        full: bool,
        phone_session_available: bool = True,
    ) -> dict[str, Any]:
        self.request(serial)
        self.effects.clear()
        self.battery_percent = battery_percent
        self.charging = charging
        self.full = full
        self.phone_session_available = phone_session_available
        self.machine.call(
            REQUESTED_DEVICE_STATUS,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {
            "serial": serial,
            "battery_percent": battery_percent,
            "charging": charging,
            "full": full,
            "phone_session_available": phone_session_available,
            "effects": list(self.effects),
        }

    def run_unsolicited_device(
        self,
        *,
        battery_percent: int,
        charging: bool,
        phone_session_available: bool = True,
    ) -> dict[str, Any]:
        self.effects.clear()
        self.phone_session_available = phone_session_available
        self.machine.call(UNSOLICITED_DEVICE_STATUS, battery_percent, int(charging))
        return {
            "battery_percent": battery_percent,
            "charging": charging,
            "phone_session_available": phone_session_available,
            "effects": list(self.effects),
        }

    def run_requested_wear(
        self,
        *,
        serial: int,
        samples: list[int],
        phone_session_available: bool = True,
    ) -> dict[str, Any]:
        self.request(serial)
        self.effects.clear()
        self.wear_samples = list(samples)
        self.phone_session_available = phone_session_available
        self.machine.call(REQUESTED_WEAR_STATUS, INCOMING_SESSION, REQUEST)
        if self.wear_samples:
            raise AssertionError("wear fixture supplied unused accessor samples")
        return {
            "serial": serial,
            "samples": samples,
            "phone_session_available": phone_session_available,
            "effects": list(self.effects),
        }

    def run_unsolicited_wear(
        self,
        *,
        internal_state: int,
        phone_session_available: bool = True,
        glasses_session_available: bool = True,
    ) -> dict[str, Any]:
        self.effects.clear()
        self.phone_session_available = phone_session_available
        self.glasses_session_available = glasses_session_available
        self.machine.uc.mem_write(
            WEAR_STATE + WEAR_STATE_OFFSET,
            bytes([internal_state]),
        )
        self.machine.call(UNSOLICITED_WEAR_STATUS)
        return {
            "internal_state": internal_state,
            "phone_session_available": phone_session_available,
            "glasses_session_available": glasses_session_available,
            "effects": list(self.effects),
        }


def phone_effect(header: str, payload: str) -> dict[str, Any]:
    return {
        "operation": "phone_response",
        "session": f"0x{PHONE_SESSION:08x}",
        "header_hex": header,
        "payload_hex": payload,
        "payload_length": len(bytes.fromhex(payload)),
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = StatusFixture(image)

    requested_not_charging = fixture.run_requested_device(
        serial=0x1234,
        battery_percent=75,
        charging=False,
        full=False,
    )
    requested_charging = fixture.run_requested_device(
        serial=0x1234,
        battery_percent=76,
        charging=True,
        full=False,
    )
    requested_full_override = fixture.run_requested_device(
        serial=0xFFFF,
        battery_percent=100,
        charging=True,
        full=True,
    )
    unsolicited_not_charging = fixture.run_unsolicited_device(
        battery_percent=74,
        charging=False,
    )
    unsolicited_charging = fixture.run_unsolicited_device(
        battery_percent=75,
        charging=True,
    )
    requested_wear_zero = fixture.run_requested_wear(serial=0x1234, samples=[0])
    requested_wear_confirmed = fixture.run_requested_wear(
        serial=0x1234,
        samples=[2, 2],
    )
    requested_wear_race = fixture.run_requested_wear(
        serial=0xFFFF,
        samples=[2, 1],
    )
    unsolicited_wear_zero = fixture.run_unsolicited_wear(internal_state=0)
    unsolicited_wear_nonzero_without_phone = fixture.run_unsolicited_wear(
        internal_state=2,
        phone_session_available=False,
    )
    unsolicited_wear_nonzero_without_glasses = fixture.run_unsolicited_wear(
        internal_state=1,
        glasses_session_available=False,
    )

    assert requested_not_charging["effects"] == [
        {"operation": "battery_percentage", "normalized_value": 75},
        {"operation": "is_charging", "value": False},
        {"operation": "is_full", "value": False},
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0301000134120000", "4b020100000000"),
    ]
    assert requested_charging["effects"][-1] == phone_effect(
        "0301000134120000",
        "4c010100000000",
    )
    assert requested_full_override["effects"][-1] == phone_effect(
        "03010001ffff0000",
        "64030100000000",
    )
    assert unsolicited_not_charging["effects"] == [
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0201000100000000", "4a020000000000"),
    ]
    assert unsolicited_charging["effects"][-1] == phone_effect(
        "0201000100000000",
        "4b010000000000",
    )
    assert requested_wear_zero["effects"] == [
        {"operation": "wear_state_accessor", "value": 0},
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0301000334120000", "01"),
    ]
    assert requested_wear_confirmed["effects"] == [
        {"operation": "wear_state_accessor", "value": 2},
        {"operation": "wear_state_accessor", "value": 2},
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0301000334120000", "00"),
    ]
    assert requested_wear_race["effects"][-1] == phone_effect(
        "03010003ffff0000",
        "02",
    )
    assert unsolicited_wear_zero["effects"] == [
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0201000300000000", "01"),
        {"operation": "current_glasses_session", "value": f"0x{GLASSES_SESSION:08x}"},
        {"operation": "current_glasses_session", "value": f"0x{GLASSES_SESSION:08x}"},
        {
            "operation": "glasses_dispatch",
            "session": f"0x{GLASSES_SESSION:08x}",
            "payload_hex": "00098c0000",
            "payload_length": 5,
        },
    ]
    assert unsolicited_wear_nonzero_without_phone["effects"] == [
        {"operation": "current_eus_session", "value": "0x0000ffff"},
        {"operation": "current_glasses_session", "value": f"0x{GLASSES_SESSION:08x}"},
        {"operation": "current_glasses_session", "value": f"0x{GLASSES_SESSION:08x}"},
        {
            "operation": "glasses_dispatch",
            "session": f"0x{GLASSES_SESSION:08x}",
            "payload_hex": "00098c0001",
            "payload_length": 5,
        },
    ]
    assert unsolicited_wear_nonzero_without_glasses["effects"] == [
        {"operation": "current_eus_session", "value": f"0x{PHONE_SESSION:08x}"},
        phone_effect("0201000300000000", "02"),
        {"operation": "current_glasses_session", "value": "0x0000ffff"},
    ]

    return {
        "fixture_groups": 11,
        "requested_device_not_charging": requested_not_charging,
        "requested_device_charging": requested_charging,
        "requested_device_full_overrides_charging": requested_full_override,
        "unsolicited_device_not_charging": unsolicited_not_charging,
        "unsolicited_device_charging": unsolicited_charging,
        "requested_wear_zero": requested_wear_zero,
        "requested_wear_confirmed_anomaly": requested_wear_confirmed,
        "requested_wear_two_sample_race": requested_wear_race,
        "unsolicited_wear_zero": unsolicited_wear_zero,
        "unsolicited_wear_nonzero_without_phone": (
            unsolicited_wear_nonzero_without_phone
        ),
        "unsolicited_wear_nonzero_without_glasses": (
            unsolicited_wear_nonzero_without_glasses
        ),
        "interpretation": {
            "requested_device_payload_hex_template": "PPSS0100000000",
            "unsolicited_device_payload_hex_template": "PPSS0000000000",
            "requested_wear_reads_internal_state_twice_when_first_nonzero": True,
            "requested_confirmed_state_2_maps_to_unknown_0": True,
            "unsolicited_nonzero_wear_maps_to_worn_2": True,
            "unsolicited_wear_phone_response_precedes_glasses_dispatch": True,
            "phone_and_glasses_session_absence_are_independent": True,
        },
        "safety": {
            "physical_device_access": False,
            "phone_ble_sender_intercepted": True,
            "glasses_ble_dispatch_intercepted": True,
            "battery_accessors_intercepted": True,
            "wear_accessor_uses_synthetic_samples": True,
            "live_sram_access": False,
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
