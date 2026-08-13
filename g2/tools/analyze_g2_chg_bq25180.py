#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party BQ25180 charger object."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-chg-bq25180-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-chg-bq25180-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-chg-bq25180-provenance.tsv"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/chg_bq25180.c"
PINS = {
    FUNCTION_MAP: "5c71b831fbe1f1a254a742d0c3d07b89617b1397412b185625397dab6c60ef57",
    CLOSURE: "dc4d98d5304d2bc817ebf993f9e9e3d7cbeb642ae5b4863b962c183e5c56d4c1",
    PROVENANCE: "87f000e80e818aad2841db0011f8d49d4a187b733dbdac7418f635374cebbb6b",
    CANDIDATE: "0291aa058fd90a957b97fd0066e2d49bf16676b761662a32bdb5d717be74067b",
}
PHYSICAL = (0x0053A670, 0x0053AFC0)
PHYSICAL_SHA256 = "a2886fb69c9abc85bfa25a1d71db3c9c040a47d0609751f71c9f5c305c6c1f30"
POOL = (0x0053AF4C, 0x0053AFC0)
POOL_SHA256 = "1709443848efd8bb84f60e554b5d07002e4d74f32a13a5288ea6e1dd2b3da4cf"
BODY_SHA256 = "7ddab9a21b4394ca80bbedcac0fee1141f4e407c7c86038f4aa52b9f50fc8620"
ENTRY_COUNT = 56
ENTRY_SHA256 = "ac7ddc6f6d0b6367d958649975065e3b90206e94bbb93f843ef1941f8f9d8bc0"
EXTERIOR_ENTRY_CALLS = [(0x004C6886, 0x0053AE66), (0x00509438, 0x0053AE7E)]
EXTERIOR_ENTRY_SHA256 = "041227f3ea11d59807015a1b123667cbaff5555e08c299ccff7fa868d4c0c6ae"
BODY_CALLS = 93
BODY_CALL_SHA256 = "d0cf5ecd1fa1327b6b806638ed38471d8f1e73a46cf92458025c099ec8dbf5d5"
WORDS = {
    0x0053AF4C: 0x00000000,
    0x0053AF50: 0x2007456C,
    0x0053AF54: 0x00776AB4,
    0x0053AF58: 0x0078A8B0,
    0x0053AF5C: 0x007538AC,
    0x0053AF60: 0x0070AD24,
    0x0053AF64: 0x0078D45C,
    0x0053AF68: 0x00776ACC,
    0x0053AF6C: 0x20073B18,
    0x0053AF70: 0x00733224,
    0x0053AF74: 0x00776AE4,
    0x0053AF78: 0x0078D464,
    0x0053AF7C: 0x0071DFF0,
    0x0053AF80: 0x00733254,
    0x0053AF84: 0x0071E028,
    0x0053AF88: 0x00749344,
    0x0053AF8C: 0x007021D4,
    0x0053AF90: 0x0073E0B4,
    0x0053AF94: 0x006E7630,
    0x0053AF98: 0x0075F570,
    0x0053AF9C: 0x0070AD64,
    0x0053AFA0: 0x200744FC,
    0x0053AFA4: 0x0074936C,
    0x0053AFA8: 0x0077EEC4,
    0x0053AFAC: 0x00733284,
    0x0053AFB0: 0x0071E060,
    0x0053AFB4: 0x0070ADA4,
    0x0053AFB8: 0x007538D0,
    0x0053AFBC: 0x007332B4,
}
STRINGS = {
    0x00776AB4: "DRV_Bq25180ReadEvent",
    0x0078A8B0: "p != NULL",
    0x0070AD24: r"D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq25180.c",
    0x00776ACC: "DRV_Bq25180ReadStatet",
    0x00776AE4: "bq25180_read_device_id",
    0x00749344: "DRV_Bq25180SetBatteryRegulationVoltage",
    0x007021D4: "millivoltage >= MIN_BAT_REG_mV && millivoltage <= MAX_BAT_REG_mV",
    0x0073E0B4: "DRV_Bq25180SetBatteryUnderVoltage_lockout",
    0x006E7630: "millivoltage >= MIN_BAT_UNDERVOLTAGE_mV && millivoltage <= MAX_BAT_UNDERVOLTAGE_mV",
    0x0075F570: "DRV_Bq25180SetFastchargeCurrent",
    0x0070AD64: "milliampere >= MIN_IN_CURR_mA && milliampere <= MAX_IN_CURR_mA",
    0x0077EEC4: "DRV_Bq25180HwInit",
}


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sl(blob: bytes, start: int, end: int) -> bytes:
    return blob[start - BASE : end - BASE]


