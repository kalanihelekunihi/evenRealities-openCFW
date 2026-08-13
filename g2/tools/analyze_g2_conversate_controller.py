#!/usr/bin/env python3
"""Fail-closed object/provider audit for app/gui/conversate/conversate.c."""

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
import recover_apollo_embedded_source_paths as paths

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-conversate-controller-function-map.tsv"
PM = ROOT / "tools/manifests/g2-conversate-controller-provider-map.tsv"
CL = ROOT / "tools/manifests/g2-conversate-controller-closure.tsv"
PINS = {
    FM: "bcf116dbbaaa750046057201fb54831d67bbd14dd48facf8833685e10ff596c5",
    PM: "3f5ebf4dac39e471b6496241f0138a6afdb701bd4861259de786515a02a0dcf2",
    CL: "8764f4f2f9a62802c6d303f636f2c75c191ad40d43a2a6e2cbcc7ce93a2f46cc",
}
PHYSICAL = (0x005B0114, 0x005B0B58)
EASYLOGGER = {0x0043CE9E, 0x0043D0CE, 0x0043D574}
IAR = {0x00439BE4, 0x0043C0E4}
CMSIS = {0x004490CC, 0x0044971C, 0x004497B6, 0x0044981C}
LVGL = {0x00441488}
NANOPB = {0x0048EB32}
EABI = {0x0047CC60}
CMBACKTRACE = {0x005944BC}
FIRST_PARTY = {
    0x004434D0, 0x0045A568, 0x00464BB2, 0x00478110, 0x00478252,
    0x0054F50E, 0x0059624E, 0x005B14CE, 0x005B156C, 0x005B15E0,
    0x005B16D0, 0x005B16FC, 0x005B1724, 0x005B1B4C, 0x005B1D2A,
    0x005B200E, 0x005B23AE, 0x005B3D62, 0x005B430E, 0x005B43D4,
    0x005B473A, 0x005B4904,
}
EXPECTED_STORED = [
    (0x0043800C, 0x005B0115),
    (0x006A44D4, 0x005B0477),
    (0x006A44D8, 0x005B06AB),
    (0x00791B0B, 0x005B05D1),
]
EXPECTED_INTERIOR_COLLISIONS = [
    (0x0055C470, 0x005B085B), (0x0055E14A, 0x005B085B),
    (0x0058E218, 0x005B085B), (0x0058FE38, 0x005B085B),
    (0x00591E18, 0x005B085B), (0x00591E32, 0x005B085B),
    (0x005921EA, 0x005B085B), (0x00643427, 0x005B03FF),
]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def cstring(blob: bytes, address: int) -> str:
    offset = address - common.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise common.AuditError("unterminated retained path")
    return blob[offset:end].decode("ascii")


