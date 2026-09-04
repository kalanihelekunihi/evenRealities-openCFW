#!/usr/bin/env python3
"""Fail-closed audit of the pathless G2 eAT bond/connect command pair."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
import apollo_overlay  # noqa: E402
from apollo_artifact_consistency import validate_apollo_main_artifacts  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-eat-bond-connect-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-eat-bond-connect-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-eat-bond-connect-provenance.tsv"
PINS = {
    FUNCTION_MAP: "3328e3fd8e9ae66381d9e64c1084c7305fd685dd5bc96a58a924a34824f58c58",
    CLOSURE: "cffe9e43c91aa2474f04e82d373c424c54855ae3c011b9be4e1b5f6d20a9c0e9",
    PROVENANCE: "61992537b8c3232f58b74d7c5e420ae4bf487f7317d6297596b52853c6f8f105",
}
PHYSICAL = (0x005A4FA4, 0x005A4FD0)
PHYSICAL_SHA256 = "32c7ffcc3bff0ac19951e69f662ee02c93ede84871d98e026f65c0db3f72c5d6"
POOL = (0x005A4FC6, 0x005A4FD0)
POOL_SHA256 = "b2a1b8bf327cbfd103f143d160bf78ce3b58c79a9eb8a24f4e5279a8dbb43cbc"
BODY_SHA256 = "3e9408b876d80efd450be92dcd28f209c51fba952fef4d93431198bad37f66d4"
BODY_CALL_SHA256 = "b255e6294e444b4780d2562269a98dbe638764b5fc4c99730cc013f0c7ac0e5e"
STORED_POINTER_SHA256 = "ee1e2e70557bbb7f17c33328e6f4c002d167d0afde14c5528283a5de01a53660"
COMMAND_RECORDS = (0x006C9260, 0x006C9280)
COMMAND_RECORDS_SHA256 = "0fe0547d78b235f3580e6956fd040824bf3248ffa7bafa6099f03db6a5d469e3"
COMMANDS = (
    (0, 0x007850E0, 0x005A4FA5, 0, "AT^CLEANBOND", "atCleanBondHandler"),
    (1, 0x0077E17C, 0x005A4FB5, 0, "AT^BLE_KEEPCONNECT", "atBleKeepConnectHandler"),
)
SOURCE = ROOT / "components/apollo_main/core_overlay/eat_bond_connect.c"
HEADER = ROOT / "components/apollo_main/core_overlay/eat_bond_connect.h"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (1799, "cea3207e5a8d5508a7a263665105968eeaf83367266ee9a38090d2ae0c48eebe")
HEADER_PIN = (204, "8e9091b99dfff22fd7d2f017ba60cdcc9eb4290eb83f7ebeede696323175d58c")
NAMES = (
    "open_cfw_eat_clean_bond_handler",
    "open_cfw_eat_keep_connect_handler",
)
PATCHES = ("replace_eat_bond_connect_01", "replace_eat_bond_connect_02")
FUNCTIONS = ((0x005A4FA4, 0x005A4FB4), (0x005A4FB4, 0x005A4FC6))
PROVIDER_TARGETS = (
    (0x004B46CE, 0x00541430),
    (0x0046F2DC, 0x00541430),
)
COMPILED_SIZES = (22, 24)
UNRELOCATED_SHA256 = (
    "52e148f9f2c6e0492bbcc24c8c208c7908ac5d1d8b2c83e72b970ea34bbd4e6a",
    "43fffe90be30ad4108f0b809ebc2d2509afafec65f9b627d33990b90496917a8",
)
ROUTES = {
    "apple-clang": {
        "path": ROOT / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        "report": ROOT / "components/apollo_main/core_overlay/build/build-report.json",
        "component": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        "targets": (0x004D0EC8, 0x004D0E68),
        "text": (
            "233cb9f79a29fb024fec5e534c4da010df2cca00a6bce52285a7c044b79fad7a",
            "bb3f1640ab69b2bef7649a3b9e6d629aa4bc6c975ed04da70bdc4c0a56bd9733",
        ),
    },
    "linux-clang": {
        "path": ROOT / "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
        "report": ROOT / "build/canonical-observation-g2-final97/linux-b/build-report.json",
        "component": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        "targets": (0x007BC2B8, 0x007BC2D0),
        "text": (
            "a111977ee85d1c76844fe070eeef5b6f34141eea8f09e0e60769ab0244927cc8",
            "c6663aed4361988c4ba5bda348b8274709ebf4c54e3d2fc75423ac5f464130ce",
        ),
    },
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


def validate_production() -> dict[str, object]:
    for path, pin, label in (
        (SOURCE, SOURCE_PIN, "source"),
        (HEADER, HEADER_PIN, "header"),
    ):
        payload = path.read_bytes()
        if (len(payload), sha256(payload)) != pin:
            raise AuditError(f"eAT bond/connect production {label} changed")

    config = json.loads(CONFIG.read_text())
    leaves = {
        item.get("function"): item
        for item in config.get("relocated_leaves", [])
        if item.get("function") in NAMES
    }
    if set(leaves) != set(NAMES):
        raise AuditError("eAT bond/connect production leaf inventory changed")
    for index, name in enumerate(NAMES):
        leaf = leaves[name]
        linux = leaf.get("toolchain_profiles", {}).get("linux-clang", {})
        for relocations in (leaf.get("relocations", []), linux.get("relocations", [])):
            if tuple(item.get("target_address") for item in relocations) != PROVIDER_TARGETS[index]:
                raise AuditError(f"eAT bond/connect provider closure changed: {name}")
        if (
            leaf.get("profiles") != ["apple-clang", "linux-clang"]
            or leaf.get("strict_relocation_contract") is not True
            or leaf.get("source", {}).get("sha256") != SOURCE_PIN[1]
            or leaf.get("expected", {}).get("size") != COMPILED_SIZES[index]
            or leaf.get("expected", {}).get("unrelocated_sha256")
            != UNRELOCATED_SHA256[index]
            or linux.get("expected", {}).get("size") != COMPILED_SIZES[index]
            or linux.get("expected", {}).get("unrelocated_sha256")
            != UNRELOCATED_SHA256[index]
            or linux.get("reviewed_version_prefix") != "Homebrew clang version 22.1.8"
        ):
            raise AuditError(f"eAT bond/connect production pins changed: {name}")

    patches = {
        item.get("name"): item
        for item in config.get("patch_sites", [])
        if item.get("name") in PATCHES
    }
    if set(patches) != set(PATCHES):
        raise AuditError("eAT bond/connect production patch inventory changed")
    for patch_name, function, bounds in zip(PATCHES, NAMES, FUNCTIONS):
        patch = patches[patch_name]
        if (
            patch.get("runtime_address") != bounds[0]
            or patch.get("expected_size") != bounds[1] - bounds[0]
            or patch.get("target_function") != function
            or patch.get("profiles") != ["apple-clang", "linux-clang"]
        ):
            raise AuditError(f"eAT bond/connect production patch changed: {patch_name}")

    component_manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    for start, _end in FUNCTIONS:
        offset = start - BASE
        owners = [
            region for region in component_manifest["regions"]
            if region.get("file_offset", -1) <= offset
            < region.get("file_offset", -1) + region.get("size", 0)
        ]
        if len(owners) != 1 or owners[0].get("address_status") not in {
            "generated_source_entry_replacement", "generated_source_data_replacement"
        }:
            raise AuditError("eAT bond/connect manifest entry ownership changed")

    for profile, route in ROUTES.items():
        component = route["path"].read_bytes()
        if len(component) != 3_956_672 or sha256(component) != route["component"]:
            raise AuditError(f"{profile} eAT bond/connect component changed")
        report = json.loads(route["report"].read_text())
        built = {
            item.get("extraction", {}).get("function"): item.get("extraction", {})
            for item in report.get("relocated_leaves", [])
            if item.get("extraction", {}).get("function") in NAMES
        }
        if set(built) != set(NAMES):
            raise AuditError(f"{profile} eAT bond/connect built leaf inventory changed")
        for index, (bounds, target, text_digest) in enumerate(
            zip(FUNCTIONS, route["targets"], route["text"])
        ):
            replacement = image_slice(component, bounds[0], bounds[1])
            if (
                apollo_overlay.decode_thumb_branch(bounds[0], replacement[:4], link=False)
                != target
                or replacement[4:] != b"\x00\xbf" * ((len(replacement) - 4) // 2)
            ):
                raise AuditError(f"{profile} eAT bond/connect redirect changed")
            extraction = built[NAMES[index]]
            if (
                extraction.get("size") != COMPILED_SIZES[index]
                or extraction.get("unrelocated_sha256") != UNRELOCATED_SHA256[index]
                or extraction.get("relocation_count") != 2
            ):
                raise AuditError(f"{profile} eAT bond/connect compiled text changed")
            if sha256(image_slice(component, target, target + COMPILED_SIZES[index])) != text_digest:
                raise AuditError(f"{profile} eAT bond/connect routed text changed")

    validate_apollo_main_artifacts(ROOT, AuditError, "production eAT bond/connect")
    return {
        "candidate": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "production_routed": True,
        "ownership_bytes": 34,
        "source_inventory_available": True,
        "source_functions": 2,
        "compiled_text_bytes": {"apple-clang": 46, "linux-clang": 46},
        "alignment_bytes": {"apple-clang": 2, "linux-clang": 2},
        "strict_relocations": 4,
        "stock_body_bytes_displaced": 34,
        "retained_stock_noncode_bytes": 10,
        "profiles_verified": ["apple-clang", "linux-clang"],
        "software_functional_gap": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_evidence_required": [
            "authorized bonded G2/peer trace proving AT^CLEANBOND deletes the persisted bond and permits a fresh pairing",
            "authorized connected G2/peer trace proving AT^BLE_KEEPCONNECT enables the intended retained connection policy",
        ],
        "hardware_operations": [],
    }


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
    if len(rows) != 2 or sum(map(len, bodies)) != 34:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")
    pool = image_slice(data, *POOL)
    if len(pool) != 10 or sha256(pool) != POOL_SHA256:
        raise AuditError("owned pool changed")
    if pool[:2] != b"\0\0" or struct.unpack_from("<II", pool, 2) != (0x007850D0, 0x0077553C):
        raise AuditError("pool layout changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical cluster changed")

    records = image_slice(data, *COMMAND_RECORDS)
    if sha256(records) != COMMAND_RECORDS_SHA256:
        raise AuditError("command records changed")
    for index, expected in enumerate(COMMANDS):
        words = struct.unpack_from("<IIII", records, index * 16)
        if words != expected[:4] or cstring(data, words[1]) != expected[4]:
            raise AuditError(f"command registration changed: {expected[4]}")
    if cstring(data, 0x007850D0) != "CLEANBOND+OK\r\n":
        raise AuditError("clean-bond response changed")
    if cstring(data, 0x0077553C) != "BLE_KEEPCONNECT+OK\r\n":
        raise AuditError("keep-connect response changed")

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
    expected_calls = [
        (0x005A4FA6, 0x004B46CE), (0x005A4FAC, 0x00541430),
        (0x005A4FB8, 0x0046F2DC), (0x005A4FBE, 0x00541430),
    ]
    if calls != expected_calls or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointers = [(0x006C9268, 0x005A4FA5), (0x006C9278, 0x005A4FB5)]
    if raw_addresses != expected_pointers or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    production = validate_production()

    return {
        "surface": {
            "linked_functions": 2,
            "body_bytes": 34,
            "owned_noncode_bytes": 10,
            "physical_bytes": 44,
            "direct_bl_entry_sites": 0,
            "direct_body_calls": 4,
            "stored_entry_pointers": 2,
            "strict_interior_ingress": 0,
        },
        "commands": [
            {
                "name": "AT^CLEANBOND", "handler": "atCleanBondHandler",
                "record_type": 0, "provider": "0x004b46ce", "return_value": 0,
            },
            {
                "name": "AT^BLE_KEEPCONNECT", "handler": "atBleKeepConnectHandler",
                "record_type": 1, "provider": "0x0046f2dc", "provider_argument": 1,
                "return_value": 0,
            },
        ],
        "lineage": {"retained_path": None, "source_partition_known": False},
        "production": production,
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 pathless eAT bond/connect audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
