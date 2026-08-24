#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 pb_service_ring object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-pb-service-ring-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pb-service-ring-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-pb-service-ring-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/pb_service_ring.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FUNCTION_MAP: "43700fbb0f7015e30b1ed5b5e18eb57a862ad2ff3b565677ee0888cdba6706df",
    CLOSURE: "47b2ff130fb3beb8a5d34032b4f9cb258ce0fccd6a477a04a184b7ab7b18a77f",
    PROVENANCE: "1658f580d2dac74213a387f7d7800c569e4c825a240cf8a8e02a7783366ee426",
}
SOURCE_SIZE = 8179
SOURCE_SHA256 = "270772d136060be649f684e05e3de604bd89bd8ea6e0a4599ee550077c5c19cb"
FUNCTIONS = (
    ("open_cfw_pb_service_ring_buffer_write", 146, 193876, 0),
    ("APP_PbRxRingFrameDataProcess", 128, 194024, 4),
    ("PB_RxRingEvent", 10, 194152, 0),
    ("APP_PbTxEncodeRingEvent", 284, 194164, 4),
    ("RingDataRelay_common_data_handler", 26, 194448, 1),
)
PATCHES = (
    ("replace_pb_ring_rx_frame", 0x005CE1DC, 498,
     "91584b2a82140bf9e7a99283d76e3ceef267daeb75d469caf283037b3c9e2ed6",
     "APP_PbRxRingFrameDataProcess"),
    ("replace_pb_ring_rx_event", 0x005CE3CE, 280,
     "807dda29aad8d7dd432396548b36068614a066a0a7e1c128b0e1051798080ddc",
     "PB_RxRingEvent"),
    ("replace_pb_ring_tx_event", 0x005CE4E6, 426,
     "c50bfc78dcb2a0925d27509bf7b122ce1a0e5ce8c749e77a331578fda85d93eb",
     "APP_PbTxEncodeRingEvent"),
    ("replace_pb_ring_relay", 0x005CE690, 158,
     "db44519e2c518465e77aeedeee75f7eb8d9cde03d2240804cbab70f2dc3407e9",
     "RingDataRelay_common_data_handler"),
)
PHYSICAL = (0x005CE1DC, 0x005CE7C4)
PHYSICAL_SHA256 = "2e570db8cab30734f3a547a7ad4dfa704d167010710fa5a925d465dc4e81348c"
TAIL = (0x005CE72E, 0x005CE7C4)
TAIL_SHA256 = "dabbf3fe420fa5c2fb505c225a4641a092f66ccc9ac4ad01118557fb018e4deb"
BODY_SHA256 = "6bf1505dabaea4b5a7a4d4708729bf96cd61dba84b7bfef4a15b0224732f2be7"
ENTRY_SHA256 = "5b36860ef501337410e05238b9ed7a2e44e32e5e6fdba44a4d17f6c400b009cf"
BODY_CALL_SHA256 = "f068db1641d0199c3128c4385ac39f747ec9d5bfa0295f3a481b197364cb7580"
STORED_SHA256 = "0db43e16cc0240db8d9b98ede51521834fd01711dd529667337db0ca8131cd4a"
FALSE_INTERIOR_SHA256 = "8263c3216971e361e7a252743167c96403e2846941902ecec6f9e61a7d5d872d"
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"pb_service_ring\pb_service_ring.c"
)
TAIL_WORDS = (
    0x0078DF54, 0x007636B0, 0x006E1264, 0x0078DF4C, 0x00787ED0,
    0x00787EE0, 0x0077A5C4, 0x200F86BC, 0x0077B104, 0x0078DF5C,
    0x007823E4, 0x007636D0, 0x007823F8, 0x007636F0, 0x0077A5DC,
    0x00763710, 0x00782420, 0x00787F00, 0x00787EF0, 0x0077A5F4,
    0x00717794, 0x00704748, 0x0077A60C, 0x00763730, 0x00782434,
    0x0077A624, 0x2037C8A0, 0x200F86FC, 0x0078B7B0, 0x0078240C,
    0x0077A63C, 0x00763750, 0x00757D94, 0x00757D70, 0x0074154C,
    0x0077A654, 0x00763770,
)
STRINGS = {
    0x0078DF54: "len=%d",
    0x007636B0: "APP_PbRxRingFrameDataProcess",
    0x006E1264: RETAINED_PATH,
    0x0078DF4C: "pb.ring",
    0x00787ED0: "[pb.ring]len=%d",
    0x00787EE0: "pData is NULL",
    0x0077A5C4: "[pb.ring]pData is NULL",
    0x0078DF5C: "(none)",
    0x007823E4: "Decoding failed: %s",
    0x007636D0: "[pb.ring]Decoding failed: %s",
    0x007823F8: "ring command_id: %d",
    0x007636F0: "[pb.ring]ring command_id: %d",
    0x0077A5DC: "Unknown command_id: %d",
    0x00763710: "[pb.ring]Unknown command_id: %d",
    0x00787F00: "POINTER NULL",
    0x00787EF0: "PB_RxRingEvent",
    0x0077A5F4: "[pb.ring]POINTER NULL",
    0x00717794: "pEvent:event_id = %d, event_param = %d, ring_mac size = %d",
    0x00704748: "[pb.ring]pEvent:event_id = %d, event_param = %d, ring_mac size = %d",
    0x0077A60C: "Unknown event_id: %d",
    0x00763730: "[pb.ring]Unknown event_id: %d",
    0x0077A624: "APP_PbTxEncodeRingEvent",
    0x0078B7B0: "txLen = %d",
    0x0078240C: "[pb.ring]txLen = %d",
    0x0077A63C: "Encoding failed: %s\n",
    0x00763750: "[pb.ring]Encoding failed: %s\n",
    0x00757D94: "ring recv eventType = %d, len = %d",
    0x00757D70: "RingDataRelay_common_data_handler",
    0x0074154C: "[pb.ring]ring recv eventType = %d, len = %d",
    0x0077A654: "Unknown event type: %d",
    0x00763770: "[pb.ring]Unknown event type: %d",
}
ASSERT_RECORDS = {
    0x00782420: "000000000000000064126e00f07e780058000000",
    0x00782434: "000000000000000064126e0024a6770082000000",
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
    if len(rows) != 4 or sum(map(len, bodies)) != 1362:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    tail = image_slice(data, *TAIL)
    if len(tail) != 150 or sha256(tail) != TAIL_SHA256 or tail[:2] != b"\0\0":
        raise AuditError("alignment/pool tail changed")
    if struct.unpack("<37I", tail[2:]) != TAIL_WORDS:
        raise AuditError("literal pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 2) != bytes.fromhex("2de9"):
        raise AuditError("next-function boundary changed")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    for address, expected_hex in ASSERT_RECORDS.items():
        if image_slice(data, address, address + 20).hex() != expected_hex:
            raise AuditError(f"assert record changed at 0x{address:08x}")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == 0x006E1264]
    if path_cells != [0x005CE738, 0x00782428, 0x0078243C]:
        raise AuditError("retained path-pointer closure changed")
    registry = image_slice(data, 0x006A45B0, 0x006A45C0)
    if sha256(registry) != "2ae6b619c2447592af6235750c7322318a97d7ff7e19fbe01f9f8952d03b3516":
        raise AuditError("ring relay registration changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    raw_interior: list[tuple[int, int]] = []
    entry_bw: list[tuple[int, int]] = []
    interior_bw: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            raw_interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts:
            entry_bw.append((site, target))
        elif target in interiors:
            interior_bw.append((site, target))
    expected_entry = [
        (0x005CE36C, 0x005CE3CE), (0x005CE378, 0x005CE4E6),
        (0x005CE6E4, 0x005CE1DC),
    ]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    expected_false = [(0x004DDD58, 0x005CE370)]
    if raw_interior != expected_false or pair_digest(raw_interior) != FALSE_INTERIOR_SHA256:
        raise AuditError("raw interior candidate closure changed")
    if image_slice(data, 0x004DDD56, 0x004DDD5A) != bytes.fromhex("99fbf0f0"):
        raise AuditError("SDIV overlap proof changed")
    if entry_bw or interior_bw:
        raise AuditError("direct B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 82 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            stored.append((BASE + offset, value))
    if stored != [(0x006A45B4, 0x005CE691)] or pair_digest(stored) != STORED_SHA256:
        raise AuditError("stored entry/interior closure changed")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {row[0] for row in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise AuditError("production leaf inventory changed")
    for name, size, offset, relocations in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") !=
                "components/apollo_main/core_overlay/pb_service_ring.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"), leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocations):
            raise AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for name, address, size, digest, function in PATCHES:
        patch = patch_by_name.get(name)
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != (address, size, digest, "b_w", function, ["apple-clang"]):
            raise AuditError(f"production patch changed: {name}")
    report = json.loads(REPORT.read_text())
    if (report["overlay"]["size"], report["overlay"]["sha256"],
            report["component"]["size"], report["component"]["sha256"]) != (
        197488, "a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183",
        3720884, "026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a",
    ):
        raise AuditError("production build pins changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    if (main["provider"].get("size"), main["provider"].get("sha256"),
            manifest["package"].get("expected_size"),
            manifest["package"].get("expected_sha256")) != (
        3720884, "026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a",
        4499378, "03d4b3f7813ce41814ae821ccbdaa3a1f2802fe4a459cf20351487a18332e783",
    ):
        raise AuditError("production manifest pins changed")
    region_names = {item["name"] for item in main["regions"]}
    required = {name.removeprefix("replace_") + "_source_replacement"
                for name, *_ in PATCHES}
    required |= {
        "pb_service_ring_retained_literal_pool",
        "pb_service_ring_buffer_write_source_text",
        "pb_ring_rx_frame_source_alignment", "pb_ring_rx_frame_source_text",
        "pb_ring_rx_event_source_text", "pb_ring_tx_event_source_alignment",
        "pb_ring_tx_event_source_text", "pb_ring_relay_source_text",
    }
    if not required <= region_names:
        raise AuditError("production manifest regions changed")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 1362,
            "owned_tail_bytes": 150,
            "physical_bytes": 1512,
            "direct_bl_entry_sites": 3,
            "stored_exact_entry_pointers": 1,
            "direct_body_calls": 82,
            "strict_interior_ingress": 0,
            "false_halfword_bl_candidates": 1,
        },
        "contracts": {
            "rx_status": {"success": 0, "unsupported_or_invalid": 1,
                          "null": 2, "decode_failure": 0x2B},
            "tx_status": {"success": 0, "null": 2, "encode_failure": 0x2B},
            "command_id": 1,
            "nested_payload_tag": 3,
            "relay_event_type": 0,
            "route": 1,
            "service": "0x91",
            "decoded_message": "0x200f86bc",
            "encoded_message": "0x200f86fc",
            "message_bytes": 0x40,
            "encode_buffer": "0x2037c8a0",
            "encode_capacity": 0x100,
            "ring_mac_max_copied": 6,
            "event_id_supported": 1,
            "event_param_bytes": 4,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{address:08x}" for address in path_cells],
            "exact_symbols": [row["function"] for row in rows],
            "relay_registry_record": "0x006a45b0",
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "ownership_bytes": 1362,
            "source_inventory_available": True,
            "source_functions": 5,
            "compiled_text_bytes": 594,
            "alignment_bytes": 4,
            "strict_relocations": 9,
            "stock_replaced_bytes": 1362,
            "retained_literal_pool_bytes": 150,
            "software_functional_gap": False,
            "hardware_validation": "blocked",
            "hardware_blocker": (
                "No authorized physical paired-G2 BLE relay, live nanopb peer, "
                "or ring-event evidence is available."
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError, UnicodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pb_service_ring audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
