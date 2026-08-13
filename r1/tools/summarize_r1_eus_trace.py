#!/usr/bin/env python3
"""Produce a payload-redacted summary of R1 EUS traffic.

Input may be ATT JSONL emitted by ``extract_att_hci_pcap.py`` (or the legacy
SybilSight-v2/tools/hci/parse_btsnoop.py), or SybilSight's native lossless R1
capture. HCI input is independently reassembled and checksum-validated. Native
capture starts after transport validation, so its summary explicitly limits the
claims that can be made from it. Neither mode prints payload, device-address,
serial, decoded health, identity, or timestamp values.
"""

from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
import json
from pathlib import Path
from typing import Any


MAX_SEQUENCE = 0x10
MAX_FRAGMENT_PAYLOAD = 0xEF

COMMAND_NAMES = {
    (0x01, 0x00, 0x01): "system.deviceStatus",
    (0x01, 0x00, 0x02): "system.deviceInfo",
    (0x01, 0x00, 0x03): "system.wearStatus",
    (0x01, 0x00, 0x04): "system.userInfo",
    (0x01, 0x00, 0x05): "system.systemTime",
    (0x01, 0x00, 0x06): "system.touchStatus",
    (0x01, 0x00, 0x07): "system.touchSwitch",
    (0x01, 0x00, 0x08): "system.pairAuth",
    (0x01, 0x00, 0x09): "system.otaStart",
    (0x01, 0x00, 0x0A): "system.advStart",
    (0x01, 0x00, 0x0B): "system.getAlgoKeyStatus",
    (0x01, 0x00, 0x0C): "system.setAlgoKey",
    (0x01, 0x00, 0x0E): "system.healthSettingsStatus",
    (0x01, 0x00, 0x0F): "system.systemSettingsStatus",
    (0x01, 0x00, 0x10): "system.deviceSn",
    (0x01, 0x00, 0x11): "system.nvRecover",
    (0x01, 0x00, 0x12): "system.powerControl",
    (0x01, 0x00, 0x7E): "system.packetAck",
    (0x01, 0x00, 0x7F): "system.heartbeatPack",
    (0x01, 0x00, 0x80): "system.ringGlassesHeartbeatPack",
    (0x01, 0x00, 0x81): "system.ringGlassesShakeHands",
    (0x01, 0x00, 0x82): "system.removeRingNotify",
    (0x02, 0x01, 0x01): "heartRate.daily",
    (0x02, 0x01, 0x02): "heartRate.point",
    (0x02, 0x01, 0x03): "heartRate.measure",
    (0x02, 0x02, 0x01): "spo2.daily",
    (0x02, 0x02, 0x02): "spo2.point",
    (0x02, 0x02, 0x03): "spo2.measure",
    (0x02, 0x03, 0x01): "temperature.daily",
    (0x02, 0x03, 0x02): "temperature.point",
    (0x02, 0x03, 0x03): "temperature.measure",
    (0x02, 0x04, 0x01): "hrv.daily",
    (0x02, 0x04, 0x02): "hrv.point",
    (0x02, 0x04, 0x03): "hrv.measure",
    (0x02, 0x05, 0x01): "activity.daily",
    (0x02, 0x05, 0x02): "activity.allDay",
    (0x02, 0x06, 0x01): "sleep.daily",
    (0x02, 0x06, 0x02): "sleep.forceAwake",
    (0x02, 0x7F, 0x01): "healthSetting.reportEnable",
    (0x03, 0x07, 0x00): "sport.start",
    (0x03, 0x07, 0x01): "sport.stop",
    (0x03, 0x08, 0x00): "sport.data",
}


def crc32_r1(data: bytes) -> int:
    crc = 0
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFFFFFF) ^ (
                0x1EDC6F41 if crc & 0x80000000 else 0
            )
    return crc


def crc16_r1(data: bytes) -> int:
    crc = 0xFFFF
    for byte in data:
        crc = ((crc >> 8) | ((crc << 8) & 0xFFFF)) & 0xFFFF
        crc ^= byte
        crc ^= (crc & 0x00FF) >> 4
        crc ^= (crc << 12) & 0xFFFF
        crc ^= ((crc & 0x00FF) << 5) & 0xFFFF
    return crc & 0xFFFF


def crc16_nonreflected(data: bytes, initial: int, xor_out: int = 0) -> int:
    crc = initial
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) & 0xFFFF) ^ (0x1021 if crc & 0x8000 else 0)
    return crc ^ xor_out


def crc16_reflected(data: bytes, initial: int, xor_out: int = 0) -> int:
    crc = initial
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = (crc >> 1) ^ (0xA001 if crc & 1 else 0)
    return crc ^ xor_out


