#!/usr/bin/env python3
"""Fail-closed linked-object/provider audit for pt_protocol_procsr.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as cfg
import analyze_g2_ux_system as common
import recover_apollo_embedded_source_paths as thumb
from analyze_g2_thread_ble_production import wide_branch_target

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FUNCTION_MAP = ROOT / "tools/manifests/g2-pt-protocol-function-map.tsv"
PROVIDER_MAP = ROOT / "tools/manifests/g2-pt-protocol-provider-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-pt-protocol-closure.tsv"
PINS = {
    FUNCTION_MAP: "ef607bceeecf2ae7d11eaf7cbe2cf68e68a05cedc39fcf4fde6b04b047568a6b",
    PROVIDER_MAP: "77365dcf9798cfe109e8c8d2ff956f7cbaa7322f46f36971189d3cdbac5736a6",
    CLOSURE: "88fbae31e296a6285eb8cfe8eb5dac29b980a3746d82fbdb5353520264705435",
}
PHYSICAL = (0x0056F178, 0x00577C3C)
PATH_ADDRESS = 0x006EF458
PATH_CELLS = (
    0x0056FBE4, 0x0057075C, 0x00571050, 0x005713CC, 0x00571FD4,
    0x00572AE4, 0x005735F0, 0x00573F7C, 0x005747D0, 0x00575410,
    0x00575E94, 0x005768B8, 0x00577354, 0x00577BB8,
)
EASYLOGGER = {0x0043CE9E, 0x0043D0CE, 0x0043D574}
CMSIS = {0x004491AA, 0x004491B2, 0x00449376}
FREERTOS = {0x00454EFE}
RUNTIME = {
    0x00439BE4, 0x00439C04, 0x0043C0E4, 0x0044A43C, 0x0044B0AE,
    0x0046CACC, 0x004751C8, 0x00475FC0, 0x0048D540,
}
MPALAND = {0x004B4728}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def cstring(blob, address):
    offset = address - common.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < offset:
        raise common.AuditError("unterminated retained path")
    return blob[offset:end].decode("ascii")


def verify_provenance():
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise common.AuditError("EasyLogger provenance changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise common.AuditError("CMSIS-FreeRTOS provenance changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise common.AuditError("FreeRTOS-Kernel provenance changed")


def analyze(image=IMAGE):
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or sha256(blob) != common.IMAGE_SHA256:
        raise common.AuditError("official G2 image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise common.AuditError(f"manifest changed: {path.name}")
    verify_provenance()

    with FUNCTION_MAP.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    functions = [
        (int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0))
        for row in rows
    ]
    if len(functions) != 73 or sum(row["path_anchored"] == "yes" for row in rows) != 69:
        raise common.AuditError("function inventory changed")
    starts = {start for start, _ in functions}
    instructions = {}
    calls = []
    indirect = []
    body = b""
    for start, end in functions:
        recovered, direct, dynamic = cfg._recover_function(blob, start, end)
        uncovered = common._uncovered((start, end), recovered)
        if uncovered not in ([], [(0x00571908, 0x0057190C)]):
            raise common.AuditError(f"unexpected inline data in 0x{start:08X}")
        if set(instructions) & set(recovered):
            raise common.AuditError("function instruction overlap")
        instructions.update(recovered)
        calls.extend(direct)
        indirect.extend(dynamic)
        body += common._slice(blob, start, end)
    calls.sort()
    if (
        len(body) != 32866
        or sha256(body) != "c4654517691febe2e2c5c5c56b6ad719b59dc79b33148860d1aadb52d58f0b84"
        or len(instructions) != 12443
        or common._instruction_digest(sorted((address, insn.size) for address, insn in instructions.items()))
        != "3eb83dc523579e3ea3d290726760fe884ed5fd58e1b616b8e554305c67bcd738"
        or indirect != [0x0056F838]
    ):
        raise common.AuditError("body or internal dispatch closure changed")

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
        != "a543c819bc9fc21577cdc71d8cab14aeb61cce8f684509b7517e7ed853025b59"
        or len(outer) != 2662
        or sha256(outer) != "d3aa33dd934b1ad64ef7b16f855bb13ad09aed41372efc5d0d5d5bd6bf5032f7"
        or sha256(common._slice(blob, PHYSICAL[0] - 16, PHYSICAL[0]))
        != "c9b0c058449d459429cb0294614d7ca808bccee71e7b31d343ed4fd5b2e1ffba"
        or sha256(common._slice(blob, PHYSICAL[1], PHYSICAL[1] + 16))
        != "85ee2ba6a57b18253f0503ab43d1a87345f4afd32574d6c2c51f037847868d38"
    ):
        raise common.AuditError("physical or adjacent boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    reusable = EASYLOGGER | CMSIS | FREERTOS | RUNTIME | MPALAND
    first_party = set(external) - reusable
    if (
        len(calls) != 1553
        or sum(target in starts for _, target in calls) != 27
        or common._pair_digest(calls)
        != "5d4283b5b6024ae9c1bb9dfbd12b2a0bdf33e8b73e7599916e86c1141082a9dd"
        or tuple(sum(external[target] for target in provider) for provider in (EASYLOGGER, CMSIS, FREERTOS, RUNTIME, MPALAND))
        != (1280, 7, 1, 41, 1)
        or len(first_party) != 83
        or sum(external[target] for target in first_party) != 196
    ):
        raise common.AuditError("provider closure changed")

    entries, strict, noncode, wide_entries, wide_strict = [], [], [], [], []
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
        len(entries) != 30
        or common._pair_digest(entries) != "adbfd99707ed39cc8b635a48e04b1dbf51025001e6a9d2cb197210176f5c721c"
        or strict != [(0x0047CC90, 0x0056F298), (0x00482F5A, 0x00573078)]
        or noncode != [(0x0047CCA6, 0x0056F2AE), (0x0056F1A6, 0x005727AC)]
        or wide_entries
        or wide_strict != [(0x00571490, 0x00571CB0)]
    ):
        raise common.AuditError("whole-image branch classification changed")

    raw_matches = []
    exact_entries = []
    for offset in range(len(blob) - 3):
        value = struct.unpack_from("<I", blob, offset)[0]
        target = value & ~1
        if target in starts or target in interiors:
            address = common.BASE + offset
            raw_matches.append((address, value, target))
            if target in starts and address % 4 == 0 and value & 1:
                exact_entries.append((address, value))
    if (
        len(raw_matches) != 104
        or sha256(b"".join(struct.pack("<III", *item) for item in raw_matches))
        != "84efeb7a4a6be8079211390d731ad84108ecf25510ca867d946d1e107c398d8e"
        or len(exact_entries) != 66
        or common._pair_digest(exact_entries)
        != "0f1ee182584cbcbcf54bef3fcb70b598181d5eedeb1162a01739bc82d3345f97"
        or not all(0x0056FFB0 <= address <= 0x00570430 for address, _ in exact_entries)
    ):
        raise common.AuditError("handler table or raw lookalike classification changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\product_test\pt_protocol_procsr.c"
    if cstring(blob, PATH_ADDRESS) != expected_path:
        raise common.AuditError("retained path changed")
    path_refs = sorted(
        (cell, address) for cell in PATH_CELLS for address in thumb.literal_references(blob, cell)
    )
    if len(path_refs) != 256 or common._pair_digest(path_refs) != "7ce238713af104f62e8669c15c336f2fc1e2cbee9dd2ebdc4fad8b9df7c2643a":
        raise common.AuditError("retained path references changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any(item.get("path", "").lower().endswith("/pt_protocol_procsr.c") for item in overlay["sources"]):
        raise common.AuditError("unimplemented product-test object routed")
    return {
        "schema_version": 1,
        "identity": {
            "image_sha256": common.IMAGE_SHA256,
            "retained_path": r"platform\product_test\pt_protocol_procsr.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 73,
            "ghidra_discovered_functions": 72,
            "path_anchored_functions": 69,
            "restored_non_anchor_functions": 4,
            "body_bytes": 32866,
            "physical_bytes": 35524,
            "outer_pool_bytes": 2662,
            "reachable_instructions": 12443,
            "direct_body_calls": 1553,
            "internal_direct_body_calls": 27,
            "external_direct_body_calls": 1526,
            "indirect_body_calls": 1,
            "bounded_internal_dispatches": 1,
            "direct_bl_entry_sites": 30,
            "stored_function_pointers": 66,
            "unaligned_pseudo_bl": 4,
            "external_strict_interior_ingress": 0,
        },
        "provider_boundary": {
            "easylogger_calls": 1280,
            "cmsis_freertos_calls": 7,
            "freertos_kernel_calls": 1,
            "runtime_calls": 41,
            "mpaland_printf_calls": 1,
            "first_party_calls": 196,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "historical_product_test_commit": None,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
