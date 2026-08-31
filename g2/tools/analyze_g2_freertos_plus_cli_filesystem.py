#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for kernel\\FreeRTOS-Plus-CLI\\prvCommand\\prvCommand_filesystem.c."""
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

from capstone import (CS_ARCH_ARM, CS_GRP_JUMP, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS, CS_MODE_THUMB, Cs)
from capstone.arm import ARM_OP_IMM

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t
from apollo_artifact_consistency import validate_apollo_main_artifacts

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-freertos-plus-cli-filesystem-function-map.tsv"
CL = ROOT / "tools/manifests/g2-freertos-plus-cli-filesystem-closure.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/freertos_cli_filesystem.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINS = {FM: "4687cfb65b7331807a36e84efd75d664b85f3c26f19ab3d66800e6dcc050d340", CL: "70217413b8752abef1ef2b405a778525971f07897011747f4879df8e338a78ff"}
SOURCE_PATH = "components/apollo_main/core_overlay/freertos_cli_filesystem.c"
SOURCE_PIN = (22106, "6c80a375bce42595d995eaf947d51ba6fa71eb9afd7ea4b8ec79314395a50562")
LEAF_NAMES = (
    "open_cfw_cli_fs_normalize_path", "open_cfw_cli_fs_ls",
    "open_cfw_cli_fs_cat", "open_cfw_cli_fs_rm", "open_cfw_cli_fs_cd",
    "open_cfw_cli_fs_mkdir", "open_cfw_cli_fs_touch",
    "open_cfw_cli_fs_pwd", "open_cfw_cli_fs_mv", "open_cfw_cli_fs_md5",
    "open_cfw_cli_fs_df", "open_cfw_cli_fs_block_stats_accumulate",
)
LEAF_DIGEST = "a5cc6cc4cd5a10bd326e9afa2f6dca89c594aca49026c67628bd6c158f85c4d2"
PATCH_DIGEST = "c5551ed8d5b629b1878de1860aace37552e55b1cf99096bf21c29af67baa98ed"
BUILT_DIGEST = "9b988a7d9c998910ec28aea5b40f704ade411bf110ff1ea95294b1661c4169b2"
REGION_DIGEST = "308a8f94fda77fe675d8045ea97cd093be68b8cd370e1e471a8c8e51904935a7"
RETAINED = 'kernel\\FreeRTOS-Plus-CLI\\prvCommand\\prvCommand_filesystem.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\kernel\\FreeRTOS-Plus-CLI\\prvCommand\\prvCommand_filesystem.c'
PATH_RUN = 0x6de434
CELLS = (5765456,)
CELL_REFS = {5765456: (5762824, 5762906, 5763214, 5763296, 5763580, 5764336)}
ALL_REFS = (5762824, 5762906, 5763214, 5763296, 5763580, 5764336)
F = ((5761176, 5761312), (5761312, 5761546), (5761546, 5761704), (5761704, 5761924), (5761940, 5762172), (5762172, 5762342), (5762342, 5762530), (5762530, 5762562), (5762572, 5763690), (5763700, 5764030), (5764044, 5764394), (5764400, 5764432))
PHYS = (5761176, 5764432)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((5762090, 5761704), (5763356, 5761704), (5763384, 5761704), (5763800, 5761704), (5765148, 5761704), (5765174, 5761704))
BL_STRICT = ()
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((5767092, 5764401),)
GUARD_BEFORE = "259b9ca9e9e35e9d2077ed25ee2c8510d975fdf92561b5bcabc00fa39eb6b06f"
GUARD_AFTER = "b95be6439d1282a67d7646c78826dd7650ea880f230fb6103df725464d084ace"
TAGS = ((7358892, '[prvCommand_filesystem]Block info: size=%lu, total=%lu, used=%ld'), (7609212, '[prvCommand_filesystem]final_dst_path: %s'), (7701372, '[prvCommand_filesystem]param1: %s'), (7701408, '[prvCommand_filesystem]param2: %s'), (7701444, '[prvCommand_filesystem]src_path: %s'), (7701480, '[prvCommand_filesystem]dst_path: %s'))
EXPECTED = {'body_bytes': 3200, 'body_concat_sha256': '5e9da7dcc2734c2a25cc01de24f0d06a3ff3e8cb8df10ad7baa5546944f3cc7d', 'reachable_instructions': 1229, 'reachable_instruction_digest': 'c7a42bedb041c9a1986e2d252131382da5462fdc911aa25e54417b6cd9504ad9', 'direct_body_calls': 186, 'direct_body_call_digest': '0838e517f9166cb85e91556af86569a558c43368377b7cb52fc8a057ca11753d', 'internal_direct_body_calls': 4, 'outer_pool_bytes': 56, 'outer_pool_sha256': 'ca466a06b7371c1d68a4cabac715c5b0b7d89a214ee03357a5c4b57a8c35df63', 'physical_bytes': 3256, 'physical_sha256': 'cf81b4805490ce0b3a693689a4cab383508d6c3b7011b637003bdb8884ceffbf', 'path_literal_references': 6}
DECODER = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS)
DECODER.detail = True


