#!/usr/bin/env python3
"""Fail-closed linked-object audit for the G2 distortion-test screen."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import apollo_overlay  # noqa: E402
from apollo_artifact_consistency import validate_apollo_main_artifacts  # noqa: E402

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pdt-distortion-test-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pdt-distortion-test-closure.tsv"
PINS = {
    FUNCTION_MAP: "8dd46d77d9b0ad5e2d576726d1e8cded5ab59d042c82c977a3f7e2f743041e90",
    CLOSURE: "1cf5e26e73c80daf25610f55ea4b69a7368dcd5da5e0844e0bcc4faf208903b8",
}
PHYSICAL = (0x005CF2B4, 0x005CF634)
PHYSICAL_SHA256 = "9b2057f67369aade287e9a2e4f52a58e3862bd2b609d6dd730bc32004870e583"
BODY_SHA256 = "adfd25e063b29828689ce9ce4eb77eef9452eb391de280a64b2dbd904df0f2d5"
POOL = (0x005CF606, 0x005CF634)
POOL_SHA256 = "8f588fad13260784069bb2bf8a61db63461c5bf091237e5a25bb14b82990345f"
ADJACENT_PREFIX = (0x005CF634, 0x005CF67E)
ADJACENT_PREFIX_SHA256 = "6c21b4628de75b80f6b74a11e3db2bf296c3d1b86a2313a4c58024f0a20a5cde"
DESCRIPTOR = (0x006A45C0, 0x006A45D0)
DESCRIPTOR_SHA256 = "9dd4097ead355a6e3c435ca39b34f466069d30030b2c36fb965a02c5b2712e10"
ENTRY_SHA256 = "d459fa33c57a62f42418a26574dbb96cb893ac961bddbd2dbfa6b2449a25fb0b"
BODY_CALL_SHA256 = "32c76a738b928371849dc3631ab264afd8176bc8ecc4f5df185023aecedcbb19"
STORED_SHA256 = "89f5c108e872bdc8823b0df803c209a17b36a972d716070801df106d61ed187a"
PATH_ADDRESS = 0x006E92BC
RETAINED_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\app\gui\PdtDistortionTest"
    r"\pdt_distortion_test.c"
)
ADJACENT_PATH_ADDRESS = 0x006F5314
ADJACENT_PATH = (
    r"D:\01_workspace\s200_ap510b_iar_git\app\gui\PdtGrayScreen"
    r"\pdt_gray_screen.c"
)
WORDS = {
    0x005CF608: 0x0074C88C,
    0x005CF60C: 0x0074C864,
    0x005CF610: PATH_ADDRESS,
    0x005CF614: 0x0078254C,
    0x005CF618: 0x007179B0,
    0x005CF61C: 0x2007487C,
    0x005CF620: 0x00769F58,
    0x005CF624: 0x00736AF4,
    0x005CF628: 0x200746DC,
    0x005CF62C: 0x00736B24,
    0x005CF630: 0x20003064,
    0x005CF790: ADJACENT_PATH_ADDRESS,
    0x006A45C0: 0x00000110,
    0x006A45C4: 0x005CF2E7,
    0x006A45C8: 0x005CF331,
    0x006A45CC: 0x20003064,
    0x006A45D0: 0x0000010F,
    0x006A45D4: 0x005CF635,
    0x006A45D8: 0x005CF67F,
    0x006A45DC: 0x20003080,
    0x00793734: 0x005CF32D,
    0x0079373C: 0x005CF67B,
    0x00793748: 0x005CF7EF,
}
STRINGS = {
    PATH_ADDRESS: RETAINED_PATH,
    ADJACENT_PATH_ADDRESS: ADJACENT_PATH,
    0x0074C88C: "PdtDistortionTest recv data len = %d",
    0x0074C864: "PdtDistortionTest_common_data_handler",
    0x0078254C: "pdt_distortion_test",
    0x007179B0: "[pdt_distortion_test]PdtDistortionTest recv data len = %d",
    0x00736AF4: "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1",
    0x00736B24: "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_2",
}
STORED = [
    (0x006A45C4, 0x005CF2E7),
    (0x006A45C8, 0x005CF331),
    (0x00793734, 0x005CF32D),
]

SOURCE = ROOT / "components/apollo_main/core_overlay/pdt_distortion_test.c"
HEADER = ROOT / "components/apollo_main/core_overlay/pdt_distortion_test.h"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (12825, "500b0df06e0d2cc224dd3c8f5ae706ea493d4be7560607669c5cc0b45cd8da92")
HEADER_PIN = (624, "11a988bac766c4acc675468a0ba1f2054e056af140d4843835f98fbb3b94a66f")
NAMES = (
    "open_cfw_pdt_distortion_zero_styles",
    "open_cfw_pdt_distortion_common_data_handler",
    "open_cfw_pdt_distortion_predicate",
    "open_cfw_pdt_distortion_screen_event",
)
PATCHES = tuple(f"replace_pdt_distortion_test_{index:02d}" for index in range(1, 5))
FUNCTIONS = ((0x005CF2B4, 0x005CF2E6), (0x005CF2E6, 0x005CF32C),
             (0x005CF32C, 0x005CF330), (0x005CF330, 0x005CF606))
RELOCATION_COUNTS = (4, 0, 0, 82)
RELOCATION_TARGET_SHA256 = (
    "8681c721db3ce47a492f97898914ce1762ccaf4c7b92d86e2e82b53642c5310e",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    "39330311d6bc0c01f6461323f3df3ee61d0fa7e39f877713b3bfe432cff60970",
)
COMPILED_SIZES = (46, 4, 4, 836)
UNRELOCATED_SHA256 = (
    "f5a2d07ecb6ee51a66307db6d56be4a8494637a85313fff444ea5c4382c77106",
    "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
    "64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb",
    "6a9b464ae1d02f6fb77516399509f0653f4c3bc60faae98fc193cfd71336c58f",
)
ROUTES = {
    "apple-clang": {
        "path": ROOT / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        "report": ROOT / "components/apollo_main/core_overlay/build/build-report.json",
        "component": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        "targets": (0x004BC2F4, 0x004D1104, 0x004D1100, 0x0044828C),
        "text": (
            "7fb60f28a132a3b2ed2226ddc22d29644c99b53981fe39c28e4bd065851b8993",
            "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
            "64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb",
            "bc2799d730c463c039ee80ad07d7a28d4ce223eb87cdf9a1838716a89c843ce5",
        ),
    },
    "linux-clang": {
        "path": ROOT / "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
        "report": ROOT / "build/canonical-observation-g2-final97/linux-b/build-report.json",
        "component": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        "targets": (0x007BBF3C, 0x007BBF6C, 0x007BBF70, 0x007BBF74),
        "text": (
            "74e584ee584561bc28275ec8eee1c663f8f8acd6eed3149cb6b1cb9d4d9d3c1b",
            "a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4",
            "64d23481cb6a254816fb9c4c9b22031f78ed0a6ece5a6b0f6849a3ee7f77a2bb",
            "9c7b713ff58ddd0af28d780c4ef5eea017850c2044c3c40b6977bc3e37b9226d",
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
    immediate = (
        (sign << 24) | (i1 << 23) | (i2 << 22)
        | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1)
    )
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def validate_production() -> dict[str, object]:
    for path, pin, label in ((SOURCE, SOURCE_PIN, "source"), (HEADER, HEADER_PIN, "header")):
        payload = path.read_bytes()
        if (len(payload), sha256(payload)) != pin:
            raise AuditError(f"distortion-test production {label} changed")

    config = json.loads(CONFIG.read_text())
    leaves = {item.get("function"): item for item in config["relocated_leaves"]
              if item.get("function") in NAMES}
    if set(leaves) != set(NAMES):
        raise AuditError("distortion-test production leaf inventory changed")
    for index, name in enumerate(NAMES):
        leaf = leaves[name]
        relocations = leaf.get("relocations", [])
        linux = leaf.get("toolchain_profiles", {}).get("linux-clang", {})
        linux_relocations = linux.get("relocations", [])
        expected_count = RELOCATION_COUNTS[index]
        if (leaf.get("profiles") != ["apple-clang", "linux-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or leaf.get("source", {}).get("sha256") != SOURCE_PIN[1]
                or len(relocations) != expected_count
                or len(linux_relocations) != expected_count
                or linux.get("reviewed_version_prefix") != "Homebrew clang version 22.1.8"):
            raise AuditError(f"distortion-test production pins changed: {name}")
        for observed in (relocations, linux_relocations):
            packed = b"".join(struct.pack("<I", item["target_address"]) for item in observed)
            if sha256(packed) != RELOCATION_TARGET_SHA256[index]:
                raise AuditError(f"distortion-test provider closure changed: {name}")

    patches = {item.get("name"): item for item in config["patch_sites"]
               if item.get("name") in PATCHES}
    if set(patches) != set(PATCHES):
        raise AuditError("distortion-test production patch inventory changed")
    for name, function, bounds in zip(PATCHES, NAMES, FUNCTIONS):
        patch = patches[name]
        if (patch.get("runtime_address") != bounds[0]
                or patch.get("expected_size") != bounds[1] - bounds[0]
                or patch.get("target_function") != function
                or patch.get("profiles") != ["apple-clang", "linux-clang"]):
            raise AuditError(f"distortion-test production patch changed: {name}")

    manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    for start, _end in FUNCTIONS:
        offset = start - BASE
        owners = [region for region in manifest["regions"]
                  if region.get("file_offset", -1) <= offset
                  < region.get("file_offset", -1) + region.get("size", 0)]
        if len(owners) != 1 or owners[0].get("address_status") not in {
                "generated_source_entry_replacement", "generated_source_data_replacement"}:
            raise AuditError("distortion-test manifest entry ownership changed")

    for profile, route in ROUTES.items():
        component = route["path"].read_bytes()
        if len(component) != 3956672 or sha256(component) != route["component"]:
            raise AuditError(f"{profile} distortion-test component changed")
        report = json.loads(route["report"].read_text())
        built = {item.get("extraction", {}).get("function"): item.get("extraction", {})
                 for item in report["relocated_leaves"]
                 if item.get("extraction", {}).get("function") in NAMES}
        if set(built) != set(NAMES):
            raise AuditError(f"{profile} distortion-test built leaf inventory changed")
        for index, (bounds, target, text_digest) in enumerate(
                zip(FUNCTIONS, route["targets"], route["text"])):
            replacement = image_slice(component, bounds[0], bounds[1])
            if (apollo_overlay.decode_thumb_branch(bounds[0], replacement[:4], link=False) != target
                    or replacement[4:] != b"\x00\xbf" * ((len(replacement) - 4) // 2)):
                raise AuditError(f"{profile} distortion-test redirect changed")
            extraction = built[NAMES[index]]
            if (extraction.get("size") != COMPILED_SIZES[index]
                    or extraction.get("unrelocated_sha256") != UNRELOCATED_SHA256[index]
                    or extraction.get("relocation_count") != RELOCATION_COUNTS[index]):
                raise AuditError(f"{profile} distortion-test compiled text changed")
            if sha256(image_slice(
                    component, target, target + COMPILED_SIZES[index])) != text_digest:
                raise AuditError(
                    f"{profile} distortion-test routed text changed: {NAMES[index]}"
                )

    validate_apollo_main_artifacts(ROOT, AuditError, "production distortion-test screen")
    return {
        "candidate": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "production_routed": True,
        "ownership_bytes": 850,
        "source_inventory_available": True,
        "source_functions": 4,
        "compiled_text_bytes": {"apple-clang": 890, "linux-clang": 890},
        "alignment_bytes": {"apple-clang": 2, "linux-clang": 2},
        "strict_relocations": 86,
        "stock_body_bytes_displaced": 850,
        "retained_stock_noncode_bytes": 46,
        "profiles_verified": ["apple-clang", "linux-clang"],
        "software_functional_gap": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_evidence_required": [
            "authorized G2 panel trace confirming the recovered 640x480 root, 574x206 frame at (0,50), nested flex layout, image asset, and both localized resource labels"
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
    if len(rows) != 4 or sum(map(len, bodies)) != 850:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("logical body digest changed")
    if sha256(image_slice(data, *POOL)) != POOL_SHA256:
        raise AuditError("literal pool changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if sha256(image_slice(data, *ADJACENT_PREFIX)) != ADJACENT_PREFIX_SHA256:
        raise AuditError("adjacent gray-screen prefix changed")
    if sha256(image_slice(data, *DESCRIPTOR)) != DESCRIPTOR_SHA256:
        raise AuditError("module descriptor changed")
    for address, expected in WORDS.items():
        actual = struct.unpack("<I", image_slice(data, address, address + 4))[0]
        if actual != expected:
            raise AuditError(f"word changed at 0x{address:08x}")
    for address, expected in STRINGS.items():
        if cstring(data, address) != expected:
            raise AuditError(f"retained string changed at 0x{address:08x}")
    path_words = []
    needle = struct.pack("<I", PATH_ADDRESS)
    offset = data.find(needle)
    while offset >= 0:
        path_words.append(BASE + offset)
        offset = data.find(needle, offset + 1)
    if path_words != [0x005CF610]:
        raise AuditError("retained-path pointer topology changed")

    tools_dir = str(ROOT / "tools")
    if tools_dir not in sys.path:
        sys.path.insert(0, tools_dir)
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
    if len(entry) != 4 or pair_digest(entry) != ENTRY_SHA256:
        raise AuditError("BL entry closure changed")
    exterior = [pair for pair in entry if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    if exterior or interior or entry_bw or interior_bw:
        raise AuditError("exterior/strict-interior/B.W closure changed")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 83 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("direct body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    raw_addresses = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        if value in encoded:
            raw_addresses.append((BASE + offset, value))
    if raw_addresses != STORED or pair_digest(raw_addresses) != STORED_SHA256:
        raise AuditError("stored entry/interior topology changed")

    return {
        "surface": {
            "linked_functions": 4,
            "body_bytes": 850,
            "literal_pool_bytes": 46,
            "physical_bytes": 896,
            "descriptor_bytes": 16,
            "direct_bl_entry_sites": 4,
            "exterior_bl_entry_sites": 0,
            "direct_body_calls": 83,
            "stored_entry_pointers": 3,
            "strict_interior_ingress": 0,
        },
        "registration": {
            "descriptor_address": "0x006a45c0",
            "screen_id": "0x00000110",
            "data_handler": "0x005cf2e7",
            "screen_event_handler": "0x005cf331",
            "state_address": "0x20003064",
            "predicate_pointer_cell": "0x00793734",
            "predicate": "0x005cf32d",
        },
        "behavior": {
            "data_handler_returns_zero": True,
            "predicate_returns_one": True,
            "construct_event": 2,
            "recognized_noop_event": 3,
            "root_dimensions": [640, 480],
            "root_global": "0x2007487c",
            "registry_root_field": "0x20003068",
            "object_create_calls": 4,
            "resource_ids": [
                "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_1",
                "ID_DASHBOARD_CALENDAR_BLUETOOTH_DISCONNECTED_2",
            ],
        },
        "boundary": {
            "next_object": "PdtGrayScreen/pdt_gray_screen.c",
            "next_handler": "0x005cf634",
            "adjacent_template_has_predicate": "0x005cf67a",
            "adjacent_descriptor": "0x006a45d0",
        },
        "production": validate_production(),
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 distortion-test screen audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