def matching_inner_crc_candidates(data: bytes) -> list[str]:
    observed = int.from_bytes(data[10:12], "little")
    payload = data[12:]
    zeroed = bytearray(data)
    zeroed[10:12] = b"\x00\x00"
    compact = bytes((
        data[0], data[1], data[2], data[3], data[5], data[6], data[7], data[8], 0,
    )) + payload
    preimages = {
        "app_constructor_compact": compact,
        "full_model_crc_zeroed": bytes(zeroed),
        "model_without_crc_field": data[:10] + payload,
        "header_before_crc_only": data[:10],
        "payload_only": payload,
    }
    algorithms = {
        "app_ccitt": crc16_r1,
        "ccitt_false": lambda value: crc16_nonreflected(value, 0xFFFF),
        "xmodem": lambda value: crc16_nonreflected(value, 0),
        "genibus": lambda value: crc16_nonreflected(value, 0xFFFF, 0xFFFF),
        "modbus": lambda value: crc16_reflected(value, 0xFFFF),
        "arc": lambda value: crc16_reflected(value, 0),
        "usb": lambda value: crc16_reflected(value, 0xFFFF, 0xFFFF),
    }
    matches = []
    for algorithm_name, algorithm in algorithms.items():
        for preimage_name, preimage in preimages.items():
            if algorithm(preimage) == observed:
                matches.append(f"{algorithm_name}/{preimage_name}")
    return matches


def classify_inner_crc(candidates: list[str]) -> str:
    if "app_ccitt/app_constructor_compact" in candidates:
        return "application_compact_ccitt"
    if "modbus/full_model_crc_zeroed" in candidates:
        return "firmware_full_model_modbus"
    return "unknown"


def parse_model(data: bytes) -> dict[str, Any] | None:
    if len(data) < 12 or data[0] != 100 or data[2] != 100:
        return None
    declared_length = int.from_bytes(data[8:10], "little")
    if declared_length != len(data):
        return None
    module, command, subcommand = data[1], data[6], data[7]
    if module not in (0x01, 0x02, 0x03, 0x7F):
        return None
    inner_crc_candidates = matching_inner_crc_candidates(data)
    return {
        "module": module,
        "command": command,
        "subcommand": subcommand,
        "name": COMMAND_NAMES.get(
            (module, command, subcommand),
            f"unknown.{module:02x}.{command:02x}.{subcommand:02x}",
        ),
        "serial_id": int.from_bytes(data[3:5], "little"),
        "status": data[5],
        "acknowledgement": bool(data[5] & 0x01),
        "succeeded": ((data[5] >> 2) & 0x03) == 0,
        "payload_length": len(data) - 12,
        "inner_crc_scheme": classify_inner_crc(inner_crc_candidates),
        "inner_crc_candidates": inner_crc_candidates,
    }


