#!/usr/bin/env python3
"""Fail-closed audit of the retained first-party G2 OTA service object."""

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
FUNCTION_MAP = ROOT / "tools/manifests/g2-ota-service-function-map.tsv"
CLOSURE = ROOT / "tools/manifests/g2-ota-service-closure.tsv"
PROVENANCE = ROOT / "tools/manifests/g2-ota-service-provenance.tsv"
PINS = {
    FUNCTION_MAP: "14854f14615287a4cd95aac16c18f92bcd3da582f1a3bbb86698f4374963631d",
    CLOSURE: "024454153c2f0df214ad8b9eeff89de64a8eb685566d07632cd5f8799261d4ef",
    PROVENANCE: "1c32ca41264759e8f629cdd4300cc67487afc70b4ffc358f3ed79c7d3fccef01",
}
SOURCE = ROOT / "components/apollo_main/core_overlay/ota_service.c"
OVERLAY = ROOT / "components/apollo_main/core_overlay/overlay.json"
REPORT = ROOT / "components/apollo_main/core_overlay/build/build-report.json"
MANIFEST = ROOT / "manifests/g2-2.2.6.10-core-source.json"
SOURCE_SIZE = 25_015
SOURCE_SHA256 = "87b90aa0793add8647af2c99014a61bcb56fd93c545b1352db8bf67bfafc2dea"
PRODUCTION_LEAVES = (
    ("open_cfw_ota_flash_erase", 28, 219800, 1),
    ("open_cfw_ota_flash_read", 130, 219828, 1),
    ("open_cfw_ota_flash_write", 42, 219960, 2),
    ("open_cfw_ota_status_sync", 80, 220004, 1),
    ("OtaSelectFlashOps", 22, 220084, 0),
    ("OtaFileSize", 14, 220108, 1),
    ("OtaEraseRange", 42, 220124, 1),
    ("_evenOtaSetFwAddr", 106, 220168, 2),
    ("_verifyFlashContent", 174, 220276, 1),
    ("OtaBufferedFlashWrite", 66, 220452, 2),
    ("OtaCommitDescriptor", 72, 220520, 1),
    ("_evenOtaReplyToAPP", 44, 220592, 1),
    ("_RPC_SystemOtaStatusSync", 4, 220636, 1),
    ("OtaParseHexAddress", 100, 220640, 0),
    ("_evenOtaBootloaderWriteFile2MRAM", 202, 220740, 9),
    ("_otaFsHealthProbe", 4, 220944, 1),
    ("_otaFsHealthCheckAndHeal", 40, 220948, 3),
    ("_fileCmdParse", 576, 220988, 9),
    ("_fileRawDataParse", 420, 221564, 7),
    ("OTA_FileCaculateCRC", 156, 221984, 6),
    ("_exportFileParse", 456, 222140, 6),
    ("OTA_FrameDispatch", 92, 222596, 3),
    ("OTA_ResetExportState", 52, 222688, 1),
    ("OTA_NotifyStatus4", 32, 222740, 1),
    ("OTA_NotifyStatus3", 32, 222772, 1),
    ("OTA_NotifyStatus5", 32, 222804, 1),
    ("OTA_CancelExport", 64, 222836, 2),
    ("OTA_TransferActive", 36, 222900, 0),
    ("OTA_SetInterface", 12, 222936, 0),
)
PATCH_TARGETS = tuple(name for name, *_ in PRODUCTION_LEAVES[4:])
PHYSICAL = (0x004448F4, 0x004488EC)
PHYSICAL_SHA256 = "b58c8256ffee83bc9af1e920be4ba419f46e19695823a71dc8dc21c16be21acd"
BODY_SHA256 = "2e6d2e90187fdd801af4f898a486524d2a03b64ba10a7cee6958c505ff76e3f1"
GAP_SHA256 = "60df545c40e9a17fbe5fae49b7942a9ae23b84f140731d1c05c74f9e2b8a9194"
ENTRY_SHA256 = "c1a4339a12650222a09af64f1b757f215bb9a52a7a526e461ca6c00630fadb90"
BODY_CALL_SHA256 = "5988d7f1e0e3a2374e2a1edc3edaeffe82aef07f2d4289c00b18bd6a6a01ebcf"
BW_SHA256 = "fefd18abb88336fea22ec8dd1822a34387dbee25084ceaf6416b03a9131b0225"
RAW_WINDOW_SHA256 = "28678acd5adbec9c8ad588919dba2f5133276520cfa22e4341cf84ca8a39508a"
RETAINED_PATH_ADDRESS = 0x006E8F74
RETAINED_PATH = (
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\protocols\\"
    r"ota_service\ota_service.c"
)
PATH_CELLS = (
    0x00444DE8, 0x004455AC, 0x00446388, 0x00446CB4,
    0x00447A20, 0x0044877C, 0x004488E0,
)
EXACT_SYMBOLS = (
    (0x00781584, "_evenOtaSetFwAddr"),
    (0x00781598, "_verifyFlashContent"),
    (0x007815AC, "_evenOtaReplyToAPP"),
    (0x0076F160, "_RPC_SystemOtaStatusSync"),
    (0x00757398, "_evenOtaBootloaderWriteFile2MRAM"),
    (0x007815C0, "_otaFsHealthProbe"),
    (0x0076F1D0, "_otaFsHealthCheckAndHeal"),
    (0x00787BB0, "_fileCmdParse"),
    (0x007816C4, "_fileRawDataParse"),
    (0x0077F1D0, "_fileCaculateCRC"),
    (0x00781700, "_exportFileParse"),
    (0x0078173C, "OTA_SetInterface"),
)
GAPS = (
    (0x00444932, 0x0044494C, "225809998560b4ca710fdcb8d950a7ba35a200f02afc1e95a9d8f26cccf7a4d5"),
    (0x00444C96, 0x00444C9C, "9c0d3042c8508f86483b2f663af44c423ab0386d9bc12ceea2ef62bcaff5fb8a"),
    (0x00444DE6, 0x00444DF0, "b22290b3ee80138efcb7d6de418cb5999e14f2824a9cd6cdb877c953ad991ee1"),
    (0x00444E06, 0x00444E08, "96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7"),
    (0x00445106, 0x00445110, "9891389c1dccfa41957b2f686f76dd91bcc68dbf2cc581c4b1e151e7a63121ea"),
    (0x00445422, 0x0044545C, "7b2f9ee2107207dac81f3145dcc06035d4cc26a322206a46f36ce8ccff43f95f"),
    (0x0044557A, 0x00445660, "c3c47f0a3d18c4ca48f30706c65828542e4ad4c36e95a5271956390f6432c0a8"),
    (0x00446C5E, 0x00446D40, "39af2ff78314d83a96417afecc2a1d2a874822d05df993d54eb278361f2da0ae"),
    (0x00447A1A, 0x00447A60, "b8d63f0bd37b021de605b7dcc7e45268710379d41d7dadf520fe12c277a7ac42"),
    (0x00447E94, 0x00447F00, "0a3fca0dc5c98e6131208bddbc8fa0fe3e6af4a764c18acab3b5bc94a3a616dd"),
    (0x00448660, 0x00448670, "449c1ad58a432dd7d17b5dafbb0a32cfb1c42ae1107bcbbe7fab0d8987a2793d"),
    (0x004486E0, 0x004486EC, "f2ebfe3b842b6f62f4b4c5af6c5fe2fc8c6634b0b1fef112072b3f5682ee6f3d"),
    (0x00448748, 0x0044874C, "7d2596275c1d515e4babf59c90d9f2fb55e82af87737393439d7f172911d7ae8"),
    (0x0044877A, 0x00448784, "234cfdaa530ec01d8d6ab5c67b8ba0ae5fc44d3b318242229f403807a0966d8c"),
    (0x004487A4, 0x004487AC, "095b3bec486caa13ad21a141cd1aacaaaebc7d2925a339a1a909fe3c863e288b"),
    (0x004487D2, 0x004487E4, "e598b5d81383a1a3c20f1dde6c7b1829ab2f46679bf6d0d2712d24cb02a9a2a4"),
    (0x00448844, 0x004488EC, "3f6362dd3b652bd7bff7ce4021d910378ebc1ee8df8e55ddb39568734c4b5697"),
)
BW_TARGETS = (
    (0x0044569A, 0x00446C58), (0x004457D6, 0x00446C58),
    (0x0044584A, 0x00446C58), (0x00445862, 0x00446C58),
    (0x00445908, 0x00446C58), (0x00445D5E, 0x00446C58),
    (0x00446118, 0x00446C58), (0x00446184, 0x00446C58),
    (0x00446202, 0x00446C58), (0x00446254, 0x00446C58),
    (0x004462C0, 0x00446C58), (0x00446360, 0x00446C58),
    (0x0044637E, 0x00446C58), (0x00446E5A, 0x00447A10),
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
    for row in rows:
        start, end = int(row["entry"], 0), int(row["end_exclusive"], 0)
        raw = image_slice(data, start, end)
        if len(raw) != int(row["size"]) or sha256(raw) != row["sha256"]:
            raise AuditError(f"body changed: {row['name']}")
        starts.add(start)
        interiors.update(range(start + 2, end, 2))
        intervals.append((start, end))
        bodies.append(raw)
    if len(rows) != 25 or sum(map(len, bodies)) != 15_394:
        raise AuditError("function inventory changed")
    if sha256(b"".join(bodies)) != BODY_SHA256:
        raise AuditError("body digest changed")

    gaps = []
    for start, end, expected in GAPS:
        raw = image_slice(data, start, end)
        if sha256(raw) != expected:
            raise AuditError(f"owned gap changed at 0x{start:08x}")
        gaps.append(raw)
    if sum(map(len, gaps)) != 982 or sha256(b"".join(gaps)) != GAP_SHA256:
        raise AuditError("owned gap/pool closure changed")
    if sha256(image_slice(data, *PHYSICAL)) != PHYSICAL_SHA256:
        raise AuditError("physical object changed")
    if image_slice(data, PHYSICAL[1], PHYSICAL[1] + 8) != bytes.fromhex("0160bff35f8f7047"):
        raise AuditError("next-object boundary changed")

    if cstring(data, RETAINED_PATH_ADDRESS) != RETAINED_PATH:
        raise AuditError("retained path changed")
    if any(cstring(data, address) != name for address, name in EXACT_SYMBOLS):
        raise AuditError("retained OTA symbol changed")
    path_cells = [BASE + offset for offset in range(len(data) - 3)
                  if struct.unpack_from("<I", data, offset)[0] == RETAINED_PATH_ADDRESS]
    if path_cells != list(PATH_CELLS):
        raise AuditError("retained path-pointer closure changed")

    tools = str(ROOT / "tools")
    if tools not in sys.path:
        sys.path.insert(0, tools)
    import recover_apollo_embedded_source_paths as decoder

    entries: list[tuple[int, int]] = []
    interior: list[tuple[int, int]] = []
    bw_hits: list[tuple[int, int]] = []
    for offset in range(0, len(data) - 3, 2):
        site = BASE + offset
        target = decoder._thumb_bl_target(data, site)
        if target in starts:
            entries.append((site, target))
        elif target in interiors:
            interior.append((site, target))
        target = thumb_bw_target(data, site)
        if target in starts or target in interiors:
            bw_hits.append((site, target))
    if len(entries) != 107 or pair_digest(entries) != ENTRY_SHA256 or interior:
        raise AuditError("direct BL entry/interior closure changed")
    if tuple(bw_hits) != BW_TARGETS or pair_digest(bw_hits) != BW_SHA256:
        raise AuditError("B.W closure changed")
    for site, target in bw_hits:
        owner = next(((start, end) for start, end in intervals if start <= site < end), None)
        if owner is None or not (owner[0] < target < owner[1]):
            raise AuditError("external or cross-body B.W ingress appeared")

    calls: list[tuple[int, int]] = []
    for start, end in intervals:
        for site in range(start, end - 3, 2):
            target = decoder._thumb_bl_target(data, site)
            if target is not None:
                calls.append((site, target))
    if len(calls) != 855 or pair_digest(calls) != BODY_CALL_SHA256:
        raise AuditError("body-call closure changed")

    raw_windows: list[tuple[int, int]] = []
    aligned_entry_pointers: list[tuple[int, int]] = []
    for offset in range(len(data) - 3):
        value = struct.unpack_from("<I", data, offset)[0]
        target = (value & ~1) if value & 1 else value
        if target in starts or target in interiors:
            raw_windows.append((BASE + offset, value))
            if offset % 4 == 0 and target in starts:
                aligned_entry_pointers.append((BASE + offset, value))
    if len(raw_windows) != 81 or pair_digest(raw_windows) != RAW_WINDOW_SHA256:
        raise AuditError("raw entry/interior byte-window closure changed")
    if aligned_entry_pointers:
        raise AuditError("stored exact-entry pointer appeared")

    source = SOURCE.read_bytes()
    if len(source) != SOURCE_SIZE or sha256(source) != SOURCE_SHA256:
        raise AuditError("production OTA service source changed")
    overlay = json.loads(OVERLAY.read_text())
    leaves = {leaf["function"]: leaf for leaf in overlay["relocated_leaves"]}
    patches = {patch["name"]: patch for patch in overlay["patch_sites"]}
    for name, size, offset, relocations in PRODUCTION_LEAVES:
        leaf = leaves.get(name)
        if (
            not leaf
            or leaf.get("source", {}).get("path")
            != "components/apollo_main/core_overlay/ota_service.c"
            or leaf.get("source", {}).get("size") != SOURCE_SIZE
            or leaf.get("source", {}).get("sha256") != SOURCE_SHA256
            or leaf.get("expected", {}).get("size") != size
            or leaf.get("expected", {}).get("offset") != offset
            or leaf.get("expected", {}).get("alignment") != 4
            or len(leaf.get("relocations", [])) != relocations
            or not leaf.get("strict_relocation_contract")
            or leaf.get("profiles") != ["apple-clang"]
        ):
            raise AuditError(f"production OTA service leaf changed: {name}")
    for order, (row, target) in enumerate(zip(rows, PATCH_TARGETS), 1):
        patch = patches.get(f"replace_ota_service_{order:02d}")
        if (
            not patch
            or patch.get("runtime_address") != int(row["entry"], 0)
            or patch.get("expected_size") != int(row["size"])
            or patch.get("expected_sha256") != row["sha256"]
            or patch.get("target_function") != target
            or patch.get("branch") != "b_w"
            or patch.get("profiles") != ["apple-clang"]
        ):
            raise AuditError(f"production OTA service patch changed: {target}")

    report = json.loads(REPORT.read_text())
    reported = {
        leaf["extraction"]["function"]: leaf
        for leaf in report["relocated_leaves"]
        if leaf.get("source", {}).get("path")
        == "components/apollo_main/core_overlay/ota_service.c"
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
            raise AuditError(f"production OTA service report changed: {name}")
    validate_apollo_main_artifacts(ROOT, AuditError, "OTA service")

    manifest = json.loads(MANIFEST.read_text())
    main = manifest["component_overrides"]["apollo_main"]
    regions = {region["name"]: region for region in main["regions"]}
    for order, row in enumerate(rows, 1):
        item = regions.get(f"ota_service_{order:02d}_source_replacement")
        replacement_size = 4 if row["name"] == "_fileCmdParse" else int(row["size"])
        expected = (
            int(row["entry"], 0), replacement_size,
            "generated_source_entry_replacement",
        )
        if not item or (
            item.get("target_address"), item.get("size"),
            item.get("address_status"),
        ) != expected:
            raise AuditError(f"production OTA stock region changed: {row['name']}")
    reclaimed_tail = {
        "liblc3_ltpf_source_text": (0x00445664, 5596, "source_compiled"),
        "liblc3_ltpf_text_cave_tail": (0x00446C40, 30, "generated_alignment"),
    }
    for name, expected in reclaimed_tail.items():
        item = regions.get(name)
        if not item or (
            item.get("target_address"), item.get("size"),
            item.get("address_status"),
        ) != expected:
            raise AuditError(f"production OTA reclaimed tail changed: {name}")
    if 4 + sum(item[1] for item in reclaimed_tail.values()) != 5630:
        raise AuditError("production OTA reclaimed tail tiling changed")
    service_regions = [region for region in main["regions"]
                       if region["name"].startswith("ota_service_")]
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "source_compiled") != 3130:
        raise AuditError("production OTA compiled region coverage changed")
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "generated_alignment") != 18:
        raise AuditError("production OTA alignment coverage changed")
    if sum(region["size"] for region in service_regions
           if region["address_status"] == "official_blob") != 982:
        raise AuditError("production OTA retained-gap coverage changed")

    external_entries = [pair for pair in entries
                        if not (PHYSICAL[0] <= pair[0] < PHYSICAL[1])]
    return {
        "surface": {
            "retained_path_anchors": 12,
            "restored_pathless_functions": 13,
            "linked_functions": 25,
            "body_bytes": 15_394,
            "owned_gap_pool_bytes": 982,
            "physical_bytes": 16_376,
            "direct_bl_entry_sites": 107,
            "external_direct_bl_entry_sites": len(external_entries),
            "direct_body_calls": 855,
            "intra_body_b_w_targets": 14,
            "stored_exact_entry_pointers": 0,
            "strict_interior_ingress": 0,
            "raw_instruction_windows": 81,
        },
        "contracts": {
            "frame_ids": {0xC0: "import_control", 0xC1: "raw_or_status",
                          0xC2: "export_control", 0xC3: "export_control_alt"},
            "control_subcommands": {0: "start", 1: "continue_or_activate",
                                    2: "result_check", 3: "cancel_export"},
            "transfer_state_bytes": 0x70,
            "export_state_bytes": 0x60,
            "chunk_capacity": 0x1000,
            "notification_payloads_le": [0x0402, 0x0302, 0x0502],
            "storage_backends": ["mram", "filesystem", "external_xip_flash"],
            "sector_bytes": 0x1000,
            "read_after_write_verification": True,
        },
        "lineage": {
            "retained_path": RETAINED_PATH,
            "path_pointer_cells": [f"0x{value:08x}" for value in path_cells],
            "exact_symbols": [name for _, name in EXACT_SYMBOLS],
            "source_inventory": "unavailable",
            "license": "unknown",
        },
        "production": {
            "candidate": "components/apollo_main/core_overlay/ota_service.c",
            "source_inventory_available": True,
            "production_routed": True,
            "ownership_bytes": 15_394,
            "source_functions": 29,
            "compiled_text_bytes": 3_130,
            "alignment_bytes": 18,
            "strict_relocations": 65,
            "stock_replaced_bytes": 15_394,
            "retained_gap_pool_bytes": 982,
            "software_functional_gap": False,
            "hardware_validation": "blocked by unavailable physical evidence",
            "hardware_blocker": (
                "hardware validation is blocked by unavailable physical evidence; future qualification "
                "requires an authorized G2 pair and either a component-specific writable OTA-target "
                "fixture or an authenticated golden OTA capture covering MRAM, filesystem, XIP-flash, "
                "bootloader, export, cancellation, CRC failure, power loss, and rollback"
            ),
        },
    }


def main() -> int:
    try:
        report = analyze()
    except (AuditError, OSError, ValueError) as error:
        print(f"G2 OTA service audit: FAIL: {error}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, sort_keys=True))
    print("G2 OTA service audit: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
