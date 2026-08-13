#!/usr/bin/env python3
"""Fail-closed complete-object and provider audit for service_time.c."""

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
FM = ROOT / "tools/manifests/g2-service-time-function-map.tsv"
CL = ROOT / "tools/manifests/g2-service-time-closure.tsv"
PM = ROOT / "tools/manifests/g2-service-time-provider-map.tsv"
PINS = {
    FM: "05bc821956a7a1b42a624b0aa0ddc59ad6aaafa29ab6a09eb461c226ed42edc5",
    CL: "00047c6964bcef35a02ce2baaf8d1a8c91513310dc2cffb8d14cc0321e697b4e",
    PM: "64df17fcf1c2980c987040025cf7ef2728f3cb6e825f5534b43d2d7f018e5549",
}
F = (
    (0x449ED4,0x449FDA),(0x449FDA,0x44A100),(0x44A100,0x44A108),
    (0x44A108,0x44A192),(0x44A192,0x44A19A),(0x44A19A,0x44A1C6),
    (0x44A1C6,0x44A1EA),(0x44A1EA,0x44A1FE),(0x44A1FE,0x44A2B2),
    (0x44A2B2,0x44A3B4),(0x44A3B4,0x44A3F0),
)
PHYS = (0x449ED4, 0x44A43C)
POOL = (0x44A3F0, 0x44A43C)
STARTS = {start for start, _ in F}
EASY = {0x43CE9E,0x43D0CE,0x43D574}
IAR = {0x439BE4,0x439C04,0x43C0E4}
FIRST = {0x45A568,0x4651E0,0x46650C,0x47697E,0x476ACE,0x47EE78,0x47EF10}
STRICT = [(0x554914, 0x449F22)]
STORED = [
    (0x446398,0x44A2B3),(0x44886C,0x44A2B3),(0x44A438,0x44A2B3),
    (0x4C9C6C,0x44A3B5),(0x543BDC,0x44A2B3),(0x5F9F10,0x44A2B3),
]
PATH_REFS = [0x44A260, 0x44A33C]


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
    for marker in ("9.20 is therefore a practical lower bound", "9.60.2"):
        if marker not in iar:
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
    if anchored != 2 or len(body) != 1308 or sh(body) != "15123a584375bdce24f686d3a6f5cd6e54de0937823dd4dab963fa1d21470c2b":
        raise c.AuditError("body closure changed")
    if code != body or len(instructions) != 497:
        raise c.AuditError("instruction coverage changed")
    if c._instruction_digest(sorted((address, item.size) for address, item in instructions.items())) != "f2cede4ef3b9ac5650fb59a55d5809fdbcf03ef508051a6258e27d764bd5e5a4":
        raise c.AuditError("instruction topology changed")
    if indirect:
        raise c.AuditError("unexpected indirect call")

    if len(c._slice(blob, *POOL)) != 76 or sh(c._slice(blob, *POOL)) != "5e116a5ff2aa92cad2ac039efa30d3a464fcc5b9fcc8de0e642cbb9be0b5d69d":
        raise c.AuditError("outer pool changed")
    if sh(c._slice(blob, *PHYS)) != "c53d1641e065eef61d1a240d15bd7439f45d9f4aff2469e0e1b661f12daddcf9":
        raise c.AuditError("physical object changed")
    if sh(c._slice(blob, 0x449EAC, PHYS[0])) != "9b8152271d46a81303658bec9a10ab1ed5d2c91f9d2d055b63ba18cd8e9f21a2":
        raise c.AuditError("preceding CMSIS boundary changed")
    if sh(c._slice(blob, PHYS[1], 0x44A474)) != "71a165ecb8076258019892002fe7de83336ede123b55de742bd34aaf9b2027a6":
        raise c.AuditError("following IAR strlen boundary changed")
    if tuple(struct.unpack_from("<3I", blob, 0x44A3F8 - c.BASE)) != (946684800, 86400, 0xFFFFD533):
        raise c.AuditError("calendar epoch constants changed")
    if _cstring(blob, 0x6F6024) != r"D:\01_workspace\s200_ap510b_iar_git\platform\service\time\service_time.c":
        raise c.AuditError("retained path changed")
    if _cstring(blob, 0x78362C) != "SVC_SystemTimeSync" or _cstring(blob, 0x783640) != "RPC_SystemTimeSync":
        raise c.AuditError("exact service symbols changed")

    external = Counter(target for _, target in calls if target not in starts)
    providers = (EASY, IAR, FIRST)
    if len(calls) != 45 or sum(target in starts for _, target in calls) != 11:
        raise c.AuditError("call totals changed")
    if c._pair_digest(calls) != "e5d7f38d23ceba1cbf048b0ba070e9480240d9c7b0354036b5f8f24ff2d46ea7":
        raise c.AuditError("call topology changed")
    if set(external) != set().union(*providers):
        raise c.AuditError("provider target set changed")
    if tuple(sum(external[target] for target in provider) for provider in providers) != (10, 8, 16):
        raise c.AuditError("provider accounting changed")

    entries, strict = [], []
    for address in range(c.BASE, c.BASE + len(blob) - 3, 2):
        target = t._thumb_bl_target(blob, address)
        if target in starts:
            entries.append((address, target))
        elif target in interiors:
            strict.append((address, target))
    if len(entries) != 64 or c._pair_digest(entries) != "2d666251a3e7b70e0c7549dd4f1b489fd71fbf21f8060e6dd5f631495248bac9":
        raise c.AuditError("direct entry topology changed")
    if strict != STRICT:
        raise c.AuditError("alternate interior entry changed")
    encoded = starts | {start | 1 for start in starts}
    stored = [
        (c.BASE + offset, struct.unpack_from("<I", blob, offset)[0])
        for offset in range(len(blob) - 3)
        if struct.unpack_from("<I", blob, offset)[0] in encoded
    ]
    if stored != STORED or c._pair_digest(stored) != "c980e69abafda23baf6eb9032d6d581abeeb74e93990049084c6ccc0895e315c":
        raise c.AuditError("stored ingress changed")
    if t.literal_references(blob, 0x44A41C) != PATH_REFS:
        raise c.AuditError("retained-path references changed")

    overlay = json.loads((ROOT / "components/apollo_main/core_overlay/overlay.json").read_text())
    routed = any("service_time" in item.get("path", "").lower() for item in overlay["sources"])
    if routed:
        raise c.AuditError("unimplemented time service entered production overlay")
    return {
        "schema_version": 1,
        "analysis_mode": "read-only raw-image closure; corpus-independent",
        "identity": {
            "image_sha256": c.IMAGE_SHA256,
            "retained_path": r"platform\service\time\service_time.c",
            "embedded_third_party_definitions": [],
        },
        "surface": {
            "linked_functions": 11,
            "ghidra_discovered_functions": 10,
            "restored_functions": 1,
            "alternate_interior_entries": 1,
            "path_anchored_functions": 2,
            "raw_path_referencing_functions": 2,
            "body_bytes": 1308,
            "physical_bytes": 1384,
            "outer_pool_bytes": 76,
            "direct_body_calls": 45,
            "internal_direct_body_calls": 11,
            "external_direct_body_calls": 34,
            "indirect_body_calls": 0,
            "direct_bl_entry_sites": 64,
            "stored_entry_pointers": 6,
        },
        "behavior": {
            "unix_epoch_2000_seconds": 946684800,
            "seconds_per_day": 86400,
            "days_1970_to_2000": 10957,
            "timezone_unit_seconds": 900,
            "calendar_record_bytes": 40,
        },
        "provider_boundary": {
            "easylogger_calls": 10,
            "iar_dlib_calls": 8,
            "first_party_calls": 16,
            "direct_cmsis_freertos_calls": 0,
            "easylogger_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
            "new_version_discriminator": False,
            "private_generating_commit_recoverable": False,
        },
        "production": {"production_routed": False},
    }


if __name__ == "__main__":
    print(json.dumps(analyze(), indent=2, sort_keys=True))
