#!/usr/bin/env python3
"""Execute the production R1 RMSSD helper with synthetic RR intervals in private emulated RAM.

The SHA-pinned helper uses firmware allocation/free and logging services. This fixture replaces
only those environment services with two bounded private buffers and no-op diagnostics, while the
production filter, Float32 accumulation, division and square root execute unchanged. It never
connects to BLE, sensors, health storage, or a physical ring.
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
    UC_ARM_REG_S0,
)

from emulate_r1_locomotion_window import IMAGE_SHA256, LocomotionFirmwareFixture, RAM_BASE


RMSSD = 0x000575D8
ALLOCATE = 0x000855A0
FREE = 0x00095D48
MODE = 0x0004A8BC
LOG_FLAGS = 0x000914EC
INTERVALS = RAM_BASE + 0x30000
VALIDITY = RAM_BASE + 0x31000
DIFFERENCES = RAM_BASE + 0x32000
PRODUCER = 0x0004A24C
ELIGIBILITY = 0x0004C634
TIMESTAMP = 0x0008ADA4
PUBLISH_EVENT = 0x0008D8FC
RESET_PRODUCER = 0x00049E00
CONVERSION_RESULT_SITE = 0x0004A31E
RMSSD_RETURN_SITE = 0x0004A2E8
PRODUCER_STATE = 0x2001A300
PRODUCER_CONTROL = 0x20006D84
PRODUCER_INPUT = RAM_BASE + 0x33000


def float_record(bits: int) -> dict[str, Any]:
    return {
        "bits": f"0x{bits:08x}",
        "value": struct.unpack("<f", struct.pack("<I", bits))[0],
    }


class RMSSDFixture:
    def __init__(self, image: bytes, *, alternate_mode: bool = False) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.alternate_mode = alternate_mode
        self.allocation_count = 0
        self.machine.uc.hook_add(UC_HOOK_CODE, self._environment_hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _environment_hook(
        self, uc: Any, address: int, size: int, user_data: Any
    ) -> None:
        del size, user_data
        if address == ALLOCATE:
            destination = VALIDITY if self.allocation_count == 0 else DIFFERENCES
            self.allocation_count += 1
            self._return(uc, destination)
        elif address == FREE:
            self._return(uc, 0)
        elif address == MODE:
            self._return(uc, int(self.alternate_mode))
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def calculate(self, intervals: list[int]) -> dict[str, Any]:
        if len(intervals) > 0xFFFF or any(not 0 <= value <= 0xFFFF for value in intervals):
            raise ValueError("RR intervals must be UInt16 values with a UInt16 count")
        self.allocation_count = 0
        self.machine.uc.mem_write(
            INTERVALS,
            struct.pack("<" + "H" * len(intervals), *intervals),
        )
        self.machine.uc.mem_write(VALIDITY, b"\xa5" * max(1, len(intervals)))
        self.machine.uc.mem_write(DIFFERENCES, b"\xa5" * max(2, len(intervals) * 2))
        self.machine.call(RMSSD, INTERVALS if intervals else 0, len(intervals))
        output_bits = self.machine.uc.reg_read(UC_ARM_REG_S0)
        return {
            "intervals": intervals,
            "alternate_mode": self.alternate_mode,
            "output": float_record(output_bits),
            "validity": list(self.machine.uc.mem_read(VALIDITY, len(intervals))),
            "difference_words": list(struct.unpack(
                "<" + "H" * max(0, len(intervals) - 1),
                bytes(self.machine.uc.mem_read(DIFFERENCES, max(0, len(intervals) * 2 - 2))),
            )),
            "allocation_count": self.allocation_count,
        }


class HRVPublicationFixture:
    def __init__(
        self,
        image: bytes,
        *,
        rmssd_bits: int,
        eligibility: bool = True,
    ) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.rmssd_bits = rmssd_bits
        self.eligibility = eligibility
        self.converted_uint32: int | None = None
        self.published_event: dict[str, Any] | None = None
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == RMSSD:
            uc.reg_write(UC_ARM_REG_S0, self.rmssd_bits)
            uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))
        elif address == ELIGIBILITY:
            self._return(uc, int(self.eligibility))
        elif address == TIMESTAMP:
            self._return(uc, 0x12345678)
        elif address == CONVERSION_RESULT_SITE:
            self.converted_uint32 = uc.reg_read(UC_ARM_REG_R0)
        elif address == PUBLISH_EVENT:
            event_id = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            self.published_event = {
                "event_id": event_id,
                "payload_hex": bytes(uc.mem_read(pointer, length)).hex(),
                "payload_length": length,
            }
            self._return(uc, 0)
        elif address in (RESET_PRODUCER, LOG_FLAGS):
            self._return(uc, 0)

    def run(self) -> dict[str, Any]:
        self.machine.uc.mem_write(PRODUCER_STATE, b"\x00" * 0xD0)
        self.machine.uc.mem_write(PRODUCER_STATE + 0xCA, struct.pack("<H", 70))
        self.machine.uc.mem_write(PRODUCER_STATE + 0xCC, struct.pack("<H", 70))
        self.machine.uc.mem_write(PRODUCER_STATE + 0xCE, struct.pack("<H", 59))
        self.machine.uc.mem_write(PRODUCER_CONTROL, b"\x00" * 0x20)
        self.machine.uc.mem_write(PRODUCER_INPUT, b"\x00" * 10)
        self.machine.call(PRODUCER, 0, PRODUCER_INPUT)
        return {
            "rmssd": float_record(self.rmssd_bits),
            "eligibility": self.eligibility,
            "converted_uint32": self.converted_uint32,
            "published_event": self.published_event,
        }


class HRVProducerFixture:
    def __init__(self, image: bytes, *, alternate_mode: bool = False) -> None:
        self.machine = LocomotionFirmwareFixture(image)
        self.alternate_mode = alternate_mode
        self.allocation_count = 0
        self.published_events: list[dict[str, Any]] = []
        self.rmssd_input_snapshots: list[list[int]] = []
        self.rmssd_output_bits: list[int] = []
        self.states_before_reset: list[bytes] = []
        self.machine.uc.mem_write(PRODUCER_STATE, b"\x00" * 0xD0)
        self.machine.uc.mem_write(PRODUCER_CONTROL, b"\x00" * 0x20)
        self.machine.uc.hook_add(UC_HOOK_CODE, self._hook)

    @staticmethod
    def _return(uc: Any, value: int) -> None:
        uc.reg_write(UC_ARM_REG_R0, value)
        uc.reg_write(UC_ARM_REG_PC, uc.reg_read(UC_ARM_REG_LR))

    def _hook(self, uc: Any, address: int, size: int, user_data: Any) -> None:
        del size, user_data
        if address == ALLOCATE:
            destination = VALIDITY if self.allocation_count % 2 == 0 else DIFFERENCES
            self.allocation_count += 1
            self._return(uc, destination)
        elif address == FREE:
            self._return(uc, 0)
        elif address == MODE:
            self._return(uc, int(self.alternate_mode))
        elif address == ELIGIBILITY:
            self._return(uc, 1)
        elif address == TIMESTAMP:
            self._return(uc, 0x12345678)
        elif address == RMSSD:
            pointer = uc.reg_read(UC_ARM_REG_R0)
            count = uc.reg_read(UC_ARM_REG_R1)
            raw = bytes(uc.mem_read(pointer, count * 2))
            self.rmssd_input_snapshots.append(list(struct.unpack("<" + "H" * count, raw)))
        elif address == RMSSD_RETURN_SITE:
            self.rmssd_output_bits.append(uc.reg_read(UC_ARM_REG_S0))
        elif address == PUBLISH_EVENT:
            event_id = uc.reg_read(UC_ARM_REG_R0)
            pointer = uc.reg_read(UC_ARM_REG_R1)
            length = uc.reg_read(UC_ARM_REG_R2)
            self.published_events.append({
                "event_id": event_id,
                "payload_hex": bytes(uc.mem_read(pointer, length)).hex(),
                "payload_length": length,
            })
            self._return(uc, 0)
        elif address == RESET_PRODUCER:
            self.states_before_reset.append(bytes(uc.mem_read(PRODUCER_STATE, 0xD0)))
            uc.mem_write(PRODUCER_STATE, b"\x00" * 0xD0)
            self._return(uc, 0)
        elif address == LOG_FLAGS:
            self._return(uc, 0)

    def callback(self, values: list[int]) -> dict[str, Any]:
        if len(values) > 4 or any(not 0 <= value <= 0xFFFF for value in values):
            raise ValueError("a producer callback accepts at most four UInt16 values")
        padded = values + [0] * (4 - len(values))
        self.machine.uc.mem_write(
            PRODUCER_INPUT,
            struct.pack("<4HBB", *padded, 0, len(values)),
        )
        self.machine.call(PRODUCER, 0, PRODUCER_INPUT)
        state = bytes(self.machine.uc.mem_read(PRODUCER_STATE, 0xD0))
        return {
            "values": values,
            "write_index": struct.unpack("<H", state[0xC8:0xCA])[0],
            "buffered_count": struct.unpack("<H", state[0xCA:0xCC])[0],
            "nonzero_count": struct.unpack("<H", state[0xCC:0xCE])[0],
            "callback_count": struct.unpack("<H", state[0xCE:0xD0])[0],
            "published_event_count": len(self.published_events),
            "rmssd_call_count": len(self.rmssd_output_bits),
        }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    image = args.image.read_bytes()

    cases: dict[str, dict[str, Any]] = {}
    fixtures = (
        ("null", False, []),
        ("one_interval", False, [800]),
        ("constant", False, [800, 800, 800, 800]),
        ("simple", False, [800, 810, 790, 820]),
        ("positive_150_boundary", False, [800, 950, 800]),
        ("positive_151_rejects_neighbors", False, [800, 951, 800]),
        ("negative_150_boundary", False, [950, 800, 950]),
        ("negative_151_rejects_neighbors", False, [951, 800, 951]),
        ("current_default_maximum", False, [1_000, 1_100, 1_000]),
        ("current_above_default_maximum", False, [1_000, 1_101, 1_000]),
        ("first_above_maximum_quirk", False, [1_101, 1_100, 1_099]),
        ("alternate_1500_maximum", True, [1_400, 1_500, 1_400]),
        ("alternate_above_maximum", True, [1_400, 1_501, 1_400]),
        ("mixed_invalid_islands", False, [800, 810, 1_100, 1_090, 800, 820, 830]),
    )
    for name, alternate, intervals in fixtures:
        cases[name] = RMSSDFixture(image, alternate_mode=alternate).calculate(intervals)

    expected = {
        "null": "0xbf800000",
        "one_interval": "0xbf800000",
        "constant": "0x00000000",
        "simple": "0x41acd1db",
        "positive_150_boundary": "0x43160000",
        "positive_151_rejects_neighbors": "0xbf800000",
        "negative_150_boundary": "0x43160000",
        "negative_151_rejects_neighbors": "0xbf800000",
        "current_default_maximum": "0x42c80000",
        "current_above_default_maximum": "0xbf800000",
        "first_above_maximum_quirk": "0x3f800000",
        "alternate_1500_maximum": "0x42c80000",
        "alternate_above_maximum": "0xbf800000",
        "mixed_invalid_islands": "0x41200000",
    }
    observed = {name: case["output"]["bits"] for name, case in cases.items()}
    assert observed == expected, (observed, expected)

    publication_cases = {
        name: HRVPublicationFixture(
            image,
            rmssd_bits=bits,
            eligibility=eligibility,
        ).run()
        for name, bits, eligibility in (
            ("negative_one", 0xBF800000, True),
            ("negative_zero", 0x80000000, True),
            ("positive_zero", 0x00000000, True),
            ("smallest_positive_subnormal", 0x00000001, True),
            ("fraction_below_one", 0x3F666666, True),
            ("fraction_above_one", 0x3FF33333, True),
            ("uint16_max_fraction", 0x477FFFE6, True),
            ("uint16_wrap", 0x47800000, True),
            ("largest_in_range_uint32_float", 0x4F7FFFFF, True),
            ("uint32_overflow", 0x4F800000, True),
            ("positive_infinity", 0x7F800000, True),
            ("positive_nan", 0x7FC00000, True),
            ("negative_nan", 0xFFC00000, True),
            ("eligibility_rejected", 0x42C80000, False),
        )
    }
    expected_publication = {
        "negative_one": (None, None),
        "negative_zero": (None, None),
        "positive_zero": (None, None),
        "smallest_positive_subnormal": (0, "0000000078563412"),
        "fraction_below_one": (0, "0000000078563412"),
        "fraction_above_one": (1, "0100000078563412"),
        "uint16_max_fraction": (65_535, "ffff000078563412"),
        "uint16_wrap": (65_536, "0000000078563412"),
        "largest_in_range_uint32_float": (4_294_967_040, "00ff000078563412"),
        "uint32_overflow": (0xFFFFFFFF, "ffff000078563412"),
        "positive_infinity": (0xFFFFFFFF, "ffff000078563412"),
        "positive_nan": (None, None),
        "negative_nan": (None, None),
        "eligibility_rejected": (None, None),
    }
    for name, (converted, payload) in expected_publication.items():
        case = publication_cases[name]
        assert case["converted_uint32"] == converted, (name, case, converted)
        observed_payload = case["published_event"]
        assert (None if observed_payload is None else observed_payload["payload_hex"]) == payload
        if observed_payload is not None:
            assert observed_payload["event_id"] == 7
            assert observed_payload["payload_length"] == 8

    warmup = HRVProducerFixture(image)
    warmup_state = warmup.callback([800, 810, 820, 830])
    assert warmup_state == {
        "values": [800, 810, 820, 830],
        "write_index": 0,
        "buffered_count": 0,
        "nonzero_count": 0,
        "callback_count": 1,
        "published_event_count": 0,
        "rmssd_call_count": 0,
    }

    below_gate = HRVProducerFixture(image)
    below_gate_updates = []
    for callback_index in range(60):
        if callback_index < 9:
            values = [800, 800, 800, 800]
        elif callback_index < 26:
            values = [800, 800, 800, 800]
        elif callback_index == 26:
            values = [800]
        else:
            values = []
        below_gate_updates.append(below_gate.callback(values))
    assert below_gate_updates[-1]["callback_count"] == 60
    assert below_gate_updates[-1]["buffered_count"] == 69
    assert below_gate_updates[-1]["nonzero_count"] == 69
    assert not below_gate.rmssd_output_bits
    assert not below_gate.published_events

    constant = HRVProducerFixture(image)
    constant_updates = [constant.callback([800, 800, 800, 800]) for _ in range(60)]
    assert constant.rmssd_output_bits == [0]
    assert not constant.published_events
    assert len(constant.states_before_reset) == 1
    assert constant_updates[-1]["callback_count"] == 0

    wrapped = HRVProducerFixture(image)
    wrapped_updates = []
    values = [800 + index % 200 for index in range(204)]
    for callback_index in range(9):
        wrapped_updates.append(wrapped.callback([900, 900, 900, 900]))
    for offset in range(0, len(values), 4):
        wrapped_updates.append(wrapped.callback(values[offset:offset + 4]))
    assert len(wrapped_updates) == 60
    assert len(wrapped.rmssd_input_snapshots) == 1
    physical_buffer = wrapped.rmssd_input_snapshots[0]
    assert physical_buffer[:4] == [800, 801, 802, 803]
    assert physical_buffer[4:] == list(range(904, 1000))
    assert wrapped.rmssd_output_bits == [0x41233141], [
        f"0x{bits:08x}" for bits in wrapped.rmssd_output_bits
    ]
    assert wrapped.published_events == [{
        "event_id": 7,
        "payload_hex": "0a00000078563412",
        "payload_length": 8,
    }]
    pre_reset = wrapped.states_before_reset[0]
    assert struct.unpack("<4H", pre_reset[0:8]) == (800, 801, 802, 803)
    assert struct.unpack("<4H", pre_reset[8:16]) == (904, 905, 906, 907)
    assert struct.unpack("<4H", pre_reset[0xC8:0xD0]) == (4, 100, 100, 60)
    assert wrapped_updates[-1]["callback_count"] == 0

    producer_cases = {
        "warmup_ignored": warmup_state,
        "sixty_callbacks_but_69_nonzero": below_gate_updates[-1],
        "constant_zero_result_resets": {
            "final_state": constant_updates[-1],
            "rmssd_output_bits": [f"0x{bits:08x}" for bits in constant.rmssd_output_bits],
            "published_events": constant.published_events,
        },
        "wrapped_physical_buffer": {
            "final_state": wrapped_updates[-1],
            "physical_buffer": physical_buffer,
            "rmssd_output_bits": [f"0x{bits:08x}" for bits in wrapped.rmssd_output_bits],
            "published_events": wrapped.published_events,
            "pre_reset_counters": list(struct.unpack("<4H", pre_reset[0xC8:0xD0])),
        },
    }

    print(json.dumps({
        "image_sha256": IMAGE_SHA256,
        "function": f"0x{RMSSD:08x}",
        "cases": cases,
        "publication_conversion_cases": publication_cases,
        "producer_state_cases": producer_cases,
        "safety": {
            "physical_device_access": False,
            "ble_access": False,
            "sensor_access": False,
            "firmware_execution_outside_private_emulation": False,
            "flash_writes": False,
            "health_store_access": False,
        },
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
