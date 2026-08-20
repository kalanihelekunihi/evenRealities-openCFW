#!/usr/bin/env python3
"""Fail-closed audit of the G2 first-party charger-common object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-charger-common-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-charger-common-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-charger-common-provenance.tsv"
CANDIDATE = ROOT / "components/apollo_main/core_overlay/charger_common.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
PINS = {
    FUNCTION_MAP: "bcf46ec7ffb64fc3146247490f94e83b8069885367e12945b9374d7954cde11b",
    CLOSURE: "66ef12042a120285653cf24625c5538ee53bfeb92809fe5f3b932c907cec104e",
    PROVENANCE: "61fcd58f3727a1a287c7030a26c1292fa85ae7aa4265d49a0070e6e4c9eff349",
    CANDIDATE: "1c3b2d7fa0da4e3e4aed565c1e8585638c5dcb0e3ba7a36e0f9335956d7c12ab",
}
PHYSICAL = (0x004ACE10, 0x004AD9B8)
PHYSICAL_SHA256 = "66629608034c65df865a5376ea4e6caf566216810d698d842f77ea487031004c"
GAPS = [
    (0x004AD7C6, 0x004AD7DC),
    (0x004AD86A, 0x004AD880),
    (0x004AD908, 0x004AD9B8),
]
NONCODE_SHA256 = "c9e1e05b77a186c9d8fa32bd7ca8332032f17ce6a7f69022d5aab404dc8838f9"
BODY_SHA256 = "cc3b89cc5efc5d671fdda351e6fb3a194f6bf1277a798e2f399ecaf3603cbd88"
ENTRY_COUNT = 25
ENTRY_SHA256 = "e658e2bf0d107ffe2c80972b1234aed4ef7c793bc328182c43de19d938c742a9"
EXTERIOR_ENTRY_CALLS = [
    (0x0046B43A, 0x004AD8FA),
    (0x0046B440, 0x004AD900),
    (0x004C632E, 0x004ACF7C),
    (0x004C64A6, 0x004AD06C),
    (0x004C6896, 0x004AD45C),
    (0x00509F90, 0x004AD8FA),
    (0x005F969C, 0x004AD53E),
    (0x005F96E0, 0x004AD652),
    (0x005F9720, 0x004AD652),
    (0x005F9760, 0x004AD53E),
]
EXTERIOR_ENTRY_SHA256 = "8f7e126331a8a9c9447b5693393aced1305a1e2a1a373e86a85f98ebc391dd45"
BODY_CALLS = 157
BODY_CALL_SHA256 = "80bbb6bd8256d28fa514c0c654114170e54c85eb9c03f1a836c0cecbc0621752"
RAW_INTERIOR_WINDOWS = [
    (0x00595772, 0x004AD05D),
    (0x005957A0, 0x004AD046),
    (0x005957EC, 0x004AD020),
    (0x0059581A, 0x004AD009),
    (0x00595836, 0x004AD006),
    (0x0064CF2B, 0x004AD0FF),
]
OVERLAP_BYTES = {
    0x00595772: bytes.fromhex("5dd04a00"),
    0x005957A0: bytes.fromhex("46d04a00"),
    0x005957EC: bytes.fromhex("20d04a00"),
    0x0059581A: bytes.fromhex("09d04a00"),
    0x00595836: bytes.fromhex("06d04a00"),
    0x0064CF2B: bytes.fromhex("ffd04a00"),
}
WORDS = {
    0x004AD7C8: 0x20074F98,
    0x004AD7D0: 0x0077E884,
    0x004AD7D8: 0x20074F1A,
    0x004AD874: 0x20074F99,
    0x004AD878: 0x20074F1C,
    0x004AD908: 0x20073B30,
    0x004AD90C: 0x006EB9E8,
    0x004AD910: 0x00785720,
    0x004AD924: 0x20074370,
    0x004AD930: 0x20074104,
    0x004AD934: 0x20074F97,
    0x004AD97C: 0x20073B18,
}
STRINGS = {
    0x006EB9E8: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\charger\charger_common.c",
    0x00785720: "charger_common",
    0x0077E884: "_CHG_HandleInitSync",
    0x0077E8AC: "CHG_InitBatterySync",
    0x007759D4: "CHG_DeinitBatterySync",
    0x007759EC: "CHG_CompareAndUpdateSoc",
    0x0075E5F0: "CHG_CompareAndUpdateIsCharging",
    0x0076A038: "CHG_OnBatteryLevelChanged",
    0x0076A054: "CHG_SendBatteryInfoToPeer",
    0x0075E610: "CHG_ReceiveBatteryInfoFromPeer",
    0x007481C4: "CHG_RequestNotifyBatteryInfoFromPeer",
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
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = sl(blob, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 14 or sum(map(len, bodies)) != 2764:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(sl(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    noncode = b"".join(sl(blob, *gap) for gap in GAPS)
    if len(noncode) != 220 or sha256(noncode) != NONCODE_SHA256:
        raise AuditError("owned non-code regions changed")
    for address, expected in WORDS.items():
        if struct.unpack("<I", sl(blob, address, address + 4))[0] != expected:
            raise AuditError(f"literal changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(blob, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")

    decoder = load(
        "charger_common_thumb",
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
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
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
    raw_windows = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value in encoded_entries:
            stored_entries.append((BASE + offset, value))
        if value in encoded_interiors:
            raw_windows.append((BASE + offset, value))
    if stored_entries or raw_windows != RAW_INTERIOR_WINDOWS:
        raise AuditError("stored/raw pointer qualification changed")
    for address, expected in OVERLAP_BYTES.items():
        if sl(blob, address, address + 4) != expected:
            raise AuditError(f"qualified overlap changed at 0x{address:08x}")

    overlay = json.loads(OVERLAY.read_text())
    candidate_rel = str(CANDIDATE.relative_to(ROOT))
    expected_patches = {
        "replace_charger_init_battery_sync": (
            0x004ACF7C, 240,
            "cf644d6896767580a69237ee70ca971109f791029041e5ae57f0e49f8c0ff25a",
            "open_cfw_charger_init_battery_sync",
        ),
        "replace_charger_deinit_battery_sync": (
            0x004AD06C, 94,
            "62c8977e52b362b234934c83e090e4b5b2b9183b50e8751dba7f963a5660d63d",
            "open_cfw_charger_deinit_battery_sync",
        ),
        "replace_charger_compare_and_update_soc": (
            0x004AD0CA, 464,
            "cc52b2c86a8b3ef7e4db02b129c12d5333a2a2f22810d0952d23ebe6485a2305",
            "open_cfw_charger_compare_and_update_soc",
        ),
        "replace_charger_compare_and_update_is_charging": (
            0x004AD29A, 450,
            "ccb7326dc41fdb422b4b246fa1b2b31747cbdf945190776edc3bc5a83a00e1aa",
            "open_cfw_charger_compare_and_update_is_charging",
        ),
        "replace_charger_on_battery_level_changed": (
            0x004AD45C, 226,
            "e29ae19b89477617a740c0025ea2a60dd550061a3f601ec3b9556b6950846e3b",
            "open_cfw_charger_on_battery_level_changed",
        ),
        "replace_charger_send_battery_info_to_peer": (
            0x004AD53E, 276,
            "9b7203c4a29a8fcf45415491aabe4806677a1f0e0eb1e894fbe6baf5c324753a",
            "open_cfw_charger_send_battery_info",
        ),
        "replace_charger_receive_battery_info_from_peer": (
            0x004AD652, 372,
            "283651c314e14353d854e5dcbaa154f27ff51e6ef2a6f9840f2699bcdca13a6b",
            "open_cfw_charger_receive_battery_info_from_peer",
        ),
        "replace_charger_request_notify_battery_info_from_peer": (
            0x004AD7DC, 142,
            "9edd932a9f208179c1de2298e182b7120e2fc032e2792161abfe9b52a6d80284",
            "open_cfw_charger_request_notify_battery_info_from_peer",
        ),
        "replace_charger_get_local_battery_info": (
            0x004AD880, 122,
            "15cc132f0050bd3c19d36cded1d55d4db9ede0687191893e04e87036b1254730",
            "open_cfw_charger_get_local_battery_info",
        ),
        "replace_charger_get_soc": (
            0x004AD8FA, 6,
            "7fac141f4147b1db32ed2e0539f95c5e1d644579df6c927bc46831ee74e83279",
            "open_cfw_charger_get_soc",
        ),
        "replace_charger_get_is_charging": (
            0x004AD900, 8,
            "088459aac967667404120ae7e5b83c78aff05128a6b069810d3b5ff532eacd6a",
            "open_cfw_charger_get_is_charging",
        ),
    }
    patches = {
        row["name"]: row
        for row in overlay["patch_sites"]
        if row.get("name") in expected_patches
    }
    leaves = {
        row["function"]: row
        for row in overlay["relocated_leaves"]
        if row.get("source", {}).get("path") == candidate_rel
    }
    bound_state_leaves = {
        "open_cfw_charger_init_battery_sync",
        "open_cfw_charger_compare_and_update_soc",
        "open_cfw_charger_on_battery_level_changed",
        "open_cfw_charger_receive_battery_info_from_peer",
    }
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[name]["runtime_address"] != address
            or patches[name]["expected_size"] != size
            or patches[name]["expected_sha256"] != digest
            or patches[name]["branch"] != "b_w"
            or patches[name]["target_function"] != target
            or patches[name].get("profiles") != ["apple-clang"]
            for name, (address, size, digest, target) in expected_patches.items()
        )
        or set(leaves) != {target for *_, target in expected_patches.values()}
        or any(
            leaf["source"]["sha256"] != PINS[CANDIDATE]
            or leaf.get("profiles") != ["apple-clang"]
            or (leaf.get("allow_bound_static_data") is True)
            != (name in bound_state_leaves)
            for name, leaf in leaves.items()
        )
    ):
        raise AuditError("production charger-common routing changed")

    return {
        "surface": {
            "linked_functions": 14,
            "body_bytes": 2764,
            "owned_noncode_bytes": 220,
            "physical_bytes": 2984,
            "direct_bl_entry_sites": 25,
            "exterior_bl_entry_sites": 10,
            "direct_body_calls": 157,
            "stored_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "qualified_raw_overlap_windows": 6,
        },
        "abi": {
            "runtime_address": "0x20073b30",
            "runtime_bytes": 24,
            "peer_soc_offset": "0x08",
            "peer_charging_offset": "0x0c",
            "soc_offset": "0x10",
            "charging_offset": "0x14",
            "local_cache_address": "0x20074104",
            "local_cache_bytes": 8,
            "wire_message_bytes": 12,
            "service_id": "0x0105",
        },
        "behavior": {
            "aggregate_soc": "minimum of local and peer",
            "initial_retry_polls": [2, 4, 6, 8],
            "initial_timeout_poll": 16,
            "near_full_charge_debounce_samples": 4,
            "notify_message_id": 3,
            "response_message_id": 2,
            "request_message_id": 4,
        },
        "production": {
            "candidate": candidate_rel,
            "candidate_sha256": PINS[CANDIDATE],
            "production_routed": True,
            "ownership_bytes": 2400,
            "retained_stock_noncode_bytes": 220,
            "retained_stock_dead_body_bytes": 364,
            "bound_static_state": {
                "open_cfw_charger_charge_debounce": "0x20074f97",
                "open_cfw_charger_initial_sync_active": "0x20074f98",
                "open_cfw_charger_initial_sync_poll": "0x20074f1a",
                "open_cfw_charger_initial_sync_next": "0x20074f1c",
                "open_cfw_charger_initial_sync_retries": "0x20074f99",
            },
            "toolchain_profiles": ["apple-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
