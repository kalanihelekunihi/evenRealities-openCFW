#!/usr/bin/env python3
"""Fail-closed audit of the retained first-party G2 EFS service object."""

from __future__ import annotations

import csv
import hashlib
import json
import struct
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apollo_artifact_consistency import validate_apollo_main_artifacts
IMAGE = ROOT / "blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin"
BASE = 0x00437FE0
IMAGE_SHA256 = "36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863"
FUNCTION_MAP = ROOT / "tools/manifests/g2-efs-service-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-efs-service-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-efs-service-provenance.tsv"
PINS = {
    FUNCTION_MAP: "2d0eebd09ece2500d5bd6c915768b5d393e4416b76b49a88758b961a8268c106",
    CLOSURE: "4439eeeac75455f1b1c709b994627216e8e0b25c1173647a0e4a4b0b98497b36",
    PROVENANCE: "0be68aa8a51bde606eb415f35e7ee073bdf0b9843c367b22025cb50a7d8e4496",
}
SOURCE = ROOT / "components/apollo_main/core_overlay/efs_service.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_SIZE = 29563
SOURCE_SHA256 = "df18380b86c20b027c8f5a1aae266d8e6f0c9b52705ed8c02cd5cadecf315959"
PRODUCTION_LEAVES = (
    ("_evenEfsReplyToAPP", 30, 216848, 1),
    ("_fileCaculateCRC", 162, 216880, 6),
    ("_efsFileCmdParse", 944, 217044, 20),
    ("_efsFileRawDataParse", 464, 217988, 7),
    ("_efsExportFileParse", 944, 218452, 23),
    ("EFS_FrameDispatch", 82, 219396, 3),
    ("EFS_NotifyStatus4", 46, 219480, 1),
    ("EFS_NotifyStatus2", 46, 219528, 1),
    ("EFS_NotifyStatus5", 46, 219576, 1),
    ("EFS_TransferActive", 18, 219624, 0),
    ("EFS_ServiceInit", 18, 219644, 1),
    ("EFS_CancelExport", 136, 219664, 4),
)
PHYSICAL = (0x00456722, 0x00458DF0)
PHYSICAL_SHA256 = "22a070bb00d0a5555c5a1867804a1fe89678350777c9f3e42258bc7953473175"
BODY_SHA256 = "bbc93a69d35b24750a74a667598ff599189ca52d2b6223578a303854a16edf44"
GAPS = (
    (0x004567A0, 0x004567B8, "5ae02ff6e53b8366317a57fa4f157a9de18f62536411334d6743520659ce4c98"),
    (0x00456BAC, 0x00456C0C, "309534b80932886168e8e1114fe5bef328dc05651bd5e19cf8e8cb4885b09b29"),
    (0x004579BA, 0x00457A54, "acb1c08d7826af07b123ecfdc57043996bcf35a522f0725e33c5ffb73fec8bae"),
    (0x00458018, 0x004580C0, "664b18278e581263ef240529975afb7e6f2028d084dc579d704c409339980ace"),
    (0x00458B5C, 0x00458B60, "e1fe6923f60c92f8b46688ee250e8a1cdf0394099a16324f58416cc892672ce6"),
    (0x00458C30, 0x00458C48, "d77ebb947d77d78ff3e67f1b230d78092365fb7c2a627e8efd7c2d6c536dd5de"),
    (0x00458D34, 0x00458DF0, "99f99a6a82eefc904fab21473dc9f0e76387b444ad4dad36c8ed808a7e852ecb"),
)
GAP_SHA256 = "fcd21039255ece1191801ddc03d6d9ab01209d468a6decfaa39cf369f43f23d6"
ENTRY_SHA256 = "f9064f6c8b13ef0bf36b23f1bd300e9538d75351b63606ef450107bd360daf0f"
BODY_CALL_SHA256 = "57def929f3c98cb6988e50349796cf66c1b92a599c0e840e8ac088ab9d09f061"
BW_SHA256 = "82fb4969e0b29b26334e943706044977cee31ba2876495c37cf0d03b7ee1bf50"
RAW_WINDOW_SHA256 = "950bae6075199d5c82d7a61f078a3ae4fbec7d93ec4c977961bd772437a7163a"
RETAINED_PATH_ADDRESS = 0x006E772C
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"efs_service\efs_service.c"
)
PATH_CELLS = (0x00456BC4, 0x004578F4, 0x00458068, 0x00458D38)
EXACT_SYMBOLS = (
    (0x0077F1BC, "_evenEfsReplyToAPP"),
    (0x0077F1D0, "_fileCaculateCRC"),
    (0x0077F1F8, "_efsFileCmdParse"),
    (0x0077703C, "_efsFileRawDataParse"),
    (0x0077F248, "_efsExportFileParse"),
    (0x0077F270, "EFS_CancelExport"),
)
BW_TARGETS = (
    (0x00456C3C, 0x004579B4), (0x00456D60, 0x004579B4),
    (0x004570BA, 0x004579B4), (0x0045715A, 0x004579B4),
    (0x0045715E, 0x004579B4), (0x00458102, 0x00458AEC),
    (0x00458242, 0x00458AF0), (0x00458A26, 0x00458222),
    (0x00458AA0, 0x00458222), (0x00458AE8, 0x00458222),
)
RAW_WINDOWS = (
    (0x0055E095, 0x00458000), (0x00568585, 0x0045810B),
    (0x005A9C8D, 0x00458A91), (0x005CC5B1, 0x004588DA),
    (0x005D7635, 0x00458198), (0x005E116D, 0x00458109),
    (0x005EB7A1, 0x0045823E), (0x006A4252, 0x00458272),
)