def _sh(value):
    return hashlib.sha256(value).hexdigest()


def _jsh(value):
    return _sh(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def _cstring(blob, address):
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError("unterminated string at 0x%08x" % address)
    return blob[offset:end].decode("ascii")


def _recover(blob, start, end):
    pending = [start]
    seen = {}
    calls = []
    escapes = []
    indirect = []
    while pending:
        a = pending.pop()
        if a in seen:
            continue
        if not start <= a < end:
            raise c.AuditError("escape 0x%x" % a)
        decoded = list(DECODER.disasm(c._slice(blob, a, min(a + 4, end)), a, count=1))
        if not decoded:
            raise c.AuditError("decode 0x%x" % a)
        i = decoded[0]
        if a + i.size > end:
            raise c.AuditError("cross 0x%x" % a)
        seen[a] = i
        f = a + i.size
        mn = i.mnemonic
        if mn in ("bl", "blx"):
            if i.operands and i.operands[0].type == ARM_OP_IMM:
                calls.append((a, i.operands[0].imm))
            else:
                indirect.append(a)
            if f < end:
                pending.append(f)
            else:
                raise c.AuditError("tail call falls out 0x%x" % a)
            continue
        if (mn.startswith("pop") and "pc" in i.op_str) or mn in ("bx", "bxj") or (mn.startswith("ldr") and i.op_str.startswith("pc,")):
            continue
        if mn in ("tbb", "tbh"):
            raise c.AuditError("table 0x%x" % a)
        if i.group(CS_GRP_JUMP):
            if not i.operands or i.operands[-1].type != ARM_OP_IMM:
                raise c.AuditError("branch 0x%x" % a)
            tgt = i.operands[-1].imm
            if start <= tgt < end:
                pending.append(tgt)
            else:
                escapes.append((a, tgt))
            if mn not in ("b", "b.w"):
                if f < end:
                    pending.append(f)
                else:
                    raise c.AuditError("cond branch falls out 0x%x" % a)
            continue
        if f < end:
            pending.append(f)
        else:
            raise c.AuditError("fell off end 0x%x" % a)
    return seen, calls, escapes, indirect


def analyze(image=IMAGE):
    blob = image.read_bytes()
    if len(blob) != c.IMAGE_SIZE or _sh(blob) != c.IMAGE_SHA256:
        raise c.AuditError("image changed")
    for path, expected in PINS.items():
        if _sh(path.read_bytes()) != expected:
            raise c.AuditError("manifest changed: " + path.name)
    with FM.open(newline="", encoding="utf8") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    if len(rows) != len(F):
        raise c.AuditError("function inventory changed")
    starts = set()
    ins = {}
    calls = []
    esc = []
    ind = []
    body = b""
    for row, (a, z) in zip(rows, F):
        if (int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)) != (a, z):
            raise c.AuditError("function bounds changed")
        raw = c._slice(blob, a, z)
        if len(raw) != int(row["stock_bytes"]) or _sh(raw) != row["stock_sha256"]:
            raise c.AuditError("function body changed")
        seen, cc, ee, ii = _recover(blob, a, z)
        if c._uncovered((a, z), seen):
            raise c.AuditError("function coverage changed")
        if len(seen) != int(row["reachable_instructions"]):
            raise c.AuditError("instruction census changed")
        if sum(1 for x in ALL_REFS if a <= x < z) != int(row["path_reference_sites"]):
            raise c.AuditError("path reference census changed")
        if set(ins) & set(seen):
            raise c.AuditError("function overlap")
        starts.add(a)
        ins.update(seen)
        calls += cc
        esc += ee
        ind += ii
        body += raw
    calls.sort()
    esc.sort()
    ind.sort()
    if len(body) != EXPECTED["body_bytes"] or _sh(body) != EXPECTED["body_concat_sha256"]:
        raise c.AuditError("body closure changed")
    if len(ins) != EXPECTED["reachable_instructions"] or c._instruction_digest(sorted((a, i.size) for a, i in ins.items())) != EXPECTED["reachable_instruction_digest"]:
        raise c.AuditError("instruction closure changed")
    if esc != list(ESCAPES) or ind != list(INDIRECT):
        raise c.AuditError("escape closure changed")
    if len(calls) != EXPECTED["direct_body_calls"] or c._pair_digest(calls) != EXPECTED["direct_body_call_digest"]:
        raise c.AuditError("call closure changed")
    if sum(1 for _, y in calls if y in starts) != EXPECTED["internal_direct_body_calls"]:
        raise c.AuditError("internal call census changed")
    phys = c._slice(blob, *PHYS)
    if _sh(phys) != EXPECTED["physical_sha256"]:
        raise c.AuditError("physical closure changed")
    covered = set()
    for a, i in ins.items():
        covered.update(range(a, a + i.size))
    pool = bytes(v for a2, v in zip(range(PHYS[0], PHYS[1]), phys) if a2 not in covered)
    if len(pool) != EXPECTED["outer_pool_bytes"] or _sh(pool) != EXPECTED["outer_pool_sha256"]:
        raise c.AuditError("pool closure changed")
    for fa, fz, fsha in FOREIGN:
        if _sh(c._slice(blob, fa, fz)) != fsha:
            raise c.AuditError("interleaved foreign block changed")
    if _sh(c._slice(blob, PHYS[0] - 16, PHYS[0])) != GUARD_BEFORE or _sh(c._slice(blob, PHYS[1], PHYS[1] + 16)) != GUARD_AFTER:
        raise c.AuditError("boundary changed")
    if _cstring(blob, PATH_RUN) != FULL_PATH:
        raise c.AuditError("retained path changed")
    for cell in CELLS:
        if struct.unpack("<I", c._slice(blob, cell, cell + 4))[0] != PATH_RUN:
            raise c.AuditError("path pointer cell changed")
        if t.literal_references(blob, cell) != list(CELL_REFS[cell]):
            raise c.AuditError("path literal references changed")
    interiors = set()
    for a, z in F:
        interiors.update(range(a + 2, z, 2))
    bl = []
    bls = []
    bw = []
    b16 = []
    n = len(blob)
    for o in range(0, n - 3, 2):
        f16, s16 = struct.unpack_from("<HH", blob, o)
        if f16 & 0xF800 == 0xF000:
            d = s16 & 0xD000
            if d == 0xD000 or d == 0x9000:
                sign = (f16 >> 10) & 1
                j1 = (s16 >> 13) & 1
                j2 = (s16 >> 11) & 1
                i1 = (~(j1 ^ sign)) & 1
                i2 = (~(j2 ^ sign)) & 1
                imm = (sign << 24) | (i1 << 23) | (i2 << 22) | ((f16 & 0x3FF) << 12) | ((s16 & 0x7FF) << 1)
                if imm & (1 << 24):
                    imm -= 1 << 25
                tgt = o + c.BASE + 4 + imm
                if tgt in starts:
                    (bl if d == 0xD000 else bw).append((o + c.BASE, tgt))
                elif d == 0xD000 and tgt in interiors:
                    bls.append((o + c.BASE, tgt))
        elif f16 & 0xF800 == 0xE000:
            imm = f16 & 0x7FF
            if imm & 0x400:
                imm -= 0x800
            tgt = o + c.BASE + 4 + (imm << 1)
            if tgt in starts:
                b16.append((o + c.BASE, tgt))
    if bl != list(BL_ENTRY) or bls != list(BL_STRICT) or bw != list(BW_ENTRY) or b16 != list(B16_ENTRY):
        raise c.AuditError("direct ingress changed")
    stored = []
    for s0 in sorted(starts):
        needle = struct.pack("<I", s0 | 1)
        q = blob.find(needle)
        while q >= 0:
            stored.append((c.BASE + q, s0 | 1))
            q = blob.find(needle, q + 1)
    stored.sort()
    if stored != list(STORED_RAW):
        raise c.AuditError("stored pointer topology changed")
    for address, text in TAGS:
        if _cstring(blob, address) != text:
            raise c.AuditError("tag string changed")
    source = SOURCE.read_bytes()
    if (len(source), _sh(source)) != SOURCE_PIN:
        raise c.AuditError("production FreeRTOS+CLI filesystem source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = [x for x in overlay["relocated_leaves"] if x.get("source", {}).get("path") == SOURCE_PATH]
    if tuple(x.get("function") for x in leaves) != LEAF_NAMES or not set(LEAF_NAMES) <= set(overlay["functions"]) or _jsh(leaves) != LEAF_DIGEST:
        raise c.AuditError("production FreeRTOS+CLI filesystem leaf inventory changed")
    if any(x.get("profiles") != ["apple-clang"] or not x.get("strict_relocation_contract") or x.get("source", {}).get("license") != "MIT" for x in leaves):
        raise c.AuditError("production FreeRTOS+CLI filesystem leaf policy changed")
    if sum(x["expected"]["size"] for x in leaves) != 9866 or sum(x["expected"].get("closure_size", x["expected"]["size"]) - x["expected"]["size"] for x in leaves) != 704 or sum(len(x["relocations"]) for x in leaves) != 179:
        raise c.AuditError("production FreeRTOS+CLI filesystem compiled census changed")
    previous = 228222
    alignment = 0
    for leaf in leaves:
        alignment += leaf["expected"]["offset"] - previous
        previous = leaf["expected"]["offset"] + leaf["expected"].get("closure_size", leaf["expected"]["size"])
    if alignment != 20 or previous != 238812:
        raise c.AuditError("production FreeRTOS+CLI filesystem placement changed")
    patches = [x for x in overlay["patch_sites"] if x.get("name", "").startswith("replace_freertos_cli_filesystem_")]
    stock_order = (LEAF_NAMES[1], LEAF_NAMES[2], LEAF_NAMES[3], LEAF_NAMES[0], *LEAF_NAMES[4:])
    if len(patches) != 12 or _jsh(patches) != PATCH_DIGEST or sum(x["expected_size"] for x in patches) != 3200 or tuple(x["target_function"] for x in patches) != stock_order:
        raise c.AuditError("production FreeRTOS+CLI filesystem redirects changed")
    if any(x.get("branch") != "b_w" or x.get("profiles") != ["apple-clang"] for x in patches):
        raise c.AuditError("production FreeRTOS+CLI filesystem redirect policy changed")
    build = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT,c.AuditError,"FreeRTOS+CLI filesystem")
    built = [x for x in build["relocated_leaves"] if x.get("source", {}).get("path") == SOURCE_PATH]
    normalized = [{"function": x["extraction"]["function"], "size": x["placement"]["size"], "text_size": x["placement"].get("text_size", x["placement"]["size"]), "padding_before": x["placement"]["padding_before"], "offset": x["placement"]["offset"], "runtime_address": x["placement"]["runtime_address"], "relocation_count": x["extraction"]["relocation_count"]} for x in built]
    if len(built) != 12 or _jsh(normalized) != BUILT_DIGEST or sum(x["size"] for x in normalized) != 10570 or sum(x["text_size"] for x in normalized) != 9866 or sum(x["padding_before"] for x in normalized) != 20 or sum(x["relocation_count"] for x in normalized) != 179:
        raise c.AuditError("production FreeRTOS+CLI filesystem built closure changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = [x for x in main["regions"] if x["name"].startswith("freertos_cli_filesystem_")]
    if len(regions) != 49 or _jsh(regions) != REGION_DIGEST or sum(x["size"] for x in regions) != 13846:
        raise c.AuditError("production FreeRTOS+CLI filesystem manifest regions changed")
    counts = {key: (sum(x["address_status"] == key for x in regions), sum(x["size"] for x in regions if x["address_status"] == key)) for key in ("generated_source_entry_replacement", "official_blob", "source_compiled", "generated_alignment")}
    if counts != {"generated_source_entry_replacement": (12, 3200), "official_blob": (5, 56), "source_compiled": (22, 10570), "generated_alignment": (10, 20)}:
        raise c.AuditError("production FreeRTOS+CLI filesystem stock/overlay tiling changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor linked-object closure",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": {
            "source_admitted": True,
            "production_routed": True,
            "source_functions": 12,
            "compiled_text_bytes": 9866,
            "compiled_rodata_bytes": 704,
            "alignment_bytes": 20,
            "strict_relocations": 179,
            "stock_replaced_bytes": 3200,
            "retained_literal_pool_bytes": 56,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": "Future physical qualification requires an authorized G2 pair and captured littlefs media for live directory, file, rename, MD5, capacity, and block-stat behavior; hardware testing is blocked by unavailable physical evidence.",
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
