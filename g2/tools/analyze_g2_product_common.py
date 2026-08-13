#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for platform\\product_test\\product_common.c."""
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
FM = ROOT / "tools/manifests/g2-product-common-function-map.tsv"
CL = ROOT / "tools/manifests/g2-product-common-closure.tsv"
PINS = {FM: "d3067c597fdc26238887bcd146d6ee3888498b6039025745d15639c12c1c3dea", CL: "72d45d341d5c401912cb0ba951ed5082367aec2ba5dc50ef7c95540fed5c2ac8"}
RETAINED = 'platform\\product_test\\product_common.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\platform\\product_test\\product_common.c'
PATH_RUN = 0x6f5360
CELLS = (5829796,)
CELL_REFS = {5829796: (5829172, 5829290, 5829358, 5829462, 5829628, 5829708)}
ALL_REFS = (5829172, 5829290, 5829358, 5829462, 5829628, 5829708)
F = ((5829100, 5829128), (5829128, 5829766), (5829766, 5829776), (5829776, 5829786))
PHYS = (5829100, 5829860)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((5700548, 5829766), (5700558, 5829776), (5829224, 5829100), (5829534, 5829100), (5829770, 5829128), (5829780, 5829128))
BL_STRICT = ()
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ()
GUARD_BEFORE = "679fd3c7c170db2fd9bbe911804ae0ad032350a5489aa6dda4a8ecb81a34b4b3"
GUARD_AFTER = "87160f876ddef57d1abee2879fc3801b476c85739eeed0b9c0f76a084878f1c2"
TAGS = ((7396644, '[product_common]font crc: mismatch, calc=0x%04x expect=0x%04x'), (7436780, '[product_common]font crc: len overflow, base=0x%08x len=%u'), (7436840, '[product_common]font crc: match, calc=0x%04x expect=0x%04x'), (7519840, '[product_common]font crc: invalid base addr 0x%08x'), (7564116, '[product_common]font crc: len=%u, crc16=0x%04x'), (7653556, '[product_common]font crc: invalid len=0'))
EXPECTED = {'body_bytes': 686, 'body_concat_sha256': '6f98fd337b83f2c09034d268165bd559b62b936f2400b6debef107790fe038b6', 'reachable_instructions': 265, 'reachable_instruction_digest': '48505a228872d96b1efa19bec730a3c1f609d92065ff2c477a893b9ab234e882', 'direct_body_calls': 38, 'direct_body_call_digest': '24de9573765bb26d8c3148d57a3bdff4ca7b105af294abdf9461284c73e60ece', 'internal_direct_body_calls': 4, 'outer_pool_bytes': 74, 'outer_pool_sha256': '3d33859a5893c959483daec98183cb6dbfa3d265a03b90a39b5c7b186fe2f0ca', 'physical_bytes': 760, 'physical_sha256': '0050bbeef639d426ddf1f79e32dd0bc784060af1dd82a8b7a51b0f83626c88cd', 'path_literal_references': 6}
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
    if any(x.get("path", "").replace("\\", "/").split("/")[-1].lower() == 'product_common.c' for x in overlay["sources"]):
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
