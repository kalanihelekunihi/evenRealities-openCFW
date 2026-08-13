#!/usr/bin/env python3
"""Execute the production systemTime handler with every stateful effect intercepted.

The handler and its real payload/response constructors execute in private emulator RAM. Callback
cancellation, clocks, internal events, NV classification/recovery and final transport are all
intercepted. No BLE, clock, flash, identifier, calibration, or physical-device access occurs.
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


SYSTEM_TIME_HANDLER = 0x000846DC
CANCEL_CALLBACK = 0x00065D64
TIMEZONE_ACCESSOR = 0x0008ADB4
TIME_ACCESSOR = 0x0008ADA4
EVENT_PUBLISHER = 0x0008D8FC
FINAL_RESPONSE = 0x000828B4
NV_VALIDITY = 0x0007BB20
NV_REQUEST = 0x00083C86
NV_REPORT = 0x0007BBE8
LOG_FLAGS = 0x000914EC

REQUEST = RAM_BASE + 0x3A000
INCOMING_SESSION = 0x0042
OLD_TIMEZONE_BITS = 0xFE98  # -360 minutes
OLD_TIMESTAMP = 0x01020304
NEW_TIMEZONE_BITS = 0x014A  # +330 minutes
NEW_TIMESTAMP = 0x0A0B0C0D


class SystemTimeFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
        self.event_publish_result = 0
        self.nv_valid = False
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == CANCEL_CALLBACK:
            self.effects.append({
                "operation": "cancel_delayed_callback",
                "callback_thumb": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "context_filter": uc.reg_read(UC_ARM_REG_R1),
            })
            self._return(uc, 1)
        elif address == TIMEZONE_ACCESSOR:
            self.effects.append({
                "operation": "read_old_timezone",
                "raw_bits": f"0x{OLD_TIMEZONE_BITS:04x}",
            })
            self._return(uc, OLD_TIMEZONE_BITS)
        elif address == TIME_ACCESSOR:
            self.effects.append({
                "operation": "read_old_timestamp",
                "timestamp": OLD_TIMESTAMP,
            })
            self._return(uc, OLD_TIMESTAMP)
        elif address == EVENT_PUBLISHER:
            length = uc.reg_read(UC_ARM_REG_R2)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            self.effects.append({
                "operation": "publish_internal_event",
                "event_id": uc.reg_read(UC_ARM_REG_R0),
                "payload_length": length,
                "payload_hex": bytes(uc.mem_read(pointer, length)).hex(),
                "result": self.event_publish_result,
            })
            self._return(uc, self.event_publish_result)
        elif address == FINAL_RESPONSE:
            header_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_pointer = uc.reg_read(UC_ARM_REG_R2)
            payload_length = uc.reg_read(UC_ARM_REG_R3)
            self.effects.append({
                "operation": "protocol_message",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):04x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_length": payload_length,
                "payload_hex": (
                    bytes(uc.mem_read(payload_pointer, payload_length)).hex()
                    if payload_length else ""
                ),
            })
            self._return(uc, 1)
        elif address == NV_VALIDITY:
            raw = 1 if self.nv_valid else 0xFF
            self.effects.append({
                "operation": "classify_nv_state",
                "raw_state": raw,
                "local_record_valid": self.nv_valid,
            })
            self._return(uc, 0 if self.nv_valid else 1)
        elif address == NV_REQUEST:
            self.effects.append({
                "operation": "request_phone_nv_recovery",
                "uses_current_eus_session": True,
            })
            self._return(uc, 1)
        elif address == NV_REPORT:
            self.effects.append({
                "operation": "report_local_nv_recovery",
                "nested_payload_bytes": 121,
                "body_bytes": 116,
            })
            self._return(uc, 0)
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def run(
        self,
        *,
        declared_frame_length: int,
        serial: int,
        payload_backing: bytes,
        nv_valid: bool,
        event_publish_result: int = 0,
    ) -> dict[str, Any]:
        request = bytearray(64)
        struct.pack_into("<H", request, 3, serial)
        struct.pack_into("<H", request, 8, declared_frame_length)
        request[12 : 12 + len(payload_backing)] = payload_backing
        self.machine.uc.mem_write(REQUEST, bytes(request))
        self.effects.clear()
        self.nv_valid = nv_valid
        self.event_publish_result = event_publish_result
        self.machine.call(
            SYSTEM_TIME_HANDLER,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {
            "declared_frame_length": declared_frame_length,
            "serial": serial,
            "payload_backing_hex": payload_backing.hex(),
            "nv_valid": nv_valid,
            "event_publish_result": event_publish_result,
            "effects": list(self.effects),
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = SystemTimeFixture(image)
    meaningful = struct.pack("<HI", NEW_TIMEZONE_BITS, NEW_TIMESTAMP)
    official = meaningful + b"\x00" * 6

    header_only = fixture.run(
        declared_frame_length=12,
        serial=0x1234,
        payload_backing=b"",
        nv_valid=False,
    )
    six_byte_nv_lost = fixture.run(
        declared_frame_length=18,
        serial=0x1234,
        payload_backing=meaningful,
        nv_valid=False,
    )
    official_nv_valid = fixture.run(
        declared_frame_length=24,
        serial=0xFFFF,
        payload_backing=official,
        nv_valid=True,
    )
    malformed_zero = fixture.run(
        declared_frame_length=0,
        serial=0,
        payload_backing=meaningful,
        nv_valid=False,
    )
    ignored_event_failure = fixture.run(
        declared_frame_length=24,
        serial=0xABCD,
        payload_backing=official,
        nv_valid=True,
        event_publish_result=1,
    )

    cancel = {
        "operation": "cancel_delayed_callback",
        "callback_thumb": "0x00084c83",
        "context_filter": 0,
    }
    transition = {
        "operation": "publish_internal_event",
        "event_id": 3,
        "payload_length": 12,
        "payload_hex": "98fe4a01040302010d0c0b0a",
        "result": 0,
    }
    ack = {
        "operation": "protocol_message",
        "session": "0x0042",
        "header_hex": "0301000534120000",
        "payload_length": 0,
        "payload_hex": "",
    }
    user_info = {
        "operation": "protocol_message",
        "session": "0x0042",
        "header_hex": "0201000400000000",
        "payload_length": 0,
        "payload_hex": "",
    }
    prefix = [
        cancel,
        {"operation": "read_old_timezone", "raw_bits": "0xfe98"},
        {"operation": "read_old_timestamp", "timestamp": OLD_TIMESTAMP},
        transition,
        ack,
        user_info,
    ]

    assert header_only["effects"] == [cancel]
    assert six_byte_nv_lost["effects"] == [
        *prefix,
        {
            "operation": "classify_nv_state",
            "raw_state": 0xFF,
            "local_record_valid": False,
        },
        {
            "operation": "request_phone_nv_recovery",
            "uses_current_eus_session": True,
        },
    ]
    assert official_nv_valid["effects"] == [
        *[
            effect if effect.get("header_hex") != "0301000534120000"
            else {**effect, "header_hex": "03010005ffff0000"}
            for effect in prefix
        ],
        {
            "operation": "classify_nv_state",
            "raw_state": 1,
            "local_record_valid": True,
        },
        {
            "operation": "report_local_nv_recovery",
            "nested_payload_bytes": 121,
            "body_bytes": 116,
        },
    ]
    assert malformed_zero["effects"] == [
        *[
            effect if effect.get("header_hex") != "0301000534120000"
            else {**effect, "header_hex": "0301000500000000"}
            for effect in prefix
        ],
        {
            "operation": "classify_nv_state",
            "raw_state": 0xFF,
            "local_record_valid": False,
        },
        {
            "operation": "request_phone_nv_recovery",
            "uses_current_eus_session": True,
        },
    ]
    expected_failure = [
        {**effect, "result": 1}
        if effect.get("operation") == "publish_internal_event"
        else (
            {**effect, "header_hex": "03010005cdab0000"}
            if effect.get("header_hex") == "0301000534120000"
            else effect
        )
        for effect in prefix
    ]
    assert ignored_event_failure["effects"] == [
        *expected_failure,
        {
            "operation": "classify_nv_state",
            "raw_state": 1,
            "local_record_valid": True,
        },
        {
            "operation": "report_local_nv_recovery",
            "nested_payload_bytes": 121,
            "body_bytes": 116,
        },
    ]

    return {
        "fixture_groups": 5,
        "header_only": header_only,
        "six_meaningful_bytes_nv_lost": six_byte_nv_lost,
        "official_twelve_bytes_nv_valid": official_nv_valid,
        "malformed_declared_zero": malformed_zero,
        "ignored_internal_event_failure": ignored_event_failure,
        "interpretation": {
            "callback_cancel_precedes_payload_check": True,
            "only_declared_length_twelve_is_silent_after_cancel": True,
            "six_meaningful_payload_bytes_consumed": True,
            "official_six_reserved_tail_bytes_ignored": True,
            "malformed_short_declarations_can_reach_six_byte_read": True,
            "event_publish_result_ignored": True,
            "ack_precedes_user_info_and_nv_followups": True,
            "nv_invalid_requests_phone_backup": True,
            "nv_valid_reports_local_backup": True,
        },
        "safety": {
            "physical_device_access": False,
            "callback_cancellation_intercepted": True,
            "clock_reads_and_write_event_intercepted": True,
            "final_transport_intercepted": True,
            "nv_state_and_recovery_intercepted": True,
            "identifier_or_calibration_bytes_accessed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
