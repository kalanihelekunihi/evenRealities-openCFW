#!/usr/bin/env python3
"""Fail-closed stock and production audit for service_ring_battery.c."""

import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as c
from apollo_artifact_consistency import validate_apollo_main_artifacts
import analyze_g2_dashboard_watchface_manager as d
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-service-ring-battery-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-ring-battery-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-ring-battery-provider-map.tsv"
PV = ROOT / "tools/manifests/g2-service-ring-battery-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/service_ring_battery.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FM: "1c3e5ed36c1382bc3adc62683ee8a26887f702a11c8b0be5fbfadbd0dce06bc0",
    CL: "9f7a02c1641aef2ffafbde435f32de8700fdd99950a053845086bd7a20409248",
    PM: "b9544563bc91ead78b1d39b6abd218b7cabf5880c8d09844249d2a24f1e7e4f1",
    PV: "a1cf5192e587eea8af8fa2e79e1fde2c12598d6112a78938ef48ebec2fcc0e95",
}
SOURCE_SIZE = 2978
SOURCE_SHA256 = "6385dc5658e91c1bfc6adb80b6133843c8afc8c885185f0a72218706c2e46060"
FUNCTIONS = (
    ("open_cfw_ring_battery_update", 48, 253588, 1),
    ("open_cfw_ring_battery_state_set", 26, 253636, 0),
    ("open_cfw_ring_battery_level_get", 12, 253664, 0),
    ("open_cfw_ring_battery_charging_get", 12, 253676, 0),
    ("open_cfw_ring_battery_request_from_peer", 36, 253688, 1),
)
PATCHES = (
    ("replace_ring_battery_update", 0x4FF8E4, 136, "df0945fd0d90e6d37c7889a53ae6b4f5391812efbf6fbc5c3fd7b06b347445d8", FUNCTIONS[0][0]),
    ("replace_ring_battery_state_set", 0x4FF96C, 30, "bb2242cfd158e7987b47e565ff5e23d94919930a2c47a550a90834c6a73218a6", FUNCTIONS[1][0]),
    ("replace_ring_battery_level_get", 0x4FF98A, 10, "d6c150df1d1d531a552fde16672d3f94c8da08facf6f7f6bff9d527b5508f053", FUNCTIONS[2][0]),
    ("replace_ring_battery_charging_get", 0x4FF994, 6, "c9d258eb43a37c428ed92141a7322f6c0e72920cbcd234f42581702f1944a902", FUNCTIONS[3][0]),
    ("replace_ring_battery_request_from_peer", 0x4FF99A, 170, "2f7d2bffbe3aea243c730a055e12d04e771aef98125c01a072b6a746f240878f", FUNCTIONS[4][0]),
)
F = ((0x4FF8E4, 0x4FF96C), (0x4FF96C, 0x4FF98A), (0x4FF98A, 0x4FF994),
     (0x4FF994, 0x4FF99A), (0x4FF99A, 0x4FFA44))
