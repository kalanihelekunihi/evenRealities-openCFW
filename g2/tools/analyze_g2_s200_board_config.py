#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for product\\s200\\app\\config\\board_config.c."""
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
import apollo_overlay
from apollo_artifact_consistency import validate_apollo_main_artifacts

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-s200-board-config-function-map.tsv"
CL = ROOT / "tools/manifests/g2-s200-board-config-closure.tsv"
PINS = {FM: "34a932a1bc300c05d8b9f505269c266d1cd55a5d5cf6532f915c41099cb95eff", CL: "3f5a2fddfa09d75b593e32d65333f519cca06435f604f61eb310315da8a9135e"}
RETAINED = 'product\\s200\\app\\config\\board_config.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\board_config.c'
PATH_RUN = 0x6f1bdc
CELLS = (5280952,)
CELL_REFS = {5280952: (5280762,)}
ALL_REFS = (5280762,)
F = ((5280724, 5280838),)
PHYS = (5280720, 5281420)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ()
BL_STRICT = ()
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((0x006D1E0C, 0x005093D5),)
GUARD_BEFORE = "7084f1727a10b1ff88209fbec85c2c954bfe19d4b5807431418cd17b3c18ac0e"
GUARD_AFTER = "042c3f59e877e5ca16d3850723b49abfc86bd8895fe853029ad1419987344be4"
TAGS = ((7677288, '[BSP]hw_version: %d, hw_adc_val: %d'),)
EXPECTED = {'body_bytes': 114, 'body_concat_sha256': '80e6eecae3fce4e7ddb3b3b5a82a821a94f3e5e69c8313ba8cd776b101fa5df4', 'reachable_instructions': 46, 'reachable_instruction_digest': '356481648832a7698145c714539bbb331974dd1c86dd5ebc7f97b920c397eeeb', 'direct_body_calls': 9, 'direct_body_call_digest': 'ae365f6bd941a82a89941f6d03a82e595564fb00caaaeca46daf00b3a894e3f2', 'internal_direct_body_calls': 0, 'outer_pool_bytes': 586, 'outer_pool_sha256': '0eb023bfdd6d61149ffe81d0389dc46ab1a3ba80d588b70b8628b435be8388a2', 'physical_bytes': 700, 'physical_sha256': 'befcd26e00da296f7ce7e4e7177a0f686ae9854e8cf437d859f2d5ff75f1f4c3', 'path_literal_references': 1}
SOURCE = ROOT / "components/apollo_main/core_overlay/s200_board_config.c"
HEADER = ROOT / "components/apollo_main/core_overlay/s200_board_config.h"
CONFIG = ROOT / "components/apollo_main/core_overlay/overlay.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_PIN = (1531, "883735e258b8eb6919b4e5e4100e60b5d3637dc7e7959dfcfb72dc8a59cc45bf")
HEADER_PIN = (167, "1e74a14568949bb5e4e7f23771a4eb7a687438fe8f5b4788f7a529310de8416b")
FUNCTION = "open_cfw_s200_board_config_initialize"
PATCH = "replace_s200_board_config_01"
RELOCATIONS = (
    (4, "open_cfw_retained_s200_board_config_record", 0x0050938E),
    (18, "open_cfw_retained_s200_board_config_npmx_init", 0x00512644),
    (26, "open_cfw_bq25180_hardware_init", 0x0053AE7E),
    (30, "open_cfw_bq27427_hardware_init", 0x0053C0FE),
)
ROUTES = {
    "apple-clang": {
        "component": ROOT / "components/apollo_main/core_overlay/build/ota_s200_firmware_ota.bin",
        "report": ROOT / "components/apollo_main/core_overlay/build/build-report.json",
        "overlay": ROOT / "components/apollo_main/core_overlay/build/apollo_core_overlay.bin",
        "component_sha256": "7bfc8a60ab7b057eb98bc5d72569d6712dfada77c8bb54a8ccc22e994b39b2e6",
        "overlay_sha256": "21095c67c3376be1010a7bea19156bae8b1b67bb471525d196c1135d0894f622",
        "overlay_size": 380444,
        "offset": 379016,
        "text_sha256": "c5c905d30b02e99a4da1a0c64b64c55f9d4c5a9790ffcf698c26a6717d7d5cf8",
        "target": 0x007F0BAC,
        "effective_target": 0x004C4A1C,
        "effective_text_sha256": "f3fd180da1ff43ed49db2a940e24264c953697776c574c4d5f76c53f1f38f0b0",
    },
    "linux-clang": {
        "component": ROOT / "build/canonical-provider/linux-clang/apollo_main-final81/ota_s200_firmware_ota.bin",
        "report": ROOT / "build/canonical-observation-g2-final97/linux-b/build-report.json",
        "overlay": ROOT / "build/canonical-observation-g2-final97/linux-b/apollo_core_overlay.bin",
        "component_sha256": "dbfc7bbf1462166b04fb962e9e639ba2296c84a6e0b4f6f22d7ae5e321efc0e6",
        "overlay_sha256": "13a12b7fc7ec3af866d4ebe9229105ce923d6842ec6e8c4b0e01564582ed8ab1",
        "overlay_size": 172828,
        "offset": 163780,
        "text_sha256": "173ebdb089ac94d2ce1161ae276a911a09c8fd808e38951b907353d8923b4934",
        "target": 0x007BC2E8,
        "effective_target": 0x007BC2E8,
        "effective_text_sha256": "173ebdb089ac94d2ce1161ae276a911a09c8fd808e38951b907353d8923b4934",
    },
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


def _validate_production():
    for path, expected, label in ((SOURCE, SOURCE_PIN, "source"),
                                  (HEADER, HEADER_PIN, "header")):
        payload = path.read_bytes()
        if (len(payload), _sh(payload)) != expected:
            raise c.AuditError("S200 board-config production %s changed" % label)

    config = json.loads(CONFIG.read_text())
    leaves = [item for item in config.get("relocated_leaves", [])
              if item.get("function") == FUNCTION]
    if len(leaves) != 1:
        raise c.AuditError("S200 board-config production leaf inventory changed")
    leaf = leaves[0]
    linux = leaf.get("toolchain_profiles", {}).get("linux-clang", {})
    for observed in (leaf.get("relocations", []), linux.get("relocations", [])):
        compact = tuple((item.get("offset"), item.get("symbol"),
                         item.get("target_address")) for item in observed)
        if compact != RELOCATIONS or any(
                item.get("type") != "R_ARM_THM_CALL"
                or item.get("symbol_type") != "STT_NOTYPE" for item in observed):
            raise c.AuditError("S200 board-config relocation closure changed")
    if (leaf.get("profiles") != ["apple-clang", "linux-clang"]
            or leaf.get("strict_relocation_contract") is not True
            or leaf.get("source", {}).get("sha256") != SOURCE_PIN[1]
            or leaf.get("expected", {}).get("offset") != 379016
            or leaf.get("expected", {}).get("size") != 38
            or leaf.get("expected", {}).get("sha256") != ROUTES["apple-clang"]["text_sha256"]
            or leaf.get("expected", {}).get("unrelocated_sha256") != "d34b94dfab51da6721caad566197326337e2e494017854242c15a2d42388e910"
            or linux.get("reviewed_version_prefix") != "Homebrew clang version 22.1.8"
            or linux.get("expected", {}).get("offset") != 163780
            or linux.get("expected", {}).get("size") != 38
            or linux.get("expected", {}).get("sha256") != ROUTES["linux-clang"]["text_sha256"]
            or linux.get("expected", {}).get("unrelocated_sha256") != "d34b94dfab51da6721caad566197326337e2e494017854242c15a2d42388e910"):
        raise c.AuditError("S200 board-config production pins changed")

    patches = [item for item in config.get("patch_sites", [])
               if item.get("name") == PATCH]
    if len(patches) != 1:
        raise c.AuditError("S200 board-config patch inventory changed")
    patch = patches[0]
    if (patch.get("runtime_address") != F[0][0]
            or patch.get("expected_size") != EXPECTED["body_bytes"]
            or patch.get("expected_sha256") != EXPECTED["body_concat_sha256"]
            or patch.get("target_function") != FUNCTION
            or patch.get("profiles") != ["apple-clang", "linux-clang"]):
        raise c.AuditError("S200 board-config patch contract changed")

    manifest = json.loads(MANIFEST.read_text())["component_overrides"]["apollo_main"]
    stock_offset = F[0][0] - c.BASE
    owners = [region for region in manifest["regions"]
              if region.get("file_offset", -1) <= stock_offset
              < region.get("file_offset", -1) + region.get("size", 0)]
    if len(owners) != 1 or owners[0].get("address_status") not in {
            "generated_source_entry_replacement", "generated_source_data_replacement"}:
        raise c.AuditError("S200 board-config manifest entry ownership changed")

    for profile, route in ROUTES.items():
        component = route["component"].read_bytes()
        overlay = route["overlay"].read_bytes()
        if len(component) != 3956672 or _sh(component) != route["component_sha256"]:
            raise c.AuditError("%s S200 board-config component changed" % profile)
        if len(overlay) != route["overlay_size"] or _sh(overlay) != route["overlay_sha256"]:
            raise c.AuditError("%s S200 board-config overlay changed" % profile)
        text = overlay[route["offset"]:route["offset"] + 38]
        if len(text) != 38 or _sh(text) != route["text_sha256"]:
            raise c.AuditError("%s S200 board-config compiled text changed" % profile)
        report = json.loads(route["report"].read_text())
        built = [item.get("extraction", {}) for item in report.get("relocated_leaves", [])
                 if item.get("extraction", {}).get("function") == FUNCTION]
        if len(built) != 1:
            raise c.AuditError("%s S200 board-config report inventory changed" % profile)
        extraction = built[0]
        if (extraction.get("runtime_address") != route["target"]
                or extraction.get("size") != 38
                or extraction.get("sha256") != route["text_sha256"]
                or extraction.get("unrelocated_sha256") != "d34b94dfab51da6721caad566197326337e2e494017854242c15a2d42388e910"
                or extraction.get("relocation_count") != 4):
            raise c.AuditError("%s S200 board-config build receipt changed" % profile)
        replacement = c._slice(component, *F[0])
        if (apollo_overlay.decode_thumb_branch(F[0][0], replacement[:4], link=False)
                != route["effective_target"]
                or replacement[4:] != b"\x00\xbf" * ((len(replacement) - 4) // 2)):
            raise c.AuditError("%s S200 board-config redirect changed" % profile)
        effective = c._slice(component, route["effective_target"],
                             route["effective_target"] + 38)
        if _sh(effective) != route["effective_text_sha256"]:
            raise c.AuditError("%s S200 board-config effective text changed" % profile)
        seen, calls, escapes, indirect = _recover(
            component, route["effective_target"], route["effective_target"] + 38)
        call_contract = tuple((site - route["effective_target"], target)
                              for site, target in sorted(calls))
        if (len(seen) != 15 or escapes or indirect
                or call_contract != tuple((offset, target)
                                          for offset, _symbol, target in RELOCATIONS)):
            raise c.AuditError("%s S200 board-config effective call closure changed" % profile)

    validate_apollo_main_artifacts(ROOT, c.AuditError, "production S200 board-config")
    return {
        "candidate": str(SOURCE.relative_to(ROOT)),
        "header": str(HEADER.relative_to(ROOT)),
        "production_routed": True,
        "ownership_bytes": 114,
        "source_inventory_available": True,
        "source_functions": 1,
        "compiled_text_bytes": {"apple-clang": 38, "linux-clang": 38},
        "alignment_bytes": {"apple-clang": 0, "linux-clang": 0},
        "strict_relocations": 4,
        "stock_body_bytes_displaced": 114,
        "retained_stock_noncode_bytes": 586,
        "profiles_verified": ["apple-clang", "linux-clang"],
        "software_functional_gap": False,
        "hardware_validation": "blocked by unavailable physical evidence",
        "hardware_evidence_required": [
            "authorized G2 examples of both supported charger families, or authenticated golden traces, proving selector-3 record decoding, nPMx versus BQ dispatch, BQ25180-before-BQ27427 ordering, and resulting rail, charging, and fuel-gauge behavior"
        ],
        "hardware_operations": [],
    }


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
    production = _validate_production()
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor linked-object closure",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": production,
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
