#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for platform\\input\\service_gesture_processor.c."""
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
FM = ROOT / "tools/manifests/g2-service-gesture-processor-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-gesture-processor-closure.tsv"
PV = ROOT / "tools/manifests/g2-service-gesture-processor-provenance.tsv"
PINS = {
    FM: "9cba1744560a8e25c60baae07d8b636af0fae55f19c03194e5049f255333e1c2",
    CL: "781ba37e4979b5f5f659f176625fcae78d4dcaf59d6f7eeee1d6173adc15276e",
    PV: "bd7d38a01eb33a3b0f08e894d8b02fe282a151c1338e56906670179f3d3298f8",
}
RETAINED = 'platform\\input\\service_gesture_processor.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\platform\\input\\service_gesture_processor.c'
PATH_RUN = 0x6ef958
CELLS = (5255736,)
CELL_REFS = {5255736: (5254528, 5255112, 5255248, 5255398, 5255484)}
ALL_REFS = (5254528, 5255112, 5255248, 5255398, 5255484)
F = ((5254486, 5254574), (5254574, 5254582), (5254582, 5254594), (5254594, 5254894), (5254900, 5255728))
PHYS = (5254486, 5255832)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((4845418, 5254574), (5255048, 5254594), (5255142, 5254594), (5255226, 5254582), (5255278, 5254582), (5255364, 5254594), (5255428, 5254594), (5321016, 5254900), (5711308, 5254574), (5711328, 5254574), (5711382, 5254574))
BL_STRICT = ((5255346, 5254488),)
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ()
GUARD_BEFORE = "2bc01ec5e95e2923011a467ec0482e180f244638f4d97437441eaa09e8d4b6e5"
GUARD_AFTER = "e58e99b80491e982182e598ebccec8d3442b4d7f56fcdea42907fb20ff0f259c"
TAGS = ((7182708, '[touch.ges]prox:%d, bsln:%5d, kv_bsln:%5d, raw:%5d, diff:%4d, diffX:%3d, speed:%3d, slider:(0x%02x)%s'), (7439780, '[touch.ges]slider mask = 0x%02x(%s), diffX = %d, speed = %d'), (7615064, '[touch.ges]SLIDER_EVENT_ERROR: reset touch'), (7659116, '[touch.ges]EVENT_SLIDER_SINGLE_CLICK'), (7845972, '[touch.ges]prox=%s(%u)'))
EXPECTED = {'body_bytes': 1236, 'body_concat_sha256': 'f186aaeacbf76358d14fffade60bd89d5d96ba461ab532fad46e42f7adad8e67', 'reachable_instructions': 501, 'reachable_instruction_digest': '67bf73953599ffd053c5576edd27780218b5945dedfac9b5968b6d53959bb7d9', 'direct_body_calls': 68, 'direct_body_call_digest': 'e4ded3f6a231435d565dec70a0c0042b209c8088357e2badda8d9bef62f18bc4', 'internal_direct_body_calls': 6, 'outer_pool_bytes': 110, 'outer_pool_sha256': 'ce96250122876b614088497597f95efcf99727bbfc28a719668174540087c515', 'physical_bytes': 1346, 'physical_sha256': 'e6275f41dcacabc796afb33e5ba14d76129076334014119879f80344e32904cf', 'path_literal_references': 5}
PRODUCTION_SOURCE = ROOT / "components/apollo_main/core_overlay/service_gesture_processor.c"
OVERLAY_CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
OVERLAY_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
SOURCE_MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PRODUCTION_SOURCE_PIN = (13052, "da9cf1e010d0d736c3782d59204993cf074d3d82105412e5fd40d90b8b1d9cc5")
LEAF_PINS = {
    "open_cfw_gesture_production_click": (118, "8d5df040247142cdc8888e431baeb7edd824a01ac17a1043d60df20dda4ad933", 188812, "1a927d88a6295264f535e25a76ff34d32c63f3ba34fb3976e737b90eceb722af", 6, 0),
    "open_cfw_gesture_get_proximity": (12, "4b5de0babb48e1a66b99f96e9decf025811db259bf84ce9b218d4fae69632b4d", 188932, "4b5de0babb48e1a66b99f96e9decf025811db259bf84ce9b218d4fae69632b4d", 0, 2),
    "open_cfw_gesture_event_name": (14, "06d8bd8223342f79f986e0e2f8cfa030d14cac1d49f1f88d7e1480429a3902fa", 188944, "06d8bd8223342f79f986e0e2f8cfa030d14cac1d49f1f88d7e1480429a3902fa", 0, 0),
    "open_cfw_gesture_format_mask": (586, "08f7ac2057cf30be8389d8e2a8ede4de74ea02d4f282136e3e2557acecfe0c76", 188960, "08f7ac2057cf30be8389d8e2a8ede4de74ea02d4f282136e3e2557acecfe0c76", 0, 2),
    "open_cfw_gesture_process": (878, "1f8f5af41a31b17ee71a36c0927dfca419eefc864002efb06efbe186bc8be438", 189548, "bb6df8074642bd52fd73485f4350ac7afe2b8be99da7e4b09861b4f558e65397", 47, 2),
}
PATCH_PINS = {
    "replace_gesture_production_click": (0x00502D56, 88, "b9c55e0c9d939dbff58ce1aa4ad91209f714c6435f4ff654e9e869aa921c71a8", "open_cfw_gesture_production_click"),
    "replace_gesture_get_proximity": (0x00502DAE, 8, "b0b65aa4b0b432c33fd6590774165cafc3afa6a4f4fdc43e6341cbaed467b44c", "open_cfw_gesture_get_proximity"),
    "replace_gesture_event_name": (0x00502DB6, 12, "6ca0a840c9b5efbaa84e75741a8f559f5f3202d43718f76f0e15dd2e49a55d01", "open_cfw_gesture_event_name"),
    "replace_gesture_format_mask": (0x00502DC2, 306, "8547b6ea3fc608b92b8187fd93f081ffc3869985cc1cca493ecd471ad4463b7e", "open_cfw_gesture_format_mask"),
    "replace_gesture_process": (0x00502EF4, 932, "86795b9e46101113d97297579064958c76f33ad4973ed691d6ba2bea3e91517f", "open_cfw_gesture_process"),
}
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
    source = PRODUCTION_SOURCE.read_bytes()
    if (len(source), _sh(source)) != PRODUCTION_SOURCE_PIN:
        raise c.AuditError("production gesture source changed")
    overlay = json.loads(OVERLAY_CONFIG.read_text())
    leaves = {
        item.get("function"): item
        for item in overlay.get("relocated_leaves", [])
        if item.get("function") in LEAF_PINS
    }
    if set(leaves) != set(LEAF_PINS) or not set(LEAF_PINS) <= set(overlay["functions"]):
        raise c.AuditError("production gesture leaf inventory changed")
    external_targets = {
        "open_cfw_retained_gesture_log_level": 0x0043D0CE,
        "open_cfw_retained_gesture_log": 0x0043D574,
        "open_cfw_retained_gesture_trace": 0x0043CE9E,
        "open_cfw_retained_gesture_hexdump": 0x00475D78,
        "open_cfw_retained_gesture_touch_read": 0x0055B676,
        "open_cfw_retained_gesture_touch_stop": 0x0055B64A,
        "open_cfw_retained_gesture_touch_prepare_baseline": 0x0055B6DC,
        "open_cfw_retained_gesture_product_mode": 0x004ABE60,
        "open_cfw_retained_gesture_buzzer_play": 0x00502BF0,
        "open_cfw_retained_gesture_proximity_notify": 0x0049EAE2,
        "open_cfw_retained_gesture_timestamp": 0x004C5874,
        "open_cfw_retained_gesture_publish": 0x004C5916,
    }
    sibling_targets = {
        "open_cfw_gesture_production_click",
        "open_cfw_gesture_event_name",
        "open_cfw_gesture_format_mask",
    }
    expected_offsets = {
        "open_cfw_gesture_production_click": (0x0E, 0x12, 0x46, 0x4A, 0x52, 0x72),
        "open_cfw_gesture_get_proximity": (),
        "open_cfw_gesture_event_name": (),
        "open_cfw_gesture_format_mask": (),
        "open_cfw_gesture_process": (
            0x1A, 0x26, 0x4E, 0x6E, 0xBA, 0xBE, 0xC6, 0xE0,
            0x108, 0x112, 0x11C, 0x14A, 0x14E, 0x156, 0x160,
            0x17C, 0x190, 0x19C, 0x1A8, 0x1B2, 0x1BC, 0x1F4,
            0x1F8, 0x200, 0x20A, 0x226, 0x23A, 0x246, 0x25E,
            0x28E, 0x292, 0x29A, 0x2B0, 0x2B4, 0x2BA, 0x2CE,
            0x2DA, 0x2FE, 0x30A, 0x314, 0x320, 0x32A, 0x336,
            0x340, 0x34C, 0x356, 0x362,
        ),
    }
    for name, pin in LEAF_PINS.items():
        leaf = leaves[name]
        expected = leaf.get("expected", {})
        relocations = leaf.get("relocations", [])
        source_record = leaf.get("source", {})
        if (
            leaf.get("profiles") != ["apple-clang"]
            or not leaf.get("strict_relocation_contract")
            or source_record.get("path") != "components/apollo_main/core_overlay/service_gesture_processor.c"
            or (source_record.get("size"), source_record.get("sha256")) != PRODUCTION_SOURCE_PIN
            or (
                expected.get("size"), expected.get("sha256"),
                expected.get("alignment"), expected.get("offset"),
                expected.get("unrelocated_sha256"), len(relocations),
            ) != (pin[0], pin[1], 4, pin[2], pin[3], pin[4])
            or tuple(item.get("offset") for item in relocations) != expected_offsets[name]
        ):
            raise c.AuditError("production gesture leaf changed: " + name)
        for item in relocations:
            symbol = item.get("symbol")
            expected_type = (
                "R_ARM_THM_JUMP24"
                if name == "open_cfw_gesture_production_click" and item.get("offset") == 0x72
                else "R_ARM_THM_CALL"
            )
            if item.get("type") != expected_type or item.get("symbol_type") != "STT_NOTYPE":
                raise c.AuditError("production gesture relocation type changed")
            if symbol in external_targets:
                if item.get("target_address") != external_targets[symbol] or "target_function" in item:
                    raise c.AuditError("production gesture retained target changed")
            elif symbol in sibling_targets:
                if item.get("target_function") != symbol or "target_address" in item:
                    raise c.AuditError("production gesture sibling target changed")
            else:
                raise c.AuditError("unknown production gesture relocation")

    patches = {
        item.get("name"): item
        for item in overlay.get("patch_sites", [])
        if item.get("name") in PATCH_PINS
    }
    if set(patches) != set(PATCH_PINS):
        raise c.AuditError("production gesture patch inventory changed")
    for name, pin in PATCH_PINS.items():
        patch = patches[name]
        if (
            patch.get("runtime_address"), patch.get("expected_size"),
            patch.get("expected_sha256"), patch.get("target_function"),
            patch.get("branch"), patch.get("profiles"),
        ) != (pin[0], pin[1], pin[2], pin[3], "b_w", ["apple-clang"]):
            raise c.AuditError("production gesture patch changed: " + name)

    build = json.loads(OVERLAY_REPORT.read_text())
    validate_apollo_main_artifacts(ROOT, c.AuditError, "gesture processor")
    built = {
        item.get("extraction", {}).get("function"): item
        for item in build.get("relocated_leaves", [])
        if item.get("extraction", {}).get("function") in LEAF_PINS
    }
    if set(built) != set(LEAF_PINS):
        raise c.AuditError("production gesture compiled inventory changed")
    for name, pin in LEAF_PINS.items():
        record = built[name]
        if (
            record["placement"].get("size"),
            record["placement"].get("padding_before"),
            record["extraction"].get("relocation_count"),
        ) != (pin[0], pin[5], pin[4]):
            raise c.AuditError("production gesture compiled closure changed")

    manifest = json.loads(SOURCE_MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = {item.get("name"): item for item in main["regions"]}
    source_regions = {
        "gesture_production_click_source_text": (3712208, 118, 0x007C24B0),
        "gesture_get_proximity_source_text": (3712328, 12, 0x007C2528),
        "gesture_event_name_source_text": (3712340, 14, 0x007C2534),
        "gesture_format_mask_source_text": (3712356, 586, 0x007C2544),
        "gesture_process_source_text": (3712944, 878, 0x007C2790),
    }
    for name, pin in source_regions.items():
        region = regions.get(name, {})
        if (
            region.get("file_offset"), region.get("size"),
            region.get("target_address"), region.get("address_status"),
        ) != (*pin, "source_compiled"):
            raise c.AuditError("production gesture manifest source region changed")
    for name, pin in PATCH_PINS.items():
        region_name = name.removeprefix("replace_") + "_source_replacement"
        region = regions.get(region_name, {})
        if (
            region.get("size"), region.get("target_address"),
            region.get("address_status"),
        ) != (pin[1], pin[0], "generated_source_entry_replacement"):
            raise c.AuditError("production gesture manifest replacement changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor linked-object closure",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": {
            "candidate": "components/apollo_main/core_overlay/service_gesture_processor.c",
            "production_routed": True,
            "ownership_bytes": 2954,
            "source_inventory_available": True,
            "source_functions": 5,
            "compiled_text_bytes": 1608,
            "alignment_bytes": 6,
            "stock_replaced_bytes": 1346,
            "strict_relocations": 53,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "Authorized physical G2 touch/proximity device or captured "
                "gesture electrical/event/timing evidence is required for future qualification."
            ),
        },
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