def summarize_hci(path: Path) -> dict[str, Any]:
    fragment_state: dict[tuple[str, int], dict[str, Any]] = {}
    models: list[dict[str, Any]] = []
    lane_counts: Counter[tuple[str, int]] = Counter()
    malformed_json = 0
    sequence_failures = 0
    checksum_failures = 0

    with path.open("r", encoding="utf-8") as source:
        for line in source:
            try:
                event = json.loads(line)
                value = bytes.fromhex(event.get("hex", ""))
                direction = str(event.get("dir", "unknown"))
                handle = int(event.get("handle", -1))
            except (ValueError, TypeError, json.JSONDecodeError):
                malformed_json += 1
                continue
            if len(value) < 6:
                continue
            sequence = value[0]
            fragment = value[5:]
            if sequence > MAX_SEQUENCE or len(fragment) > MAX_FRAGMENT_PAYLOAD:
                continue
            checksum = int.from_bytes(value[1:5], "little")
            key = (direction, handle)

            if sequence:
                current = fragment_state.get(key)
                if current is None:
                    if not fragment or fragment[0] != 100:
                        continue
                    fragment_state[key] = {
                        "checksum": checksum,
                        "expected": sequence - 1,
                        "chunks": [fragment],
                    }
                elif current["checksum"] == checksum and current["expected"] == sequence:
                    current["chunks"].append(fragment)
                    current["expected"] = sequence - 1
                else:
                    sequence_failures += 1
                    fragment_state.pop(key, None)
                continue

            current = fragment_state.pop(key, None)
            if current is not None:
                if current["checksum"] != checksum or current["expected"] != 0:
                    sequence_failures += 1
                    continue
                logical = b"".join(current["chunks"] + [fragment])
            else:
                logical = fragment
            model = parse_model(logical)
            if model is None:
                continue
            if crc32_r1(logical) != checksum:
                checksum_failures += 1
                continue
            model["direction"] = direction
            model["handle"] = handle
            models.append(model)
            lane_counts[key] += 1

    grouped: dict[tuple[int, int, int, str], dict[str, Any]] = {}
    for model in models:
        key = (
            model["module"], model["command"], model["subcommand"], model["direction"]
        )
        entry = grouped.setdefault(
            key,
            {
                "name": model["name"],
                "direction": model["direction"],
                "module": model["module"],
                "command": model["command"],
                "subcommand": model["subcommand"],
                "models": 0,
                "acknowledgements": 0,
                "successful": 0,
                "payload_lengths": set(),
                "inner_crc_candidates": Counter(),
            },
        )
        entry["models"] += 1
        entry["acknowledgements"] += int(model["acknowledgement"])
        entry["successful"] += int(model["succeeded"])
        entry["payload_lengths"].add(model["payload_length"])
        if model["inner_crc_candidates"]:
            entry["inner_crc_candidates"].update(model["inner_crc_candidates"])
        else:
            entry["inner_crc_candidates"].update(["none_of_tested_preimages"])

    commands = []
    for entry in grouped.values():
        entry["payload_lengths"] = sorted(entry["payload_lengths"])
        entry["inner_crc_candidates"] = dict(sorted(entry["inner_crc_candidates"].items()))
        commands.append(entry)
    commands.sort(key=lambda item: (item["name"], item["direction"]))

    checksum_schemes: dict[str, Counter[str]] = {}
    for model in models:
        checksum_schemes.setdefault(model["direction"], Counter()).update(
            [model["inner_crc_scheme"]]
        )

    return {
        "source": str(path),
        "source_format": "att_hci_jsonl",
        "privacy": "payloads and identity values omitted",
        "evidence_scope": (
            "ATT values independently reassembled; outer EUS CRC32 and inner model checksum "
            "validated from captured bytes"
        ),
        "parsed_models": len(models),
        "checksum_failures": checksum_failures,
        "sequence_failures": sequence_failures,
        "malformed_json_lines": malformed_json,
        "incomplete_fragment_sequences": len(fragment_state),
        "lanes": [
            {"direction": direction, "handle": handle, "models": count}
            for (direction, handle), count in sorted(lane_counts.items())
        ],
        "inner_crc_schemes": {
            direction: dict(sorted(counts.items()))
            for direction, counts in sorted(checksum_schemes.items())
        },
        "commands": commands,
    }


SAFE_NATIVE_SOURCES = {
    "direct",
    "direct-trigger",
    "direct_notification",
    "direct_response",
}


def _native_payload_length(value: Any) -> int | None:
    if not isinstance(value, str):
        return None
    try:
        return len(base64.b64decode(value, validate=True))
    except (ValueError, TypeError):
        return None


