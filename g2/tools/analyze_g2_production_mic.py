#!/usr/bin/env python3
"""Fail-closed object/provider audit for product_test/production_mic_func.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_compress_log_core as q
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-production-mic-function-map.tsv"
CL = ROOT / "tools/manifests/g2-production-mic-closure.tsv"
PM = ROOT / "tools/manifests/g2-production-mic-provider-map.tsv"
PINS = {
    FM: "fa9f7a2db816a7ad0165545fa39d747e11cbf355fd3d7538c7077bc5fcafbb3d",
    CL: "0a491746aa898b6e942f73db3000c7967c50b2f921dba5c28bf8be858a0d850d",
    PM: "81d088580a13c9329463be980175291e9fe30de234fbe87b2864215d806bfb06",
}
F = (
    (0x58F4E4, 0x58F5E0), (0x58F5E0, 0x58F69A),
    (0x58F69A, 0x58F74A), (0x58F74A, 0x58F7B0),
    (0x58F7B0, 0x58F806), (0x58F806, 0x58F866),
)
PHYS = (0x58F4E4, 0x58F8CC)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E, 0x43D0CE, 0x43D574}
IAR = {0x439BE4, 0x43C0E4}
AUDIO = {0x53CA10, 0x53CA32, 0x57A926, 0x57A940, 0x57AB78, 0x57ACD0, 0x57B12C, 0x57B1F4, 0x57B312}
EXTERNAL_TARGET_COUNTS = {
    0x439BE4: 2, 0x43C0E4: 3, 0x43CE9E: 7, 0x43D0CE: 21,
    0x43D574: 7, 0x53CA10: 2, 0x53CA32: 2, 0x57A926: 3,
    0x57A940: 4, 0x57AB78: 3, 0x57ACD0: 2, 0x57B12C: 2,
    0x57B1F4: 4, 0x57B312: 2,
}
PATH_REFS = [0x58F510, 0x58F604, 0x58F6BC, 0x58F708, 0x58F774, 0x58F7C4, 0x58F830]


def sh(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _cstring(blob: bytes, address: int) -> str:
    offset = address - c.BASE
    end = blob.find(b"\0", offset)
    if offset < 0 or end < 0:
        raise c.AuditError(f"unterminated string at 0x{address:08x}")
    return blob[offset:end].decode("ascii")


def _provenance() -> None:
    easy = json.loads((ROOT / "third_party/easylogger/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    iar = (ROOT / "docs/research/iar-dlib-runtime-census.md").read_text()
    if "9.20 is therefore a practical lower bound" not in iar or "9.60.2" not in iar:
        raise c.AuditError("IAR DLIB family assessment changed")


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
    body, calls, indirect, anchored = b"", [], [], 0
    for row, bounds in zip(rows, F):
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = c._slice(blob, start, end)
        if (start, end) != bounds or len(raw) != int(row["stock_bytes"]) or sh(raw) != row["stock_sha256"]:
            raise c.AuditError("function body changed")
        decoded, direct, dynamic = q._recover_function(blob, start, end)
        if c._uncovered(bounds, decoded):
            raise c.AuditError("function has uncovered bytes")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        instructions.update(decoded)
        calls.extend(direct)
        indirect.extend(dynamic)
        body += raw
        anchored += row["source_path_anchor"] == "yes"
    calls.sort()
    code = b"".join(c._slice(blob, address, address + item.size) for address, item in sorted(instructions.items()))
    if anchored != 5 or len(body) != 898 or sh(body) != "c7ffe280cd5489f7ab79866325addfb3aa9fe89fed0142170c5819e6899c870b":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 359:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "f1e45cdff96add83d701bbe4b895c10a37d30afe4a1c77781a5d90486399761c":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    pool = c._slice(blob, 0x58F866, 0x58F8CC)
    if len(pool) != 102 or sh(pool) != "24b3c606e780a49f57ec57fa38e3ce4502b239f7ef4e70b252b841e9bb91110b":
        raise c.AuditError("object pool/alignment changed")
    if sh(c._slice(blob, *PHYS)) != "5a277c1e7b593a09a3861987f57707b99651c8b4bc63b5f9f3c07fa4b7f1ad05":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x58F4A4, 0x58F4E4)) != "f4cda3e50856da8a7dcca5dac3c060af6c6f13b6155c3bba1cbf957671d6e080":
        raise c.AuditError("preceding boundary changed")
    if sh(c._slice(blob, 0x58F8CC, 0x58F8D8)) != "7a2376fd6327f3097adb642b60ef52c5dbdd96c637f0d91f894bff7174097d27":
        raise c.AuditError("following object boundary changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, AUDIO)
    if len(calls) != 64 or sum(target in starts for _, target in calls) != 0:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "7b8a79197f67519a833a1e8b30d0921c7b7bfa4bc36d54ddad47dbb98beb1b70":
        raise c.AuditError("call topology changed")
    if external != Counter(EXTERNAL_TARGET_COUNTS):
        raise c.AuditError("external call multiplicity changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (35, 5, 24):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 8 or c._pair_digest(entries) != "c7cc86ed24abb8757f57aed4d62fdae0bca0dcf631104a0284b79a5a6329f47f":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != [(0x58F8A0, 0x58F5E1), (0x58F8AC, 0x58F4E5)]:
        raise c.AuditError("stored PCM callback entries changed")

    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\product_test\production_mic_func.c"
    if _cstring(blob, 0x6EEE18) != expected_path:
        raise c.AuditError("retained path changed")
    if t.literal_references(blob, 0x58F870) != PATH_REFS:
        raise c.AuditError("retained-path references changed")
    for address, expected in {
        0x7639D0: "production_pcm_callback_stereo",
        0x7639F0: "production_pcm_callback_single",
        0x763A10: "production_codec_mic_func_init",
        0x758118: "production_codec_mic_func_deinit",
        0x763A30: "production_pdm_mic_func_init",
        0x763A50: "production_pdm_mic_func_deinit",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("production microphone symbol changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("production_mic" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented production microphone object entered overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\product_test\production_mic_func.c",
            "nationalchip_lvp_code_linked": False,
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 6, "ghidra_discovered_functions": 5,
            "restored_functions": 1, "path_anchored_functions": 5,
            "raw_path_references": 7, "raw_path_referencing_functions": 6,
            "body_bytes": 898, "physical_bytes": 1000,
            "outer_pool_and_alignment_bytes": 102, "reachable_instructions": 359,
            "direct_body_calls": 64, "internal_direct_body_calls": 0,
            "external_direct_body_calls": 64, "indirect_body_calls": 0,
            "direct_bl_entry_sites": 8, "stored_entry_pointers": 2,
        },
        "behavior": {
            "listener_id": 0x10B,
            "codec_capture_mode": 0,
            "pdm_capture_mode": 1,
            "channel_scratch_bytes": 400,
            "stereo_callback_only_accepts_source_zero": True,
            "stereo_extracted_channels_concatenated": True,
            "single_callback_accepts_sources": [0, 1],
            "raw_pcm_forwarded_when_extraction_disabled": True,
        },
        "provider_boundary": {
            "easylogger_and_compact_calls": 35,
            "iar_dlib_memory_calls": 5,
            "g2_codec_pdm_pcm_calls": 24,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
