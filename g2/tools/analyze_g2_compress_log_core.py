#!/usr/bin/env python3
"""Fail-closed complete-body and provider audit for compress_log/core."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

from capstone import (
    CS_ARCH_ARM,
    CS_GRP_JUMP,
    CS_MODE_LITTLE_ENDIAN,
    CS_MODE_MCLASS,
    CS_MODE_THUMB,
    Cs,
)
from capstone.arm import ARM_OP_IMM

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-compress-log-core-function-map.tsv"
CL = ROOT / "tools/manifests/g2-compress-log-core-closure.tsv"
PM = ROOT / "tools/manifests/g2-compress-log-core-provider-map.tsv"
PINS = {
    FM: "94bbfb637c10b8da9f6ede23d7789a4009377991bb4aa26276bef3a43cfba8ed",
    CL: "2b54a5890f33aba4bb732e65a0d8fd729755c613e198d9ce0919a23c945e60cb",
    PM: "54654cc6e7e1c29258194f197534f07874d97633d8546d0375a25408c7164d71",
}
F = (
    (0x43C7CC, 0x43C7FA),
    (0x43C7FA, 0x43C8D2),
    (0x43C8D2, 0x43CA50),
    (0x43CA50, 0x43CB84),
    (0x43CB84, 0x43CE9E),
    (0x43CE9E, 0x43CF02),
    (0x43CF02, 0x43CF8C),
    (0x43CF8C, 0x43D0C8),
)
STARTS = {start for start, _ in F}
IAR = {0x439BE4, 0x43C0E4, 0x44A43C}
EASYLOGGER = {0x43D0CE, 0x43D0DA, 0x43D574}
FREERTOS = {0x4416F0, 0x441710, 0x441750, 0x4420D0, 0x4420E8, 0x5FA0A4, 0x5FA0BA}
CMSIS = {0x4490CC}
FIRST_PARTY = {0x443484, 0x4487AC, 0x448F7C, 0x44A1C6, 0x44A798, 0x44A9AE}
EXTERNAL_TARGET_COUNTS = {
    0x439BE4: 10,
    0x43C0E4: 2,
    0x43D0CE: 23,
    0x43D0DA: 1,
    0x43D574: 6,
    0x4416F0: 1,
    0x441710: 5,
    0x441750: 3,
    0x4420D0: 1,
    0x4420E8: 1,
    0x443484: 1,
    0x4487AC: 1,
    0x448F7C: 1,
    0x4490CC: 2,
    0x44A1C6: 1,
    0x44A43C: 1,
    0x44A798: 3,
    0x44A9AE: 1,
    0x5FA0A4: 2,
    0x5FA0BA: 1,
}
PATH_REFS = [0x43C918, 0x43CA18, 0x43CF60, 0x43CFAC, 0x43D010, 0x43D094]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _recover_function(
    blob: bytes, start: int, end: int
) -> tuple[dict[int, object], list[tuple[int, int]], list[int]]:
    """Recover M-profile Thumb control flow without treating BICS as a branch."""
    decoder = Cs(
        CS_ARCH_ARM,
        CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS,
    )
    decoder.detail = True
    pending = [start]
    seen: dict[int, object] = {}
    calls: list[tuple[int, int]] = []
    indirect: list[int] = []
    while pending:
        address = pending.pop()
        if address in seen:
            continue
        if not start <= address < end:
            raise c.AuditError(f"control flow escaped at 0x{address:08x}")
        decoded = list(
            decoder.disasm(c._slice(blob, address, min(address + 4, end)), address, count=1)
        )
        if not decoded:
            raise c.AuditError(f"Thumb M-profile decode failed at 0x{address:08x}")
        instruction = decoded[0]
        if address + instruction.size > end:
            raise c.AuditError(f"instruction crosses function end at 0x{address:08x}")
        seen[address] = instruction
        following = address + instruction.size
        mnemonic = instruction.mnemonic
        if mnemonic in ("bl", "blx"):
            if instruction.operands and instruction.operands[0].type == ARM_OP_IMM:
                calls.append((address, instruction.operands[0].imm))
            elif mnemonic == "blx":
                indirect.append(address)
            else:
                raise c.AuditError(f"unresolved call at 0x{address:08x}")
            pending.append(following)
            continue
        if (mnemonic.startswith("pop") and "pc" in instruction.op_str) or mnemonic in (
            "bx",
            "bxj",
        ):
            continue
        if mnemonic.startswith("ldr") and instruction.op_str.startswith("pc,"):
            continue
        if mnemonic in ("tbb", "tbh"):
            raise c.AuditError(f"unclosed jump table at 0x{address:08x}")
        if instruction.group(CS_GRP_JUMP):
            if not instruction.operands or instruction.operands[-1].type != ARM_OP_IMM:
                raise c.AuditError(f"unresolved branch at 0x{address:08x}")
            pending.append(instruction.operands[-1].imm)
            if mnemonic not in ("b", "b.w"):
                pending.append(following)
            continue
        pending.append(following)
    return seen, calls, indirect


def _provenance() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"] != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c":
        raise c.AuditError("CMSIS_5 source selection changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise c.AuditError("FreeRTOS-Kernel source selection changed")
    easy_audit = (ROOT / "docs/research/easylogger-output-core-audit.md").read_text()
    if "[0x0043D574, 0x0043D976)" not in easy_audit or "Two deliberate G2 semantic changes" not in easy_audit:
        raise c.AuditError("EasyLogger output boundary assessment changed")
    queue_audit = (ROOT / "docs/research/freertos-queue-wrapper-tranche-source-boundary-audit.md").read_text()
    if "private lazy static recursive-mutex initializer" not in queue_audit:
        raise c.AuditError("private static-mutex caller assessment changed")
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
        decoded, direct, dynamic = _recover_function(blob, start, end)
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
    if anchored != 2 or len(body) != 2300 or sh(body) != "f106c8bfa77dc32dad8dc3a9fc1cceeff7eb36c872fb2b3525e12ceb963a9565":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 898:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "c825c08437327d58cb711c5412109b4548c0e4731ef59364eae798ee6e87f880":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (IAR, EASYLOGGER, FREERTOS, CMSIS, FIRST_PARTY)
    if len(calls) != 78 or sum(target in starts for _, target in calls) != 11:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "1ba055d02427a000609eae520e852b5c622023f490eec9201e3f930dcba4e14f":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (13, 30, 14, 2, 8):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 5726 or c._pair_digest(entries) != "4aa233cc3570726566c9925232cecbda6663f65e69bb487976ec267a0141a0ae":
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

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\service\compress_log\core\compress_log.c"
    if _cstring(blob, 0x6E2B18) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x43D0F4) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    if sh(c._slice(blob, 0x43D0E0, 0x43D13C)) != "e773a770bfbbb9f2f22dcb5d680d229ccc7027ce0996def759c7b21b1cbf68c1":
        raise c.AuditError("external literal cells changed")
    if sh(c._slice(blob, 0x43C7B0, 0x43C7CC)) != "5d870b20b2ea10c600b6a8d5096c2874b8e469349ffbdb5d896c4286871c304c":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, 0x43D0C8, 0x43D0E0)) != "14bc7317970fee9b7319a90ce6826f081fb366bdc23c744d3eaf196aa9b271a3":
        raise c.AuditError("following accessor boundary changed")
    for address, expected in {
        0x77E988: "_log_get_all_buffer",
        0x75E7F0: "svc_compress_log_sync_to_files",
        0x74841C: "svc_compress_log_force_sync_to_files",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("exact compact-log symbol changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("compress_log" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented compact-log core entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\compress_log\core\compress_log.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 8,
            "ghidra_discovered_functions": 7,
            "restored_functions": 1,
            "path_anchored_functions": 2,
            "raw_path_references": 6,
            "raw_path_referencing_functions": 3,
            "body_bytes": 2300,
            "reachable_instructions": 898,
            "external_interleaved_literal_cells": 23,
            "physical_interval_claimed": False,
            "direct_body_calls": 78,
            "internal_direct_body_calls": 11,
            "external_direct_body_calls": 67,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 5726,
            "stored_entry_pointers": 0,
        },
        "behavior": {
            "compact_record_bytes": 44,
            "compact_header_bytes": 12,
            "maximum_argument_bytes": 32,
            "string_tail_bytes": 16,
            "sync_period_ticks": 10000,
            "sync_block_bytes": 4096,
            "maximum_periodic_blocks": 9,
        },
        "provider_boundary": {
            "iar_dlib_calls": 13,
            "easylogger_control_output_calls": 30,
            "freertos_kernel_port_calls": 14,
            "cmsis_freertos_calls": 2,
            "other_first_party_calls": 8,
            "private_compact_output_entry": "0x0043CE9E",
            "upstream_derived_elog_output_entry": "0x0043D574",
            "private_hook_is_upstream_easylogger": False,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "cmsis_5_commit": "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
