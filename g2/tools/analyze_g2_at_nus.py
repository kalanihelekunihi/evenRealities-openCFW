#!/usr/bin/env python3
"""Fail-closed audit of the pathless G2 AT^NUS command handler."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-at-nus-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-at-nus-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-at-nus-provenance.tsv"
PINS = {
    FUNCTION_MAP: "ee8961ddbf0fdbb586de1347fdc2a1a6feeedea94ce8efda98509a0eb9f09dc6",
    CLOSURE: "0a191202b3b7fe192eb711c9afe080a9c36b553d02a2d71398f1d85d65ded097",
    PROVENANCE: "d61b78f04114852cd5821b17b50b255fd81d02ad319beebe0ff7b0609f7e3157",
}
BODY = (0x005A5520, 0x005A552C)
BODY_SHA256 = "6e4a3e381abcbd8e2cc20d13cf39e575c0165b96e20b8ec1b7a8da780ff1548a"
POOL = (0x005A552C, 0x005A5530)
POOL_SHA256 = "2567cbc76b274edabf68bf27abbc7935b2877b2e743e89d5ca54da297b43693d"
PHYSICAL = (0x005A5520, 0x005A5530)
PHYSICAL_SHA256 = "e7839a2d6e1af4863ff17f7010a3fc079e44f5565526b612458904f5c539ace8"
BODY_CALL_SHA256 = "762168582643167734fff76393883b4595b37bd5d6fdd0dc057b7b7779a42fce"
STORED_POINTER_SHA256 = "f3acea229f68518c9c55c083a8853ef9a4b7e7ce83354146aeb3b27da6e98408"
COMMAND_RECORD = (0x006C92A0, 0x006C92B0)
COMMAND_RECORD_SHA256 = "a31e85e096511bf4d8a97a11bbf5c6aa6e57ffe102282499a32fc9eec3fd4520"
COMMAND_RECORD_WORDS = (0, 0x0078CBC4, 0x005A5521, 0)
RESPONSE_ADDRESS = 0x0078A370


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
    if len(rows) != 1:
        raise AuditError("function inventory changed")
    row = rows[0]
    start = int(row["stock_start"], 0)
    end = int(row["stock_end_exclusive"], 0)
    body = image_slice(data, start, end)
    if (start, end) != BODY or len(body) != 12 or sha256(body) != BODY_SHA256:
        raise AuditError("handler body changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 4 or sha256(pool) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if struct.unpack("<I", pool)[0] != RESPONSE_ADDRESS:
        raise AuditError("response literal changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    record = image_slice(data, *COMMAND_RECORD)
    if sha256(record) != COMMAND_RECORD_SHA256:
        raise AuditError("command record changed")
    if struct.unpack("<IIII", record) != COMMAND_RECORD_WORDS:
        raise AuditError("command record layout changed")
    if cstring(data, COMMAND_RECORD_WORDS[1]) != "AT^NUS":
        raise AuditError("command name changed")
    if cstring(data, RESPONSE_ADDRESS) != "NUS+OK\r\n":
        raise AuditError("response changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    starts = {BODY[0]}
    interiors = set(range(BODY[0] + 2, BODY[1], 2))
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
    for site in range(BODY[0], BODY[1] - 3, 2):
        target = decoder._thumb_bl_target(data, site)
        if target is not None:
            calls.append((site, target))
    expected_call = [(0x005A5524, 0x00541430)]
    if calls != expected_call or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointer = [(0x006C92A8, 0x005A5521)]
    if raw_addresses != expected_pointer or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    candidate = "components/apollo_main/core_overlay/at_nus.c"
    expected_patches = {
        "replace_at_nus_handler_apple": (
            0x005A5520, 16, PHYSICAL_SHA256,
            "open_cfw_at_nus_handler", ["apple-clang"],
        ),
        "replace_at_nus_handler_linux": (
            0x005A5520, 16, PHYSICAL_SHA256,
            "open_cfw_at_nus_handler_linux", ["linux-clang"],
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
        if row.get("source", {}).get("path") == candidate
    }
    if (
        set(patches) != set(expected_patches)
        or any(
            patches[name]["runtime_address"] != address
            or patches[name]["expected_size"] != size
            or patches[name]["expected_sha256"] != digest
            or patches[name]["branch"] != "b_w"
            or patches[name]["target_function"] != target
            or patches[name].get("profiles") != profiles
            for name, (address, size, digest, target, profiles)
            in expected_patches.items()
        )
        or set(leaves) != {
            target for *_prefix, target, _profiles in expected_patches.values()
        }
        or any(
            leaf["source"]["sha256"]
            != "acc7eacdc2d064a62bfa9d4150ad5cf1b8e8130fee4616c0f2295bdba7469f06"
            or leaf.get("profiles") != [profile]
            or leaf.get("strict_relocation_contract") is not True
            for profile, leaf in (
                ("apple-clang", leaves.get("open_cfw_at_nus_handler", {})),
                ("linux-clang", leaves.get("open_cfw_at_nus_handler_linux", {})),
            )
        )
    ):
        raise AuditError("production AT^NUS routing changed")

    return {
        "surface": {
            "linked_functions": 1,
            "body_bytes": 12,
            "owned_noncode_bytes": 4,
            "physical_bytes": 16,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 1,
            "stored_entry_pointers": 1,
            "strict_interior_ingress": 0,
        },
        "command": {
            "name": "AT^NUS",
            "handler": "atNusHandler",
            "record_type": 0,
            "response": "NUS+OK\\r\\n",
            "output_provider": "0x00541430",
            "return_value": 1,
        },
        "lineage": {
            "retained_path": None,
            "exact_historical_symbol": None,
            "command_record": "[0x006c92a0,0x006c92b0)",
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/at_nus.c",
            "production_routed": True,
            "ownership_bytes": 16,
            "source_inventory_available": True,
            "historical_source_inventory_available": False,
            "toolchain_profiles": ["apple-clang", "linux-clang"],
            "relocated_leaves": sorted(leaves),
            "patch_sites": sorted(patches),
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_evidence_required": [
                "authorized G2 command trace proving AT^NUS response bytes "
                "and return behavior over the production eAT registry",
            ],
            "hardware_operations": [],
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pathless AT^NUS audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