def summarize_native_events(
    events: list[Any], *, source: str, malformed_json_lines: int = 0
) -> dict[str, Any]:
    kind_counts: Counter[str] = Counter()
    telemetry: list[dict[str, Any]] = []
    invalid_telemetry = 0
    command_name_mismatches = 0

    for event in events:
        if not isinstance(event, dict):
            invalid_telemetry += 1
            continue
        kind = event.get("kind")
        if not isinstance(kind, str):
            kind = "unknown"
        kind_counts[kind] += 1
        if kind != "telemetry":
            continue
        value = event.get("value")
        if not isinstance(value, dict):
            invalid_telemetry += 1
            continue
        try:
            module = int(value["module"])
            command = int(value["command"])
            subcommand = int(value["subcommand"])
        except (KeyError, TypeError, ValueError):
            invalid_telemetry += 1
            continue
        if not all(0 <= field <= 0xFF for field in (module, command, subcommand)):
            invalid_telemetry += 1
            continue
        name = COMMAND_NAMES.get(
            (module, command, subcommand),
            f"unknown.{module:02x}.{command:02x}.{subcommand:02x}",
        )
        if value.get("commandName") != name:
            command_name_mismatches += 1
        raw_source = value.get("source")
        lane = raw_source if raw_source in SAFE_NATIVE_SOURCES else "other"
        payload_length = _native_payload_length(value.get("rawPayload"))
        if payload_length is None:
            invalid_telemetry += 1
        telemetry.append({
            "module": module,
            "command": command,
            "subcommand": subcommand,
            "name": name,
            "source": lane,
            "succeeded": value.get("succeeded") is True,
            "acknowledgement": value.get("acknowledgement") is True,
            "wire_status": value.get("wireStatusRaw")
                if isinstance(value.get("wireStatusRaw"), int) else None,
            "payload_length": payload_length,
            "inner_crc_scheme": value.get("innerChecksumScheme")
                if isinstance(value.get("innerChecksumScheme"), str) else "unclassified",
        })

    grouped: dict[tuple[int, int, int, str], dict[str, Any]] = {}
    for model in telemetry:
        key = (
            model["module"], model["command"], model["subcommand"], model["source"]
        )
        entry = grouped.setdefault(key, {
            "name": model["name"],
            "source": model["source"],
            "module": model["module"],
            "command": model["command"],
            "subcommand": model["subcommand"],
            "models": 0,
            "acknowledgements": 0,
            "successful": 0,
            "wire_statuses": Counter(),
            "payload_lengths": set(),
            "inner_crc_schemes": Counter(),
        })
        entry["models"] += 1
        entry["acknowledgements"] += int(model["acknowledgement"])
        entry["successful"] += int(model["succeeded"])
        if model["wire_status"] is not None:
            entry["wire_statuses"].update([str(model["wire_status"])])
        if model["payload_length"] is not None:
            entry["payload_lengths"].add(model["payload_length"])
        entry["inner_crc_schemes"].update([model["inner_crc_scheme"]])

    commands = []
    for entry in grouped.values():
        entry["wire_statuses"] = dict(sorted(entry["wire_statuses"].items()))
        entry["payload_lengths"] = sorted(entry["payload_lengths"])
        entry["inner_crc_schemes"] = dict(sorted(entry["inner_crc_schemes"].items()))
        commands.append(entry)
    commands.sort(key=lambda item: (item["name"], item["source"]))

    direct_response_sequence = [
        model["name"] for model in telemetry if model["source"] == "direct_response"
    ]
    startup_prefix = [
        "system.pairAuth",
        "system.systemTime",
        "system.deviceStatus",
    ]
    startup_prefix_matches = sum(
        direct_response_sequence[index:index + len(startup_prefix)] == startup_prefix
        for index in range(len(direct_response_sequence) - len(startup_prefix) + 1)
    )

    checksum_schemes = Counter(
        model["inner_crc_scheme"] for model in telemetry
    )
    lane_counts = Counter(model["source"] for model in telemetry)
    return {
        "source": source,
        "source_format": "sybilsight_r1_lossless_capture_v1",
        "privacy": (
            "payloads, decoded health and identity values, serials, addresses, and timestamps omitted"
        ),
        "evidence_scope": (
            "application telemetry emitted after EUS transport validation; independently proves "
            "decoded command flow and recorded inner-checksum classification, but not ATT handles, "
            "fragmentation, link encryption, or outer CRC32 from raw captured bytes"
        ),
        "events": len(events),
        "event_kinds": dict(sorted(kind_counts.items())),
        "parsed_models": len(telemetry),
        "malformed_json_lines": malformed_json_lines,
        "invalid_telemetry_fields": invalid_telemetry,
        "command_name_mismatches": command_name_mismatches,
        "lanes": dict(sorted(lane_counts.items())),
        "recorded_inner_crc_schemes": dict(sorted(checksum_schemes.items())),
        "startup_contract": {
            "expected_direct_response_prefix": startup_prefix,
            "matching_cycles": startup_prefix_matches,
            "first_direct_response_commands": direct_response_sequence[:12],
        },
        "commands": commands,
    }


def summarize_native(path: Path) -> dict[str, Any]:
    events: list[Any] = []
    malformed_json = 0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                malformed_json += 1
    return summarize_native_events(
        events, source=str(path), malformed_json_lines=malformed_json
    )


def summarize(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            try:
                first = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(first, dict) and first.get("kind") in {"telemetry", "snapshot"}:
                return summarize_native(path)
            return summarize_hci(path)
    return summarize_hci(path)


def run_self_test() -> None:
    model = {
        "module": 1,
        "command": 0,
        "subcommand": 8,
        "commandName": "system.pairAuth",
        "source": "direct_response",
        "succeeded": True,
        "acknowledgement": True,
        "wireStatusRaw": 3,
        "rawPayload": base64.b64encode(b"\x01").decode("ascii"),
        "innerChecksumScheme": "firmware_full_model_modbus",
    }
    result = summarize_native_events(
        [{"kind": "telemetry", "value": model}, {"kind": "snapshot", "value": {}}],
        source="self-test",
    )
    assert result["parsed_models"] == 1
    assert result["commands"][0]["payload_lengths"] == [1]
    assert result["commands"][0]["name"] == "system.pairAuth"
    assert "rawPayload" not in json.dumps(result)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_jsonl", type=Path, nargs="?")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        run_self_test()
        return 0
    if args.events_jsonl is None:
        parser.error("events_jsonl is required unless --self-test is used")
    print(json.dumps(summarize(args.events_jsonl), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
