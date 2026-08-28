#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/ux/ux_battery_sync/ux_battery_sync.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-ux-battery-sync-function-map.tsv"
CL = ROOT / "tools/manifests/g2-ux-battery-sync-closure.tsv"
PM = ROOT / "tools/manifests/g2-ux-battery-sync-provider-map.tsv"
PV = ROOT / "tools/manifests/g2-ux-battery-sync-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/ux_battery_sync.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FM: "044811cba6e8cf0ec894c29026b527e121db60db790fb468323dbc06aa89da6f",
    CL: "f59cc27f982357569fd6ee2ee12abd8ce954ffe4735cd83e01db74ad8043f449",
    PM: "e7f0d4fcfae0ce36a2bf4ad061aeb6881ea6bff225e38252a68e24ac70fc5be6",
    PV: "2e5b288abad5fe930b9783208320505280f60d7ed42c39fd0c99439f20aed0aa",
}
SOURCE_SIZE = 3686
SOURCE_SHA256 = "f0a5be0735deb2547ef5cb202eceef8909ecdd21b5e012f94b880527a2da1724"
PRODUCTION_FUNCTION = "open_cfw_ux_battery_sync_handler"
F = ((0x5F958C, 0x5F98D0),)
PHYS = (0x5F958C, 0x5F9924)
POOL = (0x5F98D0, 0x5F9924)
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CHARGER = {0x4AD53E, 0x4AD652}
RING = {0x4FF8E4, 0x4FF96C, 0x4FF98A, 0x4FF994}
CALLBACK = {0x5003E4}
EXTERNAL_TARGET_COUNTS = {
    0x43CE9E: 9, 0x43D0CE: 27, 0x43D574: 9,
    0x4AD53E: 2, 0x4AD652: 2,
    0x4FF8E4: 1, 0x4FF96C: 1, 0x4FF98A: 2, 0x4FF994: 2,
    0x5003E4: 2,
}
PATH_REFS = [
    0x5F95B6, 0x5F960E, 0x5F9674, 0x5F96B8, 0x5F96F8,
    0x5F9738, 0x5F9778, 0x5F9822, 0x5F98A2,
]
POOL_STRINGS = {
    0x5F98D0: "Invalid battery sync data: raw_data=%p, len=%d",
    0x5F98D4: "UX_BatterySyncHandler",
    0x5F98D8: r"D:\01_workspace\s200_ap510b_iar_git\app\ux\ux_battery_sync\ux_battery_sync.c",
    0x5F98DC: "ux.battery_sync",
    0x5F98E4: "UX_BatterySyncHandler: msg_id=%d, msg_len=%d, self_role=%d, peer_role=%d",
    0x5F98EC: "Received battery sync request",
    0x5F98F4: "Received battery sync response",
    0x5F98FC: "Received battery sync notification",
    0x5F9904: "Received battery sync request notify",
    0x5F990C: "Received ring battery sync request",
    0x5F9914: "Received ring battery sync update: soc=%d, charge=%d, soc_changed=%d, charge_changed=%d",
    0x5F991C: "Unknown battery sync message ID: %d",
}


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")

    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1:
        raise c.AuditError("function inventory changed")
    row = rows[0]
    start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
    raw = c._slice(blob, start, end)
    if (start, end) != F[0] or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
        raise c.AuditError("function body changed")
    instructions, calls, indirect = q._recover_function(blob, start, end)
    if c._uncovered(F[0], instructions):
        raise c.AuditError("function has uncovered bytes")
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if code != raw or len(instructions) != 341:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "9b571d10386710cf5c289cf4f70f9356aedcc64aec70fe271111152d7b002226":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    if sh(c._slice(blob, *PHYS)) != "b822ef2274c0a8a04637ffc8a25de3bc8d2e4af1693e5702aa140ed1c0242362":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, *POOL)) != "b29622cd4a216e257fa7db08e27b03c62904d3241c638f16de65c8809b7c3e29":
        raise c.AuditError("literal pool changed")
    if sh(c._slice(blob, 0x5F957C, PHYS[0])) != "52b273f9cb10f6db98525ded043bce8ebc5ca7964e9a1bfd0d85fc15960fb9dc":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x5F9934)) != "03f4eb12a2ff2e400f5e45e0e660f19aaf794fc74b44bf1e3ff6190dc94b3b1d":
        raise c.AuditError("following function boundary changed")

    calls.sort()
    external = Counter(target for _, target in calls)
    providers = (EASY, CHARGER, RING, CALLBACK)
    if len(calls) != 57 or c._pair_digest(calls) != "a76c5e373ff5a6be88905c9078a6ad73e3df4f88fc57cbf165ad9eeef4ffbb52":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS) or set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (45, 4, 6, 2):
        raise c.AuditError("provider accounting changed")

    interiors = set(range(start + 2, end, 2))
    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target == start:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if entries or strict:
        raise c.AuditError("unexpected direct or strict-interior entry")
    encoded = {start, start | 1}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != [(0x6A46F4, 0x5F958D)]:
        raise c.AuditError("stored callback entry changed")
    if struct.unpack("<I", c._slice(blob, 0x6A46F0, 0x6A46F4))[0] != 0x105:
        raise c.AuditError("service-record registration ID changed")

    if t.literal_references(blob, 0x5F98D8) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for pool_address, expected in POOL_STRINGS.items():
        target = struct.unpack("<I", c._slice(blob, pool_address, pool_address + 4))[0]
        if _cstring(blob, target) != expected:
            raise c.AuditError(f"literal string changed at 0x{pool_address:08x}")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sh(source) != SOURCE_SHA256:
        raise c.AuditError("production battery-sync source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = [item for item in overlay["relocated_leaves"]
              if item.get("function") == PRODUCTION_FUNCTION]
    if len(leaves) != 1:
        raise c.AuditError("production battery-sync leaf inventory changed")
    leaf = leaves[0]
    if (
        leaf["source"].get("path") != "components/apollo_main/core_overlay/ux_battery_sync.c"
        or leaf["source"].get("size") != SOURCE_SIZE
        or leaf["source"].get("sha256") != SOURCE_SHA256
        or leaf.get("strict_relocation_contract") is not True
        or leaf.get("profiles") != ["apple-clang"]
        or (leaf["expected"].get("size"), leaf["expected"].get("offset"),
            leaf["expected"].get("alignment")) != (158, 253428, 4)
        or len(leaf["relocations"]) != 11
    ):
        raise c.AuditError("production battery-sync source/placement changed")
    patches = [item for item in overlay["patch_sites"]
               if item.get("name") == "replace_ux_battery_sync_handler"]
    if len(patches) != 1 or (
        patches[0].get("runtime_address"), patches[0].get("expected_size"),
        patches[0].get("expected_sha256"), patches[0].get("branch"),
        patches[0].get("target_function"), patches[0].get("profiles"),
    ) != (
        0x5F958C, 836, "4e196cf085fd48c54bb65acfc14ef1b55f185f598ade74be448e663b1be2945a",
        "b_w", PRODUCTION_FUNCTION, ["apple-clang"],
    ):
        raise c.AuditError("production battery-sync patch routing changed")
    report = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "battery sync")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    region_names = {item["name"] for item in main["regions"]}
    if not {
        "ux_battery_sync_handler_source_replacement",
        "ux_battery_sync_retained_literal_pool",
        "ux_battery_sync_handler_source_alignment",
        "ux_battery_sync_handler_source_text",
    } <= region_names:
        raise c.AuditError("production battery-sync manifest regions changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"app\ux\ux_battery_sync\ux_battery_sync.c",
            "retained_symbol": "UX_BatterySyncHandler",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 1, "ghidra_discovered_functions": 1,
            "path_anchored_functions": 1, "raw_path_references": 9,
            "raw_path_referencing_functions": 1, "body_bytes": 836,
            "physical_bytes": 920, "outer_pool_bytes": 84,
            "reachable_instructions": 341, "direct_body_calls": 57,
            "internal_direct_body_calls": 0, "external_direct_body_calls": 57,
            "indirect_body_calls": 0, "direct_bl_entry_sites": 0,
            "stored_entry_pointers": 1,
        },
        "behavior": {
            "minimum_message_bytes": 12,
            "service_record_id": 0x105,
            "accepted_message_ids": [1, 2, 3, 4, 5, 6],
            "charger_request_role": 2,
            "charger_notify_role": 3,
            "ring_level_clamp": [0, 100],
            "ring_level_callback_key": 0,
            "ring_charging_callback_key": 1,
            "callbacks_only_on_change": True,
        },
        "provider_boundary": {
            "easylogger_calls": 45, "g2_charger_common_calls": 4,
            "g2_ring_battery_calls": 6, "g2_callback_manager_calls": 2,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "source_inventory_available": True,
            "source_functions": 1,
            "compiled_text_bytes": 158,
            "alignment_bytes": 2,
            "strict_relocations": 11,
            "stock_replaced_bytes": 836,
            "retained_literal_pool_bytes": 84,
            "diagnostic_logging": "stock EasyLogger observability omitted; six-message dispatch preserved",
            "software_functional_gap": False,
            "hardware_validation": "deferred by project direction",
            "hardware_blocker": "Authorized physical G2/peer battery-sync traffic, charger, or ring-state evidence is required for future qualification.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
