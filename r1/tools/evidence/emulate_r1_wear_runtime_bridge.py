#!/usr/bin/env python3
"""Execute isolated production-Thumb wear runtime, charge, and sleep-bridge fixtures."""

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


WEAR_LED_CALLBACK = 0x0003D150
SLEEP_STATUS_CALLBACK = 0x0003D1B8
CHARGE_CHECK_TIMEOUT = 0x0004C3D0
CHARGE_STATUS_CALLBACK = 0x0004C4B8
SLEEP_FORCE_AWAKE = 0x0004A4B4
SLEEP_HISTORY_TIMEOUT = 0x0004A56C
SLEEP_PUBLISH_STATUS = 0x0004A7F4
SLEEP_VIVO_TIMEOUT = 0x0004A998

SUBSCRIBE = 0x000897E8
UNSUBSCRIBE = 0x00089B08
TIMER_CREATE = 0x0008A310
TIMER_RESTART = 0x0008A59E
TIMER_DELETE = 0x0008A3C0
SENSOR_EVENT = 0x0008B028
SYSTEM_EVENT = 0x0008D8FC
LOG_FLAGS = 0x000914EC
GOMORE_AUTHORIZATION = 0x00049410
LOW_LEVEL_CHARGE_STATE = 0x0003529A
SENSOR_POLICY_A = 0x0008345C
SENSOR_POLICY_B = 0x000913FC
SENSOR_POLICY_CONTEXT = 0x00091270
SYSTEM_TASK_EVENT = 0x00033AE4
SLEEP_SHUTDOWN = 0x0004BD54
FINAL_SLEEP_RESULT = 0x0006B50C

WEAR_RUNTIME = 0x20006E94
SLEEP_BRIDGE = 0x20006ED4
WEAR_STATE = 0x2001E454
CALLBACK_PAYLOAD = RAM_BASE + 0x3A000


