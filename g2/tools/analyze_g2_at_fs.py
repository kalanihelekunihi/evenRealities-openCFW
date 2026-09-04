#!/usr/bin/env python3
"""Fail-closed audit of the retained G2 eAT filesystem command module."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts


ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-at-fs-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-at-fs-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-at-fs-provenance.tsv"
PINS = {
    FUNCTION_MAP: "a4588cdb2d244e374423eb603d9b2debbc20bf1fb005c30ac16bff290061e742",
    CLOSURE: "697672a15835ff1014d9f71aefbcaf8b4d5cd4d2cfd8a8edfcf625844001740b",
    PROVENANCE: "4463d448352d283f02a8738d834d346e7a6b163eb2fded5b0fcf2c1b351e781e",
}
SOURCE = ROOT / "components/apollo_main/core_overlay/at_fs.c"
HEADER = ROOT / "components/apollo_main/core_overlay/at_fs.h"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (9331, "2ebcc8c5b60683408e3de0bc0937a38c71a1f182cfdf72254f8ddcdd0b0916b4")
HEADER_PIN = (279, "6b283718bb4706004fae16ce19836d60310e4728db209991b357bbe2712cfb86")
PRODUCTION_NAMES = (
    "open_cfw_at_fs_remove",
    "open_cfw_at_fs_list_recursive",
    "open_cfw_at_fs_list",
    "open_cfw_at_fs_mkdir",
)
COMPILED = {
    "apple-clang": (
        (64, "ab29bfb12d24671ff77af7a54ea8e04e50d226738c592afdce1d5d9a82816108"),
        (280, "500b3f2cf26c0721a8c920da11376396ad973d1fab223c330e2f2547007770fd"),
        (42, "509c147d4137233e77fa375cf2d8c01ea88a79b16b0d2c77e33860e38068eeee"),
        (72, "a0430039e9f75b0f6287c66013c88531bf9e52e37e291053483f7496fd47f1e9"),
    ),
    "linux-clang": (
        (64, "ab29bfb12d24671ff77af7a54ea8e04e50d226738c592afdce1d5d9a82816108"),
        (278, "1084b5bc2d38291c52a122391ba665520ac78784424e0989b3a8b4d0d1f88581"),
        (42, "509c147d4137233e77fa375cf2d8c01ea88a79b16b0d2c77e33860e38068eeee"),
        (72, "a0430039e9f75b0f6287c66013c88531bf9e52e37e291053483f7496fd47f1e9"),
    ),
}
RELOCATION_COUNTS = (3, 18, 3, 3)
ROUTES = {
    "apple-clang": {
        "path": ROOT / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        "report": ROOT / "components/apollo_main/core_overlay/build/build-report.json",
        "component": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        "targets": (0x004BA5C0, 0x0046A190, 0x004C4970, 0x004B98B8),
        "text": (
            "7c8181ae3986833c47653cee5cadaa952159a761781a44cc71c804af52982dc2",
            "92b8c0e9da77f41eb98899c5e22ed40f5415602d43e560b7ba54acbe10a4173f",
            "fe8f1dd51e7229aec0925ac9d1393fe9f2f1016eb466085517c024b363cc011b",
            "4b9e4ee985434a70e08a9a963f4131a778ffdf7458f006d63d748aa1c4f72913",
        ),
    },
    "linux-clang": {
        "path": ROOT / "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
        "report": ROOT / "build/canonical-observation-g2-final97/linux-a/build-report.json",
        "component": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        "targets": (0x007BC6B4, 0x007BC6F4, 0x007BC80C, 0x007BC838),
        "text": (
            "1ff77b72f60a04f76de7a244b985f0488ea9af97421e77e87a121fa6461d8170",
            "2af484499d63735e9d16d1ccba51cae95b635b6918fa717409c66dcc34ed4865",
            "12032ca2885e29a7fd62532cb5bae4375cf0931dcee5feee19c428f90270646d",
            "304aa501a21b05889137bfff91205b49d5bf3524986763d95085fa89b471eafc",
        ),
    },
}
PHYSICAL = (0x005A5530, 0x005A5720)
PHYSICAL_SHA256 = "ec0c3d2a695770371c9d68c14b3b1c0c1ddbcd8ee1e4724dbceaeb90185740ce"
POOL = (0x005A56D0, 0x005A5720)
POOL_SHA256 = "d5ee576a68ebf81d47bdf81cb4d1e2d55c659d08759d5e7ab3d4a0eb9c213200"
BODY_SHA256 = "6dac5f046c2c46f179431deae73ae7cbf6e77fc391a53542aa17a6033b10795a"
ENTRY_SHA256 = "969e8bb5e97b5ec69501779b7c8e548f547123c36be19466e0363523becff812"
BODY_CALL_SHA256 = "659c91baac5bfacdfc99e208e05597c342cc829c634649f95e5ddca4055faa36"
STORED_POINTER_SHA256 = "d322ac67b73ef7c3191cabe331b9e56948128842d2ef498ee48e3adbb04c437e"
COMMAND_RECORDS = (0x006C92B0, 0x006C92E0)
COMMAND_RECORDS_SHA256 = "d3c96fd8597a5e40134e051efe123fdc96858afb4ea22b1f65350ba75a54f624"
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_fs.c"
EXPECTED_RECORD_WORDS = (
    3, 0x0078CBFC, 0x005A5531, 0,
    3, 0x0078CC04, 0x005A567B, 0,
    3, 0x0078A394, 0x005A56A1, 0,
)
WORDS = {
    0x005A56D0: 0x0000002E,
    0x005A56D4: 0x00002E2E,
    0x005A56D8: 0x002F7325,
    0x005A56DC: 0x00000072,
    0x005A56E0: 0x0078CBDC,
    0x005A56E4: 0x0078CBCC,
    0x005A56E8: 0x00700854,
    0x005A56EC: 0x0078CBD4,
    0x005A56F0: 0x00785160,
    0x005A56F4: 0x200746A8,
    0x005A56F8: 0x00752394,
    0x005A56FC: 0x0078CBE4,
    0x005A5700: 0x00769B30,
    0x005A5704: 0x0078CBEC,
    0x005A5708: 0x007755FC,
    0x005A570C: 0x0078CBF4,
    0x005A5710: 0x0078A37C,
    0x005A5714: 0x20071AC8,
    0x005A5718: 0x0075E230,
    0x005A571C: 0x0078A388,
}
STRINGS = {
    0x0078CBFC: "AT^RM",
    0x0078CC04: "AT^LS",
    0x0078A394: "AT^MKDIR",
    0x0078CBDC: "RM %s",
    0x0078CBCC: "_atRM",
    0x00700854: RETAINED_PATH,
    0x0078CBD4: "at.fs",
    0x00785160: "[at.fs]RM %s",
    0x00752394: "^RM: remove file[%s] error(%d)\r\n",
    0x0078CBE4: "RM+OK\r\n",
    0x00769B30: "opendir fail, path: %s\r\n",
    0x0078CBEC: "D %s\r\n",
    0x007755FC: "F %s\t size:%ld(%ldKB)\r\n",
    0x0078CBF4: "LS+OK\r\n",
    0x0078A37C: "LS+ERR\r\n",
    0x0075E230: "Directory creation failed %s\r\n",
    0x0078A388: "MKDIR+OK\r\n",
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


def validate_production(function_rows: list[dict[str, str]]) -> dict:
    for path, expected, label in (
        (SOURCE, SOURCE_PIN, "source"),
        (HEADER, HEADER_PIN, "header"),
    ):
        payload = path.read_bytes()
        if (len(payload), sha256(payload)) != expected:
            raise AuditError(f"eAT filesystem production {label} changed")

    config = json.loads(CONFIG.read_text())
    leaves = {
        row.get("function"): row
        for row in config.get("relocated_leaves", [])
        if row.get("function") in PRODUCTION_NAMES
    }
    if set(leaves) != set(PRODUCTION_NAMES):
        raise AuditError("eAT filesystem production leaf inventory changed")
    for index, name in enumerate(PRODUCTION_NAMES):
        leaf = leaves[name]
        for profile, record in (
            ("apple-clang", leaf),
            ("linux-clang", leaf.get("toolchain_profiles", {}).get("linux-clang", {})),
        ):
            expected = record.get("expected", {})
            if (expected.get("size"), expected.get("unrelocated_sha256")) != COMPILED[profile][index]:
                raise AuditError(f"eAT filesystem production pins changed: {profile}/{name}")
            if len(record.get("relocations", [])) != RELOCATION_COUNTS[index]:
                raise AuditError(f"eAT filesystem relocation closure changed: {profile}/{name}")
        if (
            leaf.get("profiles") != ["apple-clang", "linux-clang"]
            or leaf.get("strict_relocation_contract") is not True
            or leaf.get("source", {}).get("sha256") != SOURCE_PIN[1]
        ):
            raise AuditError(f"eAT filesystem profile contract changed: {name}")

    if any(row.get("name", "").startswith("replace_at_fs_")
           for row in config.get("patch_sites", [])):
        raise AuditError("eAT filesystem must not collide with LC3 host bytes")
    bounds = [
        (int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0))
        for row in function_rows
    ]
    data_groups = [
        row for row in config.get("in_place_data", [])
        if row.get("symbol") == "open_cfw_at_fs_command_records"
    ]
    if len(data_groups) != 1:
        raise AuditError("eAT filesystem command-record route changed")
    data_group = data_groups[0]
    if (
        data_group.get("profiles") != ["apple-clang", "linux-clang"]
        or data_group.get("placements") != [{
            "name": "at_fs_command_records", "runtime_address": COMMAND_RECORDS[0],
            "size": 48, "source_offset": 0, "stock_sha256": COMMAND_RECORDS_SHA256,
        }]
    ):
        raise AuditError("eAT filesystem command-record placement changed")

    manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    for pointer_address in (0x006C92B8, 0x006C92C8, 0x006C92D8):
        offset = pointer_address - BASE
        owners = [
            row for row in manifest["regions"]
            if row.get("file_offset", -1) <= offset
            < row.get("file_offset", -1) + row.get("size", 0)
        ]
        if (
            len(owners) != 1
            or owners[0].get("address_status") != "generated_source_data_replacement"
            or owners[0].get("file_offset") != offset
            or owners[0].get("size") != 3
        ):
            raise AuditError("eAT filesystem manifest ownership changed")

    for profile, route in ROUTES.items():
        component = route["path"].read_bytes()
        if len(component) != 3_956_672 or sha256(component) != route["component"]:
            raise AuditError(f"{profile} eAT filesystem component changed")
        report = json.loads(route["report"].read_text())
        built = {
            row.get("extraction", {}).get("function"): row.get("extraction", {})
            for row in report.get("relocated_leaves", [])
            if row.get("extraction", {}).get("function") in PRODUCTION_NAMES
        }
        if set(built) != set(PRODUCTION_NAMES):
            raise AuditError(f"{profile} eAT filesystem build inventory changed")
        record_values = struct.unpack(
            "<12I", image_slice(component, *COMMAND_RECORDS)
        )
        expected_records = (
            3, 0x0078CBFC, route["targets"][0] | 1, 0,
            3, 0x0078CC04, route["targets"][2] | 1, 0,
            3, 0x0078A394, route["targets"][3] | 1, 0,
        )
        if record_values != expected_records:
            raise AuditError(f"{profile} eAT filesystem command ingress changed")
        for index, ((start, end), target, text_digest) in enumerate(
            zip(bounds, route["targets"], route["text"])
        ):
            extraction = built[PRODUCTION_NAMES[index]]
            size, unrelocated = COMPILED[profile][index]
            if (
                extraction.get("size") != size
                or extraction.get("unrelocated_sha256") != unrelocated
                or extraction.get("relocation_count") != RELOCATION_COUNTS[index]
                or sha256(image_slice(component, target, target + size)) != text_digest
            ):
                raise AuditError(f"{profile} eAT filesystem routed text changed")

    validate_apollo_main_artifacts(ROOT, AuditError, "production eAT filesystem")
    return {
        "candidate": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "production_routed": True,
        "ownership_bytes": 48,
        "changed_flash_bytes": 9,
        "source_inventory_available": True,
        "source_functions": 4,
        "compiled_text_bytes": {"apple-clang": 458, "linux-clang": 456},
        "alignment_bytes": {"apple-clang": 2, "linux-clang": 4},
        "strict_relocations": 27,
        "stock_body_bytes_displaced": 0,
        "command_record_bytes_replaced": 48,
        "stock_body_bytes_superseded_by_lc3_host": 416,
        "retained_stock_noncode_bytes": 80,
        "profiles_verified": ["apple-clang", "linux-clang"],
        "software_functional_gap": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_evidence_required": [
            "authorized G2 trace proving remove, recursive list, and mkdir against mounted production storage",
            "authorized fault trace proving readiness, provider-error, and inaccessible-directory responses",
        ],
        "hardware_operations": [],
    }


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
    if len(rows) != 4 or sum(map(len, bodies)) != 416:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *POOL)) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    records = image_slice(data, *COMMAND_RECORDS)
    if sha256(records) != COMMAND_RECORDS_SHA256:
        raise AuditError("AT command records changed")
    if struct.unpack("<" + "I" * 12, records) != EXPECTED_RECORD_WORDS:
        raise AuditError("AT command-record layout changed")
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
    expected_entry = [(0x005A5626, 0x005A55A0), (0x005A567C, 0x005A55A0)]
    if entry != expected_entry or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("direct entry closure changed")
    if interior or entry_bw or interior_bw:
        raise AuditError("strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 33 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    expected_pointers = [
        (0x006C92B8, 0x005A5531),
        (0x006C92C8, 0x005A567B),
        (0x006C92D8, 0x005A56A1),
    ]
    if raw_addresses != expected_pointers or pair_digest(raw_addresses) != STORED_POINTER_SHA256:
        raise AuditError("stored handler-pointer closure changed")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 416,
            "owned_noncode_bytes": 80,
            "physical_bytes": 496,
            "direct_bl_entry_sites": 2,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 33,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
        },
        "commands": {
            "names": ["AT^RM", "AT^LS", "AT^MKDIR"],
            "record_type": 3,
            "filesystem_ready_global": "0x200746a8",
            "filesystem_ready_value": 1,
            "remove_provider": "0x0047498c",
            "mkdir_provider": "0x004cfc5c",
            "list_skips": [".", ".."],
            "file_size_units": ["bytes", "integer KiB"],
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "exact_symbol": "_atRM",
            "command_records": "[0x006c92b0,0x006c92e0)",
        },
        "production": validate_production(rows),
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 eAT filesystem audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
