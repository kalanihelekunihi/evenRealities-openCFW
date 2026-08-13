#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party BQ27427 fuel-gauge object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-chg-bq27427-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-chg-bq27427-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-chg-bq27427-provenance.tsv"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/chg_bq27427.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
PINS = {
    FUNCTION_MAP: "1450c00f03999356aeaca638922f4262a753ab5dad678df5bd76a0afc5e1097b",
    CLOSURE: "a81497200d9340d14b89e9ebfb1051b5df12c652dc3a3dcbb42eb3d59ea2af7c",
    PROVENANCE: "1cefcb8d40b42ee5afff89c700a618c8f564e42e95d844a35dfd173e5db2c232",
    CANDIDATE: "c435642a5f377b8265d9311c1e73f69a5b9ffc1f47a1e0d0e68e47179bbd34ee",
}
PHYSICAL = (0x0053AFC0, 0x0053C2A4)
PHYSICAL_SHA256 = "ed5d39ec1667c7b623eba6dfd0deddb9d732ab53dc0e8c6b18392c77a6a929a5"
BODY_SHA256 = "0cdbcb99880d06d844f54b183fbcd484ec45b4c299bf230e2c251c32d28d4529"
NONCODE = [
    (0x0053BB6A, 0x0053BB8C),
    (0x0053BCDA, 0x0053BD0C),
    (0x0053BE8A, 0x0053BEB4),
    (0x0053C016, 0x0053C024),
    (0x0053C0D4, 0x0053C0F4),
    (0x0053C1C4, 0x0053C2A4),
]
NONCODE_SHA256 = "2945fc1a3fc2e2b8c8db96a3577605d213c1962e4a1ef2d7a2c95c1af960ae83"
ENTRY_COUNT = 88
ENTRY_SHA256 = "31c5e418944241c3dcebe62042ad1cf8d7c4227a91a5c397df3e6d57d0f9db00"
EXTERIOR_ENTRY = [(0x004C688A, 0x0053C0F4), (0x0050943C, 0x0053C0FE)]
EXTERIOR_ENTRY_SHA256 = "6352135e959405e766fcacfb4541fde22830f5cb86d0b37b909ad1a5a895664c"
BODY_CALL_COUNT = 287
BODY_CALL_SHA256 = "9633a7b8a873d6b33a91492c47448a07b5cf684140483ef373cfdc9f49049c34"
RAW_INTERIOR_FALSE_POSITIVE = [(0x0063062A, 0x0053B4BE)]
PATH_ADDRESS = 0x0070ADE4
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\driver\chg\drv_bq27427.c"
UNSEAL_KEY_ADDRESS = 0x200006E8
UNSEAL_KEY = bytes.fromhex("00800080")
UNSEAL_KEY_SHA256 = "da60b92bc70e999c07a6ded180a16c1e801e89a5722b565ea242d6aff2f507d8"
DM_TABLE_ADDRESS = 0x200006EC
DM_TABLE = bytes.fromhex(
    "520602000000401f520802000000ff7f520a0200b80b3011400401000000ff00"
    "520201000000ff00510002000000d007690501000000ff7f0604000000000000"
)
DM_TABLE_SHA256 = "4c4a1ae9505326f73b3a74b1e5b3845b7d984ff065d454684fbd9dc1b037a08a"
DEFAULTS_ADDRESS = 0x0078A8BC
DEFAULTS = bytes.fromhex("f0000000500000001c0c0000")
DEFAULTS_SHA256 = "49083b7573db70b2264c79114484fec2ea30facc04431f8cacefde2a1c141f62"


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
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
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
    if len(rows) != 37 or sum(map(len, bodies)) != 4440:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(image_slice(data, *span) for span in NONCODE)
    if len(noncode) != 396 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code changed")
    if cstring(data, PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained source path changed")
    if image_slice(data, DEFAULTS_ADDRESS, DEFAULTS_ADDRESS + 12) != DEFAULTS:
        raise AuditError("product defaults changed")
    if sha256(DEFAULTS) != DEFAULTS_SHA256:
        raise AuditError("product-default pin changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import analyze_g2_flashdb as flashdb
    import recover_apollo_embedded_source_paths as decoder
    initialized = flashdb._decode_initialized_sram(data)
    key_offset = UNSEAL_KEY_ADDRESS - flashdb.IAR_SCATTER_DESTINATION
    table_offset = DM_TABLE_ADDRESS - flashdb.IAR_SCATTER_DESTINATION
    if initialized[key_offset : key_offset + 4] != UNSEAL_KEY:
        raise AuditError("initialized unseal key changed")
    if initialized[table_offset : table_offset + 64] != DM_TABLE:
        raise AuditError("initialized DM descriptor table changed")
    if sha256(UNSEAL_KEY) != UNSEAL_KEY_SHA256 or sha256(DM_TABLE) != DM_TABLE_SHA256:
        raise AuditError("initialized-data pin changed")

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
    if interior != RAW_INTERIOR_FALSE_POSITIVE:
        raise AuditError("raw BL interior-window classification changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if exterior != EXTERIOR_ENTRY or pair_digest(exterior) != EXTERIOR_ENTRY_SHA256:
        raise AuditError("exterior BL closure changed")
    if entry_bw or interior_bw:
        raise AuditError("B.W entry/interior closure changed")

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
    stored_entries = []
    stored_interiors = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            stored_interiors.append((BASE + offset, value))
    if stored_entries or stored_interiors:
        raise AuditError("stored entry/interior pointer appeared")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    routed = any(source.get("path") == candidate_rel for source in overlay["sources"])
    if routed:
        raise AuditError("candidate unexpectedly entered production overlay")

    descriptors = [
        {
            "subclass": DM_TABLE[index],
            "offset": DM_TABLE[index + 1],
            "width": DM_TABLE[index + 2],
            "minimum": struct.unpack_from("<H", DM_TABLE, index + 4)[0],
            "maximum": struct.unpack_from("<H", DM_TABLE, index + 6)[0],
        }
        for index in range(0, 56, 8)
    ]
    return {
        "surface": {
            "linked_functions": 37,
            "body_bytes": 4440,
            "owned_noncode_bytes": 396,
            "physical_bytes": 4836,
            "direct_bl_entry_sites": 88,
            "exterior_bl_entry_sites": 2,
            "direct_body_calls": 287,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
        },
        "abi": {
            "i2c_bus": 7,
            "i2c_address": "0x55",
            "runtime_global": "0x20073b18",
            "runtime_offsets": {"soc": 4, "voltage": 8, "current": 12, "temperature": 16},
            "unseal_key": "0x80008000",
            "dm_block_size": 36,
        },
        "configuration": {
            "defaults": [240, 80, 3100],
            "descriptors": descriptors,
            "dm_table_sha256": DM_TABLE_SHA256,
        },
        "production": {
            "candidate": candidate_rel,
            "production_routed": routed,
            "ownership_bytes": 0,
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 BQ27427 fuel-gauge audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
