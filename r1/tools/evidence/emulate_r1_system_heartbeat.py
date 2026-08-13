#!/usr/bin/env python3
"""Execute the 28-byte system 0x7f handler with both queue helpers intercepted.

No delayed callback is actually queued. BLE, protocol response helpers, sensors, storage, physical
hardware, and host health stores are absent.
"""

from __future__ import annotations

import argparse
import json
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

from emulate_r1_locomotion_window import LocomotionFirmwareFixture


HANDLER = 0x00084130
CALLBACK = 0x0004D2F0
CALLBACK_THUMB = CALLBACK | 1
CANCEL_DELAYED = 0x00065D64
SCHEDULE_DELAYED = 0x00065B4C
RESPONSE_HELPERS = {0x00082844, 0x0008287C, 0x00084C5E, 0x000828B4}
DELAY_MILLISECONDS = 0x7800


class SystemHeartbeatFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.calls: list[dict[str, Any]] = []
        self.response_calls: list[str] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == CANCEL_DELAYED:
            self.calls.append({
                "operation": "cancel",
                "callback_thumb": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "context_filter_raw": uc.reg_read(UC_ARM_REG_R1),
            })
            self._return(uc, 1)
        elif address == SCHEDULE_DELAYED:
            self.calls.append({
                "operation": "schedule",
                "callback_thumb": f"0x{uc.reg_read(UC_ARM_REG_R0):08x}",
                "context_raw": f"0x{uc.reg_read(UC_ARM_REG_R1):08x}",
                "delay_milliseconds": uc.reg_read(UC_ARM_REG_R2),
            })
            self._return(uc, 0)
        elif address in RESPONSE_HELPERS:
            self.response_calls.append(f"0x{address:08x}")
            self._return(uc, 0)

    def run(
        self,
        *,
        session_context: int,
        ignored_request_pointer: int,
        ignored_argument2: int,
        ignored_argument3: int,
    ) -> dict[str, Any]:
        self.calls.clear()
        self.response_calls.clear()
        self.machine.call(
            HANDLER,
            session_context,
            ignored_request_pointer,
            ignored_argument2,
            ignored_argument3,
        )
        return {
            "session_context": f"0x{session_context:08x}",
            "calls": list(self.calls),
            "response_calls": list(self.response_calls),
        }

    def run_callback(self, context: int) -> dict[str, Any]:
        self.calls.clear()
        self.response_calls.clear()
        result = self.machine.call(CALLBACK, context, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF)
        return {
            "context_raw": f"0x{context:08x}",
            "return_r0_raw": f"0x{result:08x}",
            "queue_helper_calls": list(self.calls),
            "response_calls": list(self.response_calls),
        }


def expected_calls(session_context: int) -> list[dict[str, Any]]:
    return [
        {
            "operation": "cancel",
            "callback_thumb": f"0x{CALLBACK_THUMB:08x}",
            "context_filter_raw": 0,
        },
        {
            "operation": "schedule",
            "callback_thumb": f"0x{CALLBACK_THUMB:08x}",
            "context_raw": f"0x{session_context:08x}",
            "delay_milliseconds": DELAY_MILLISECONDS,
        },
    ]


def run(image: bytes) -> dict[str, Any]:
    fixture = SystemHeartbeatFixture(image)
    zero = fixture.run(
        session_context=0,
        ignored_request_pointer=0,
        ignored_argument2=0,
        ignored_argument3=0,
    )
    ordinary = fixture.run(
        session_context=0x20037100,
        ignored_request_pointer=0xDEADBEEF,
        ignored_argument2=0x55667788,
        ignored_argument3=0x99AABBCC,
    )
    all_bits = fixture.run(
        session_context=0xFFFFFFFF,
        ignored_request_pointer=0xFFFFFFFF,
        ignored_argument2=0xFFFFFFFF,
        ignored_argument3=0xFFFFFFFF,
    )
    callback = fixture.run_callback(0xA5A5A5A5)

    for result, context in ((zero, 0), (ordinary, 0x20037100), (all_bits, 0xFFFFFFFF)):
        assert result["calls"] == expected_calls(context)
        assert result["response_calls"] == []
    assert callback["queue_helper_calls"] == []
    assert callback["response_calls"] == []
    # `bx lr` leaves r0/context untouched.
    assert callback["return_r0_raw"] == "0xa5a5a5a5"

    return {
        "fixture_groups": 4,
        "zero_context": zero,
        "ordinary_context_and_ignored_request_arguments": ordinary,
        "all_bits_context_and_ignored_request_arguments": all_bits,
        "delayed_callback": callback,
        "interpretation": {
            "protocol_response_emitted": False,
            "delayed_callback_effects": 0,
            "connection_liveness_signal": False,
        },
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "queue_helpers_intercepted": True,
            "delayed_callback_executes_bx_lr_only": True,
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
