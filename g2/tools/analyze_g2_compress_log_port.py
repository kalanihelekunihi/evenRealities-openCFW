#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for compress_log/port."""

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
FM = ROOT / "tools/manifests/g2-compress-log-port-function-map.tsv"
CL = ROOT / "tools/manifests/g2-compress-log-port-closure.tsv"
PM = ROOT / "tools/manifests/g2-compress-log-port-provider-map.tsv"
PINS = {
    FM: "9d0f30c9c8b85dac7f4e3e17b86311512d53f97d2c6a7389f4a15cfc1bffffc1",
    CL: "9e6b840fdd53ab4b6206be9281cc0ddb954e38798fa9393a8fb713a80b261ce1",
    PM: "cbe8190851ae934782a61c6cdbf9a6f07ed0ffd4aaecb742cef3188fc0bfd184",
}
F = (
    (0x44A474, 0x44A488),
    (0x44A488, 0x44A4B0),
    (0x44A4B0, 0x44A530),
    (0x44A530, 0x44A5E0),
    (0x44A5E0, 0x44A622),
    (0x44A622, 0x44A63A),
    (0x44A63A, 0x44A71A),
    (0x44A71A, 0x44A78E),
    (0x44A798, 0x44A8B6),
    (0x44A8B6, 0x44A8FA),
    (0x44A904, 0x44A9AE),
    (0x44A9AE, 0x44A9B4),
)
PHYS = (0x44A474, 0x44AA2C)
DATA = ((0x44A78E, 0x44A798), (0x44A8FA, 0x44A904), (0x44A9B4, 0x44AA2C))
STARTS = {start for start, _ in F}
EASYLOGGER = {0x43D0CE, 0x43D574}
CORE = {0x43CE9E}
IAR = {0x44B728}
FILE_RUNTIME = {0x474550, 0x4745F4, 0x474634, 0x474682, 0x474814, 0x47498C}
EVENT_RUNTIME = {0x47697E, 0x476ACE}
EXTERNAL_TARGET_COUNTS = {
    0x43CE9E: 6,
    0x43D0CE: 18,
    0x43D574: 6,
    0x44B728: 2,
    0x474550: 6,
    0x4745F4: 5,
    0x474634: 1,
    0x474682: 3,
    0x474814: 2,
    0x47498C: 1,
    0x47697E: 1,
    0x476ACE: 2,
}
PATH_REFS = [0x44A678, 0x44A6E0, 0x44A882, 0x44A8CC, 0x44A922, 0x44A968]
STORED = [(0x44AA24, 0x44A8B7)]
SOURCE_OWNED_PATCHES = {
    0x474550: "open_cfw_file_open",
    0x4745F4: "open_cfw_file_close",
    0x474634: "open_cfw_file_read",
    0x474682: "open_cfw_file_write",
    0x474814: "open_cfw_file_seek",
    0x47498C: "open_cfw_file_remove",
    0x47697E: "open_cfw_event_loop_push_delayed",
    0x476ACE: "open_cfw_event_loop_remove_delayed",
}


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
    littlefs = json.loads((ROOT / "third_party/littlefs/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    if littlefs["upstream"]["selected_commit"] != "0494ce7169f06a734a7bd7585f49a9fa91fa7318":
        raise c.AuditError("littlefs source selection changed")
    if littlefs["upstream"]["selected_tag"] != "v2.10.1":
        raise c.AuditError("littlefs source-equivalent release changed")
    if littlefs["selection"]["exact_historical_checkout_proven"]:
        raise c.AuditError("littlefs historical provenance overclaim")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")


def _source_owned_provider_patches() -> None:
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    observed = {
        item.get("runtime_address"): item.get("target_function")
        for item in overlay["patch_sites"]
        if item.get("runtime_address") in SOURCE_OWNED_PATCHES
    }
    if observed != SOURCE_OWNED_PATCHES:
        raise c.AuditError("file/event provider production ownership changed")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    _provenance()
    _source_owned_provider_patches()
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
    code = b"".join(
        c._slice(blob, address, address + item.size)
        for address, item in sorted(instructions.items())
    )
    if anchored != 3 or len(body) != 1324 or sh(body) != "3a7ad30e3761b47953eda29a8237033c7209e950beffc605587f74b3e502ac42":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 526:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "2be142ae6dd88378871ba1176b8cb5286ace5a8c17da07dbd5b9178c0f352165":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    data = b"".join(c._slice(blob, *bounds) for bounds in DATA)
    if len(data) != 140 or sh(data) != "7785de649c5314a53367e5b74d679dbeca21dc39b01232c6e669ef3e52ea7d54":
        raise c.AuditError("outer data changed")
    if sh(c._slice(blob, *PHYS)) != "ecded42852da19e04b0e31b75c62e2a0fa3b596ee53f13bed94bde2eaad00411":
        raise c.AuditError("physical object changed")
    if c._slice(blob, 0x44A472, 0x44A474) != b"\0\0":
        raise c.AuditError("preceding alignment changed")
    if sh(c._slice(blob, 0x44AA2C, 0x44AA40)) != "556944e5a56e73a3f05cd03f5565628a6292aaee8d89df2a4d9db42ea6f33470":
        raise c.AuditError("following object boundary changed")
    if c._slice(blob, 0x44A78E, 0x44A798) != b"\0\0rb\0\0wb\0\0":
        raise c.AuditError("manager file modes changed")
    if c._slice(blob, 0x44A8FA, 0x44A904) != b"\0\0r+b\0w+b\0":
        raise c.AuditError("append file modes changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASYLOGGER, CORE, IAR, FILE_RUNTIME, EVENT_RUNTIME)
    if len(calls) != 68 or sum(target in starts for _, target in calls) != 15:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "24ac77cd8ad08248569a02b25321f89159eed8ce374aba0c3c545e4b41818597":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (24, 6, 2, 18, 3):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 23 or c._pair_digest(entries) != "bb3a1f3738e141705139ae867fe0151df0f4cd4ae700d51d6689821e0a46f087":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != STORED or c._pair_digest(stored) != "6d87e8aa28ef84b17790e0b1735d6584ffc1e58552295413ed9f7746488f3abd":
        raise c.AuditError("stored callback ingress changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\compress_log\port\compress_log_port.c"
    if _cstring(blob, 0x6DFCD4) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x44A9E0) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x76A134: "/log/compress_log_%d.bin",
        0x76A150: "/log/compress_manager.bin",
        0x775AAC: "Software_Version: %s\n",
        0x78A640: "2.2.6.10",
        0x76A16C: "_write_file_version_header",
        0x76A188: "compress_log_sync_to_files",
        0x748444: "compress_log_export_timeout_callback",
        0x76A1A4: "compress_log_export_notify",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("compact-log port string changed")
    if struct.unpack_from("<I", blob, 0x44A9C4 - c.BASE)[0] != 0x4C4D4752:
        raise c.AuditError("manager magic changed")
    if struct.unpack_from("<I", blob, 0x44AA28 - c.BASE)[0] != 120000:
        raise c.AuditError("export timeout changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("compress_log_port" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented compact-log port entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\compress_log\port\compress_log_port.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 12,
            "ghidra_discovered_functions": 11,
            "restored_functions": 1,
            "path_anchored_functions": 3,
            "raw_path_references": 6,
            "raw_path_referencing_functions": 4,
            "body_bytes": 1324,
            "physical_bytes": 1464,
            "outer_data_bytes": 140,
            "reachable_instructions": 526,
            "direct_body_calls": 68,
            "internal_direct_body_calls": 15,
            "external_direct_body_calls": 53,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 23,
            "stored_entry_pointers": 1,
        },
        "behavior": {
            "rotation_file_count": 5,
            "maximum_file_bytes": 512000,
            "manager_record_bytes": 12,
            "manager_magic": "0x4C4D4752",
            "version_header": "Software_Version: 2.2.6.10\n",
            "export_timeout_ticks": 120000,
        },
        "provider_boundary": {
            "easylogger_control_output_calls": 24,
            "closed_compact_log_core_calls": 6,
            "iar_dlib_calls": 2,
            "source_owned_file_runtime_calls": 18,
            "source_owned_delayed_callback_calls": 3,
            "littlefs_transitive_calls": 18,
            "all_file_runtime_entries_production_source_owned": True,
            "all_delayed_callback_entries_production_source_owned": True,
            "private_compact_hook_is_upstream_easylogger": False,
            "littlefs_version": "v2.10.1-equivalent",
            "littlefs_commit": "0494ce7169f06a734a7bd7585f49a9fa91fa7318",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