def pairs(values: list[tuple[int, int]]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def load(name: str, path: Path):
    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AuditError(f"cannot load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def cstring(blob: bytes, address: int) -> str:
    offset = address - BASE
    end = blob.find(b"\0", offset)
    return blob[offset:end].decode("ascii")


def thumb_bw_target(blob: bytes, address: int) -> int | None:
    offset = address - BASE
    first, second = struct.unpack_from("<HH", blob, offset)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    i1 = (~(j1 ^ sign)) & 1
    i2 = (~(j2 ^ sign)) & 1
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    blob = image_path.read_bytes()
    if len(blob) != 3_523_396 or sha256(blob) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")

    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    starts: set[int] = set()
    interiors: set[int] = set()
    bodies: list[bytes] = []
    intervals: list[tuple[int, int]] = []
    for row in rows:
        start = int(row["stock_start"], 0)
        end = int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 28 or sum(map(len, bodies)) != 2268:
        raise AuditError("function inventory changed")
    if intervals[0][0] != PHYSICAL[0] or intervals[-1][1] != POOL[0]:
        raise AuditError("object boundary changed")
    if any(left[1] != right[0] for left, right in zip(intervals, intervals[1:])):
        raise AuditError("unexpected function gap appeared")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(sl(blob, *POOL)) != POOL_SHA256:
        raise AuditError("owned literal pool changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"pool word changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    decoder = load(
        "chg_bq25180_thumb",
        ROOT / "tools/recover_apollo_embedded_source_paths.py",
    )
    entry: list[tuple[int, int]] = []
    interior_bl: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(blob) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(blob, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior_bl.append((site, target))
        target = thumb_bw_target(blob, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    if len(entry) != ENTRY_COUNT or pairs(entry) != ENTRY_SHA256 or interior_bl:
        raise AuditError("BL entry/interior closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < POOL[0])]
    if exterior != EXTERIOR_ENTRY_CALLS or pairs(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior entry closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(blob, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != BODY_CALLS or pairs(calls) != BODY_CALL_SHA256:
        raise AuditError("direct-call closure changed")

    encoded_entries = starts | {value | 1 for value in starts}
    encoded_interiors = interiors | {value | 1 for value in interiors}
    stored_entries = []
    stored_interiors = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored entry/interior pointer appeared")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    if any(source.get("path") == candidate_rel for source in overlay["sources"]):
        raise AuditError("candidate unexpectedly entered production overlay")

    return {
        "surface": {
            "linked_functions": 28,
            "body_bytes": 2268,
            "owned_pool_bytes": 116,
            "physical_bytes": 2384,
            "direct_bl_entry_sites": 56,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 93,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "abi": {
            "i2c_bus": 7,
            "i2c_address": "0x6a",
            "runtime_pointer": "0x200744fc",
            "runtime_event_offset": "0x14",
            "runtime_state_offset": "0x16",
            "cached_charge_state": "0x20073b18",
        },
        "defaults": {
            "call_count": 19,
            "register_image_hex": "0000005a24241f4406002100f0",
            "battery_regulation_mv": 4400,
            "fastcharge_ma": 91,
            "input_limit_ma": 1000,
            "battery_uvlo_mv": 2800,
            "charger_enabled_at_exit": True,
        },
        "behavior": {
            "device_id_register": "0x0c",
            "accepted_device_id": 0,
            "event_register": "0x02",
            "state_registers": ["0x00", "0x01"],
            "field_helper_masks_input_value": False,
        },
        "production": {
            "candidate": candidate_rel,
            "production_routed": False,
            "ownership_bytes": 0,
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