class WearRuntimeFixture:
    def __init__(self, image: bytes) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.next_handle = RAM_BASE + 0x3B000
        self.timer_creation_succeeds = True
        self.goMore_authorization_result = 1
        self.low_level_charge_state = 0
        self.subscriptions: list[tuple[str, str, int]] = []
        self.unsubscriptions: list[str] = []
        self.timers: list[tuple[int, int, int]] = []
        self.deleted_timers: list[int] = []
        self.sensor_events: list[tuple[int, bytes]] = []
        self.system_events: list[tuple[int, bytes]] = []
        self.goMore_requests: list[tuple[int, int]] = []
        self.sensor_policy_resets: list[tuple[int, int]] = []
        self.system_task_events: list[int] = []
        self.sleep_shutdowns = 0
        self.final_sleep_results = 0
        self.machine.uc.mem_write(WEAR_RUNTIME, b"\x00" * 32)
        self.machine.uc.mem_write(SLEEP_BRIDGE, b"\x00" * 12)
        self.machine.uc.mem_write(WEAR_STATE, b"\x00" * 41)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)
        self.machine.uc.hook_add(UC_HOOK_MEM_INVALID, self._invalid_memory)

    @staticmethod
    def _return(uc: Any, value: int = 0) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _allocate_handle(self) -> int:
        result = self.next_handle
        self.next_handle += 0x20
        return result

    def _cstring(self, address: int, maximum: int = 32) -> str:
        raw = bytes(self.machine.uc.mem_read(address, maximum))
        return raw.split(b"\x00", 1)[0].decode("ascii")

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == LOG_FLAGS:
            self._return(uc, 0)
        elif address == SUBSCRIBE:
            topic = self._cstring(uc.reg_read(UC_ARM_REG_R0))
            owner = self._cstring(uc.reg_read(UC_ARM_REG_R1))
            callback = uc.reg_read(UC_ARM_REG_R2)
            handle = self._allocate_handle()
            self.subscriptions.append((topic, owner, callback))
            self._return(uc, handle)
        elif address == UNSUBSCRIBE:
            self.unsubscriptions.append(self._cstring(uc.reg_read(UC_ARM_REG_R0)))
            self._return(uc)
        elif address == TIMER_CREATE:
            callback = uc.reg_read(UC_ARM_REG_R0)
            duration = uc.reg_read(UC_ARM_REG_R1)
            handle = self._allocate_handle() if self.timer_creation_succeeds else 0
            self.timers.append((callback, duration, handle))
            self._return(uc, handle)
        elif address == TIMER_RESTART:
            self._return(uc)
        elif address == TIMER_DELETE:
            self.deleted_timers.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)
        elif address in (SENSOR_EVENT, SYSTEM_EVENT):
            event_id = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            payload = bytes(uc.mem_read(pointer, length))
            target = self.sensor_events if address == SENSOR_EVENT else self.system_events
            target.append((event_id, payload))
            self._return(uc)
        elif address == GOMORE_AUTHORIZATION:
            mode = uc.reg_read(UC_ARM_REG_R0)
            enabled = uc.reg_read(UC_ARM_REG_R1)
            self.goMore_requests.append((mode, enabled))
            self._return(uc, self.goMore_authorization_result if enabled else 1)
        elif address == LOW_LEVEL_CHARGE_STATE:
            self._return(uc, self.low_level_charge_state)
        elif address in (SENSOR_POLICY_A, SENSOR_POLICY_B):
            self.sensor_policy_resets.append(
                (address, uc.reg_read(UC_ARM_REG_R1))
            )
            self._return(uc)
        elif address == SENSOR_POLICY_CONTEXT:
            self._return(uc, RAM_BASE + 0x3C000)
        elif address == SYSTEM_TASK_EVENT:
            self.system_task_events.append(uc.reg_read(UC_ARM_REG_R0))
            self._return(uc)
        elif address == SLEEP_SHUTDOWN:
            self.sleep_shutdowns += 1
            self._return(uc)
        elif address == FINAL_SLEEP_RESULT:
            self.final_sleep_results += 1
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
        self.subscriptions.clear()
        self.unsubscriptions.clear()
        self.timers.clear()
        self.deleted_timers.clear()
        self.sensor_events.clear()
        self.system_events.clear()
        self.goMore_requests.clear()
        self.sensor_policy_resets.clear()
        self.system_task_events.clear()
        self.sleep_shutdowns = 0
        self.final_sleep_results = 0

    def u32(self, address: int) -> int:
        return struct.unpack("<I", bytes(self.machine.uc.mem_read(address, 4)))[0]

    def write_u32(self, address: int, value: int) -> None:
        self.machine.uc.mem_write(address, struct.pack("<I", value))

    def runtime(self) -> dict[str, int]:
        raw = bytes(self.machine.uc.mem_read(WEAR_RUNTIME, 32))
        words = struct.unpack_from("<7I", raw, 4)
        return {
            "wear_led": raw[0],
            "sleep_status": raw[1],
            "sleep_living": raw[2],
            "acc_handle": words[0],
            "adt_handle": words[1],
            "living_handle": words[2],
            "adt_timer": words[3],
            "charge_timer": words[4],
            "raw_hr_handle": words[5],
            "raw_hr_timer": words[6],
        }

    def bridge(self) -> dict[str, int]:
        raw = bytes(self.machine.uc.mem_read(SLEEP_BRIDGE, 12))
        return {
            "status": raw[0],
            "authorization": raw[1],
            "reserved": struct.unpack_from("<H", raw, 2)[0],
            "history_timer": struct.unpack_from("<I", raw, 4)[0],
            "vivo_timer": struct.unpack_from("<I", raw, 8)[0],
        }

    def wear_state(self) -> dict[str, int]:
        raw = bytes(self.machine.uc.mem_read(WEAR_STATE, 41))
        return {
            "history_count": raw[0x14],
            "previous": struct.unpack_from("<I", raw, 0x18)[0],
            "state": raw[0x24],
            "policy": raw[0x25],
            "charge": raw[0x26],
        }


