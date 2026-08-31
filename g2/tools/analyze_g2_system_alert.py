#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for app\\gui\\SystemAlert\\systemAlert.c."""
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
FM = ROOT / "tools/manifests/g2-system-alert-function-map.tsv"
CL = ROOT / "tools/manifests/g2-system-alert-closure.tsv"
PINS = {FM: "70bfe0ac4ea1d67fdc4aac21423d4c52f4b578a86d3610dd7a74e6a11a6ddb41", CL: "c59f0ac046ed2a5be63e29e67b24acdfb892f132f16472824100ea37206f4d1b"}
SOURCE = ROOT / "components/apollo_main/core_overlay/system_alert.c"
SOURCE_PATH = "components/apollo_main/core_overlay/system_alert.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
SOURCE_PIN = (19693, "9f94e517abcef761812b93f43ec0a64acd1a6e733d1f1fbff4927c85210edcc8")
LEAF_NAMES = (
    "open_cfw_system_alert_set_box_padding",
    "open_cfw_system_alert_common_data_handler",
    "open_cfw_system_alert_page_event_handler",
    "open_cfw_system_alert_main_page_init",
    "open_cfw_system_alert_send_event_throttled",
    "open_cfw_system_alert_reflash_event_handler",
    "open_cfw_system_alert_ui_event_handler",
)
LEAF_DIGEST = "dbc6a5d37554fb05d34257db61ce26cbb4ac40005264c0b38ace5779dd7f5a68"
PATCH_DIGEST = "1438650fbe6295315d0429def79c3d4eae2fcb31dafc5a57ff2e1a22830108ca"
BUILT_DIGEST = "0dafcad8ff47cb1a94052b1793cd37169c1cd8caf804fa8cc6d0d7d1265a1e93"
REGION_DIGEST = "ff843c92d0d94b5c499defa50e0d334d34bfbeba69ac8e0338083f30c95f7da6"
RETAINED = 'app\\gui\\SystemAlert\\systemAlert.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\SystemAlert\\systemAlert.c'
PATH_RUN = 0x6fd85c
CELLS = (5059620,)
CELL_REFS = {5059620: (5057516, 5057630, 5057808, 5057930, 5058052, 5058174, 5058248, 5058322, 5058774, 5058886, 5059444, 5059568)}
ALL_REFS = (5057516, 5057630, 5057808, 5057930, 5058052, 5058174, 5058248, 5058322, 5058774, 5058886, 5059444, 5059568)
F = ((5057434, 5057486), (5057486, 5057602), (5057602, 5058376), (5058376, 5058668), (5058668, 5058746), (5058746, 5059412), (5059412, 5059610))
PHYS = (5057434, 5059780)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((4707340, 5058668), (4707374, 5058668), (4708064, 5058668), (4708110, 5058668), (5059488, 5058376), (5059522, 5058746), (5773420, 5058668))
BL_STRICT = ((5058496, 5057436),)
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((6964868, 5057487), (6964872, 5059413))
GUARD_BEFORE = "edfa9b3ae829c8147c203d401457c91cf6ec7637270f1764f0376a73903f2ec6"
GUARD_AFTER = "cf0a1e149b6427265a32f95debba325c36cf82a304b6a305fd8c24904281a070"
TAGS = ((7486304, '[system_alert]PAGE_EVENT_FOREGROUND_ENTER_ANIM_COMPLETE'), (7486360, '[system_alert]send system alert auto exit event to self'), (7486416, '[system_alert]PAGE_EVENT_FOREGROUND_EXIT_ANIM_COMPLETE'), (7529356, '[system_alert]unknown system alert event type: %d'), (7573332, '[system_alert]MessageNotify recv data len = %d'), (7573380, '[system_alert]system_alert_ReflashEventHandler'), (7619464, '[system_alert]system_alert_MainPage_init'), (7711164, '[system_alert]IMU Reflash Event.'), (7711308, '[system_alert]UI_EVENT_TYPE_EXIT'), (7756272, '[system_alert]LV_EVENT_CLICKED'), (7756304, '[system_alert]SCROLLUP_EVENT'), (7756336, '[system_alert]SCROLLDOWN_EVENT'))
EXPECTED = {'body_bytes': 2176, 'body_concat_sha256': '0ec40c0f8d41475559c3965ef3c5e20f7efd316db6a1aa8040a7da82be99a8ff', 'reachable_instructions': 829, 'reachable_instruction_digest': '6c01024f602ab26becabec95666312256f837c63c65b8874f322938b678b12e5', 'direct_body_calls': 171, 'direct_body_call_digest': 'e26d347ddcdf64ca0b35a9d5bb2a3cc8f25497dbfb6386124b83403ae58a836a', 'internal_direct_body_calls': 2, 'outer_pool_bytes': 170, 'outer_pool_sha256': 'b202d158cdb435abe3b6424939173571c54f82559d68c3fd463cde1394c20195', 'physical_bytes': 2346, 'physical_sha256': '6de69853ca2ff4d9616cd0dbbfd4171768487955125d435a8a30f55d65584af2', 'path_literal_references': 12}
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
        raise c.AuditError("production SystemAlert source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = [x for x in overlay["relocated_leaves"] if x.get("source", {}).get("path") == SOURCE_PATH]
    if tuple(x.get("function") for x in leaves) != LEAF_NAMES or not set(LEAF_NAMES) <= set(overlay["functions"]):
        raise c.AuditError("production SystemAlert leaf inventory changed")
    if _jsh(leaves) != LEAF_DIGEST or any(x.get("profiles") != ["apple-clang"] or not x.get("strict_relocation_contract") or x.get("source", {}).get("license") != "MIT" for x in leaves):
        raise c.AuditError("production SystemAlert leaf closure changed")
    if sum(x["expected"]["size"] for x in leaves) != 1138 or sum(x["expected"].get("closure_size", x["expected"]["size"]) for x in leaves) != 1189 or sum(len(x["relocations"]) for x in leaves) != 85:
        raise c.AuditError("production SystemAlert compiled census changed")
    previous = 224198
    alignment = 0
    for leaf in leaves:
        alignment += leaf["expected"]["offset"] - previous
        previous = leaf["expected"]["offset"] + leaf["expected"].get("closure_size", leaf["expected"]["size"])
    if alignment != 9 or previous != 225396:
        raise c.AuditError("production SystemAlert placement changed")
    patches = [x for x in overlay["patch_sites"] if x.get("target_function") in set(LEAF_NAMES)]
    if len(patches) != 7 or _jsh(patches) != PATCH_DIGEST or sum(x["expected_size"] for x in patches) != 2174 or {x["target_function"] for x in patches} != set(LEAF_NAMES):
        raise c.AuditError("production SystemAlert redirects changed")
    if any(x.get("branch") != "b_w" or x.get("profiles") != ["apple-clang"] for x in patches):
        raise c.AuditError("production SystemAlert redirect policy changed")
    build = json.loads(REPORT.read_text())
    validate_apollo_main_artifacts(ROOT,c.AuditError,"SystemAlert")
    built = [x for x in build["relocated_leaves"] if x.get("source", {}).get("path") == SOURCE_PATH]
    normalized = [{"function": x["extraction"]["function"], "size": x["placement"]["size"], "padding_before": x["placement"]["padding_before"], "offset": x["placement"]["offset"], "runtime_address": x["placement"]["runtime_address"], "relocation_count": x["extraction"]["relocation_count"]} for x in built]
    if len(built) != 7 or _jsh(normalized) != BUILT_DIGEST or sum(x["size"] for x in normalized) != 1189 or sum(x["padding_before"] for x in normalized) != 9 or sum(x["relocation_count"] for x in normalized) != 85:
        raise c.AuditError("production SystemAlert built closure changed")
    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = [x for x in main["regions"] if x["name"].startswith("system_alert_") or x["name"].startswith("opaque_system_alert_")]
    if len(regions) != 21 or _jsh(regions) != REGION_DIGEST or sum(x["size"] for x in regions) != 3544:
        raise c.AuditError("production SystemAlert manifest regions changed")
    replacements = [x for x in regions if x["address_status"] == "generated_source_entry_replacement"]
    retained = [x for x in regions if x["address_status"] == "official_blob"]
    compiled = [x for x in regions if x["address_status"] == "source_compiled"]
    generated_alignment = [x for x in regions if x["address_status"] == "generated_alignment"]
    if (len(replacements), sum(x["size"] for x in replacements), len(retained), sum(x["size"] for x in retained), len(compiled), sum(x["size"] for x in compiled), len(generated_alignment), sum(x["size"] for x in generated_alignment)) != (7, 2174, 2, 172, 8, 1189, 4, 9):
        raise c.AuditError("production SystemAlert stock/overlay tiling changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor stock and production-source closure; no hardware or flash operation",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": {"source_admitted": True, "production_routed": True, "source_functions": 7, "compiled_text_bytes": 1138, "compiled_rodata_bytes": 51, "alignment_bytes": 9, "stock_replaced_bytes": 2174, "retained_literal_pool_bytes": 172, "strict_relocations": 85, "software_functional_gap": False, "hardware_validation": "blocked by unavailable physical evidence", "hardware_blocker": "An authorized responsive G2 pair is required for future dual-temple lifecycle, delayed-exit, translation, and rendered-display validation."},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
