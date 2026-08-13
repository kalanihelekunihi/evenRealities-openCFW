#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for app\\gui\\setting\\setting.c."""
import csv
import hashlib
import json
import struct
import sys
from pathlib import Path

from capstone import (CS_ARCH_ARM, CS_GRP_JUMP, CS_MODE_LITTLE_ENDIAN, CS_MODE_MCLASS, CS_MODE_THUMB, Cs)
from capstone.arm import ARM_OP_IMM

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-setting-function-map.tsv"
CL = ROOT / "tools/manifests/g2-setting-closure.tsv"
PINS = {FM: "489307b2bd664218c8bf30d64bf874ed7376c7b6f48e356c494580cbc937b571", CL: "902a937de908ee29800f3af7287b541175e0c6690ee3f8448c23b9ff4785fa55"}
RETAINED = 'app\\gui\\setting\\setting.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\setting\\setting.c'
PATH_RUN = 0x70f3a4
CELLS = (4616940, 4620048)
CELL_REFS = {4616940: (4614358, 4614444, 4614546, 4614638, 4614714, 4614792, 4614874, 4615092, 4615178, 4615274, 4615354, 4615436, 4615548, 4615660, 4615744, 4615872, 4616008, 4616100, 4616184, 4616264, 4616338, 4616550, 4616640, 4616744, 4616836), 4620048: (4617002, 4617082, 4617158, 4617308, 4617572, 4617660, 4617798, 4617888, 4617978, 4618068, 4618178, 4618322, 4618462, 4618560, 4618634, 4618808, 4618906, 4618980, 4619098, 4619232, 4619348, 4619414, 4619498, 4619562, 4619704, 4619922)}
ALL_REFS = (4614358, 4614444, 4614546, 4614638, 4614714, 4614792, 4614874, 4615092, 4615178, 4615274, 4615354, 4615436, 4615548, 4615660, 4615744, 4615872, 4616008, 4616100, 4616184, 4616264, 4616338, 4616550, 4616640, 4616744, 4616836, 4617002, 4617082, 4617158, 4617308, 4617572, 4617660, 4617798, 4617888, 4617978, 4618068, 4618178, 4618322, 4618462, 4618560, 4618634, 4618808, 4618906, 4618980, 4619098, 4619232, 4619348, 4619414, 4619498, 4619562, 4619704, 4619922)
F = ((4614268, 4614288), (4614288, 4614318), (4614318, 4614518), (4614518, 4614844), (4614844, 4615148), (4615148, 4615708), (4615708, 4615842), (4615842, 4615976), (4615976, 4616500), (4616500, 4616510), (4616510, 4616610), (4616610, 4616710), (4616710, 4616922), (4616968, 4617382), (4617536, 4619288), (4619316, 4619602), (4619624, 4619850), (4619880, 4620034))
PHYS = (4614268, 4620040)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((4614496, 4614518), (4614600, 4614844), (4614968, 4615148), (4614976, 4615708), (4614984, 4615842), (4614994, 4615976), (4615002, 4616500), (4615010, 4616510), (4615020, 4616610), (4615030, 4616710), (4615040, 4616968), (4615050, 4617536), (4615060, 4619316), (4615808, 4614288), (4615942, 4614288), (4619536, 4614288), (4637090, 4614288))
BL_STRICT = ()
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((6964788, 4614269), (6964804, 4614319), (6964808, 4619881), (7945475, 4619625))
GUARD_BEFORE = "79cb6158aae0d7310ad8e23ad9b87d4f4811e26a536357cb6933bf6afcf56e11"
GUARD_AFTER = "0695a8680dc82087aab34725101e3b6bdc60283010bbeb8328f1125e9e03b848"
TAGS = ((7166552, '[setting]Received universal unit setting: unit_format=%d, distance_unit=%d, time_format=%d, date_format=%d, temperature_unit=%d'), (7230024, '[setting]dominant_hand ring_mac changed, reconnect required old[5-3]=%02X:%02X:%02X:'), (7230112, '[setting]dominant_hand ring_mac changed, reconnect required new[5-3]=%02X:%02X:%02X:'), (7230200, '[setting]dominant_hand: ring_mac recovered from factory placeholder, delay connect %ums'), (7249884, '[setting]dominant_hand ring_mac changed, reconnect required old[2-0]=%02X:%02X:%02X'), (7249968, '[setting]dominant_hand ring_mac changed, reconnect required new[2-0]=%02X:%02X:%02X'), (7250052, '[setting]setting_handle_dominant_hand: rejected within switch window, keep cur=%u'), (7273592, '[setting]Updated gesture config: screen_off=[%d,%d,%d], screen_on=[%d,%d,%d]'), (7299640, '[setting]Received dominant_hand setting: dominant_hand=%u, ring_mac.size=%d'), (7328588, '[setting]setting_handle_dominant_hand: unchanged, refresh local kv%s'), (7402468, '[setting]setting respond with local data serialize failed: %d'), (7441400, '[setting][Brightness Level] Received brightness level: %d'), (7441460, '[setting][Right Calibration] Received right_calibration: %d'), (7441520, '[setting]advanced_setting is valid, kill_all_feature = %d'), (7484344, '[setting]setting respond to app serialize failed: %d'), (7484456, '[setting]dominant_hand policy: cur=%u new=%u role=%s'), (7484512, '[setting]Updated ring_mac=%02X:%02X:%02X:%02X:%02X:%02X'), (7484568, '[setting]ring_mac not provided by APP, keep local value'), (7484624, '[setting]Received app control device, turn_on_device=%d'), (7484680, '[setting]Device already running, ignore turn_on request'), (7484736, '[setting]LV_EVENT_CLICKED head_up_angle_calibration:%d'), (7527432, '[Brightness Level] Received brightness level: %d'), (7527484, '[Right Calibration] Received right_calibration: %d'), (7527536, '[setting]Received head up calibration switch: %d'), (7527588, '[setting][Setting] Handle silent mode from APP: %s'), (7527692, '[setting]Received gesture control list, count=%d'), (7527744, '[setting]Device not running, start background app'), (7571892, '[setting][Left Calibration] Received level: %d'), (7572036, '[setting]Unexpected ring_mac size %d, ignore'), (7617572, '[setting]setting_parse_data_package failed!'), (7617660, '[setting]-----is_calibration_ui_showing:%d'), (7617704, '[Setting] Handle silent mode from APP: %s'), (7617748, '[setting]No gesture control items received'), (7661556, '[setting]Received auto_adjust value: %d'), (7661596, '[Left Calibration] Received level: %d'), (7661636, '[setting]Unknown brightness type: %d'), (7661676, '[setting]set y_coordinate_level = %d'), (7661716, '[setting]set x_coordinate_level = %d'), (7661756, '[setting]Received head up switch: %d'), (7709004, '[setting]BLE data parsing started'), (7709112, '[setting]Unknown setting type: %d'), (7709256, '[setting]Received head up angle: %d'), (7709400, '[setting]gesture_list_data is NULL'), (7709472, '[setting]dominant_hand_data is NULL'), (7709580, '[setting]setting DISPLAY_STARTUP'), (7755184, '[setting]Processing APP request'), (7755280, '[setting]head_up_data is NULL'), (7755376, '[setting]control_data is NULL'), (7805736, '[setting]pMessage is NULL'), (7805792, '[setting]bri_data is NULL'), (7805988, '[setting]unit_data is NULL'))
EXPECTED = {'body_bytes': 5486, 'body_concat_sha256': '13b18191451e5d05f95435e26e969951641995a98370749e32c36f4ce9829d7f', 'reachable_instructions': 2024, 'reachable_instruction_digest': '2dfcec6fcf9a65f0d6b70b5a53c6330d15b7eac34324237c92433e0c32f4757e', 'direct_body_calls': 361, 'direct_body_call_digest': 'f118d13b2bb6a37a3a1eedd7eb081696b3459be2c9ac7591b0658c0df42e3b6e', 'internal_direct_body_calls': 16, 'outer_pool_bytes': 286, 'outer_pool_sha256': '662eaae7c643e70c8677f56703841a659919fdf881722a8a40d17278d682601d', 'physical_bytes': 5772, 'physical_sha256': '97d60497ba2d7cf29f78db2474bf7f7342167ee97aaf636399981760add024d4', 'path_literal_references': 51}
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
    if any(x.get("path", "").replace("\\", "/").split("/")[-1].lower() == 'setting.c' for x in overlay["sources"]):
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