class AuditError(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def image_slice(data: bytes, start: int, end: int) -> bytes:
    return data[start - BASE:end - BASE]


def pair_digest(values: list[tuple[int, int]] | tuple[tuple[int, int], ...]) -> str:
    return sha256(b"".join(struct.pack("<II", *value) for value in values))


def cstring(data: bytes, address: int) -> str:
    offset = address - BASE
    end = data.find(b"\0", offset)
    if end < 0:
        raise AuditError(f"unterminated string at 0x{address:08x}")
    return data[offset:end].decode("ascii")


def thumb_bw_target(data: bytes, address: int) -> int | None:
    first, second = struct.unpack_from("<HH", data, address - BASE)
    if first & 0xF800 != 0xF000 or second & 0xD000 != 0x9000:
        return None
    sign = (first >> 10) & 1
    j1, j2 = (second >> 13) & 1, (second >> 11) & 1
    i1, i2 = (~(j1 ^ sign)) & 1, (~(j2 ^ sign)) & 1
    immediate = ((sign << 24) | (i1 << 23) | (i2 << 22)
                 | ((first & 0x03FF) << 12) | ((second & 0x07FF) << 1))
    if immediate & (1 << 24):
        immediate -= 1 << 25
    return address + 4 + immediate


def analyze(image_path: Path = IMAGE) -> dict:
    data = image_path.read_bytes()
    if len(data) != 3_523_396 or sha256(data) != IMAGE_SHA256:
        raise AuditError("official image changed")
    for path, expected in PINS.items():
        if sha256(path.read_bytes()) != expected:
            raise AuditError(f"pinned input changed: {path.name}")
    with FUNCTION_MAP.open(newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    starts: set[int] = set()
    interiors: set[int] = set()
    intervals: list[tuple[int, int]] = []
    bodies: list[bytes] = []
    manifest_callers: list[tuple[int, int]] = []
    for row in rows:
        start, end = int(row["stock_start"], 0), int(row["stock_end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["stock_bytes"]) or sha256(raw) != row["stock_sha256"]:
            raise AuditError(f"body changed: {row['function']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
        for caller in filter(None, row["direct_callers"].split(";")):
            manifest_callers.append((int(caller, 0), start))
    if len(rows) != 12 or sum(map(len, bodies)) != 9276:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 658 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 4) != bytes.fromhex("80b5c0b2"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained EFS symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entry: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    bw_hits: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entry.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw_hits.append((site, target))
    if entry != sorted(manifest_callers) or len(entry) != 35:
        raise AuditError("direct entry closure changed")
    if pair_digest(entry) != ENTRY_SHA256 or interior:
        raise AuditError("direct BL digest/interior closure changed")
    if tuple(bw_hits) != BW_TARGETS or pair_digest(bw_hits) != BW_SHA256:
        raise AuditError("B.W closure changed")
    if any(not (start <= site < end and start < target < end)
               for site, target in bw_hits for start, end in intervals
               if start <= site < end):
        raise AuditError("external or cross-body B.W interior ingress appeared")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 559 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    encoded = starts | interiors | {value | 1 for value in starts | interiors}
    stored = [(BASE + offset, struct.unpack_from("<I", data, offset)[0])
              for offset in range(len(data) - 3)
              if struct.unpack_from("<I", data, offset)[0] in encoded]
    if tuple(stored) != RAW_WINDOWS or pair_digest(stored) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if any((value & ~1) in starts for _, value in stored):
        raise AuditError("unexpected stored exact-entry pointer")

    literal_checks = {
        0x00456BD0: 0x20071CC8, 0x00456BF0: 0x2035BE08,
        0x00457A04: 0x20074554, 0x00457A38: 0x2007455C,
        0x00458A2C: 0x20074560, 0x00458A30: 0x20074558,
        0x00458D8C: 0x20074FBC, 0x00458DA4: 0x2035ADF8,
    }
    if any(struct.unpack_from("<I", data, address - BASE)[0] != value
           for address, value in literal_checks.items()):
        raise AuditError("EFS state/buffer literal closure changed")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production EFS service source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = {leaf["function"]: leaf for leaf in overlay["relocated_leaves"]}
    patches = {patch["name"]: patch for patch in overlay["patch_sites"]}
    for order, (name, size, offset, relocations) in enumerate(PRODUCTION_LEAVES, 1):
        leaf = leaves.get(name)
        if (
            not leaf
            or leaf.get("source", {}).get("path")
            != "components/apollo_main/core_overlay/efs_service.c"
            or leaf.get("source", {}).get("size") != SOURCE_SIZE
            or leaf.get("source", {}).get("sha256") != SOURCE_SHA256
            or leaf.get("expected", {}).get("size") != size
            or leaf.get("expected", {}).get("offset") != offset
            or leaf.get("expected", {}).get("alignment") != 4
            or len(leaf.get("relocations", [])) != relocations
            or not leaf.get("strict_relocation_contract")
            or leaf.get("profiles") != ["apple-clang"]
        ):
            raise AuditError(f"production EFS service leaf changed: {name}")
        stock = rows[order - 1]
        patch = patches.get(f"replace_efs_service_{order:02d}")
        if (
            not patch
            or patch.get("runtime_address") != int(stock["stock_start"], 0)
            or patch.get("expected_size") != int(stock["stock_bytes"])
            or patch.get("expected_sha256") != stock["stock_sha256"]
            or patch.get("target_function") != name
            or patch.get("branch") != "b_w"
            or patch.get("profiles") != ["apple-clang"]
        ):
            raise AuditError(f"production EFS service patch changed: {name}")

    report = json.loads(REPORT.read_text())
    reported = {
        leaf["extraction"]["function"]: leaf
        for leaf in report["relocated_leaves"]
        if leaf.get("source", {}).get("path")
        == "components/apollo_main/core_overlay/efs_service.c"
    }
    for name, size, offset, relocations in PRODUCTION_LEAVES:
        item = reported.get(name)
        if (
            not item
            or item["placement"]["offset"] != offset
            or item["placement"]["size"] != size
            or item["placement"]["alignment"] != 4
            or item["extraction"]["relocation_count"] != relocations
        ):
            raise AuditError(f"production EFS service report changed: {name}")
    validate_apollo_main_artifacts(ROOT, AuditError, "EFS service")

    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = {region["name"]: region for region in main["regions"]}
    for order, row in enumerate(rows, 1):
        item = regions.get(f"efs_service_{order:02d}_source_replacement")
        expected = (
            int(row["stock_start"], 0), int(row["stock_bytes"]),
            "generated_source_entry_replacement",
        )
        if not item or (
            item.get("target_address"), item.get("size"),
            item.get("address_status"),
        ) != expected:
            raise AuditError(f"production EFS service stock region changed: {row['function']}")
    service_regions = [region for region in main["regions"]
                       if region["name"].startswith("efs_service_")]
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "source_compiled") != 2936:
        raise AuditError("production EFS service compiled region coverage changed")
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "generated_alignment") != 16:
        raise AuditError("production EFS service alignment coverage changed")
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "official_blob") != 658:
        raise AuditError("production EFS service retained-gap coverage changed")

    external_entries = [pair for pair in entry
                        if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    return {
        "surface": {
            "retained_path_anchors": 6, "restored_pathless_functions": 6,
            "linked_functions": 12, "body_bytes": 9276,
            "owned_gap_pool_bytes": 658, "physical_bytes": 9934,
            "direct_bl_entry_sites": 35,
            "external_direct_bl_entry_sites": len(external_entries),
            "direct_body_calls": 559, "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0, "raw_instruction_windows": 8,
        },
        "contracts": {
            "frame_ids": {0xC4: "import_control", 0xC5: "import_raw_data",
                          0xC6: "export_control", 0xC7: "export_data"},
            "control_subcommands": {0: "start", 1: "continue_or_activate",
                                    2: "result_check", 3: "cancel_export"},
            "file_types": {0: "notification_whitelist", 1: "android_message_json",
                           2: "logger_export", 3: "tracepoint_export",
                           0xAA: "other_file"},
            "transfer_state": "0x20071cc8", "transfer_state_bytes": 0x78,
            "import_buffer": "0x2035be08", "export_buffer": "0x2035adf8",
            "chunk_capacity": 0x1000, "android_message_capacity": 0x2137,
            "export_active": "0x20074fbc",
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS],
            "observed_source_lines": [0x106, 0x11F, 0x14E, 0x15B, 0x207,
                                      0x21F, 0x26C, 0x288, 0x342, 0x3A8, 0x3B3],
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/efs_service.c",
            "source_inventory_available": True,
            "production_routed": True, "ownership_bytes": 9276,
            "source_functions": 12, "compiled_text_bytes": 2936,
            "alignment_bytes": 16, "strict_relocations": 68,
            "stock_replaced_bytes": 9276, "retained_gap_pool_bytes": 658,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification "
                "requires an authorized G2 pair and either a component-specific writable/readable "
                "EFS-media fixture or an authenticated golden EFS capture covering whitelist import, "
                "Android JSON consumption, arbitrary-file import, logger/trace export, 4 KiB streaming, "
                "cancellation, CRC/size failure, disconnect, and resume"
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 EFS service audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 EFS service audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
