#!/usr/bin/env python3
"""Pin the production R1 power-control and persisted ship-mode record route.

This audit is deliberately static. It reads a caller-supplied production image and decompiled
first-party AOT text; it never opens BLE, sends a power command, posts a thread flag, writes the
device-info record, resets a ring, enters ship mode, or resumes system settings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from summarize_r1_adc_registry import DEFAULT_BASE, mapped_offset
from summarize_r1_gomore_call_graph import direct_thumb_branches_to
from summarize_r1_gomore_input_abi import IMAGE_SHA256


DEFAULT_AOT_ROOT = (
    Path(__file__).resolve().parents[3]
    / "SybilSight-v2"
    / "firmware"
    / "blutter_output_2.2.0"
    / "asm"
)

RANGES = [
    (
        0x000843C8,
        0x0008449A,
        "41317679cc3d2f429d5ef7314b664018550d035b920ae3880641eacc3c26eaca",
        "system power-control handler",
    ),
    (
        0x00082BD4,
        0x00082BE6,
        "1f0181948d602c0210ecae853b284d17e6b01d0e14a901c8b6548d03d81c9dac",
        "payload-presence helper",
    ),
    (
        0x0007EFD6,
        0x0007EFEA,
        "f5f20cd326030969b639bda3b9561b04fbc68e6ac180ed986ede7131b6944464",
        "persistent reset-tag replacement helper",
    ),
    (
        0x0007EF06,
        0x0007EF4C,
        "75f3a2038e40662326683c09ae2a344c2cf935360fa1425348f475b9315a49e5",
        "persistent reset-tag clear helper",
    ),
    (
        0x0007EE30,
        0x0007EE76,
        "6704ba247e2313adaff20df009598e1182e338277b3e4e92a6c088c79b621635",
        "persistent reset-tag slot writer",
    ),
    (
        0x00073694,
        0x000736B4,
        "cecd7f3413612d182834754332fb5689c03123c4e0dc0ab39cc6260b0b3c3121",
        "device-info ship-mode record getter",
    ),
    (
        0x00073710,
        0x0007374C,
        "d6f1b90c70a386c34b5351e59786145c87aa2aaac91259bc733f58055c47320d",
        "device-info ship-mode record setter",
    ),
    (
        0x00091290,
        0x000912A4,
        "af1f05b702fdb875a7b1db7e7f80a19be8932f9dd17ddb790da9e0d69e555046",
        "battery-voltage accessor",
    ),
    (
        0x000912A8,
        0x00091366,
        "4335ae50170dfaba1027bc388a8262772006531884625128578da06fa68a5dda",
        "boot ship-mode record reporter",
    ),
    (
        0x0003D88C,
        0x0003D93C,
        "47da08214c49bac1655559c2f7f199b7ea4c0ef4a90e5cecf02ef719652478bf",
        "sustained-low-voltage shutdown producer",
    ),
    (
        0x0004F4D4,
        0x0004F50C,
        "2eb10962b78d9955ba18e7e248c54634961c3c0ed1c5a56b39559deca79076dc",
        "PMIC power-off shutdown producer",
    ),
    (
        0x0007D6F4,
        0x0007D77A,
        "69696dfb493efb820587ad41c2131e3629f11ace71bfa338ea28c79f522f2cfd",
        "RTOS thread-flag setter",
    ),
    (
        0x0009230C,
        0x0009238C,
        "65da7625dd83c8f74a802a46676632679fc978ef5268b4981207facb30d45a45",
        "system worker wait loop",
    ),
]

POWER_HANDLER = 0x000843C8
PAYLOAD_HELPER = 0x00082BD4
RESET_TAG_SETTER = 0x0007EFD6
SHIP_MODE_GETTER = 0x00073694
SHIP_MODE_SETTER = 0x00073710
BATTERY_VOLTAGE_GETTER = 0x00091290

REGISTRATION_ADDRESS = 0x0009A544
REGISTRATION_BYTES = bytes.fromhex("12000000c9430800")

EXPECTED_BRANCHES = {
    RESET_TAG_SETTER: [0x0003E9CE, 0x00084428],
    SHIP_MODE_GETTER: [0x00091306],
    SHIP_MODE_SETTER: [0x0003D912, 0x0004F4FA, 0x0008444E],
}

STRINGS = {
    0x0003D940: "[RING]battery voltage low %d(3350mv), low_power_cnt=%d",
    0x0004F50C: "at_pmic_power_off\r\n",
    0x00091370: "[RING]shipmode ts:%d, type:%d, voltage:%d",
    0x000C0278: (
        "[RING]CMD_SYSTEM_POWER_CONTROL: recovery, "
        "post EVENT_SYSTEM_RESUME_SETTING"
    ),
}


def flash_bytes(image: bytes, base: int, start: int, end: int) -> bytes:
    offset = mapped_offset(start, base, len(image))
    return image[offset : offset + end - start]


def checked_range(
    image: bytes,
    base: int,
    start: int,
    end: int,
    expected: str,
    label: str,
) -> dict[str, str]:
    actual = hashlib.sha256(flash_bytes(image, base, start, end)).hexdigest()
    if actual != expected:
        raise ValueError(f"unexpected {label} range: {actual}")
    return {
        "label": label,
        "start": f"0x{start:08x}",
        "end_exclusive": f"0x{end:08x}",
        "sha256": actual,
    }


def c_string(image: bytes, base: int, address: int) -> str:
    offset = mapped_offset(address, base, len(image))
    end = image.find(b"\0", offset)
    if end < 0:
        raise ValueError(f"unterminated string at 0x{address:08x}")
    return image[offset:end].decode("ascii")


def checked_marker(source: str, marker: str, label: str) -> dict[str, str]:
    if marker not in source:
        raise ValueError(f"missing {label}: {marker}")
    return {"label": label, "marker": marker}


def summarize(image_path: Path, base: int, aot_root: Path) -> dict[str, Any]:
    image = image_path.read_bytes()
    digest = hashlib.sha256(image).hexdigest()
    if digest != IMAGE_SHA256:
        raise ValueError(f"unexpected image SHA-256: {digest}")

    verified_ranges = [
        checked_range(image, base, start, end, sha256, label)
        for start, end, sha256, label in RANGES
    ]
    actual_registration = flash_bytes(
        image,
        base,
        REGISTRATION_ADDRESS,
        REGISTRATION_ADDRESS + len(REGISTRATION_BYTES),
    )
    if actual_registration != REGISTRATION_BYTES:
        raise ValueError(
            "unexpected power-control registration: "
            f"{actual_registration.hex()}"
        )
    if direct_thumb_branches_to(image, base, POWER_HANDLER):
        raise ValueError("table-dispatched power handler acquired a direct branch")

    branch_sets: dict[str, list[str]] = {}
    for target, expected in EXPECTED_BRANCHES.items():
        actual = [
            address
            for address, _ in direct_thumb_branches_to(image, base, target)
        ]
        if actual != expected:
            raise ValueError(
                f"unexpected complete branch set for 0x{target:08x}: {actual}"
            )
        branch_sets[f"0x{target:08x}"] = [
            f"0x{address:08x}" for address in actual
        ]

    payload_calls = [
        address
        for address, _ in direct_thumb_branches_to(image, base, PAYLOAD_HELPER)
        if POWER_HANDLER <= address < 0x0008449A
    ]
    if payload_calls != [0x000843D0]:
        raise ValueError(f"unexpected power-handler payload calls: {payload_calls}")

    voltage_calls = [
        address
        for address, _ in direct_thumb_branches_to(
            image, base, BATTERY_VOLTAGE_GETTER
        )
    ]
    required_voltage_calls = {0x0003D8FE, 0x0004F4E6, 0x0008443A}
    if not required_voltage_calls.issubset(voltage_calls):
        raise ValueError(
            f"missing ship-mode battery-voltage calls: {voltage_calls}"
        )

    string_evidence = []
    for address, expected in STRINGS.items():
        actual = c_string(image, base, address)
        if actual != expected:
            raise ValueError(
                f"unexpected string at 0x{address:08x}: {actual!r}"
            )
        string_evidence.append({
            "address": f"0x{address:08x}",
            "value": actual,
        })

    proto_path = aot_root / "even_connect/ring1/ble_ring1_cmd_proto.dart"
    controller_path = (
        aot_root
        / "even/pages/devices/mine/settings/advanced/"
        / "advanced_settings_controller.dart"
    )
    proto = proto_path.read_text(encoding="utf-8")
    controller = controller_path.read_text(encoding="utf-8")
    aot_markers = [
        checked_marker(
            proto,
            "_ powerControl(/* No info */) async {",
            "first-party powerControl routine",
        ),
        checked_marker(
            proto,
            "0x1574d94: r2 = 2",
            "tagged Smi one-element source-array length",
        ),
        checked_marker(
            proto,
            "0x1574dc0: r4 = 2",
            "tagged Smi one-byte Uint8List length",
        ),
        checked_marker(
            proto,
            "0x1574da0: r16 = 2",
            "tagged Smi command value one",
        ),
        checked_marker(
            proto,
            "0x1574e14: r0 = BleRing1CmdPublicExt.sendCmd()",
            "first-party command send",
        ),
        checked_marker(
            controller,
            "_ quickRestartDevice(/* No info */) async {",
            "advanced-settings quick restart action",
        ),
        checked_marker(
            controller,
            "0x1574d44: r0 = powerControl()",
            "R1 quick restart invokes powerControl",
        ),
    ]

    return {
        "analysis": "R1 production power-control and ship-mode route",
        "image": str(image_path),
        "image_sha256": digest,
        "load_base": f"0x{base:08x}",
        "verified_ranges": verified_ranges,
        "registration": {
            "address": f"0x{REGISTRATION_ADDRESS:08x}",
            "system_subcommand": "0x12",
            "handler_thumb": "0x000843c9",
            "raw_hex": actual_registration.hex(),
        },
        "complete_direct_branch_sets": branch_sets,
        "string_evidence": string_evidence,
        "first_party_aot_markers": aot_markers,
        "handler": {
            "header_bytes": 12,
            "payload_present_rule": "declared frame length != 12",
            "minimum_payload_length_checked": False,
            "significant_payload_bytes": 1,
            "accepted_command_values": [1, 2, 3],
            "invalid_status": 1,
            "accepted_status": 0,
            "response_precedes_delay_and_effect": True,
            "delay_raw": 100,
            "commands": {
                "1": {
                    "first_party_name": "quickRestartDevice",
                    "persistent_reset_tag": 1,
                    "system_thread_flag": "0x00000002",
                },
                "2": {
                    "ship_mode_type": 3,
                    "battery_voltage_bits": [2, 15],
                    "system_thread_flag": "0x00000001",
                },
                "3": {
                    "firmware_log_name": "EVENT_SYSTEM_RESUME_SETTING",
                    "system_thread_flag": "0x00000100",
                },
            },
        },
        "ship_mode_record": {
            "device_info_timestamp_offset": 36,
            "device_info_state_offset": 40,
            "type_bits": [0, 1],
            "battery_voltage_bits": [2, 15],
            "preserved_state_bits": [16, 31],
            "boot_use": "reported as shipmode timestamp, type and voltage",
            "observed_type_producers": {
                "0": "sustained battery voltage below 3350 mV",
                "2": "PMIC power-off callback",
                "3": "public power-control command 2",
            },
            "low_voltage_notification_count": 9,
            "low_voltage_shutdown_count": 10,
            "setter_calls_commit_wrapper": False,
        },
        "first_party": {
            "official_payload_hex": "01",
            "official_payload_bytes": 1,
            "only_observed_command": 1,
            "legacy_trailing_zero_consumed_but_not_required": True,
        },
        "safety": {
            "static_firmware_read_only": True,
            "ble_access": False,
            "thread_flag_publication": False,
            "persistent_record_write": False,
            "reset_or_shutdown": False,
            "live_sender_recommended": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    parser.add_argument("--base", type=lambda value: int(value, 0), default=DEFAULT_BASE)
    parser.add_argument("--aot-root", type=Path, default=DEFAULT_AOT_ROOT)
    args = parser.parse_args()
    print(json.dumps(
        summarize(args.image, args.base, args.aot_root),
        indent=2,
        sort_keys=True,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
