#!/usr/bin/env python3
"""Pin the Ghidra-omitted R1 NFC charge-task event policy."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE
from summarize_r1_gomore_call_graph import direct_thumb_branches_to


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "research/decompilation/rebuild/rebuilt-application.bin"
EXPECTED_IMAGE_SHA256 = "0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a"

EXECUTABLE_START = 0x000461CC
EXECUTABLE_END = 0x00046462
ENVELOPE_END = 0x00046650

R1_NFC_CHARGE_TASK_POLICY_FUNCTIONS: tuple[dict[str, Any], ...] = ({
    "entry": EXECUTABLE_START,
    "end_exclusive": ENVELOPE_END,
    "size": ENVELOPE_END - EXECUTABLE_START,
    "symbol": "r1_nfc_charge_task_plan_build",
    "sha256": "ed5a9b82902f050e4940ea199d8de22031802f7d7abc4cd3041e98a6590f19fc",
    "callers": ((0x00092556, "BL"),),
    "inventory": "manual_provenance_supplement",
    "provider_family": "r1_product_specific",
    "source_disposition": "clean_room_behavior_only",
},)

EXPECTED_STRINGS = {
    0x00046470: b"[RING]NFC_CHARGE_EVENT_STDCMD_IRQ_HANDLER",
    0x000464C0: b"[RING]NFC_CHARGE_EVENT_NOT_CHARGING",
    0x00046504: b"[RING]retry %d success",
    0x00046534: b"charge end: temp id invalid (retry=%d, T1=0x%02x T2=0x%02x)",
    0x00046570: b"[RING]charge end: temp id invalid 3 times, enable wdg and reset",
    0x000465EC: b"[RING]NFC_CHARGE_EVENT_CHARGING_BATTERY_UPDATA = %d",
}


def _bytes(image: bytes, start: int, end: int) -> bytes:
    return image[start - DEFAULT_BASE:end - DEFAULT_BASE]


def _read_c_string(image: bytes, address: int) -> bytes:
    start = address - DEFAULT_BASE
    return image[start:image.index(b"\0", start)]


def _local_calls(image: bytes, target: int) -> tuple[tuple[int, str], ...]:
    return tuple(
        item for item in direct_thumb_branches_to(image, DEFAULT_BASE, target)
        if EXECUTABLE_START <= item[0] < EXECUTABLE_END
    )


def summarize(image_path: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != EXPECTED_IMAGE_SHA256:
        raise ValueError(f"unexpected recovered application image: {digest}")

    function = R1_NFC_CHARGE_TASK_POLICY_FUNCTIONS[0]
    envelope = _bytes(image, EXECUTABLE_START, ENVELOPE_END)
    executable = _bytes(image, EXECUTABLE_START, EXECUTABLE_END)
    callers = tuple(direct_thumb_branches_to(
        image, DEFAULT_BASE, EXECUTABLE_START))
    strings = {
        address: _read_c_string(image, address) for address in EXPECTED_STRINGS
    }
    if len(envelope) != int(function["size"]) or \
            hashlib.sha256(envelope).hexdigest() != function["sha256"] or \
            len(executable) != 662 or \
            hashlib.sha256(executable).hexdigest() != \
            "632f49d7a293f0826bc7d52e62ec21d06b1e35054424e80b5a79d054ff643a6f" or \
            callers != function["callers"] or strings != EXPECTED_STRINGS or \
            _local_calls(image, 0x0008D8FC) != (
                (0x00046236, "BL"), (0x000462A8, "BL")) or \
            _local_calls(image, 0x00033AE4) != (
                (0x0004626E, "BL"), (0x000462DA, "BL")) or \
            _local_calls(image, 0x000510D8) != ((0x000462FC, "BL"),) or \
            _local_calls(image, 0x0007D154) != (
                (0x0004639A, "BL"), (0x0004642A, "BL"),
                (0x00046458, "BL")) or \
            _local_calls(image, 0x00031FCC) != (
                (0x00046424, "BL"), (0x0004643A, "BL")) or \
            _local_calls(image, 0x00096AD0) != ((0x000463DE, "BL"),):
        raise ValueError("R1 NFC charge-task policy changed")

    return {
        "analysis": "R1 NFC charge-task event policy",
        "image": str(image_path),
        "image_sha256": digest,
        "function_count": 1,
        "function_bytes": len(envelope),
        "executable_bytes": len(executable),
        "ghidra_function_count": 0,
        "manual_supplement_count": 1,
        "function": {
            **function,
            "entry": f"0x{EXECUTABLE_START:08x}",
            "end_exclusive": f"0x{ENVELOPE_END:08x}",
            "callers": [
                {"callsite": f"0x{address:08x}", "kind": kind}
                for address, kind in callers
            ],
        },
        "executable": {
            "start": f"0x{EXECUTABLE_START:08x}",
            "end_exclusive": f"0x{EXECUTABLE_END:08x}",
            "bytes": len(executable),
            "sha256": hashlib.sha256(executable).hexdigest(),
        },
        "event_masks": {
            "charged_notification": 0x00000001,
            "standard_command_irq": 0x00000002,
            "charged_notification_clear": 0x00000004,
            "pmic_charge_event": 0x00000008,
            "not_charging": 0x00000010,
            "battery_update": 0x00000020,
            "charging_battery_update": 0x00000040,
            "message_pending": 0x00400000,
            "terminate": 0x00800000,
        },
        "fixed_policy": {
            "message_bytes": 44,
            "st25_dynamic_register": 0x100B,
            "standard_command_register_value": 1,
            "not_charging_register_value": 0,
            "standard_command_delay_ticks": 0x800,
            "not_charging_delay_ticks": 0x1000,
            "temperature_id_expected": (0x50, 0x50),
            "temperature_id_attempts": 3,
            "temperature_retry_delay_ticks": 100,
            "zero_battery_update_count": 8,
            "zero_battery_update_delay_ticks": 10,
            "pmic_charge_event_value": 0x5A,
            "terminal_delay_ticks": 0xFFFFFFFF,
        },
        "boundary": {
            "provider_family": "r1_product_specific",
            "source_disposition": "clean_room_behavior_only",
            "st25_transport_reimplemented": False,
            "touch_provider_reimplemented": False,
            "battery_provider_reimplemented": False,
            "rtos_queue_timer_task_reimplemented": False,
            "logging_reimplemented": False,
            "live_event_dispatch_exposed": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE)
    print(json.dumps(summarize(parser.parse_args().image), indent=2,
                     sort_keys=True))


if __name__ == "__main__":
    main()
