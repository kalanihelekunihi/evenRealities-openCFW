#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 first-party buzzer driver object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-drv-buzzer-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-drv-buzzer-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-drv-buzzer-provenance.tsv"
PINS = {
    FUNCTION_MAP: "e7cbdec66996c1fcdb33a026447094405772fe673096d82ecc1cc1255a645c1f",
    CLOSURE: "75b0a8580e3691481630ee399f3b8caf50f6b2af74a16ccd852d7fdae31b02d3",
    PROVENANCE: "7b967db320652b73db4c5537c5c660dbaeed2a5622ac4ee7fd822fc06119d618",
}
PHYSICAL = (0x005026BC, 0x00502D58)
PHYSICAL_SHA256 = "bb0e91e073997cef46149ad62602af99d31c53100384029a6677232485b42c7d"
BODY_SHA256 = "485d4b4858a0fcb6ab2a502d430cbcea4cb6d12796f18fe15a1d10573b8ef1e5"
GAPS = [
    (0x0050278E, 0x00502790),
    (0x005029F8, 0x005029FC),
    (0x00502CA8, 0x00502D4C),
    (0x00502D56, 0x00502D58),
]
NONCODE_SHA256 = "84c4e7ad87f1993779fbdf10a0a9a4bd6a19d24f8542b03d5e2df3c1a9246825"
ENTRY_COUNT = 35
ENTRY_SHA256 = "b85bf31b40bc82a17242e5d909f3fc404887dd8ceb921cc8f678c7dec24739f3"
EXTERIOR_COUNT = 18
BODY_CALL_COUNT = 88
BODY_CALL_SHA256 = "90cc9a6bec84ce64796ec37979007d29c8970a7f22b2d10d9b232776e9a7264f"
STORED_ENTRIES = [(0x00502D14, 0x005029FD)]
STORED_ENTRY_SHA256 = "a6199f14f401108513c62d9686f27e01d0a95aa624346a2e6d69ba986d6103d3"
RAW_INTERIOR_WINDOWS = [
    (0x00446977, 0x005027F2),
    (0x0045DDC7, 0x00502BF2),
    (0x00470B5D, 0x00502AF2),
    (0x0047B1EF, 0x00502AF2),
    (0x00495FBD, 0x005027F2),
    (0x004E8B7B, 0x00502BF2),
    (0x004EC1E1, 0x005029F2),
    (0x0054D57B, 0x005026F6),
    (0x0057668B, 0x005028F6),
    (0x005ADBB7, 0x00502AF8),
    (0x005E5FBB, 0x005026F2),
]
RAW_INTERIOR_SHA256 = "448b0662fa673d212150ec4ceec2414726aa7452a139cf921a2e01e174e00531"
RELOAD_LOW = (0x0076B014, 0x0076B030)
RELOAD_LOW_SHA256 = "170e9c388fe4150ab5db7805770daadfb54635fd08eb2452b81d6ba194db589a"
RELOAD_HIGH = (0x0076B030, 0x0076B04C)
RELOAD_HIGH_SHA256 = "7d17fc20e450b7a9c76fc8bf99c4062634fff0281dd2326623e29ad92feb9ebd"
RELOAD_COMBINED_SHA256 = "6a06ee22d72c02a369bedbc5b8c27998dff91cab5c649b839f84884b2da7bf43"
VOICE_TABLE = (0x006C1E2C, 0x006C1FEE)
VOICE_TABLE_SHA256 = "183d6370260fc192ce25b57b40b8d0768bd4362e842a6bc826c45d7b16939d41"
PATH_ADDRESS = 0x0070AE24
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\buzzer\drv_buzzer.c"
WORDS = {
    0x00502CA8: 0x20074120,
    0x00502CAC: 0x05B8D800,
    0x00502CB0: 0x0078EE48,
    0x00502CB4: 0x20074500,
    0x00502CB8: 0x20074FB5,
    0x00502CBC: 0x20074FB4,
    0x00502CC0: 0x20074F2E,
    0x00502CC4: 0x00753A14,
    0x00502CC8: 0x0077EF50,
    0x00502CCC: PATH_ADDRESS,
    0x00502CD0: 0x0078A8C8,
    0x00502CD4: 0x00733494,
    0x00502CD8: 0x20074504,
    0x00502CDC: 0x0078A8D4,
    0x00502CE0: 0x00776C04,
    0x00502CE4: 1_000_000,
    0x00502CE8: RELOAD_LOW[0],
    0x00502CEC: RELOAD_HIGH[0],
    0x00502CF0: 0x00753A38,
    0x00502CF4: 0x007334C4,
    0x00502CF8: 0x0075F6D0,
    0x00502CFC: 0x0077EF64,
    0x00502D00: 0x0073E1E8,
    0x00502D04: 0x0074954C,
    0x00502D08: 0x00728C34,
    0x00502D0C: 0x20000724,
    0x00502D10: 0x00785C60,
    0x00502D14: 0x005029FD,
    0x00502D18: 0x00749574,
    0x00502D1C: 0x00785C50,
    0x00502D20: 0x00728C68,
    0x00502D24: 0x0073E214,
    0x00502D28: 0x0076AFF8,
    0x00502D2C: 0x0071E140,
    0x00502D30: 0x0077EF78,
    0x00502D34: 0x0075F6F0,
    0x00502D38: VOICE_TABLE[0],
    0x00502D3C: 0x007334F4,
    0x00502D40: 0x0077EF8C,
    0x00502D44: 0x007145A8,
    0x00502D48: 0x20074128,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    0x0078A8C8: "drv.buzzer",
    0x00753A14: "play again times=%d, intervel=%d",
    0x0077EF50: "_buzzerPlayVoice",
    0x0078A8D4: "beep:stop",
    0x00753A38: "beep: freq=%d, delay=%d times=%d",
    0x0075F6D0: "_buzzerPlayStart: pVoice=NULL",
    0x0077EF64: "_buzzerPlayStart",
    0x0074954C: "_buzzerPlayStart: times=%d, interval=%d",
    0x00749574: "[buzzerPwmGpioInit]osTimerNew failed",
    0x00785C50: "DRV_BuzzerInit",
    0x0073E214: "DRV_BuzzerPlayAfterQueue type out of range",
    0x0076AFF8: "DRV_BuzzerPlayAfterQueue",
    0x0077EF78: "buzzer play type %d",
    0x007334F4: "DRV_BuzzerPlayNote note=%d, tone=%d, beat=%d",
    0x0077EF8C: "DRV_BuzzerPlayNote",
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
    return data[offset:end].decode("ascii")


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
    if len(rows) != 17 or sum(map(len, bodies)) != 1520:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *gap) for gap in GAPS)
    if len(noncode) != 172 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")
    if image_slice(data, 0x005029F8, 0x005029FC) != struct.pack("<f", 100.0):
        raise AuditError("PWM percentage constant changed")

    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    reload_low = image_slice(data, *RELOAD_LOW)
    reload_high = image_slice(data, *RELOAD_HIGH)
    if sha256(reload_low) != RELOAD_LOW_SHA256 or sha256(reload_high) != RELOAD_HIGH_SHA256:
        raise AuditError("PWM reload table changed")
    if sha256(reload_low + reload_high) != RELOAD_COMBINED_SHA256:
        raise AuditError("combined PWM reload table changed")
    voice_table = image_slice(data, *VOICE_TABLE)
    if len(voice_table) != 9 * 50 or sha256(voice_table) != VOICE_TABLE_SHA256:
        raise AuditError("predefined voice table changed")
    triple_counts: list[int] = []
    for index in range(9):
        record = voice_table[index * 50 : (index + 1) * 50]
        count = 0
        for cursor in range(2, 50, 3):
            if record[cursor] == 0:
                break
            if cursor + 2 >= 50:
                raise AuditError(f"unterminated voice record {index}")
            count += 1
        else:
            raise AuditError(f"unterminated voice record {index}")
        triple_counts.append(count)
    if triple_counts != [1, 14, 12, 1, 2, 1, 7, 7, 1]:
        raise AuditError("voice record shape changed")

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
    if len(entry) != ENTRY_COUNT or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if len(exterior) != EXTERIOR_COUNT:
        raise AuditError("exterior BL closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("direct strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALL_COUNT or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries: list[tuple[int, int]] = []
    stored_interiors: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries != STORED_ENTRIES or pair_digest(stored_entries) != STORED_ENTRY_SHA256:
        raise AuditError("stored callback entry closure changed")
    if stored_interiors != RAW_INTERIOR_WINDOWS or pair_digest(stored_interiors) != RAW_INTERIOR_SHA256:
        raise AuditError("raw interior overlap qualification changed")
    if any(site % 2 == 0 for site, _ in stored_interiors):
        raise AuditError("unaligned overlap became executable-looking")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("drv_buzzer" in source.get("path", "").lower() for source in overlay["sources"])
    if routed:
        raise AuditError("unimplemented buzzer driver unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 17,
            "body_bytes": 1520,
            "owned_noncode_bytes": 172,
            "physical_bytes": 1692,
            "direct_bl_entry_sites": 35,
            "exterior_bl_entry_sites": 18,
            "direct_body_calls": 88,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 11,
        },
        "audio": {
            "peripheral_clock_hz": 96_000_000,
            "frequency_divisor": 1_000_000,
            "reload_entries": 28,
            "reload_bytes_per_entry": 2,
            "voice_records": 9,
            "voice_record_bytes": 50,
            "voice_triple_counts": triple_counts,
            "duration_quantum_ms": 62,
            "interval_quantum_ms": 10,
        },
        "runtime": {
            "timer_callback": "0x005029fd",
            "timer_handle_slot": "0x20074504",
            "voice_pointer_slot": "0x20074500",
            "voice_cursor_slot": "0x20074fb5",
            "repeat_count_slot": "0x20074fb4",
            "repeat_interval_slot": "0x20074f2e",
            "single_note_script": "0x20074128",
            "valid_voice_types": 9,
            "queued_play_event": 1,
            "timer_event": 2,
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
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 buzzer driver audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
