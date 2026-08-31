#!/usr/bin/env python3
"""Fail-closed zero-anchor linked-object audit for platform\\device_mgr\\box_uart_mgr.c."""
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
FM = ROOT / "tools/manifests/g2-box-uart-mgr-function-map.tsv"
CL = ROOT / "tools/manifests/g2-box-uart-mgr-closure.tsv"
SOURCE = ROOT / "components/apollo_main/core_overlay/box_uart_mgr.c"
SOURCE_PATH = "components/apollo_main/core_overlay/box_uart_mgr.c"
SOURCE_SHA256 = "d7d419940733206f76e8d8661d261f3d0eb7435f2975315274c072b99e1f1ae2"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
BUILD_REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
PACKAGE = ROOT / "build/source/package/g2-openCFW-s200_v2.2.6.10-core-source.evenota.bin"
FLASH_PLAN = ROOT / "build/source/flash-plan.json"
PINS = {FM: "59b450ae9ad9341eef8350bdb74d425df7cb44d73845801e85603d9ede19005a", CL: "eb746be4c575f1214c91bed99e3cc8c573579106c7a4ab0ee645213346a13356"}
RETAINED = 'platform\\device_mgr\\box_uart_mgr.c'
FULL_PATH = 'D:\\01_workspace\\s200_ap510b_iar_git\\platform\\device_mgr\\box_uart_mgr.c'
PATH_RUN = 0x6f890c
CELLS = (5481388,)
CELL_REFS = {5481388: (5480126, 5480358, 5480666, 5480780, 5480854, 5480930, 5481014, 5481100, 5481174, 5481246, 5481332)}
ALL_REFS = (5480126, 5480358, 5480666, 5480780, 5480854, 5480930, 5481014, 5481100, 5481174, 5481246, 5481332)
F = ((5480082, 5480464), (5480464, 5480476), (5480476, 5480604), (5480604, 5480630), (5480630, 5481380))
PHYS = (5480082, 5481492)
FOREIGN = ()
ESCAPES = ()
INDIRECT = ()
BL_ENTRY = ((5006494, 5480604), (5481070, 5480464))
BL_STRICT = ((4497154, 5480644), (4497416, 5480906), (5480900, 5480084))
PSEUDO_BL_STRICT = ((4497154, 5480644), (4497416, 5480906))
LIVE_BL_STRICT = ((5480900, 5480084),)
BW_ENTRY = ()
B16_ENTRY = ()
STORED_RAW = ((5481420, 5480477), (7639240, 5480631))
ROUTES = (
    ("replace_box_uart_mgr_01", "open_cfw_box_uart_unpack", 0x00539E94, 0x0053A010),
    ("replace_box_uart_mgr_02", "open_cfw_box_uart_send", 0x0053A010, 0x0053A01C),
    ("replace_box_uart_mgr_03", "open_cfw_box_uart_receive", 0x0053A01C, 0x0053A09C),
    ("replace_box_uart_mgr_04", "open_cfw_box_uart_init", 0x0053A09C, 0x0053A0B6),
    ("replace_box_uart_mgr_05", "open_cfw_box_uart_handle", 0x0053A0B6, 0x0053A3A4),
)
GUARD_BEFORE = "0cd1f72ddf9ec8f332e3c7568687371e5ad77107efb0b3c50001834452cd8df1"
GUARD_AFTER = "228adbf7d252de6592988f87b5bfebde50f62cf4a046165238a8bcbf185f6522"
TAGS = ((7195412, '[box_uart_mgr]crc check failed, data len = %d, tmp_crc: 0x%x, tmp_buf[idx + tmp_len - 1]: 0x%x'), (7587696, '[box_uart_mgr]uart clear buffer failed: %d\n'), (7634676, '[box_uart_mgr]box uart unpack err:%d\n'), (7634716, '[box_uart_mgr]uart tx flush failed: %d\n'), (7634756, '[box_uart_mgr]uart start failed: %d\n'), (7634796, '[box_uart_mgr]pt cmd execute err:%d\n'), (7677468, '[box_uart_mgr]uart stop failed: %d\n'), (7677504, '[box_uart_mgr]box uart pack err:%d\n'), (7677540, '[box_uart_mgr]box uart send err:%d\n'), (7726288, '[box_uart_mgr]box rcv msg err\n'))
EXPECTED = {'body_bytes': 1298, 'body_concat_sha256': '08fc6828806a6830c6542c27e7349505643a6c3d61d40f31f0c6cc1321b7832d', 'reachable_instructions': 502, 'reachable_instruction_digest': 'bb062c5f970b49a3ee1a6e8c5d617a79a550903081e2d02a9d758c9977e643b0', 'direct_body_calls': 75, 'direct_body_call_digest': '6405f5be1f8f2eac027b6790e5ac9cb3e2b8f70e1fe26149b215ed1d4ff87e42', 'internal_direct_body_calls': 1, 'outer_pool_bytes': 112, 'outer_pool_sha256': 'b3c5f4efa6adef47bed35d84667ee452239a75e2c37ad0741721a7eb89433a6b', 'physical_bytes': 1410, 'physical_sha256': '6e1ba9470189a6da0abe61010fc201a96f846d2933336a59f74227a83d55d7a3', 'path_literal_references': 11}
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
    if tuple(bls[:2]) != PSEUDO_BL_STRICT or tuple(bls[2:]) != LIVE_BL_STRICT:
        raise c.AuditError("strict-interior pseudo-decode classification changed")

    overlay = json.loads(OVERLAY.read_text())
    if _sh(SOURCE.read_bytes()) != SOURCE_SHA256:
        raise c.AuditError("case-UART production source changed")
    leaves = [
        item for item in overlay["relocated_leaves"]
        if item.get("source", {}).get("path") == SOURCE_PATH
    ]
    if len(leaves) != len(ROUTES) or any(
        item.get("source", {}).get("sha256") != SOURCE_SHA256
        for item in leaves
    ):
        raise c.AuditError("case-UART production source inventory changed")
    sites = {item["name"]: item for item in overlay["patch_sites"]}
    routed = 0
    for name, function, start, end in ROUTES:
        site = sites.get(name)
        if (
            site is None
            or site.get("runtime_address") != start
            or site.get("target_function") != function
            or site.get("branch") != "b_w"
            or site.get("expected_size") != end - start
            or site.get("expected_sha256") != _sh(c._slice(blob, start, end))
            or function not in overlay["functions"]
        ):
            raise c.AuditError("case-UART production route changed: " + name)
        routed += end - start
    compiled = sum(item["expected"]["size"] for item in leaves)
    alignment = sum(
        leaves[index + 1]["expected"]["offset"]
        - leaves[index]["expected"]["offset"]
        - leaves[index]["expected"]["size"]
        for index in range(len(leaves) - 1)
    )
    relocations = sum(len(item["relocations"]) for item in leaves)
    if (compiled, alignment, relocations, routed) != (514, 4, 21, 1296):
        raise c.AuditError("case-UART production metrics changed")

    report = json.loads(BUILD_REPORT.read_text())
    if (
        report["overlay"]["size"] != 362272
        or report["overlay"]["sha256"] != "8c80c3fa53a89c77d145533f59f63389dfa31f968642f783323ed81ac81be5ae"
        or report["component"]["size"] != 3885668
        or report["component"]["sha256"] != "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5"
    ):
        raise c.AuditError("case-UART production component changed")
    report_leaves = [
        item for item in report["relocated_leaves"]
        if item.get("source", {}).get("path") == SOURCE_PATH
    ]
    if len(report_leaves) != 5 or sum(
        item["extraction"]["relocation_count"] for item in report_leaves
    ) != 21:
        raise c.AuditError("case-UART built leaf inventory changed")

    manifest = json.loads(MANIFEST.read_text())
    provider = manifest["component_overrides"]["apollo_main"]["provider"]
    regions = manifest["component_overrides"]["apollo_main"]["regions"]
    if (
        provider.get("size") != 3885668
        or provider.get("sha256") != "898d5efb1430dc0c3e0b8b7e26823a653952114ffeab0d3ae6e89d8925301ef5"
        or len([item for item in regions if item["name"].startswith("box_uart_mgr_")]) != 12
    ):
        raise c.AuditError("case-UART package ownership manifest changed")
    if (
        PACKAGE.stat().st_size != 4678740
        or _sh(PACKAGE.read_bytes()) != "d569793138c6bc2ee456536daee59dcef0bb6051034ed966f7144083790a777a"
    ):
        raise c.AuditError("case-UART production package changed")
    flash = json.loads(FLASH_PLAN.read_text())
    if (
        FLASH_PLAN.stat().st_size != 4586947
        or _sh(FLASH_PLAN.read_bytes()) != "0180ded6475c22f46ec79dd4985c8194d73f67f9827100dc5c2358f204da8f55"
        or (
            len(flash["flash_regions"]),
            len(flash["unresolved_flash_regions"]),
            len(flash["container_only_regions"]),
            len(flash["protected_regions"]),
            ) != (6586, 0, 6, 6)
    ):
        raise c.AuditError("case-UART production flash plan changed")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only zero-anchor linked-object closure",
        "identity": {"disposition": "linked-unanchored", "ghidra_discovered_functions": 0, "image_sha256": c.IMAGE_SHA256, "path_anchored_functions": 0, "retained_path": RETAINED, "retained_product_path": FULL_PATH},
        "surface": {"body_bytes": EXPECTED["body_bytes"], "direct_body_calls": EXPECTED["direct_body_calls"], "function_escapes": len(esc), "indirect_body_calls": len(ind), "internal_direct_body_calls": EXPECTED["internal_direct_body_calls"], "linked_functions": len(F), "outer_pool_bytes": EXPECTED["outer_pool_bytes"], "path_literal_references": EXPECTED["path_literal_references"], "physical_bytes": EXPECTED["physical_bytes"], "raw_path_referencing_functions": sum(1 for row in rows if int(row["path_reference_sites"]) > 0), "reachable_instructions": EXPECTED["reachable_instructions"]},
        "ingress": {"direct_b16_entry_sites": len(b16), "direct_bl_entry_sites": len(bl), "direct_bl_strict_interior_sites": len(bls), "strict_interior_overlapping_pseudo_decodes": len(PSEUDO_BL_STRICT), "strict_interior_live_internal_calls": len(LIVE_BL_STRICT), "direct_bw_entry_sites": len(bw), "stored_entry_pointer_words": len(stored)},
        "evidence": {"boundary_guards": True, "pointer_cells": ["0x%08X" % x for x in CELLS], "path_string_run_address": "0x%08X" % PATH_RUN, "tag_strings": len(TAGS)},
        "production": {"production_routed": True, "source_files": 1, "source_functions": len(leaves), "compiled_text_bytes": compiled, "alignment_bytes": alignment, "strict_relocations": relocations, "guarded_redirects": len(ROUTES), "routed_stock_bytes": routed, "retained_compatibility_bytes": PHYS[1] - PHYS[0] - routed, "package_size": PACKAGE.stat().st_size, "placed_flash_regions": len(flash["flash_regions"])},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
