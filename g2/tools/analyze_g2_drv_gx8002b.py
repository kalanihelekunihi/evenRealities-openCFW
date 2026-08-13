#!/usr/bin/env python3
"""Fail-closed raw-image and provider audit for drv_gx8002b.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-drv-gx8002b-function-map.tsv"
CL = ROOT / "tools/manifests/g2-drv-gx8002b-closure.tsv"
PM = ROOT / "tools/manifests/g2-drv-gx8002b-provider-map.tsv"
US = ROOT / "tools/manifests/g2-drv-gx8002b-upstream-source.tsv"
PINS = {
    FM: "c066953fa62cbff4d0c5117a0a3cfcdaee4af0da78fc1b8342167a612ef74025",
    CL: "ae0bb66c067a71be84e7c8ac865949a3a48b03ab4d24e5523ec710ffa8e32fbc",
    PM: "645e08dbf9e6643fe7a7efa1c22cd5c44811187d73cd8e5051cc79082930e0d5",
    US: "e9870b5bd3de3f73134060f0d483a7a7a777a0eafc837a92715449bef7f07d47",
}
F = (
    (0x57A46C, 0x57A48A), (0x57A48A, 0x57A4B0),
    (0x57A4B0, 0x57A4D8), (0x57A4D8, 0x57A508),
    (0x57A508, 0x57A5BC), (0x57A5BC, 0x57A656),
    (0x57A656, 0x57A65C), (0x57A65C, 0x57A734),
    (0x57A734, 0x57A7E0), (0x57A7E0, 0x57A80E),
    (0x57A80E, 0x57A816), (0x57A816, 0x57A870),
)
PHYS = (0x57A46C, 0x57A900)
POOL = (0x57A870, 0x57A900)
INTERNAL = {a for a, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CMSIS_RTOS = {0x449376}
AMBIQ_I2S = {
    0x59005E: "am_hal_i2s_initialize",
    0x5900CE: "am_hal_i2s_deinitialize",
    0x590104: "am_hal_i2s_configure",
    0x5904CE: "am_hal_i2s_dma_transfer_start",
    0x590648: "am_hal_i2s_power_control",
    0x590818: "am_hal_i2s_interrupt_clear",
    0x590848: "am_hal_i2s_interrupt_status_get",
    0x5908A0: "am_hal_i2s_interrupt_service",
    0x590A24: "am_hal_i2s_dma_configure",
    0x590B6C: "am_hal_i2s_dma_get_buffer",
    0x590B92: "am_hal_i2s_enable",
    0x590C62: "am_hal_i2s_disable",
}
FIRST = {0x473934, 0x475014, 0x4C3074, 0x4C3138, 0x509024, 0x53C6B2, 0x53CC8C}
STORED = [(0x4380F0, 0x57A4D8), (0x686F1C, 0x57A80E)]
PATH_REFS = [
    0x57A52A, 0x57A594, 0x57A5D8, 0x57A62E, 0x57A678,
    0x57A70C, 0x57A750, 0x57A7B8, 0x57A848,
]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _provenance() -> None:
    ambiq = json.loads((ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())
    core = json.loads((ROOT / "third_party/cmsis-core/PROVENANCE.json").read_text())
    rtos = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if ambiq["upstream"]["selected_commit"] != "5efc0228528a8adce5eae0d226fac85d2551eb3b":
        raise c.AuditError("AmbiqSuite source selection changed")
    if core["upstream"]["selected_commit"] != "d23a6949a0331ca96853bcd98b0fdcc4db47184c":
        raise c.AuditError("CMSIS-Core source selection changed")
    if rtos["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    i2s_header = ROOT / "third_party/ambiqsuite-apollo510/mcu/apollo510/hal/am_hal_i2s.h"
    header_text = i2s_header.read_text(encoding="ascii")
    for name in AMBIQ_I2S.values():
        if name not in header_text:
            raise c.AuditError(f"Ambiq I2S declaration missing: {name}")
    core_header = (ROOT / "third_party/cmsis-core/CMSIS/Core/Include/core_cm55.h").read_text(encoding="utf-8")
    for name in ("__NVIC_EnableIRQ", "__NVIC_DisableIRQ", "__NVIC_SetPriority"):
        if name not in core_header:
            raise c.AuditError(f"CMSIS-Core helper missing: {name}")
    with US.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != 1 or rows[0]["sha256"] != "16888e7bc9e2daf3ed936463c4e0ecfec73ea3c74c3c49b1fe60618b8aa86dc4":
        raise c.AuditError("I2S source-oracle record changed")
    if rows[0]["git_blob_sha1"] != "cc422934767912c218b619084e7fbe92ce7eaf6b":
        raise c.AuditError("I2S source Git blob changed")


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
    if anchored != 3 or len(body) != 1028 or sh(body) != "df9d94bce63f02b703ef9e53b66f607637e809b255849aacef8a9e2573832f6d":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 399:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((a, i.size) for a, i in instructions.items())) != "0cf76e396ce059fb2da497016499b18ea3fb7ed9969d060a515cdf2117a064d4":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, *POOL)
    if len(pool) != 144 or sh(pool) != "27b833b8879e6264f36526ce3184d148479d9c8cb93c73d263d2b49ac953ae67":
        raise c.AuditError("outer pool changed")
    if sh(c._slice(blob, *PHYS)) != "ed39a7222a759c559218e3356a453da7571dd8e1df649befaddad4cfe1d49a43":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x57A44C, PHYS[0])) != "abc5a5fab5377e4d87ca16345f0c420ee6860f015f60c39687631f28c5da096a":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x57A926)) != "5bbff3fde30dd7e091d8d496ab401b1036e0dc5f158c071b57a0404ed0ace8f0":
        raise c.AuditError("following boundary changed")
    if tuple(struct.unpack_from("<4I", pool)) != (0xE000E100, 0xE000E180, 0xE000E400, 0xE000ED18):
        raise c.AuditError("CMSIS NVIC register constants changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, CMSIS_RTOS, set(AMBIQ_I2S), FIRST)
    if len(calls) != 79 or sum(target in starts for _, target in calls) != 5:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "65e8b3de9b4b95df3ec4fe44273925ac10ef29f6268363b39f66f3dcc5af8791":
        raise c.AuditError("call topology changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (45, 4, 13, 12):
        raise c.AuditError("provider accounting changed")
    if external[0x590648] != 2 or any(external[target] != 1 for target in AMBIQ_I2S if target != 0x590648):
        raise c.AuditError("Ambiq I2S API use changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 18 or c._pair_digest(entries) != "ee3637f2d41fc02e0a37e6245d663b8a046006b00529f6317f56c54067212361" or strict:
        raise c.AuditError("direct ingress changed")
    stored = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if value & 1 and target in starts:
            stored.append((c.BASE + offset, target))
    if stored != STORED or c._pair_digest(stored) != "807cf15cf8e3a9a379a13a6b9ffde8634d6c2b5b1687de72f96c32600a3cd77f":
        raise c.AuditError("stored ingress changed")
    if t.literal_references(blob, 0x57A894) != PATH_REFS:
        raise c.AuditError("retained-path references changed")

    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"driver\codec\drv_gx8002b.c",
            "embedded_third_party_definitions": [
                "__NVIC_EnableIRQ", "__NVIC_DisableIRQ", "__NVIC_SetPriority"
            ],
            "nationalchip_lvp_code_linked": False,
        },
        "surface": {
            "linked_functions": 12,
            "ghidra_discovered_functions": 9,
            "restored_functions": 3,
            "path_anchored_functions": 3,
            "raw_path_referencing_functions": 5,
            "body_bytes": 1028,
            "physical_bytes": 1172,
            "outer_pool_bytes": 144,
            "direct_body_calls": 79,
            "internal_direct_body_calls": 5,
            "external_direct_body_calls": 74,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 18,
            "stored_entry_pointers": 2,
        },
        "provider_boundary": {
            "cmsis_core_linked_definitions": 3,
            "ambiqsuite_i2s_calls": 13,
            "cmsis_freertos_calls": 4,
            "easylogger_calls": 45,
            "first_party_calls": 12,
            "ambiqsuite_i2s_apis": list(AMBIQ_I2S.values()),
            "ambiqsuite_public_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "ambiqsuite_file_revision": "release_sdk5p1p0-366b80e084",
            "ambiqsuite_source_sha256": "16888e7bc9e2daf3ed936463c4e0ecfec73ea3c74c3c49b1fe60618b8aa86dc4",
            "cmsis_core_commit": "d23a6949a0331ca96853bcd98b0fdcc4db47184c",
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
