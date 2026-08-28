#!/usr/bin/env python3
"""Fail-closed object/provider audit for callback_mgr/callback_manager.c."""

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
FM = ROOT / "tools/manifests/g2-callback-manager-function-map.tsv"
CL = ROOT / "tools/manifests/g2-callback-manager-closure.tsv"
PM = ROOT / "tools/manifests/g2-callback-manager-provider-map.tsv"
PV = ROOT / "tools/manifests/g2-callback-manager-provenance.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/callback_manager.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PINS = {
    FM: "031e83ae4d5d76b36ef82768d4747d1399f521bee5520b4fd2f7b7fb2460b95a",
    CL: "f2a2d13cba0f80cddd94916ca80deab78081102dc58de4541995b10ebac7a371",
    PM: "f852dd3ba7e7ad36fd58cce9bf7aa3469d3bedca2c176491a85e9791df9a8ab2",
    PV: "1b1816a1d20381bd6726ed81ab84247a689971ea9f4d91fd857891ae2c45ad96",
}
SOURCE_SIZE = 6461
SOURCE_SHA256 = "a38f47ee52c54c6117716553a039917b15c8f8c7f2674d9d5d751d23cb4040f9"
PRODUCTION_FUNCTIONS = (
    "open_cfw_callback_mgr_create", "open_cfw_callback_mgr_delete",
    "open_cfw_callback_mgr_init", "open_cfw_callback_mgr_deinit",
    "open_cfw_callback_mgr_is_registered", "open_cfw_callback_mgr_register",
    "open_cfw_callback_mgr_unregister", "open_cfw_callback_mgr_notify",
)
PRODUCTION_PATCHES = tuple("replace_callback_mgr_" + name for name in (
    "create", "delete", "init", "deinit", "is_registered", "register",
    "unregister", "notify",
))
F = (
    (0x5100A0,0x5100FC),(0x5100FC,0x510108),(0x510108,0x5101AE),
    (0x5101AE,0x510218),(0x510218,0x510240),(0x510240,0x5103C4),
    (0x5103C4,0x510546),(0x5105BC,0x5105EE),
)
PHYS = (0x5100A0, 0x5105F0)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
HEAP = {0x474CD2, 0x474D16}
EXTERNAL_TARGET_COUNTS = {
    0x43CE9E:14, 0x43D0CE:42, 0x43D574:14,
    0x474CD2:1, 0x474D16:1,
}
ENTRIES = [
    (0x4ABCB6,0x510108),(0x4ABCC0,0x5101AE),(0x4ABD0E,0x510240),
    (0x4ABD5A,0x5103C4),(0x4ABD68,0x5105BC),(0x4AEA46,0x510108),
    (0x4AEA50,0x5101AE),(0x4AEA9E,0x510240),(0x4AEAEA,0x5103C4),
    (0x4AEAF8,0x5105BC),(0x4E1A4E,0x510108),(0x4E1A58,0x5101AE),
    (0x4E1AA6,0x510240),(0x4E1AF2,0x5103C4),(0x4E1B00,0x5105BC),
    (0x500386,0x510108),(0x500390,0x5101AE),(0x5003DE,0x510240),
    (0x5003EC,0x5105BC),(0x5101BC,0x5100FC),(0x5102D6,0x510218),
    (0x510322,0x5100A0),(0x5104B2,0x5100FC),
]
PATH_REFS = [
    0x5100C4,0x510126,0x51017A,0x5101E8,0x510262,0x5102A8,0x5102F4,
    0x510340,0x510392,0x5103E0,0x510420,0x510464,0x5104D6,0x51051A,
]
POOL_STRINGS = {
    0x510548:"Failed to allocate memory for callback node",
    0x51054C:"CALLBACK_MGR_CreateNode",
    0x510550:r"D:\01_workspace\s200_ap510b_iar_git\platform\service\callback_mgr\callback_manager.c",
    0x510554:"callback.mgr",
    0x51055C:"Invalid manager pointer",
    0x510560:"CALLBACK_MGR_Init",
    0x510570:"[%s] Callback manager deinitialized",
    0x510574:"CALLBACK_MGR_Deinit",
    0x51057C:"CALLBACK_MGR_Register",
    0x5105A0:"CALLBACK_MGR_Unregister",
    0x5105B4:"[%s] Callback not found",
}


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError("unterminated string")
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
    tlsf_note = (ROOT / "third_party/tlsf/README.openCFW.md").read_text()
    if "a1f743ffac0305408b39e791e0ffb45f6d9bc777" not in tlsf_note or "deff9ab509341f264addbd3c8ada533678591905" not in tlsf_note:
        raise c.AuditError("TLSF source interval changed")

    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 8:
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
        starts.add(start); interiors.update(range(start + 2, end, 2)); instructions.update(decoded)
        body += raw; calls.extend(direct); indirect.extend(dynamic)
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if anchored != 4 or len(body) != 1240 or code != body or sh(body) != "bc98a1f63adf8a2b7e0e2b1b29832249fb51a4d8d8a04a7eb2e0bd4ad940d3aa":
        raise c.AuditError("body closure changed")
    if len(instructions) != 506 or c._instruction_digest(sorted((a, i.size) for a, i in instructions.items())) != "2fca164c53ac0b0e3603a5475d3bea5aa16d189682904fe18c5eb1a2e5e8483d":
        raise c.AuditError("instruction topology changed")
    if indirect != [0x5105E4]:
        raise c.AuditError("dynamic callback site changed")

    pool = c._slice(blob, 0x510546, 0x5105BC)
    align = c._slice(blob, 0x5105EE, 0x5105F0)
    if sh(c._slice(blob, *PHYS)) != "1def5576e2fd57223ea0f79417044c1a96ceac4f05ced61ba4421abb97269ea9":
        raise c.AuditError("physical object changed")
    if sh(pool) != "65fff5bf26677150a7313480dace63cdb9c735b5359c55fa3dc558f64b92f2cf" or sh(align) != "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7":
        raise c.AuditError("noncode region changed")
    if sh(pool + align) != "c8fcd0c702f68165ac2008125b3c150f1327e7a7bf32e1f9d1280980b6e7c5e3":
        raise c.AuditError("noncode concatenation changed")
    if sh(c._slice(blob, 0x510090, PHYS[0])) != "fb7b61287a0b3cb9b00a2d01460ea5bf0924d34d6eff0c9465dc5ca1e8b10b8c":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x510600)) != "b727afabe787c29d985a90c32b7f8f3bd0cac3408d46ef7ba4b1a32d998676ef":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    if len(calls) != 76 or sum(target in starts for _, target in calls) != 4 or c._pair_digest(calls) != "5751635024d1cb80dab535cd742d31e810a8f59df8633e21e811ff3af97a11b7":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS) or set(external) != EASY | HEAP:
        raise c.AuditError("provider topology changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts: entries.append((address, target))
        elif target in interiors: strict.append((address, target))
    if entries != ENTRIES or c._pair_digest(entries) != "56c930a3fff5147b646ccc635ca46e9eddf34f148623bcefd09d6d2ac11a1179" or strict:
        raise c.AuditError("entry topology changed")
    encoded = starts | {start | 1 for start in starts}
    if any(struct.unpack_from("<I", blob, offset)[0] in encoded for offset in range(len(blob) - 3)):
        raise c.AuditError("unexpected stored entry")
    if t.literal_references(blob, 0x510550) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for pool_address, expected in POOL_STRINGS.items():
        target = struct.unpack("<I", c._slice(blob, pool_address, pool_address + 4))[0]
        if cstring(blob, target) != expected:
            raise c.AuditError("retained string changed")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sh(source) != SOURCE_SHA256:
        raise c.AuditError("production callback-manager source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = {
        item.get("function"): item
        for item in overlay["relocated_leaves"]
        if item.get("function") in PRODUCTION_FUNCTIONS
    }
    if set(leaves) != set(PRODUCTION_FUNCTIONS):
        raise c.AuditError("production callback-manager leaf inventory changed")
    expected_sizes = (22, 10, 22, 40, 70, 66, 130, 48)
    expected_offsets = (252916, 252940, 252952, 252976, 253016, 253088, 253156, 253288)
    if any(
        leaf["source"].get("path")
        != "components/apollo_main/core_overlay/callback_manager.c"
        or leaf["source"].get("size") != SOURCE_SIZE
        or leaf["source"].get("sha256") != SOURCE_SHA256
        or leaf.get("strict_relocation_contract") is not True
        or leaf.get("profiles") != ["apple-clang"]
        or leaf["expected"].get("size") != expected_size
        or leaf["expected"].get("offset") != expected_offset
        for leaf, expected_size, expected_offset in zip(
            (leaves[name] for name in PRODUCTION_FUNCTIONS),
            expected_sizes,
            expected_offsets,
        )
    ):
        raise c.AuditError("production callback-manager source/placement pins changed")
    if sum(len(leaves[name]["relocations"]) for name in PRODUCTION_FUNCTIONS) != 6:
        raise c.AuditError("production callback-manager relocation count changed")
    patches = {
        item.get("name"): item for item in overlay["patch_sites"]
        if item.get("name") in PRODUCTION_PATCHES
    }
    if set(patches) != set(PRODUCTION_PATCHES) or any(
        patches[name].get("target_function") != function
        for name, function in zip(PRODUCTION_PATCHES, PRODUCTION_FUNCTIONS)
    ):
        raise c.AuditError("production callback-manager patch routing changed")
    report = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "callback manager")
    manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    region_names = {item["name"] for item in manifest["regions"]}
    required_regions = {
        "callback_mgr_create_source_replacement",
        "callback_mgr_delete_source_replacement",
        "callback_mgr_init_source_replacement",
        "callback_mgr_deinit_source_replacement",
        "callback_mgr_is_registered_source_replacement",
        "callback_mgr_register_source_replacement",
        "callback_mgr_unregister_source_replacement",
        "callback_mgr_notify_source_replacement",
        "callback_mgr_retained_diagnostic_pool",
    }
    if not required_regions <= region_names:
        raise c.AuditError("production callback-manager manifest regions changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {"image_sha256": c.IMAGE_SHA256, "retained_path": r"platform\service\callback_mgr\callback_manager.c", "embedded_third_party_definitions": []},
        "surface": {
            "linked_functions":8,"ghidra_discovered_functions":7,"restored_functions":1,
            "path_anchored_functions":4,"raw_path_references":14,"body_bytes":1240,
            "physical_bytes":1360,"noncode_regions":2,"noncode_bytes":120,
            "reachable_instructions":506,"direct_body_calls":76,
            "internal_direct_body_calls":4,"external_direct_body_calls":72,
            "indirect_body_calls":1,"direct_bl_entry_sites":23,"stored_entry_pointers":0,
        },
        "behavior": {
            "manager_record_bytes":12,"node_bytes":8,"count_field_bytes":1,
            "duplicate_registration_returns_success":True,"list_insertion":"prepend",
            "deinit_frees_all_nodes":True,"notify_dynamic_call_site":"0x005105E4",
            "notify_arguments":2,"null_callbacks_skipped":True,
        },
        "provider_boundary": {
            "easylogger_calls":70,"source_owned_heap_wrapper_calls":2,
            "tlsf_compatible_interval":["a1f743ffac0305408b39e791e0ffb45f6d9bc777","deff9ab509341f264addbd3c8ada533678591905"],
            "direct_cmsis_freertos_calls":0,"bounded_registered_callback_sites":1,
            "new_version_discriminator":False,"private_generating_commit_recoverable":False,
        },
        "production": {
            "candidate": str(SOURCE.relative_to(ROOT)),
            "production_routed": True,
            "source_inventory_available": True,
            "source_functions": 8,
            "compiled_text_bytes": 408,
            "alignment_bytes": 14,
            "strict_relocations": 6,
            "stock_replaced_bytes": 1240,
            "retained_diagnostic_pool_bytes": 118,
            "diagnostic_logging": "stock EasyLogger observability omitted; callback-list functionality preserved",
            "software_functional_gap": False,
            "hardware_validation": "not-applicable",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
