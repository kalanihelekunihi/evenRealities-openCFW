#!/usr/bin/env python3
"""Verify the hidden R1 sport client contract in Even Android 2.2.0 AOT output.

This is a read-only evidence check. It does not connect to a ring or invoke the recovered
start/stop senders. The conclusions below are valid only when both the source libapp image and
the derived Blutter files match their pinned SHA-256 digests.
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
    "asm/even_connect/ring1/ble_ring1_service.dart":
        "e667083792db5caacb9a013fc95afd12447aaf1c9a19068f855c3c78084dc496",
    "asm/even_connect/ring1/models/ble_ring1_enum.dart":
        "8bfcdcfcf51eee062ea47c2b0c01481a5c327fc5f7eaa9412a485141ffdb74e2",
    "asm/even_connect/ring1/models/ble_ring1_model.dart":
        "d631a1177bd97af1c641aeaadc8d26eaab9e848ec543679da46f2e12687ff08f",
    "asm/even_connect/ring1/models/sport/ble_ring1_sport_run_data.dart":
        "33991e882e2b30ce02fbcfad51f25f7b5e628edf8d82b0a86bb242a4742127a2",
    "asm/even/pages/debug/ring1_debug/sport_mode_debug_controller.dart":
        "51c06e06580585944f4d129da75ce634b0227522ac7520708a431ab498a9a104",
    "asm/even/pages/debug/ring1_debug/sport_mode_debug_page.dart":
        "29d32f834d5eb588caaa03988fb4a982075db01ea979f96f0d2ecf81371df7be",
}

REQUIRED_MARKERS = {
    "asm/even_connect/ring1/ble_ring1_cmd_proto.dart": (
        "BleRing1CmdSportExt.sportRunStart",
        "BleRing1CmdSportExt.sportRunStop",
        "BleRing1StatusMethod",
        "r30 = 3000",
    ),
    "asm/even_connect/ring1/ble_ring1_service.dart": (
        "BleRing1SportRunData::fromBytes",
    ),
    "asm/even_connect/ring1/models/ble_ring1_enum.dart": (
        "BleRing1SubCmd::subCmd",
        "Obj!BleRing1SubCmd@20b1751",
        "Obj!BleRing1SubCmd@20b1731",
        "Obj!BleRing1SubCmd@20b1711",
    ),
    "asm/even_connect/ring1/models/ble_ring1_model.dart": (
        "r0 = 3",
        "BleRing1SubCmd::subCmd",
    ),
    "asm/even_connect/ring1/models/sport/ble_ring1_sport_run_data.dart": (
        "cmp             x1, #0xc",
        "add             x0, x6, #4",
        "add             x0, x6, #6",
        "add             x0, x6, #0xa",
    ),
    "asm/even/pages/debug/ring1_debug/sport_mode_debug_controller.dart": (
        "SportModeDebugController::startRunMode",
        "SportModeDebugController::stopRunMode",
        "BleRing1CmdSportExt.sportRunStart",
        "BleRing1CmdSportExt.sportRunStop",
    ),
    "asm/even/pages/debug/ring1_debug/sport_mode_debug_page.dart": (
        '"Heart Rate"',
        '" bpm"',
        '"Steps"',
        '"Calories"',
        '" kcal"',
    ),
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def default_reference_root() -> Path:
    return Path(__file__).resolve().parents[3] / "SybilSight-v2" / "firmware"


def summarize(aot_root: Path, libapp: Path) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    observed_libapp_sha256 = sha256(libapp) if libapp.is_file() else None
    if observed_libapp_sha256 != LIBAPP_SHA256:
        errors.append(
            f"libapp SHA-256 mismatch: expected {LIBAPP_SHA256}, "
            f"observed {observed_libapp_sha256}"
        )

    derived_files: dict[str, dict[str, Any]] = {}
    for relative, expected_digest in DERIVED_FILE_SHA256.items():
        path = aot_root / relative
        observed_digest = sha256(path) if path.is_file() else None
        missing_markers: list[str] = []
        if path.is_file():
            source = path.read_text(encoding="utf-8")
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

    report = {
        "analysis": "Even Android first-party R1 sport AOT contract",
        "controller_app_version": CONTROLLER_APP_VERSION,
        "libapp": str(libapp),
        "libapp_sha256": observed_libapp_sha256,
        "derived_aot_root": str(aot_root),
        "derived_files": derived_files,
        "hidden_ui": {
            "route": "pages/debug/ring1_debug/sport_mode_debug_page.dart",
            "controller": "SportModeDebugController",
            "start_sender": True,
            "stop_sender": True,
            "live_data_subscription": True,
        },
        "wire_contract": {
            "module": 0x03,
            "start": {"command": 0x07, "subcommand": 0x00, "method": "set"},
            "stop": {"command": 0x07, "subcommand": 0x01, "method": "set"},
            "sample": {"command": 0x08, "subcommand": 0x00, "method": "notify"},
            "start_stop_timeout_milliseconds": 3_000,
            "start_stop_payload_bytes": 0,
        },
        "sample_contract": {
            "minimum_payload_bytes": 12,
            "trailing_bytes_ignored_by_first_party_parser": True,
            "fields": [
                {
                    "name": "timestampSeconds",
                    "offset": 0,
                    "width": 4,
                    "encoding": "uint32_le",
                },
                {
                    "name": "heartRate",
                    "offset": 4,
                    "width": 2,
                    "encoding": "uint16_le",
                    "display_unit": "bpm",
                },
                {
                    "name": "steps",
                    "offset": 6,
                    "width": 4,
                    "encoding": "uint32_le",
                    "display_unit": "count",
                },
                {
                    "name": "calories",
                    "offset": 10,
                    "width": 2,
                    "encoding": "uint16_le",
                    "display_unit": "kcal",
                },
            ],
        },
        "safety": {
            "static_aot_read_only": True,
            "physical_device_access": False,
            "ble_access": False,
            "health_data_read": False,
            "start_or_stop_invoked": False,
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
