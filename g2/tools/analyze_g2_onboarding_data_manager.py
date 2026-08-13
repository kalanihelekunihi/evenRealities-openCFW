#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/onboarding/onboarding_data_manager.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-onboarding-data-manager-function-map.tsv"
CL = ROOT / "tools/manifests/g2-onboarding-data-manager-closure.tsv"
PM = ROOT / "tools/manifests/g2-onboarding-data-manager-provider-map.tsv"
PINS = {
    FM: "42f7d38678aabca8cd2c39e1e0c649d136a54ef6ca2e77e76263e5b5ce254e97",
    CL: "04d7af8c054a2b2d7616d85d500f99d5a7cfd5c7aca67ff478635926175caecd",
    PM: "b316841469d0abac44da1855ffea5143b885b10d6cc3a5bbe6d8fca627ff7dd5",
}
F = (
    (0x47E2D0, 0x47E320),
    (0x47E320, 0x47E3E6),
    (0x47E3E6, 0x47E470),
    (0x47E470, 0x47E4A6),
    (0x47E4A6, 0x47E51C),
    (0x47E51C, 0x47E58E),
    (0x47E58E, 0x47E60A),
)
PHYS = (0x47E2D0, 0x47E674)
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CMSIS = {0x4495E4, 0x4497B6, 0x44981C}
IAR = {0x43C0E4}
POLICY = {0x443484, 0x4434D0, 0x4487AC}
TRANSPORT = {0x465480}
KVDB = {0x4A777C, 0x4A77D2, 0x4A7832, 0x4A7838}
PROTOBUF = {0x4A8368}
EXTERNAL_TARGET_COUNTS = {
    0x43C0E4: 3,
    0x43CE9E: 7,
    0x43D0CE: 21,
    0x43D574: 7,
    0x443484: 1,
    0x4434D0: 1,
    0x4487AC: 1,
    0x4495E4: 1,
    0x4497B6: 1,
    0x44981C: 1,
    0x465480: 3,
    0x4A777C: 1,
    0x4A77D2: 1,
    0x4A7832: 1,
    0x4A7838: 1,
    0x4A8368: 1,
}
PATH_REFS = [0x47E37A, 0x47E3BA, 0x47E402, 0x47E448, 0x47E4EE, 0x47E560, 0x47E5DA]
ENTRIES = [
    (0x448F1E, 0x47E3E6),
    (0x468518, 0x47E470),
    (0x4687C6, 0x47E470),
    (0x46881E, 0x47E51C),
    (0x4688CA, 0x47E470),
    (0x468C1C, 0x47E58E),
    (0x49EC3C, 0x47E320),
    (0x49EC9A, 0x47E320),
    (0x4A7BBA, 0x47E2D0),
    (0x4A81A4, 0x47E2D0),
    (0x541934, 0x47E4A6),
]
FALSE_COMPRESSED_DATA_BL = [(0x5FE13C, 0x47E512)]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def provenance() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    deps = json.loads((ROOT / "tools/manifests/g2-third-party-dependency-closure.json").read_text())
    by_name = {row["family"]: row for row in deps["dependencies"]}
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"] != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c":
        raise c.AuditError("CMSIS_5 source selection changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise c.AuditError("FreeRTOS-Kernel source selection changed")
    if by_name["nanopb"]["selected_source_commit"] != "98bf4db69897b53434f3d0ba72e0a3ab1a902824":
        raise c.AuditError("nanopb source selection changed")
    if by_name["FlashDB"]["selected_source_commit"] != "714d6159e7e6afb267a3953756abca445c350e61":
        raise c.AuditError("FlashDB source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    provenance()
    with FM.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(F):
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
        calls.extend(direct)
        indirect.extend(dynamic)
        body += raw
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if anchored != 5 or len(body) != 826 or sh(body) != "ca1560d997fdc060d219ab3a70ad212e296aea62e641ffaa5140f457be91cae1":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 343:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "7de63e3cf2a66072e4ea0dac7ff6bafa8d2ae169bfc738df28de30e2a11e5e20":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, 0x47E60A, 0x47E674)
    if len(pool) != 106 or sh(pool) != "8c3b1348e9a2780b1c02fa2be5ec75ab04b071d4a6e41497c1cc1339b8a7766d":
        raise c.AuditError("object pool changed")
    if sh(c._slice(blob, *PHYS)) != "9489f7981e88888561acf50944360b7ad38fa15ea82248b919b2792cd4336ef6":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x47E2C0, PHYS[0])) != "857e5cd217db6d882b9d631c3ce831634d824cc60a802d184785413e14aa2be5":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x47E684)) != "9ab4d8ea824ffa388bf57b699d50cbb6f53452f7ed580a15995210a192517b79":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, CMSIS, IAR, POLICY, TRANSPORT, KVDB, PROTOBUF)
    if len(calls) != 52 or sum(target in starts for _, target in calls) != 0:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "114d6d816431c8964b535c7d5813d6bfbd9f0c703378a0b8cb8383040e94f99e":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS) or set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (35, 3, 3, 3, 3, 4, 1):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if entries != ENTRIES or c._pair_digest(entries) != "e049694adf90f181685403ce538b40ece30b0fc12267c2be1e2757e4144ced16":
        raise c.AuditError("direct entry topology changed")
    if strict != FALSE_COMPRESSED_DATA_BL:
        raise c.AuditError("strict-interior raw BL-like decodes changed")
    if sh(c._slice(blob, 0x5FE130, 0x5FE150)) != "f4a4fa29671447f525947d18c6a0b74d2efd927dbd8aacdeb7e4e2b1caae7dcb":
        raise c.AuditError("compressed-data false-positive window changed")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored:
        raise c.AuditError("stored entry pointer appeared")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\onboarding_data_manager.c"
    if cstring(blob, 0x6E8ECC) != expected_path or t.literal_references(blob, 0x47E620) != PATH_REFS:
        raise c.AuditError("retained path changed")
    for address, expected in {
        0x74BD4C: "onboarding_notify_wear_status_to_app",
        0x76E980: "OnboardingFlagSaveToFlash",
        0x762B70: "RPC_OnboardingFlagSendToPeer",
        0x762B90: "RPC_OnboardingFlagReplyToPeer",
        0x762BB0: "RPC_OnboardingProcessSyncToPeer",
    }.items():
        if cstring(blob, address) != expected:
            raise c.AuditError("retained symbol changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("onboarding_data_manager" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented onboarding manager entered overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"app\gui\onboarding\onboarding_data_manager.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 7,
            "ghidra_discovered_functions": 7,
            "restored_functions": 0,
            "path_anchored_functions": 5,
            "raw_path_references": 7,
            "raw_path_referencing_functions": 5,
            "body_bytes": 826,
            "physical_bytes": 932,
            "outer_pool_and_alignment_bytes": 106,
            "reachable_instructions": 343,
            "direct_body_calls": 52,
            "internal_direct_body_calls": 0,
            "external_direct_body_calls": 52,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 11,
            "stored_entry_pointers": 0,
            "raw_bl_like_compressed_data_decodes": 1,
            "strict_interior_code_ingress": 0,
        },
        "behavior": {
            "process_record_address": "0x200F4800",
            "process_record_bytes": 3,
            "accepted_common_data_types": [1, 2, 3],
            "type_one_updates_process_under_mutex": True,
            "flag_dirty_marker_address": "0x20074840",
            "flag_save_event_bit": 4,
            "peer_service_id": 0x10,
            "peer_role": 5,
            "peer_message_ids": [0x09, 0x0D, 0x0E],
            "phone_notification_command": 3,
            "phone_notification_tag": 5,
        },
        "provider_boundary": {
            "easylogger_calls": 35,
            "cmsis_freertos_calls": 3,
            "iar_memset_calls": 3,
            "g2_ota_role_display_policy_calls": 3,
            "g2_peer_transport_calls": 3,
            "closed_onboarding_kvdb_calls": 4,
            "closed_onboarding_protobuf_calls": 1,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "selected_nanopb_commit": "98bf4db69897b53434f3d0ba72e0a3ab1a902824",
            "selected_flashdb_commit": "714d6159e7e6afb267a3953756abca445c350e61",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
