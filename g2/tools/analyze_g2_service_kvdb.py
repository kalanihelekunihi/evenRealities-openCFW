#!/usr/bin/env python3
"""Fail-closed object/provider and boot-counter audit for flashDB/kv/service_kvdb.c."""

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
import analyze_g2_flashdb as fdb
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-service-kvdb-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-kvdb-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-kvdb-provider-map.tsv"
PINS = {
    FM: "2cc29379bc966b452a0e375f3804319a5298f1fff18c3b925e2d4077937f3bc9",
    CL: "3eef0a4efca2260713924f8aa5307c23b97d082c9993baced89909fb577156a9",
    PM: "7217ea96f6e58671d1e1aeb536c8ea289edc959af7b530fa2d2e40f22c2725e2",
}
F = (
    (0x4D9530, 0x4D956C), (0x4D956C, 0x4D957E),
    (0x4D957E, 0x4D9590), (0x4D9590, 0x4D959C),
    (0x4D959C, 0x4D96D8), (0x4D96D8, 0x4D9A84),
    (0x4D9A84, 0x4D9A98),
)
PHYS = (0x4D9530, 0x4D9B34)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x439BE4}
ONBOARDING = {0x4A77D2, 0x4A7846}
DB_ADAPTER = {0x54116E, 0x5411F2, 0x541232}
FLASHDB = {0x5450A4, 0x545320, 0x5453FE}
EXTERNAL_TARGET_COUNTS = {
    0x439BE4: 1, 0x43CE9E: 13, 0x43D0CE: 39, 0x43D574: 13,
    0x4A77D2: 1, 0x4A7846: 1, 0x54116E: 5, 0x5411F2: 3,
    0x541232: 4, 0x5450A4: 1, 0x545320: 2, 0x5453FE: 1,
}
PATH_REFS = [
    0x4D95F8, 0x4D968C, 0x4D9706, 0x4D97A2, 0x4D97EC,
    0x4D983A, 0x4D988A, 0x4D98D4, 0x4D9924, 0x4D9974,
    0x4D99B6, 0x4D9A02, 0x4D9A56,
]
MIGRATION_TABLE = (0x746D20, 0x746D4C)
MIGRATION_TARGETS = (
    0x4AECB8, 0x492508, 0x492422, 0x4922F8, 0x5D9B82,
    0x4AEB34, 0x49B028, 0x4B03F4, 0x58562C, 0x49AEA4,
    0x49AD20,
)
ZERO_RECORD = (0x75D3C8, 0x75D3E0)
ZERO_RANGE = (0x20004558, 0x20075048)
BOOT_COUNT_ADDRESS = 0x20074988


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _provenance_and_configuration(blob: bytes) -> dict:
    provenance = json.loads((ROOT / "third_party/flashdb/PROVENANCE.json").read_text())
    if (
        provenance["upstream"]["selected_commit"]
        != "714d6159e7e6afb267a3953756abca445c350e61"
        or provenance["upstream"].get("selected_tag") != "2.1.1"
    ):
        raise c.AuditError("FlashDB source selection changed")
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")
    findings = fdb.audit(blob)
    sysenv = next(item for item in findings["default_kv_tables"] if item["database"] == "sysenv")
    binding = next(item for item in findings["database_bindings"] if item["index"] == 0)
    boot = next(item for item in sysenv["nodes"] if item["key"] == "kvbooCount")
    if (
        findings["version"] != "2.1.1"
        or binding != {"index": 0, "database_name": "sysenv", "partition_name": "kvdb"}
        or sysenv["address"] != 0x2000372C
        or len(sysenv["nodes"]) != 12
        or boot["value_address"] != BOOT_COUNT_ADDRESS
        or findings["first_party_policy"]["sysenv_magic"]
        != {"key": "kvMagic", "value": 0x5A000020}
    ):
        raise c.AuditError("authenticated sysenv/kvdb configuration changed")
    return findings


