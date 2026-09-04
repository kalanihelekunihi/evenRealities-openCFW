#!/usr/bin/env python3
"""Fail-closed linked-object/provider audit for cb_ble_status.c."""
from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as indirect_common
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts


AuditError = common.AuditError
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-cb-ble-status-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-cb-ble-status-closure.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-cb-ble-status-provider-map.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/cb_ble_status.c"
HEADER = ROOT / "components/apollo_main/core_overlay/cb_ble_status.h"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
APPLE_COMPONENT = (
    ROOT / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin"
)
LINUX_COMPONENT = (
    ROOT / "build/canonical-provider/linux-clang/apollo_main-final81/"
    "ota_s200_firmware_ota.bin"
)
INPUT_PINS = {
    FUNCTION_MAP: "31047dbd3d932216e849e4c26f4d75985ea487f9bf953cffb00cf747d6ae526b",
    CLOSURE: "247847ad6c5221da176705c12879df4e875850248bf5418542bec52329d2962a",
    PROVIDER_MAP: "b7eef415605655059e066e8346161c3767e7bd7a00e08537e7b5c0cdcf6b9d09",
}
RETAINED_PATH = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_ble_status.c"
PATH_RUN = 0x006E_6670
PATH_POINTER_CELLS = [0x004A_BD80]
FUNCTIONS = (
    (0x004A_BCC6, 0x004A_BD14),
    (0x004A_BD14, 0x004A_BD60),
    (0x004A_BD60, 0x004A_BD6E),
)
PHYSICAL = (0x004A_BCC6, 0x004A_BD90)
PHYSICAL_SHA256 = "327b225f115721e024b2569134079e342c890032e25305849275e0c8bf6d33cf"
BODY_SHA256 = "6576af9b125fa95782ddc3f87c937dc89f933eedd364e2416a2abb9473a42b0f"
INSTRUCTION_COUNT = 69
INSTRUCTION_DIGEST = "ab8a5e37f015c9190744a4d09b98ec7289deebdb5e3b04f60c4d8b909667a82b"
POOL = (0x004A_BD6E, 0x004A_BD90)
POOL_SHA256 = "d1a1217d460309537d12246b101b911e8365ff53f47b4b29da2f9fb7f3a0ccfd"
PRECEDING_TAIL = (0x004A_BCB0, 0x004A_BCC6)
PRECEDING_TAIL_SHA256 = "4837201a009d93d25625b7163da7b7abc213bdb635770ca58e0e5b9c9ce057ee"
FOLLOWING_HEAD = (0x004A_BD90, 0x004A_BDA4)
FOLLOWING_HEAD_SHA256 = "80c08774a0852a8bedd18ee767b2e92898b50212b321c2e4f4de71f0478fc781"
CALLS_DIGEST = "802349dd50c44016c113e4c8c05faa7d3d2b9b86907aece9e1b052c1968cb87b"
ENTRY_DIGEST = "2f6d7c4e87b8de53ab53f6a19105f52213c6c3e0760f974056c5c3579dbd6857"
ENTRIES = [
    (0x0046_8F9A, 0x004A_BCC6),
    (0x0046_907A, 0x004A_BD14),
    (0x0047_D63C, 0x004A_BD60),
    (0x0047_D80E, 0x004A_BD60),
    (0x0049_E720, 0x004A_BCC6),
    (0x0049_E9D4, 0x004A_BD14),
    (0x0058_2FF8, 0x004A_BD60),
    (0x005E_4566, 0x004A_BCC6),
    (0x005E_8A58, 0x004A_BCC6),
    (0x005E_8B8E, 0x004A_BD14),
]
EXTERNAL_TARGET_COUNTS = {
    0x0043_CE9E: 2,
    0x0043_D0CE: 6,
    0x0043_D574: 2,
    0x0051_0240: 1,
    0x0051_03C4: 1,
    0x0051_05BC: 1,
}
STRINGS = {
    PATH_RUN: RETAINED_PATH,
    0x0078_A568: "BLE_STATUS",
    0x0076_9FC8: "Invalid callback function",
    0x0075_E530: "CB_BLE_STATUS_RegisterCallback",
    0x0078_56D0: "cb.ble_status",
    0x0073_C7F4: "[cb.ble_status]Invalid callback function",
    0x0075_2718: "CB_BLE_STATUS_UnregisterCallback",
}
SOURCE_SIZE = 2259
SOURCE_SHA256 = "29dc354fed60f0aa56a29f40572081e8a8d9df0a8c1906de47c3a9e29d4f9aea"
HEADER_SIZE = 326
HEADER_SHA256 = "b1d861b8ab7b4c1e28870cf9160b3b511c8966e7ce9d9a242b7f59665094b6fa"
PRODUCTION_FUNCTIONS = (
    "open_cfw_cb_ble_status_register",
    "open_cfw_cb_ble_status_unregister",
    "open_cfw_cb_ble_status_notify",
)
PRODUCTION_PATCHES = tuple(
    f"replace_cb_ble_status_{index:02d}" for index in range(1, 4)
)
PROVIDER_TARGETS = (0x0051_0240, 0x0051_03C4, 0x0051_05BC)
PROFILE_ROUTES = {
    "apple-clang": {
        "component": APPLE_COMPONENT,
        "component_sha256": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        "entry_targets": (0x004D_0F28, 0x004D_0F54, 0x004D_0DC4),
        "text_sha256": (
            "31fc80e3f7638a4a4de8cc9adcc68296ad5f13e1c29c932eaa8afe627344a2bc",
            "bb060cb173e10e5806aacbd2cd3bce7911e5b7fbe919da9d35d6cabc5f607aa8",
            "df0faf9469d90248d3d129b9a717bfaa69bdba0300bd308e2f88778ee65ccc70",
        ),
        "configured_offsets": (373688, 373712, 373732),
    },
    "linux-clang": {
        "component": LINUX_COMPONENT,
        "component_sha256": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        "entry_targets": (0x007B_ADE4, 0x007B_ADFC, 0x007B_AE10),
        "text_sha256": (
            "a6c87f86c76512d66d3aca3333406171473bbc01d774475aa725caebba1793c2",
            "bf7e9b6465d5b0d0c661d2d8ed434d97e81c87cb43bc1e67c670f30e41694f6c",
            "b96bf7060f86912dc17814ab3f1af20176e1579cf6cf8cecff01e858fc333536",
        ),
        "configured_offsets": (158400, 158424, 158444),
    },
}