def run(image: bytes) -> dict[str, Any]:
    fixture = WearRuntimeFixture(image)

    # Wear-LED zero opens the bounded ADT history subscription and seven-second timeout.
    fixture.machine.uc.mem_write(WEAR_STATE + 0x26, b"\x00")
    fixture.machine.call(WEAR_LED_CALLBACK, 0)
    wear_led_started = fixture.runtime()
    wear_led_started_topics = list(fixture.subscriptions)
    wear_led_started_timers = [(duration, handle) for _, duration, handle in fixture.timers]

    # Wear-LED one closes ADT and clears only its count/previous-history state.
    fixture.machine.uc.mem_write(WEAR_STATE + 0x14, b"\x05")
    fixture.write_u32(WEAR_STATE + 0x18, 0x11223344)
    fixture.reset_observations()
    fixture.machine.call(WEAR_LED_CALLBACK, 1)
    wear_led_stopped = fixture.runtime()
    wear_led_stopped_state = fixture.wear_state()

    # Sleep callback resets living confirmation only on exact 0 -> 1.
    fixture.machine.uc.mem_write(WEAR_RUNTIME + 1, b"\x00\x01")
    fixture.machine.uc.mem_write(CALLBACK_PAYLOAD, b"\x01")
    fixture.machine.call(SLEEP_STATUS_CALLBACK, CALLBACK_PAYLOAD)
    sleep_transition = fixture.runtime()
    fixture.machine.uc.mem_write(WEAR_RUNTIME + 2, b"\x01")
    fixture.machine.call(SLEEP_STATUS_CALLBACK, CALLBACK_PAYLOAD)
    sleep_repeat = fixture.runtime()

    # Entering charge status one stops ADT, starts raw-HR readiness, reports not-worn,
    # and starts the sixty-second fallback check without changing internal wear state.
    fixture.machine.uc.mem_write(WEAR_RUNTIME, b"\x00" * 32)
    fixture.write_u32(WEAR_RUNTIME + 8, 0x11110000)
    fixture.write_u32(WEAR_RUNTIME + 16, 0x22220000)
    fixture.machine.uc.mem_write(WEAR_STATE, b"\x00" * 41)
    fixture.machine.uc.mem_write(WEAR_STATE + 0x14, b"\x03")
    fixture.write_u32(WEAR_STATE + 0x18, 0x33330000)
    fixture.machine.uc.mem_write(WEAR_STATE + 0x24, b"\x02\x02\x00")
    fixture.reset_observations()
    fixture.machine.call(CHARGE_STATUS_CALLBACK, 1)
    charging_runtime = fixture.runtime()
    charging_state = fixture.wear_state()
    charging_events = list(fixture.sensor_events)
    charging_topics = list(fixture.subscriptions)
    charging_timers = [duration for _, duration, _ in fixture.timers]

    # The check retains charge for normalized status two, but clears only on zero.
    fixture.low_level_charge_state = 13
    fixture.reset_observations()
    fixture.machine.call(CHARGE_CHECK_TIMEOUT)
    charge_two_runtime = fixture.runtime()
    charge_two_state = fixture.wear_state()
    fixture.low_level_charge_state = 0
    fixture.reset_observations()
    fixture.machine.call(CHARGE_CHECK_TIMEOUT)
    charge_zero_runtime = fixture.runtime()
    charge_zero_state = fixture.wear_state()
    charge_zero_events = list(fixture.sensor_events)
    charge_zero_policy_resets = list(fixture.sensor_policy_resets)
    charge_zero_task_events = list(fixture.system_task_events)

    # A sleep-result 0 -> 1 transition skips vivo probing only for exact state two.
    fixture.machine.uc.mem_write(SLEEP_BRIDGE, b"\x00" * 12)
    fixture.machine.uc.mem_write(WEAR_STATE + 0x24, b"\x02")
    fixture.reset_observations()
    fixture.machine.call(SLEEP_PUBLISH_STATUS, 1)
    confirmed_bridge = fixture.bridge()
    confirmed_events = (list(fixture.system_events), list(fixture.sensor_events))
    confirmed_mode_requests = list(fixture.goMore_requests)

    # State zero starts GoMore mode five and the five-second probe.
    fixture.machine.uc.mem_write(SLEEP_BRIDGE, b"\x00" * 12)
    fixture.machine.uc.mem_write(WEAR_STATE + 0x24, b"\x00")
    fixture.goMore_authorization_result = 1
    fixture.timer_creation_succeeds = True
    fixture.reset_observations()
    fixture.machine.call(SLEEP_PUBLISH_STATUS, 1)
    probing_bridge = fixture.bridge()
    probing_events = (list(fixture.system_events), list(fixture.sensor_events))
    probing_mode_requests = list(fixture.goMore_requests)
    probing_timer_durations = [duration for _, duration, _ in fixture.timers]

    # The five-second timeout forces status zero, finalizes sleep, disables mode five,
    # and creates a three-second history timer when wear remains zero.
    vivo_timer_handle = probing_bridge["vivo_timer"]
    fixture.reset_observations()
    fixture.machine.call(SLEEP_VIVO_TIMEOUT, vivo_timer_handle)
    forced_bridge = fixture.bridge()
    forced_events = list(fixture.system_events)
    forced_mode_requests = list(fixture.goMore_requests)
    forced_timer_durations = [duration for _, duration, _ in fixture.timers]
    forced_shutdowns = fixture.sleep_shutdowns
    forced_final_results = fixture.final_sleep_results

    # The delayed callback publishes the exact event-14 sleep-history query.
    history_timer_handle = forced_bridge["history_timer"]
    fixture.reset_observations()
    fixture.machine.call(SLEEP_HISTORY_TIMEOUT, history_timer_handle, 0, 0, 0x11223344)
    history_bridge = fixture.bridge()
    history_events = list(fixture.system_events)

    # Failed five-second timer creation immediately rolls back a successful authorization.
    fixture.machine.uc.mem_write(SLEEP_BRIDGE, b"\x00" * 12)
    fixture.machine.uc.mem_write(WEAR_STATE + 0x24, b"\x00")
    fixture.timer_creation_succeeds = False
    fixture.goMore_authorization_result = 1
    fixture.reset_observations()
    fixture.machine.call(SLEEP_PUBLISH_STATUS, 1)
    failed_timer_bridge = fixture.bridge()
    failed_timer_mode_requests = list(fixture.goMore_requests)

    observed = {
        "wear_led_start": {
            "status": wear_led_started["wear_led"],
            "adt_handle_nonzero": wear_led_started["adt_handle"] != 0,
            "adt_timer_nonzero": wear_led_started["adt_timer"] != 0,
            "topics": [[topic, owner] for topic, owner, _ in wear_led_started_topics],
            "timer_durations": [duration for duration, _ in wear_led_started_timers],
        },
        "wear_led_stop": {
            "status": wear_led_stopped["wear_led"],
            "adt_handle": wear_led_stopped["adt_handle"],
            "adt_timer": wear_led_stopped["adt_timer"],
            "history_count": wear_led_stopped_state["history_count"],
            "previous": wear_led_stopped_state["previous"],
        },
        "sleep_callback": {
            "transition": [
                sleep_transition["sleep_status"], sleep_transition["sleep_living"],
            ],
            "repeat": [sleep_repeat["sleep_status"], sleep_repeat["sleep_living"]],
        },
        "charge_enter": {
            "wear_state": charging_state["state"],
            "charge_state": charging_state["charge"],
            "adt_handle": charging_runtime["adt_handle"],
            "adt_timer": charging_runtime["adt_timer"],
            "raw_hr_handle_nonzero": charging_runtime["raw_hr_handle"] != 0,
            "raw_hr_timer_nonzero": charging_runtime["raw_hr_timer"] != 0,
            "charge_timer_nonzero": charging_runtime["charge_timer"] != 0,
            "notification": [list(payload) for event, payload in charging_events if event == 4],
            "topics": [[topic, owner] for topic, owner, _ in charging_topics],
            "timer_durations": charging_timers,
        },
        "charge_check": {
            "normalized_two": [
                charge_two_state["charge"], charge_two_runtime["charge_timer"] != 0,
            ],
            "normalized_zero": [
                charge_zero_state["charge"], charge_zero_runtime["charge_timer"],
            ],
            "notification": [
                list(payload) for event, payload in charge_zero_events if event == 4
            ],
            "policy_reset_count": len(charge_zero_policy_resets),
            "task_events": charge_zero_task_events,
        },
        "confirmed_sleep_status": {
            "bridge": confirmed_bridge,
            "system_events": [
                [event, list(payload)] for event, payload in confirmed_events[0]
            ],
            "sensor_events": [
                [event, list(payload)] for event, payload in confirmed_events[1]
            ],
            "mode_requests": [list(item) for item in confirmed_mode_requests],
        },
        "vivo_probe": {
            "bridge": probing_bridge,
            "system_events": [
                [event, list(payload)] for event, payload in probing_events[0]
            ],
            "sensor_events": [
                [event, list(payload)] for event, payload in probing_events[1]
            ],
            "mode_requests": [list(item) for item in probing_mode_requests],
            "timer_durations": probing_timer_durations,
        },
        "forced_awake": {
            "bridge": forced_bridge,
            "system_events": [
                [event, list(payload)] for event, payload in forced_events
            ],
            "mode_requests": [list(item) for item in forced_mode_requests],
            "timer_durations": forced_timer_durations,
            "sleep_shutdowns": forced_shutdowns,
            "final_sleep_results": forced_final_results,
        },
        "history_timeout": {
            "bridge": history_bridge,
            "system_events": [
                [event, list(payload)] for event, payload in history_events
            ],
        },
        "failed_vivo_timer": {
            "bridge": failed_timer_bridge,
            "mode_requests": [list(item) for item in failed_timer_mode_requests],
        },
    }

    expected = {
        "wear_led_start": {
            "status": 0,
            "adt_handle_nonzero": True,
            "adt_timer_nonzero": True,
            "topics": [["adt", "algo"]],
            "timer_durations": [7_000],
        },
        "wear_led_stop": {
            "status": 1,
            "adt_handle": 0,
            "adt_timer": 0,
            "history_count": 0,
            "previous": 0,
        },
        "sleep_callback": {
            "transition": [1, 0],
            "repeat": [1, 1],
        },
        "charge_enter": {
            "wear_state": 2,
            "charge_state": 1,
            "adt_handle": 0,
            "adt_timer": 0,
            "raw_hr_handle_nonzero": True,
            "raw_hr_timer_nonzero": True,
            "charge_timer_nonzero": True,
            "notification": [[0]],
            "topics": [["raw_hr", "wearled"]],
            "timer_durations": [3_000, 60_000],
        },
        "charge_check": {
            "normalized_two": [1, True],
            "normalized_zero": [0, 0],
            "notification": [[1]],
            "policy_reset_count": 2,
            "task_events": [0x1000],
        },
        "confirmed_sleep_status": {
            "bridge": {
                "status": 1,
                "authorization": 0,
                "reserved": 0,
                "history_timer": 0,
                "vivo_timer": 0,
            },
            "system_events": [[12, [1]]],
            "sensor_events": [[3, [1]]],
            "mode_requests": [],
        },
        "vivo_probe": {
            "bridge": {
                "status": 1,
                "authorization": 1,
                "reserved": 0,
                "history_timer": 0,
                "vivo_timer": probing_bridge["vivo_timer"],
            },
            "system_events": [[12, [1]]],
            "sensor_events": [[3, [1]]],
            "mode_requests": [[5, 1]],
            "timer_durations": [5_000],
        },
        "forced_awake": {
            "bridge": {
                "status": 0,
                "authorization": 0,
                "reserved": 0,
                "history_timer": forced_bridge["history_timer"],
                "vivo_timer": 0,
            },
            "system_events": [[12, [0]]],
            "mode_requests": [[5, 0]],
            "timer_durations": [3_000],
            "sleep_shutdowns": 1,
            "final_sleep_results": 1,
        },
        "history_timeout": {
            "bridge": {
                "status": 0,
                "authorization": 0,
                "reserved": 0,
                "history_timer": 0,
                "vivo_timer": 0,
            },
            "system_events": [[14, [6, 1, 0, 0, 0x44, 0x33, 0x22, 0x11]]],
        },
        "failed_vivo_timer": {
            "bridge": {
                "status": 1,
                "authorization": 0,
                "reserved": 0,
                "history_timer": 0,
                "vivo_timer": 0,
            },
            "mode_requests": [[5, 1], [5, 0]],
        },
    }
    if observed != expected:
        raise ValueError(f"production wear-runtime fixture mismatch: {observed} != {expected}")

    return {
        "validated": True,
        "case_count": 9,
        "observed": observed,
        "safety": {
            "emulated_private_flash_and_ram_only": True,
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
