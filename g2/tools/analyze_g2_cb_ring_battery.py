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
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-cb-ring-battery-function-map.tsv"
CL = ROOT / "tools/manifests/g2-cb-ring-battery-closure.tsv"
PM = ROOT / "tools/manifests/g2-cb-ring-battery-provider-map.tsv"
PINS = {
    FM: "b48263f7670992e341ee5ec0e5d320398059934570a2abf18d5bdf5af24dee35",
    CL: "db90e19077210eb488713ef7bf059375e4f1a1ef793039ac8627d65b01223742",
    PM: "3eb7fbd3b29fcf655b8795c32dcf37c4eb473b4886380d94ae7ec69cbf618131",
}
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

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("cb_ring_battery" in item.get("path", "").lower() for item in overlay["sources"]):
        raise c.AuditError("unimplemented facade entered overlay")
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
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
