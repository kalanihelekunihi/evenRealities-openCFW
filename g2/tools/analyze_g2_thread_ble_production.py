#!/usr/bin/env python3
"""Fail-closed object/provider audit for thread_ble_production.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-thread-ble-production-function-map.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-thread-ble-production-provider-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-thread-ble-production-closure.tsv"
PINNED_INPUTS = {
    FUNCTION_MAP: "22eb6994bb37260f4b02463ed12151ac56cbfafbb2c4fb73ff65d63be9bbd35e",
    PROVIDER_MAP: "43f94f3184cae0d3040973593ca4ac73ff8e04d0c7fbda0431ed5aa8003a1857",
    CLOSURE: "cdef41688bb34edeeff4d8fd177fcc14592a417f46aa51153e1c28b37aaa44e0",
}
PHYSICAL = (0x005382E4, 0x00538C24)
PATH_ADDRESS = 0x006F06C8
PATH_CELL = 0x00538B50
TASK_ATTRIBUTES = (0x0075B910, 0x0075B934)
TASK_ATTRIBUTE_WORDS = {
    0x0075B910: 0x00789990,
    0x0075B914: 0,
    0x0075B918: 0x200723E0,
    0x0075B91C: 0x70,
    0x0075B920: 0x2036DE40,
    0x0075B924: 0x1000,
    0x0075B928: 0x21,
    0x0075B92C: 1,
    0x0075B930: 0,
}
EASYLOGGER = {0x0043CE9E, 0x0043D0CE, 0x0043D574, 0x0043DACC}
CMSIS_FREERTOS = {
    0x004490E2,
    0x004491FE,
    0x00449238,
    0x004492C2,
    0x00449376,
    0x00449A32,
    0x00449ABE,
    0x00449B3C,
    0x00449BEC,
    0x00449C14,
    0x00449D3E,
    0x00449DD4,
}
FREERTOS_ASSERT = {0x005FA0A4}
RUNTIME = {0x00439BE4, 0x0043C0E4, 0x0044B0AE, 0x0044B610}
FIRST_PARTY = {0x004BE856, 0x004C9B86, 0x004C9BE2, 0x004C9C3C, 0x0054136C, 0x0056F4A0}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def cstring(blob, address):
    offset = address - common.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < offset:
        raise common.AuditError(f"unterminated string at 0x{address:08X}")
    return blob[offset:end].decode("ascii")


def wide_branch_target(address, first, second):
    """Decode Thumb-2 B.W encodings, excluding BL."""
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    imm10 = first & 0x03FF
    j1 = (second >> 13) & 1
    j2 = (second >> 11) & 1
    imm11 = second & 0x07FF
    i1 = 1 ^ (j1 ^ sign)
    i2 = 1 ^ (j2 ^ sign)
    immediate = (
        (sign << 24)
        | (i1 << 23)
        | (i2 << 22)
        | (imm10 << 12)
        | (imm11 << 1)
    )
    if sign:
        immediate -= 1 << 25
    return (address + 4 + immediate) & 0xFFFFFFFF


def verify_provenance():
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise common.AuditError("EasyLogger provenance changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise common.AuditError("CMSIS-FreeRTOS provenance changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"] != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c":
        raise common.AuditError("CMSIS_5 provenance changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise common.AuditError("FreeRTOS-Kernel provenance changed")
    if kernel["g2_boundary"]["g2_selected_portable_variant"] != "portable/IAR/ARM_CM55_NTZ/non_secure":
        raise common.AuditError("G2 FreeRTOS port selection changed")


def analyze(image=IMAGE):
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or sha256(blob) != common.IMAGE_SHA256:
        raise common.AuditError("official G2 image changed")
    for path, expected in PINNED_INPUTS.items():
        if sha256(path.read_bytes()) != expected:
            raise common.AuditError(f"manifest changed: {path.name}")
    verify_provenance()

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    functions = [
        (int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0))
        for row in rows
    ]
    if len(functions) != 14 or sum(row["path_anchored"] == "yes" for row in rows) != 6:
        raise common.AuditError("function inventory changed")

    starts = {start for start, _ in functions}
    instructions = {}
    calls = []
    indirect = []
    body = b""
    for row, (start, end) in zip(rows, functions):
        raw = common._slice(blob, start, end)
        recovered, direct, dynamic = cfg._recover_function(blob, start, end)
        if (
            len(raw) != int(row["interval_bytes"])
            or sha256(raw) != row["interval_sha256"]
            or common._uncovered((start, end), recovered)
        ):
            raise common.AuditError(f"function closure changed: {row['function']}")
        if set(instructions) & set(recovered):
            raise common.AuditError("function instruction overlap")
        instructions.update(recovered)
        calls.extend(direct)
        indirect.extend(dynamic)
        body += raw
    calls.sort()
    if (
        len(body) != 2140
        or sha256(body) != "1229ec18f1cbcee360d98c38975e83326a68b635631e7736a4af03ff600319f9"
        or len(instructions) != 791
        or common._instruction_digest(sorted((address, insn.size) for address, insn in instructions.items()))
        != "46e8e0b69e5008bc93aa83a69dc93e26923ed935cbe7e825f6471e6466d332df"
        or indirect
    ):
        raise common.AuditError("body closure changed")

    covered = set()
    for address, insn in instructions.items():
        covered.update(range(address, address + insn.size))
    outer = bytes(
        value
        for address, value in zip(range(*PHYSICAL), common._slice(blob, *PHYSICAL))
        if address not in covered
    )
    if (
        sha256(common._slice(blob, *PHYSICAL))
        != "fd92850239eed0b6021c25bb25e545a457acbb7b449f1d7a3657622ad25993fe"
        or len(outer) != 228
        or sha256(outer) != "cd3cc1f5c9f46637ed1880a3959091c679b3dadc7b8dd3e12afdc30dd1a1964c"
        or sha256(common._slice(blob, PHYSICAL[0] - 16, PHYSICAL[0]))
        != "5340f314f3c04128a0f9b0006d17c807b900bbf12b635a73d1f9589d8cd97fd0"
        or sha256(common._slice(blob, PHYSICAL[1], PHYSICAL[1] + 16))
        != "841fb194678432d3fa6e70fa882fa00786e268f6e84ddb088abfd1a3457c5922"
    ):
        raise common.AuditError("physical or adjacent boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASYLOGGER, CMSIS_FREERTOS, FREERTOS_ASSERT, RUNTIME, FIRST_PARTY)
    if (
        len(calls) != 145
        or sum(target in starts for _, target in calls) != 10
        or common._pair_digest(calls)
        != "c98fa8c4a8abf13aadf0a29de153b1f35e5de66183aba4c31f4c8ae00e329519"
        or set(external) != set().union(*providers)
        or tuple(sum(external[target] for target in provider) for provider in providers)
        != (106, 15, 3, 5, 6)
    ):
        raise common.AuditError("provider closure changed")

    entries = []
    strict = []
    noncode = []
    wide_entries = []
    wide_strict = []
    interiors = set(instructions) - starts
    for address in range(common.BASE, common.BASE + len(blob) - 3, 2):
        target = thumb._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
        elif target is not None and PHYSICAL[0] <= target < PHYSICAL[1]:
            noncode.append((address, target))
        first, second = struct.unpack("<HH", common._slice(blob, address, address + 4))
        target = wide_branch_target(address, first, second)
        if target in starts:
            wide_entries.append((address, target))
        elif target in interiors:
            wide_strict.append((address, target))
    if (
        len(entries) != 11
        or common._pair_digest(entries)
        != "95f6147b7ff57558598b333414e0b9c746ca66f83f7ab821a569e3140d96f0fc"
        or strict
        or noncode
        or wide_entries
        or wide_strict
    ):
        raise common.AuditError("whole-image branch ingress changed")

    raw_matches = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts or target in interiors:
            raw_matches.append((common.BASE + offset, value, target))
    if raw_matches != [
        (0x00538B64, 0x005382E5, 0x005382E4),
        (0x00644A27, 0x00538900, 0x00538900),
        (0x007940D3, 0x005383BF, 0x005383BE),
    ]:
        raise common.AuditError("stored entry or unaligned lookalike set changed")

    if cstring(blob, PATH_ADDRESS) != r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_ble_production.c":
        raise common.AuditError("retained path changed")
    path_refs = sorted((PATH_CELL, address) for address in thumb.literal_references(blob, PATH_CELL))
    if (
        len(path_refs) != 21
        or common._pair_digest(path_refs)
        != "b99fe2c7153933789c390b1150aa769ba09f527a0b956c39960cb4f9f91bc2c3"
    ):
        raise common.AuditError("retained path references changed")

    if sha256(common._slice(blob, *TASK_ATTRIBUTES)) != "df6d4d4b00159ecb08bd9129593ae1893d0517f88aca64da5591fa3363b37baa":
        raise common.AuditError("thread attributes changed")
    for address, expected in TASK_ATTRIBUTE_WORDS.items():
        if struct.unpack("<I", common._slice(blob, address, address + 4))[0] != expected:
            raise common.AuditError(f"thread attribute changed at 0x{address:08X}")
    if cstring(blob, 0x00789990) != "ble_production":
        raise common.AuditError("thread name changed")
    if struct.unpack("<I", common._slice(blob, 0x00538B64, 0x00538B68))[0] != 0x005382E5:
        raise common.AuditError("thread task-entry literal changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any(item.get("path", "").lower().endswith("/thread_ble_production.c") for item in overlay["sources"]):
        raise common.AuditError("unimplemented product thread routed into production")

    return {
        "schema_version": 1,
        "identity": {
            "image_sha256": common.IMAGE_SHA256,
            "retained_path": r"platform\threads\thread_ble_production.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 14,
            "ghidra_discovered_functions": 11,
            "path_anchored_functions": 6,
            "restored_non_anchor_functions": 8,
            "body_bytes": 2140,
            "physical_bytes": 2368,
            "outer_pool_bytes": 228,
            "reachable_instructions": 791,
            "direct_body_calls": 145,
            "internal_direct_body_calls": 10,
            "external_direct_body_calls": 135,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 11,
            "stored_function_pointers": 1,
            "excluded_unaligned_entry_lookalikes": 1,
            "excluded_unaligned_interior_lookalikes": 1,
            "strict_interior_ingress": 0,
            "wide_branch_entry_targets": 0,
        },
        "thread": {
            "name": "ble_production",
            "entry": 0x005382E4,
            "control_block": 0x200723E0,
            "control_block_bytes": 0x70,
            "stack": 0x2036DE40,
            "stack_bytes": 0x1000,
            "priority": 0x21,
            "queue_depth": 3,
            "memory_pool_blocks": 3,
            "memory_pool_block_bytes": 0x104,
        },
        "protocol": {
            "header": [0x5A, 0xA5, 0x7F],
            "checksum": "additive byte sum",
            "processor_translation_unit": r"platform\product_test\pt_protocol_procsr.c",
        },
        "provider_boundary": {
            "easylogger_calls": 106,
            "cmsis_freertos_calls": 15,
            "freertos_assert_calls": 3,
            "runtime_calls": 5,
            "first_party_calls": 6,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "historical_product_thread_commit": None,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