PHYS = (0x4FF8E4, 0x4FFA70)
POOL = (0x4FFA44, 0x4FFA70)
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x43C0E4}
TRANSPORT = {0x464D1C, 0x4651E0}


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("provider selection changed")

    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 5:
        raise c.AuditError("function inventory changed")
    starts, interiors, body, instructions, calls, indirect, anchored = set(), set(), b"", {}, [], [], 0
    for row, bounds in zip(rows, F):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = c._slice(blob, start, end)
        if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
            raise c.AuditError("body changed")
        recovered, direct, ind = d._recover_function(blob, start, end)
        if c._uncovered(bounds, recovered):
            raise c.AuditError("uncovered body")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        body += raw
        instructions.update(recovered)
        calls += direct
        indirect += ind
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(c._slice(blob, address, address + item.size)
                    for address, item in sorted(instructions.items()))
    if (anchored != 2 or len(body) != 352
            or sh(body) != "77f223b6c8cf312ccbbccb79e41c1b54fedc36cb3c2204902ba346d646485377"
            or code != body or len(instructions) != 146
            or c._instruction_digest(sorted((address, item.size) for address, item in instructions.items()))
            != "c634c54f4c510b068d1a98005d65162f483c7d8de17b91fe1ea6f0f1f0598287"
            or indirect):
        raise c.AuditError("instruction closure changed")
    if sh(c._slice(blob, *PHYS)) != "671ac6562c8d006acb17e39d816e19a2cd6c00887edac1cbeebb0364a36c459e":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, *POOL)) != "5b6f8497a0d814000f0d5eaea1d73ffb2ebb5244884a04b357514cbec88b30cd":
        raise c.AuditError("pool changed")
    if sh(c._slice(blob, 0x4FF7DC, PHYS[0])) != "f04b9f03dcdcb9940020eea098e1be9a8736eafbb4c2bc9f0d5055d020d49eb3":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x4FFAC8)) != "c17ac5e6e1670deebd0fa2388b5c777a837692ede5eccb76a20319bc8e8becb9":
        raise c.AuditError("following boundary changed")
    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, TRANSPORT)
    if (len(calls) != 19 or sum(target in starts for _, target in calls) != 0
            or c._pair_digest(calls) != "ab0009c7054662dc96cfe2e1966057a9e7e1dccf1bca45a9706544adc63f176f"
            or set(external) != set().union(*providers)
            or tuple(sum(external[target] for target in group) for group in providers) != (15, 2, 2)):
        raise c.AuditError("provider accounting changed")
    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if (len(entries) != 9
            or c._pair_digest(entries) != "e9d3a2205c922d079f8480f12d9fcfe482ea37b4eb69ed02e580a1ecbb94bab9"
            or strict):
        raise c.AuditError("BL entry topology changed")
    if t.literal_references(blob, 0x4FFA4C) != [0x4FF940, 0x4FF9DE, 0x4FFA1A]:
        raise c.AuditError("path references changed")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sh(source) != SOURCE_SHA256:
        raise c.AuditError("production source changed")
    overlay = json.loads(OVERLAY.read_text())
    names = {row[0] for row in FUNCTIONS}
    leaves = {item.get("function"): item for item in overlay["relocated_leaves"]
              if item.get("function") in names}
    if set(leaves) != names:
        raise c.AuditError("production leaf inventory changed")
    for name, size, offset, relocations in FUNCTIONS:
        leaf = leaves[name]
        if (leaf["source"].get("path") != "components/apollo_main/core_overlay/service_ring_battery.c"
                or leaf["source"].get("size") != SOURCE_SIZE
                or leaf["source"].get("sha256") != SOURCE_SHA256
                or leaf.get("profiles") != ["apple-clang"]
                or leaf.get("strict_relocation_contract") is not True
                or (leaf["expected"].get("size"), leaf["expected"].get("offset"),
                    leaf["expected"].get("alignment")) != (size, offset, 4)
                or len(leaf.get("relocations", [])) != relocations):
            raise c.AuditError(f"production leaf changed: {name}")
    patch_by_name = {item.get("name"): item for item in overlay["patch_sites"]}
    for name, address, size, digest, function in PATCHES:
        patch = patch_by_name.get(name)
        if patch is None or (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("branch"),
            patch.get("target_function"), patch.get("profiles"),
        ) != (address, size, digest, "b_w", function, ["apple-clang"]):
            raise c.AuditError(f"production patch changed: {name}")
    report = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "ring battery service")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    region_names = {item["name"] for item in main["regions"]}
    required = {name.removeprefix("replace_") + "_source_replacement" for name, *_ in PATCHES}
    required |= {
        "ring_battery_service_retained_literal_pool",
        "ring_battery_update_source_alignment", "ring_battery_update_source_text",
        "ring_battery_state_set_source_text", "ring_battery_level_get_source_alignment",
        "ring_battery_level_get_source_text", "ring_battery_charging_get_source_text",
        "ring_battery_request_from_peer_source_text",
    }
    if not required <= region_names:
        raise c.AuditError("production manifest regions changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image and production closure; corpus-independent",
        "identity": {"image_sha256": c.IMAGE_SHA256,
                     "retained_path": r"platform\service\ring_battery\service_ring_battery.c",
                     "embedded_third_party_definitions": []},
        "surface": {"linked_functions": 5, "ghidra_discovered_functions": 5,
                    "path_anchored_functions": 2, "body_bytes": 352,
                    "physical_bytes": 396, "outer_pool_bytes": 44,
                    "direct_body_calls": 19, "internal_direct_body_calls": 0,
                    "external_direct_body_calls": 19, "indirect_body_calls": 0,
                    "direct_bl_entry_sites": 9, "stored_entry_pointers": 0},
        "behavior": {"state_address": 0x20074F3A, "level_clamp": [0, 100],
                     "charging_normalized": True, "service_record_id": 0x105,
                     "update_message_id": 5, "request_message_id": 6,
                     "message_bytes": 12},
        "provider_boundary": {"easylogger_calls": 15, "iar_dlib_calls": 2,
                              "first_party_transport_calls": 2,
                              "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
                              "new_version_discriminator": False},
        "production": {"candidate": str(SOURCE.relative_to(ROOT)),
                       "production_routed": True, "source_inventory_available": True,
                       "source_functions": 5, "compiled_text_bytes": 134,
                       "alignment_bytes": 4, "strict_relocations": 2,
                       "stock_replaced_bytes": 352, "retained_literal_pool_bytes": 44,
                       "diagnostic_logging": "stock EasyLogger observability omitted; cached-state and service-record behavior preserved",
                       "software_functional_gap": False, "hardware_validation": "deferred by project direction",
                       "hardware_blocker": "Authorized physical paired-G2 service-record transport or ring battery-state evidence is required for future qualification."},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
