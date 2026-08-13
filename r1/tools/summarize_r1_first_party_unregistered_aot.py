#!/usr/bin/env python3
"""Audit first-party AOT use of R1 commands absent from ring firmware 2.2.6.0009.

This read-only analyzer distinguishes enum/catalog presence, receive-only parsing, and actual
first-party transmission. It never connects to a ring or invokes any recovered command.
Conclusions fail closed unless the source libapp and every derived Blutter input retain their
pinned SHA-256 digests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


CONTROLLER_APP_VERSION = "2.2.0"
LIBAPP_SHA256 = "451de716e2958c330683d7c6b6fda49fed3fe45ca0e952bbb331471e26cb98af"

DERIVED_FILE_SHA256 = {
    "asm/even_connect/ring1/ble_ring1_cmd_proto.dart":
        "5d8225ac1c10fe2be5102928681d5fa466313cbbee8bf116637123d39880c485",
    "asm/even_connect/ring1/models/ble_ring1_enum.dart":
        "8bfcdcfcf51eee062ea47c2b0c01481a5c327fc5f7eaa9412a485141ffdb74e2",
    "asm/even/pages/main_screen/tab_page/health/health_controller.dart":
        "5ba6e71727f7c5518ca9bafedcc4f32493b7268d286e45263f3876767cd8c667",
    "asm/even/pages/main_screen/tab_page/health/models/health_module_type.dart":
        "38e9bb64a6fbd2bfff9614599e755d532a15c1a8944c75b04f9e75be79f82b2f",
    "asm/even/pages/debug/ring1_debug/health_data_point_debug_controller.dart":
        "8b48aae2cf546921a851066fdb104c8fb3eeea58794a718cca4e3327de60b410",
    "asm/even/pages/debug/ring1_debug/health_data_point_debug_page.dart":
        "a51abaa89bd6349b93fc1786db658d4077cf82c8b7266ccb48d14dbd79e77b12",
}

REQUIRED_MARKERS = {
    "asm/even_connect/ring1/ble_ring1_cmd_proto.dart": (
        "BleRing1CmdHealthExt.getDailyData",
    ),
    "asm/even_connect/ring1/models/ble_ring1_enum.dart": (
        "Obj!BleRing1SubCmd@20b19f1",
        "Obj!BleRing1SubCmd@20b1851",
        "Obj!BleRing1SubCmd@20b1831",
        "Obj!BleRing1SubCmd@20b17b1",
        "Obj!BleRing1Cmd@20b1b91",
    ),
    "asm/even/pages/main_screen/tab_page/health/health_controller.dart": (
        "request heartRate history via getDailyData",
        "request HRV history via getDailyData",
        "request SpO2 history via getDailyData",
        "request sleep/skinTemp history via getDailyData",
        "request steps/calories (activity) history via getDailyData",
    ),
    "asm/even/pages/main_screen/tab_page/health/models/health_module_type.dart": (
        "get _ ring1Cmd",
        "Obj!BleRing1Cmd@20b1b91",
    ),
    "asm/even/pages/debug/ring1_debug/health_data_point_debug_controller.dart": (
        "HealthDataPointDebugController::onInit",
        "BleRing1HealthPoint::fromBytes",
        "Obj!BleRing1Cmd@20b1b91",
    ),
    "asm/even/pages/debug/ring1_debug/health_data_point_debug_page.dart": (
        '"Temperature"',
    ),
}

ENUM_OBJECT_MARKERS = {
    "touchStatus": "Obj!BleRing1SubCmd@20b19f1",
    "glassesHeartbeat": "Obj!BleRing1SubCmd@20b1851",
    "glassesHandshake": "Obj!BleRing1SubCmd@20b1831",
    "healthMeasure": "Obj!BleRing1SubCmd@20b17b1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_reference_root() -> Path:
    return Path(__file__).resolve().parents[3] / "SybilSight-v2" / "firmware"


def marker_paths(asm_root: Path, marker: str) -> list[str]:
    matches: list[str] = []
    for path in sorted(asm_root.rglob("*.dart")):
        source = path.read_text(encoding="utf-8", errors="replace")
        if marker in source:
            matches.append(str(path.relative_to(asm_root)))
    return matches


def summarize(aot_root: Path, libapp: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    observed_libapp_sha256 = sha256(libapp) if libapp.is_file() else None
    if observed_libapp_sha256 != LIBAPP_SHA256:
        errors.append(
            f"libapp SHA-256 mismatch: expected {LIBAPP_SHA256}, "
            f"observed {observed_libapp_sha256}"
        )

    derived_files: dict[str, dict[str, Any]] = {}
    sources: dict[str, str] = {}
    for relative, expected_digest in DERIVED_FILE_SHA256.items():
        path = aot_root / relative
        observed_digest = sha256(path) if path.is_file() else None
        source = path.read_text(encoding="utf-8") if path.is_file() else ""
        sources[relative] = source
        missing_markers = [
            marker for marker in REQUIRED_MARKERS[relative]
            if marker not in source
        ]
        if observed_digest != expected_digest:
            errors.append(
                f"{relative}: SHA-256 mismatch: expected {expected_digest}, "
                f"observed {observed_digest}"
            )
        if missing_markers:
            errors.append(f"{relative}: missing markers {missing_markers}")
        derived_files[relative] = {
            "sha256": observed_digest,
            "expected_sha256": expected_digest,
            "missing_markers": missing_markers,
        }

    asm_root = aot_root / "asm"
    reference_paths = {
        name: marker_paths(asm_root, marker)
        for name, marker in ENUM_OBJECT_MARKERS.items()
    }
    enum_path = "even_connect/ring1/models/ble_ring1_enum.dart"
    for name, paths in reference_paths.items():
        if paths != [enum_path]:
            errors.append(f"{name}: unexpected enum-object reference paths {paths}")

    health_controller = sources[
        "asm/even/pages/main_screen/tab_page/health/health_controller.dart"
    ]
    daily_call_count = health_controller.count(
        "BleRing1CmdHealthExt.getDailyData()"
    )
    if daily_call_count != 5:
        errors.append(
            f"unexpected getDailyData call-site count: {daily_call_count} != 5"
        )
    if "request temperature history via getDailyData" in health_controller:
        errors.append("standalone temperature daily request unexpectedly appeared")

    report = {
        "analysis": "Even Android first-party use of exact-firmware-unregistered R1 descriptors",
        "controller_app_version": CONTROLLER_APP_VERSION,
        "libapp": str(libapp),
        "libapp_sha256": observed_libapp_sha256,
        "derived_aot_root": str(aot_root),
        "derived_files": derived_files,
        "system_descriptor_use": {
            "touch_status": {
                "wire": {"module": 0x01, "command": 0x00, "subcommand": 0x06},
                "enum_present": True,
                "non_enum_aot_reference_found": False,
                "first_party_sender_found": False,
                "exact_ring_firmware_registered": False,
            },
            "glasses_heartbeat": {
                "wire": {"module": 0x01, "command": 0x00, "subcommand": 0x80},
                "enum_present": True,
                "non_enum_aot_reference_found": False,
                "first_party_sender_found": False,
                "exact_ring_firmware_registered": False,
            },
            "glasses_handshake": {
                "wire": {"module": 0x01, "command": 0x00, "subcommand": 0x81},
                "enum_present": True,
                "non_enum_aot_reference_found": False,
                "first_party_sender_found": False,
                "exact_ring_firmware_registered": False,
            },
        },
        "temperature_descriptor_use": {
            "wire_family": {"module": 0x02, "command": 0x03},
            "daily_subcommand": 0x01,
            "point_subcommand": 0x02,
            "measure_subcommand": 0x03,
            "enum_and_parser_present": True,
            "debug_page_is_receive_only": True,
            "debug_page_decodes_unsolicited_temperature_points": True,
            "generic_daily_sender_present": True,
            "normal_history_daily_call_count": daily_call_count,
            "normal_history_requested_families": [
                "heartRate", "heartRateVariability", "bloodOxygen",
                "sleepIncludingSkinTemperature", "activity",
            ],
            "standalone_temperature_daily_sender_call_found": False,
            "standalone_temperature_point_sender_call_found": False,
            "standalone_temperature_measure_sender_call_found": False,
            "sleep_route_marks_sleep_and_skin_temperature_received_together": True,
            "exact_ring_firmware_registered": {
                "daily": False,
                "point": False,
                "measure": False,
            },
        },
        "enum_object_reference_paths": reference_paths,
        "safety": {
            "static_aot_read_only": True,
            "physical_device_access": False,
            "ble_access": False,
            "health_data_read": False,
            "command_invoked": False,
            "live_sender_exposed": False,
        },
        "valid": not errors,
        "errors": errors,
    }
    return report, errors


def main() -> None:
    reference_root = default_reference_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--aot-root",
        type=Path,
        default=reference_root / "blutter_output_2.2.0",
    )
    parser.add_argument(
        "--libapp",
        type=Path,
        default=(
            reference_root
            / "even_android_installed/extracted_from_phone/2.2.0/"
            "split_config.arm64_v8a/lib/arm64-v8a/libapp.so"
        ),
    )
    arguments = parser.parse_args()
    report, errors = summarize(arguments.aot_root.resolve(), arguments.libapp.resolve())
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
