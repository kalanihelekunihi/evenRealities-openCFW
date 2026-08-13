#!/usr/bin/env python3
"""Fail-closed raw-image and dependency audit for service_db_api.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_flashdb as flashdb
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-service-db-api-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-db-api-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-db-api-provider-map.tsv"
PINS = {
    FM: "9f3cb0321ca8fd72b1fdbb80f0106f922ee03fabc9f75e79f6bcff2d23b560f3",
    CL: "e5696fa7ca6cc56d34d43e33531098c6f08973f1eeee86618b018f666d07db69",
    PM: "91d6f9062ed68f17525c2ada29a985fe5709faace2b48da8dcf8993e76ff5fce",
}
F = (
    (0x540ED0, 0x540ED4), (0x540ED4, 0x540F2C),
    (0x540F2C, 0x540F84), (0x540F84, 0x541088),
    (0x541088, 0x5410DA), (0x5410DA, 0x541126),
    (0x541126, 0x54116E), (0x54116E, 0x5411F2),
    (0x5411F2, 0x541232), (0x541232, 0x541240),
    (0x541240, 0x54125C),
)
PHYS = (0x540ED0, 0x5412E0)
POOL = (0x54125C, 0x5412E0)
INTERNAL = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CMSIS_RTOS = {
    0x4490CC: "osKernelGetTickCount",
    0x44971C: "osMutexNew",
    0x4497B6: "osMutexAcquire",
    0x44981C: "osMutexRelease",
}
FLASHDB = {0x54454A: "fdb_kv_get_blob", 0x54503A: "fdb_kv_set_blob"}
FIRST = {0x47075C, 0x4708A8, 0x4709C8, 0x4D96D8, 0x51079C}
STORED = [
    (0x5412D8, 0x5410DA), (0x5412DC, 0x541126),
    (0x722B54, 0x540ED0), (0x722B58, 0x540ED4),
    (0x722B5C, 0x540F2C), (0x722B60, 0x540F84),
]
PATH_REFS = [
    0x540EF8, 0x540F50, 0x540FA8, 0x540FEC, 0x541058,
    0x5410B2, 0x5410FE, 0x541146, 0x5411BE,
]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _provenance(blob: bytes) -> dict:
    fdb = json.loads((ROOT / "third_party/flashdb/PROVENANCE.json").read_text())
    rtos = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if fdb["upstream"]["selected_commit"] != "714d6159e7e6afb267a3953756abca445c350e61":
        raise c.AuditError("FlashDB source selection changed")
    if fdb["upstream"]["declared_library_version"] != "2.1.1":
        raise c.AuditError("FlashDB version changed")
    if rtos["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")

    fdb_header = (ROOT / "third_party/flashdb/inc/flashdb.h").read_text(encoding="utf-8")
    cmsis_source = (ROOT / "third_party/cmsis-freertos/CMSIS-FreeRTOS/CMSIS/RTOS2/FreeRTOS/Source/cmsis_os2.c").read_text(encoding="utf-8")
    for name in FLASHDB.values():
        if name not in fdb_header:
            raise c.AuditError(f"FlashDB declaration missing: {name}")
    for name in CMSIS_RTOS.values():
        if name not in cmsis_source:
            raise c.AuditError(f"CMSIS-FreeRTOS definition missing: {name}")

    prior = flashdb.audit(blob)
    if prior["version"] != "2.1.1" or not prior["retained_kvdb_only"]:
        raise c.AuditError("FlashDB recovery result changed")
    if prior["db_object_abi"] != {
        **prior["db_object_abi"], "base": 0x2005DFFC, "count": 2, "stride": 0x8AC
    }:
        raise c.AuditError("FlashDB database-object ABI changed")
    if prior["database_callbacks"] != {
        "lock": 0x5410DB,
        "lock_wait": "forever",
        "mutex_object": 0x20074944,
        "per_node_callbacks": "none in FlashDB fdb_default_kv_node ABI",
        "unlock": 0x541127,
    }:
        raise c.AuditError("FlashDB mutex binding changed")
    if prior["fal_device"]["address"] != 0x1FC0000 or tuple(
        prior["fal_device"][key] for key in ("init", "read", "write", "erase")
    ) != (0x540ED1, 0x540ED5, 0x540F2D, 0x540F85):
        raise c.AuditError("FlashDB FAL callback binding changed")
    if not prior["norflash_port"]["flashdb_error_mapping"].startswith("unsafe stock seam"):
        raise c.AuditError("FlashDB error-seam finding changed")
    return prior


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if sh(path.read_bytes()) != expected:
            raise c.AuditError(f"manifest changed: {path.name}")
    prior = _provenance(blob)
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
        decoded, direct, dynamic = d._recover_function(blob, start, end)
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
    if anchored != 5 or len(body) != 908 or sh(body) != "4543128905f9c50185a34ca423ad0e0ed0ac61f1a8d0847d18a501cbe20a13bc":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 366:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "b0a59eced9c0d53c471563d4a861a905331c4600562a947eab8f3f094174d2ca":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    if len(c._slice(blob, *POOL)) != 132 or sh(c._slice(blob, *POOL)) != "175570b9821b29ab5e79ac426a166db7975a8c3f2544351b1fc1c1aef0a032ff":
        raise c.AuditError("outer pool changed")
    if sh(c._slice(blob, *PHYS)) != "5bc673adf9a8d39874f81329837fabfca45dbeab8d5af0d1c16b799e784cc4c4":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x540EB4, PHYS[0])) != "6d43800153274d7f30db6ec7b8c09c5c15cb801c4ea8f5950166e1c8f40a6961":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x541302)) != "fab1d89d4f37e4b965fb55be1d18dd5c9914a90da2cc56e2ec152857d5adbf31":
        raise c.AuditError("following boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, set(CMSIS_RTOS), set(FLASHDB), FIRST)
    if len(calls) != 60 or sum(target in starts for _, target in calls) != 1:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "6f30ebbeec42c912578d718f089a4686fd0c75b271e117bf140b5ccb131ba3f9":
        raise c.AuditError("call topology changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (45, 7, 2, 5):
        raise c.AuditError("provider accounting changed")
    if tuple(external[target] for target in CMSIS_RTOS) != (4, 1, 1, 1):
        raise c.AuditError("CMSIS-FreeRTOS API use changed")
    if any(external[target] != 1 for target in FLASHDB):
        raise c.AuditError("FlashDB API use changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 23 or c._pair_digest(entries) != "91e8ecc1d60f89279d72110a1ee45beea7220fd6e817464e7881b032cf36402f" or strict:
        raise c.AuditError("direct ingress changed")
    stored = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if value & 1 and target in starts:
            stored.append((c.BASE + offset, target))
    if stored != STORED or c._pair_digest(stored) != "b71e7c1c755a2e6f72eea346d70746ace306a2a294a51254202d855df61bdc96":
        raise c.AuditError("stored ingress changed")
    if t.literal_references(blob, 0x541264) != PATH_REFS:
        raise c.AuditError("retained-path references changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\flashDB\db_api\service_db_api.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 11,
            "ghidra_discovered_functions": 9,
            "restored_functions": 2,
            "path_anchored_functions": 5,
            "raw_path_referencing_functions": 7,
            "body_bytes": 908,
            "physical_bytes": 1040,
            "outer_pool_bytes": 132,
            "direct_body_calls": 60,
            "internal_direct_body_calls": 1,
            "external_direct_body_calls": 59,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 23,
            "stored_entry_pointers": 6,
        },
        "provider_boundary": {
            "flashdb_calls": 2,
            "cmsis_freertos_calls": 7,
            "easylogger_calls": 45,
            "first_party_calls": 5,
            "flashdb_apis": list(FLASHDB.values()),
            "cmsis_freertos_apis": list(CMSIS_RTOS.values()),
            "flashdb_version": prior["version"],
            "flashdb_commit": "714d6159e7e6afb267a3953756abca445c350e61",
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "unsafe_zero_on_failure_fal_seam": True,
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
