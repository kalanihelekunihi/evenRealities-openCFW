#!/usr/bin/env python3
"""Execute pairAuth and advStart handlers with every external effect intercepted.

Production Thumb handlers and response builders run in private emulator RAM. Phone-role changes,
BLE event delivery, Peer Manager security, responses, advertising, disconnects, timers, and live
addresses are all intercepted or unreachable. No physical device or BLE radio is accessed.
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


PAIR_HANDLER = 0x000842EC
ADV_HANDLER = 0x00083D04
PHONE_ROLE_SETTER = 0x0004DA28
EVENT_ENQUEUE = 0x00033850
CURRENT_EUS_SESSION = 0x0004CBA4
FINAL_RESPONSE = 0x000828B4
ALLOCATE = 0x000855A0
QUEUE_PUT = 0x0007D40C
EVENT_FLAG_SET = 0x0007D6F4
FREE = 0x00095D48
LOG_FLAGS = 0x000914EC

THREAD_STATE = 0x20006568
REQUEST = RAM_BASE + 0x38000
INCOMING_SESSION = 0x0042
CURRENT_SESSION = 0x0044
EVENT = RAM_BASE + 0x38400
QUEUE_HANDLE = 0x11223344
EVENT_FLAG_HANDLE = 0x55667788


class ConnectionControlFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.effects: list[dict[str, Any]] = []
        self.queue_available = True
        self.allocation_succeeds = True
        self.queue_put_succeeds = True
        self.execute_event_enqueue = False
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == PHONE_ROLE_SETTER:
            self.effects.append({
                "operation": "phone_role_setter",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):04x}",
            })
            self._return(uc)
        elif address == EVENT_ENQUEUE:
            if self.execute_event_enqueue:
                return
            payload_length = uc.reg_read(UC_ARM_REG_R2)
            payload_pointer = uc.reg_read(UC_ARM_REG_R3)
            self.effects.append({
                "operation": "event_enqueue",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):04x}",
                "event_type": uc.reg_read(UC_ARM_REG_R1),
                "payload_length": payload_length,
                "payload_hex": bytes(
                    uc.mem_read(payload_pointer, payload_length)
                ).hex(),
            })
            self._return(uc, 0)
        elif address == CURRENT_EUS_SESSION:
            self.effects.append({
                "operation": "current_eus_session",
                "session": f"0x{CURRENT_SESSION:04x}",
            })
            self._return(uc, CURRENT_SESSION)
        elif address == FINAL_RESPONSE:
            header_pointer = uc.reg_read(UC_ARM_REG_R1)
            payload_pointer = uc.reg_read(UC_ARM_REG_R2)
            payload_length = uc.reg_read(UC_ARM_REG_R3)
            self.effects.append({
                "operation": "response",
                "session": f"0x{uc.reg_read(UC_ARM_REG_R0):04x}",
                "header_hex": bytes(uc.mem_read(header_pointer, 8)).hex(),
                "payload_hex": (
                    bytes(uc.mem_read(payload_pointer, payload_length)).hex()
                    if payload_length
                    else ""
                ),
                "payload_length": payload_length,
            })
            self._return(uc, 1)
        elif address == ALLOCATE:
            allocation_size = uc.reg_read(UC_ARM_REG_R0)
            self.effects.append({
                "operation": "allocate_event",
                "size": allocation_size,
                "succeeded": self.allocation_succeeds,
            })
            if self.allocation_succeeds:
                uc.mem_write(EVENT, b"\x00" * max(24, allocation_size))
            self._return(uc, EVENT if self.allocation_succeeds else 0)
        elif address == QUEUE_PUT:
            event_pointer_pointer = uc.reg_read(UC_ARM_REG_R1)
            event_pointer = struct.unpack(
                "<I", bytes(uc.mem_read(event_pointer_pointer, 4))
            )[0]
            event = bytes(uc.mem_read(event_pointer, 24))
            session, event_type, payload_length = struct.unpack("<III", event[:12])
            self.effects.append({
                "operation": "queue_event",
                "queue_handle": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "session": f"0x{session:04x}",
                "event_type": event_type,
                "payload_length": payload_length,
                "payload_hex": event[12 : 12 + payload_length].hex(),
                "succeeded": self.queue_put_succeeds,
            })
            self._return(uc, 0 if self.queue_put_succeeds else 1)
        elif address == EVENT_FLAG_SET:
            self.effects.append({
                "operation": "signal_event_thread",
                "event_flag_handle": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "bits": f"0x{uc.reg_read(UC_ARM_REG_R1):08x}",
            })
            self._return(uc)
        elif address == FREE:
            self.effects.append({
                "operation": "free_failed_event",
                "pointer": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
            })
            self._return(uc)

    def _request(
        self,
        *,
        declared_frame_length: int,
        serial: int,
        payload_backing: bytes,
    ) -> None:
        request = bytearray(64)
        struct.pack_into("<H", request, 3, serial)
        struct.pack_into("<H", request, 8, declared_frame_length)
        request[12 : 12 + len(payload_backing)] = payload_backing
        self.machine.uc.mem_write(REQUEST, bytes(request))

    def run_pair(
        self,
        *,
        declared_frame_length: int,
        serial: int,
        payload_backing: bytes,
    ) -> dict[str, Any]:
        self._request(
            declared_frame_length=declared_frame_length,
            serial=serial,
            payload_backing=payload_backing,
        )
        self.effects.clear()
        self.execute_event_enqueue = False
        self.machine.call(
            PAIR_HANDLER,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {
            "declared_frame_length": declared_frame_length,
            "serial": serial,
            "payload_backing_hex": payload_backing.hex(),
            "effects": list(self.effects),
        }

    def run_adv(
        self,
        *,
        declared_frame_length: int,
        serial: int,
        payload_backing: bytes,
        queue_available: bool = True,
        allocation_succeeds: bool = True,
        queue_put_succeeds: bool = True,
    ) -> dict[str, Any]:
        self._request(
            declared_frame_length=declared_frame_length,
            serial=serial,
            payload_backing=payload_backing,
        )
        self.queue_available = queue_available
        self.allocation_succeeds = allocation_succeeds
        self.queue_put_succeeds = queue_put_succeeds
        self.execute_event_enqueue = True
        self.machine.uc.mem_write(
            THREAD_STATE + 8,
            struct.pack(
                "<II",
                EVENT_FLAG_HANDLE,
                QUEUE_HANDLE if queue_available else 0,
            ),
        )
        self.effects.clear()
        self.machine.call(
            ADV_HANDLER,
            INCOMING_SESSION,
            REQUEST,
            0x55667788,
            0x99AABBCC,
        )
        return {
            "declared_frame_length": declared_frame_length,
            "serial": serial,
            "payload_backing_hex": payload_backing.hex(),
            "queue_available": queue_available,
            "allocation_succeeds": allocation_succeeds,
            "queue_put_succeeds": queue_put_succeeds,
            "effects": list(self.effects),
        }


def response(header: str, payload: str = "") -> dict[str, Any]:
    return {
        "operation": "response",
        "session": f"0x{INCOMING_SESSION:04x}",
        "header_hex": header,
        "payload_hex": payload,
        "payload_length": len(bytes.fromhex(payload)),
    }


def run(image: bytes) -> dict[str, Any]:
    fixture = ConnectionControlFixture(image)
    first = bytes([1, 2, 3, 4, 5, 6])
    second = bytes([7, 8, 9, 10, 11, 12])
    targets = first + second

    pair_header_only = fixture.run_pair(
        declared_frame_length=12,
        serial=0x1234,
        payload_backing=b"",
    )
    pair_other_type = fixture.run_pair(
        declared_frame_length=13,
        serial=0x1234,
        payload_backing=b"\x02",
    )
    pair_phone = fixture.run_pair(
        declared_frame_length=13,
        serial=0xFFFF,
        payload_backing=b"\x01",
    )
    pair_malformed_zero = fixture.run_pair(
        declared_frame_length=0,
        serial=0x1234,
        payload_backing=b"\x01",
    )

    adv_header_only = fixture.run_adv(
        declared_frame_length=12,
        serial=0x1234,
        payload_backing=b"",
    )
    adv_older_six_bytes = fixture.run_adv(
        declared_frame_length=18,
        serial=0x1234,
        payload_backing=first,
    )
    adv_two_targets = fixture.run_adv(
        declared_frame_length=24,
        serial=0x1234,
        payload_backing=targets,
    )
    adv_malformed_zero = fixture.run_adv(
        declared_frame_length=0,
        serial=0xFFFF,
        payload_backing=targets,
    )
    adv_queue_unavailable = fixture.run_adv(
        declared_frame_length=24,
        serial=0x1234,
        payload_backing=targets,
        queue_available=False,
    )
    adv_queue_failure = fixture.run_adv(
        declared_frame_length=24,
        serial=0x1234,
        payload_backing=targets,
        queue_put_succeeds=False,
    )
    adv_allocation_failure = fixture.run_adv(
        declared_frame_length=24,
        serial=0x1234,
        payload_backing=targets,
        allocation_succeeds=False,
    )

    assert pair_header_only["effects"] == []
    assert pair_other_type["effects"] == [
        response("0301000834120000", "00")
    ]
    assert pair_phone["effects"] == [
        {"operation": "phone_role_setter", "session": "0x0042"},
        {
            "operation": "event_enqueue",
            "session": "0x0042",
            "event_type": 2,
            "payload_length": 1,
            "payload_hex": "01",
        },
        response("03010008ffff0000", "00"),
    ]
    assert pair_malformed_zero["effects"] == [
        {"operation": "phone_role_setter", "session": "0x0042"},
        {
            "operation": "event_enqueue",
            "session": "0x0042",
            "event_type": 2,
            "payload_length": 1,
            "payload_hex": "01",
        },
        response("0301000834120000", "00"),
    ]

    assert adv_header_only["effects"] == [response("0701000a34120000")]
    assert adv_older_six_bytes["effects"] == [response("0701000a34120000")]
    successful_prefix = [
        response("0301000a34120000"),
        {"operation": "current_eus_session", "session": "0x0044"},
        {"operation": "allocate_event", "size": 24, "succeeded": True},
        {
            "operation": "queue_event",
            "queue_handle": f"0x{QUEUE_HANDLE:08x}",
            "session": "0x0044",
            "event_type": 0x200,
            "payload_length": 12,
            "payload_hex": targets.hex(),
            "succeeded": True,
        },
        {
            "operation": "signal_event_thread",
            "event_flag_handle": f"0x{EVENT_FLAG_HANDLE:08x}",
            "bits": "0x00400000",
        },
    ]
    assert adv_two_targets["effects"] == successful_prefix
    assert adv_malformed_zero["effects"] == [
        {**response("0301000affff0000")},
        *successful_prefix[1:],
    ]
    assert adv_queue_unavailable["effects"] == [
        response("0301000a34120000"),
        {"operation": "current_eus_session", "session": "0x0044"},
    ]
    assert adv_queue_failure["effects"] == [
        *successful_prefix[:3],
        {
            **successful_prefix[3],
            "succeeded": False,
        },
        {"operation": "free_failed_event", "pointer": f"0x{EVENT:08x}"},
    ]
    assert adv_allocation_failure["effects"] == [
        response("0301000a34120000"),
        {"operation": "current_eus_session", "session": "0x0044"},
        {"operation": "allocate_event", "size": 24, "succeeded": False},
    ]

    return {
        "fixture_groups": 11,
        "pair_auth": {
            "header_only": pair_header_only,
            "non_phone_type": pair_other_type,
            "phone_type": pair_phone,
            "malformed_declared_zero": pair_malformed_zero,
        },
        "advertise_start": {
            "header_only_rejected": adv_header_only,
            "older_six_byte_payload_rejected": adv_older_six_bytes,
            "two_target_payload": adv_two_targets,
            "malformed_declared_zero": adv_malformed_zero,
            "queue_unavailable_after_success_response": adv_queue_unavailable,
            "queue_failure_after_success_response": adv_queue_failure,
            "allocation_failure_after_success_response": adv_allocation_failure,
        },
        "interpretation": {
            "pair_auth_exact_header_only_is_silent": True,
            "pair_auth_type_one_order": [
                "phone role setter",
                "event type 2 enqueue",
                "one-byte zero response",
            ],
            "adv_start_requires_twelve_payload_bytes": True,
            "adv_start_success_response_precedes_event_work": True,
            "adv_start_event_uses_current_eus_session": True,
            "adv_start_copies_two_six_byte_targets": True,
            "adv_start_queue_failures_are_not_returned_to_phone": True,
        },
        "safety": {
            "physical_device_access": False,
            "phone_role_setter_intercepted": True,
            "ble_event_delivery_intercepted": True,
            "ble_response_intercepted": True,
            "advertising_and_disconnect_paths_unreachable": True,
            "pairing_and_peer_manager_paths_unreachable": True,
            "live_address_access": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
