#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for thread_audio.c."""

import csv
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import analyze_g2_dashboard_watchface_manager as d
import analyze_g2_ux_system as c
import recover_apollo_embedded_source_paths as t

IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
FM = ROOT / "tools/manifests/g2-thread-audio-function-map.tsv"
CL = ROOT / "tools/manifests/g2-thread-audio-closure.tsv"
PM = ROOT / "tools/manifests/g2-thread-audio-provider-map.tsv"
PINS = {
    FM: "25b9b37c2eeb0692a4f79218693167fca9890edc42473df4a806f2b5e16fb1d9",
    CL: "397dab9a3238f49808b887ddcf10e389cc3e80267191a76354a47b27599a6e77",
    PM: "54c039ccfdc746014c2de650af2efb0bc2df3d90fc81aa5ffe7e1bdd0be2f400",
}
F = (
    (0x53C2BE,0x53C31C),(0x53C31C,0x53C330),(0x53C330,0x53C33A),
    (0x53C33A,0x53C344),(0x53C344,0x53C3EE),(0x53C3EE,0x53C4F2),
    (0x53C4F2,0x53C50A),(0x53C50A,0x53C514),(0x53C514,0x53C52A),
    (0x53C52C,0x53C5AC),(0x53C5AC,0x53C638),(0x53C638,0x53C6B2),
    (0x53C6B2,0x53C6D2),(0x53C6D2,0x53C6F2),(0x53C6F2,0x53C776),
    (0x53C776,0x53C7B0),(0x53C7B0,0x53C838),(0x53C838,0x53C860),
    (0x53C860,0x53C92E),(0x53C92E,0x53C9FA),(0x53C9FA,0x53CA10),
    (0x53CA10,0x53CA32),(0x53CA32,0x53CA54),(0x53CA54,0x53CA72),
    (0x53CA72,0x53CC8C),(0x53CC8C,0x53CCA6),(0x53CCA6,0x53CD38),
    (0x53CD40,0x53CD62),(0x53CD62,0x53CD8C),(0x53CDAC,0x53CDC2),
    (0x53CDC2,0x53CE72),
)
PHYS = (0x53C2BE, 0x53CF78)
POOLS = ((0x53CD38,0x53CD40),(0x53CD8C,0x53CDAC),(0x53CE72,0x53CF78))
STARTS = {start for start, _ in F}
EASY = {0x43CE9E,0x43D0CE,0x43D574}
CMSIS = {
    0x4490CC,0x4490E2,0x4491FE,0x449238,0x4492C2,0x449376,0x4493B0,
    0x449498,0x4494D8,0x44953E,0x449A32,0x449ABE,0x449B3C,0x449BEC,
}
IAR = {0x43C0E4}
CLOSED_AUDIO = {
    0x579FB8,0x57A656,0x57A65C,0x57A734,0x57A7E0,0x57A816,
    0x57BA88,0x57BAEC,0x57D6B4,0x57D794,0x57D93C,0x57DA40,
}
FIRST = {
    0x46B0EC,0x46C630,0x49832E,0x498528,0x4ABE60,0x4C9B86,0x4C9BE2,
    0x4C9C3C,0x53A590,0x54F6F4,0x54F88E,0x57ADF8,0x57B4A8,0x57B586,
    0x57B640,0x57B770,0x57B86C,0x57B9BA,
}
STORED = [(0x79407F,0x53C345),(0x794083,0x53C4F3),(0x7940B9,0x53CCA7)]
PATH_REFS_1 = [
    0x53C2EE,0x53C376,0x53C3BE,0x53C41C,0x53C464,0x53C4C4,0x53C57E,
    0x53C606,0x53C676,0x53C726,0x53C7D2,0x53C882,0x53C96E,0x53C9C8,
    0x53CA96,0x53CAE8,0x53CB48,0x53CB98,0x53CBE2,0x53CC5C,0x53CCC0,
    0x53CD04,
]
PATH_REFS_2 = [0x53CE08,0x53CE42]


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
    cmsis = json.loads((ROOT / "third_party/cmsis-freertos/PROVENANCE.json").read_text())
    kernel = json.loads((ROOT / "third_party/freertos-kernel/PROVENANCE.json").read_text())
    if easy["upstream"]["selected_commit"] != "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24":
        raise c.AuditError("EasyLogger source selection changed")
    if cmsis["upstreams"]["cmsis_freertos"]["selected_commit"] != "d213f261b5be6bb29a7cce8b84071706b72f4d53":
        raise c.AuditError("CMSIS-FreeRTOS source selection changed")
    if cmsis["upstreams"]["cmsis_5"]["selected_commit"] != "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c":
        raise c.AuditError("CMSIS_5 source selection changed")
    if kernel["upstream"]["selected_commit"] != "def7d2df2b0506d3d249334974f51e427c17a41c":
        raise c.AuditError("FreeRTOS-Kernel source selection changed")
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
        decoded, direct, dynamic = d._recover_function(blob, start, end)
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
    if anchored != 3 or len(body) != 2954 or sh(body) != "fe72e2aa3c1df48e4c23ab953a0cfec61b336fce338bb782c9f57143c08d9e04":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 1101:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "a789ec5ff1acf31b9539a95a78d10fe861d5a215c5c5be6faebc780d9e0b0ee8":
        raise c.AuditError("instruction topology changed")
    if indirect != [0x53C5E0]:
        raise c.AuditError("runtime message-dispatch call changed")

    pool = b"".join(c._slice(blob, *bounds) for bounds in POOLS)
    if len(pool) != 302 or sh(pool) != "7239351882f3e42b71f940232283b20fdf23d6ff62f7398fc539d6ca7d562c22":
        raise c.AuditError("outer pools changed")
    if c._slice(blob, 0x53C52A, 0x53C52C) != b"\0\0":
        raise c.AuditError("inline alignment changed")
    if sh(c._slice(blob, *PHYS)) != "93f6ab6fc3ae5b0a010e129af409e66ffea08ec30210defc299b8ca3daa39aa9":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x53C2A4, PHYS[0])) != "ec2166b8ab5a8e47c4a6c03901f66a40ac93866b4ea88712826950162b9dbbb6":
        raise c.AuditError("preceding object boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x53CFE4)) != "87d2921ff11a7e6c3658dd898320742affa4a5264b8de48f371cc497e8d52587":
        raise c.AuditError("following object boundary changed")
    expected_path = r"D:\01_workspace\s200_ap510b_iar_git\platform\threads\thread_audio.c"
    if _cstring(blob, 0x706FEC) != expected_path:
        raise c.AuditError("retained path changed")
    for address, expected in {
        0x766750: "AUD_CodecAudioCheckTimerStart", 0x7899B0: "AUD_ThreadInit",
        0x784144: "AUD_ResourceInit", 0x784158: "AUD_ThreadHandler",
        0x77CB14: "AUD_MessageProcesser", 0x7899D0: "AUD_SendMessage",
        0x7899E0: "AUD_CodecDmaInt", 0x78C620: "AUD_PdmCtr",
        0x7899F0: "AUD_CodecCtr", 0x78416C: "AUD_CodecAudioCheck",
        0x784180: "AUD_CodecIntNotify", 0x789A20: "AUD_PeerSyncMsg",
        0x789A30: "AUD_ThreadExit",
    }.items():
        if _cstring(blob, address) != expected:
            raise c.AuditError("exact audio symbol changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, CMSIS, IAR, CLOSED_AUDIO, FIRST)
    if len(calls) != 203 or sum(target in starts for _, target in calls) != 20:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "8b5ff513f63773c26a81ac0ea4dcbea82fd8afb9b92951ccf40024433edb50f4":
        raise c.AuditError("call topology changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (120,20,1,19,23):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 43 or c._pair_digest(entries) != "0a0dd4d6d6326d0b414452d2a5db9a7468570e875bea710a6fdc9341502272c9":
        raise c.AuditError("direct entry topology changed")
    if strict:
        raise c.AuditError("unexpected strict-interior entry")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != STORED or c._pair_digest(stored) != "37c06719e55019815feaff7850615694941329642e63205a1a8bea5050492e6d":
        raise c.AuditError("stored ingress changed")
    if t.literal_references(blob, 0x53CD8C) != PATH_REFS_1 or t.literal_references(blob, 0x53CF64) != PATH_REFS_2:
        raise c.AuditError("retained-path references changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("thread_audio" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented audio thread entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\threads\thread_audio.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 31,
            "ghidra_discovered_functions": 12,
            "restored_functions": 19,
            "path_anchored_functions": 3,
            "raw_path_references": 24,
            "raw_path_referencing_functions": 13,
            "body_bytes": 2954,
            "physical_bytes": 3258,
            "outer_pool_bytes": 302,
            "inline_alignment_bytes": 2,
            "direct_body_calls": 203,
            "internal_direct_body_calls": 20,
            "external_direct_body_calls": 183,
            "indirect_body_calls": 1,
            "direct_bl_entry_sites": 43,
            "stored_entry_pointers": 3,
        },
        "behavior": {
            "message_queue_capacity": 50,
            "message_bytes": 12,
            "known_dispatch_ids": 8,
            "watchdog_period_ticks": 2000,
            "codec_activity_threshold": 20,
            "dma_interrupt_max_age_ticks": 40,
        },
        "provider_boundary": {
            "easylogger_calls": 120,
            "cmsis_freertos_calls": 20,
            "cmsis_wrapper_count": 14,
            "iar_dlib_calls": 1,
            "closed_codec_gx8002b_calls": 19,
            "other_first_party_calls": 23,
            "bounded_first_party_indirect_calls": 1,
            "cmsis_freertos_commit": "d213f261b5be6bb29a7cce8b84071706b72f4d53",
            "freertos_kernel_commit": "def7d2df2b0506d3d249334974f51e427c17a41c",
            "cmsis_5_commit": "2b7495b8535bdcb306dac29b9ded4cfb679d7e5c",
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "nationalchip_lvp_code_linked": False,
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