def _sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _stored_hits(blob: bytes, targets: set[int]) -> list[tuple[int, int]]:
    result = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        if value & 1 and (value & ~1) in targets:
            result.append((common.BASE + offset, value & ~1))
    return result


def _component_slice(component: bytes, start: int, end: int) -> bytes:
    first = start - common.BASE
    return component[first:first + end - start]


def _validate_production() -> dict[str, object]:
    source = SOURCE.read_bytes()
    header = HEADER.read_bytes()
    if len(source) != SOURCE_SIZE or _sha256(source) != SOURCE_SHA256:
        raise AuditError("production BLE-status source changed")
    if len(header) != HEADER_SIZE or _sha256(header) != HEADER_SHA256:
        raise AuditError("production BLE-status header changed")

    config = json.loads(OVERLAY.read_text())
    leaves = {
        item.get("function"): item
        for item in config["relocated_leaves"]
        if item.get("function") in PRODUCTION_FUNCTIONS
    }
    if set(leaves) != set(PRODUCTION_FUNCTIONS):
        raise AuditError("production BLE-status leaf inventory changed")
    sizes = (22, 20, 30)
    for index, (name, size, provider) in enumerate(zip(
        PRODUCTION_FUNCTIONS, sizes, PROVIDER_TARGETS
    )):
        leaf = leaves[name]
        if (
            leaf.get("profiles") != ["apple-clang", "linux-clang"]
            or leaf.get("strict_relocation_contract") is not True
            or leaf.get("source", {}).get("path")
                != "components/apollo_main/core_overlay/cb_ble_status.c"
            or leaf["source"].get("size") != SOURCE_SIZE
            or leaf["source"].get("sha256") != SOURCE_SHA256
            or leaf.get("expected", {}).get("size") != size
            or leaf["expected"].get("offset")
                != PROFILE_ROUTES["apple-clang"]["configured_offsets"][index]
            or len(leaf.get("relocations", [])) != 1
            or leaf["relocations"][0].get("target_address") != provider
        ):
            raise AuditError(f"production BLE-status Apple pins changed: {name}")
        linux = leaf.get("toolchain_profiles", {}).get("linux-clang", {})
        if (
            linux.get("reviewed_version_prefix")
                != "Homebrew clang version 22.1.8"
            or linux.get("expected", {}).get("size") != size
            or linux["expected"].get("offset")
                != PROFILE_ROUTES["linux-clang"]["configured_offsets"][index]
            or linux["expected"].get("sha256")
                != PROFILE_ROUTES["linux-clang"]["text_sha256"][index]
        ):
            raise AuditError(f"production BLE-status Linux pins changed: {name}")

    patches = {
        item.get("name"): item for item in config["patch_sites"]
        if item.get("name") in PRODUCTION_PATCHES
    }
    if set(patches) != set(PRODUCTION_PATCHES):
        raise AuditError("production BLE-status patch inventory changed")
    for name, function, bounds in zip(
        PRODUCTION_PATCHES, PRODUCTION_FUNCTIONS, FUNCTIONS
    ):
        patch = patches[name]
        if (
            patch.get("runtime_address") != bounds[0]
            or patch.get("expected_size") != bounds[1] - bounds[0]
            or patch.get("target_function") != function
            or patch.get("profiles") != ["apple-clang", "linux-clang"]
        ):
            raise AuditError(f"production BLE-status patch changed: {name}")

    report = json.loads(REPORT.read_text())
    report_leaves = {
        item.get("extraction", {}).get("function"): item
        for item in report["relocated_leaves"]
        if item.get("extraction", {}).get("function") in PRODUCTION_FUNCTIONS
    }
    if set(report_leaves) != set(PRODUCTION_FUNCTIONS):
        raise AuditError("built BLE-status leaf inventory changed")
    if any(
        report_leaves[name]["extraction"].get("sha256")
            != leaves[name]["expected"]["sha256"]
        or report_leaves[name]["placement"].get("offset")
            != leaves[name]["expected"]["offset"]
        for name in PRODUCTION_FUNCTIONS
    ):
        raise AuditError("built BLE-status Apple leaf pins changed")

    manifest = json.loads(MANIFEST.read_text())
    override = manifest["component_overrides"]["apollo_main"]
    required_regions = {
        "cb_ble_status_register_source_nop_fill",
        "cb_ble_status_unregister_source_nop_fill",
        "cb_ble_status_notify_source_nop_fill",
        "cb_ble_status_retained_diagnostic_pool",
    }
    regions = {item["name"]: item for item in override["regions"]}
    if not required_regions <= set(regions):
        raise AuditError("production BLE-status manifest regions changed")
    if any(
        regions[name].get("address_status")
            not in {"generated_source_data_replacement",
                    "generated_source_entry_replacement"}
        for name in required_regions
        if name != "cb_ble_status_retained_diagnostic_pool"
    ) or regions["cb_ble_status_retained_diagnostic_pool"].get(
        "address_status"
    ) != "official_blob":
        raise AuditError("production BLE-status manifest ownership changed")
    for start, _end in FUNCTIONS:
        offset = start - common.BASE
        owners = [
            item for item in override["regions"]
            if item.get("file_offset", -1) <= offset
            < item.get("file_offset", -1) + item.get("size", 0)
        ]
        if (
            len(owners) != 1
            or owners[0].get("address_status")
                != "generated_source_data_replacement"
        ):
            raise AuditError("post-link BLE-status entry ownership changed")

    for profile, route in PROFILE_ROUTES.items():
        component = route["component"].read_bytes()
        if len(component) != 3956672 or _sha256(component) != route[
            "component_sha256"
        ]:
            raise AuditError(f"{profile} BLE-status component changed")
        for index, ((start, end), target, size, digest, provider) in enumerate(zip(
            FUNCTIONS, route["entry_targets"], sizes,
            route["text_sha256"], PROVIDER_TARGETS
        )):
            replacement = _component_slice(component, start, end)
            if (
                apollo_overlay.decode_thumb_branch(
                    start, replacement[:4], link=False
                ) != target
                or replacement[4:] != b"\x00\xbf" * ((len(replacement) - 4) // 2)
            ):
                raise AuditError(
                    f"{profile} BLE-status stock redirect {index} changed"
                )
            text = _component_slice(component, target, target + size)
            if _sha256(text) != digest:
                raise AuditError(f"{profile} BLE-status text {index} changed")
            relocation_offset = (18, 16, 20)[index]
            if apollo_overlay.decode_thumb_branch(
                target + relocation_offset,
                text[relocation_offset:relocation_offset + 4],
                link=(index == 2),
            ) != provider:
                raise AuditError(
                    f"{profile} BLE-status provider route {index} changed"
                )

    validate_apollo_main_artifacts(ROOT, AuditError, "BLE-status callback")
    return {
        "candidate": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "production_routed": True,
        "source_inventory_available": True,
        "source_functions": 3,
        "compiled_text_bytes": 72,
        "alignment_bytes": 4,
        "strict_relocations": 3,
        "stock_replaced_bytes": 168,
        "retained_diagnostic_pool_bytes": 34,
        "post_link_suffix_relocation_verified": True,
        "profiles_verified": ["apple-clang", "linux-clang"],
        "diagnostic_logging": (
            "stock EasyLogger diagnostics omitted; callback semantics preserved"
        ),
        "software_functional_gap": False,
        "hardware_validation": "not-applicable",
        "hardware_operations": [],
    }


def analyze(image: Path = IMAGE) -> dict[str, object]:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or _sha256(blob) != common.IMAGE_SHA256:
        raise AuditError("official Apollo image changed")
    for path, expected in INPUT_PINS.items():
        if _sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise AuditError("EasyLogger source selection changed")

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    with PROVIDER_MAP.open(newline="", encoding="utf-8") as handle:
        providers = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 3 or len(providers) != 2 or sum(int(r["edges"].split()[0]) for r in providers) != 13:
        raise AuditError("function or provider inventory changed")

    starts, interiors, bodies, instructions, calls, indirect = set(), set(), [], {}, [], []
    anchored = 0
    for row, bounds in zip(rows, FUNCTIONS):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        if (start, end) != bounds:
            raise AuditError("function bounds changed")
        body = common._slice(blob, start, end)
        if len(body) != int(row["stock_bytes"]) or _sha256(body) != row["stock_sha256"]:
            raise AuditError(f"function changed: {row['function']}")
        recovered, function_calls, function_indirect = indirect_common._recover_function(blob, start, end)
        if common._uncovered(bounds, recovered):
            raise AuditError(f"function contains uncovered bytes: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        bodies.append(body)
        instructions.update(recovered)
        calls.extend(function_calls)
        indirect.extend(function_indirect)
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(common._slice(blob, a, a + i.size) for a, i in sorted(instructions.items()))
    if (
        anchored != 2 or len(code) != 168 or code != b"".join(bodies)
        or _sha256(code) != BODY_SHA256 or len(instructions) != INSTRUCTION_COUNT
        or common._instruction_digest(sorted((a, i.size) for a, i in instructions.items())) != INSTRUCTION_DIGEST
        or indirect
    ):
        raise AuditError("body, instruction, anchor, or indirect closure changed")
    if len(common._slice(blob, *PHYSICAL)) != 202 or _sha256(common._slice(blob, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical BLE-status callback object changed")
    if len(common._slice(blob, *POOL)) != 34 or _sha256(common._slice(blob, *POOL)) != POOL_SHA256:
        raise AuditError("BLE-status callback pool changed")
    for bounds, expected, label in (
        (PRECEDING_TAIL, PRECEDING_TAIL_SHA256, "preceding UI-object tail"),
        (FOLLOWING_HEAD, FOLLOWING_HEAD_SHA256, "following NVDB helper head"),
    ):
        if _sha256(common._slice(blob, *bounds)) != expected:
            raise AuditError(f"{label} changed")

    external_counts = Counter(target for _, target in calls if target not in starts)
    if len(calls) != 13 or common._pair_digest(calls) != CALLS_DIGEST or dict(external_counts) != EXTERNAL_TARGET_COUNTS:
        raise AuditError("direct body-call topology changed")
    decoded_entries, strict = [], []
    for address in range(common.BASE, common.BASE + len(blob) - 3, 2):
        target = thumb._thumb_bl_target(blob, address)
        if target in starts:
            decoded_entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if decoded_entries != ENTRIES or common._pair_digest(decoded_entries) != ENTRY_DIGEST or strict:
        raise AuditError("direct entry or interior topology changed")
    if _stored_hits(blob, starts) or _stored_hits(blob, interiors):
        raise AuditError("stored entry or interior pointer appeared")

    for address, expected in STRINGS.items():
        if common._c_string(blob, address) != expected:
            raise AuditError(f"string changed at 0x{address:08x}")
    path_word = struct.pack("<I", PATH_RUN)
    hits, cursor = [], blob.find(path_word)
    while cursor >= 0:
        hits.append(common.BASE + cursor)
        cursor = blob.find(path_word, cursor + 1)
    if hits != PATH_POINTER_CELLS or thumb.literal_references(blob, PATH_POINTER_CELLS[0]) != [0x004A_BCE0, 0x004A_BD2E]:
        raise AuditError("retained-path reference topology changed")
    if struct.unpack_from("<I", blob, 0x004A_BD74 - common.BASE)[0] != 0x2007_3F6C:
        raise AuditError("BLE_STATUS callback-list address changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only; no hardware or flash operation",
        "identity": {
            "image_sha256": common.IMAGE_SHA256,
            "retained_path": RETAINED_PATH,
            "physical_interval": [*PHYSICAL],
            "physical_sha256": PHYSICAL_SHA256,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 3,
            "ghidra_discovered_functions": 3,
            "additional_recovered_functions": 0,
            "path_anchored_functions": 2,
            "body_bytes": 168,
            "reachable_instruction_bytes": 168,
            "outer_pool_regions": 1,
            "outer_pool_bytes": 34,
            "physical_bytes": 202,
            "direct_bl_entry_sites": 10,
            "external_direct_bl_entry_sites": 10,
            "direct_body_calls": 13,
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": 13,
            "indirect_body_calls": 0,
            "stored_entry_pointers": 0,
            "strict_interior_raw_bl_decodes": 0,
            "unrecovered_direct_object_targets": 0,
        },
        "behavior": {
            "callback_list_address": 0x2007_3F6C,
            "null_registration_rejected": True,
            "null_unregistration_rejected": True,
            "notify_uses_in_out_status_word": True,
        },
        "provider_boundary": {
            "direct_external_calls": 13,
            "easylogger_calls": 10,
            "first_party_callback_manager_calls": 3,
            "cmsis_freertos_calls": 0,
            "cordio_calls": 0,
            "iar_dlib_calls": 0,
            "new_version_discriminator": False,
        },
        "production": _validate_production(),
    }


def main() -> int:
    print(json.dumps(analyze(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