def analyze(image: Path = IMAGE) -> dict:
    blob = image.read_bytes()
    if len(blob) != common.IMAGE_SIZE or sha(blob) != common.IMAGE_SHA256:
        raise common.AuditError("image changed")
    for manifest, digest in PINS.items():
        if sha(manifest.read_bytes()) != digest:
            raise common.AuditError(f"manifest changed: {manifest.name}")
    for provenance, commit in (
        (ROOT / "third_party/easylogger/PROVENANCE.json", "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24"),
        (ROOT / "third_party/lvgl/PROVENANCE.json", "344c7c318047b7348e1be8572a9fd4260c251cfa"),
        (ROOT / "third_party/cmbacktrace/PROVENANCE.json", "73714489f9d8af130aacb515586b397b604a5768"),
    ):
        if json.loads(provenance.read_text())["upstream"]["selected_commit"] != commit:
            raise common.AuditError(f"provider provenance changed: {provenance.parent.name}")

    with FM.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    functions = [(int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)) for row in rows]
    if len(functions) != 12 or sum(row["source_path_anchor"] == "yes" for row in rows) != 9:
        raise common.AuditError("function inventory changed")
    starts = {start for start, _ in functions}
    interiors = set()
    instructions = {}
    calls = []
    indirect = []
    bodies = []
    decoder = cfg.Cs(cfg.CS_ARCH_ARM, cfg.CS_MODE_THUMB | cfg.CS_MODE_LITTLE_ENDIAN | cfg.CS_MODE_MCLASS)
    for index, (row, (start, end)) in enumerate(zip(rows, functions)):
        raw = common._slice(blob, start, end)
        if sha(raw) != row["stock_sha256"]:
            raise common.AuditError(f"function changed at 0x{start:08X}")
        if index < 2:
            decoded = list(decoder.disasm(raw, start))
            if sum(insn.size for insn in decoded) != len(raw):
                raise common.AuditError("fatal-entry decode changed")
            recovered = {insn.address: insn for insn in decoded}
            direct = [(0x005B0118, 0x005944BC)] if index == 0 else [(0x005B011C, 0x005B011C)]
            dynamic = []
        else:
            recovered, direct, dynamic = cfg._recover_function(blob, start, end)
            if common._uncovered((start, end), recovered):
                raise common.AuditError(f"control-flow coverage changed at 0x{start:08X}")
        bodies.append(raw)
        instructions.update(recovered)
        calls.extend(direct)
        indirect.extend(dynamic)
        interiors.update(range(start + 2, end, 2))
    body = b"".join(bodies)
    calls.sort()
    indirect.sort()
    if len(body) != 2250 or sha(body) != "7aa3437ffd474ec766826acce344af4495aba0eb20fbf2fb3a3a68770df03086":
        raise common.AuditError("body closure changed")
    if len(instructions) != 845 or common._instruction_digest(sorted((address, insn.size) for address, insn in instructions.items())) != "cb23ed88ead58f08bb023276adeb04ecf3dbc4bf262707df6dae0c62a951534a":
        raise common.AuditError("instruction closure changed")
    if indirect:
        raise common.AuditError("indirect call appeared")

    noncode = bytearray()
    cursor = PHYSICAL[0]
    for start, end in functions:
        if start > cursor:
            noncode.extend(common._slice(blob, cursor, start))
        cursor = end
    noncode.extend(common._slice(blob, cursor, PHYSICAL[1]))
    if len(noncode) != 378 or sha(bytes(noncode)) != "6dca6ea8fc70c17bd6e7bf62ec9910027ff907f9a149706bb9ccb212cb21b6ad":
        raise common.AuditError("noncode closure changed")
    if sha(common._slice(blob, *PHYSICAL)) != "9dad2a5945df6f0a76a0c78da9f52f86f3144b29ffd3e897c0bd03d0719c180f":
        raise common.AuditError("physical closure changed")
    if sha(common._slice(blob, PHYSICAL[0] - 16, PHYSICAL[0])) != "81a2ae1112f94892c9488862126dfd74f9e4eda9266857e3910fc336541a48ba" or sha(common._slice(blob, PHYSICAL[1], PHYSICAL[1] + 16)) != "4719079d0e39bc448cb16cb38cff7b400aba0d9818a412df9efea6f403ddd42d":
        raise common.AuditError("object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    groups = (EASYLOGGER, IAR, CMSIS, LVGL, NANOPB, EABI, CMBACKTRACE, FIRST_PARTY)
    expected_counts = (80, 4, 7, 2, 3, 1, 1, 41)
    if len(calls) != 152 or sum(target in starts for _, target in calls) != 13 or common._pair_digest(calls) != "c15a3074732bc876aa34c01d0ba92ad6b25a257d1a740539f9dbadc9748f53e6":
        raise common.AuditError("direct call closure changed")
    if set(external) != set().union(*groups) or tuple(sum(external[target] for target in group) for group in groups) != expected_counts:
        raise common.AuditError("provider boundary changed")

    entries = []
    strict = []
    for address in range(common.BASE, common.BASE + len(blob) - 3, 2):
        target = paths._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 46 or common._pair_digest(entries) != "89fee70257646f101f150250da80d680be61a4569d9d749f2caf874a60d76037" or strict:
        raise common.AuditError("BL ingress changed")
    words = [(common.BASE + offset, struct.unpack_from("<I", blob, offset)[0]) for offset in range(len(blob) - 3)]
    encoded = starts | {start | 1 for start in starts}
    stored = [(address, value) for address, value in words if value in encoded]
    interior_collisions = [(address, value) for address, value in words if (value & 1) and (value & ~1) in interiors]
    if stored != EXPECTED_STORED or interior_collisions != EXPECTED_INTERIOR_COLLISIONS:
        raise common.AuditError("stored-entry census changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\app\gui\conversate\conversate.c"
    if cstring(blob, 0x0070104C) != expected_path:
        raise common.AuditError("retained path changed")
    path_refs = [(0x005B09F0, address) for address in paths.literal_references(blob, 0x005B09F0)]
    if len(path_refs) != 16 or common._pair_digest(path_refs) != "01787c60c9fc7e6f6bffa627362bdf8e54769cec78aa86fae08ce7cd2febc569":
        raise common.AuditError("retained-path references changed")
    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    if any("conversate_controller" in source.get("path", "").lower() for source in overlay["sources"]):
        raise common.AuditError("unimplemented object routed")

    return {
        "schema_version": 1,
        "identity": {
            "image_sha256": common.IMAGE_SHA256,
            "retained_path": r"app\gui\conversate\conversate.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 12, "ghidra_discovered_functions": 9,
            "restored_functions": 3, "path_anchored_functions": 9,
            "body_bytes": 2250, "physical_bytes": 2628, "noncode_bytes": 378,
            "reachable_instructions": 845, "direct_body_calls": 152,
            "internal_direct_body_calls": 13, "external_direct_body_calls": 139,
            "indirect_body_calls": 0, "direct_bl_entry_sites": 46,
            "stored_aligned_function_entry_pointers": 3,
            "unaligned_exact_entry_byte_windows": 1,
            "raw_instruction_word_interior_collisions": 8,
            "strict_interior_ingress": 0,
        },
        "provider_boundary": {
            "easylogger_calls": 80, "iar_dlib_calls": 4,
            "cmsis_freertos_calls": 7, "lvgl_calls": 2,
            "nanopb_calls": 3, "source_owned_eabi_calls": 1,
            "cmbacktrace_calls": 1, "first_party_calls": 41,
            "cmbacktrace_selected_compatibility_commit": "73714489f9d8af130aacb515586b397b604a5768",
            "cmbacktrace_exact_historical_commit": None,
            "new_version_discriminator": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
