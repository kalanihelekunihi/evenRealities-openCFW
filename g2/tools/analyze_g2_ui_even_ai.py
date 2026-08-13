#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for ui_even_ai.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_even_ai_timer as timer
import analyze_g2_text_stream_service as text_stream
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-ui-even-ai-function-map.tsv"
CL = ROOT / "tools/manifests/g2-ui-even-ai-closure.tsv"
PM = ROOT / "tools/manifests/g2-ui-even-ai-provider-map.tsv"
PINS = {
    FM: "09b3ea0f6886b8dd96009b01da2ee3fa2732993e3c8c9e62b1a2c35723766725",
    CL: "8dde6411ff9c79714b5df041a46f6c56d1fcc7a92b4a4e420e201ebec19fc974",
    PM: "bc10616aff57ed63a753abc2f90ab805adbce29cc3db75fb82869a649f4194f3",
}
F = (
    (0x4E54C8,0x4E54FA),(0x4E54FA,0x4E5502),(0x4E5502,0x4E550A),(0x4E550A,0x4E551E),
    (0x4E551E,0x4E557C),(0x4E557C,0x4E55F8),(0x4E55F8,0x4E5672),(0x4E5672,0x4E5678),
    (0x4E5678,0x4E571A),(0x4E571A,0x4E5A0E),(0x4E5A0E,0x4E5B48),(0x4E5B48,0x4E5C1C),
    (0x4E5C1C,0x4E5CD4),(0x4E5CD4,0x4E5D16),(0x4E5D16,0x4E5D3E),(0x4E5D3E,0x4E5D54),
    (0x4E5D54,0x4E5D94),(0x4E5D94,0x4E5E12),(0x4E5E12,0x4E5E92),(0x4E5E92,0x4E5F20),
    (0x4E5F20,0x4E5F84),(0x4E5F84,0x4E5F8E),(0x4E5FA4,0x4E5FF8),(0x4E5FF8,0x4E607C),
    (0x4E6088,0x4E60E4),(0x4E6100,0x4E61A2),(0x4E61B4,0x4E61EA),(0x4E61F0,0x4E6254),
    (0x4E6254,0x4E62B8),(0x4E62C0,0x4E62CE),(0x4E62CE,0x4E64A6),(0x4E64B4,0x4E654A),
    (0x4E6560,0x4E68A2),(0x4E68A2,0x4E6956),(0x4E6956,0x4E69DE),(0x4E69E4,0x4E6A4E),
    (0x4E6A4E,0x4E6A6E),(0x4E6A80,0x4E6AAA),(0x4E6AAA,0x4E6ADE),(0x4E6AEC,0x4E6C16),
    (0x4E6C44,0x4E7162),(0x4E7170,0x4E74C2),(0x4E74CC,0x4E74FA),
)
PHYS = (0x4E54C8, 0x4E75B0)
INLINE = (0x4E6FD0, 0x4E6FD4)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x439BE4, 0x43C0E4, 0x44A43C}
CMSIS_RTOS = {0x4490CC}
LVGL = {
    0x43DE82,0x43DED4,0x43DFA4,0x43E2EA,0x43F09A,0x43F0E0,0x43F142,
    0x43F4C0,0x43F506,0x43F568,0x43F6B8,0x43F6D6,0x43FDDA,0x440656,
    0x44104C,0x4411AA,0x44120E,0x44121C,0x44122A,0x441238,0x44127E,
    0x44129E,0x4412EC,0x44131C,0x44140E,0x44143E,0x44145A,0x44146A,
    0x44D7B8,0x44E368,0x44E3CA,0x44E498,0x44EA04,0x450286,0x451740,
    0x498310,0x498668,0x498680,0x499416,0x49942E,0x4997F8,
    0x55751E,0x557536,0x557630,
}
FIRST = {
    0x45A568,0x45FFFE,0x460084,0x464BB2,0x464C36,0x4E1FA6,0x4E1FBE,
    0x4E2E10,0x4E2E62,0x509C1C,0x509C96,0x509DFA,0x509E14,
    0x552B30,0x552BE6,0x552CDC,0x552CE8,0x552CF8,0x552D04,0x552D10,
    0x552D40,0x5531A8,0x553274,0x55344E,0x553794,0x5537CC,0x55389A,
    0x553D28,0x5546BE,
}
PATH_CELLS = {
    0x4E5F9C: [0x4E554E,0x4E55CA,0x4E5636,0x4E56A8,0x4E5762,0x4E5830,0x4E5C3E],
    0x4E6A78: [0x4E616C,0x4E6226,0x4E628A,0x4E63D4,0x4E64E8,0x4E6656,0x4E69B2],
    0x4E7510: [0x4E6B38,0x4E6BB6,0x4E6CA6,0x4E6D0C,0x4E6D82,0x4E6E0A,0x4E7472],
}
STORED = [(0x4E7598, 0x4E5D17)]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _provenance() -> None:
    lvgl = json.loads((ROOT / "third_party/lvgl/PROVENANCE.json").read_text())
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if lvgl["upstream"]["selected_commit"] != "344c7c318047b7348e1be8572a9fd4260c251cfa":
        raise c.AuditError("LVGL source selection changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    for marker in ("9.20 is therefore a practical lower bound", "9.60.2"):
        if marker not in iar:
            raise c.AuditError("IAR DLIB family assessment changed")
    text = text_stream.analyze()
    timed = timer.analyze()
    if text["surface"]["linked_functions"] != 26 or text["identity"]["embedded_third_party_definitions"]:
        raise c.AuditError("text-stream provider closure changed")
    if timed["surface"]["linked_functions"] != 13 or timed["identity"]["embedded_third_party_definitions"]:
        raise c.AuditError("EvenAI timer provider closure changed")


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
    body, calls, indirect, anchored, uncovered = b"", [], [], 0, []
    for row, bounds in zip(rows, F):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = c._slice(blob, start, end)
        if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
            raise c.AuditError("function body changed")
        decoded, direct, dynamic = d._recover_function(blob, start, end)
        uncovered.extend(c._uncovered(bounds, decoded))
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        instructions.update(decoded)
        calls.extend(direct)
        indirect.extend(dynamic)
        body += raw
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    if uncovered != [INLINE]:
        raise c.AuditError(f"unexpected non-instruction bytes: {uncovered!r}")
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if anchored != 2 or len(body) != 8004 or sh(body) != "5f99e8daf09fd45e0a014b97ef9ea84e3147c78a9c5057198f5b8f4e299ebe63":
        raise c.AuditError("body closure changed")
    if len(code) != 8000 or len(instructions) != 3141:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "5d3e283213816bd4ba2670f2f9c53bf348fc9e8c786c6e4c3939c49747b39cbd":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    gaps, cursor = [], PHYS[0]
    for start, end in F:
        if cursor < start:
            gaps.append(c._slice(blob, cursor, start))
        cursor = end
    if cursor < PHYS[1]:
        gaps.append(c._slice(blob, cursor, PHYS[1]))
    if len(gaps) != 15 or sum(map(len, gaps)) != 420 or sh(b"".join(gaps)) != "01c56aab9bcd2b7e29752054f55cb30c40ac56dbf619ce2110e82c6909ea9c87":
        raise c.AuditError("outer pool closure changed")
    if c._slice(blob, *INLINE) != b"\0\0\0\0":
        raise c.AuditError("inline literal changed")
    if sh(c._slice(blob, *PHYS)) != "5e86ec5580e55c7b3576559f6e6574c86364976c7196c9246743b53b194f3122":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x4E54A0, PHYS[0])) != "313175aff2a7be514c1c51b545aba9a7d083f5ccc209a85a257959e3696854b7":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x4E772C)) != "85e04a613658c1e604b6e743e99c28386ea12a256c11a755c8cf9d288a3f1731":
        raise c.AuditError("following boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (LVGL, EASY, IAR, CMSIS_RTOS, FIRST)
    if len(calls) != 512 or sum(target in starts for _, target in calls) != 99:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "16bc90adba5cc7755b78429c511671e075c3c4bce87829f1881b277303088eb6":
        raise c.AuditError("call topology changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (182, 105, 22, 1, 103):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 131 or c._pair_digest(entries) != "9552bee2789cb471fdc26926db92f3d32ffd1832f79d94d1a0adbf2ffde26f9c" or strict:
        raise c.AuditError("direct ingress changed")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != STORED or c._pair_digest(stored) != "ff177266bc4b9e00e3fccb20180d05fbf52889c7383a520c7084d0f3dc8215d1":
        raise c.AuditError("stored ingress changed")
    for cell, expected in PATH_CELLS.items():
        if t.literal_references(blob, cell) != expected:
            raise c.AuditError(f"retained-path references changed at 0x{cell:08x}")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("ui_even_ai" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented EvenAI UI entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"app\gui\EvenAI\ui_even_ai.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 43,
            "ghidra_discovered_functions": 15,
            "restored_functions": 28,
            "path_anchored_functions": 2,
            "raw_path_referencing_functions": 16,
            "body_bytes": 8004,
            "instruction_bytes": 8000,
            "physical_bytes": 8424,
            "outer_pool_bytes": 420,
            "inline_literal_bytes": 4,
            "direct_body_calls": 512,
            "internal_direct_body_calls": 99,
            "external_direct_body_calls": 413,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 131,
            "stored_entry_pointers": 1,
        },
        "provider_boundary": {
            "lvgl_calls": 182,
            "easylogger_calls": 105,
            "iar_dlib_calls": 22,
            "cmsis_freertos_calls": 1,
            "first_party_calls": 103,
            "lvgl_commit": "344c7c318047b7348e1be8572a9fd4260c251cfa",
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