def _startup_zero_proof(blob: bytes) -> None:
    gate = c._slice(blob, 0x5E4228, 0x5E4232)
    if gate.hex() != "06480749086001207047" or sh(gate) != "bee8bcf07546d7e7b549b10cfe4fc3c6519a6a49dc357d32179df469f5a8e36c":
        raise c.AuditError("startup zero gate changed")
    if t._thumb_bl_target(blob, 0x5E4294) != 0x5E4228 or t._thumb_bl_target(blob, 0x5E429C) != 0x5E42B4:
        raise c.AuditError("reset-to-scatter call path changed")
    record = c._slice(blob, *ZERO_RECORD)
    if sh(record) != "2a52162870b1f1b036f1769e75dabcf475f17eb6c37c85ffcabcb9dcfd064e15":
        raise c.AuditError("startup zero record changed")
    handler_delta, byte_count, destination = struct.unpack_from("<iII", record)
    handler = (ZERO_RECORD[0] + handler_delta) & ~1
    if (handler, destination, destination + byte_count) != (0x5FA01E, *ZERO_RANGE):
        raise c.AuditError("startup zero range changed")
    handler_body = c._slice(blob, 0x5FA01E, 0x5FA056)
    if sh(handler_body) != "8b74bda81d1262930007b87bd980ccaebc6028472d7dd7413c20cc1f281b1b67":
        raise c.AuditError("startup zero handler changed")
    if not ZERO_RANGE[0] <= BOOT_COUNT_ADDRESS < BOOT_COUNT_ADDRESS + 4 <= ZERO_RANGE[1]:
        raise c.AuditError("boot count escaped startup zero range")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    flashdb = _provenance_and_configuration(blob)
    _startup_zero_proof(blob)
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
    if anchored != 2 or len(body) != 1384 or sh(body) != "2c07e82aa841a5f3a6cd0cdefc14f91a357fd9f8f6fa2e341cbd9a3ca0ea1665":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 550:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "921ef30a8be2b109603d722ccfccc84a2956e6b5bd53c356dc07c1156a20e348":
        raise c.AuditError("instruction topology changed")
    if indirect != [0x4D9562]:
        raise c.AuditError("migration dispatch site changed")

    pool = c._slice(blob, 0x4D9A98, 0x4D9B34)
    if len(pool) != 156 or sh(pool) != "1e9d634f8dec4d914a0173ab2ed5732b1ff6d928a43292fa72fc3cc6f331864a":
        raise c.AuditError("object pool/alignment changed")
    if sh(c._slice(blob, *PHYS)) != "373fb5e4f07d20e74c238fe6fe5922064d28e398b19696459167432fdbbc83c0":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x4D9522, 0x4D9530)) != "12611160fc8e6ee3552e451f338ef1a611ad59ddf77254c51b5a1685d9d7c7f9":
        raise c.AuditError("preceding TinyFrame boundary changed")
    if sh(c._slice(blob, 0x4D9B34, 0x4D9B4A)) != "866dc79ed3d0075d1b9ffbdd45fe225caeb9f0822904bb272ce0b731e5336e42":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, ONBOARDING, DB_ADAPTER, FLASHDB)
    if len(calls) != 88 or sum(target in starts for _, target in calls) != 4:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "a556efd6d2a9a46c504f06860fc378f21588c759e4504fd69b8221f391702a2c":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (65, 1, 2, 12, 4):
        raise c.AuditError("provider accounting changed")

    migration = c._slice(blob, *MIGRATION_TABLE)
    observed_targets = tuple(value & ~1 for value in struct.unpack("<11I", migration))
    if sh(migration) != "bd1d3336c4e37373945074a222e8bc34f71269373b0cf16ffe7fbd7bc779b112" or observed_targets != MIGRATION_TARGETS:
        raise c.AuditError("migration table changed")
    for name in (
        "als-scale", "module-configure", "ring", "setting", "temperature-unit",
        "terminal-mode", "time", "time-format", "universal-setting",
        "onboarding-config",
    ):
        if not (ROOT / f"tools/manifests/g2-kvdb-{name}-closure.tsv").is_file():
            raise c.AuditError(f"closed KV leaf evidence missing: {name}")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 32 or c._pair_digest(entries) != "16f2c10309cf150e770bbc4add0c95e7c79c1ce45139e9694ca9c0ca43c27c09":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored:
        raise c.AuditError("unexpected stored entry pointer")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\kv\service_kvdb.c"
    if _cstring(blob, 0x6EF9F8) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x4D9AB4) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x788A30: "SVC_KvdbReadAll", 0x788A40: "SVC_KvdbInit",
        0x78E58C: "kvdb", 0x78E594: "sysenv", 0x78E574: "kvMagic",
        0x78BF6C: "kvbooCount",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("KVDB diagnostic/configuration string changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("service_kvdb.c" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented KVDB service entered production overlay")
    sysenv_partition = next(item for item in flashdb["partitions"] if item["name"] == "kvdb")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\flashDB\kv\service_kvdb.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 7, "ghidra_discovered_functions": 7,
            "restored_functions": 5, "path_anchored_functions": 2,
            "raw_path_references": 13, "raw_path_referencing_functions": 2,
            "body_bytes": 1384, "physical_bytes": 1540,
            "outer_pool_and_alignment_bytes": 156, "reachable_instructions": 550,
            "direct_body_calls": 88, "internal_direct_body_calls": 4,
            "external_direct_body_calls": 84, "indirect_body_call_sites": 1,
            "bounded_indirect_target_entries": 11,
            "direct_bl_entry_sites": 32, "stored_entry_pointers": 0,
        },
        "behavior": {
            "database_index": 0, "database_name": "sysenv", "partition_name": "kvdb",
            "partition_offset": sysenv_partition["offset"],
            "partition_bytes": sysenv_partition["length"],
            "default_table_address": "0x2000372c", "default_node_count": 12,
            "magic_key": "kvMagic", "magic_value": 0x5A000020,
            "magic_mismatch_policy": "wholesale fdb_kv_set_default",
            "lock_callback_command": 2, "unlock_callback_command": 3,
            "migration_callbacks": 11,
            "boot_count_key": "kvbooCount", "boot_count_value_address": "0x20074988",
            "boot_count_startup_value": 0,
            "boot_count_startup_zero_range": ["0x20004558", "0x20075048"],
            "boot_count_read_increment_write": True,
            "invalidate_magic_writes_zero": True,
            "stock_fal_zero_on_driver_failure_hazard": True,
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 65, "iar_dlib_calls": 1,
            "flashdb_core_calls": 4, "g2_database_adapter_calls": 12,
            "closed_onboarding_record_calls": 2,
            "closed_migration_target_entries": 11,
            "flashdb_version": flashdb["version"],
            "flashdb_commit": "714d6159e7e6afb267a3953756abca445c350e61",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
