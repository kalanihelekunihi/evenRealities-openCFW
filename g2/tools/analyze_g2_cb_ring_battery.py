#!/usr/bin/env python3
"""Fail-closed object/provider audit for callback_mgr/cb_ring_battery.c."""

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

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-cb-ring-battery-function-map.tsv"
CL = ROOT / "tools/manifests/g2-cb-ring-battery-closure.tsv"
PM = ROOT / "tools/manifests/g2-cb-ring-battery-provider-map.tsv"
PV = ROOT / "tools/manifests/g2-cb-ring-battery-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/cb_ring_battery.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FM: "b48263f7670992e341ee5ec0e5d320398059934570a2abf18d5bdf5af24dee35",
    CL: "9bb55be62d824cbbe3d94ed123b2d67a202c3918617443101d59858a105ed8ac",
    PM: "3eb7fbd3b29fcf655b8795c32dcf37c4eb473b4886380d94ae7ec69cbf618131",
    PV: "0a763c9f929aae87ed46d96ef62bddac7b733bdb7be80d06ee9e220117da742e",
}
SOURCE_SIZE = 3136
SOURCE_SHA256 = "dfade488fa37a47b8c242916ea7f6a89334339c3ebe181c26d6cb3a9b359f294"
PRODUCTION_FUNCTIONS = (
    "open_cfw_cb_ring_battery_forward", "open_cfw_cb_ring_battery_init",
    "open_cfw_cb_ring_battery_deinit", "open_cfw_cb_ring_battery_register",
    "open_cfw_cb_ring_battery_notify",
)
PRODUCTION_PATCHES = tuple("replace_cb_ring_battery_" + name for name in (
    "forward", "init", "deinit", "register", "notify",
))
F = (
    (0x500378, 0x500380), (0x500380, 0x50038C),
    (0x50038C, 0x500396), (0x500396, 0x5003E4),
    (0x5003E4, 0x5003F2),
)
PHYS = (0x500378, 0x500410)
POOL = (0x5003F2, 0x500410)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CONSUMER = {0x4E93E4}
CALLBACK = {0x510108, 0x5101AE, 0x510240, 0x5105BC}
EXTERNAL_TARGET_COUNTS = {
    0x43CE9E: 1, 0x43D0CE: 3, 0x43D574: 1,
    0x4E93E4: 1, 0x510108: 1, 0x5101AE: 1,
    0x510240: 1, 0x5105BC: 1,
}
ENTRIES = [
    (0x49E706, 0x500378), (0x49E738, 0x500396),
    (0x4FF8D6, 0x500380), (0x4FF8DE, 0x50038C),
    (0x5F9876, 0x5003E4), (0x5F9886, 0x5003E4),
]
STRINGS = {
    0x5003F4: "RING_BAT_INFO",
    0x5003FC: "Invalid ring callback function",
    0x500400: "CB_RING_BAT_RegisterCallback",
    0x500404: r"D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\cb_ring_battery.c",
    0x500408: "cb.ring_bat",
    0x50040C: "[cb.ring_bat]Invalid ring callback function",
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
    if len(rows) != 5:
        raise c.AuditError("function inventory changed")
    starts, interiors, instructions = set(), set(), {}
    body, calls, indirect, anchored = b"", [], [], 0
    for row, bounds in zip(rows, F):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = c._slice(blob, start, end)
        if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
            raise c.AuditError("function body changed")
        decoded, direct, dynamic = q._recover_function(blob, start, end)
        if c._uncovered(bounds, decoded):
            raise c.AuditError("function has uncovered bytes")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        instructions.update(decoded)
        body += raw
        calls.extend(direct)
        indirect.extend(dynamic)
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if anchored != 1 or code != body or len(body) != 122 or sh(body) != "f2aa9b9351507231abf4477d282430b6ad131534ce9cef690efbf517ed8ddb3c":
        raise c.AuditError("body closure changed")
    if len(instructions) != 50 or c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "d0f1e9497162807afa5f3a2b03e1cf5eede4281c0f2d4d1910c826f29b8ae37f":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    if sh(c._slice(blob, *PHYS)) != "44457e6f84125b2f1fdf9cc42b1fafae4cfe2d16db17f701f500ba1bec5f75bf":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, *POOL)) != "8dd85319d46353c7505c4abcc1b04d496e2d4d2d39fd0b97bfc068c3d53eae9c":
        raise c.AuditError("pool/alignment changed")
    if sh(c._slice(blob, 0x500368, PHYS[0])) != "16a726e68fb30f11a638003ca712471d0b557e708f2ad8ee5f0425bd93d7f181":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x500420)) != "9a8ab14bd34c472993696d525bf32319633e22137e1fff021848aad14270a44a":
        raise c.AuditError("following function boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, CONSUMER, CALLBACK)
    if len(calls) != 10 or c._pair_digest(calls) != "27bc822f805097bbf671870eb6bc107a2f0a64fc63ab8cced997111734e1b67c":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS) or set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (5, 1, 4):
        raise c.AuditError("provider accounting changed")

    decoded_entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            decoded_entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if decoded_entries != ENTRIES or c._pair_digest(decoded_entries) != "49dc1cab8d3e479a7b3e0b2350d9a4da4e205486bf80004e22f0b580bc042afe" or strict:
        raise c.AuditError("direct entry topology changed")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored:
        raise c.AuditError("unexpected stored entry")

    if t.literal_references(blob, 0x500404) != [0x5003B0]:
        raise c.AuditError("retained-path reference changed")
    if struct.unpack("<I", c._slice(blob, 0x5003F8, 0x5003FC))[0] != 0x20073F90:
        raise c.AuditError("callback-list address changed")
    for pool_address, expected in STRINGS.items():
        target = struct.unpack("<I", c._slice(blob, pool_address, pool_address + 4))[0]
        if _cstring(blob, target) != expected:
            raise c.AuditError(f"literal string changed at 0x{pool_address:08x}")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sh(source) != SOURCE_SHA256:
        raise c.AuditError("production ring-battery source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = {
        item.get("function"): item
        for item in overlay["relocated_leaves"]
        if item.get("function") in PRODUCTION_FUNCTIONS
    }
    if set(leaves) != set(PRODUCTION_FUNCTIONS):
        raise c.AuditError("production ring-battery leaf inventory changed")
    expected_sizes = (4, 20, 12, 22, 30)
    expected_offsets = (193488, 193492, 193512, 193524, 193548)
    if any(
        leaf["source"].get("path")
        != "components/apollo_main/core_overlay/cb_ring_battery.c"
        or leaf["source"].get("size") != SOURCE_SIZE
        or leaf["source"].get("sha256") != SOURCE_SHA256
        or leaf.get("strict_relocation_contract") is not True
        or leaf.get("profiles") != ["apple-clang"]
        or leaf["expected"].get("size") != expected_size
        or leaf["expected"].get("offset") != expected_offset
        for leaf, expected_size, expected_offset in zip(
            (leaves[name] for name in PRODUCTION_FUNCTIONS),
            expected_sizes, expected_offsets,
        )
    ):
        raise c.AuditError("production ring-battery source/placement pins changed")
    if sum(len(leaves[name]["relocations"]) for name in PRODUCTION_FUNCTIONS) != 5:
        raise c.AuditError("production ring-battery relocation count changed")
    patches = {
        item.get("name"): item for item in overlay["patch_sites"]
        if item.get("name") in PRODUCTION_PATCHES
    }
    if set(patches) != set(PRODUCTION_PATCHES) or any(
        patches[name].get("target_function") != function
        for name, function in zip(PRODUCTION_PATCHES, PRODUCTION_FUNCTIONS)
    ):
        raise c.AuditError("production ring-battery patch routing changed")
    report = json.loads(REPORT.read_text())
    if (
        report["overlay"]["size"], report["overlay"]["sha256"],
        report["component"]["size"], report["component"]["sha256"],
    ) != (
        197488, "a4c7927efe625a95e3bd928e5bb75b32c057837577dd9b9bf0cc3a5c19a42183",
        3720884, "026ba2cc0c5f4dd5ca052b630edd3bbbae8addd95b53f7bd0b16c0ebb40c316a",
    ):
        raise c.AuditError("production ring-battery build pins changed")
    manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    if manifest["provider"].get("size") != 3720884 or manifest["provider"].get("sha256") != report["component"]["sha256"]:
        raise c.AuditError("production ring-battery manifest provider changed")
    region_names = {item["name"] for item in manifest["regions"]}
    required_regions = {
        "cb_ring_battery_forward_source_replacement",
        "cb_ring_battery_init_source_replacement",
        "cb_ring_battery_deinit_source_replacement",
        "cb_ring_battery_register_source_replacement",
        "cb_ring_battery_notify_source_replacement",
        "cb_ring_battery_retained_pool",
        "cb_ring_battery_forward_source_text",
        "cb_ring_battery_init_source_text",
        "cb_ring_battery_deinit_source_text",
        "cb_ring_battery_register_source_text",
        "cb_ring_battery_notify_source_alignment",
        "cb_ring_battery_notify_source_text",
    }
    if not required_regions <= region_names:
        raise c.AuditError("production ring-battery manifest regions changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\callback_mgr\cb_ring_battery.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 5, "ghidra_discovered_functions": 1,
            "restored_functions": 4, "path_anchored_functions": 1,
            "raw_path_references": 1, "body_bytes": 122,
            "physical_bytes": 152, "outer_pool_and_alignment_bytes": 30,
            "reachable_instructions": 50, "direct_body_calls": 10,
            "internal_direct_body_calls": 0, "external_direct_body_calls": 10,
            "indirect_body_calls": 0, "direct_bl_entry_sites": 6,
            "stored_entry_pointers": 0,
        },
        "behavior": {
            "callback_list_address": 0x20073F90,
            "callback_type": "RING_BAT_INFO",
            "has_init": True, "has_deinit": True,
            "null_registration_rejected": True,
            "notification_uses_in_out_value_word": True,
            "notification_keys_observed_from_battery_sync": [0, 1],
        },
        "provider_boundary": {
            "easylogger_calls": 5, "g2_ring_battery_consumer_calls": 1,
            "g2_generic_callback_manager_calls": 4,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "source_inventory_available": True,
            "source_functions": 5,
            "compiled_text_bytes": 88,
            "alignment_bytes": 2,
            "strict_relocations": 5,
            "stock_replaced_bytes": 122,
            "retained_diagnostic_pool_bytes": 30,
            "diagnostic_logging": "stock EasyLogger observability omitted; callback forwarding and list operations preserved",
            "software_functional_gap": False,
            "hardware_validation": "not-applicable",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
