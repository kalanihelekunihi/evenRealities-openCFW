#!/usr/bin/env python3
"""Fail-closed audit of the pathless G2 eAT core/sensor command cluster."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-eat-core-sensor-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-eat-core-sensor-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-eat-core-sensor-provenance.tsv"
PINS = {
    FUNCTION_MAP: "47e2c64c8eb70808e81b637171c356d22660787f974f9e3b06716d10e7c4e182",
    CLOSURE: "76df83316b855d9a8a316a1b9049432bea4a128913ec70bac5caea26717376b1",
    PROVENANCE: "399e39122a1a4a64ef6eb7faa579c0779b5cf7e0b1a003aea83e9057ff816dd5",
}
PHYSICAL = (0x005A5720, 0x005A5984)
PHYSICAL_SHA256 = "e0eb932297c2b57ba92b7a89b65d4ed5ae22038efb8d6bbf1fecaf4f2ef797a8"
NONCODE = (
    (0x005A57B4, 0x005A57F0),
    (0x005A5822, 0x005A5830),
    (0x005A589A, 0x005A58A8),
    (0x005A595E, 0x005A5984),
)
NONCODE_SHA256 = "17f9964ab7af8332ecdec76ce35a1be4e12aa5f85ecaa4cfaf2b72d739efebdb"
BODY_SHA256 = "0d22c9e3a24002da78523b336961d3b84f9875be006380e65b28d73da99118c2"
BODY_CALL_SHA256 = "69e8a0ff61b5478588b7bfc6410adaa8793adb389ce22d6a7b558c52c723f60a"
STORED_POINTER_SHA256 = "85d7f12117a9bfc149f659d4438f1ca46b16d793a827c5a098c5cd2e6b307704"
COMMAND_RECORDS = (0x006C92E0, 0x006C93A0)
COMMAND_RECORDS_SHA256 = "e8d55ae6c7fd5e5cad86205eca9d6c1dfca9772ee29d415ad6151f209a7937d5"
COMMANDS = (
    (0, 0x0078CC14, 0x005A5721, 0, "AT^INFO", "atInfoHandler"),
    (0, 0x0078A3DC, 0x005A57A5, 0, "AT^RESET", "atResetHandler"),
    (0, 0x0078CC1C, 0x005A57F1, 0, "AT^PSN", "atPsnHandler"),
    (2, 0x00785170, 0x005A5831, 0, "AT^IMU_RAWDATA", "atImuRawDataHandler"),
    (0, 0x00785180, 0x005A5865, 0, "AT^IMU_EULER", "atImuEulerHandler"),
    (2, 0x0078A3F4, 0x005A58A9, 0, "AT^SCRN_X", "atScreenXHandler"),
    (2, 0x0078A400, 0x005A58B5, 0, "AT^SCRN_Y", "atScreenYHandler"),
    (0, 0x0078A40C, 0x005A58D5, 0, "AT^ALS_READ", "atAlsReadHandler"),
    (0, 0x0078CC24, 0x005A58FB, 0, "AT^ALS", "atAlsHandler"),
    (2, 0x007851B0, 0x005A5921, 0, "AT^BRIGHTNESS", "atBrightnessHandler"),
    (0, 0x0077E1B8, 0x005A593B, 0, "AT^ALS_SCALE_READ", "atAlsScaleReadHandler"),
    (0, 0x0077E1CC, 0x005A594D, 0, "AT^BRIGHTNESS_READ", "atBrightnessReadHandler"),
)
WORDS = {
    0x005A57B4: 0x0078CC0C,
    0x005A57B8: 0x00769B4C,
    0x005A57BC: 0x00769B68,
    0x005A57C0: 0x0078A3A0,
    0x005A57C4: 0x00769B84,
    0x005A57C8: 0x00769BA0,
    0x005A57CC: 0x00769BBC,
    0x005A57D0: 0x0078A3B8,
    0x005A57D4: 0x0078A3AC,
    0x005A57D8: 0x00769BD8,
    0x005A57DC: 0x00769BF4,
    0x005A57E0: 0x00769C10,
    0x005A57E4: 0x00727200,
    0x005A57E8: 0x0078A3C4,
    0x005A57EC: 0x0078A3D0,
    0x005A5824: 0x00007325,
    0x005A5828: 0x006DF828,
    0x005A582C: 0x0078A3E8,
    0x005A589C: 0x00769C2C,
    0x005A58A0: 0x006F887C,
    0x005A58A4: 0x00731B44,
    0x005A5960: 0x00785190,
    0x005A5964: 0x00731B74,
    0x005A5968: 0x007851A0,
    0x005A596C: 0x20003994,
    0x005A5970: 0x00747C74,
    0x005A5974: 0x00775614,
    0x005A5978: 0x007523B8,
    0x005A597C: 0x007523DC,
    0x005A5980: 0x00747C9C,
}
STRINGS = {
    0x0078CC0C: "S200",
    0x00769B4C: "Product name:     [%s]\r\n",
    0x00769B68: "Hardware version: [%s]\r\n",
    0x0078A3A0: "2.2.6.10",
    0x00769B84: "Software version: [%s]\r\n",
    0x00769BA0: "Codec version:    [%s]\r\n",
    0x00769BBC: "Touch version:    [%s]\r\n",
    0x0078A3AC: "Jul  6 2026",
    0x0078A3B8: "21:37:47",
    0x00769BD8: "Compile time:     [%s %s]\r\n",
    0x00769BF4: "Product SN:       [%s]\r\n",
    0x00769C10: "BLE NAME:         [%s]\r\n",
    0x00727200: "BLE ADDR:         [%02X:%02X:%02X:%02X:%02X:%02X]\r\n",
    0x0078A3C4: "INFO+OK\r\n",
    0x0078A3D0: "RESET+OK\r\n",
    0x006DF828: "AT^PSN: set PSN: The parameter is incorrect. Please enter the correct command (len %d)\r\n",
    0x0078A3E8: "PSN+OK\r\n",
    0x00769C2C: "AT^IMU_RAWDATA+OK:type=%d\r\n",
    0x006F887C: "AT^IMU_RAWDATA+ERROR: invalid parameter, use 1 to start or 0 to stop\r\n",
    0x00731B44: "AT^IMU_EULER+OK:roll=%.2f,pitch=%.2f,yaw=%.2f\r\n",
    0x00785190: "AT^SCRN_X+OK\r\n",
    0x00731B74: "AT^SCRN_Y Error,height value must be 1 - 192.\r\n",
    0x007851A0: "AT^SCRN_Y+OK\r\n",
    0x00747C74: "AT^ALS_READ+OK:ALS值=%u, LUX_BASE=%d\r\n",
    0x00775614: "AT^ALS+OK:enable=%d\r\n",
    0x007523B8: "AT^BRIGHTNESS+OK:brightness=%d\r\n",
    0x007523DC: "AT^ALS_SCALE_READ+OK:scale_q10=%u\r\n",
    0x00747C9C: "AT^BRIGHTNESS_READ+OK:brightness=%u\r\n",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE : end - BASE]


def pair_digest(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("utf-8")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", data, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 12 or sum(map(len, bodies)) != 486:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    noncode = b"".join(image_slice(data, *interval) for interval in NONCODE)
    if len(noncode) != 126 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned noncode changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical cluster changed")

    raw_records = image_slice(data, *COMMAND_RECORDS)
    if len(raw_records) != 192 or sha256(raw_records) != COMMAND_RECORDS_SHA256:
        raise AuditError("command records changed")
    for index, expected in enumerate(COMMANDS):
        words = struct.unpack_from("<IIII", raw_records, index * 16)
        if words != expected[:4] or cstring(data, words[1]) != expected[4]:
            raise AuditError(f"command registration changed: {expected[4]}")
    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if entry or interior or entry_bw or interior_bw:
        raise AuditError("direct entry/interior closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 49 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointers = [
        (COMMAND_RECORDS[0] + index * 16 + 8, command[2])
        for index, command in enumerate(COMMANDS)
    ]
    if raw_addresses != expected_pointers or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    registered_names = {command[4].lower() for command in COMMANDS}
    routed = any(
        any(name in source.get("path", "").lower() for name in registered_names)
        for source in overlay["sources"]
    )
    if routed:
        raise AuditError("pathless eAT command cluster unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 12,
            "body_bytes": 486,
            "owned_noncode_bytes": 126,
            "physical_bytes": 612,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 49,
            "stored_entry_pointers": 12,
            "strict_interior_ingress": 0,
        },
        "commands": [
            {"name": command[4], "handler": command[5], "record_type": command[0]}
            for command in COMMANDS
        ],
        "product": {
            "name": "S200",
            "software": "2.2.6.10",
            "compile_date": "Jul  6 2026",
            "compile_time": "21:37:47",
        },
        "contracts": {
            "psn_required_length": 14,
            "imu_raw_values": [0, 1],
            "screen_y_machine_range": [0, 192],
            "screen_y_diagnostic_range": [1, 192],
            "als_other_values_acknowledged": True,
            "brightness_unvalidated": True,
            "lux_base_address": "0x200039bc",
        },
        "lineage": {
            "retained_path": None,
            "source_partition_known": False,
            "command_records": "[0x006c92e0,0x006c93a0)",
        },
        "production": {
            "candidate": None,
            "production_routed": routed,
            "ownership_bytes": 0,
            "source_inventory_available": False,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pathless eAT core/sensor cluster audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
