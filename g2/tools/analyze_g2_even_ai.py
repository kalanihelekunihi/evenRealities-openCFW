#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for app\\gui\\EvenAI\\even_ai.c."""
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

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-even-ai-function-map.tsv"
CL = ROOT / "tools/manifests/g2-even-ai-closure.tsv"
PINS = {FM: "af6335e43d2517a301f770e32c78c97380ee2885c1e0504408124124df2517cf", CL: "345d14c76ef409a1ef837c379e94de768b41d9b40503209b08bb0659954c0a6c"}
RETAINED = 'app\\gui\\EvenAI\\even_ai.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\even_ai.c'
PATH_RUN = 0x70b3a4
CELLS = (5122636, 5123572)
CELL_REFS = {5122636: (5120004, 5120166, 5120284, 5120880, 5121378, 5121466, 5121568, 5121780, 5121854, 5121938, 5122476, 5122562), 5123572: (5123166, 5123330)}
ALL_REFS = (5120004, 5120166, 5120284, 5120880, 5121378, 5121466, 5121568, 5121780, 5121854, 5121938, 5122476, 5122562, 5123166, 5123330)
F = ((5119868, 5119910), (5119954, 5120242), (5120242, 5122422), (5122422, 5122624), (5122652, 5122774), (5122774, 5123106), (5123136, 5123436))
PHYS = (5119954, 5123600)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((5120616, 5119954), (5120628, 5119954), (5120770, 5119954), (5120782, 5119954), (5120816, 5119954), (5121288, 5119954), (5121338, 5119954), (5121740, 5119954), (5122150, 5119954), (5122176, 5119954), (5122228, 5119954), (5122302, 5119954), (5122332, 5119954), (5122410, 5119954), (5122430, 5119868), (5122616, 5120242), (5122812, 5120242), (5123204, 5119868), (5123246, 5122774))
BL_STRICT = ()
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((6964484, 5122423), (6964488, 5123137), (7937457, 5122653))
GUARD_BEFORE = "454b4bd399a6aa39c3533ef8886bda21fd105f9682a3baf5ece4732276016b20"
GUARD_AFTER = "f8cc4ac3dc0d99e30518ca93b28ef142c0c2dca187939e5346aa2bf4a52d2d03"
TAGS = ((7315988, '[even_ai.page]recv evenai f_text_end = %d, text_len = %d, text = %.*s'), (7424840, '[even_ai.page]stop current streaming, avoid text confusion'), (7465528, '[even_ai.page][even ai]action_id = %d, action_type = %d'), (7465584, '[even_ai.page]recv evenai text_len = %d, text = %.*s'), (7465696, '[even_ai.page]not asked, not allow to show skills text'), (7509180, '[even_ai.page]not asked, not allow to show reply'), (7509232, '[even_ai.page]APP_PbRxEvenAIFrameDataProcess failed'), (7552548, '[even_ai.page]try to stop evenai, enable = %d'), (7552644, '[even_ai.page]SVC_DecodeLocalEvenAIInfo failed'), (7596672, '[even ai]action_id = %d, action_type = %d'), (7596760, '[even_ai.page]recv evenai skill_param = %d'), (7684920, '[even_ai.page]try to start evenai'), (7685028, '[even_ai.page]UI_EVENT_TYPE_INIT'), (7685064, '[even_ai.page]UI_EVENT_TYPE_EXIT'))
EXPECTED = {'body_bytes': 3466, 'body_concat_sha256': '88926dc85dd603bc46162f4bc791cb6baa46e4b648505c697ff379f37ab49246', 'reachable_instructions': 1321, 'reachable_instruction_digest': '003ff7fd01a063e627319fb43650b836f5926bb37204aac31b31006427d66b2b', 'direct_body_calls': 212, 'direct_body_call_digest': 'c28c06134315d085e852d9d50154a25061406e2313680f557d13858c27add58c', 'internal_direct_body_calls': 19, 'outer_pool_bytes': 222, 'outer_pool_sha256': '8a4974c371601b3c719b574e439aaf2be9533cb5021e7f965d084c0598b3b077', 'physical_bytes': 3646, 'physical_sha256': '9dafacf55dbaf40d43f95a44d41e3909328ef6addfaeedd43c6add252fa2df34', 'path_literal_references': 14}
DECODER = Cs(CS_ARCH_ARM, CS_MODE_THUMB | CS_MODE_LITTLE_ENDIAN | CS_MODE_MCLASS)
DECODER.detail = True


def _sh(value):
    return hashlib.sha256(value).hexdigest()


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
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any(x.get("path", "").replace("\\", "/").split("/")[-1].lower() == 'even_ai.c' for x in overlay["sources"]):
        raise c.AuditError("object entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor linked-object closure",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
