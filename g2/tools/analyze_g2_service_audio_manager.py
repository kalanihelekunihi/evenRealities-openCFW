#!/usr/bin/env python3
"""Fail-closed object/provider audit for platform/audio/service_audio_manager.c."""

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
FM = ROOT / "tools/manifests/g2-service-audio-manager-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-audio-manager-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-audio-manager-provider-map.tsv"
PINS = {
    FM: "dfe94d485d39023b11f708f3555bf0d0ee70fc2523c0cd68136b8020052c603a",
    CL: "cc2e732c7c60f0dd3c3fb9d05a941eb1a1a883d1b3de1024834c7906bcd4a6f6",
    PM: "2248e9a99011125fcde6aa40e5ac3c332c967deeeef5b646d57947af3a4c18c1",
}
F = (
    (0x54F364, 0x54F380), (0x54F380, 0x54F50E),
    (0x54F50E, 0x54F694), (0x54F694, 0x54F6F4),
    (0x54F6F4, 0x54F88E), (0x54F88E, 0x54F912),
    (0x54F912, 0x54F976),
)
PHYS = (0x54F364, 0x54FA24)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x43C0E4}
ROLE = {0x45A568, 0x509024}
AUDIO = {0x53CA10, 0x53CA32, 0x53CD40, 0x579FB8, 0x57A926, 0x57D6B4, 0x57D794}
TRANSPORT = {0x4651E0}
EXTERNAL_TARGET_COUNTS = {
    0x43C0E4: 1, 0x43CE9E: 16, 0x43D0CE: 48, 0x43D574: 16,
    0x45A568: 7, 0x4651E0: 1, 0x509024: 1, 0x53CA10: 2,
    0x53CA32: 2, 0x53CD40: 1, 0x579FB8: 2, 0x57A926: 1,
    0x57D6B4: 2, 0x57D794: 1,
}
PATH_REFS = [
    0x54F3B6, 0x54F412, 0x54F472, 0x54F4DC, 0x54F544, 0x54F5A0,
    0x54F600, 0x54F656, 0x54F6B8, 0x54F72C, 0x54F77A, 0x54F7CE,
    0x54F81C, 0x54F862, 0x54F8E2, 0x54F938,
]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _provenance() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
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
    _provenance()
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
    if anchored != 4 or len(body) != 1554 or sh(body) != "765778845b689e2b9efe344a4124ad234937dc9153fc1c42bab082fd19a84a34":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 595:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "7d834996a706d2a5363e6e84b6caba23af75be44ab7b610bcae8787576a2ef02":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, 0x54F976, 0x54FA24)
    if len(pool) != 174 or sh(pool) != "1acea8cf5453c5a5342f8d7594d1d7d031d4efdf776b732befb66c3de7cf3644":
        raise c.AuditError("object pool/alignment changed")
    if sh(c._slice(blob, *PHYS)) != "c1044f123eecf9afce8e604681f57055c72ac644379d00cf0d5f239ed9ea6a8f":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x54F338, 0x54F364)) != "acbfe656072dc4b0a9cb05c08c530fd893cfd5873903a2a2d71d7c9aebf6fe5c":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, 0x54FA24, 0x54FA34)) != "cb44e0be85e43faf40f449c9aa15da5c0d29830577219dff3597dd37968ec858":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, ROLE, AUDIO, TRANSPORT)
    if len(calls) != 112 or sum(target in starts for _, target in calls) != 11:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "1b63b834d7f5d096ea3bc99480e000cc06fa57aedf36e59f46fb3b3724ee04af":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (80, 1, 8, 11, 1):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 38 or c._pair_digest(entries) != "2683b5d9932445daeee8517f2117c75b6bfda17926232b081982a50e6a189d59":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != [(0x6A4604, 0x54F913)]:
        raise c.AuditError("stored common-data callback entry changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_audio_manager.c"
    if _cstring(blob, 0x6F5BFC) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x54F984) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x788710: "AUDM_appAcquire",
        0x788720: "AUDM_appRelease",
        0x77B3D4: "AUDM_SendSyncMsgToPeer",
        0x77B3EC: "AUDM_HandlePeerSyncMsg",
        0x78BE58: "AUDM_Init",
        0x770C48: "AUDM_common_data_handler",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("audio-manager symbol changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("service_audio_manager" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented audio manager entered overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\audio\service_audio_manager.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 7, "ghidra_discovered_functions": 5,
            "restored_functions": 2, "path_anchored_functions": 4,
            "raw_path_references": 16, "raw_path_referencing_functions": 6,
            "body_bytes": 1554, "physical_bytes": 1728,
            "outer_pool_and_alignment_bytes": 174, "reachable_instructions": 595,
            "direct_body_calls": 112, "internal_direct_body_calls": 11,
            "external_direct_body_calls": 101, "indirect_body_calls": 0,
            "direct_bl_entry_sites": 38, "stored_entry_pointers": 1,
        },
        "behavior": {
            "application_slots": 8,
            "valid_application_ids": [1, 2, 3, 4, 5, 6, 7],
            "hardware_ownership_role": 2,
            "hardware_enabled_on_first_acquire": True,
            "hardware_disabled_on_last_release": True,
            "common_data_frame_id": 0x10C,
            "peer_message_ids": [1, 2, 3, 4],
            "peer_messages_are_role_sensitive": True,
            "incoming_payload_dispatch_bytes": 1,
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 80,
            "iar_dlib_memset_calls": 1,
            "g2_product_role_and_system_calls": 8,
            "g2_audio_hardware_and_power_calls": 11,
            "g2_common_data_transport_calls": 1,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
