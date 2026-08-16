#!/usr/bin/env python3
"""Execute isolated production-Thumb GoMore authorization fixtures."""

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
)

from emulate_r1_locomotion_window import LocomotionFirmwareFixture


AUTHORIZATION_DISPATCH = 0x00049410
LOG_FLAGS = 0x000914EC
STREAM_REGISTER = 0x000897E8
STREAM_UNREGISTER = 0x00089B08
TIMER_CREATE = 0x0008A368
TIMER_DELETE = 0x0008A3C0
AUTHORIZATION_STATE = 0x20006DA0
ENGINE_STATE = 0x2001A56C


class AuthorizationFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.next_handle = 0x100
        self.registered: list[str] = []
        self.unregistered: list[str] = []
        self.created_periods: list[int] = []
        self.deleted_handles: list[int] = []
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _cstring(self, address: int) -> str:
        data = bytearray()
        while True:
            value = self.machine.uc.mem_read(address + len(data), 1)[0]
            if value == 0:
                return data.decode("ascii")
            data.append(value)

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == STREAM_REGISTER:
            self.registered.append(self._cstring(uc.reg_read(UC_ARM_REG_R0)))
            self.next_handle += 1
            self._return(uc, self.next_handle)
        elif address == STREAM_UNREGISTER:
            self.unregistered.append(self._cstring(uc.reg_read(UC_ARM_REG_R0)))
            self._return(uc)
        elif address == TIMER_CREATE:
            self.created_periods.append(uc.reg_read(UC_ARM_REG_R1))
            self.next_handle += 1
            self._return(uc, self.next_handle)
        elif address == TIMER_DELETE:
            self.deleted_handles.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)

    def reset(self) -> None:
        self.machine.uc.mem_write(AUTHORIZATION_STATE, b"\x00" * 0xA0)
        self.machine.uc.mem_write(ENGINE_STATE, b"\x00" * 0x40)
        self.registered.clear()
        self.unregistered.clear()
        self.created_periods.clear()
        self.deleted_handles.clear()
        self.next_handle = 0x100

    def call(self, slot: int, enable: int) -> int:
        return self.machine.call(AUTHORIZATION_DISPATCH, slot, enable, 0, 0)

    def handle(self, offset: int) -> int:
        return struct.unpack(
            "<I", self.machine.uc.mem_read(AUTHORIZATION_STATE + offset, 4)
        )[0]

    def record_flags(self, slot: int) -> int:
        return self.machine.uc.mem_read(
            AUTHORIZATION_STATE + 0x24 + slot * 0x10, 1
        )[0]


def run(image: bytes) -> dict[str, Any]:
    fixture = AuthorizationFixture(image)

    fixture.reset()
    uninitialized_return = fixture.call(0, 1)

    fixture.reset()
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE, b"\x01")
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x18,
                                 struct.pack("<I", 0x99))
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x1C,
                                 struct.pack("<II", 0x55, 0x66))
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x24, b"\x1E")
    fixture.machine.uc.mem_write(ENGINE_STATE + 0x24, b"\x01")
    fixture.machine.uc.mem_write(ENGINE_STATE + 0x28,
                                 struct.pack("<f", 72.0))
    enabled_return = fixture.call(0, 1)
    enabled = {
        "return": enabled_return,
        "registered": list(fixture.registered),
        "deleted_handles": list(fixture.deleted_handles),
        "flags": fixture.record_flags(0),
        "handles": [fixture.handle(offset) for offset in (8, 12, 16, 20)],
        "idle_timer": fixture.handle(0x18),
    }
    fixture.registered.clear()
    fixture.deleted_handles.clear()
    disabled_return = fixture.call(0, 0)
    disabled = {
        "return": disabled_return,
        "unregistered": list(fixture.unregistered),
        "created_periods": list(fixture.created_periods),
        "flags": fixture.record_flags(0),
        "handles": [fixture.handle(offset) for offset in (8, 12, 16, 20)],
        "idle_timer": fixture.handle(0x18),
        "auxiliary": [fixture.handle(0x1C), fixture.handle(0x20)],
        "engine_hrv": fixture.machine.uc.mem_read(ENGINE_STATE + 0x24, 1)[0],
        "engine_hr": struct.unpack(
            "<f", fixture.machine.uc.mem_read(ENGINE_STATE + 0x28, 4)
        )[0],
    }
    unchanged_return = fixture.call(0, 0)

    fixture.reset()
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE, b"\x01")
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x0C,
                                 struct.pack("<I", 0x77))
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x18,
                                 struct.pack("<I", 0x99))
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x24, b"\x04")
    fixture.machine.uc.mem_write(AUTHORIZATION_STATE + 0x34, b"\x05")
    shared_enable_return = fixture.call(0, 1)
    shared_enable = {
        "return": shared_enable_return,
        "registered": list(fixture.registered),
        "deleted_handles": list(fixture.deleted_handles),
        "stream_handle": fixture.handle(0x0C),
        "idle_timer": fixture.handle(0x18),
    }
    fixture.deleted_handles.clear()
    shared_disable_return = fixture.call(0, 0)
    shared_disable = {
        "return": shared_disable_return,
        "unregistered": list(fixture.unregistered),
        "created_periods": list(fixture.created_periods),
        "stream_handle": fixture.handle(0x0C),
        "idle_timer": fixture.handle(0x18),
    }

    assert uninitialized_return == 0
    assert enabled == {
        "return": 1,
        "registered": ["acc", "raw_hr", "hr", "hrv"],
        "deleted_handles": [0x99],
        "flags": 0x1F,
        "handles": [0x101, 0x102, 0x103, 0x104],
        "idle_timer": 0,
    }
    assert disabled == {
        "return": 1,
        "unregistered": ["acc", "raw_hr", "hr", "hrv"],
        "created_periods": [1000],
        "flags": 0x1E,
        "handles": [0, 0, 0, 0],
        "idle_timer": 0x105,
        "auxiliary": [0, 0],
        "engine_hrv": 0,
        "engine_hr": 0.0,
    }
    assert unchanged_return == 0
    assert shared_enable == {
        "return": 1,
        "registered": [],
        "deleted_handles": [0x99],
        "stream_handle": 0x77,
        "idle_timer": 0,
    }
    assert shared_disable == {
        "return": 1,
        "unregistered": [],
        "created_periods": [],
        "stream_handle": 0x77,
        "idle_timer": 0,
    }
    return {
        "fixture_groups": 5,
        "uninitialized_return": uninitialized_return,
        "enabled": enabled,
        "disabled": disabled,
        "unchanged_return": unchanged_return,
        "shared_enable": shared_enable,
        "shared_disable": shared_disable,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "flash_writes": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.image.read_bytes()), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
