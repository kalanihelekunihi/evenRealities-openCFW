#!/usr/bin/env python3
"""Fail-closed object/provider audit for FlashDB/NV/service_nvdb.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_flashdb as fdb
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
SOURCE = ROOT / "components/apollo_main/core_overlay/service_nvdb.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
FM = ROOT / "tools/manifests/g2-service-nvdb-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-nvdb-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-nvdb-provider-map.tsv"
PINS = {
    FM: "7c7357bfabb00ef58b917994c3638a482a9ca8d0aec391666b0ba646cb93f9a1",
    CL: "eb836f43fc8eacdfc529419af354df4ee09a11c5d25829e38ac051833657c8fd",
    PM: "a0f0780e1e6c248a00c20fb6206f7c310d5d027166698b66b8ac13db2bfa9162",
}
F = (
    (0x5105F0, 0x510602), (0x510602, 0x510614),
    (0x510614, 0x510620), (0x510620, 0x51079C),
    (0x51079C, 0x510992),
)
PHYS = (0x5105F0, 0x510A0C)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x439BE4, 0x46CACC}
FLASHDB = {0x5450A4, 0x545320, 0x5453FE}
DB_ADAPTER = {0x54116E, 0x5411F2, 0x541232}
SERIAL_POLICY = {0x4AFC68, 0x4AFCDC}
EXTERNAL_TARGET_COUNTS = {
    0x439BE4: 1, 0x43CE9E: 8, 0x43D0CE: 24, 0x43D574: 8,
    0x46CACC: 1, 0x4AFC68: 1, 0x4AFCDC: 1, 0x54116E: 4,
    0x5411F2: 1, 0x541232: 4, 0x5450A4: 1, 0x545320: 2,
    0x5453FE: 1,
}
PATH_REFS = [0x510650, 0x5106D8, 0x510748, 0x510818, 0x510870, 0x5108BE, 0x510908, 0x510964]


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
    factory = next(item for item in findings["default_kv_tables"] if item["database"] == "factory")
    binding = next(item for item in findings["database_bindings"] if item["index"] == 1)
    if (
        findings["version"] != "2.1.1"
        or binding != {"index": 1, "database_name": "factory", "partition_name": "NVdb"}
        or factory["address"] != 0x20003868
        or len(factory["nodes"]) != 9
        or findings["first_party_policy"]["factory_magic"]
        != {"key": "nvMagic", "value": 0x55550022}
    ):
        raise c.AuditError("authenticated factory/NVdb configuration changed")
    return findings


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    flashdb = _provenance_and_configuration(blob)
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
    if anchored != 2 or len(body) != 930 or sh(body) != "69a92529d34123e3cd0e04272754940e699a0c6323215ceff1d0f7c88f47a9bd":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 379:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "d716e7b623620fd7365c60d95a149a71e47f28a37c16ba6f350c5cc7f1476f7f":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, 0x510992, 0x510A0C)
    if len(pool) != 122 or sh(pool) != "79e4adb96f8ec6d06352567f76c32569114e64c5fc30a4f59e8f38411b690634":
        raise c.AuditError("object pool/alignment changed")
    if sh(c._slice(blob, *PHYS)) != "89b3755f401952cd93615b007fdcdade3c203c60f2dccdd7c9a587c12b8e761e":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x5105BC, 0x5105F0)) != "1ac60a3f5c52dfc08f2e9446fedee1a7b25a8c152f0a1c79c4d26abef474f9af":
        raise c.AuditError("preceding object boundary changed")
    if sh(c._slice(blob, 0x510A0C, 0x510BFE)) != "51066606d4eddeff00303140367954f03d501a5f413fedcac973c0b1f5bbe5b7":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, FLASHDB, DB_ADAPTER, SERIAL_POLICY)
    if len(calls) != 60 or sum(target in starts for _, target in calls) != 3:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "d97b1798aef49da4f4578969e2a5e33a283c5361a803cf6994c84500cd41a2c3":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (40, 2, 4, 9, 2):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 20 or c._pair_digest(entries) != "bc064656f7280e01d0a70993254087ad7337885d9bd92f54635e4c7689c533c5":
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

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\flashDB\NV\service_nvdb.c"
    if _cstring(blob, 0x6EFA98) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x5109A4) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x78E5E4: "nvMagic", 0x78E5EC: "nvSysDt", 0x78E604: "nvdb",
        0x78E60C: "factory", 0x78E614: "NVdb",
        0x788BD0: "SVC_NvdbInit", 0x74E024: "[nvdb]read the fdbMagic:0x%x,length:%d",
        0x788BF0: "[nvdb]success",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("NVdb diagnostic/configuration string changed")

    source_bytes = SOURCE.read_bytes()
    if (len(source_bytes), sh(source_bytes)) != (
        8595,
        "f915b7fb32542c7c9c1e49b3e29b0beac075e59bda8e6ccef752df3a6922f0d7",
    ):
        raise c.AuditError("service_nvdb production source changed")
    source_text = source_bytes.decode("utf-8")
    if (
        "#define OPEN_CFW_NVDB_ALLOW_FACTORY_RESET 0" not in source_text
        or "return OPEN_CFW_NVDB_ERR_SCHEMA" not in source_text
        or "0x0078E5E4u" not in source_text
        or "0x0078E5ECu" not in source_text
        or "0x0078E60Cu" not in source_text
        or "0x0078E614u" not in source_text
    ):
        raise c.AuditError("non-destructive factory-media policy changed")

    overlay = json.loads(OVERLAY.read_text())
    names = [
        "open_cfw_service_nvdb_read",
        "open_cfw_service_nvdb_write",
        "open_cfw_service_nvdb_defaults_get",
        "open_cfw_service_nvdb_defaults_validate",
        "open_cfw_service_nvdb_init",
    ]
    leaves = [item for item in overlay["relocated_leaves"]
              if item.get("source", {}).get("path") ==
              "components/apollo_main/core_overlay/service_nvdb.c"]
    if [item.get("function") for item in leaves] != names:
        raise c.AuditError("service_nvdb relocated-leaf order changed")
    if [item["expected"]["size"] for item in leaves] != [12, 12, 22, 330, 138]:
        raise c.AuditError("service_nvdb compiled surface changed")
    if sum(len(item["relocations"]) for item in leaves) != 11:
        raise c.AuditError("service_nvdb relocation contract changed")
    patches = [item for item in overlay["patch_sites"]
               if item.get("target_function") in names]
    if (
        [item.get("target_function") for item in patches] != names
        or [item.get("runtime_address") for item in patches]
        != [start for start, _ in F]
        or [item.get("expected_size") for item in patches]
        != [end - start for start, end in F]
    ):
        raise c.AuditError("service_nvdb guarded redirect contract changed")

    build = json.loads(BUILD_REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "service NVDB")
    built_leaves = [item for item in build["relocated_leaves"]
                    if item.get("source", {}).get("path") ==
                    "components/apollo_main/core_overlay/service_nvdb.c"]
    if (
        [item["extraction"]["function"] for item in built_leaves] != names
        or sum(item["extraction"]["size"] for item in built_leaves) != 514
        or sum(item["placement"]["padding_before"] for item in built_leaves) != 4
        or sum(item["extraction"]["relocation_count"] for item in built_leaves) != 11
    ):
        raise c.AuditError("service_nvdb compiled report changed")

    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    nv_regions = [item for item in main["regions"] if item["name"].startswith("service_nvdb_")]
    if len(nv_regions) != 13:
        raise c.AuditError("service_nvdb manifest ownership changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\flashDB\NV\service_nvdb.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 5, "ghidra_discovered_functions": 5,
            "restored_functions": 3, "path_anchored_functions": 2,
            "raw_path_references": 8, "raw_path_referencing_functions": 2,
            "body_bytes": 930, "physical_bytes": 1052,
            "outer_pool_and_alignment_bytes": 122, "reachable_instructions": 379,
            "direct_body_calls": 60, "internal_direct_body_calls": 3,
            "external_direct_body_calls": 57, "indirect_body_calls": 0,
            "direct_bl_entry_sites": 20, "stored_entry_pointers": 0,
        },
        "behavior": {
            "database_index": 1,
            "database_name": "factory",
            "partition_name": "NVdb",
            "partition_offset": 0x01FF8000,
            "partition_bytes": 0x8000,
            "default_table_address": "0x20003868",
            "default_node_count": 9,
            "factory_magic_key": "nvMagic",
            "factory_magic_value": 0x55550022,
            "stock_magic_mismatch_policy": "wholesale fdb_kv_set_default",
            "magic_mismatch_policy": "wholesale fdb_kv_set_default",
            "production_magic_mismatch_policy": "fail closed without reset",
            "lock_callback_command": 2,
            "unlock_callback_command": 3,
            "sector_size_override_present": False,
            "stock_fal_zero_on_driver_failure_hazard": True,
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 40,
            "iar_dlib_calls": 2,
            "flashdb_core_calls": 4,
            "g2_database_adapter_calls": 9,
            "g2_serial_policy_calls": 2,
            "flashdb_version": flashdb["version"],
            "flashdb_commit": "714d6159e7e6afb267a3953756abca445c350e61",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {
            "production_routed": True,
            "compiled_text_bytes": 514,
            "alignment_bytes": 4,
            "strict_relocations": 11,
            "replaced_stock_body_bytes": 930,
            "retained_official_pool_bytes": 122,
            "destructive_default_reset_enabled": False,
            "hardware_validation": "blocked by unavailable physical evidence",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
