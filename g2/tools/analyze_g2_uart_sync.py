#!/usr/bin/env python3
"""Fail-closed object/provider audit for framework/sync/uart_sync.c."""

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
FM = ROOT / "tools/manifests/g2-uart-sync-function-map.tsv"
CL = ROOT / "tools/manifests/g2-uart-sync-closure.tsv"
PM = ROOT / "tools/manifests/g2-uart-sync-provider-map.tsv"
PINS = {
    FM: "e3fdb261d696a913f9c20b6567c4dedede10a3ec5ceb95c5545c5d56631e41e9",
    CL: "85558be2dd2079f9e45d757550c5b2ffdd0962687b6aa4115603c6d9a0a69299",
    PM: "ce8d0489ae2a85a8ef9b5e3a46da4b71d106fde56868cc1c23aaecdbbb8b89f5",
}
F = (
    (0x541790, 0x5417A4), (0x5417A4, 0x5417C4),
    (0x5417C4, 0x5417D6), (0x5417D6, 0x541A2E),
    (0x541A2E, 0x541A86),
)
PHYS = (0x541790, 0x541AF8)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
CMSIS = {0x4490E2, 0x449590, 0x4495E4, 0x449642, 0x44969C, 0x44971C}
IAR = {0x43C0E4}
STREAM = {0x57DF7C, 0x57E05E, 0x57E136}
UART = {0x584BC0, 0x584C8C, 0x584C98, 0x584DB6, 0x584E94}
SYNC = {0x45D4B8, 0x45D4DC, 0x45E664, 0x45E8D0}
FIRST_PARTY = {
    0x444720, 0x45A570, 0x471528, 0x47D818, 0x47E4A6,
    0x4ABE60, 0x4AC828, 0x4FF99A, 0x501066, 0x501D5C,
}
EXTERNAL_TARGET_COUNTS = {
    0x43C0E4: 1, 0x43CE9E: 6, 0x43D0CE: 18, 0x43D574: 6,
    0x444720: 1, 0x4490E2: 1, 0x449590: 1, 0x4495E4: 1,
    0x449642: 3, 0x44969C: 1, 0x44971C: 1, 0x45A570: 1,
    0x45D4B8: 1, 0x45D4DC: 1, 0x45E664: 1, 0x45E8D0: 1,
    0x471528: 1, 0x47D818: 1, 0x47E4A6: 1, 0x4ABE60: 1,
    0x4AC828: 1, 0x4FF99A: 1, 0x501066: 1, 0x501D5C: 1,
    0x57DF7C: 1, 0x57E05E: 1, 0x57E136: 2, 0x584BC0: 1,
    0x584C8C: 1, 0x584C98: 1, 0x584DB6: 1, 0x584E94: 1,
}
PATH_REFS = [0x5417FC, 0x541848, 0x5418A6, 0x5418E8, 0x541972, 0x541A56]


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
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    if (
        cmsis["upstreams"]["cmsis_freertos"]["selected_commit"]
        != "d213f261b5be6bb29a7cce8b84071706b72f4d53"
        or cmsis["upstreams"]["cmsis_5"]["selected_commit"]
        != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c"
    ):
        raise c.AuditError("CMSIS source selection changed")
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise c.AuditError("FreeRTOS-Kernel source selection changed")
    tiny = json.loads((ROOT / "third_party/tinyframe/PROVENANCE.json").read_text())
    if (
        tiny["upstream"]["selected_commit"]
        != "eb75483e035916ef9f3e9fce0d2ae389cb09785f"
        or tiny["selection"]["core_identical_ceiling_commit"]
        != "a29167a69f052975b0e0134a73b4d31d03afa8fa"
    ):
        raise c.AuditError("TinyFrame source interval changed")
    ambiq = json.loads((ROOT / "third_party/ambiqsuite-apollo510/PROVENANCE.json").read_text())
    if (
        ambiq["upstream"]["selected_commit"]
        != "5efc0228528a8adce5eae0d226fac85d2551eb3b"
        or "SDK 5.1.0" not in ambiq["upstream"]["sdk_revision"]
    ):
        raise c.AuditError("AmbiqSuite source selection changed")
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
    code = b"".join(
        c._slice(blob, address, address + item.size)
        for address, item in sorted(instructions.items())
    )
    if anchored != 2 or len(body) != 758 or sh(body) != "abcaf8e394fffe0ca78733c6669bd0c8d1c9e5af2d3b787cc670e53f70ea685d":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 297:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "bf3108a63a6c98c085b62c25d4a4d7f1dd6792bc299ded75a926f8587e3e1893":
        raise c.AuditError("instruction topology changed")
    if indirect != [0x541914]:
        raise c.AuditError("indirect initializer dispatch changed")

    pool = c._slice(blob, 0x541A86, 0x541AF8)
    if len(pool) != 114 or sh(pool) != "9018b72b84bdcdca6891521de86f1d504d539c5385cc119b9469b89527b71014":
        raise c.AuditError("object pool changed")
    if sh(c._slice(blob, *PHYS)) != "95687bbb2342d095658c6986dac9270648f8b3afdf69a34aabd78a969b9f576c":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x54171C, 0x541790)) != "7934ade39937cfce85279a0d5d70008fe8ad93d9c8882a955d41b3aaa96cbde3":
        raise c.AuditError("preceding object boundary changed")
    if sh(c._slice(blob, 0x541AF8, 0x541B2C)) != "163bcbb175a1e4dc0ccb315e577c1f38ffb0c318dc21d1b35590247b2b207b07":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, CMSIS, IAR, STREAM, UART, SYNC, FIRST_PARTY)
    if len(calls) != 63 or sum(target in starts for _, target in calls) != 1:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "39b6bae2a0c6e29987505d5c1919ac694942b3acbf3f97677afb247f45887e53":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (30, 8, 1, 4, 5, 4, 10):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 4 or c._pair_digest(entries) != "5f90c0a8dc64377cee620d15fa44e67e97cd4c6120c7e11b662389b3c750f4d5":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != [(0x541A90, 0x5417A5), (0x541AE8, 0x5417D7)]:
        raise c.AuditError("stored callback/thread entries changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\framework\sync\uart_sync.c"
    if _cstring(blob, 0x710B64) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x541AA0) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x7846BC: "uart_thread_handler",
        0x7846E4: "uart_instance_init",
        0x75C180: "Failed to create uart sender mutex",
        0x75C1A4: "Failed to create uart EventFlags",
        0x745C74: "Failed to create uart receive stream buffer",
        0x77D0FC: "sync module init failed",
        0x7672D0: "xStreamBufferReceive val :%s",
        0x75C1C8: "Failed to create uart sync thread",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("UART-sync diagnostic changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("uart_sync" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented UART sync object entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"framework\sync\uart_sync.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 5,
            "ghidra_discovered_functions": 5,
            "restored_functions": 3,
            "path_anchored_functions": 2,
            "raw_path_references": 6,
            "raw_path_referencing_functions": 2,
            "body_bytes": 758,
            "physical_bytes": 872,
            "outer_pool_bytes": 114,
            "reachable_instructions": 297,
            "direct_body_calls": 63,
            "internal_direct_body_calls": 1,
            "external_direct_body_calls": 62,
            "indirect_body_calls": 1,
            "direct_bl_entry_sites": 4,
            "stored_entry_pointers": 2,
        },
        "behavior": {
            "receive_stream_capacity_bytes": 0x6000,
            "worker_event_mask": 7,
            "receive_event_bit": 1,
            "send_event_bit": 2,
            "tick_event_bit": 4,
            "event_wait_timeout": 0xFFFFFFFF,
            "event_wait_no_auto_clear": True,
            "receive_chunk_bytes": 0x400,
            "receive_dispatch_iteration_limit": 32,
            "receive_dispatch_byte_threshold": 0x7FFF,
            "product_mode_handshake_read_bytes": 10,
            "hardware_write_success_value": 0,
            "public_write_failure_value": -1,
            "dynamic_initializer_pointer_slot": "0x20000658",
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 30,
            "cmsis_freertos_calls": 8,
            "iar_dlib_calls": 1,
            "g2_stream_calls": 4,
            "g2_uart_adapter_calls": 5,
            "tinyframe_and_sync_framework_calls": 4,
            "g2_subsystem_policy_calls": 10,
            "bounded_indirect_initializer_calls": 1,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "tinyframe_selected_commit": "eb75483e035916ef9f3e9fce0d2ae389cb09785f",
            "tinyframe_core_identical_ceiling_commit": "a29167a69f052975b0e0134a73b4d31d03afa8fa",
            "ambiqsuite_apollo510_commit": "5efc0228528a8adce5eae0d226fac85d2551eb3b",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
